#!/usr/bin/env python3
"""
clickup_pull_projetos_ntics.py
Lê todas as tasks da pasta de Projetos Ativos NTICS no ClickUp.
Resolve custom fields (Fase, Áreas, Trimestre, Completion Rate).
Salva em .tmp/pmo_raw_tasks.json.
"""

import sys
import time
import argparse
from pathlib import Path
from datetime import timedelta

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from reports._common import (
    load_env, load_config, clickup_get, ensure_dirs,
    setup_utf8_stdout, write_json, now_brt, TMP_DIR,
)

CUSTOM_FIELDS_KEYWORDS = ("fase", "áreas", "areas", "setores", "trimestre", "completion")


def _is_interest_field(name: str) -> bool:
    n = (name or "").lower()
    return any(kw in n for kw in CUSTOM_FIELDS_KEYWORDS)


def list_lists(folder_id: str, exclude: list[str]) -> list[dict]:
    data = clickup_get(f"/folder/{folder_id}/list")
    out = []
    for lst in data.get("lists", []):
        if lst["id"] in exclude:
            continue
        out.append({"id": lst["id"], "name": lst["name"]})
    return out


def _normalized_key(name: str) -> str:
    n = (name or "").lower().strip()
    if "completion" in n:
        return "Completion Rate"
    if "fase pmbok" in n:
        return "Fase PMBOK"
    if n == "fase":
        return "Fase"
    if "trimestre" in n:
        return "Trimestre"
    if "área" in n or "areas" in n or "setores" in n:
        return "Áreas/Setores"
    return name


def resolve_custom_fields(task_fields: list[dict]) -> dict:
    """Converte custom_fields ClickUp em {nome_canonico: valor_resolvido}."""
    resolved = {}
    for f in task_fields or []:
        name = f.get("name", "")
        if not _is_interest_field(name):
            continue
        canon = _normalized_key(name)
        ftype = f.get("type")
        value = f.get("value")
        if value is None or value == "":
            resolved.setdefault(canon, None)
            continue
        if ftype == "drop_down":
            options = (f.get("type_config") or {}).get("options", [])
            if isinstance(value, int) or (isinstance(value, str) and str(value).isdigit()):
                idx = int(value)
                opt = next((o for o in options if o.get("orderindex") == idx or o.get("id") == value), None)
                resolved[canon] = (opt or {}).get("name") if opt else None
            else:
                resolved[canon] = str(value)
        elif ftype == "labels":
            options = (f.get("type_config") or {}).get("options", [])
            ids = value if isinstance(value, list) else [value]
            labels = []
            for vid in ids:
                opt = next((o for o in options if o.get("id") == vid), None)
                if opt:
                    labels.append(opt.get("label") or opt.get("name"))
            resolved[canon] = labels
        elif ftype == "automatic_progress" or ftype == "manual_progress":
            try:
                if isinstance(value, dict):
                    resolved[canon] = float(value.get("percent_complete", 0)) / 100
                else:
                    resolved[canon] = float(value) / 100 if float(value) > 1 else float(value)
            except (TypeError, ValueError):
                resolved[canon] = None
        elif ftype == "number":
            try:
                resolved[canon] = float(value)
            except (TypeError, ValueError):
                resolved[canon] = None
        else:
            resolved[canon] = value
    return resolved


def slim_task(task: dict, list_id: str, list_name: str) -> dict:
    return {
        "id": task["id"],
        "name": task.get("name", ""),
        "url": task.get("url", ""),
        "status": (task.get("status") or {}).get("status", ""),
        "status_type": (task.get("status") or {}).get("type", ""),
        "priority": (task.get("priority") or {}).get("priority") if task.get("priority") else None,
        "date_created": task.get("date_created"),
        "date_updated": task.get("date_updated"),
        "date_done": task.get("date_done"),
        "due_date": task.get("due_date"),
        "start_date": task.get("start_date"),
        "assignees": [
            {"id": a.get("id"), "username": a.get("username")}
            for a in (task.get("assignees") or [])
        ],
        "tags": [t.get("name") for t in (task.get("tags") or [])],
        "parent": task.get("parent"),
        "archived": task.get("archived", False),
        "custom_fields": resolve_custom_fields(task.get("custom_fields", [])),
        "list_id": list_id,
        "list_name": list_name,
    }


