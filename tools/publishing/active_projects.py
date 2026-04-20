"""
active_projects.py

Query de projetos ativos para alimentar a secao "Projetos em Execucao"
da newsletter ESG em Foco.

Fonte: assets/projetos/_metadata-sites-2026.json (enriquecido via
tools/publishing/enrich_projects_metadata.py com status, start_date, end_date).

Uso:
    from tools.publishing.active_projects import get_active_projects
    ctx = get_active_projects(2026, 4)
    # {'visible': [...], 'extra_count': 3, 'mes_referencia': 'Abril/2026'}
"""

from __future__ import annotations

import json
import re
from calendar import monthrange
from datetime import date, timedelta as _timedelta
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent.parent
JSON_PATH = REPO_ROOT / "assets" / "projetos" / "_metadata-sites-2026.json"

MES_PT = {
    1: "Janeiro", 2: "Fevereiro", 3: "Marco", 4: "Abril",
    5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
    9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro",
}

# Override para manter acento correto (MES_PT eh sem acento para chave de lookup)
MES_PT_ACENTO = {
    1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
    5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
    9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro",
}


def _load_metadata(json_path: Path | None = None) -> list[dict]:
    path = Path(json_path) if json_path else JSON_PATH
    return json.loads(path.read_text(encoding="utf-8"))


def _is_active_in_month(project: dict, year: int, month: int) -> bool:
    start = project.get("start_date")
    end = project.get("end_date")
    if not start or not end:
        return False
    target_first = date(year, month, 1)
    target_last = date(year, month, monthrange(year, month)[1])
    s = date.fromisoformat(start)
    e = date.fromisoformat(end)
    return s <= target_last and e >= target_first


def _fmt_br(iso: str) -> str:
    """'2026-03-10' -> '10/03/2026'."""
    d = date.fromisoformat(iso)
    return d.strftime("%d/%m/%Y")


_PEC_RE = re.compile(r"\bPEC\b")


def _expand_pec(name: str) -> str:
    """PEC (isolado) -> Empreendedorismo e Cultura.
    Preserva uso como prefixo. Regra: so expande quando PEC aparece como
    palavra isolada E existe texto antes/depois.
    """
    if not name:
        return name
    return _PEC_RE.sub("Empreendedorismo e Cultura", name)


def _build_card(project: dict) -> dict:
    """Reduz o projeto ao formato esperado pelo template da newsletter."""
    sponsors = project.get("sponsors") or []
    cities = project.get("cities") or []
    return {
        "id": project.get("id"),
        "project_short_name": _expand_pec(project.get("project_short_name") or project.get("project_name", "")),
        "sponsors": sponsors,
        "cities": cities,
        "kv_url": project.get("kv_url", ""),
        "photo_url": project.get("photo_url", ""),
        "editorial_text": project.get("editorial_text", ""),
        "accent_color": project.get("accent_color") or "#005F73",
        "start_date": project.get("start_date"),
        "start_date_br": _fmt_br(project["start_date"]) if project.get("start_date") else "",
    }


def apply_overrides(ctx: dict, overrides: dict) -> dict:
    """Aplica overrides por id em ctx['visible'].
    overrides = {"119_pec": {"photo_url": "...", "editorial_text": "...", "project_short_name": "..."}, ...}
    """
    if not overrides:
        return ctx
    for card in ctx.get("visible", []):
        o = overrides.get(card["id"])
        if not o:
            continue
        for k, v in o.items():
            card[k] = v
    return ctx


def _starts_soon(project: dict, today: date, days: int) -> bool:
    s = project.get("start_date")
    if not s:
        return False
    s_d = date.fromisoformat(s)
    return today < s_d <= today + _timedelta(days=days)


def get_active_projects(
    year: int,
    month: int,
    limit: int = 4,
    lookahead_days: int = 60,
    ids: list[str] | None = None,
    json_path: Path | None = None,
) -> dict:
    """Retorna contexto para o template da newsletter.

    {
      "mes_referencia": "Abril/2026",
      "visible": [ {project_short_name, sponsors, cities, kv_url, accent_color,
                    start_date_br, ...}, ... ],  # max `limit`
      "extra_count": int,
      "total": int,
    }
    """
    all_p = _load_metadata(json_path)
    today = date.today()
    use_custom_order = False
    if ids:
        # Respeita ordem da lista (uso editorial)
        by_id = {p.get("id"): p for p in all_p}
        ativos = [by_id[i] for i in ids if i in by_id]
        use_custom_order = True
    else:
        ativos = [
            p for p in all_p
            if p.get("status") == "ativo"
            and (_is_active_in_month(p, year, month) or _starts_soon(p, today, lookahead_days))
        ]

    # Ordenacao editorial: em andamento hoje > futuro proximo > demais

    def _priority(p):
        s = p.get("start_date")
        e = p.get("end_date")
        if not s:
            return (9, 0)
        s_d = date.fromisoformat(s)
        e_d = date.fromisoformat(e) if e else s_d
        if s_d <= today <= e_d:
            return (0, (e_d - today).days)  # em andamento: termina antes primeiro
        if s_d > today:
            return (1, (s_d - today).days)  # futuro: comeca mais cedo primeiro
        return (2, -(today - e_d).days)     # passado

    if not use_custom_order:
        ativos.sort(key=_priority)

    visible = [_build_card(p) for p in ativos[:limit]]
    return {
        "mes_referencia": f"{MES_PT_ACENTO[month]}/{year}",
        "visible": visible,
        "extra_count": max(0, len(ativos) - limit),
        "total": len(ativos),
    }


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--year", type=int, default=date.today().year)
    ap.add_argument("--month", type=int, default=date.today().month)
    ap.add_argument("--limit", type=int, default=4)
    args = ap.parse_args()
    ctx = get_active_projects(args.year, args.month, args.limit)
    print(json.dumps(ctx, indent=2, ensure_ascii=False))
