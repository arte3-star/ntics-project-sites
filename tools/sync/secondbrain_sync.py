#!/usr/bin/env python3
"""
secondbrain_sync.py — Sync batch ClickUp -> SecondBrain para todos os projetos ativos.

Lê todos os README.md com clickup_list_id, puxa tasks do ClickUp e escreve:
  - SecondBrain/projetos/{slug}/tasks-summary.md  (por projeto)
  - SecondBrain/projetos/_rollup-areas.md          (cross-project por área)
  - Atualiza last_refresh no frontmatter de cada README.md

Uso:
    python tools/sync/secondbrain_sync.py                        # sync diário completo
    python tools/sync/secondbrain_sync.py --since 2026-04-25    # backfill 3 semanas
    python tools/sync/secondbrain_sync.py --slug 132-estacao-samarco
    python tools/sync/secondbrain_sync.py --dry-run
    python tools/sync/secondbrain_sync.py --quiet
"""

from __future__ import annotations

import argparse
import re
import sys
import time
import unicodedata
from collections import defaultdict
from datetime import datetime, date, timedelta
from pathlib import Path

import yaml
from dotenv import load_dotenv

# SecondBrain/ is gitignored — not present in worktrees. Walk up until we find it.
_SCRIPT_DIR = Path(__file__).resolve().parent   # tools/sync/
_TOOLS_DIR = _SCRIPT_DIR.parent                 # tools/

sys.path.insert(0, str(_TOOLS_DIR))
sys.path.insert(0, str(_TOOLS_DIR / "integrations"))


def _find_project_root() -> Path:
    """Find the project root that contains SecondBrain/ (may differ from worktree root)."""
    for p in [_TOOLS_DIR.parent, *_TOOLS_DIR.parent.parents]:
        if (p / "SecondBrain").is_dir():
            return p
    raise RuntimeError("Project root not found — SecondBrain/ directory missing")


ROOT = _find_project_root()
SECONDBRAIN_DIR = ROOT / "SecondBrain"
PROJECTS_DIR = SECONDBRAIN_DIR / "projetos"

# Load .env from the real project root (not worktree root where it doesn't exist)
load_dotenv(ROOT / ".env", override=True)

from reports._common import (
    epoch_ms_to_datetime, now_brt, load_config, setup_utf8_stdout, BR_TZ,
)
from clickup_pull_projetos_ntics import list_lists, fetch_tasks, slim_task


# ---------------------------------------------------------------------------
# Status helpers
# ---------------------------------------------------------------------------

def _norm(s: str) -> str:
    nfkd = unicodedata.normalize("NFKD", (s or "").lower().strip())
    return "".join(c for c in nfkd if not unicodedata.combining(c))


_DONE_NAMES = {"concluido", "completo", "complete", "closed", "fechado", "entregue", "done"}
_INPROGRESS_NAMES = {"em andamento", "em progresso", "in progress", "executando", "revisao", "revisão"}
_BLOCKED_NAMES = {"bloqueado", "blocked", "em risco", "aguardando", "impedido"}


def is_done(task: dict) -> bool:
    return task.get("status_type") == "closed" or _norm(task.get("status", "")) in _DONE_NAMES


def is_blocked(task: dict) -> bool:
    sn = _norm(task.get("status", ""))
    tags = [_norm(t) for t in task.get("tags", [])]
    return sn in _BLOCKED_NAMES or "bloqueado" in sn or "bloqueado" in tags or "blocked" in tags


def is_in_progress(task: dict) -> bool:
    sn = _norm(task.get("status", ""))
    return sn in _INPROGRESS_NAMES or "andamento" in sn or "progresso" in sn


def task_areas(task: dict) -> list[str]:
    areas = (task.get("custom_fields") or {}).get("Áreas/Setores")
    if not areas:
        return ["Sem área"]
    if isinstance(areas, str):
        return [areas]
    return areas or ["Sem área"]


def task_fase(task: dict) -> str:
    cf = task.get("custom_fields") or {}
    return cf.get("Fase PMBOK") or cf.get("Fase") or "Sem fase"


