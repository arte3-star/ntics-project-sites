#!/usr/bin/env python3
"""
extract_palette.py — Extrai paleta de cores dominantes do logo de um projeto NTICS.

Lê o primeiro PNG em LOGOS/, usa PIL quantize para extrair 3 cores dominantes
(filtro brancos e cinzas), salva cores.json no diretório do projeto.

Uso:
  python tools/migration/extract_palette.py \
    --project-dir "assets/projetos/87. EXPOSIÇÃO CULINÁRIA SUSTENTÁVEL (IMETAME)"

  python tools/migration/extract_palette.py --all   # roda em todos
"""

import argparse
import colorsys
import json
import os
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]


def rgb_to_hsl(r, g, b):
    h, l, s = colorsys.rgb_to_hls(r / 255, g / 255, b / 255)
    return h * 360, s, l


def extract_dominant_colors(img_path: Path, n_colors=8) -> list[tuple[int, int, int]]:
    """Extrai cores dominantes de uma imagem PNG, filtrando brancos/cinzas."""
    img = Image.open(img_path).convert("RGBA")
    # Remove pixels transparentes — converte p/ branco
    bg = Image.new("RGBA", img.size, (255, 255, 255, 255))
    bg.paste(img, mask=img.split()[3])
    rgb = bg.convert("RGB")
    # Reduz pra acelerar
    rgb = rgb.resize((150, 150), Image.LANCZOS)
    # Quantize
    quantized = rgb.quantize(colors=n_colors, method=Image.Quantize.MEDIANCUT)
    palette = quantized.getpalette()
    histogram = quantized.histogram()

    colors = []
    for i in range(n_colors):
        r, g, b = palette[i * 3], palette[i * 3 + 1], palette[i * 3 + 2]
        count = histogram[i] if i < len(histogram) else 0
        h, s, l = rgb_to_hsl(r, g, b)
        colors.append((r, g, b, count, h, s, l))

    # Filtra: remove brancos (l > 0.92), cinzas (s < 0.12), pretos (l < 0.08)
    filtered = [c for c in colors if 0.08 < c[6] < 0.92 and c[5] > 0.12]
    # Se filtrou demais, relaxa
    if len(filtered) < 2:
        filtered = [c for c in colors if 0.05 < c[6] < 0.95 and c[5] > 0.05]
    if len(filtered) < 2:
        filtered = colors  # fallback total

    # Ordena por frequência
    filtered.sort(key=lambda c: -c[3])
    return [(c[0], c[1], c[2]) for c in filtered[:5]]


def rgb_to_hex(r, g, b):
    return f"#{r:02X}{g:02X}{b:02X}"


def darken(r, g, b, factor=0.6):
    return (int(r * factor), int(g * factor), int(b * factor))


def lighten(r, g, b, factor=0.3):
    return (int(r + (255 - r) * factor), int(g + (255 - g) * factor), int(b + (255 - b) * factor))


def build_palette(colors: list[tuple[int, int, int]]) -> dict:
    """Constrói paleta de 5 cores a partir das dominantes."""
    if not colors:
        # Fallback NTICS azul
        return {
            "primary": "#1E3A8A",
            "secondary": "#E91E63",
            "accent": "#F472B6",
            "dark": "#0F1F4D",
            "light": "#EFF6FF",
        }

    primary = colors[0]
    secondary = colors[1] if len(colors) > 1 else darken(*primary, 0.7)
    accent = colors[2] if len(colors) > 2 else lighten(*primary, 0.4)

    # dark = versão escura do primary
    dark = darken(*primary, 0.5)
    # light = versão clarinha para backgrounds
    light = lighten(*primary, 0.85)

    return {
        "primary": rgb_to_hex(*primary),
        "secondary": rgb_to_hex(*secondary) if isinstance(secondary, tuple) and len(secondary) == 3 else rgb_to_hex(*secondary),
        "accent": rgb_to_hex(*accent) if isinstance(accent, tuple) and len(accent) == 3 else rgb_to_hex(*accent),
        "dark": rgb_to_hex(*dark),
        "light": rgb_to_hex(*light),
    }


def process_project(project_dir: Path) -> dict | None:
    logos_dir = project_dir / "LOGOS"
    if not logos_dir.exists():
        return None

    pngs = [f for f in logos_dir.iterdir() if f.suffix.lower() == ".png" and f.name != "desktop.ini"]
    if not pngs:
        return None

    logo = pngs[0]
    colors = extract_dominant_colors(logo)
    palette = build_palette(colors)

    out = project_dir / "cores.json"
    out.write_text(json.dumps(palette, indent=2, ensure_ascii=False), encoding="utf-8")

    return palette


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project-dir", type=str, default=None)
    ap.add_argument("--all", action="store_true")
    args = ap.parse_args()

    if args.all:
        base = ROOT / "assets" / "projetos"
        dirs = sorted([d for d in base.iterdir() if d.is_dir() and (d / "LOGOS").exists()])
        for d in dirs:
            num = d.name.split(".")[0].strip()
            if not num.isdigit():
                continue
            n = int(num)
            if n not in (81, 82, 86, 87, 89, 91, 98, 104, 106, 110):
                continue
            palette = process_project(d)
            if palette:
                print(f"  {n:>3}: {palette['primary']} {palette['secondary']} {palette['accent']}")
            else:
                print(f"  {n:>3}: NO LOGO FOUND")
    elif args.project_dir:
        d = Path(args.project_dir)
        palette = process_project(d)
        if palette:
            print(json.dumps(palette, indent=2))
        else:
            print("No logo found", file=sys.stderr)
    else:
        ap.print_help()


if __name__ == "__main__":
    main()
