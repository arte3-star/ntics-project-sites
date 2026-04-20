"""
adapt_motion_aftereffects.py — Adapta template de motion graphics com dados do cliente.

Controla o Adobe After Effects via COM (Windows) + aerender para:
  1. Abrir projeto .aep template
  2. Trocar textos (nome do projeto, patrocinador, datas)
  3. Substituir footage (logo, imagens, vídeos)
  4. Trocar cores de shape layers, solids e textos
  5. Renderizar vídeo final (H.264, ProRes, etc.)

Usage:
  # Via config JSON (completo)
  python tools/adapt_motion_aftereffects.py \
    --project "C:/projetos/template.aep" \
    --config .tmp/motion_config.json \
    --output-dir .tmp/rendered

  # Via flags inline (simples)
  python tools/adapt_motion_aftereffects.py \
    --project "C:/projetos/template.aep" \
    --comp "Main Comp" \
    --texts "Titulo>Projeto Statkraft" "Patrocinador>Statkraft Energias" \
    --footage "logo.png>C:/logos/statkraft.png" \
    --colors "255,0,0>0,100,200" \
    --output .tmp/rendered/statkraft.mp4

  # Só renderizar (sem alterações)
  python tools/adapt_motion_aftereffects.py \
    --project "C:/projetos/projeto.aep" \
    --comp "Final" \
    --output .tmp/rendered/video.mp4 \
    --render-only

Config JSON schema:
  {
    "comp_name": "Main Comp",
    "text_map": [
      {"layer_name": "Titulo", "new_text": "Projeto X"},
      {"find": "EMPRESA", "replace": "Statkraft"}
    ],
    "footage_map": [
      {"layer_name": "Logo", "new_file": "C:/logos/logo.png"},
      {"item_name": "background.jpg", "new_file": "C:/imgs/bg.jpg"}
    ],
    "color_map": [
      {"from_rgb": [255, 0, 0], "to_rgb": [0, 100, 200]}
    ],
    "color_tolerance": 0.05,
    "render": {
      "output_path": "C:/output/video.mp4",
      "output_template": "H.264 - Match Render Settings - 15 Mbps",
      "render_template": "Best Settings"
    },
    "save_as": "C:/projetos/projeto_adaptado.aep"
  }

Environment:
  Requires Adobe After Effects (any recent version) installed on Windows.
  Requires pywin32: pip install pywin32
  aerender.exe is used for rendering (found automatically).
"""

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

# Fix Windows console encoding for Unicode output
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# ── aerender path ─────────────────────────────────────────────────────────────

AERENDER_PATHS = [
    r"C:\Program Files\Adobe\Adobe After Effects 2026\Support Files\aerender.exe",
    r"C:\Program Files\Adobe\Adobe After Effects 2025\Support Files\aerender.exe",
    r"C:\Program Files\Adobe\Adobe After Effects 2024\Support Files\aerender.exe",
]


def find_aerender():
    """Find aerender.exe on the system."""
    for p in AERENDER_PATHS:
        if Path(p).exists():
            return p
    return None


# ── COM Connection ────────────────────────────────────────────────────────────

def connect_aftereffects(timeout=90):
    """Connect to After Effects via COM. Launches it if not running."""
    import pythoncom
    import win32com.client
    import pywintypes

    pythoncom.CoInitialize()

    # Try to get running instance first
    try:
        app = win32com.client.GetActiveObject("AfterEffects.Application")
        print("[OK] Connected to running After Effects instance.")
        return app
    except pywintypes.com_error:
        pass

    # Launch After Effects
    print("[...] Launching After Effects (may take up to 90s)...")
    app = win32com.client.Dispatch("AfterEffects.Application")

    # Wait until AE is responsive
    start = time.time()
    while time.time() - start < timeout:
        try:
            _ = app.project
            print(f"[OK] After Effects ready ({int(time.time() - start)}s).")
            return app
        except Exception:
            time.sleep(3)

    raise TimeoutError(f"After Effects did not respond within {timeout}s.")


def open_project(app, project_path):
    """Open an .aep project in After Effects."""
    path = Path(project_path).resolve()
    if not path.exists():
        raise FileNotFoundError(f"Project file not found: {path}")

    if path.suffix.lower() not in {".aep", ".aepx"}:
        raise ValueError(f"Unsupported project format: {path.suffix}. Use .aep or .aepx")

    print(f"[...] Opening project: {path.name}")
    app.Open(str(path))
    print(f"[OK] Project opened: {path.name}")


# ── JSX Execution ─────────────────────────────────────────────────────────────

