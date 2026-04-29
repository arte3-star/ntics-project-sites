#!/usr/bin/env python3
"""
render_pmo_html.py
Renderiza o HTML final do relatório PMO juntando metrics + summary + template Jinja.
Aplica premailer para inline CSS (compatibilidade email).
Salva em output/relatorios/pmo-diario/YYYY-MM-DD.html.
Faz auto-review bloqueante (sem em-dash, seções presentes, mínimo de tamanho).
"""

import re
import sys
import argparse
from pathlib import Path
from datetime import date, datetime

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from reports._common import (
    load_config, ensure_dirs, setup_utf8_stdout, read_json, write_json,
    today_brt, OUTPUT_DIR, TMP_DIR,
)


MESES_PT = ["janeiro", "fevereiro", "março", "abril", "maio", "junho",
            "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"]
DIAS_PT = ["segunda-feira", "terça-feira", "quarta-feira", "quinta-feira",
           "sexta-feira", "sábado", "domingo"]


def data_extenso(d: date) -> str:
    return f"{DIAS_PT[d.weekday()]}, {d.day} de {MESES_PT[d.month - 1]} de {d.year}"


def data_curta(d: date) -> str:
    return d.strftime("%d/%m")


def br_date(iso: str | None) -> str:
    if not iso:
        return "-"
    try:
        return date.fromisoformat(iso[:10]).strftime("%d/%m")
    except ValueError:
        return iso


def enrich_for_template(metrics: dict, summary: dict) -> dict:
    today_iso = metrics.get("today")
    today = date.fromisoformat(today_iso) if today_iso else today_brt()

    sprint = metrics.get("sprint", {}) or {}
    sprint_aderencia_pct = 0
    if sprint.get("available"):
        s = sprint["sprint"]
        s["start_br"] = br_date(s.get("start"))
        s["end_br"] = br_date(s.get("end"))
        for d in sprint.get("days", []):
            d["date_br"] = br_date(d["date"])
            d["is_today"] = d["date"] == today.isoformat()
        ad = sprint.get("aderencia_semana_pct")
        if ad is not None:
            sprint_aderencia_pct = int(round(ad * 100))

    def _enrich_views(buckets: list[list[dict]]):
        for bucket in buckets:
            for v in bucket or []:
                v["due_date_br"] = br_date(v.get("due_date"))

    for p in metrics.get("projects", []):
        _enrich_views([p.get("milestones_7d"), p.get("overdue"),
                       p.get("due_today"), p.get("due_7d"),
                       p.get("changes_24h"), p.get("blockers")])

    for coord in metrics.get("coordinators", []):
        for p in coord.get("projects", []):
            _enrich_views([p.get("milestones_7d"), p.get("overdue"),
                           p.get("due_today"), p.get("due_7d"),
                           p.get("changes_24h"), p.get("blockers")])

    for c in metrics.get("creative", []):
        _enrich_views([c.get("tasks_atrasadas"), c.get("tasks_proximas"),
                       c.get("tasks_outras")])

    return {
        "data_extenso": data_extenso(today),
        "data_curta": data_curta(today),
        "totals": metrics.get("totals", {}),
        "projects": metrics.get("projects", []),
        "coordinators": metrics.get("coordinators", []),
        "creative": metrics.get("creative", []),
        "blockers": metrics.get("blockers", []),
        "decisions": metrics.get("decisions_pendentes", []),
        "sprint": sprint,
        "sprint_aderencia_pct": sprint_aderencia_pct,
        "summary": summary,
    }


def render(template_path: Path, ctx: dict) -> str:
    from jinja2 import Environment, FileSystemLoader, select_autoescape
    env = Environment(
        loader=FileSystemLoader(str(template_path.parent)),
        autoescape=select_autoescape(["html"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    tpl = env.get_template(template_path.name)
    return tpl.render(**ctx)


def inline_css(html: str) -> str:
    try:
        from premailer import transform
        return transform(html, keep_style_tags=False, strip_important=False)
    except ImportError:
        return html


REQUIRED_SECTIONS = ["header", "resumo", "kpis", "saude", "design", "mudancas", "marcos", "decisoes", "footer"]
# Sprint section removed per user request


def auto_review(html: str) -> list[str]:
    errs = []
    if len(html) < 4000:
        errs.append(f"HTML muito curto ({len(html)} bytes)")
    if "{{" in html or "{%" in html:
        errs.append("placeholder Jinja não resolvido")
    if "\u2014" in html:
        errs.append("contém em-dash (—) — proibido")
    for s in REQUIRED_SECTIONS:
        if f'data-section="{s}"' not in html:
            errs.append(f"seção ausente: {s}")
    return errs


def main():
    setup_utf8_stdout()
    cfg = load_config()
    ensure_dirs()

    parser = argparse.ArgumentParser()
    parser.add_argument("--metrics", default=str(TMP_DIR / "pmo_metrics.json"))
    parser.add_argument("--summary", default=str(TMP_DIR / "pmo_summary.json"))
    parser.add_argument("--template", default=str(Path(__file__).parent / "templates" / "pmo_diario.html.j2"))
    parser.add_argument("--output", default=None)
    parser.add_argument("--quiet", action="store_true")
    parser.add_argument("--no-inline", action="store_true", help="Pular premailer")
    parser.add_argument("--allow-warnings", action="store_true", help="Não falhar em warnings de auto-review")
    args = parser.parse_args()

    metrics = read_json(Path(args.metrics))
    summary = read_json(Path(args.summary))

    today_iso = metrics.get("today") or today_brt().isoformat()
    out_path = Path(args.output) if args.output else OUTPUT_DIR / f"{today_iso}.html"
    out_path.parent.mkdir(exist_ok=True, parents=True)

    ctx = enrich_for_template(metrics, summary)
    html = render(Path(args.template), ctx)
    if not args.no_inline:
        html = inline_css(html)

    errs = auto_review(html)
    if errs:
        if args.allow_warnings:
            print("[render] WARN: " + "; ".join(errs), file=sys.stderr)
        else:
            print("[render] ERRO auto-review:", file=sys.stderr)
            for e in errs:
                print(f"  - {e}", file=sys.stderr)
            sys.exit(2)

    out_path.write_text(html, encoding="utf-8")
    if not args.quiet:
        print(f"[render] OK {len(html)} bytes -> {out_path}")


if __name__ == "__main__":
    main()