def fetch_tasks(list_id: str, include_closed: bool = False, limit_pages: int | None = None) -> list[dict]:
    """Pagina todas as tasks de uma lista."""
    tasks = []
    page = 0
    while True:
        params = {
            "archived": "false",
            "subtasks": "true",
            "include_closed": str(include_closed).lower(),
            "order_by": "updated",
            "reverse": "true",
            "page": page,
        }
        data = clickup_get(f"/list/{list_id}/task", params=params)
        page_tasks = data.get("tasks", [])
        tasks.extend(page_tasks)
        if len(page_tasks) < 100:
            break
        page += 1
        if limit_pages is not None and page >= limit_pages:
            break
        time.sleep(0.65)
    return tasks


def main():
    setup_utf8_stdout()
    load_env()
    cfg = load_config()
    ensure_dirs()

    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=None,
                        help="Máx de listas a processar (debug)")
    parser.add_argument("--cutoff-hours", type=int, default=24,
                        help="Janela em horas para incluir tasks fechadas no payload (default 24)")
    parser.add_argument("--quiet", action="store_true")
    parser.add_argument("--output", default=str(TMP_DIR / "pmo_raw_tasks.json"))
    args = parser.parse_args()

    folder_id = cfg["clickup"]["folder_projetos_ativos"]
    exclude = cfg["clickup"]["exclude_lists"]

    if not args.quiet:
        print(f"[pull-projetos] Listando folder {folder_id}...")
    lists = list_lists(folder_id, exclude)
    if args.limit:
        lists = lists[: args.limit]
    if not args.quiet:
        print(f"[pull-projetos] {len(lists)} lista(s) a processar")

    cutoff_ms = int((now_brt() - timedelta(hours=args.cutoff_hours)).timestamp() * 1000)

    out = {
        "generated_at": now_brt().isoformat(),
        "folder_id": folder_id,
        "cutoff_hours": args.cutoff_hours,
        "cutoff_ms": cutoff_ms,
        "cutoff_24h_ms": cutoff_ms,
        "lists": [],
    }

    for i, lst in enumerate(lists, 1):
        if not args.quiet:
            print(f"[pull-projetos] ({i}/{len(lists)}) {lst['name']}")
        try:
            open_tasks = fetch_tasks(lst["id"], include_closed=False)
            recent_closed = []
            closed_all = fetch_tasks(lst["id"], include_closed=True)
            for t in closed_all:
                date_done = t.get("date_done")
                if date_done and int(date_done) >= cutoff_ms:
                    if not any(o["id"] == t["id"] for o in open_tasks):
                        recent_closed.append(t)
            all_tasks = open_tasks + recent_closed
            slim = [slim_task(t, lst["id"], lst["name"]) for t in all_tasks]
            out["lists"].append({
                "id": lst["id"],
                "name": lst["name"],
                "task_count": len(slim),
                "tasks": slim,
            })
        except Exception as e:
            print(f"[pull-projetos] ERRO em {lst['name']}: {e}", file=sys.stderr)
            out["lists"].append({
                "id": lst["id"],
                "name": lst["name"],
                "task_count": 0,
                "tasks": [],
                "error": str(e),
            })
        time.sleep(0.65)

    output_path = Path(args.output)
    write_json(output_path, out)
    total = sum(l["task_count"] for l in out["lists"])
    if not args.quiet:
        print(f"[pull-projetos] OK {total} task(s) em {len(out['lists'])} lista(s) -> {output_path}")


if __name__ == "__main__":
    main()
