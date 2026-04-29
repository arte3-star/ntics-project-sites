#!/usr/bin/env python3
"""
aggregate_pmo_metrics.py
Lê .tmp/pmo_raw_tasks.json + .tmp/pmo_raw_sprint.json e gera .tmp/pmo_metrics.json
com saúde por projeto, atrasos, mudanças 24h, marcos 7d, bloqueios, decisões e
aderência da Sprint por dia da semana.
"""

import re
import sys
import argparse
from pathlib import Path
from datetime import date, timedelta, datetime
from collections import Counter

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from reports._common import (
    load_config, ensure_dirs, setup_utf8_stdout, write_json, read_json,
    epoch_ms_to_datetime, today_brt, normalize, in_set_normalized,
    TMP_DIR,
)

DIAS_SEMANA = ["segunda", "terça", "quarta", "quinta", "sexta", "sábado", "domingo"]


def is_done(status: str, status_type: str, done_keywords: list[str]) -> bool:
    if normalize(status_type) in ("closed", "done"):
        return True
    return in_set_normalized(status, done_keywords)


def detect_blocker(task: dict, cfg: dict) -> str | None:
    """Retorna razão do bloqueio ou None."""
    bcfg = cfg["blockers"]
    status = task.get("status") or ""
    if any(normalize(k) in normalize(status) for k in bcfg["status_keywords"]):
        return f"status: {status}"
    tags_norm = [normalize(t) for t in (task.get("tags") or [])]
    for tag in bcfg["tags"]:
        if normalize(tag) in tags_norm:
            return f"tag: {tag}"
    fase = (task.get("custom_fields") or {}).get("Fase")
    if fase in ("Pré-Execução", "Planejamento"):
        due = epoch_ms_to_datetime(task.get("due_date"))
        if due and due.date() < today_brt() - timedelta(days=7):
            return "parado fora do prazo (>7d)"
    return None


def detect_decisao(task: dict, cfg: dict) -> bool:
    bcfg = cfg["blockers"]
    name = task.get("name") or ""
    if name.startswith(bcfg.get("decisao_name_prefix", "[DECISAO]")):
        return True
    tags_norm = [normalize(t) for t in (task.get("tags") or [])]
    for tag in bcfg.get("decisao_tags", []):
        if normalize(tag) in tags_norm:
            return True
    return False


def detect_milestone(task: dict, cfg: dict) -> bool:
    mcfg = cfg["milestones"]
    fase = (task.get("custom_fields") or {}).get("Fase")
    if fase in mcfg["fase_milestone"]:
        return True
    tags_norm = [normalize(t) for t in (task.get("tags") or [])]
    for tag in mcfg["tags"]:
        if normalize(tag) in tags_norm:
            return True
    name = task.get("name") or ""
    if re.search(mcfg["name_regex"], name):
        return True
    return False


def health_for_project(overdue_pct: float, has_blocker: bool, cfg: dict) -> str:
    """Saúde baseada em overdue_pct + presença de bloqueio.
    Completion Rate do ClickUp é exibido mas não pondera no scoring porque
    tasks raiz sem subtasks ficam em 0% (falso negativo)."""
    h = cfg["health"]
    if has_blocker:
        return "VERMELHO"
    if overdue_pct >= h["yellow"]["overdue_pct_max"]:
        return "VERMELHO"
    if overdue_pct >= h["green"]["overdue_pct_max"]:
        return "AMARELO"
    return "VERDE"


def task_view(task: dict) -> dict:
    """Forma compacta para exibição/contexto IA."""
    due = epoch_ms_to_datetime(task.get("due_date"))
    return {
        "id": task["id"],
        "name": task.get("name", "")[:140],
        "url": task.get("url", ""),
        "status": task.get("status", ""),
        "priority": task.get("priority"),
        "due_date": due.date().isoformat() if due else None,
        "assignees": [a.get("username", "").split(",")[0].strip() for a in (task.get("assignees") or [])],
        "list_name": task.get("list_name", ""),
    }


def _is_creative(username: str, creative_keywords: list[str]) -> bool:
    n = normalize(username or "")
    return any(normalize(k) in n for k in creative_keywords)


def _first_name(username: str) -> str:
    if not username:
        return "-"
    return username.split(",")[0].strip()