def run_jsx(app, jsx_path, config_path):
    """Execute JSX script in After Effects with injected config path."""
    jsx_file = Path(jsx_path).resolve()
    if not jsx_file.exists():
        raise FileNotFoundError(f"JSX script not found: {jsx_file}")

    config_file = Path(config_path).resolve()
    if not config_file.exists():
        raise FileNotFoundError(f"Config file not found: {config_file}")

    # Read JSX content
    jsx_content = jsx_file.read_text(encoding="utf-8")

    # Inject CONFIG_PATH variable (forward slashes for JSX)
    config_path_jsx = str(config_file).replace("\\", "/")
    injection = f'var CONFIG_PATH = "{config_path_jsx}";\n'
    jsx_content = injection + jsx_content

    print("[...] Executing JSX script in After Effects...")
    try:
        result = app.DoScript(jsx_content)
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


# ── aerender Execution ────────────────────────────────────────────────────────

def render_with_aerender(project_path, comp_name=None, output_path=None,
                         output_template=None, render_template=None):
    """Render using aerender.exe (headless, no GUI needed)."""
    aerender = find_aerender()
    if not aerender:
        raise FileNotFoundError("aerender.exe not found. Is After Effects installed?")

    cmd = [aerender, "-project", str(Path(project_path).resolve())]

    if comp_name:
        cmd.extend(["-comp", comp_name])
    if output_path:
        # Ensure output directory exists
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        cmd.extend(["-output", str(Path(output_path).resolve())])
    if output_template:
        cmd.extend(["-OMtemplate", output_template])
    if render_template:
        cmd.extend(["-RStemplate", render_template])

    cmd.extend(["-close", "DO_NOT_SAVE_CHANGES"])

    print(f"\n[...] Rendering with aerender...")
    print(f"      Comp: {comp_name or '(render queue)'}")
    print(f"      Output: {output_path or '(from project settings)'}")

    try:
        process = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=3600,  # 1 hour max render time
        )
        if process.returncode == 0:
            print("[OK] Render completed successfully.")
            return True
        else:
            print(f"[ERROR] aerender exited with code {process.returncode}")
            if process.stderr:
                print(f"        {process.stderr[:500]}")
            return False
    except subprocess.TimeoutExpired:
        print("[ERROR] Render timed out after 1 hour.")
        return False


# ── Config Generation ─────────────────────────────────────────────────────────

