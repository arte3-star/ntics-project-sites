"""
publish_to_brevo.py — Creates an email campaign in Brevo (formerly Sendinblue) from rendered HTML.

This tool creates a draft campaign by default so the user can review in the Brevo
dashboard before sending. Mirrors the interface of send_newsletter.py (Gmail).

Usage:
  # Create draft campaign (recommended — review in Brevo before sending)
  python tools/publishing/publish_to_brevo.py \
    --html-file .tmp/newsletter_2026-04-04.html \
    --subject "ESG em Foco: Titulo da Newsletter" \
    --list-id 3 \
    --mode draft

  # Send immediately
  python tools/publishing/publish_to_brevo.py \
    --html-file .tmp/newsletter_2026-04-04.html \
    --subject "ESG em Foco: ..." \
    --mode send

Environment:
  BREVO_API_KEY=xkeysib-...   (required)
  BREVO_LIST_ID=3             (default list ID, optional if --list-id provided)
  BREVO_SENDER_NAME=NTICS Projetos  (optional)
  BREVO_SENDER_EMAIL=contato@ntics.com.br  (optional)
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).parent.parent
LOG_PATH = PROJECT_ROOT / ".tmp" / "send_log.json"


def get_brevo_api(api_key: str):
    """Configure and return Brevo EmailCampaignsApi instance."""
    try:
        import sib_api_v3_sdk
    except ImportError:
        print("ERROR: sib-api-v3-sdk not installed. Run: pip install sib-api-v3-sdk")
        sys.exit(1)

    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key["api-key"] = api_key
    api_client = sib_api_v3_sdk.ApiClient(configuration)
    return sib_api_v3_sdk.EmailCampaignsApi(api_client), sib_api_v3_sdk


def create_campaign(api, sdk, html: str, subject: str, list_id: int,
                    sender_name: str, sender_email: str, campaign_name: str) -> dict:
    """Create an email campaign in Brevo."""
    campaign = sdk.CreateEmailCampaign(
        name=campaign_name,
        subject=subject,
        sender={"name": sender_name, "email": sender_email},
        html_content=html,
        recipients={"listIds": [list_id]},
    )
    result = api.create_email_campaign(campaign)
    return {"id": result.id}


def send_campaign(api, campaign_id: int):
    """Send an existing draft campaign immediately."""
    api.send_email_campaign_now(campaign_id)


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
    parser = argparse.ArgumentParser(description="Publish newsletter to Brevo")
    parser.add_argument("--html-file", required=True, help="Path to rendered HTML newsletter")
    parser.add_argument("--subject", required=True, help="Email subject line")
    parser.add_argument("--list-id", type=int, help="Brevo contact list ID")
    parser.add_argument("--sender-name", help="Sender display name")
    parser.add_argument("--sender-email", help="Sender email address")
    parser.add_argument("--campaign-name", help="Campaign name in Brevo dashboard")
    parser.add_argument("--mode", choices=["draft", "send"], default="draft",
                        help="'draft' (default) or 'send' immediately")
    args = parser.parse_args()

    # Validate API key
    api_key = os.getenv("BREVO_API_KEY", "")
    if not api_key:
        print("ERROR: BREVO_API_KEY environment variable is required")
        print("Get your API key from: Brevo > Settings > SMTP & API > API Keys")
        sys.exit(1)

    # Load HTML
    html_path = Path(args.html_file)
    if not html_path.exists():
        print(f"ERROR: HTML file not found: {html_path}")
        sys.exit(1)
    with open(html_path, "r", encoding="utf-8") as f:
        html = f.read()

    # Resolve parameters
    list_id = args.list_id or int(os.getenv("BREVO_LIST_ID", "0"))
    if not list_id:
        print("ERROR: --list-id or BREVO_LIST_ID env var required")
        print("Find your list ID in: Brevo > Contacts > Lists")
        sys.exit(1)

    sender_name = args.sender_name or os.getenv("BREVO_SENDER_NAME", "NTICS Projetos")
    sender_email = args.sender_email or os.getenv("BREVO_SENDER_EMAIL", "contato@ntics.com.br")
    date_str = datetime.today().strftime("%Y-%m-%d")
    campaign_name = args.campaign_name or f"ESG em Foco - {date_str}"

    print(f"Mode: {args.mode.upper()}")
    print(f"Subject: {args.subject}")
    print(f"List ID: {list_id}")
    print(f"Sender: {sender_name} <{sender_email}>")
    print(f"Campaign: {campaign_name}")

    # Create campaign
    api, sdk = get_brevo_api(api_key)

    try:
        result = create_campaign(
            api, sdk, html, args.subject, list_id,
            sender_name, sender_email, campaign_name,
        )
        campaign_id = result["id"]
        print(f"\nOK Campaign created in Brevo (draft)")
        print(f"  Campaign ID: {campaign_id}")

        if args.mode == "send":
            send_campaign(api, campaign_id)
            print(f"OK Campaign sent!")
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "channel": "brevo",
                "mode": "sent",
                "subject": args.subject,
                "list_id": list_id,
                "campaign_id": campaign_id,
                "html_file": str(html_path),
            }
        else:
            print(f"  Open Brevo dashboard to review and send the campaign.")
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "channel": "brevo",
                "mode": "draft",
                "subject": args.subject,
                "list_id": list_id,
                "campaign_id": campaign_id,
                "html_file": str(html_path),
            }

        log_send(log_entry)
        print(f"  Log saved to: {LOG_PATH}")

    except Exception as e:
        error_msg = str(e)
        if "sender" in error_msg.lower():
            print(f"\nERROR: Sender not verified. Verify '{sender_email}' in Brevo > Senders.")
        elif "unauthorized" in error_msg.lower() or "authentication" in error_msg.lower():
            print(f"\nERROR: Invalid API key. Check BREVO_API_KEY in .env")
        else:
            print(f"\nERROR: Brevo API error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
