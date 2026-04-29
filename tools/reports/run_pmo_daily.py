#!/usr/bin/env python3
"""
run_pmo_daily.py
Orquestrador end-to-end do relatório diário PMO.

Modos:
  --mode dry-run  -> gera HTML local e abre no navegador (default)
  --mode draft    -> gera HTML + cria draft Gmail (não envia)
  --mode send     -> gera HTML + envia email + verifica entrega

Aborta cedo em feriado BR (configurável).
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path
from datetime import date, datetime

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from reports._common import (
    load_env, load_config, ensure_dirs, setup_utf8_stdout,
    today_brt, OUTPUT_DIR, ROOT,
)


def is_business_day(d: date) -> bool:
    if d.weekday() >= 5:
        return False
    try:
        import holidays
        br = holidays.country_holidays("BR", years=d.year)
        return d not in br
    except ImportError:
        return True


def run(cmd: list[str]) -> int:
    print(f"[run] $ {' '.join(cmd)}")
    return subprocess.call(cmd)


def main():
    setup_utf8_stdout()
    load_env()
    cfg = load_config()
    ensure_dirs()

    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["dry-run", "draft", "send"], default="dry-run")
    parser.add_argument("--date", help="YYYY-MM-DD (default: hoje BRT)")
    parser.add_argument("--no-llm", action="store_true")
    parser.add_argument("--skip-business-day-check", action="store_true")
    parser.add_argument("--limit", type=int, default=None, help="Limita listas (debug)")
    args = parser.parse_args()

    ref = today_brt() if not args.date else datetime.strptime(args.date, "%Y-%m-%d").date()

    if cfg["schedule"].get("skip_holidays_br") and not args.skip_business_day_check:
        if not is_business_day(ref):
            print(f"[run] {ref} não é dia útil, abortando.")
            sys.exit(0)

    py = sys.executable
    integ = ROOT / "tools" / "integrations"
    rep = ROOT / "tools" / "reports"

    print(f"[run] mode={args.mode} date={ref.isoformat()}")
    print("[run] Fase 1/5: Pull projetos")
    cmd = [py, "-X", "utf8", str(integ / "clickup_pull_projetos_ntics.py")]
    if args.limit:
        cmd += ["--limit", str(args.limit)]
    if run(cmd) != 0:
        sys.exit(1)

    print("[run] Fase 2/5: Agregar métricas")
    if run([py, "-X", "utf8", str(rep / "aggregate_pmo_metrics.py")]) != 0:
        sys.exit(1)

    print("[run] Fase 3/5: Comentários das tasks atrasadas")
    if run([py, "-X", "utf8", str(integ / "clickup_pull_overdue_comments.py")]) != 0:
        print("[run] WARN: comentários falharam, seguindo sem", file=sys.stderr)

    print("[run] Fase 4/5: Resumo executivo (Haiku)")
    cmd = [py, "-X", "utf8", str(rep / "generate_pmo_summary.py")]
    if args.no_llm:
        cmd.append("--no-llm")
    if run(cmd) != 0:
        sys.exit(1)

    print("[run] Fase 5/5: Render HTML + auto-review")
    out_html = OUTPUT_DIR / f"{ref.isoformat()}.html"
    if run([py, "-X", "utf8", str(rep / "render_pmo_html.py"), "--output", str(out_html)]) != 0:
        print("[run] auto-review reprovou. Verifique erros acima.", file=sys.stderr)
        sys.exit(2)

    print(f"[run] HTML pronto: {out_html}")

    if args.mode == "dry-run":
        print("[run] Abrindo HTML no navegador (modo dry-run)")
        try:
            os.startfile(str(out_html))
        except AttributeError:
            run(["xdg-open", str(out_html)])
        print("[run] OK dry-run finalizado")
        return

    print(f"[run] Email ({args.mode})")
    cmd = [py, "-X", "utf8", str(rep / "send_pmo_email.py"),
           "--html", str(out_html),
           "--mode", args.mode,
           "--date", ref.isoformat()]
    if run(cmd) != 0:
        print("[run] envio falhou. HTML local mantido.", file=sys.stderr)
        sys.exit(3)

    print("[run] OK pipeline completo")


if __name__ == "__main__":
    main()
