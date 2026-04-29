#!/usr/bin/env python3
"""
tools/integrations/sembly_to_pipedrive.py
Polling orchestrator: pulls new Sembly meetings, classifies the SALES ones
and creates a note in the matching Pipedrive deal.

Workflow: workflows/escritorio-projetos/sembly_to_pipedrive.md
Schedule: 09h, 13h, 18h, 22h (BRT).
Env: SEMBLY_API_KEY, PIPEDRIVE_API_KEY, ANTHROPIC_API_KEY

Idempotency: .cache/sembly_processed.json holds last_run + processed meeting IDs.
"""

import os
import sys
import json
import argparse
import subprocess
from pathlib import Path
from datetime import datetime, timezone, timedelta

ROOT = Path(__file__).resolve().parent.parent.parent

CACHE_DIR  = ROOT / ".cache"
CACHE_FILE = CACHE_DIR / "sembly_processed.json"
LOG_DIR    = ROOT / "logs"
TMP_DIR    = ROOT / ".tmp"

sys.path.insert(0, str(ROOT / "tools" / "integrations"))
import sembly_pull_meetings as sembly                 # noqa: E402
import pipedrive_match_deal as pdmatch                # noqa: E402

CLASSIFIER = ROOT / "tools" / "meetings" / "classify_meeting.py"
NOTE_SCRIPT = ROOT / "tools" / "integrations" / "create_pipedrive_note.py"


def load_state() -> dict:
    if CACHE_FILE.exists():
        return json.loads(CACHE_FILE.read_text(encoding="utf-8"))
    return {"last_run": None, "processed_ids": []}


def save_state(state: dict) -> None:
    CACHE_DIR.mkdir(exist_ok=True)
    CACHE_FILE.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def log_line(msg: str) -> None:
    LOG_DIR.mkdir(exist_ok=True)
    today = datetime.now().strftime("%Y-%m-%d")
    log_file = LOG_DIR / f"sembly_pipedrive_{today}.log"
    ts = datetime.now().strftime("%H:%M:%S")
    line = f"[{ts}] {msg}\n"
    with log_file.open("a", encoding="utf-8") as f:
        f.write(line)
    print(msg)


def classify(transcript: str, title: str, sembly_url: str) -> dict | None:
    TMP_DIR.mkdir(exist_ok=True)
    transcript_file = TMP_DIR / "transcript.txt"
    transcript_file.write_text(transcript, encoding="utf-8")

    cmd = [
        sys.executable, str(CLASSIFIER),
        "--name", title[:80],
        "--url", sembly_url,
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    if proc.returncode != 0:
        log_line(f"  classifier FAILED: {proc.stderr.strip()[:300]}")
        return None

    result_file = TMP_DIR / "meeting_result.json"
    if not result_file.exists():
        log_line("  classifier produced no meeting_result.json")
        return None
    return json.loads(result_file.read_text(encoding="utf-8"))


def post_note(deal_id: int | None, sembly_url: str) -> bool:
    cmd = [
        sys.executable, str(NOTE_SCRIPT),
        "--input", str(TMP_DIR / "meeting_result.json"),
        "--url", sembly_url,
    ]
    if deal_id:
        cmd += ["--deal-id", str(deal_id)]
    proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    if proc.returncode != 0:
        log_line(f"  note POST FAILED: {proc.stderr.strip()[:300]}")
        return False
    log_line(f"  note: {proc.stdout.strip().splitlines()[-1]}")
    return True


def process_meeting(meeting: dict, dry_run: bool) -> str:
    """Returns one of: PROCESSED, SKIP_NO_EXTERNAL, SKIP_NOT_SALES, FAILED."""
    mid   = meeting.get("id") or meeting.get("meeting_id")
    title = meeting.get("title") or meeting.get("name") or "Reunião"
    sembly_url = meeting.get("share_url") or meeting.get("url") or ""

    log_line(f"meeting {mid} | {title}")

    detail = sembly.get_meeting_detail(mid)
    participants = sembly.extract_participants(detail)
    if not sembly.has_external_participant(participants):
        log_line("  skip: no external participant")
        return "SKIP_NO_EXTERNAL"

    transcript = sembly.get_meeting_transcript(mid)
    if len(transcript) < 50:
        log_line("  skip: transcript too short")
        return "SKIP_NO_EXTERNAL"

    result = classify(transcript, title, sembly_url)
    if not result:
        return "FAILED"

    mtype = result.get("meeting_type")
    log_line(f"  type={mtype} confidence={result.get('confidence')}")
    if mtype != "SALES":
        return "SKIP_NOT_SALES"

    external_emails = [p["email"] for p in participants if p.get("is_external") and p.get("email")]
    deal_id, matched = pdmatch.find_deal_for_participants(external_emails)
    if deal_id:
        log_line(f"  matched deal {deal_id} via {matched}")
    else:
        log_line(f"  no deal match for emails={external_emails} -> ORPHAN note")

    if dry_run:
        log_line("  dry-run: skipping POST")
        return "PROCESSED"

    ok = post_note(deal_id, sembly_url)
    return "PROCESSED" if ok else "FAILED"


def main():
    parser = argparse.ArgumentParser(description="Sembly -> Pipedrive orchestrator")
    parser.add_argument("--lookback-hours", type=int, default=24,
                        help="Window when no last_run cached (default 24h)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Skip the actual POST to Pipedrive")
    args = parser.parse_args()

    state = load_state()
    since = state.get("last_run") or (
        datetime.now(timezone.utc) - timedelta(hours=args.lookback_hours)
    ).isoformat()

    log_line(f"=== run start | since={since} | dry_run={args.dry_run} ===")

    meetings = sembly.list_recent_meetings(since)
    processed_ids = set(state.get("processed_ids", []))
    new_meetings = [m for m in meetings if (m.get("id") or m.get("meeting_id")) not in processed_ids]

    log_line(f"sembly returned {len(meetings)} meetings, {len(new_meetings)} new")

    counts = {"PROCESSED": 0, "SKIP_NO_EXTERNAL": 0, "SKIP_NOT_SALES": 0, "FAILED": 0}
    for m in new_meetings:
        try:
            outcome = process_meeting(m, args.dry_run)
        except Exception as e:
            log_line(f"  EXCEPTION: {type(e).__name__}: {e}")
            outcome = "FAILED"
        counts[outcome] = counts.get(outcome, 0) + 1
        if outcome != "FAILED" and not args.dry_run:
            mid = m.get("id") or m.get("meeting_id")
            if mid:
                processed_ids.add(mid)

    if not args.dry_run:
        state["last_run"] = datetime.now(timezone.utc).isoformat()
        state["processed_ids"] = sorted(processed_ids)[-500:]  # keep last 500
        save_state(state)

    log_line(f"=== run end | {counts} ===")


if __name__ == "__main__":
    main()
