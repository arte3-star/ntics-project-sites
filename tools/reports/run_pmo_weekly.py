#!/usr/bin/env python3
"""
run_pmo_weekly.py
Orquestrador end-to-end do relatório semanal PMO.
Janela: semana corrida (seg-dom passado + próxima seg-dom).
Modos: dry-run | draft | send.
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
    today_brt, ROOT,
)


def run(cmd: list[str]) -> int:
    print(f"[run-weekly] $ {' '.join(cmd)}")
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
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()

    ref = today_brt() if not args.date else datetime.strptime(args.date, "%Y-%m-%d").date()

    py = sys.executable
    integ = ROOT / "tools" / "integrations"
    rep = ROOT / "tools" / "reports"
    out_dir = ROOT / "output" / "relatorios" / "pmo-semanal"
    out_dir.mkdir(exist_ok=True, parents=True)

    print(f"[run-weekly] mode={args.mode} date={ref.isoformat()}")

    print("[run-weekly] Fase 1/4: Pull projetos (janela 14 dias)")
    cmd = [py, "-X", "utf8", str(integ / "clickup_pull_projetos_ntics.py"),
           "--cutoff-hours", "336"]
    if args.limit:
        cmd += ["--limit", str(args.limit)]
    if run(cmd) != 0:
        sys.exit(1)

    print("[run-weekly] Fase 2/4: Agregar métricas semanais")
    if run([py, "-X", "utf8", str(rep / "aggregate_pmo_weekly.py"),
            "--date", ref.isoformat()]) != 0:
        sys.exit(1)

    print("[run-weekly] Fase 3/4: Resumo executivo (Haiku)")
    cmd = [py, "-X", "utf8", str(rep / "generate_weekly_summary.py")]
    if args.no_llm:
        cmd.append("--no-llm")
    if run(cmd) != 0:
        sys.exit(1)

    print("[run-weekly] Fase 4/4: Render HTML + auto-review")
    out_html = out_dir / f"{ref.isoformat()}.html"
    if run([py, "-X", "utf8", str(rep / "render_pmo_weekly.py"),
            "--output", str(out_html)]) != 0:
        sys.exit(2)

    print(f"[run-weekly] HTML pronto: {out_html}")

    if args.mode == "dry-run":
        print("[run-weekly] Abrindo no navegador (dry-run)")
        try:
            os.startfile(str(out_html))
        except AttributeError:
            run(["xdg-open", str(out_html)])
        return

    print(f"[run-weekly] Email ({args.mode})")
    cmd = [py, "-X", "utf8", str(rep / "send_pmo_email.py"),
           "--html", str(out_html),
           "--mode", args.mode,
           "--date", ref.isoformat(),
           "--subject-kind", "weekly"]
    if run(cmd) != 0:
        print("[run-weekly] envio falhou", file=sys.stderr)
        sys.exit(3)

    print("[run-weekly] OK pipeline completo")


if __name__ == "__main__":
    main()