def fmt_date(ms_str) -> str:
    dt = epoch_ms_to_datetime(ms_str)
    return dt.strftime("%d/%m") if dt else "—"


def fmt_date_full(ms_str) -> str:
    dt = epoch_ms_to_datetime(ms_str)
    return dt.strftime("%d/%m/%Y") if dt else "—"


# ---------------------------------------------------------------------------
# SecondBrain project discovery
# ---------------------------------------------------------------------------

def parse_frontmatter(text: str) -> dict | None:
    if not text.startswith("---"):
        return None
    try:
        end = text.index("---", 3)
        return yaml.safe_load(text[3:end])
    except (ValueError, yaml.YAMLError):
        return None


def discover_projects() -> list[dict]:
    projects = []
    for readme in sorted(PROJECTS_DIR.glob("*/README.md")):
        slug = readme.parent.name
        if slug.startswith(("_", ".")):
            continue
        text = readme.read_text(encoding="utf-8")
        fm = parse_frontmatter(text)
        if not fm or not fm.get("clickup_list_id"):
            continue
        projects.append({
            "slug": slug,
            "path": readme.parent,
            "readme_path": readme,
            "list_id": str(fm["clickup_list_id"]),
            "nome": fm.get("nome", slug),
            "codigo": fm.get("codigo"),
            "status": fm.get("status", ""),
        })
    return projects


def update_readme_last_refresh(readme_path: Path, new_date: str, dry_run: bool) -> None:
    text = readme_path.read_text(encoding="utf-8")
    updated = re.sub(r"(?m)^last_refresh:.*$", f"last_refresh: {new_date}", text, count=1)
    if not dry_run and updated != text:
        readme_path.write_text(updated, encoding="utf-8")


# ---------------------------------------------------------------------------
# Markdown builders
# ---------------------------------------------------------------------------

