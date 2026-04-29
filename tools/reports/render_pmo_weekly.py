#!/usr/bin/env python3
"""
render_pmo_weekly.py
Renderiza HTML do relatório PMO semanal (template pmo_semanal.html.j2).
Aplica premailer (CSS inline) e auto-review.
"""

import sys
import argparse
from pathlib import Path
from datetime import date

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from reports._common import (
    load_config, ensure_dirs, setup_utf8_stdout, read_json,
    today_brt, OUTPUT_DIR, TMP_DIR,
)
from reports.render_pmo_html import render, inline_css

MESES_PT = ["janeiro", "fevereiro", "março", "abril", "maio", "junho",
            "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"]
DIAS_PT = ["segunda-feira", "terça-feira", "quarta-feira", "quinta-feira",
           "sexta-feira", "sábado", "domingo"]


def data_extenso(d: date) -> str:
    return f"{DIAS_PT[d.weekday()]}, {d.day} de {MESES_PT[d.month - 1]} de {d.year}"


def br_date(iso: str | None) -> str:
    if not iso:
        return "-"
    try:
        return date.fromisoformat(iso[:10]).strftime("%d/%m")
    except ValueError:
        return iso


REQUIRED_SECTIONS = ["header", "resumo", "kpis", "coordenadores", "design", "footer"]


def auto_review(html: str) -> list[str]:
    errs = []
    if len(html) < 3000:
        errs.append(f"HTML muito curto ({len(html)} bytes)")
    if "{{" in html or "{%" in html:
        errs.append("placeholder Jinja não resolvido")
    if "\u2014" in html:
        errs.append("contém em-dash (—) — proibido")
    for s in REQUIRED_SECTIONS:
        if f'data-section="{s}"' not in html:
            errs.append(f"seção ausente: {s}")
    return errs


def enrich(metrics: dict, summary: dict) -> dict:
    today_iso = metrics.get("ref_date")
    today = date.fromisoformat(today_iso) if today_iso else today_brt()
    pw = metrics.get("past_window", {})
    nw = metrics.get("next_window", {})

    for c in metrics.get("coordinators", []):
        for p in c.get("projects", []):
            for v in p.get("entregues", []):
                v["closed_date_br"] = br_date(v.get("closed_date"))
            for v in p.get("proximas", []):
                v["due_iso_br"] = br_date(v.get("due_iso"))

    for c in metrics.get("creative", []):
        for v in c.get("entregues", []):
            v["closed_date_br"] = br_date(v.get("closed_date"))
        for v in c.get("proximas", []):
            v["due_iso_br"] = br_date(v.get("due_iso"))

    return {
        "data_extenso": data_extenso(today),
        "data_curta": today.strftime("%d/%m"),
        "past_window_br": f"{br_date(pw.get('start'))} a {br_date(pw.get('end'))}",
        "next_window_br": f"{br_date(nw.get('start'))} a {br_date(nw.get('end'))}",
        "totals": metrics.get("totals", {}),
        "coordinators": metrics.get("coordinators", []),
        "creative": metrics.get("creative", []),
        "summary": summary,
    }


def main():
    setup_utf8_stdout()
    cfg = load_config()
    ensure_dirs()

    parser = argparse.ArgumentParser()
    parser.add_argument("--metrics", default=str(TMP_DIR / "pmo_weekly_metrics.json"))
    parser.add_argument("--summary", default=str(TMP_DIR / "pmo_weekly_summary.json"))
    parser.add_argument("--template", default=str(Path(__file__).parent / "templates" / "pmo_semanal.html.j2"))
    parser.add_argument("--output", default=None)
    parser.add_argument("--quiet", action="store_true")
    parser.add_argument("--no-inline", action="store_true")
    parser.add_argument("--allow-warnings", action="store_true")
    args = parser.parse_args()

    metrics = read_json(Path(args.metrics))
    summary = read_json(Path(args.summary))

    today_iso = metrics.get("ref_date") or today_brt().isoformat()
    out_path = Path(args.output) if args.output else OUTPUT_DIR.parent / "pmo-semanal" / f"{today_iso}.html"
    out_path.parent.mkdir(exist_ok=True, parents=True)

    ctx = enrich(metrics, summary)
    html = render(Path(args.template), ctx)
    if not args.no_inline:
        html = inline_css(html)

    errs = auto_review(html)
    if errs:
        if args.allow_warnings:
            print("[render-weekly] WARN: " + "; ".join(errs), file=sys.stderr)
        else:
            print("[render-weekly] ERRO auto-review:", file=sys.stderr)
            for e in errs:
                print(f"  - {e}", file=sys.stderr)
            sys.exit(2)

    out_path.write_text(html, encoding="utf-8")
    if not args.quiet:
        print(f"[render-weekly] OK {len(html)} bytes -> {out_path}")


if __name__ == "__main__":
    main()
