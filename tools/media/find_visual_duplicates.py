"""Encontra imagens visualmente duplicadas (mesmo com nomes diferentes).

Usa dHash (difference hash) 64-bit: resize 9x8 em grayscale, compara cada pixel
com o pixel adjacente. Imagens com distancia de Hamming <= threshold sao consideradas
duplicatas perceptuais.

Uso:
    python find_visual_duplicates.py --folder "path/to/photos" --output "dupes.csv"
    python find_visual_duplicates.py --folder "path/to/photos" --threshold 5 --recursive

Threshold:
  0     duplicata exata (mesma imagem)
  1-3   muito similares (mesma foto com crop/resize/compressao)
  4-8   similares (mesma cena, variacoes)
  >10   diferentes
"""
from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path

from PIL import Image

EXTS = {".jpg", ".jpeg", ".png", ".webp", ".heic"}


def dhash(path: Path, size: int = 8) -> int:
    img = Image.open(path).convert("L").resize((size + 1, size), Image.LANCZOS)
    pixels = img.load()
    bits = 0
    for y in range(size):
        for x in range(size):
            bits = (bits << 1) | (1 if pixels[x, y] > pixels[x + 1, y] else 0)
    return bits


def hamming(a: int, b: int) -> int:
    return bin(a ^ b).count("1")


def iter_images(folder: Path, recursive: bool):
    it = folder.rglob("*") if recursive else folder.iterdir()
    for p in sorted(it):
        if p.is_file() and p.suffix.lower() in EXTS:
            yield p


def cluster_duplicates(hashes: list[tuple[Path, int]], threshold: int) -> list[list[Path]]:
    """Union-find simples para agrupar imagens similares."""
    n = len(hashes)
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb

    for i in range(n):
        for j in range(i + 1, n):
            if hamming(hashes[i][1], hashes[j][1]) <= threshold:
                union(i, j)

    groups: dict[int, list[Path]] = defaultdict(list)
    for idx, (path, _) in enumerate(hashes):
        groups[find(idx)].append(path)

    return [g for g in groups.values() if len(g) > 1]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--folder", required=True, type=Path)
    ap.add_argument("--output", type=Path, help="CSV com grupos de duplicatas")
    ap.add_argument("--threshold", type=int, default=5, help="Hamming max (default 5)")
    ap.add_argument("--recursive", action="store_true", help="Varrer subpastas")
    args = ap.parse_args()

    folder = args.folder.expanduser().resolve()
    if not folder.is_dir():
        raise SystemExit(f"Pasta nao existe: {folder}")

    print(f"[dhash] Varrendo {folder} (recursive={args.recursive}) ...")
    images = list(iter_images(folder, args.recursive))
    print(f"[dhash] {len(images)} imagens. Calculando hashes ...")

    hashes: list[tuple[Path, int]] = []
    errors = 0
    for i, p in enumerate(images, 1):
        try:
            h = dhash(p)
            hashes.append((p, h))
        except Exception as e:
            errors += 1
            print(f"  ERRO {p.name}: {e}")
        if i % 100 == 0:
            print(f"  [{i}/{len(images)}]")

    print(f"[dhash] {len(hashes)} hashes calculados ({errors} erros).")
    print(f"[dhash] Agrupando com threshold={args.threshold} ...")

    groups = cluster_duplicates(hashes, args.threshold)
    groups.sort(key=len, reverse=True)

    total_dupes = sum(len(g) - 1 for g in groups)
    print(f"[dhash] {len(groups)} grupos com duplicatas ({total_dupes} arquivos excedentes)")

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("w", encoding="utf-8", newline="") as f:
            w = csv.writer(f)
            w.writerow(["group_id", "group_size", "folder", "filename", "full_path"])
            for gid, group in enumerate(groups, 1):
                for p in sorted(group):
                    try:
                        rel = p.relative_to(folder)
                        parent = str(rel.parent) if rel.parent != Path(".") else ""
                    except ValueError:
                        parent = str(p.parent)
                    w.writerow([gid, len(group), parent, p.name, str(p)])
        print(f"[dhash] CSV: {args.output}")

    if groups:
        print("\n[dhash] Top 10 grupos (por tamanho):")
        for gid, group in enumerate(groups[:10], 1):
            print(f"\n  Grupo {gid} ({len(group)} arquivos):")
            for p in sorted(group):
                try:
                    rel = p.relative_to(folder)
                except ValueError:
                    rel = p
                print(f"    {rel}")


if __name__ == "__main__":
    main()
