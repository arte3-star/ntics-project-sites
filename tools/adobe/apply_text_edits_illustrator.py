"""
apply_text_edits_illustrator.py — Aplica edicoes de texto no Illustrator baseado em comentarios de PDF.

Pipeline completo:
  1. Extrai anotacoes/comentarios do PDF revisado (via PyMuPDF)
  2. Gera JSON com mapeamento de edicoes (replace, delete, insert)
  3. Permite revisao/confirmacao do usuario (modo interativo ou --auto)
  4. Aplica as edicoes no documento ativo do Illustrator via COM + JSX

Usage:
  # Pipeline completo: PDF -> extrair -> revisar -> aplicar no Illustrator
  python tools/apply_text_edits_illustrator.py --pdf "C:/revisao/arquivo_revisado.pdf"

  # Apenas extrair (gera JSON para revisao manual)
  python tools/apply_text_edits_illustrator.py --pdf "C:/revisao/arquivo.pdf" --extract-only

  # Aplicar JSON ja revisado diretamente no Illustrator
  python tools/apply_text_edits_illustrator.py --edits-json .tmp/pdf_edits.json

  # Modo dry-run: mostra o que seria feito sem alterar nada
  python tools/apply_text_edits_illustrator.py --pdf "C:/revisao/arquivo.pdf" --dry-run

  # Aplicar automaticamente (sem confirmacao)
  python tools/apply_text_edits_illustrator.py --pdf "C:/revisao/arquivo.pdf" --auto

  # Filtrar por confianca minima
  python tools/apply_text_edits_illustrator.py --pdf "C:/revisao/arquivo.pdf" --min-confidence medium

  # Match mode
  python tools/apply_text_edits_illustrator.py --pdf "C:/revisao/arquivo.pdf" --match-mode fuzzy

Environment:
  - Adobe Illustrator aberto com o documento correspondente
  - PyMuPDF: pip install PyMuPDF
  - pywin32: pip install pywin32
"""

import argparse
import json
import sys
import time
from pathlib import Path

# Fix Windows console encoding
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


# -- COM Connection (reused from adapt_artwork) --------------------------------

def connect_illustrator(timeout=60):
    """Connect to Illustrator via COM."""
    import pythoncom
    import win32com.client
    import pywintypes

    pythoncom.CoInitialize()

    try:
        app = win32com.client.GetActiveObject("Illustrator.Application")
        print("[OK] Conectado ao Illustrator.")
        return app
    except pywintypes.com_error:
        pass

    print("[...] Iniciando Illustrator (pode levar ate 60s)...")
    app = win32com.client.Dispatch("Illustrator.Application")

    start = time.time()
    while time.time() - start < timeout:
        try:
            _ = app.Name
            print(f"[OK] Illustrator pronto ({int(time.time() - start)}s).")
            return app
        except Exception:
            time.sleep(2)

    raise TimeoutError(f"Illustrator nao respondeu em {timeout}s.")


def run_jsx(app, jsx_path, config_path):
    """Execute JSX script in Illustrator."""
    jsx_file = Path(jsx_path).resolve()
    if not jsx_file.exists():
        raise FileNotFoundError(f"JSX not found: {jsx_file}")

    config_file = Path(config_path).resolve()

    jsx_content = jsx_file.read_text(encoding="utf-8")

    config_path_jsx = str(config_file).replace("\\", "/")
    injection = f'var CONFIG_PATH = "{config_path_jsx}";\n'
    jsx_content = injection + jsx_content

    print("[...] Executando JSX no Illustrator...")
    try:
        result = app.DoJavaScript(jsx_content)
        print("[OK] JSX executado.")
        return result
    except Exception as e:
        raise RuntimeError(f"JSX falhou: {e}")


def read_result(config_path):
    """Read result JSON written by JSX."""
    result_path = Path(config_path).resolve()
    result_path = result_path.with_name(result_path.stem + "_result.json")

    if not result_path.exists():
        return {"status": "error", "errors": ["Arquivo de resultado nao encontrado."]}

    with open(result_path, "r", encoding="utf-8") as f:
        return json.load(f)


# -- Extraction ----------------------------------------------------------------

def extract_pdf_edits(pdf_path, target_page=None):
    """Extract edits from PDF using extract_pdf_comments module."""
    # Import the extraction module
    tools_dir = Path(__file__).parent
    sys.path.insert(0, str(tools_dir))
    from extract_pdf_comments import extract_comments

    return extract_comments(pdf_path, target_page=target_page)


# -- Filtering -----------------------------------------------------------------

CONFIDENCE_LEVELS = {"high": 3, "medium": 2, "low": 1}


def filter_edits(edits, min_confidence="low"):
    """Filter edits by minimum confidence level."""
    min_level = CONFIDENCE_LEVELS.get(min_confidence, 1)
    return [
        e for e in edits
        if CONFIDENCE_LEVELS.get(e.get("confidence", "low"), 1) >= min_level
    ]


# -- Interactive review --------------------------------------------------------