def build_tasks_summary(project: dict, tasks: list[dict], since_date: date | None, now: datetime) -> str:
    today_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%Y-%m-%d %H:%M BRT")

    done = [t for t in tasks if is_done(t)]
    blocked = [t for t in tasks if not is_done(t) and is_blocked(t)]
    in_progress = [t for t in tasks if not is_done(t) and not is_blocked(t) and is_in_progress(t)]
    todo = [t for t in tasks if not is_done(t) and not is_blocked(t) and not is_in_progress(t)]

    by_fase: dict[str, list] = defaultdict(list)
    by_area: dict[str, list] = defaultdict(list)
    for t in tasks:
        by_fase[task_fase(t)].append(t)
        for a in task_areas(t):
            by_area[a].append(t)

    if since_date:
        since_ms = int(datetime(since_date.year, since_date.month, since_date.day, tzinfo=BR_TZ).timestamp() * 1000)
    else:
        since_ms = int((now - timedelta(days=7)).timestamp() * 1000)

    recent = sorted(
        [t for t in tasks if max(int(t.get("date_updated") or 0), int(t.get("date_created") or 0)) >= since_ms],
        key=lambda t: int(t.get("date_updated") or 0),
        reverse=True,
    )[:25]

    now_ms = int(now.timestamp() * 1000)
    overdue = [
        t for t in tasks
        if not is_done(t) and t.get("due_date") and int(t.get("due_date") or 0) < now_ms
    ]

    lines = [
        "---",
        f"last_sync: {today_str}",
        "source: clickup",
        "---",
        "",
        f"# Resumo de Tarefas — {project['nome']}",
        "",
        f"**Atualizado em:** {time_str}",
        "",
        "## Visão Geral",
        "",
        "| Status | Qtd |",
        "|--------|-----|",
        f"| Concluído | {len(done)} |",
        f"| Em andamento | {len(in_progress)} |",
        f"| A fazer | {len(todo)} |",
        f"| Bloqueado | {len(blocked)} |",
        f"| **Total** | **{len(tasks)}** |",
        "",
    ]

    if len(by_fase) > 1 or (len(by_fase) == 1 and "Sem fase" not in by_fase):
        lines += [
            "## Por Fase PMBOK",
            "",
            "| Fase | Total | Concluídas |",
            "|------|-------|------------|",
        ]
        for fase in sorted(by_fase.keys()):
            ft = by_fase[fase]
            lines.append(f"| {fase} | {len(ft)} | {sum(1 for t in ft if is_done(t))} |")
        lines.append("")

    areas_to_show = {a: v for a, v in by_area.items() if a != "Sem área"}
    if areas_to_show:
        lines += [
            "## Por Área",
            "",
            "| Área | Total | Concluídas |",
            "|------|-------|------------|",
        ]
        for area in sorted(areas_to_show.keys()):
            at = areas_to_show[area]
            lines.append(f"| {area} | {len(at)} | {sum(1 for t in at if is_done(t))} |")
        lines.append("")

    if recent:
        label = f"desde {since_date}" if since_date else "últimos 7 dias"
        lines += [
            f"## Tarefas Recentes ({label})",
            "",
            "| Data | Tarefa | Status | Área |",
            "|------|--------|--------|------|",
        ]
        for t in recent:
            dt_str = fmt_date(t.get("date_updated"))
            name = (t.get("name") or "")[:60]
            status = t.get("status") or ""
            areas = task_areas(t)
            area_str = ", ".join(a for a in areas if a != "Sem área") or "—"
            lines.append(f"| {dt_str} | {name} | {status} | {area_str} |")
        lines.append("")

    if overdue or blocked:
        lines.append("## Atenção")
        lines.append("")
        if overdue:
            lines.append(f"**Vencidas ({len(overdue)}):**")
            lines.append("")
            for t in overdue[:10]:
                lines.append(f"- [{t.get('name', '')}]({t.get('url', '#')}) — venceu {fmt_date_full(t.get('due_date'))}")
            lines.append("")
        if blocked:
            lines.append(f"**Bloqueadas ({len(blocked)}):**")
            lines.append("")
            for t in blocked[:10]:
                lines.append(f"- [{t.get('name', '')}]({t.get('url', '#')})")
            lines.append("")

    return "\n".join(lines)


def build_rollup(all_data: list[dict], now: datetime) -> str:
    by_area: dict[str, list] = defaultdict(list)
    for pd in all_data:
        project = pd["project"]
        for t in pd["tasks"]:
            for a in task_areas(t):
                by_area[a].append({"project": project, "task": t})

    area_proj: dict[str, dict[str, dict]] = defaultdict(lambda: defaultdict(lambda: {"total": 0, "done": 0, "in_progress": 0}))
    for area, items in by_area.items():
        for item in items:
            slug = item["project"]["slug"]
            area_proj[area][slug]["total"] += 1
            if is_done(item["task"]):
                area_proj[area][slug]["done"] += 1
            elif is_in_progress(item["task"]):
                area_proj[area][slug]["in_progress"] += 1

    lines = [
        "---",
        f"last_sync: {now.strftime('%Y-%m-%d')}",
        "---",
        "",
        "# Rollup por Área — Todos os Projetos",
        "",
        f"**Atualizado em:** {now.strftime('%Y-%m-%d %H:%M BRT')}",
        "",
    ]

    for area in sorted(a for a in by_area.keys() if a != "Sem área"):
        lines += [
            f"## {area}",
            "",
            "| Projeto | Total | Concluídas | Em andamento |",
            "|---------|-------|------------|--------------|",
        ]
        for pd in all_data:
            slug = pd["project"]["slug"]
            counts = area_proj[area].get(slug)
            if counts and counts["total"] > 0:
                p = pd["project"]
                lines.append(f"| {p['codigo']} — {p['nome']} | {counts['total']} | {counts['done']} | {counts['in_progress']} |")
        lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def log(msg: str, quiet: bool = False) -> None:
    if not quiet:
        print(msg, flush=True)


