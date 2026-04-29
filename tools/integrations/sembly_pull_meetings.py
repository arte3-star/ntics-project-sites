#!/usr/bin/env python3
"""
tools/integrations/sembly_pull_meetings.py
Sembly API client. Lists processed meetings, fetches transcripts and attendees.

Used by: tools/integrations/sembly_to_pipedrive.py
Workflow: workflows/escritorio-projetos/sembly_to_pipedrive.md
Auth: SEMBLY_API_KEY env var (Bearer token)

NOTE: Sembly's public API surface evolves. The endpoint paths below are the
documented v1 REST routes as of 2026. If a 404/401 appears, check the current
docs at https://developer.sembly.ai/ and update the constants near the top.
"""

import os
import sys
import json
import argparse
import requests
from pathlib import Path
from datetime import datetime, timezone, timedelta

BASE_URL = "https://api.sembly.ai/v1"

LIST_PATH        = "/meetings"
DETAIL_PATH      = "/meetings/{id}"
TRANSCRIPT_PATH  = "/meetings/{id}/transcript"

INTERNAL_DOMAINS = {
    "ntics.com.br",
    "sbsustainablebusiness.com",
}


def api_key() -> str:
    key = os.environ.get("SEMBLY_API_KEY", "")
    if not key:
        print("ERROR: SEMBLY_API_KEY not set", file=sys.stderr)
        sys.exit(1)
    return key


def _headers() -> dict:
    return {
        "Authorization": f"Bearer {api_key()}",
        "Accept": "application/json",
    }


def list_recent_meetings(since_iso: str, limit: int = 50) -> list[dict]:
    """Return meetings finished after `since_iso` whose processing is complete."""
    r = requests.get(
        f"{BASE_URL}{LIST_PATH}",
        headers=_headers(),
        params={"since": since_iso, "status": "processed", "limit": limit},
        timeout=30,
    )
    r.raise_for_status()
    payload = r.json()
    return payload.get("data") or payload.get("meetings") or payload.get("results") or []


def get_meeting_detail(meeting_id: str) -> dict:
    r = requests.get(
        f"{BASE_URL}{DETAIL_PATH.format(id=meeting_id)}",
        headers=_headers(),
        timeout=30,
    )
    r.raise_for_status()
    return r.json().get("data", r.json())


def get_meeting_transcript(meeting_id: str) -> str:
    r = requests.get(
        f"{BASE_URL}{TRANSCRIPT_PATH.format(id=meeting_id)}",
        headers=_headers(),
        timeout=60,
    )
    r.raise_for_status()
    body = r.json()
    if isinstance(body, dict):
        if "transcript" in body:
            return body["transcript"] if isinstance(body["transcript"], str) else json.dumps(body["transcript"], ensure_ascii=False)
        if "segments" in body:
            return "\n".join(
                f"{s.get('speaker','?')}: {s.get('text','')}".strip()
                for s in body["segments"] if s.get("text")
            )
        if "text" in body:
            return body["text"]
    return r.text


def extract_participants(meeting_detail: dict) -> list[dict]:
    """Normalize attendee list from Sembly detail payload."""
    attendees = (
        meeting_detail.get("attendees")
        or meeting_detail.get("participants")
        or meeting_detail.get("invitees")
        or []
    )
    out = []
    for a in attendees:
        if not isinstance(a, dict):
            continue
        email = (a.get("email") or "").strip().lower()
        name  = a.get("name") or a.get("full_name") or a.get("display_name") or email
        domain = email.split("@", 1)[1] if "@" in email else ""
        out.append({
            "name": name,
            "email": email,
            "domain": domain,
            "is_external": bool(email) and domain not in INTERNAL_DOMAINS,
        })
    return out


def has_external_participant(participants: list[dict]) -> bool:
    return any(p.get("is_external") for p in participants)


def main():
    parser = argparse.ArgumentParser(description="List recent Sembly meetings")
    parser.add_argument("--since", default="", help="ISO 8601 timestamp; default = 24h ago")
    parser.add_argument("--limit", type=int, default=50)
    parser.add_argument("--json", action="store_true", help="Output raw JSON")
    args = parser.parse_args()

    since = args.since or (datetime.now(timezone.utc) - timedelta(hours=24)).isoformat()
    meetings = list_recent_meetings(since, limit=args.limit)

    if args.json:
        print(json.dumps(meetings, ensure_ascii=False, indent=2))
        return

    print(f"Found {len(meetings)} meetings since {since}")
    for m in meetings:
        mid   = m.get("id") or m.get("meeting_id")
        title = m.get("title") or m.get("name") or "?"
        ended = m.get("end_time") or m.get("ended_at") or "?"
        print(f"  - {mid} | {ended} | {title}")


if __name__ == "__main__":
    main()
