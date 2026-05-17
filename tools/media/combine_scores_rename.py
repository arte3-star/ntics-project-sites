"""Combina scores LAION (estetica) + Haiku (relevancia NTICS) e renomeia arquivos.

Score final = w_laion * (laion_score normalizado 0-10) + w_haiku * (haiku_score)

LAION scores tipicamente variam 3-7 em fotos de evento. Normalizamos linearmente
para 0-10 usando min/max da pasta.
Haiku scores ja vem em 1-10.

Uso:
    python combine_scores_rename.py --category robotica
    python combine_scores_rename.py --all
"""
from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path

ROOT = Path(r'g:/O meu disco/AUTOMAÇÕES')
MELHORES_DIR = ROOT / 'SecondBrain' / 'banco-fotos'
LAION_CSV_DIR = ROOT / 'output'  # laion-scores-<cat>.csv
HAIKU_JSON_DIR = ROOT / 'output' / 'haiku-scores'
COMBINED_DIR = ROOT / 'output' / 'combined-scores'
COMBINED_DIR.mkdir(parents=True, exist_ok=True)

W_LAION = 0.6
W_HAIKU = 0.4
EXTS = {'.jpg', '.jpeg', '.png', '.webp'}


def strip_rank_prefix(name: str) -> str:
    """Remove prefixo de rank numerico: '01_109_rel-xxx.jpg' -> '109_rel-xxx'"""
    stem = Path(name).stem
    return re.sub(r'^\d+_', '', stem)


def load_laion(category: str) -> dict[str, float]:
    """Returns stable_key -> laion_score."""
    candidates = [
        LAION_CSV_DIR / f'laion-scores-{category}.csv',
    ]
    if category == 'empreendedorismo-cultura':
        candidates.append(LAION_CSV_DIR / 'laion-scores-empreendedorismo.csv')
    path = next((p for p in candidates if p.exists()), None)
    if path is None:
        raise FileNotFoundError(f'CSV LAION nao encontrado para {category}')

    out = {}
    with path.open(encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            out[strip_rank_prefix(row['filename'])] = float(row['score'])
    return out


def load_haiku(category: str) -> dict[str, float]:
    """Returns stable_key -> haiku_score."""
    path = HAIKU_JSON_DIR / f'{category}.json'
    if not path.exists():
        raise FileNotFoundError(f'JSON Haiku nao encontrado: {path}')
    with path.open(encoding='utf-8') as f:
        data = json.load(f)
    return {strip_rank_prefix(item['file']): float(item['score']) for item in data}


def normalize(scores: dict[str, float], mn=None, mx=None) -> dict[str, float]:
    """Linear norm to [0, 10] using min/max do dict."""
    if not scores:
        return {}
    if mn is None: mn = min(scores.values())
    if mx is None: mx = max(scores.values())
    if mx - mn < 1e-6:
        return {k: 5.0 for k in scores}
    return {k: 10.0 * (v - mn) / (mx - mn) for k, v in scores.items()}


def process_category(category: str, dry: bool = False) -> tuple[int, list[tuple[str, float, float, float]]]:
    folder = MELHORES_DIR / category
    if not folder.is_dir():
        print(f'SKIP {category}: pasta nao existe')
        return 0, []

    try:
        laion = load_laion(category)
        haiku = load_haiku(category)
    except FileNotFoundError as e:
        print(f'SKIP {category}: {e}')
        return 0, []

    # Normalizar LAION para 0-10 usando min/max da pasta
    laion_n = normalize(laion)

    # Match real files to scores by stable_key (= filename sem prefixo de rank)
    real_files = {strip_rank_prefix(p.name): p for p in folder.iterdir() if p.is_file() and p.suffix.lower() in EXTS}
    rows = []  # (key, real_filename, laion_n, haiku, combined)
    missing_laion = []
    missing_haiku = []
    for key, p in real_files.items():
        lr = laion_n.get(key)
        hk = haiku.get(key)
        if lr is None: missing_laion.append(key)
        if hk is None: missing_haiku.append(key)
        if lr is None or hk is None: continue
        combined = W_LAION * lr + W_HAIKU * hk
        rows.append((key, p, lr, hk, combined))

    if missing_laion:
        print(f'  [{category}] AVISO: {len(missing_laion)} sem LAION')
    if missing_haiku:
        print(f'  [{category}] AVISO: {len(missing_haiku)} sem Haiku')

    # Sort desc by combined
    rows.sort(key=lambda r: -r[4])

    # Write combined CSV
    csv_path = COMBINED_DIR / f'{category}.csv'
    with csv_path.open('w', encoding='utf-8', newline='') as f:
        w = csv.writer(f)
        w.writerow(['rank', 'combined', 'laion_norm', 'haiku', 'filename'])
        for rank, (stem, p, lr, hk, c) in enumerate(rows, 1):
            w.writerow([rank, f'{c:.2f}', f'{lr:.2f}', int(hk), p.name])

    if dry:
        print(f'  [{category}] {len(rows)} fotos, top: {rows[0][1].name if rows else "-"} (combined={rows[0][4]:.2f})')
        return len(rows), rows

    # Rename: passo 1 -> temp, passo 2 -> final
    width = max(2, len(str(len(rows))))
    for idx, (stem, p, lr, hk, c) in enumerate(rows, 1):
        body = re.sub(r'^\d+_', '', p.name)
        p.rename(p.with_name(f'.tmp_{idx:04d}_{body}'))

    for p in sorted(folder.iterdir()):
        if p.name.startswith('.tmp_'):
            m = re.match(r'\.tmp_(\d+)_(.+)', p.name)
            if m:
                final = f'{int(m.group(1)):0{width}d}_{m.group(2)}'
                p.rename(folder / final)

    print(f'  [{category}] {len(rows)} fotos renomeadas')
    return len(rows), rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--category')
    ap.add_argument('--all', action='store_true')
    ap.add_argument('--dry', action='store_true')
    args = ap.parse_args()

    cats = ['artes-literarias', 'caminhao-itinerante', 'cinegastroarte', 'circo',
            'empreendedorismo-cultura', 'festival', 'gastronomia', 'hub-agro',
            'negocio-cultural', 'ods-escolas', 'robotica', 'teatro']

    if args.all:
        targets = cats
    elif args.category:
        targets = [args.category]
    else:
        raise SystemExit('Use --all ou --category X')

    total = 0
    master = []
    for cat in targets:
        n, rows = process_category(cat, dry=args.dry)
        total += n
        for stem, p, lr, hk, c in rows:
            master.append((cat, c, lr, hk, p.name))

    # Master CSV
    master_csv = COMBINED_DIR / '_master.csv'
    master.sort(key=lambda r: -r[1])
    with master_csv.open('w', encoding='utf-8', newline='') as f:
        w = csv.writer(f)
        w.writerow(['categoria', 'combined', 'laion_norm', 'haiku', 'filename'])
        for cat, c, lr, hk, name in master:
            w.writerow([cat, f'{c:.2f}', f'{lr:.2f}', int(hk), name])

    print(f'\nTotal: {total} fotos processadas.')
    print(f'Master CSV: {master_csv}')
    if master:
        print(f'Top 5 geral:')
        for cat, c, lr, hk, name in master[:5]:
            print(f'  {c:5.2f}  [{cat:22}] LAION={lr:4.1f} Haiku={int(hk)}  {name}')


if __name__ == '__main__':
    main()
