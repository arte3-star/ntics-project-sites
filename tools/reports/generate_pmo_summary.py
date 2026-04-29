#!/usr/bin/env python3
"""
generate_pmo_summary.py
Lê .tmp/pmo_metrics.json e chama Claude Haiku para gerar resumo executivo
em 3 parágrafos (good / concern / decide_today). Salva em .tmp/pmo_summary.json.

Em falha do modelo, gera resumo determinístico a partir dos números.
"""

import os
import sys
import json
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from reports._common import (
    load_env, load_config, ensure_dirs, setup_utf8_stdout,
    write_json, read_json, TMP_DIR,
)


SYSTEM_PROMPT = """Voce e analista PMO da NTICS Projetos. Tom executivo, neutro, objetivo.
Escreve em PT-BR. Nao usa travessao em-dash. Nao usa a sigla CSR. Nao usa emoji.
Maximo 80 palavras por paragrafo. Audiencia: diretoria (Lucas, Bruna, Abilio).
Responde APENAS com o JSON pedido, sem texto extra."""


USER_TEMPLATE = """Metricas de hoje ({today}):

Totais: {totals}

Projetos por saude:
{projects_brief}

Top 5 atrasados (ordenados por dias de atraso):
{top_overdue}

Bloqueios ativos:
{blockers_brief}

Decisoes pendentes:
{decisions_brief}

Aderencia da Sprint {sprint_num} ({sprint_window}): {sprint_aderencia}

Devolva JSON com 3 campos preenchidos. Nada alem disso:
{{
  "good": "1 paragrafo com o que avancou bem nas ultimas 24h e projetos verdes.",
  "concern": "1 paragrafo com o que preocupa: vermelhos, atrasos crescentes, bloqueios novos.",
  "decide_today": "1 paragrafo listando ate 3 decisoes que a diretoria precisa tomar nas proximas 8 horas. Cite projeto e responsavel quando relevante."
}}"""


def build_brief_inputs(metrics: dict) -> dict:
    projs = metrics.get("projects", [])
    projects_brief = []
    for p in projs:
        projects_brief.append(
            f"- [{p['health']}] {p['name']} | fase {p['fase_dominante']} | "
            f"{p['total_open']} abertas, {len(p['overdue'])} atrasadas | resp {p['responsavel']}"
        )

    overdue_with_days = []
    for p in projs:
        for o in p.get("overdue", []):
            overdue_with_days.append({**o, "project": p["name"]})
    overdue_with_days.sort(key=lambda v: v.get("due_date") or "")
    top_overdue = []
    for o in overdue_with_days[:5]:
        top_overdue.append(f"- {o['name']} | {o['project']} | due {o.get('due_date')}")

    blockers = metrics.get("blockers", [])
    blockers_brief = [f"- {b['name']} | {b.get('project','')} | {b.get('reason','')}" for b in blockers]

    decisions = metrics.get("decisions_pendentes", [])
    decisions_brief = [f"- {d['name']} | {d.get('project','')}" for d in decisions]

    sprint = metrics.get("sprint", {})
    sprint_num = sprint.get("sprint", {}).get("num") if sprint.get("available") else "n/a"
    sprint_window = ""
    sprint_aderencia = "n/a"
    if sprint.get("available"):
        s = sprint["sprint"]
        sprint_window = f"{s.get('start')} -> {s.get('end')}"
        ad = sprint.get("aderencia_semana_pct")
        if ad is not None:
            sprint_aderencia = f"{int(round(ad * 100))}% ({sprint['totais']['entregues_no_prazo_ate_hoje']}/{sprint['totais']['previstas_ate_hoje']} no prazo)"

    return {
        "today": metrics.get("today", ""),
        "totals": metrics.get("totals", {}),
        "projects_brief": "\n".join(projects_brief) or "(nenhum)",
        "top_overdue": "\n".join(top_overdue) or "(nenhum)",
        "blockers_brief": "\n".join(blockers_brief) or "(nenhum)",
        "decisions_brief": "\n".join(decisions_brief) or "(nenhum)",
        "sprint_num": sprint_num,
        "sprint_window": sprint_window,
        "sprint_aderencia": sprint_aderencia,
    }


def deterministic_fallback(metrics: dict) -> dict:
    t = metrics.get("totals", {})
    sprint = metrics.get("sprint", {})
    ad = ""
    if sprint.get("available"):
        adp = sprint.get("aderencia_semana_pct")
        if adp is not None:
            ad = f" Aderência da sprint até hoje: {int(round(adp * 100))}%."
    good = (
        f"Resumo automatizado: {t.get('changes_24h', 0)} mudanças nas últimas 24h em "
        f"{t.get('projects', 0)} projetos.{ad}"
    )
    concern = (
        f"{t.get('overdue', 0)} tasks atrasadas, "
        f"{t.get('blockers', 0)} bloqueios identificados, "
        f"{t.get('milestones_7d', 0)} marcos nos próximos 7 dias."
    )
    blockers = metrics.get("blockers", [])[:3]
    if blockers:
        items = "; ".join(f"{b['name']} ({b.get('project','')})" for b in blockers)
        decide = f"Avaliar bloqueios: {items}."
    else:
        decide = "Sem decisões críticas detectadas automaticamente. Revisar relatório completo abaixo."
    return {"good": good, "concern": concern, "decide_today": decide}


def call_claude(cfg: dict, brief: dict) -> dict | None:
    try:
        from anthropic import Anthropic
    except ImportError:
        print("[summary] anthropic SDK ausente, usando fallback", file=sys.stderr)
        return None

    client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    user = USER_TEMPLATE.format(**brief)

    for attempt in range(2):
        try:
            resp = client.messages.create(
                model=cfg["ai"]["model"],
                max_tokens=cfg["ai"]["max_tokens"],
                temperature=cfg["ai"]["temperature"] if attempt == 0 else 0,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": user}],
            )
            text = "".join(b.text for b in resp.content if hasattr(b, "text")).strip()
            if text.startswith("```"):
                text = text.strip("`")
                if text.startswith("json"):
                    text = text[4:].strip()
            data = json.loads(text)
            if all(k in data and isinstance(data[k], str) and len(data[k]) >= 50 for k in ("good", "concern", "decide_today")):
                return data
            print(f"[summary] resposta incompleta, tentativa {attempt+1}", file=sys.stderr)
        except Exception as e:
            print(f"[summary] tentativa {attempt+1} falhou: {e}", file=sys.stderr)
    return None


def main():
    setup_utf8_stdout()
    load_env()
    cfg = load_config()
    ensure_dirs()

    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default=str(TMP_DIR / "pmo_metrics.json"))
    parser.add_argument("--output", default=str(TMP_DIR / "pmo_summary.json"))
    parser.add_argument("--no-llm", action="store_true", help="Pular Claude e usar fallback determinístico")
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()

    metrics = read_json(Path(args.input))
    brief = build_brief_inputs(metrics)

    summary = None
    if not args.no_llm:
        summary = call_claude(cfg, brief)

    source = "haiku"
    if summary is None:
        summary = deterministic_fallback(metrics)
        source = "fallback"

    out = {"source": source, **summary}
    write_json(Path(args.output), out)
    if not args.quiet:
        print(f"[summary] OK ({source}) -> {args.output}")


if __name__ == "__main__":
    main()