def aggregate_projetos(raw: dict, cfg: dict) -> dict:
    today = today_brt()
    cutoff_24h = raw.get("cutoff_24h_ms", 0)
    done_keywords = cfg["status_done"]
    team_cfg = cfg.get("team", {}) or {}
    creative_keywords = (team_cfg.get("designers") or []) + (team_cfg.get("video_makers") or [])

    projects = []
    totals = Counter()

    decisions_pendentes = []
    bloqueios_globais = []
    creative_by_person: dict[str, list[dict]] = {}
    coord_overrides = cfg.get("coordinator_overrides", {}) or {}

    for lst in raw.get("lists", []):
        tasks = lst.get("tasks", [])
        open_tasks = []
        completion_values = []
        overdue, due_today, due_7d, changes_24h, milestones, blockers = [], [], [], [], [], []
        responsavel_counter = Counter()
        fase_counter = Counter()

        for t in tasks:
            status_type = t.get("status_type", "")
            status = t.get("status", "")
            done = is_done(status, status_type, done_keywords)
            due = epoch_ms_to_datetime(t.get("due_date"))
            updated_ms = int(t.get("date_updated") or 0)

            assignees_creative = []
            assignees_pm = []
            for a in (t.get("assignees") or []):
                full = a.get("username") or ""
                u = _first_name(full)
                if not u:
                    continue
                if _is_creative(full, creative_keywords):
                    assignees_creative.append(u)
                else:
                    assignees_pm.append(u)
                    responsavel_counter[u] += 1

            if assignees_creative and not done:
                view_creative = task_view(t)
                view_creative["project"] = lst.get("name", "")
                view_creative["due_date_str"] = view_creative.get("due_date") or "-"
                for c in assignees_creative:
                    creative_by_person.setdefault(c, []).append(view_creative)

            fase = (t.get("custom_fields") or {}).get("Fase")
            if fase:
                fase_counter[fase] += 1

            if not t.get("parent"):
                cr = (t.get("custom_fields") or {}).get("Completion Rate")
                if isinstance(cr, (int, float)):
                    completion_values.append(cr)

            view = task_view(t)

            if updated_ms >= cutoff_24h:
                changes_24h.append({**view, "kind": "fechada" if done else "alterada"})

            if done:
                continue

            open_tasks.append(t)
            if due:
                if due.date() < today:
                    overdue.append(view)
                elif due.date() == today:
                    due_today.append(view)
                if today <= due.date() <= today + timedelta(days=7):
                    due_7d.append(view)

            br = detect_blocker(t, cfg)
            if br:
                blockers.append({**view, "reason": br})

            if detect_milestone(t, cfg) and due and today <= due.date() <= today + timedelta(days=7):
                milestones.append(view)

            if detect_decisao(t, cfg):
                decisions_pendentes.append({**view, "project": lst.get("name", "")})

        total_open = len(open_tasks)
        overdue_pct = len(overdue) / max(total_open, 1)
        completion_values_real = [c for c in completion_values if c > 0]
        completion_avg = sum(completion_values_real) / len(completion_values_real) if completion_values_real else 0.0
        has_blocker = bool(blockers)
        health = health_for_project(overdue_pct, has_blocker, cfg)
        override = coord_overrides.get(str(lst["id"]))
        if override:
            responsavel = override
        else:
            responsavel = responsavel_counter.most_common(1)[0][0] if responsavel_counter else "-"
        fase_dom = fase_counter.most_common(1)[0][0] if fase_counter else "sem fase"

        overdue.sort(key=lambda v: v.get("due_date") or "")
        due_today.sort(key=lambda v: v.get("name", ""))
        due_7d.sort(key=lambda v: v.get("due_date") or "")
        milestones.sort(key=lambda v: v.get("due_date") or "")
        changes_24h.sort(key=lambda v: v.get("name", ""))

        projects.append({
            "list_id": lst["id"],
            "name": lst["name"],
            "fase_dominante": fase_dom,
            "responsavel": responsavel,
            "health": health,
            "total_open": total_open,
            "completion_avg": round(completion_avg, 3),
            "overdue_pct": round(overdue_pct, 3),
            "overdue": overdue,
            "due_today": due_today,
            "due_7d": due_7d,
            "changes_24h": changes_24h,
            "blockers": blockers,
            "milestones_7d": milestones,
        })

        totals["projects"] += 1
        totals["tasks_open"] += total_open
        totals["overdue"] += len(overdue)
        totals["changes_24h"] += len(changes_24h)
        totals["milestones_7d"] += len(milestones)
        totals["blockers"] += len(blockers)
        if has_blocker:
            for b in blockers:
                bloqueios_globais.append({**b, "project": lst.get("name", "")})

    health_order = {"VERMELHO": 0, "AMARELO": 1, "VERDE": 2}
    projects.sort(key=lambda p: (health_order.get(p["health"], 9), -p["total_open"]))

    # Agrupa projetos por coordenador (responsável dominante)
    by_coordinator: dict[str, list[dict]] = {}
    for p in projects:
        coord = p.get("responsavel") or "-"
        by_coordinator.setdefault(coord, []).append(p)

    coordinators = []
    for name, projs in by_coordinator.items():
        atrasos = sum(len(p["overdue"]) for p in projs)
        bloqueios = sum(len(p["blockers"]) for p in projs)
        abertas = sum(p["total_open"] for p in projs)
        worst = "VERDE"
        for p in projs:
            if p["health"] == "VERMELHO":
                worst = "VERMELHO"; break
            if p["health"] == "AMARELO":
                worst = "AMARELO"
        coordinators.append({
            "name": name,
            "projects": projs,
            "tasks_open": abertas,
            "overdue": atrasos,
            "blockers": bloqueios,
            "health": worst,
        })
    coordinators.sort(key=lambda c: (health_order.get(c["health"], 9), -c["overdue"], -c["tasks_open"]))

    # Equipe criativa (design + video) com agregados por pessoa
    creative = []
    for person, tasks_list in creative_by_person.items():
        atrasadas = [v for v in tasks_list if v.get("due_date") and v["due_date"] < today.isoformat()]
        proximas = [v for v in tasks_list if v.get("due_date") and today.isoformat() <= v["due_date"] <= (today + timedelta(days=7)).isoformat()]
        creative.append({
            "name": person,
            "abertas": len(tasks_list),
            "atrasadas": len(atrasadas),
            "proximas_7d": len(proximas),
            "tasks_atrasadas": sorted(atrasadas, key=lambda v: v.get("due_date") or ""),
            "tasks_proximas": sorted(proximas, key=lambda v: v.get("due_date") or ""),
            "tasks_outras": [v for v in tasks_list if v not in atrasadas and v not in proximas][:8],
        })
    creative.sort(key=lambda c: (-c["atrasadas"], -c["abertas"]))

    totals["creative_open"] = sum(c["abertas"] for c in creative)
    totals["creative_overdue"] = sum(c["atrasadas"] for c in creative)

    return {
        "totals": dict(totals),
        "projects": projects,
        "coordinators": coordinators,
        "creative": creative,
        "decisions_pendentes": decisions_pendentes,
        "blockers": bloqueios_globais,
    }


