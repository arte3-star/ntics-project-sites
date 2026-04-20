#!/usr/bin/env python3
"""
tools/update_learning_registry.py
Appends a new row to the Learning Registry page in ClickUp.
Doc: 8cje8p1-65331 | Page: 8cje8p1-39691
"""

import os, sys, json, argparse, requests
from datetime import datetime

WS_ID   = "9011929793"
DOC_ID  = "8cje8p1-65331"
PAGE_ID = "8cje8p1-39691"

def headers():
    return {
        "Authorization": os.environ["CLICKUP_API_KEY"],
        "Content-Type": "application/json"
    }

def get_current_content() -> str:
    r = requests.get(
        f"https://api.clickup.com/api/v3/workspaces/{WS_ID}/docs/{DOC_ID}/pages",
        headers=headers(),
        params={"page_ids": PAGE_ID, "content_format": "text/md"}
    )
    r.raise_for_status()
    data = r.json()
    pages = data if isinstance(data, list) else data.get("pages", [])
    return pages[0].get("content", "") if pages else ""

def update_content(content: str):
    r = requests.put(
        f"https://api.clickup.com/api/v3/workspaces/{WS_ID}/docs/{DOC_ID}/pages/{PAGE_ID}",
        headers=headers(),
        json={"content": content, "content_format": "text/md"}
    )
    r.raise_for_status()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--learning", required=True, help="New learning to register")
    parser.add_argument("--meeting", default="Reunião", help="Meeting title")
    args = parser.parse_args()

    today      = datetime.now().strftime("%d/%m/%Y")
    new_row    = f"| {today} | {args.meeting[:60]} | {args.learning[:150]} | Agente IA |"
    current    = get_current_content()

    # Insert before placeholder row, or append if not found
    placeholder = "| — | — | — | — |"
    if placeholder in current:
        updated = current.replace(placeholder, f"{new_row}\n{placeholder}")
    else:
        updated = current + f"\n{new_row}"

    update_content(updated)
    print(f"✅ Learning registered: {args.learning[:60]}...")

if __name__ == "__main__":
    main()
