"""Recorta os cards Leonardo para uso como fotos do artigo do site NTICS.

Margens de segurança:
- Cards de notícia (02-08): crop 10%-45% da altura (descarta numeração X/9 no topo + gradiente teal e badge no rodapé)
- Card capa (01): crop 0%-43% (não tem numeração, mas tem texto grande no centro)

Uso:
    python tools/content-gen/crop_fotos_artigo.py --semana 2026-04-14
"""
import argparse
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]


def crop_top(src: Path, dst: Path, top_pct: float, bottom_pct: float, max_w: int = 1200) -> tuple[int, int]:
    img = Image.open(src).convert("RGB")
    w, h = img.size
    top = int(h * top_pct)
    bottom = int(h * bottom_pct)
    cropped = img.crop((0, top, w, bottom))
    if cropped.size[0] > max_w:
        ratio = max_w / cropped.size[0]
        cropped = cropped.resize((max_w, int(cropped.size[1] * ratio)), Image.LANCZOS)
    dst.parent.mkdir(parents=True, exist_ok=True)
    cropped.save(dst, "JPEG", quality=88, optimize=True)
    return cropped.size


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--semana", required=True, help="YYYY-MM-DD")
    parser.add_argument("--src-dir", default=None, help="Sobrescreve diretório de origem (default = output/marketing/carrosseis/noticias/semana-{semana})")
    parser.add_argument("--dst-dir", default=None, help="Sobrescreve diretório destino (default = output/marketing/artigos/Artigo-noticias/semana-{semana}/fotos)")
    args = parser.parse_args()

    src_dir = Path(args.src_dir) if args.src_dir else ROOT / f"output/marketing/carrosseis/noticias/semana-{args.semana}"
    dst_dir = Path(args.dst_dir) if args.dst_dir else ROOT / f"output/marketing/artigos/Artigo-noticias/semana-{args.semana}/fotos"

    # Mapping: card source → article filename, top%, bottom%
    plan = []
    for src in sorted(src_dir.glob("[0-9]*-*.jpg")):
        name = src.name
        if name.startswith("01-capa"):
            plan.append((src, dst_dir / "hero-semana.jpg", 0.00, 0.43))
        elif name.startswith("09-cta"):
            continue  # CTA card has no useful photo
        else:
            # Extract slug after the number prefix: "07-cooperacao-global.jpg" → "cooperacao-global"
            slug = name.split("-", 1)[1].replace(".jpg", "")
            plan.append((src, dst_dir / f"inline-{slug}.jpg", 0.10, 0.45))

    for src, dst, top, bottom in plan:
        size = crop_top(src, dst, top, bottom)
        print(f"OK: {dst.name} ({size[0]}x{size[1]}) crop={top:.0%}-{bottom:.0%}")


if __name__ == "__main__":
    main()
