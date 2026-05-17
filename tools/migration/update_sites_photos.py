"""
Popula os sites do Lovable (repo arte3-star/ntics-project-sites) com as melhores
fotos curadas por tema em SecondBrain/banco-fotos/.

Estratégia:
 - Prioridade 1: fotos cujo nome tem o número NTICS do projeto (ex: `_82_`)
 - Prioridade 2: fotos restantes do tema correspondente, em ordem lexicográfica
 - Substitui in-place: mantém o layout (hero / sobre / galeria), só troca as fotos

Suporta 3 padrões de site:
 A) src="https://raw.githubusercontent.com/.../FOTOS/rf-XXX.jpg"   (sites 82, 86, 87, 89, 91, 98, 104, 106, 110)
 B) src="assets/imagens/rf-XXX.jpg"                                (site 81)
 C) <span class="gal-ph">assets/galeria/<slug>/NN.jpg</span>       (sites 116, 117, 119, 125, 127_*)
"""
from __future__ import annotations

import argparse
import json
import random
import re
import shutil
from pathlib import Path
from typing import Iterable

REPO_ROOT = Path(r"G:/O meu disco/AUTOMAÇÕES/.tmp/ntics-project-sites")
PHOTOS_ROOT = Path(r"G:/O meu disco/Claude-NTICS-Projetos/SecondBrain/banco-fotos")

# Mapeamento site → tema + número NTICS canônico
SITE_CONFIG: dict[str, dict] = {
    "81_cultura_robotica_ferroporte":            {"theme": "robotica",                   "num": "81"},
    "82_robotica_cultural_nas_escolas":          {"theme": "robotica",                   "num": "82"},
    "86_teatro_bons_habitos_ferroporte":         {"theme": "teatro",                     "num": "86"},
    "87_exposicao_culinaria_sustentavel_imetame":{"theme": "gastronomia",                "num": "87"},
    "89_oficina_teatro_sustentavel_ferroport":   {"theme": "teatro",                     "num": "89"},
    "91_teatro_dos_ods":                         {"theme": "ods-escolas",                "num": "91"},
    "98_conhecendo_os_ods":                      {"theme": "ods-escolas",                "num": "98"},
    "104_pec_3aed_porto_itapoa":                 {"theme": "empreendedorismo-cultura",   "num": "104"},
    "106_teatro_oficina_robotica_2aed_cnh":      {"theme": "robotica",                   "num": "106"},
    "110_caminhao_cultura_sustentabilidade_jaepel": {"theme": "caminhao-itinerante",     "num": "110"},
    "116_cultura_robotica":                      {"theme": "robotica",                   "num": None},
    "117_teatro_robotica":                       {"theme": "robotica",                   "num": None},
    "119_pec":                                   {"theme": "empreendedorismo-cultura",   "num": None},
    "125_gastronomia":                           {"theme": "gastronomia",                "num": None},
    "127_pie_guarulhos":                         {"theme": "empreendedorismo-cultura",   "num": None},
    "127_pie_serra":                             {"theme": "empreendedorismo-cultura",   "num": None},
}

# Regex
# Pattern A: absolute raw.githubusercontent URL pointing at FOTOS/<filename>
RE_A = re.compile(
    r'(https://raw\.githubusercontent\.com/arte3-star/ntics-project-sites/[^/]+/[^/]+/FOTOS/)([^"\']+\.(?:jpg|jpeg|png|webp))',
    re.IGNORECASE,
)
# Pattern B: relative assets/imagens/<filename>  (captures rf-*.jpg only so we skip logos)
RE_B = re.compile(
    r'(src=")(assets/imagens/(?!.*/)(rf-[^"\']+\.(?:jpg|jpeg|png|webp)))(")',
    re.IGNORECASE,
)
# Pattern B2: site 81 variant (same as B but rf- prefix) -- covered by RE_B
# Pattern C: <span class="gal-ph"> placeholder (with optional preceding svg)
# We capture the ENTIRE "icon svg + gal-ph" content within a .gal-item / .cidade-img
# so we can replace with an <img>. We keep it simple: match the span and the svg
# before it inside the same parent.
RE_C_SPAN = re.compile(
    r'<svg[^>]*>[\s\S]*?</svg>\s*<span class="gal-ph">([^<]+)</span>',
    re.IGNORECASE,
)

def photo_pool(theme: str) -> list[Path]:
    d = PHOTOS_ROOT / theme
    if not d.exists():
        return []
    return sorted(
        [p for p in d.iterdir() if p.is_file() and p.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}],
        key=lambda p: p.name.lower(),
    )

def pick_photos(theme: str, num: str | None, n: int, seen: set[str]) -> list[Path]:
    """Return up to n photos. Prioritize files matching the NTICS number when provided."""
    pool = photo_pool(theme)
    if not pool:
        return []

    prio: list[Path] = []
    rest: list[Path] = []
    if num:
        num_tag = f"_{num}_"
        for p in pool:
            (prio if num_tag in p.name else rest).append(p)
    else:
        rest = list(pool)

    ordered = prio + rest
    # Remove duplicates already chosen for this site
    filtered = [p for p in ordered if p.name not in seen]
    return filtered[:n]

def safe_name(src: Path) -> str:
    """Destination filename: keep concise + URL-safe."""
    return src.name.replace(" ", "_")