def review_edits_interactive(edits):
    """Let user review and approve each edit interactively."""
    approved = []
    print(f"\n{'=' * 60}")
    print(f"REVISAO DE EDICOES ({len(edits)} encontradas)")
    print(f"{'=' * 60}")
    print("Para cada edicao, responda: [s]im / [n]ao / [e]ditar / [t]odas / [c]ancelar\n")

    for i, edit in enumerate(edits):
        conf = edit.get("confidence", "?")
        print(f"  [{i+1}/{len(edits)}] {edit['type'].upper()} (confianca: {conf})")

        if edit["type"] == "replace":
            print(f"    DE:   \"{edit['original_text'][:80]}\"")
            print(f"    PARA: \"{edit['new_text'][:80]}\"")
        elif edit["type"] == "delete":
            print(f"    REMOVER: \"{edit['original_text'][:80]}\"")
        elif edit["type"] == "insert":
            print(f"    INSERIR: \"{edit['new_text'][:80]}\"")
            if edit.get("original_text"):
                print(f"    CONTEXTO: \"{edit['original_text'][:60]}\"")

        if edit.get("comment"):
            print(f"    COMENTARIO: {edit['comment'][:80]}")

        try:
            resp = input("    Aplicar? [s/n/e/t/c]: ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print("\n[!] Cancelado.")
            return []

        if resp == "c":
            print("[!] Cancelado pelo usuario.")
            return []
        elif resp == "t":
            approved.extend(edits[i:])
            print(f"[OK] Aprovadas todas as {len(edits) - i} edicoes restantes.")
            break
        elif resp == "n":
            print("    -> Pulada.")
            continue
        elif resp == "e":
            try:
                new_text = input("    Novo texto: ").strip()
                edit["new_text"] = new_text
                if edit["type"] == "delete":
                    edit["type"] = "replace"
                approved.append(edit)
                print("    -> Editada e aprovada.")
            except (EOFError, KeyboardInterrupt):
                print("\n[!] Cancelado.")
                return []
        else:  # 's' or anything else = approve
            approved.append(edit)
            print("    -> Aprovada.")

    print(f"\n[OK] {len(approved)} edicoes aprovadas de {len(edits)} total.\n")
    return approved


# -- Build JSX config ----------------------------------------------------------

def build_jsx_config(edits, output_dir, match_mode="contains", case_sensitive=True, dry_run=False):
    """Build the config JSON for the JSX script."""
    jsx_edits = []
    for edit in edits:
        jsx_edit = {
            "type": edit["type"],
            "original_text": edit.get("original_text", ""),
            "new_text": edit.get("new_text", ""),
        }
        if edit.get("page"):
            jsx_edit["page"] = edit["page"]
        if edit["type"] == "insert" and edit.get("original_text"):
            jsx_edit["after_text"] = edit["original_text"]
        jsx_edits.append(jsx_edit)

    return {
        "edits": jsx_edits,
        "match_mode": match_mode,
        "case_sensitive": case_sensitive,
        "dry_run": dry_run,
        "output_dir": str(Path(output_dir).resolve()).replace("\\", "/"),
    }


# -- Main ----------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Aplica edicoes de texto no Illustrator baseado em comentarios de PDF."
    )

    # Input sources (at least one required)
    parser.add_argument("--pdf", help="PDF revisado com comentarios")
    parser.add_argument("--edits-json", help="JSON com edicoes ja extraidas (pula extracao)")
    parser.add_argument("--page", type=int, help="Processar apenas uma pagina do PDF")

    # Behavior
    parser.add_argument("--extract-only", action="store_true", help="Apenas extrair, nao aplicar")
    parser.add_argument("--dry-run", action="store_true", help="Simular sem alterar o documento")
    parser.add_argument("--auto", action="store_true", help="Aplicar sem confirmacao interativa")
    parser.add_argument("--min-confidence", default="low", choices=["high", "medium", "low"],
                        help="Confianca minima para incluir edicoes (default: low)")
    parser.add_argument("--match-mode", default="contains", choices=["exact", "contains", "fuzzy"],
                        help="Modo de busca de texto (default: contains)")
    parser.add_argument("--case-sensitive", action="store_true", default=True,
                        help="Busca case-sensitive (default: true)")
    parser.add_argument("--no-case-sensitive", action="store_false", dest="case_sensitive",
                        help="Busca case-insensitive")

    # Output
    parser.add_argument("--output-dir", default=".tmp/text_edits", help="Diretorio de saida")
    parser.add_argument("--timeout", type=int, default=60, help="Timeout COM em segundos")

    args = parser.parse_args()

    if not args.pdf and not args.edits_json:
        parser.error("Informe --pdf ou --edits-json")

    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    # Step 1: Get edits
    if args.edits_json:
        # Load pre-existing edits JSON
        edits_path = Path(args.edits_json).resolve()
        if not edits_path.exists():
            print(f"[ERROR] JSON nao encontrado: {edits_path}")
            sys.exit(1)

        with open(edits_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        edits = data.get("edits", [])
        notes = data.get("notes", [])
        print(f"[OK] Carregadas {len(edits)} edicoes de {edits_path.name}")

    else:
        # Extract from PDF
        pdf_path = Path(args.pdf).resolve()
        if not pdf_path.exists():
            print(f"[ERROR] PDF nao encontrado: {pdf_path}")
            sys.exit(1)

        print(f"[...] Extraindo comentarios de: {pdf_path.name}")
        data = extract_pdf_edits(str(pdf_path), target_page=args.page)

        edits = data.get("edits", [])
        notes = data.get("notes", [])

        # Save extracted data
        edits_json_path = output_dir / "pdf_edits.json"
        with open(edits_json_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"[OK] Extracao salva em: {edits_json_path}")

    # Report extraction
    print(f"\n  Edicoes encontradas: {len(edits)}")
    print(f"  Notas/avisos:        {len(notes)}")

    if not edits:
        print("\n[!] Nenhuma edicao de texto encontrada no PDF.")
        if notes:
            print("    Existem notas que podem precisar de interpretacao manual.")
            print("    Veja o JSON de saida para detalhes.")
        sys.exit(0)

    # Step 2: Filter by confidence
    edits = filter_edits(edits, args.min_confidence)
    print(f"  Apos filtro (>= {args.min_confidence}): {len(edits)}")

    if not edits:
        print(f"\n[!] Nenhuma edicao com confianca >= {args.min_confidence}.")
        sys.exit(0)

    # Step 3: Extract only?
    if args.extract_only:
        print(f"\n[OK] Modo --extract-only. Edicoes salvas em {output_dir}/pdf_edits.json")
        print("     Revise o JSON e execute novamente com --edits-json para aplicar.")
        sys.exit(0)

    # Step 4: Review
    if not args.auto:
        edits = review_edits_interactive(edits)
        if not edits:
            print("[!] Nenhuma edicao aprovada.")
            sys.exit(0)
    else:
        print(f"\n[!] Modo --auto: aplicando {len(edits)} edicoes sem confirmacao.")

    # Step 5: Build JSX config
    jsx_config = build_jsx_config(
        edits, output_dir,
        match_mode=args.match_mode,
        case_sensitive=args.case_sensitive,
        dry_run=args.dry_run,
    )

    config_path = output_dir / "edits_config.json"
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(jsx_config, f, ensure_ascii=False, indent=2)
    print(f"[OK] Config JSX: {config_path}")

    # Step 6: Connect to Illustrator and execute
    jsx_path = Path(__file__).parent / "jsx" / "apply_text_edits.jsx"
    if not jsx_path.exists():
        print(f"[ERROR] JSX nao encontrado: {jsx_path}")
        sys.exit(1)

    try:
        app = connect_illustrator(timeout=args.timeout)

        # Verify there's an active document
        try:
            doc_name = app.ActiveDocument.Name
            print(f"[OK] Documento ativo: {doc_name}")
        except Exception:
            print("[ERROR] Nenhum documento aberto no Illustrator.")
            print("        Abra o arquivo .ai correspondente e tente novamente.")
            sys.exit(1)

        # Execute JSX
        jsx_result = run_jsx(app, jsx_path, config_path)
        result = read_result(config_path)

        # Report
        print(f"\n{'=' * 60}")
        print("RESULTADO DA APLICACAO")
        print(f"{'=' * 60}")
        print(f"  Status:        {result.get('status', 'unknown')}")
        print(f"  Total edicoes: {result.get('total_edits', 0)}")
        print(f"  Aplicadas:     {result.get('applied', 0)}")
        print(f"  Nao encontr.:  {result.get('not_found', 0)}")
        print(f"  Puladas:       {result.get('skipped', 0)}")

        if args.dry_run:
            print(f"\n  [DRY RUN] Nenhuma alteracao foi feita no documento.")

        if result.get("details"):
            print(f"\n  DETALHES:")
            for d in result["details"]:
                status_icon = {
                    "applied": "+",
                    "would_apply": "~",
                    "not_found": "X",
                    "skipped": "-"
                }.get(d["status"], "?")
                print(f"    [{status_icon}] {d['type'].upper()}: {d.get('original_text', '')[:50]} -> {d['status']}")
                if d.get("frame_name"):
                    print(f"        Frame: {d['frame_name']}")

        if result.get("errors"):
            print(f"\n  ERROS:")
            for err in result["errors"]:
                print(f"    - {err}")

        print(f"{'=' * 60}")

        # Save full report
        report_path = output_dir / "apply_report.json"
        report = {
            "source": str(Path(args.pdf).resolve()) if args.pdf else str(Path(args.edits_json).resolve()),
            "config": str(config_path),
            "result": result,
            "edits_submitted": len(edits),
        }
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print(f"\n[OK] Relatorio: {report_path}")

        if result.get("status") == "error":
            sys.exit(1)

    except FileNotFoundError as e:
        print(f"\n[ERROR] {e}")
        sys.exit(1)
    except TimeoutError as e:
        print(f"\n[ERROR] {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Erro inesperado: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