def aggregate_sprint(raw: dict, cfg: dict) -> dict:
    if not raw or not raw.get("sprint"):
        return {"available": False}

    today = today_brt()
    sprint = raw["sprint"]
    start = date.fromisoformat(sprint["start"])
    end = date.fromisoformat(sprint["end"])
    done_keywords = cfg["status_done"]
    team_cfg = cfg.get("team", {}) or {}
    creative_keywords = (team_cfg.get("designers") or []) + (team_cfg.get("video_makers") or [])

    days = []
    cursor = start
    while cursor <= end:
        days.append(cursor)
        cursor += timedelta(days=1)

    by_day = {d.isoformat(): {
        "date": d.isoformat(),
        "weekday": DIAS_SEMANA[d.weekday()],
        "previstas": 0,
        "entregues_no_prazo": 0,
        "atrasadas": 0,
        "pendentes": 0,
        "tasks": [],
    } for d in days}

    semana_previstas = 0
    semana_entregues_prazo = 0

    # Matrix coordenador x dia: {coord_name: {date_iso: {previstas, no_prazo, atrasadas, pendentes}}}
    coord_matrix: dict[str, dict[str, dict]] = {}

    def _coord_of_task(task: dict) -> str:
        for a in (task.get("assignees") or []):
            full = a.get("username") or ""
            if not full:
                continue
            if creative_keywords and _is_creative(full, creative_keywords):
                continue
            return _first_name(full)
        for a in (task.get("assignees") or []):
            full = a.get("username") or ""
            if full:
                return _first_name(full)
        return "Sem responsável"

    for t in raw.get("tasks", []):
        if t.get("parent"):
            continue
        due = epoch_ms_to_datetime(t.get("due_date"))
        if not due:
            continue
        d = due.date()
        if d < start or d > end:
            continue
        bucket = by_day[d.isoformat()]
        bucket["previstas"] += 1
        view = task_view(t)
        done = is_done(t.get("status", ""), t.get("status_type", ""), done_keywords)
        date_done = epoch_ms_to_datetime(t.get("date_done"))
        if done and date_done and date_done.date() <= d:
            bucket["entregues_no_prazo"] += 1
            view["resultado"] = "entregue_no_prazo"
        elif done:
            view["resultado"] = "entregue_atrasado"
        elif d < today:
            bucket["atrasadas"] += 1
            view["resultado"] = "atrasada"
        else:
            bucket["pendentes"] += 1
            view["resultado"] = "pendente"
        bucket["tasks"].append(view)
        if d <= today:
            semana_previstas += 1
            if view.get("resultado") == "entregue_no_prazo":
                semana_entregues_prazo += 1

        coord = _coord_of_task(t)
        cell = coord_matrix.setdefault(coord, {}).setdefault(d.isoformat(), {
            "previstas": 0, "no_prazo": 0, "atrasadas": 0, "pendentes": 0,
        })
        cell["previstas"] += 1
        if view["resultado"] == "entregue_no_prazo":
            cell["no_prazo"] += 1
        elif view["resultado"] == "atrasada":
            cell["atrasadas"] += 1
        elif view["resultado"] == "pendente":
            cell["pendentes"] += 1

    for b in by_day.values():
        b["aderencia_pct"] = round(b["entregues_no_prazo"] / b["previstas"], 3) if b["previstas"] else None

    aderencia_semana = round(semana_entregues_prazo / semana_previstas, 3) if semana_previstas else None
    dias_perfeitos = sum(1 for b in by_day.values()
                         if b["previstas"] > 0 and b["entregues_no_prazo"] == b["previstas"]
                         and date.fromisoformat(b["date"]) <= today)

    coordinators_in_sprint = []
    for coord_name, by_date in coord_matrix.items():
        cells = []
        total_prev = 0
        total_prazo = 0
        for d in days:
            iso = d.isoformat()
            cell = by_date.get(iso) or {"previstas": 0, "no_prazo": 0, "atrasadas": 0, "pendentes": 0}
            cells.append({
                "date": iso,
                "weekday": DIAS_SEMANA[d.weekday()],
                **cell,
            })
            total_prev += cell["previstas"]
            total_prazo += cell["no_prazo"]
        coordinators_in_sprint.append({
            "name": coord_name,
            "cells": cells,
            "total_previstas": total_prev,
            "total_no_prazo": total_prazo,
            "aderencia_pct": round(total_prazo / total_prev, 3) if total_prev else None,
        })
    coordinators_in_sprint.sort(key=lambda c: -c["total_previstas"])

    return {
        "available": True,
        "sprint": sprint,
        "today": today.isoformat(),
        "days": [by_day[d.isoformat()] for d in days],
        "coordinators": coordinators_in_sprint,
        "aderencia_semana_pct": aderencia_semana,
        "dias_perfeitos": dias_perfeitos,
        "totais": {
            "previstas_ate_hoje": semana_previstas,
            "entregues_no_prazo_ate_hoje": semana_entregues_prazo,
        },
    }