def main():
    setup_utf8_stdout()

    parser = argparse.ArgumentParser(description="Sync ClickUp -> SecondBrain")
    parser.add_argument("--since", metavar="YYYY-MM-DD", help="Backfill desde data (inclui tasks fechadas)")
    parser.add_argument("--slug", help="Processar só este projeto")
    parser.add_argument("--dry-run", action="store_true", help="Mostra o que faria sem escrever")
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()

    since_date: date | None = None
    if args.since:
        since_date = date.fromisoformat(args.since)

    cfg = load_config()
    folder_id = cfg["clickup"]["folder_projetos_ativos"]
    exclude = cfg["clickup"]["exclude_lists"]

    projects = discover_projects()
    if args.slug:
        projects = [p for p in projects if args.slug in p["slug"]]
        if not projects:
            print(f"[secondbrain-sync] ERRO: nenhum projeto encontrado para --slug={args.slug}", file=sys.stderr)
            sys.exit(1)

    log(f"[secondbrain-sync] {len(projects)} projeto(s) no SecondBrain com clickup_list_id", args.quiet)

    id_to_project = {p["list_id"]: p for p in projects}

    log(f"[secondbrain-sync] Listando folder {folder_id}...", args.quiet)
    clickup_lists = list_lists(folder_id, exclude)

    now = now_brt()
    today_str = now.strftime("%Y-%m-%d")

    all_data: list[dict] = []
    unmatched: list[str] = []

    for lst in clickup_lists:
        project = id_to_project.get(lst["id"])
        if not project:
            unmatched.append(f"{lst['name']} ({lst['id']})")
            continue

        log(f"[secondbrain-sync] {project['slug']} — buscando tasks...", args.quiet)

        try:
            tasks_raw = fetch_tasks(lst["id"], include_closed=True)
            tasks = [slim_task(t, lst["id"], lst["name"]) for t in tasks_raw]

            all_data.append({"project": project, "tasks": tasks})

            summary = build_tasks_summary(project, tasks, since_date, now)
            summary_path = project["path"] / "tasks-summary.md"

            if args.dry_run:
                log(f"  [DRY-RUN] escreveria {summary_path.name} ({len(tasks)} tasks)", args.quiet)
            else:
                summary_path.write_text(summary, encoding="utf-8")
                update_readme_last_refresh(project["readme_path"], today_str, dry_run=False)
                log(f"  OK {summary_path.name} ({len(tasks)} tasks)", args.quiet)

        except Exception as e:
            print(f"[secondbrain-sync] ERRO em {project['slug']}: {e}", file=sys.stderr)

        time.sleep(0.5)

    clickup_ids = {lst["id"] for lst in clickup_lists}
    orphan_projects = [p for p in projects if p["list_id"] not in clickup_ids]

    if unmatched and not args.quiet:
        log(f"\n[secondbrain-sync] {len(unmatched)} lista(s) no ClickUp SEM projeto no SecondBrain:", args.quiet)
        for u in unmatched:
            log(f"  + {u}", args.quiet)

    if orphan_projects and not args.quiet:
        log(f"\n[secondbrain-sync] {len(orphan_projects)} projeto(s) no SecondBrain com list_id NAO encontrado no ClickUp:", args.quiet)
        for p in orphan_projects:
            log(f"  ! {p['slug']} (list_id: {p['list_id']})", args.quiet)

    if all_data:
        rollup = build_rollup(all_data, now)
        rollup_path = PROJECTS_DIR / "_rollup-areas.md"
        if args.dry_run:
            log(f"[DRY-RUN] escreveria {rollup_path.name}", args.quiet)
        else:
            rollup_path.write_text(rollup, encoding="utf-8")
            log(f"[secondbrain-sync] _rollup-areas.md atualizado", args.quiet)

    total_tasks = sum(len(pd["tasks"]) for pd in all_data)
    log(
        f"[secondbrain-sync] Concluído: {len(all_data)} projeto(s), {total_tasks} task(s) total",
        args.quiet,
    )


if __name__ == "__main__":
    main()
