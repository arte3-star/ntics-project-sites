#!/usr/bin/env python3
"""
aggregate_pmo_weekly.py
Lê .tmp/pmo_raw_tasks.json e gera .tmp/pmo_weekly_metrics.json com:
  - Janela passada: segunda da semana atual menos 7 dias até domingo passado
  - Janela próxima: segunda próxima até domingo próximo
Agrupado por coordenador (com overrides do YAML), separando entregues x próximos.
"""

import sys
import argparse
from pathlib import Path
from datetime import date, timedelta, datetime
from collections import Counter

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from reports._common import (
    load_config, ensure_dirs, setup_utf8_stdout, write_json, read_json,
    epoch_ms_to_datetime, today_brt, normalize, in_set_normalized, TMP_DIR,
)
from reports.aggregate_pmo_metrics import (
    is_done, _is_creative, _first_name, task_view,
)


def week_window(ref: date, offset_weeks: int = 0) -> tuple[date, date]:
    """Retorna (segunda, domingo) da semana que contém ref + offset semanas."""
    monday = ref - timedelta(days=ref.weekday()) + timedelta(weeks=offset_weeks)
    sunday = monday + timedelta(days=6)
    return monday, sunday


def aggregate_weekly(raw: dict, cfg: dict, ref: date) -> dict:
    done_keywords = cfg["status_done"]
    team_cfg = cfg.get("team", {}) or {}
    creative_keywords = (team_cfg.get("designers") or []) + (team_cfg.get("video_makers") or [])
    coord_overrides = cfg.get("coordinator_overrides", {}) or {}

    past_start, past_end = week_window(ref, offset_weeks=-1)
    next_start, next_end = week_window(ref, offset_weeks=1)

    by_coord: dict[str, dict] = {}
    creative_by_person: dict[str, dict] = {}

    totals = Counter()

    for lst in raw.get("lists", []):
        list_id = str(lst.get("id"))
        list_name = lst.get("name", "")
        responsavel_counter = Counter()

        for t in lst.get("tasks", []):
            for a in (t.get("assignees") or []):
                full = a.get("username") or ""
                if not full or _is_creative(full, creative_keywords):
                    continue
                responsavel_counter[_first_name(full)] += 1

        override = coord_overrides.get(list_id)
        if override:
            project_coord = override
        else:
            project_coord = responsavel_counter.most_common(1)[0][0] if responsavel_counter else "Sem coordenador"

        for t in lst.get("tasks", []):
            view = task_view(t)
            view["project"] = list_name
            done = is_done(t.get("status", ""), t.get("status_type", ""), done_keywords)
            due = epoch_ms_to_datetime(t.get("due_date"))
            date_done = epoch_ms_to_datetime(t.get("date_done"))

            assignees_creative = []
            assignees_pm = []
            for a in (t.get("assignees") or []):
                full = a.get("username") or ""
                if not full:
                    continue
                if _is_creative(full, creative_keywords):
                    assignees_creative.append(_first_name(full))
                else:
                    assignees_pm.append(_first_name(full))

            entregue_passada = done and date_done and past_start <= date_done.date() <= past_end
            prevista_proxima = (not done) and due and next_start <= due.date() <= next_end

            if entregue_passada:
                view["closed_date"] = date_done.date().isoformat()
            if prevista_proxima:
                view["due_iso"] = due.date().isoformat()

            if not entregue_passada and not prevista_proxima:
                continue

            if assignees_creative:
                for c in assignees_creative:
                    bucket = creative_by_person.setdefault(c, {"entregues": [], "proximas": []})
                    if entregue_passada:
                        bucket["entregues"].append(view)
                    elif prevista_proxima:
                        bucket["proximas"].append(view)
            else:
                bucket = by_coord.setdefault(project_coord, {
                    "name": project_coord,
                    "projects": {},
                })
                proj_bucket = bucket["projects"].setdefault(list_id, {
                    "list_id": list_id,
                    "name": list_name,
                    "entregues": [],
                    "proximas": [],
                })
                if entregue_passada:
                    proj_bucket["entregues"].append(view)
                    totals["entregues"] += 1
                elif prevista_proxima:
                    proj_bucket["proximas"].append(view)
                    totals["proximas"] += 1

    # Converter projects dict em lista ordenada
    coordinators = []
    for coord_name, data in by_coord.items():
        projs = []
        for p in data["projects"].values():
            p["entregues"].sort(key=lambda v: v.get("closed_date") or "")
            p["proximas"].sort(key=lambda v: v.get("due_iso") or "")
            p["total_entregues"] = len(p["entregues"])
            p["total_proximas"] = len(p["proximas"])
            projs.append(p)
        projs.sort(key=lambda p: -(p["total_entregues"] + p["total_proximas"]))
        coordinators.append({
            "name": coord_name,
            "projects": projs,
            "entregues": sum(p["total_entregues"] for p in projs),
            "proximas": sum(p["total_proximas"] for p in projs),
        })
    coordinators.sort(key=lambda c: -(c["entregues"] + c["proximas"]))

    creative = []
    for person, data in creative_by_person.items():
        data["entregues"].sort(key=lambda v: v.get("closed_date") or "")
        data["proximas"].sort(key=lambda v: v.get("due_iso") or "")
        creative.append({
            "name": person,
            "entregues": data["entregues"],
            "proximas": data["proximas"],
            "total_entregues": len(data["entregues"]),
            "total_proximas": len(data["proximas"]),
        })
        totals["creative_entregues"] += len(data["entregues"])
        totals["creative_proximas"] += len(data["proximas"])
    creative.sort(key=lambda c: -(c["total_entregues"] + c["total_proximas"]))

    return {
        "generated_at": datetime.now().isoformat(),
        "ref_date": ref.isoformat(),
        "past_window": {"start": past_start.isoformat(), "end": past_end.isoformat()},
        "next_window": {"start": next_start.isoformat(), "end": next_end.isoformat()},
        "totals": dict(totals),
        "coordinators": coordinators,
        "creative": creative,
    }


def main():
    setup_utf8_stdout()
    cfg = load_config()
    ensure_dirs()

    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default=str(TMP_DIR / "pmo_raw_tasks.json"))
    parser.add_argument("--output", default=str(TMP_DIR / "pmo_weekly_metrics.json"))
    parser.add_argument("--date", help="Data referência YYYY-MM-DD (default: hoje BRT)")
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()

    ref = today_brt() if not args.date else datetime.strptime(args.date, "%Y-%m-%d").date()
    raw = read_json(Path(args.input))
    metrics = aggregate_weekly(raw, cfg, ref)
    write_json(Path(args.output), metrics)

    if not args.quiet:
        t = metrics["totals"]
        pw = metrics["past_window"]
        nw = metrics["next_window"]
        print(f"[weekly] passada {pw['start']} a {pw['end']} | proxima {nw['start']} a {nw['end']}")
        print(f"[weekly] entregues={t.get('entregues',0)} proximas={t.get('proximas',0)} "
              f"design entregues={t.get('creative_entregues',0)} proximas={t.get('creative_proximas',0)}")
        print(f"[weekly] coordenadores={len(metrics['coordinators'])} criativos={len(metrics['creative'])}")
        print(f"[weekly] OK -> {args.output}")


if __name__ == "__main__":
    main()
