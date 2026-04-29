#!/usr/bin/env python3
"""
clickup_pull_sprint.py
Identifica a Sprint ativa (lista cuja janela contém hoje) na pasta Sprint do
Escritório de Projetos e puxa todas as tasks dela.
Salva em .tmp/pmo_raw_sprint.json.
"""

import re
import sys
import time
import argparse
from pathlib import Path
from datetime import date, datetime

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from reports._common import (
    load_env, load_config, clickup_get, ensure_dirs,
    setup_utf8_stdout, write_json, today_brt, TMP_DIR,
)
from integrations.clickup_pull_projetos_ntics import slim_task, fetch_tasks


SPRINT_NAME_RE = re.compile(
    r"Sprint\s+(\d+)\s*\(\s*(\d{1,2})/(\d{1,2})/(\d{2,4})\s*-\s*(\d{1,2})/(\d{1,2})/(\d{2,4})\s*\)",
    re.IGNORECASE,
)


def parse_sprint_window(name: str):
    """Extrai (numero, inicio, fim) do nome 'Sprint NN (DD/M/YY - DD/M/YY)'."""
    m = SPRINT_NAME_RE.search(name or "")
    if not m:
        return None
    num = int(m.group(1))
    d1, m1, y1, d2, m2, y2 = (int(g) for g in m.groups()[1:])
    y1 = 2000 + y1 if y1 < 100 else y1
    y2 = 2000 + y2 if y2 < 100 else y2
    try:
        ini = date(y1, m1, d1)
        fim = date(y2, m2, d2)
    except ValueError:
        return None
    return num, ini, fim


def find_active_sprint(folder_id: str, ref: date) -> dict | None:
    data = clickup_get(f"/folder/{folder_id}/list")
    candidates = []
    for lst in data.get("lists", []):
        parsed = parse_sprint_window(lst.get("name", ""))
        if not parsed:
            continue
        num, ini, fim = parsed
        candidates.append({"id": lst["id"], "name": lst["name"], "num": num, "ini": ini, "fim": fim})
    if not candidates:
        return None
    active = [c for c in candidates if c["ini"] <= ref <= c["fim"]]
    if active:
        return active[0]
    future = sorted([c for c in candidates if c["ini"] > ref], key=lambda c: c["ini"])
    if future:
        return future[0]
    past = sorted(candidates, key=lambda c: c["fim"], reverse=True)
    return past[0] if past else None


def main():
    setup_utf8_stdout()
    load_env()
    cfg = load_config()
    ensure_dirs()

    parser = argparse.ArgumentParser()
    parser.add_argument("--date", help="Data referência YYYY-MM-DD (default: hoje BRT)")
    parser.add_argument("--quiet", action="store_true")
    parser.add_argument("--output", default=str(TMP_DIR / "pmo_raw_sprint.json"))
    args = parser.parse_args()

    ref = today_brt() if not args.date else datetime.strptime(args.date, "%Y-%m-%d").date()
    folder_id = cfg["clickup"]["folder_sprint"]

    if not args.quiet:
        print(f"[pull-sprint] Procurando sprint ativa em {folder_id} para {ref.isoformat()}")
    active = find_active_sprint(folder_id, ref)
    if not active:
        print("[pull-sprint] ERRO: nenhuma sprint encontrada", file=sys.stderr)
        sys.exit(1)
    if not args.quiet:
        print(f"[pull-sprint] Sprint {active['num']}: {active['name']} ({active['ini']} -> {active['fim']})")

    open_tasks = fetch_tasks(active["id"], include_closed=False)
    closed_tasks = fetch_tasks(active["id"], include_closed=True)
    seen = {t["id"] for t in open_tasks}
    extra_closed = [t for t in closed_tasks if t["id"] not in seen]
    all_tasks = open_tasks + extra_closed
    slim = [slim_task(t, active["id"], active["name"]) for t in all_tasks]

    out = {
        "generated_at": datetime.now().isoformat(),
        "ref_date": ref.isoformat(),
        "sprint": {
            "id": active["id"],
            "name": active["name"],
            "num": active["num"],
            "start": active["ini"].isoformat(),
            "end": active["fim"].isoformat(),
        },
        "task_count": len(slim),
        "tasks": slim,
    }

    output_path = Path(args.output)
    write_json(output_path, out)
    if not args.quiet:
        print(f"[pull-sprint] OK {len(slim)} task(s) -> {output_path}")


if __name__ == "__main__":
    main()
