"""
extract_kv_assets.py — Extrai assets de KV (Key Visual) do Adobe Illustrator.

Abre o arquivo .ai no Illustrator via COM e:
  1. Extrai paleta de cores (via read_document_colors.jsx)
  2. Exporta cada artboard como SVG + PNG (via extract_kv_elements.jsx)
  3. Categoriza camadas por keywords e exporta individualmente
  4. Gera paleta/swatches.png e paleta/cores.json
  5. Salva manifest.json

Usage:
  python tools/adobe/extract_kv_assets.py \\
    --source "C:/Users/lucas/Downloads/KV New Holland.ai" \\
    --output-dir "assets/projetos/NEW_HOLLAND_FESTIVAL/KV"

Requer: pywin32, Pillow
"""

import argparse
import json
import sys
import time
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Import COM helpers from adapt_artwork_illustrator.py (same directory)
_THIS_DIR = Path(__file__).parent
sys.path.insert(0, str(_THIS_DIR))
from adapt_artwork_illustrator import connect_illustrator, open_artwork


# ── JSX Runner ────────────────────────────────────────────────────────────────

def run_jsx_with_vars(app, jsx_path: Path, variables: dict) -> str:
    """Execute a JSX file in Illustrator with injected variable declarations."""
    jsx_path = Path(jsx_path).resolve()
    if not jsx_path.exists():
        raise FileNotFoundError(f"JSX not found: {jsx_path}")

    jsx_content = jsx_path.read_text(encoding="utf-8")

    # Inject variable declarations at the top (forward slashes for JSX paths)
    injections = []
    for name, value in variables.items():
        safe = str(value).replace("\\", "/")
        injections.append(f'var {name} = "{safe}";')
    jsx_content = "\n".join(injections) + "\n" + jsx_content

    print(f"[...] Executando {jsx_path.name}...")
    try:
        result = app.DoJavaScript(jsx_content)
        print(f"[OK]  {jsx_path.name} concluido.")
        return result or ""
    except Exception as e:
        raise RuntimeError(f"Erro ao executar {jsx_path.name}: {e}")


# ── Step 1: Palette Extraction ────────────────────────────────────────────────

def cmyk_to_hex(cmyk):
    """Convert CMYK list [0-100] to hex string."""
    c, m, y, k = [v / 100.0 for v in cmyk]
    r = int(255 * (1 - c) * (1 - k))
    g = int(255 * (1 - m) * (1 - k))
    b = int(255 * (1 - y) * (1 - k))
    return f"#{r:02X}{g:02X}{b:02X}"


def enrich_colors_with_hex(palette_data: dict) -> dict:
    """Add hex field to CMYK colors that lack it."""
    for col in palette_data.get("colors", []):
        if not col.get("hex") and col.get("cmyk"):
            col["hex"] = cmyk_to_hex(col["cmyk"])
    for sw in palette_data.get("swatches", []):
        if not sw.get("hex") and sw.get("cmyk"):
            sw["hex"] = cmyk_to_hex(sw["cmyk"])
    return palette_data


