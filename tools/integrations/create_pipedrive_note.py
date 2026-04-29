#!/usr/bin/env python3
"""
tools/create_pipedrive_note.py
Creates a note in Pipedrive for SALES meetings.
Searches for the deal by participant name, creates note linked or unlinked.
"""

import os, sys, json, argparse, requests
from pathlib import Path
from datetime import datetime

BASE_URL = "https://api.pipedrive.com/v1"

def api_key():
    key = os.environ.get("PIPEDRIVE_API_KEY", "")
    if not key:
        print("ℹ️  PIPEDRIVE_API_KEY not set — skipping")
        sys.exit(0)
    return key

def search_deal(term: str) -> int | None:
    r = requests.get(
        f"{BASE_URL}/deals/search",
        params={"term": term, "api_token": api_key(), "limit": 5}
    )
    if not r.ok:
        return None
    items = r.json().get("data", {}).get("items", [])
    if not items:
        return None
    # Prefer open deals
    for item in items:
        deal = item.get("item", {})
        if deal.get("status") == "open":
            return deal["id"]
    return items[0]["item"]["id"]

def create_note(content: str, deal_id: int | None) -> dict:
    payload = {
        "content": content,
        "pinned_to_deal_flag": True
    }
    if deal_id:
        payload["deal_id"] = deal_id

    r = requests.post(
        f"{BASE_URL}/notes",
        params={"api_token": api_key()},
        json=payload
    )
    r.raise_for_status()
    return r.json()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default=".tmp/meeting_result.json")
    parser.add_argument("--url", default="")
    parser.add_argument("--deal-id", type=int, default=0,
                        help="If provided, skip name lookup and use this deal_id directly")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        root = Path(__file__).parent.parent
        input_path = root / args.input

    meeting = json.loads(input_path.read_text(encoding="utf-8"))

    if meeting.get("meeting_type") != "SALES":
        print("ℹ️  Not a SALES meeting — skipping Pipedrive")
        return

    participants = meeting.get("external_participants", [])
    title        = meeting.get("title", "Reunião SALES")
    summary      = meeting.get("pipedrive_summary", "")
    file_url     = args.url or ""

    # Deal resolution: caller-provided > name search > unlinked
    deal_id = args.deal_id or None
    if deal_id:
        print(f"   🔗 Using caller-provided deal_id: {deal_id}")
    else:
        for p in participants:
            deal_id = search_deal(p)
            if deal_id:
                print(f"   🔗 Deal found for '{p}': {deal_id}")
                break

    if not deal_id:
        print("   ⚠️  No deal found — creating unlinked note")

    note_content = f"""## {title}

**Data:** {datetime.now().strftime('%d/%m/%Y')}
**Participantes externos:** {', '.join(participants) if participants else 'N/A'}
**Ata:** {file_url}

---

{summary}"""

    result = create_note(note_content, deal_id)
    note_id = result.get("data", {}).get("id", "?")
    print(f"✅ Pipedrive note created: ID {note_id}" + (f" → deal {deal_id}" if deal_id else " (unlinked)"))

if __name__ == "__main__":
    main()
