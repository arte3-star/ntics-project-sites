#!/usr/bin/env python3
"""
clickup_remove_list_dependencies.py
Remove TODAS as dependências entre tasks de uma ou mais listas ClickUp.

Uso:
    python tools/integrations/clickup_remove_list_dependencies.py \
        --list 901113597559 901113597530 901113654171 \
               901113597556 901113597557 901113597561 \
        [--dry-run] [--report output/clickup-deps/2026-04-27.json]

Não deleta tasks; só o vínculo de dependência via DELETE /task/{id}/dependency.
Reaproveita helpers de tools/reports/_common.py (token .env, retry, base URL).
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from reports._common import (  # noqa: E402
    CLICKUP_BASE,
    clickup_get,
    clickup_headers,
    load_env,
)


def fetch_all_tasks(list_id: str):
    """Pagina /list/{id}/task até página vazia (100 tasks/pagina)."""
    page = 0
    while True:
        data = clickup_get(
            f"/list/{list_id}/task",
            params={
                "subtasks": "true",
                "include_closed": "true",
                "archived": "false",
                "page": page,
            },
        )
        tasks = data.get("tasks", [])
        if not tasks:
            return
        for t in tasks:
            yield t
        if len(tasks) < 100:
            return
        page += 1


def get_dependencies(task_id: str) -> list[dict]:
    return clickup_get(f"/task/{task_id}").get("dependencies", []) or []


def delete_dependency(task_id: str, depends_on: str, dry_run: bool = False) -> bool:
    if dry_run:
        return True
    url = f"{CLICKUP_BASE}/task/{task_id}/dependency"
    delay = 1.0
    for attempt in range(4):
        r = requests.delete(
            url,
            headers=clickup_headers(),
            params={"depends_on": depends_on},
            timeout=30,
        )
        if r.status_code in (200, 204):
            return True
        if r.status_code == 429 or r.status_code >= 500:
            if attempt == 3:
                r.raise_for_status()
            time.sleep(delay)
            delay *= 2
            continue
        r.raise_for_status()
    return False


def process_list(list_id: str, dry_run: bool, summary: dict) -> dict:
    info = {
        "tasks_scanned": 0,
        "deps_found": 0,
        "deps_removed": 0,
        "removed": [],
    }
    seen_pairs: set[tuple[str, str]] = set()

    for task in fetch_all_tasks(list_id):
        tid = task["id"]
        info["tasks_scanned"] += 1
        try:
            deps = get_dependencies(tid)
        except Exception as exc:  # noqa: BLE001
            summary["errors"].append({"task": tid, "stage": "get", "err": str(exc)})
            continue

        for d in deps:
            owner = d.get("task_id")
            dep_on = d.get("depends_on")
            if not owner or not dep_on:
                continue
            if owner != tid:
                continue
            pair = (owner, dep_on)
            if pair in seen_pairs:
                continue
            seen_pairs.add(pair)
            info["deps_found"] += 1
            try:
                ok = delete_dependency(owner, dep_on, dry_run)
                if ok:
                    info["deps_removed"] += 1
                    info["removed"].append(
                        {
                            "task": owner,
                            "depends_on": dep_on,
                            "type": d.get("type"),
                        }
                    )
            except Exception as exc:  # noqa: BLE001
                summary["errors"].append(
                    {
                        "task": owner,
                        "depends_on": dep_on,
                        "stage": "delete",
                        "err": str(exc),
                    }
                )

        if info["tasks_scanned"] % 25 == 0:
            print(
                f"  [{list_id}] scanned={info['tasks_scanned']} "
                f"deps_removed={info['deps_removed']}",
                flush=True,
            )

    return info


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--list", nargs="+", required=True, help="List IDs ClickUp")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--report", type=str, default=None)
    args = parser.parse_args()

    load_env()

    summary: dict = {
        "timestamp": datetime.now().isoformat(),
        "dry_run": args.dry_run,
        "lists": {},
        "total_tasks": 0,
        "total_deps_found": 0,
        "total_deps_removed": 0,
        "errors": [],
    }

    for list_id in args.list:
        print(f"\n=== Lista {list_id} ===", flush=True)
        info = process_list(list_id, args.dry_run, summary)
        summary["lists"][list_id] = info
        summary["total_tasks"] += info["tasks_scanned"]
        summary["total_deps_found"] += info["deps_found"]
        summary["total_deps_removed"] += info["deps_removed"]
        print(
            f"  -> tasks={info['tasks_scanned']} "
            f"deps_found={info['deps_found']} deps_removed={info['deps_removed']}",
            flush=True,
        )

    head = {k: v for k, v in summary.items() if k != "lists"}
    print("\n=== RESUMO ===")
    print(json.dumps(head, indent=2, ensure_ascii=False))

    if args.report:
        out = Path(args.report)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(
            json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        print(f"\nFull report -> {out}")

    return 0 if not summary["errors"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