def extract_palette(app, output_dir: Path, jsx_dir: Path, tmp_dir: Path) -> dict:
    """Run read_document_colors.jsx, enrich with hex, save paleta/cores.json."""
    result_path = tmp_dir / "colors_result.json"

    run_jsx_with_vars(app, jsx_dir / "read_document_colors.jsx", {
        "RESULT_PATH": str(result_path)
    })

    if not result_path.exists():
        print("[AVISO] Arquivo de resultado de cores nao gerado.")
        return {}

    with open(result_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    data = enrich_colors_with_hex(data)

    paleta_dir = output_dir / "paleta"
    paleta_dir.mkdir(parents=True, exist_ok=True)
    cores_path = paleta_dir / "cores.json"
    with open(cores_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    n_colors = len(data.get("colors", []))
    n_swatches = len(data.get("swatches", []))
    print(f"[OK]  Paleta salva: {n_swatches} swatches, {n_colors} cores detectadas -> {cores_path}")
    return data


# ── Step 2: Swatches Image ────────────────────────────────────────────────────

def generate_swatches(palette_data: dict, output_dir: Path):
    """Generate paleta/swatches.png: one color square per swatch/color."""
    try:
        from PIL import Image, ImageDraw
    except ImportError:
        print("[AVISO] Pillow nao instalado. Pulando swatches.png. (pip install Pillow)")
        return

    items = []

    # Named swatches first (excluding None/Registration)
    for sw in palette_data.get("swatches", []):
        hex_val = sw.get("hex") or (cmyk_to_hex(sw["cmyk"]) if sw.get("cmyk") else None)
        if hex_val:
            items.append({"hex": hex_val, "name": sw.get("name", "")})

    # Fill from detected colors (skip pure gray, skip white/black if already covered)
    for col in palette_data.get("colors", []):
        if len(items) >= 24:
            break
        if col.get("gray") is not None:
            continue  # skip pure gray
        hex_val = col.get("hex")
        if hex_val:
            items.append({"hex": hex_val, "name": ""})

    if not items:
        print("[AVISO] Nenhuma cor encontrada para gerar swatches.png.")
        return

    swatch_w, swatch_h, label_h = 80, 80, 22
    per_row = min(10, len(items))
    rows = (len(items) + per_row - 1) // per_row

    img = Image.new("RGB", (per_row * swatch_w, rows * (swatch_h + label_h)), (248, 248, 248))
    draw = ImageDraw.Draw(img)

    for i, item in enumerate(items):
        col_i = i % per_row
        row_i = i // per_row
        x = col_i * swatch_w
        y = row_i * (swatch_h + label_h)

        try:
            hex_val = item["hex"].lstrip("#")
            r, g, b = int(hex_val[0:2], 16), int(hex_val[2:4], 16), int(hex_val[4:6], 16)
        except Exception:
            continue

        draw.rectangle([x, y, x + swatch_w - 1, y + swatch_h - 1], fill=(r, g, b))
        # Label: hex value
        label = "#" + hex_val.upper()
        # Contrast: white text on dark swatch, black on light
        brightness = 0.299 * r + 0.587 * g + 0.114 * b
        text_color = (255, 255, 255) if brightness < 128 else (0, 0, 0)
        draw.text((x + 4, y + swatch_h + 3), label, fill=(30, 30, 30))

        # Color dot preview inside swatch
        if item.get("name"):
            name_short = item["name"][:12]
            draw.text((x + 4, y + 4), name_short, fill=text_color)

    out_path = output_dir / "paleta" / "swatches.png"
    img.save(out_path)
    print(f"[OK]  Swatches: {len(items)} cores -> {out_path}")


# ── Step 3b: SVG → PNG Conversion (PyMuPDF) ──────────────────────────────────

def convert_svgs_to_png(output_dir: Path, dpi: int = 300):
    """Convert all exported SVGs to PNG using PyMuPDF (reliable fallback for Illustrator PNG24)."""
    try:
        import fitz
    except ImportError:
        print("[AVISO] PyMuPDF nao instalado. Pulando conversao SVG->PNG. (pip install pymupdf)")
        return 0

    subdirs = ["paginas", "logos", "elementos", "fundos", "outros"]
    converted = 0
    scale = dpi / 72.0  # SVG points are 72 dpi base

    for subdir in subdirs:
        folder = output_dir / subdir
        if not folder.exists():
            continue
        for svg_file in sorted(folder.glob("*.svg")):
            png_file = svg_file.with_suffix(".png")
            try:
                doc = fitz.open(str(svg_file))
                page = doc[0]
                mat = fitz.Matrix(scale, scale)
                pix = page.get_pixmap(matrix=mat, alpha=True)
                pix.save(str(png_file))
                doc.close()
                converted += 1
            except Exception as e:
                print(f"[AVISO] Nao foi possivel converter {svg_file.name}: {e}")

    if converted:
        print(f"[OK]  SVG -> PNG: {converted} arquivos convertidos a {dpi} DPI")
    return converted


# ── Step 3c: Auto-organize by PDF page content ────────────────────────────────

# Keywords that determine which folder each page belongs to
_PAGE_CATEGORY_RULES = [
    (["logo", "marca", "logotipo", "assinatura", "segurança", "seguranca", "proteção", "protecao", "reducao", "redução", "negativo", "positivo"], "logos"),
    (["paleta", "cor", "cores", "colour", "color", "#"], "paleta"),
    (["tipograf", "font", "typeface", "tipo"], "tipografia"),
    (["elemento", "elementos", "composição", "composicao", "padrao", "padrão", "textura", "grafismo"], "elementos"),
    (["fundo", "background", "cenario", "cenário", "aplicação", "aplicacao"], "fundos"),
]

def classify_page_text(text: str) -> str:
    """Return folder name based on page text keywords. None = keep only in paginas."""
    lower = text.lower()
    for keywords, folder in _PAGE_CATEGORY_RULES:
        for kw in keywords:
            if kw in lower:
                return folder
    return None


def organize_by_pdf_content(output_dir: Path, pdf_path: Path):
    """Read PDF page titles and copy SVG/PNG to matching category folders."""
    import fitz
    import shutil

    try:
        doc = fitz.open(str(pdf_path))
    except Exception as e:
        print(f"[AVISO] Nao foi possivel abrir PDF para classificar paginas: {e}")
        return {}

    paginas_dir = output_dir / "paginas"
    svgs = sorted(paginas_dir.glob("*.svg"))

    mapping = {}  # filename_base -> (folder, page_title)
    moved = 0

    for i, page in enumerate(doc):
        if i >= len(svgs):
            break
        text = page.get_text().strip()
        title = " ".join(text.split("\n")[:3]).strip()
        folder = classify_page_text(text)

        base = svgs[i].stem  # e.g. "02_Prancheta_2"
        mapping[base] = {"page": i + 1, "title": title, "folder": folder or "paginas"}

        if folder and folder != "paginas":
            dest_dir = output_dir / folder
            dest_dir.mkdir(exist_ok=True)
            for ext in [".svg", ".png"]:
                src = paginas_dir / (base + ext)
                if src.exists():
                    shutil.copy2(src, dest_dir / (base + ext))
                    moved += 1

    doc.close()

    if moved:
        print(f"[OK]  Organizacao por conteudo: {moved // 2} paginas copiadas para pastas corretas")
        for base, info in mapping.items():
            mark = "" if info["folder"] == "paginas" else f" -> {info['folder']}/"
            print(f"        P{info['page']}: {info['title'][:50]}{mark}")
    else:
        print("[AVISO] Nenhuma pagina foi classificada automaticamente.")

    return mapping


# ── Step 3: Elements Export ───────────────────────────────────────────────────

def extract_elements(app, output_dir: Path, jsx_dir: Path, tmp_dir: Path, dpi: int = 300) -> dict:
    """Run extract_kv_elements.jsx. Returns manifest with artboards and layers."""
    config = {
        "output_dir": str(output_dir).replace("\\", "/"),
        "artboard_dpi": dpi,
        "categories": {
            "logos": [
                "logo", "logotipo", "marca", "simbolo", "brand",
                "new holland", "nh", "assinatura"
            ],
            "elementos": [
                "elemento", "detalhe", "grafismo", "icone", "icon",
                "pattern", "textura", "ilustra", "vetor", "grafico"
            ],
            "fundos": [
                "fundo", "background", "bg", "base", "backdrop", "cenario"
            ]
        }
    }

    config_path = tmp_dir / "extract_kv_config.json"
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

    run_jsx_with_vars(app, jsx_dir / "extract_kv_elements.jsx", {
        "CONFIG_PATH": str(config_path)
    })

    result_path = tmp_dir / "extract_kv_config_result.json"
    if not result_path.exists():
        print("[AVISO] Resultado do JSX de elementos nao gerado.")
        return {"artboards": [], "layers": [], "errors": []}

    with open(result_path, "r", encoding="utf-8") as f:
        return json.load(f)


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Extrai assets de KV (Key Visual) do Adobe Illustrator."
    )
    parser.add_argument(
        "--source", required=True,
        help="Arquivo .ai do KV (ex: Downloads/KV New Holland.ai)"
    )
    parser.add_argument(
        "--output-dir",
        default="assets/projetos/NEW_HOLLAND_FESTIVAL/KV",
        help="Diretorio de saida (default: assets/projetos/NEW_HOLLAND_FESTIVAL/KV)"
    )
    parser.add_argument(
        "--dpi", type=int, default=300,
        help="Resolucao PNG em DPI (default: 300)"
    )
    parser.add_argument(
        "--pdf",
        help="PDF do KV para classificar paginas automaticamente nas pastas certas (opcional)"
    )
    parser.add_argument(
        "--timeout", type=int, default=90,
        help="Timeout para conexao COM com Illustrator, em segundos (default: 90)"
    )
    args = parser.parse_args()

    source = Path(args.source).resolve()
    if not source.exists():
        print(f"[ERRO] Arquivo fonte nao encontrado: {source}")
        sys.exit(1)

    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    tmp_dir = Path("tmp").resolve()
    tmp_dir.mkdir(exist_ok=True)

    jsx_dir = Path(__file__).parent / "jsx"

    print(f"\n{'='*60}")
    print("KV Asset Extractor")
    print(f"  Fonte:   {source.name}")
    print(f"  Saida:   {output_dir}")
    print(f"  DPI PNG: {args.dpi}")
    print(f"{'='*60}\n")

    try:
        app = connect_illustrator(timeout=args.timeout)
        open_artwork(app, str(source))

        # Step 1: Palette
        print("\n[1/3] Extraindo paleta de cores...")
        palette_data = extract_palette(app, output_dir, jsx_dir, tmp_dir)

        # Step 2: Swatches image
        generate_swatches(palette_data, output_dir)

        # Step 3: Artboards + layers
        print("\n[2/3] Exportando artboards e camadas...")
        elements = extract_elements(app, output_dir, jsx_dir, tmp_dir, dpi=args.dpi)

        # Step 3.5: Convert SVGs to PNG via PyMuPDF
        print("\n[2.5/3] Convertendo SVGs para PNG...")
        convert_svgs_to_png(output_dir, dpi=args.dpi)

        # Step 3.6: Organize by PDF page content (if PDF provided)
        page_mapping = {}
        if args.pdf:
            pdf_path = Path(args.pdf).resolve()
            if pdf_path.exists():
                print("\n[2.6/3] Organizando paginas por conteudo do PDF...")
                page_mapping = organize_by_pdf_content(output_dir, pdf_path)
            else:
                print(f"[AVISO] PDF nao encontrado: {pdf_path}")

        # Step 4: Manifest
        print("\n[3/3] Salvando manifest.json...")
        manifest = {
            "source": str(source),
            "output_dir": str(output_dir),
            "dpi": args.dpi,
            "palette": {
                "total_swatches": len(palette_data.get("swatches", [])),
                "total_colors_detected": len(palette_data.get("colors", [])),
                "cores_json": str(output_dir / "paleta" / "cores.json"),
                "swatches_png": str(output_dir / "paleta" / "swatches.png"),
            },
            "elements": elements,
        }

        manifest_path = output_dir / "manifest.json"
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, ensure_ascii=False, indent=2)

        # Summary
        artboards = elements.get("artboards", [])
        layers = elements.get("layers", [])
        logos     = [l for l in layers if l.get("category") == "logos"]
        elementos = [l for l in layers if l.get("category") == "elementos"]
        fundos    = [l for l in layers if l.get("category") == "fundos"]
        outros    = [l for l in layers if l.get("category") == "outros"]
        vazias    = [l for l in layers if l.get("category") == "vazia"]
        erros_jsx = elements.get("errors", [])

        print(f"\n{'='*60}")
        print("EXTRACAO CONCLUIDA")
        print(f"{'='*60}")
        print(f"  Artboards exportados:   {len(artboards)}")
        print(f"  Logos:                  {len(logos)}")
        print(f"  Elementos graficos:     {len(elementos)}")
        print(f"  Fundos:                 {len(fundos)}")
        print(f"  Outros (revisar nome):  {len(outros)}")
        print(f"  Camadas vazias (skip):  {len(vazias)}")
        print(f"  Swatches de cor:        {len(palette_data.get('swatches', []))}")
        print(f"  Saida:                  {output_dir}")

        if outros:
            print(f"\n  Camadas nao categorizadas (renomeie no AI e reexecute):")
            for l in outros:
                print(f"    - '{l.get('name', '')}' ({l.get('items', 0)} itens)")

        if erros_jsx:
            print(f"\n  Avisos do Illustrator:")
            for err in erros_jsx[:10]:
                print(f"    ! {err}")

        print(f"\n  Manifest: {manifest_path}")
        print(f"{'='*60}\n")

    except FileNotFoundError as e:
        print(f"\n[ERRO] {e}")
        sys.exit(1)
    except TimeoutError as e:
        print(f"\n[ERRO] {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERRO] {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