def build_config_from_args(args):
    """Build config JSON from CLI arguments when --config is not provided."""
    config = {
        "comp_name": args.comp,
        "text_map": [],
        "footage_map": [],
        "color_map": [],
        "color_tolerance": 0.05,
    }

    # Parse text mappings: "LayerName>New Text"
    if args.texts:
        for text_str in args.texts:
            parts = text_str.split(">", 1)
            if len(parts) != 2:
                raise ValueError(f"Invalid text mapping: {text_str}. Use: LayerName>New Text")
            config["text_map"].append({
                "layer_name": parts[0].strip(),
                "new_text": parts[1].strip(),
            })

    # Parse footage mappings: "LayerOrItemName>NewFilePath"
    if args.footage:
        for f_str in args.footage:
            parts = f_str.split(">", 1)
            if len(parts) != 2:
                raise ValueError(f"Invalid footage mapping: {f_str}. Use: Name>FilePath")
            config["footage_map"].append({
                "layer_name": parts[0].strip(),
                "new_file": str(Path(parts[1].strip()).resolve()).replace("\\", "/"),
            })

    # Parse color mappings: "R,G,B>R,G,B" (0-255)
    if args.colors:
        for c_str in args.colors:
            parts = c_str.split(">")
            if len(parts) != 2:
                raise ValueError(f"Invalid color mapping: {c_str}. Use: R,G,B>R,G,B")
            from_rgb = [int(x.strip()) for x in parts[0].split(",")]
            to_rgb = [int(x.strip()) for x in parts[1].split(",")]
            if len(from_rgb) != 3 or len(to_rgb) != 3:
                raise ValueError(f"RGB needs 3 values: {c_str}")
            config["color_map"].append({"from_rgb": from_rgb, "to_rgb": to_rgb})

    # Render settings
    if args.output:
        config["render"] = {
            "output_path": str(Path(args.output).resolve()).replace("\\", "/"),
            "output_template": args.output_template,
            "render_template": args.render_template or "Best Settings",
        }

    # Save adapted project
    if args.save_as:
        config["save_as"] = str(Path(args.save_as).resolve()).replace("\\", "/")

    return config


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Adapta template de motion graphics com dados do cliente via Adobe After Effects."
    )
    parser.add_argument("--project", required=True, help="Caminho do projeto .aep template")
    parser.add_argument("--config", help="Caminho do config JSON (alternativa aos flags abaixo)")
    parser.add_argument("--output-dir", default=".tmp/rendered", help="Diretório de saída (default: .tmp/rendered)")

    # Composition
    parser.add_argument("--comp", help="Nome da composição alvo")

    # Inline config
    parser.add_argument("--texts", nargs="+", help="Textos: 'LayerName>Novo Texto' (pode repetir)")
    parser.add_argument("--footage", nargs="+", help="Footage: 'LayerName>NovoArquivo' (pode repetir)")
    parser.add_argument("--colors", nargs="+", help="Cores RGB: 'R,G,B>R,G,B' (pode repetir)")

    # Output
    parser.add_argument("--output", help="Caminho do vídeo de saída (ex: .tmp/rendered/video.mp4)")
    parser.add_argument("--output-template", help="Template de Output Module do AE (ex: 'H.264 - Match Render Settings - 15 Mbps')")
    parser.add_argument("--render-template", default="Best Settings", help="Template de Render Settings (default: Best Settings)")
    parser.add_argument("--save-as", help="Salvar projeto adaptado em novo caminho .aep")

    # Modes
    parser.add_argument("--render-only", action="store_true", help="Só renderizar, sem fazer alterações no projeto")
    parser.add_argument("--no-render", action="store_true", help="Só fazer alterações, sem renderizar")
    parser.add_argument("--use-aerender", action="store_true", help="Usar aerender.exe para renderizar (não precisa abrir AE GUI)")
    parser.add_argument("--timeout", type=int, default=90, help="Timeout para conexão COM em segundos (default: 90)")

    args = parser.parse_args()

    # Resolve output dir
    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    jsx_path = Path(__file__).parent / "jsx" / "adapt_motion.jsx"
    if not jsx_path.exists():
        print(f"[ERROR] JSX script not found: {jsx_path}")
        sys.exit(1)

    project_path = Path(args.project).resolve()
    if not project_path.exists():
        print(f"[ERROR] Project file not found: {project_path}")
        sys.exit(1)

    # ── Render-only mode (aerender, no COM needed) ────────────────────────
    if args.render_only:
        output_path = args.output or str(output_dir / (project_path.stem + ".mp4"))
        success = render_with_aerender(
            project_path=project_path,
            comp_name=args.comp,
            output_path=output_path,
            output_template=args.output_template,
            render_template=args.render_template,
        )
        sys.exit(0 if success else 1)

    # ── Full pipeline (COM + JSX + optional render) ───────────────────────

    # Build or load config
    if args.config:
        config_path = Path(args.config).resolve()
        if not config_path.exists():
            print(f"[ERROR] Config file not found: {config_path}")
            sys.exit(1)
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
    else:
        config = build_config_from_args(args)
        config_path = output_dir / "motion_config.json"
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        print(f"[OK] Config generated: {config_path}")

    # Connect and execute
    app = None
    try:
        app = connect_aftereffects(timeout=args.timeout)
        open_project(app, project_path)
        jsx_result = run_jsx(app, jsx_path, config_path)

        # Read result
        result = read_result(config_path)

        # Report
        print("\n" + "=" * 60)
        print("RESULTADO DA ADAPTAÇÃO")
        print("=" * 60)
        print(f"  Status:             {result.get('status', 'unknown')}")
        print(f"  Composição:         {result.get('comp_name', '-')}")
        print(f"  Textos trocados:    {result.get('texts_replaced', 0)}")
        print(f"  Footage trocado:    {result.get('footage_replaced', 0)}")
        print(f"  Cores trocadas:     {result.get('colors_replaced', 0)}")
        print(f"  Render na fila:     {'Sim' if result.get('render_queued') else 'Não'}")

        if result.get("errors"):
            print(f"\n  Avisos:")
            for err in result["errors"]:
                print(f"    - {err}")

        print("=" * 60)

        # Render via aerender if requested
        if not args.no_render and (args.output or (config.get("render") and config["render"].get("output_path"))):
            output_path = args.output or config["render"]["output_path"]

            if args.use_aerender:
                # Save project first, then render with aerender
                save_path = args.save_as or str(output_dir / (project_path.stem + "_adapted.aep"))
                try:
                    app.project.Save(save_path)
                    print(f"[OK] Project saved: {save_path}")
                except Exception as e:
                    print(f"[WARN] Could not save project: {e}")
                    save_path = str(project_path)

                render_with_aerender(
                    project_path=save_path,
                    comp_name=config.get("comp_name"),
                    output_path=output_path,
                    output_template=config.get("render", {}).get("output_template"),
                    render_template=config.get("render", {}).get("render_template"),
                )
            elif result.get("render_queued"):
                # Render via AE's render queue (already set up by JSX)
                print("\n[...] Starting render via AE render queue...")
                try:
                    app.project.renderQueue.Render()
                    print("[OK] Render completed.")
                except Exception as e:
                    print(f"[ERROR] Render failed: {e}")

        # Write manifest
        manifest_path = output_dir / "manifest.json"
        manifest = {
            "project": str(project_path),
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
