#!/usr/bin/env python3
"""
send_pmo_email.py
Envia o relatório diário PMO via Gmail API.
Modos: draft (cria rascunho), send (envia direto).
Após envio: verifica via users.messages.get que SENT está nos labelIds.
Salva log em output/relatorios/pmo-diario/{date}.sent.json.
"""

import os
import sys
import base64
import argparse
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from datetime import date, datetime

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from reports._common import (
    load_env, load_config, ensure_dirs, setup_utf8_stdout,
    write_json, read_json, today_brt, OUTPUT_DIR, ROOT, TMP_DIR,
)


SCOPES = [
    "https://www.googleapis.com/auth/gmail.modify",
]


def get_gmail_service():
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build

    gws_dir = ROOT / "tools" / "gws"
    token_path = gws_dir / "token.json"
    creds_path = gws_dir / "credentials.json"
    creds = None
    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not creds_path.exists():
                print(f"[send] credentials.json ausente em {creds_path}", file=sys.stderr)
                sys.exit(1)
            flow = InstalledAppFlow.from_client_secrets_file(str(creds_path), SCOPES)
            creds = flow.run_local_server(port=0)
        token_path.write_text(creds.to_json(), encoding="utf-8")
    return build("gmail", "v1", credentials=creds)


def build_subject(metrics: dict, ref: date, kind: str = "daily") -> str:
    if kind == "weekly":
        t = metrics.get("totals", {})
        return (f"PMO Semanal - {ref.strftime('%d/%m')} - "
                f"{t.get('entregues', 0)} entregues / {t.get('proximas', 0)} próxima")
    t = metrics.get("totals", {})
    vermelhos = sum(1 for p in metrics.get("projects", []) if p.get("health") == "VERMELHO")
    alertas = vermelhos + (t.get("blockers", 0) or 0) + len(metrics.get("decisions_pendentes", []))
    return f"PMO Diário - {ref.strftime('%d/%m')} - {alertas} alerta{'s' if alertas != 1 else ''}"


def build_message(html: str, subject: str, to: list[str], cc: list[str], reply_to: str, sender: str) -> dict:
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = ", ".join(to)
    if cc:
        msg["Cc"] = ", ".join(cc)
    if reply_to:
        msg["Reply-To"] = reply_to
    plain = "Este relatório requer um cliente de email com suporte a HTML."
    msg.attach(MIMEText(plain, "plain", "utf-8"))
    msg.attach(MIMEText(html, "html", "utf-8"))
    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    return {"raw": raw}


def verify_sent(service, message_id: str) -> bool:
    try:
        meta = service.users().messages().get(
            userId="me", id=message_id, format="metadata"
        ).execute()
        return "SENT" in (meta.get("labelIds") or [])
    except Exception as e:
        print(f"[send] verify falhou: {e}", file=sys.stderr)
        return False


def main():
    setup_utf8_stdout()
    load_env()
    cfg = load_config()
    ensure_dirs()

    parser = argparse.ArgumentParser()
    parser.add_argument("--html", required=True)
    parser.add_argument("--mode", choices=["draft", "send"], default="draft")
    parser.add_argument("--date", default=today_brt().isoformat())
    parser.add_argument("--metrics", default=str(TMP_DIR / "pmo_metrics.json"))
    parser.add_argument("--subject-kind", choices=["daily", "weekly"], default="daily")
    args = parser.parse_args()
    if args.subject_kind == "weekly" and args.metrics == str(TMP_DIR / "pmo_metrics.json"):
        args.metrics = str(TMP_DIR / "pmo_weekly_metrics.json")

    html_path = Path(args.html)
    if not html_path.exists():
        print(f"[send] HTML não encontrado: {html_path}", file=sys.stderr)
        sys.exit(1)
    html = html_path.read_text(encoding="utf-8")

    metrics_path = Path(args.metrics)
    metrics = read_json(metrics_path) if metrics_path.exists() else {}
    ref = date.fromisoformat(args.date)
    subject = build_subject(metrics, ref, args.subject_kind)

    to = cfg["recipients"]["to"]
    cc = cfg["recipients"].get("cc", []) or []
    reply_to = cfg["recipients"].get("reply_to", "")
    sender = cfg["sender"]["email"]

    print(f"[send] mode={args.mode} subject={subject!r}")
    print(f"[send] to={to} cc={cc}")

    service = get_gmail_service()
    message = build_message(html, subject, to, cc, reply_to, sender)

    log = {
        "timestamp": datetime.now().isoformat(),
        "mode": args.mode,
        "subject": subject,
        "to": to,
        "cc": cc,
        "html_file": str(html_path),
        "html_bytes": len(html),
    }

    if args.mode == "draft":
        result = service.users().drafts().create(userId="me", body={"message": message}).execute()
        log["draft_id"] = result.get("id")
        print(f"[send] OK draft id={log['draft_id']}")
    else:
        result = service.users().messages().send(userId="me", body=message).execute()
        msg_id = result.get("id")
        log["message_id"] = msg_id
        ok = verify_sent(service, msg_id)
        log["verified_sent"] = ok
        if not ok:
            print(f"[send] AVISO: mensagem {msg_id} sem label SENT", file=sys.stderr)
        else:
            print(f"[send] OK enviado e verificado id={msg_id}")

    if args.subject_kind == "weekly":
        out_log = OUTPUT_DIR.parent / "pmo-semanal" / f"{ref.isoformat()}.sent.json"
    else:
        out_log = OUTPUT_DIR / f"{ref.isoformat()}.sent.json"
    out_log.parent.mkdir(exist_ok=True, parents=True)
    write_json(out_log, log)
    print(f"[send] log -> {out_log}")


if __name__ == "__main__":
    main()