def process_site(slug: str, dry_run: bool = False) -> dict:
    cfg = SITE_CONFIG[slug]
    site_dir = REPO_ROOT / slug
    html_path = site_dir / "index.html"
    if not html_path.exists():
        return {"slug": slug, "error": "index.html missing"}

    html = html_path.read_text(encoding="utf-8")
    original = html

    stats = {
        "slug": slug,
        "theme": cfg["theme"],
        "num": cfg["num"],
        "pattern": None,
        "replaced": 0,
        "copied": [],
        "skipped": [],
    }

    # Detect pattern
    a_hits = list(RE_A.finditer(html))
    b_hits = list(RE_B.finditer(html))
    c_hits = list(RE_C_SPAN.finditer(html))

    seen: set[str] = set()

    # --- Pattern A: absolute github URL → FOTOS/ ---
    if a_hits:
        stats["pattern"] = "A"
        fotos_dir = site_dir / "FOTOS"
        fotos_dir.mkdir(exist_ok=True)
        picks = pick_photos(cfg["theme"], cfg["num"], len(a_hits), seen)
        if not picks:
            return {**stats, "error": f"no photos in theme {cfg['theme']}"}
        # If fewer picks than slots, repeat cyclically
        while len(picks) < len(a_hits):
            picks.extend(picks)
        picks = picks[:len(a_hits)]
        for match, src in zip(a_hits, picks):
            new_name = safe_name(src)
            # Copy file
            dst = fotos_dir / new_name
            if not dry_run and (not dst.exists() or dst.stat().st_size != src.stat().st_size):
                shutil.copy2(src, dst)
                stats["copied"].append(f"FOTOS/{new_name}")
            seen.add(src.name)
        # Rewrite (pass 2 with fresh list)
        idx = 0
        def a_sub(m):
            nonlocal idx
            pick = picks[idx]
            idx += 1
            return f"{m.group(1)}{safe_name(pick)}"
        html = RE_A.sub(a_sub, html)
        stats["replaced"] = len(a_hits)

    # --- Pattern B: assets/imagens/rf-*.jpg ---
    if b_hits and stats["pattern"] is None:
        stats["pattern"] = "B"
        img_dir = site_dir / "assets" / "imagens"
        img_dir.mkdir(parents=True, exist_ok=True)
        picks = pick_photos(cfg["theme"], cfg["num"], len(b_hits), seen)
        if not picks:
            return {**stats, "error": f"no photos in theme {cfg['theme']}"}
        while len(picks) < len(b_hits):
            picks.extend(picks)
        picks = picks[:len(b_hits)]
        for src in picks:
            dst = img_dir / safe_name(src)
            if not dry_run and (not dst.exists() or dst.stat().st_size != src.stat().st_size):
                shutil.copy2(src, dst)
                stats["copied"].append(f"assets/imagens/{safe_name(src)}")
            seen.add(src.name)
        idx = 0
        def b_sub(m):
            nonlocal idx
            pick = picks[idx]
            idx += 1
            return f'{m.group(1)}assets/imagens/{safe_name(pick)}{m.group(4)}'
        html = RE_B.sub(b_sub, html)
        stats["replaced"] = len(b_hits)

    # --- Pattern C: gal-ph placeholders ---
    if c_hits and stats["pattern"] is None:
        stats["pattern"] = "C"
        # Photos go to assets/galeria/<slug>/NN.jpg (using original path hint when possible)
        picks = pick_photos(cfg["theme"], cfg["num"], len(c_hits), seen)
        if not picks:
            return {**stats, "error": f"no photos in theme {cfg['theme']}"}
        while len(picks) < len(c_hits):
            picks.extend(picks)
        picks = picks[:len(c_hits)]
        # The placeholder text is the target path (e.g. assets/galeria/116_.../01.jpg)
        # We'll keep that path as the destination filename layout
        idx = 0
        replacements = []
        for m in c_hits:
            target_path = m.group(1).strip()  # e.g. assets/galeria/116_cultura_robotica/01.jpg
            pick = picks[idx]
            idx += 1
            dst = site_dir / target_path
            dst.parent.mkdir(parents=True, exist_ok=True)
            # Force .jpg extension (target placeholders use .jpg)
            if not dry_run:
                shutil.copy2(pick, dst)
                stats["copied"].append(target_path)
            seen.add(pick.name)
            # Replace the svg + span with an <img>
            img_tag = f'<img src="{target_path}" alt="" loading="lazy" style="width:100%;height:100%;object-fit:cover;">'
            replacements.append((m.group(0), img_tag))
        # Apply replacements in order (unique substrings)
        for old, new in replacements:
            # Guard: each match string may repeat; replace first occurrence only
            html = html.replace(old, new, 1)
        stats["replaced"] = len(c_hits)

    if stats["pattern"] is None:
        stats["error"] = "no matching pattern"
        return stats

    if html != original and not dry_run:
        html_path.write_text(html, encoding="utf-8")

    return stats

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--site", action="append", help="Process only specific site slug(s)")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    targets: Iterable[str] = args.site or list(SITE_CONFIG.keys())
    all_stats = []
    for slug in targets:
        if slug not in SITE_CONFIG:
            print(f"[skip] unknown site: {slug}")
            continue
        print(f"[run] {slug}  (theme={SITE_CONFIG[slug]['theme']}  num={SITE_CONFIG[slug]['num']})")
        st = process_site(slug, dry_run=args.dry_run)
        all_stats.append(st)
        if st.get("error"):
            print(f"       ERROR: {st['error']}")
        else:
            print(f"       pattern={st['pattern']}  replaced={st['replaced']}  copied={len(st['copied'])} files")

    print("\n=== summary ===")
    print(json.dumps(all_stats, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