def main():
    setup_utf8_stdout()
    cfg = load_config()
    ensure_dirs()

    parser = argparse.ArgumentParser()
    parser.add_argument("--projetos", default=str(TMP_DIR / "pmo_raw_tasks.json"))
    parser.add_argument("--sprint", default=str(TMP_DIR / "pmo_raw_sprint.json"))
    parser.add_argument("--output", default=str(TMP_DIR / "pmo_metrics.json"))
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()

    proj_raw = read_json(Path(args.projetos))
    sprint_raw = None
    sprint_path = Path(args.sprint)
    if sprint_path.exists():
        sprint_raw = read_json(sprint_path)

    proj = aggregate_projetos(proj_raw, cfg)
    sprint = aggregate_sprint(sprint_raw or {}, cfg) if sprint_raw else {"available": False}

    out = {
        "generated_at": datetime.now().isoformat(),
        "today": today_brt().isoformat(),
        "totals": proj["totals"],
        "projects": proj["projects"],
        "coordinators": proj["coordinators"],
        "creative": proj["creative"],
        "decisions_pendentes": proj["decisions_pendentes"],
        "blockers": proj["blockers"],
        "sprint": sprint,
    }
    write_json(Path(args.output), out)
    if not args.quiet:
        t = out["totals"]
        s = sprint
        line = (f"[aggregate] projetos={t.get('projects',0)} open={t.get('tasks_open',0)} "
                f"atrasadas={t.get('overdue',0)} bloqueios={t.get('blockers',0)} "
                f"marcos7d={t.get('milestones_7d',0)} mudancas24h={t.get('changes_24h',0)}")
        if s.get("available"):
            line += f" sprint#{s['sprint']['num']} aderencia_semana={s.get('aderencia_semana_pct')}"
        print(line)
        print(f"[aggregate] OK -> {args.output}")


if __name__ == "__main__":
    main()
