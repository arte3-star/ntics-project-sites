#!/usr/bin/env python3
"""
generate_weekly_summary.py
Lê .tmp/pmo_weekly_metrics.json e gera resumo executivo via Haiku
em 3 parágrafos: bom (entregue) / foco (próxima) / recomendação (atenção PMO).
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


SYSTEM_PROMPT = """Voce e analista PMO de NTICS Projetos. Tom executivo, retrospectivo, objetivo.
Escreve em PT-BR. Nao usa travessao em-dash. Nao usa a sigla CSR. Nao usa emoji.
Maximo 80 palavras por paragrafo. Audiencia: diretoria.
Responde APENAS com o JSON pedido, sem texto extra."""


USER_TEMPLATE = """Relatorio semanal PMO. Janelas:
- Semana passada: {past_window}
- Proxima semana: {next_window}

Totais:
{totals}

Por coordenador (entregue / proxima):
{coords_brief}

Design e video:
{creative_brief}

Devolva JSON com 3 campos. Nada alem disso:
{{
  "bom": "1 paragrafo: o que foi entregue na semana, destaque coordenadores e marcos relevantes.",
  "foco": "1 paragrafo: o que esta planejado para a proxima semana, principais entregas e responsaveis.",
  "recomendacao": "1 paragrafo: alertas PMO, gargalos, decisoes a tomar, projetos sem movimento. Maximo 3 pontos."
}}"""


def build_brief(metrics: dict) -> dict:
    coords = []
    for c in metrics.get("coordinators", []):
        projs = ", ".join(f"{p['name'][:50]} ({p['total_entregues']}E/{p['total_proximas']}P)"
                          for p in c["projects"][:5])
        coords.append(f"- {c['name']}: {c['entregues']} entregue(s), {c['proximas']} para proxima | {projs}")

    creative = []
    for c in metrics.get("creative", []):
        creative.append(f"- {c['name']}: {c['total_entregues']} entregue(s), {c['total_proximas']} para proxima")

    pw = metrics.get("past_window", {})
    nw = metrics.get("next_window", {})
    return {
        "past_window": f"{pw.get('start')} a {pw.get('end')}",
        "next_window": f"{nw.get('start')} a {nw.get('end')}",
        "totals": metrics.get("totals", {}),
        "coords_brief": "\n".join(coords) or "(sem atividade)",
        "creative_brief": "\n".join(creative) or "(sem atividade)",
    }


def deterministic_fallback(metrics: dict) -> dict:
    t = metrics.get("totals", {})
    coords = metrics.get("coordinators", [])
    top = sorted(coords, key=lambda c: -c["entregues"])[:3]
    bom = (
        f"Resumo automatizado: {t.get('entregues', 0)} task(s) concluídas na semana em "
        f"{len(coords)} coordenador(es). Destaques: " +
        "; ".join(f"{c['name']} ({c['entregues']})" for c in top)
        if top else "Sem coordenador com entregas no período."
    )
    foco = (
        f"{t.get('proximas', 0)} task(s) planejadas para a próxima semana. "
        f"Design e vídeo: {t.get('creative_proximas', 0)} entregas previstas."
    )
    sem_mov = [c["name"] for c in coords if c["entregues"] == 0 and c["proximas"] == 0]
    if sem_mov:
        recomendacao = f"Atenção: coordenadores sem movimento na semana: {', '.join(sem_mov[:3])}."
    else:
        recomendacao = "Sem alertas críticos detectados automaticamente. Revisar relatório completo abaixo."
    return {"bom": bom, "foco": foco, "recomendacao": recomendacao}


def call_claude(cfg: dict, brief: dict) -> dict | None:
    try:
        from anthropic import Anthropic
    except ImportError:
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
            if all(k in data and isinstance(data[k], str) and len(data[k]) >= 40
                   for k in ("bom", "foco", "recomendacao")):
                return data
        except Exception as e:
            print(f"[summary-weekly] tentativa {attempt+1} falhou: {e}", file=sys.stderr)
    return None


def main():
    setup_utf8_stdout()
    load_env()
    cfg = load_config()
    ensure_dirs()

    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default=str(TMP_DIR / "pmo_weekly_metrics.json"))
    parser.add_argument("--output", default=str(TMP_DIR / "pmo_weekly_summary.json"))
    parser.add_argument("--no-llm", action="store_true")
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()

    metrics = read_json(Path(args.input))
    brief = build_brief(metrics)

    summary = None
    if not args.no_llm:
        summary = call_claude(cfg, brief)
    source = "haiku"
    if summary is None:
        summary = deterministic_fallback(metrics)
        source = "fallback"

    write_json(Path(args.output), {"source": source, **summary})
    if not args.quiet:
        print(f"[summary-weekly] OK ({source}) -> {args.output}")


if __name__ == "__main__":
    main()
