"""
send_newsletter.py — Creates a Gmail draft (or sends directly) using the rendered HTML.

This tool wraps Gmail sending via the Gmail API (using credentials already configured
in the project). It creates a draft by default so the user can review before sending.

Usage:
  # Create draft (recommended — review in Gmail before sending)
  python tools/send_newsletter.py \
    --html-file .tmp/newsletter_2026-03-20.html \
    --subject "Good Signal: $2.3T in Green Bonds — March 20, 2026" \
    --to "subscriber@email.com,another@email.com" \
    --mode draft

  # Send directly (skip review)
  python tools/send_newsletter.py \
    --html-file .tmp/newsletter_2026-03-20.html \
    --subject "Good Signal: ..." \
    --to "list@email.com" \
    --mode send

Environment:
  NEWSLETTER_RECIPIENTS=email1@...,email2@... (default recipients, optional)
  NEWSLETTER_FROM=your@gmail.com (sender, optional — defaults to authenticated Gmail)

Credentials:
  credentials.json and token.json must be present in the project root.
  Run: python tools/send_newsletter.py --auth   to authenticate for the first time.
"""

import argparse
import base64
import json
import os
import sys
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).parent.parent
LOG_PATH = PROJECT_ROOT / ".tmp" / "send_log.json"

SCOPES = ["https://www.googleapis.com/auth/gmail.send",
          "https://www.googleapis.com/auth/gmail.compose"]


def get_gmail_service():
    """Authenticate and return a Gmail API service object."""
    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build
    except ImportError:
        print("ERROR: Google API libraries not installed.")
        print("Run: pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib")
        sys.exit(1)

    creds = None
    token_path = PROJECT_ROOT / "token.json"
    creds_path = PROJECT_ROOT / "credentials.json"

    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not creds_path.exists():
                print(f"ERROR: credentials.json not found at {creds_path}")
                print("Download it from Google Cloud Console > APIs > Gmail API > Credentials")
                sys.exit(1)
            flow = InstalledAppFlow.from_client_secrets_file(str(creds_path), SCOPES)
            creds = flow.run_local_server(port=0)

        with open(token_path, "w") as f:
            f.write(creds.to_json())

    service = build("gmail", "v1", credentials=creds)
    return service


def build_message(html: str, subject: str, to: str, sender: str = "me") -> dict:
    """Build a base64-encoded email message."""
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = to

    # Plain text fallback
    plain = "Esta newsletter requer um cliente de email com suporte a HTML.\nAcesse a versão web para visualizar o conteúdo completo."
    msg.attach(MIMEText(plain, "plain", "utf-8"))
    msg.attach(MIMEText(html, "html", "utf-8"))

    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    return {"raw": raw}


def create_draft(service, message: dict) -> dict:
    """Create a Gmail draft."""
    draft = service.users().drafts().create(
        userId="me",
        body={"message": message}
    ).execute()
    return draft


def send_message(service, message: dict) -> dict:
    """Send a Gmail message directly."""
    sent = service.users().messages().send(
        userId="me",
        body=message
    ).execute()
    return sent


def log_send(entry: dict):
    """Append an entry to the send log."""
    LOG_PATH.parent.mkdir(exist_ok=True)
    log = []
    if LOG_PATH.exists():
        with open(LOG_PATH, "r", encoding="utf-8") as f:
            try:
                log = json.load(f)
            except json.JSONDecodeError:
                log = []
    log.append(entry)
    with open(LOG_PATH, "w", encoding="utf-8") as f:
        json.dump(log, f, ensure_ascii=False, indent=2)


def main():
    parser = argparse.ArgumentParser(description="Send newsletter via Gmail")
    parser.add_argument("--html-file", required=True, help="Path to rendered HTML newsletter")
    parser.add_argument("--subject", required=True, help="Email subject line")
    parser.add_argument("--to", help="Recipient(s), comma-separated")
    parser.add_argument("--mode", choices=["draft", "send"], default="draft",
                        help="'draft' (default) or 'send' directly")
    parser.add_argument("--auth", action="store_true", help="Re-authenticate with Gmail")
    args = parser.parse_args()

    # Load HTML
    html_path = Path(args.html_file)
    if not html_path.exists():
        print(f"ERROR: HTML file not found: {html_path}")
        sys.exit(1)
    with open(html_path, "r", encoding="utf-8") as f:
        html = f.read()

    # Determine recipients
    recipients = args.to or os.getenv("NEWSLETTER_RECIPIENTS", "")
    if not recipients:
        print("ERROR: --to or NEWSLETTER_RECIPIENTS env var required")
        sys.exit(1)

    print(f"Mode: {args.mode.upper()}")
    print(f"Subject: {args.subject}")
    print(f"Recipients: {recipients}")

    # Authenticate
    service = get_gmail_service()
    message = build_message(html, args.subject, recipients)

    if args.mode == "draft":
        result = create_draft(service, message)
        draft_id = result.get("id", "unknown")
        print(f"\n✓ Draft created in Gmail")
        print(f"  Draft ID: {draft_id}")
        print(f"  → Open Gmail and search for the draft to review and send.")
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "mode": "draft",
            "subject": args.subject,
            "recipients": recipients,
            "html_file": str(html_path),
            "draft_id": draft_id,
        }
    else:
        result = send_message(service, message)
        msg_id = result.get("id", "unknown")
        print(f"\n✓ Message sent!")
        print(f"  Message ID: {msg_id}")
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "mode": "sent",
            "subject": args.subject,
            "recipients": recipients,
            "html_file": str(html_path),
            "message_id": msg_id,
        }

    log_send(log_entry)
    print(f"  Log saved to: {LOG_PATH}")


if __name__ == "__main__":
    main()
