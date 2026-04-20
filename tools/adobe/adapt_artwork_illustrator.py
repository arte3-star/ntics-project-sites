"""
adapt_artwork_illustrator.py — Adapta arte de projeto com identidade visual do cliente.

Controla o Adobe Illustrator via COM (Windows) para:
  1. Abrir arquivo de arte (.ai, .eps, .svg, .pdf)
  2. Trocar cores CMYK conforme paleta do cliente
  3. Posicionar logo do cliente
  4. Substituir fontes
  5. Exportar PDF vetorial (PDF/X-4) e/ou SVG

Usage:
  python tools/adapt_artwork_illustrator.py \
    --artwork "C:/projetos/arte_base.ai" \
    --config .tmp/adapt_config.json \
    --output-dir .tmp/adapted

  python tools/adapt_artwork_illustrator.py \
    --artwork "C:/projetos/arte_base.ai" \
    --colors "64,0,69,33>100,50,0,0" "100,17,0,55>0,80,95,0" \
    --logo "C:/projetos/logos/cliente.ai" \
    --logo-position top-right \
    --output-dir .tmp/adapted \
    --export pdf svg

Config JSON schema:
  {
    "client_name": "Empresa X",
    "color_map": [{"from_cmyk": [C,M,Y,K], "to_cmyk": [C,M,Y,K]}],
    "color_tolerance": 5,
    "logo": {"file": "path", "target_layer": "Logo", "position": "top-right", "max_width_mm": 60},
    "fonts": [{"from": "FontName-Bold", "to": "NewFont-Bold"}],
    "export": {"pdf_preset": "PDF/X-4", "bleed_mm": 3, "svg": true}
  }

Environment:
  Requires Adobe Illustrator (any recent version) installed on Windows.
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


# ── COM Connection ────────────────────────────────────────────────────────────

def connect_illustrator(timeout=60):
    """Connect to Illustrator via COM. Launches it if not running."""
    import pythoncom
    import win32com.client
    import pywintypes

    pythoncom.CoInitialize()

    # Try to get running instance first
    try:
        app = win32com.client.GetActiveObject("Illustrator.Application")
        print("[OK] Connected to running Illustrator instance.")
        return app
    except pywintypes.com_error:
        pass

    # Launch Illustrator
    print("[...] Launching Illustrator (may take up to 60s)...")
    app = win32com.client.Dispatch("Illustrator.Application")

    # Wait until Illustrator is responsive
    start = time.time()
    while time.time() - start < timeout:
        try:
            _ = app.Name
            print(f"[OK] Illustrator ready ({int(time.time() - start)}s).")
            return app
        except Exception:
            time.sleep(2)

    raise TimeoutError(f"Illustrator did not respond within {timeout}s.")


def open_artwork(app, artwork_path):
    """Open an artwork file in Illustrator."""
    path = Path(artwork_path).resolve()
    if not path.exists():
        raise FileNotFoundError(f"Artwork file not found: {path}")

    supported = {".ai", ".eps", ".svg", ".pdf"}
    if path.suffix.lower() not in supported:
        raise ValueError(f"Unsupported file format: {path.suffix}. Supported: {', '.join(supported)}")

    # Check if file is already open
    try:
        for i in range(app.Documents.Count):
            doc = app.Documents.Item(i + 1)
            if Path(doc.FullName).resolve() == path:
                print(f"[OK] Artwork already open: {path.name}")
                return doc
    except Exception:
        pass

    # Open the file
    print(f"[...] Opening artwork: {path.name}")
    doc = app.Open(str(path))
    print(f"[OK] Artwork opened: {path.name}")
    return doc


# ── JSX Execution ─────────────────────────────────────────────────────────────

def run_jsx(app, jsx_path, config_path):
    """Execute JSX script in Illustrator with injected config path."""
    jsx_file = Path(jsx_path).resolve()
    if not jsx_file.exists():
        raise FileNotFoundError(f"JSX script not found: {jsx_file}")

    config_file = Path(config_path).resolve()
    if not config_file.exists():
        raise FileNotFoundError(f"Config file not found: {config_file}")

    # Read JSX content
    jsx_content = jsx_file.read_text(encoding="utf-8")

    # Inject CONFIG_PATH variable (normalize path for JSX — forward slashes)
    config_path_jsx = str(config_file).replace("\\", "/")
    injection = f'var CONFIG_PATH = "{config_path_jsx}";\n'
    jsx_content = injection + jsx_content

    print("[...] Executing JSX script in Illustrator...")
    try:
        result = app.DoJavaScript(jsx_content)
        print("[OK] JSX execution completed.")
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

def build_config_from_args(args):
    """Build config JSON from CLI arguments when --config is not provided."""
    config = {
        "client_name": args.client_name or "adapted",
        "color_map": [],
        "color_tolerance": args.color_tolerance,
        "export": {
            "pdf_preset": "PDF/X-4",
            "bleed_mm": args.bleed_mm,
            "svg": "svg" in (args.export or ["pdf"]),
            "pdf": "pdf" in (args.export or ["pdf"]),
        },
        "output_dir": str(Path(args.output_dir).resolve()).replace("\\", "/"),
    }

    # Parse color mappings: "C,M,Y,K>C,M,Y,K"
    if args.colors:
        for color_str in args.colors:
            parts = color_str.split(">")
            if len(parts) != 2:
                raise ValueError(f"Invalid color mapping: {color_str}. Use: C,M,Y,K>C,M,Y,K")
            from_cmyk = [float(x.strip()) for x in parts[0].split(",")]
            to_cmyk = [float(x.strip()) for x in parts[1].split(",")]
            if len(from_cmyk) != 4 or len(to_cmyk) != 4:
                raise ValueError(f"CMYK needs 4 values: {color_str}")
            config["color_map"].append({"from_cmyk": from_cmyk, "to_cmyk": to_cmyk})

    # Logo
    if args.logo:
        config["logo"] = {
            "file": str(Path(args.logo).resolve()).replace("\\", "/"),
            "target_layer": args.logo_layer or "Logo",
            "position": args.logo_position or "top-right",
            "max_width_mm": args.logo_max_width or 60,
        }

    # Fonts: "FromFont>ToFont"
    if args.fonts:
        config["fonts"] = []
        for font_str in args.fonts:
            parts = font_str.split(">")
            if len(parts) != 2:
                raise ValueError(f"Invalid font mapping: {font_str}. Use: FromFont>ToFont")
            config["fonts"].append({"from": parts[0].strip(), "to": parts[1].strip()})

    return config


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Adapta arte de projeto com identidade visual do cliente via Adobe Illustrator."
    )
    parser.add_argument("--artwork", required=True, help="Caminho do arquivo de arte (.ai, .eps, .svg, .pdf)")
    parser.add_argument("--config", help="Caminho do config JSON (alternativa aos flags abaixo)")
    parser.add_argument("--output-dir", default=".tmp/adapted", help="Diretório de saída (default: .tmp/adapted)")
    parser.add_argument("--export", nargs="+", choices=["pdf", "svg"], default=["pdf"], help="Formatos de exportação")

    # Inline config (alternativa ao --config JSON)
    parser.add_argument("--client-name", help="Nome do cliente (usado no nome do arquivo)")
    parser.add_argument("--colors", nargs="+", help="Mapeamento de cores: 'C,M,Y,K>C,M,Y,K' (pode repetir)")
    parser.add_argument("--color-tolerance", type=float, default=5, help="Tolerância CMYK (default: 5)")
    parser.add_argument("--logo", help="Caminho do logo do cliente (.ai, .eps, .svg)")
    parser.add_argument("--logo-layer", default="Logo", help="Nome da layer alvo para o logo (default: Logo)")
    parser.add_argument("--logo-position", default="top-right",
                        choices=["top-left", "top-right", "bottom-left", "bottom-right", "center"],
                        help="Posição do logo (default: top-right)")
    parser.add_argument("--logo-max-width", type=float, default=60, help="Largura máx. do logo em mm (default: 60)")
    parser.add_argument("--fonts", nargs="+", help="Mapeamento de fontes: 'FontOriginal>FontNova' (pode repetir)")
    parser.add_argument("--bleed-mm", type=float, default=3, help="Sangria em mm (default: 3)")
    parser.add_argument("--timeout", type=int, default=60, help="Timeout para conexão COM em segundos (default: 60)")

    args = parser.parse_args()

    # Resolve paths
    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    jsx_path = Path(__file__).parent / "jsx" / "adapt_artwork.jsx"
    if not jsx_path.exists():
        print(f"[ERROR] JSX script not found: {jsx_path}")
        sys.exit(1)

    # Build or load config
    if args.config:
        config_path = Path(args.config).resolve()
        if not config_path.exists():
            print(f"[ERROR] Config file not found: {config_path}")
            sys.exit(1)
        # Inject output_dir into existing config
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
        config["output_dir"] = str(output_dir).replace("\\", "/")
        # Rewrite with output_dir
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
    else:
        config = build_config_from_args(args)
        config_path = output_dir / "adapt_config.json"
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        print(f"[OK] Config generated: {config_path}")

    # Execute pipeline
    app = None
    doc = None
    try:
        app = connect_illustrator(timeout=args.timeout)
        doc = open_artwork(app, args.artwork)
        jsx_result = run_jsx(app, jsx_path, config_path)

        # Read result
        result = read_result(config_path)

        # Report
        print("\n" + "=" * 60)
        print("RESULTADO DA ADAPTAÇÃO")
        print("=" * 60)
        print(f"  Status:          {result.get('status', 'unknown')}")
        print(f"  Cores trocadas:  {result.get('colors_replaced', 0)}")
        print(f"  Logo posicionado:{' Sim' if result.get('logo_placed') else ' Não'}")
        print(f"  Fontes alteradas:{result.get('fonts_changed', 0)}")

        if result.get("exports"):
            print(f"  Arquivos gerados:")
            for exp in result["exports"]:
                print(f"    → {exp}")

        if result.get("errors"):
            print(f"\n  ⚠ Avisos:")
            for err in result["errors"]:
                print(f"    - {err}")

        print("=" * 60)

        # Write manifest
        manifest_path = output_dir / "manifest.json"
        manifest = {
            "artwork": str(Path(args.artwork).resolve()),
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
