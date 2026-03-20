#!/usr/bin/env python3
"""
tools/read_google_doc.py
Reads a Google Doc by URL and saves content to .tmp/transcript.txt
Requires: GOOGLE_CREDS_FILE env var pointing to service account JSON
"""

import os, sys, argparse, re
from pathlib import Path
from google.oauth2 import service_account
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/documents.readonly"]

def extract_file_id(url: str) -> str:
    match = re.search(r"/d/([a-zA-Z0-9_-]+)", url)
    if match:
        return match.group(1)
    # Maybe it's already an ID
    if re.match(r"^[a-zA-Z0-9_-]{25,}$", url):
        return url
    raise ValueError(f"Cannot extract file ID from: {url}")

def read_doc(file_id: str) -> str:
    creds_file = os.environ.get("GOOGLE_CREDS_FILE", "credentials.json")
    creds = service_account.Credentials.from_service_account_file(creds_file, scopes=SCOPES)
    service = build("docs", "v1", credentials=creds)

    doc = service.documents().get(documentId=file_id).execute()
    text = []
    for element in doc.get("body", {}).get("content", []):
        paragraph = element.get("paragraph")
        if paragraph:
            for part in paragraph.get("elements", []):
                run = part.get("textRun")
                if run:
                    text.append(run.get("content", ""))
    return "".join(text).strip()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True, help="Google Doc URL or file ID")
    args = parser.parse_args()

    root = Path(__file__).parent.parent
    tmp  = root / ".tmp"
    tmp.mkdir(exist_ok=True)

    file_id = extract_file_id(args.url)
    print(f"📄 Reading Google Doc: {file_id[:20]}...")

    content = read_doc(file_id)

    if len(content) < 50:
        print("ERROR: Document too short or empty", file=sys.stderr)
        sys.exit(1)

    output = tmp / "transcript.txt"
    output.write_text(content, encoding="utf-8")

    print(f"✅ {len(content)} chars saved to {output}")

if __name__ == "__main__":
    main()
