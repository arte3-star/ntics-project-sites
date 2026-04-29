#!/usr/bin/env python3
"""
clickup_pull_overdue_comments.py
Lê .tmp/pmo_metrics.json, identifica tasks atrasadas (top N por projeto),
busca o último comentário de cada uma via ClickUp API e enriquece o JSON.
Salva em .tmp/pmo_metrics.json (sobrescreve com campo `last_comment` por task).
"""

import sys
import time
import argparse
from pathlib import Path
from datetime import datetime, timezone, timedelta

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from reports._common import (
    load_env, load_config, clickup_get, ensure_dirs, setup_utf8_stdout,
    write_json, read_json, TMP_DIR, BR_TZ,
)


def fetch_last_comment(task_id: str, since_days: int = 30) -> dict | None:
    """Retorna o último comentário NÃO-system da task, se for recente."""
    try:
        data = clickup_get(f"/task/{task_id}/comment")
    except Exception as e:
        return None
    comments = data.get("comments") or []
    if not comments:
        return None
    cutoff = datetime.now(BR_TZ) - timedelta(days=since_days)
    for c in comments:
        text = (c.get("comment_text") or "").strip()
        if not text:
            continue
        try:
            dt = datetime.fromtimestamp(int(c.get("date", 0)) / 1000, tz=BR_TZ)
        except (TypeError, ValueError):
            continue
        if dt < cutoff:
            return None
        user = (c.get("user") or {}).get("username") or ""
        return {
            "text": text[:300],
            "date": dt.strftime("%d/%m %H:%M"),
            "user": user.split(",")[0].strip(),
        }
    return None


def main():
    setup_utf8_stdout()
    load_env()
    cfg = load_config()
    ensure_dirs()

    parser = argparse.ArgumentParser()
    parser.add_argument("--metrics", default=str(TMP_DIR / "pmo_metrics.json"))
    parser.add_argument("--top-per-project", type=int, default=5,
                        help="Buscar comentário só das N atrasadas mais antigas por projeto")
    parser.add_argument("--since-days", type=int, default=30)
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()

    metrics_path = Path(args.metrics)
    metrics = read_json(metrics_path)

    targets: list[tuple[str, dict]] = []
    seen_ids = set()
    for c in metrics.get("coordinators", []):
        for p in c.get("projects", []):
            for ov in (p.get("overdue") or [])[:args.top_per_project]:
                tid = ov.get("id")
                if tid and tid not in seen_ids:
                    seen_ids.add(tid)
                    targets.append((tid, ov))

    if not args.quiet:
        print(f"[comments] {len(targets)} task(s) atrasada(s) para buscar comentário")

    found = 0
    for i, (tid, view) in enumerate(targets, 1):
        last = fetch_last_comment(tid, since_days=args.since_days)
        if last:
            view["last_comment"] = last
            found += 1
        if not args.quiet and i % 10 == 0:
            print(f"[comments] {i}/{len(targets)} ({found} com comentário)")
        time.sleep(0.4)

    write_json(metrics_path, metrics)
    if not args.quiet:
        print(f"[comments] OK {found}/{len(targets)} com comentário recente -> {metrics_path}")


if __name__ == "__main__":
    main()
