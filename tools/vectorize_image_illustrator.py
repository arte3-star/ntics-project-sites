"""
vectorize_image_illustrator.py — Vetoriza imagens raster via Image Trace no Illustrator.

Pipeline ideal: Leonardo AI gera PNG → este tool vetoriza → SVG/AI/EPS/PDF.

Controla o Adobe Illustrator via COM para:
  1. Abrir imagem raster (PNG, JPG, TIFF, PSD, BMP, GIF)
  2. Aplicar Image Trace com preset configurável
  3. Expandir tracing para paths vetoriais
  4. Exportar em formatos vetoriais (SVG, AI, EPS, PDF)

Usage:
  # Vetorizar uma imagem com preset padrão (High Fidelity Photo)
  python tools/vectorize_image_illustrator.py \
    --images .tmp/images/logo.png \
    --output-dir .tmp/vectorized

  # Vetorizar múltiplas imagens com preset específico
  python tools/vectorize_image_illustrator.py \
    --images .tmp/images/img1.png .tmp/images/img2.jpg \
    --preset "Black and White Logo" \
    --formats svg ai pdf \
    --output-dir .tmp/vectorized

  # Vetorizar com opções avançadas
  python tools/vectorize_image_illustrator.py \
    --images .tmp/images/logo.png \
    --preset "16 Colors" \
    --ignore-white \
    --formats svg eps \
    --output-dir .tmp/vectorized

  # Vetorizar todas as imagens de uma pasta
  python tools/vectorize_image_illustrator.py \
    --input-dir .tmp/images/2026-03-20 \
    --preset "High Fidelity Photo" \
    --formats svg \
    --output-dir .tmp/vectorized

  # Via config JSON
  python tools/vectorize_image_illustrator.py \
    --config .tmp/vectorize_config.json

Available presets (variam por idioma/versão):
  - High Fidelity Photo    → máxima fidelidade, muitas cores (ideal para fotos Leonardo)
  - Low Fidelity Photo     → menos detalhes, mais estilizado
  - 3 Colors / 6 Colors / 16 Colors → paleta limitada
  - Shades of Gray         → tons de cinza
  - Black and White Logo   → P&B, ideal para logos
  - Sketched Art           → estilo sketch
  - Silhouettes            → silhuetas
  - Line Art               → contornos
  - Technical Drawing      → desenho técnico

Environment:
  Requires Adobe Illustrator installed on Windows.
  Requires pywin32: pip install pywin32
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path

# Fix Windows console encoding for Unicode output
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

SUPPORTED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".bmp", ".gif", ".tif", ".tiff", ".psd", ".pct"}


# ── COM Connection ────────────────────────────────────────────────────────────

def connect_illustrator(timeout=60):
    """Connect to Illustrator via COM. Launches it if not running."""
    import pythoncom
    import win32com.client
    import pywintypes

    pythoncom.CoInitialize()

    try:
        app = win32com.client.GetActiveObject("Illustrator.Application")
        print("[OK] Connected to running Illustrator instance.")
        return app
    except pywintypes.com_error:
        pass

    print("[...] Launching Illustrator (may take up to 60s)...")
    app = win32com.client.Dispatch("Illustrator.Application")

    start = time.time()
    while time.time() - start < timeout:
        try:
            _ = app.Name
            print(f"[OK] Illustrator ready ({int(time.time() - start)}s).")
            return app
        except Exception:
            time.sleep(2)

    raise TimeoutError(f"Illustrator did not respond within {timeout}s.")


# ── JSX Execution ─────────────────────────────────────────────────────────────

def run_jsx(app, jsx_path, config_path):
    """Execute JSX script in Illustrator with injected config path."""
    jsx_file = Path(jsx_path).resolve()
    if not jsx_file.exists():
        raise FileNotFoundError(f"JSX script not found: {jsx_file}")

    config_file = Path(config_path).resolve()
    if not config_file.exists():
        raise FileNotFoundError(f"Config file not found: {config_file}")

    jsx_content = jsx_file.read_text(encoding="utf-8")
    config_path_jsx = str(config_file).replace("\\", "/")
    injection = f'var CONFIG_PATH = "{config_path_jsx}";\n'
    jsx_content = injection + jsx_content

    print("[...] Executing vectorization in Illustrator...")
    try:
        result = app.DoJavaScript(jsx_content)
        print("[OK] Vectorization completed.")
        return result
    except Exception as e:
        raise RuntimeError(f"JSX execution failed: {e}")


def read_result(config_path):
    """Read the result JSON written by the JSX script."""
    result_path = Path(config_path).resolve()
    result_path = result_path.with_name(result_path.stem + "_result.json")

    if not result_path.exists():
        return {"status": "error", "errors": ["Result file not written by JSX."]}

    with open(result_path, "r", encoding="utf-8") as f:
        return json.load(f)


# ── Config Generation ─────────────────────────────────────────────────────────

def collect_images(args):
    """Collect image paths from --images and/or --input-dir."""
    images = []

    if args.images:
        for img in args.images:
            p = Path(img).resolve()
            if p.exists() and p.suffix.lower() in SUPPORTED_EXTENSIONS:
                images.append(str(p).replace("\\", "/"))
            else:
                print(f"[WARN] Skipping: {img} (not found or unsupported format)")

    if args.input_dir:
        input_dir = Path(args.input_dir).resolve()
        if input_dir.is_dir():
            for f in sorted(input_dir.iterdir()):
                if f.suffix.lower() in SUPPORTED_EXTENSIONS:
                    images.append(str(f).replace("\\", "/"))
            print(f"[OK] Found {len(images)} images in {input_dir}")
        else:
            print(f"[WARN] Input directory not found: {input_dir}")

    return images


def build_config(args, images):
    """Build config JSON from CLI arguments."""
    config = {
        "images": images,
        "output_dir": str(Path(args.output_dir).resolve()).replace("\\", "/"),
        "preset": args.preset,
        "formats": args.formats,
        "color_space": args.color_space,
        "tracing_options": {},
    }

    if args.output_name:
        config["output_name"] = args.output_name

    if args.ignore_white:
        config["tracing_options"]["ignore_white"] = True
    if args.threshold is not None:
        config["tracing_options"]["threshold"] = args.threshold
    if args.max_colors is not None:
        config["tracing_options"]["max_colors"] = args.max_colors

    return config


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Vetoriza imagens raster via Image Trace no Adobe Illustrator."
    )
    parser.add_argument("--images", nargs="+", help="Imagens para vetorizar (PNG, JPG, TIFF, PSD, BMP)")
    parser.add_argument("--input-dir", help="Pasta com imagens para vetorizar (batch)")
    parser.add_argument("--config", help="Caminho do config JSON (alternativa aos flags)")
    parser.add_argument("--output-dir", default=".tmp/vectorized", help="Diretório de saída (default: .tmp/vectorized)")
    parser.add_argument("--output-name", help="Nome base do arquivo de saída (só para imagem única)")

    # Tracing settings
    parser.add_argument("--preset", default="High Fidelity Photo",
                        help="Preset do Image Trace (default: High Fidelity Photo)")
    parser.add_argument("--formats", nargs="+", default=["svg"],
                        choices=["svg", "ai", "eps", "pdf", "png"],
                        help="Formatos de exportação (default: svg)")
    parser.add_argument("--color-space", default="RGB", choices=["RGB", "CMYK"],
                        help="Espaço de cor do documento (default: RGB)")

    # Advanced tracing options
    parser.add_argument("--ignore-white", action="store_true", help="Ignorar branco no tracing")
    parser.add_argument("--threshold", type=int, help="Threshold para P&B (0-255)")
    parser.add_argument("--max-colors", type=int, help="Número máximo de cores")

    parser.add_argument("--timeout", type=int, default=60, help="Timeout COM em segundos (default: 60)")
    parser.add_argument("--list-presets", action="store_true", help="Listar presets disponíveis e sair")

    args = parser.parse_args()

    # Resolve output dir
    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    jsx_path = Path(__file__).parent / "jsx" / "vectorize_image.jsx"
    if not jsx_path.exists():
        print(f"[ERROR] JSX script not found: {jsx_path}")
        sys.exit(1)

    # ── List presets mode ─────────────────────────────────────────────────
    if args.list_presets:
        app = connect_illustrator(timeout=args.timeout)
        # Get presets via a quick JSX call
        presets_jsx = 'var p = app.tracingPresetsList; var r = ""; for (var i=0; i<p.length; i++) r += i + ": " + p[i] + "\\n"; r;'
        result = app.DoJavaScript(presets_jsx)
        print("\nPresets disponíveis no Image Trace:")
        print(result)
        sys.exit(0)

    # ── Build or load config ──────────────────────────────────────────────
    if args.config:
        config_path = Path(args.config).resolve()
        if not config_path.exists():
            print(f"[ERROR] Config file not found: {config_path}")
            sys.exit(1)
    else:
        images = collect_images(args)
        if not images:
            print("[ERROR] No images provided. Use --images or --input-dir.")
            sys.exit(1)

        config = build_config(args, images)
        config_path = output_dir / "vectorize_config.json"
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        print(f"[OK] Config generated: {config_path}")

    # ── Execute ───────────────────────────────────────────────────────────
    try:
        app = connect_illustrator(timeout=args.timeout)
        jsx_result = run_jsx(app, jsx_path, config_path)

        result = read_result(config_path)

        # Report
        print("\n" + "=" * 60)
        print("RESULTADO DA VETORIZAÇÃO")
        print("=" * 60)
        print(f"  Status:              {result.get('status', 'unknown')}")
        print(f"  Imagens processadas: {result.get('images_processed', 0)}")
        print(f"  Preset usado:        {args.preset if not args.config else '(from config)'}")

        if result.get("exports"):
            print(f"  Arquivos gerados:")
            for exp in result["exports"]:
                print(f"    → {exp}")

        if result.get("presets_available"):
            print(f"\n  Presets disponíveis: {len(result['presets_available'])}")

        if result.get("errors"):
            print(f"\n  Avisos:")
            for err in result["errors"]:
                print(f"    - {err}")

        print("=" * 60)

        # Write manifest
        manifest_path = output_dir / "manifest.json"
        manifest = {
            "config": str(config_path),
            "result": result,
        }
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, ensure_ascii=False, indent=2)
        print(f"\n[OK] Manifest: {manifest_path}")

        if result.get("status") == "error":
            sys.exit(1)

    except FileNotFoundError as e:
        print(f"\n[ERROR] {e}")
        sys.exit(1)
    except TimeoutError as e:
        print(f"\n[ERROR] {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
