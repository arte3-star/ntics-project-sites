"""
GWS CLI — lightweight Google Workspace access via bash.
Usage:
  python gws_cli.py gmail list [--query "newer_than:3d"] [--limit 5]
  python gws_cli.py gmail read <message_id>
  python gws_cli.py calendar list [--days 7]
  python gws_cli.py calendar create --summary "Reuniao" --start "2026-04-07T14:00:00" --end "2026-04-07T15:00:00"
  python gws_cli.py drive search --query "name contains 'relatorio'"
"""
import argparse
import json
import sys
from datetime import datetime, timedelta, timezone

from googleapiclient.discovery import build
from gws_auth import get_credentials


def gmail_list(args):
    service = build("gmail", "v1", credentials=get_credentials())
    query = args.query or ""
    results = service.users().messages().list(
        userId="me", q=query, maxResults=args.limit
    ).execute()
    messages = results.get("messages", [])
    if not messages:
        print("No messages found.")
        return
    for msg in messages:
        detail = service.users().messages().get(
            userId="me", id=msg["id"], format="metadata",
            metadataHeaders=["From", "Subject", "Date"]
        ).execute()
        headers = {h["name"]: h["value"] for h in detail["payload"]["headers"]}
        print(f"{msg['id']}  {headers.get('Date','')}  {headers.get('From','')}  {headers.get('Subject','')}")


def gmail_read(args):
    service = build("gmail", "v1", credentials=get_credentials())
    msg = service.users().messages().get(
        userId="me", id=args.message_id, format="full"
    ).execute()
    headers = {h["name"]: h["value"] for h in msg["payload"]["headers"]}
    print(f"From: {headers.get('From','')}")
    print(f"To: {headers.get('To','')}")
    print(f"Subject: {headers.get('Subject','')}")
    print(f"Date: {headers.get('Date','')}")
    print("---")
    # Get body
    import base64
    parts = msg["payload"].get("parts", [msg["payload"]])
    for part in parts:
        if part["mimeType"] == "text/plain":
            data = part["body"].get("data", "")
            if data:
                print(base64.urlsafe_b64decode(data).decode("utf-8", errors="replace"))
                return
    print(msg.get("snippet", ""))


def calendar_list(args):
    service = build("calendar", "v3", credentials=get_credentials())
    now = datetime.now(timezone.utc)
    time_max = now + timedelta(days=args.days)
    results = service.events().list(
        calendarId="primary",
        timeMin=now.isoformat(),
        timeMax=time_max.isoformat(),
        maxResults=args.limit,
        singleEvents=True,
        orderBy="startTime",
    ).execute()
    events = results.get("items", [])
    if not events:
        print("No upcoming events.")
        return
    for ev in events:
        start = ev["start"].get("dateTime", ev["start"].get("date", ""))
        print(f"{start[:16]}  {ev.get('summary','(sem titulo)')}")


def calendar_create(args):
    service = build("calendar", "v3", credentials=get_credentials())
    event = {
        "summary": args.summary,
        "start": {"dateTime": args.start, "timeZone": "America/Sao_Paulo"},
        "end": {"dateTime": args.end, "timeZone": "America/Sao_Paulo"},
    }
    if args.description:
        event["description"] = args.description
    created = service.events().insert(calendarId="primary", body=event).execute()
    print(f"Created: {created['htmlLink']}")


def drive_search(args):
    service = build("drive", "v3", credentials=get_credentials())
    results = service.files().list(
        q=args.query, pageSize=args.limit,
        fields="files(id, name, mimeType, modifiedTime)"
    ).execute()
    files = results.get("files", [])
    if not files:
        print("No files found.")
        return
    for f in files:
        print(f"{f['id']}  {f.get('modifiedTime','')[:10]}  {f['name']}")


def drive_download(args):
    """Baixa um arquivo do Drive para o caminho especificado."""
    import io
    from googleapiclient.http import MediaIoBaseDownload

    service = build("drive", "v3", credentials=get_credentials())

    # Obter metadados do arquivo
    meta = service.files().get(fileId=args.file_id, fields="id,name,mimeType").execute()
    name = meta["name"]
    mime = meta["mimeType"]

    out_path = args.output or name

    # Google Docs/Sheets/Slides precisam de export; PDFs e outros são download direto
    export_map = {
        "application/vnd.google-apps.document": "application/pdf",
        "application/vnd.google-apps.spreadsheet": "application/pdf",
        "application/vnd.google-apps.presentation": "application/pdf",
    }

    if mime in export_map:
        request = service.files().export_media(fileId=args.file_id, mimeType=export_map[mime])
        if not out_path.endswith(".pdf"):
            out_path += ".pdf"
    else:
        request = service.files().get_media(fileId=args.file_id)

    import os
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)

    with open(out_path, "wb") as f:
        downloader = MediaIoBaseDownload(f, request)
        done = False
        while not done:
            _, done = downloader.next_chunk()

    print(f"Downloaded: {out_path}  ({mime})")
    return out_path


def drive_read_pdf(args):
    """Baixa um PDF do Drive e extrai o texto com pdfplumber. Imprime como JSON."""
    import io
    import json
    import os
    import tempfile
    from googleapiclient.http import MediaIoBaseDownload

    try:
        import pdfplumber
    except ImportError:
        print("ERRO: pdfplumber nao instalado. Execute: pip install pdfplumber", file=__import__("sys").stderr)
        __import__("sys").exit(1)

    service = build("drive", "v3", credentials=get_credentials())
    meta = service.files().get(fileId=args.file_id, fields="id,name,mimeType").execute()
    mime = meta["mimeType"]

    export_map = {
        "application/vnd.google-apps.document": "application/pdf",
        "application/vnd.google-apps.spreadsheet": "application/pdf",
        "application/vnd.google-apps.presentation": "application/pdf",
    }

    if mime in export_map:
        request = service.files().export_media(fileId=args.file_id, mimeType=export_map[mime])
    else:
        request = service.files().get_media(fileId=args.file_id)

    # Baixar para arquivo temporário
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp_path = tmp.name
        downloader = MediaIoBaseDownload(tmp, request)
        done = False
        while not done:
            _, done = downloader.next_chunk()

    # Extrair texto
    pages_text = []
    try:
        with pdfplumber.open(tmp_path) as pdf:
            total = len(pdf.pages)
            for i, page in enumerate(pdf.pages):
                text = page.extract_text() or ""
                pages_text.append({"page": i + 1, "text": text})
    finally:
        os.unlink(tmp_path)

    result = {
        "file_id": args.file_id,
        "name": meta["name"],
        "total_pages": total,
        "pages": pages_text,
        "full_text": "\n\n".join(p["text"] for p in pages_text if p["text"]),
    }

    if args.output:
        import pathlib
        pathlib.Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"Saved: {args.output}  ({total} pages)", file=__import__("sys").stderr)
    else:
        # Imprimir só o texto completo para uso direto
        print(result["full_text"])


def main():
    parser = argparse.ArgumentParser(description="GWS CLI")
    sub = parser.add_subparsers(dest="service")

    # Gmail
    gmail = sub.add_parser("gmail")
    gmail_sub = gmail.add_subparsers(dest="action")
    gl = gmail_sub.add_parser("list")
    gl.add_argument("--query", "-q", default="")
    gl.add_argument("--limit", "-n", type=int, default=5)
    gr = gmail_sub.add_parser("read")
    gr.add_argument("message_id")

    # Calendar
    cal = sub.add_parser("calendar")
    cal_sub = cal.add_subparsers(dest="action")
    cl = cal_sub.add_parser("list")
    cl.add_argument("--days", "-d", type=int, default=7)
    cl.add_argument("--limit", "-n", type=int, default=10)
    cc = cal_sub.add_parser("create")
    cc.add_argument("--summary", required=True)
    cc.add_argument("--start", required=True)
    cc.add_argument("--end", required=True)
    cc.add_argument("--description", default="")

    # Drive
    drv = sub.add_parser("drive")
    drv_sub = drv.add_subparsers(dest="action")
    ds = drv_sub.add_parser("search")
    ds.add_argument("--query", "-q", required=True)
    ds.add_argument("--limit", "-n", type=int, default=10)

    dd = drv_sub.add_parser("download")
    dd.add_argument("--file-id", required=True, help="ID do arquivo no Drive")
    dd.add_argument("--output", "-o", default=None, help="Caminho de saída")

    drp = drv_sub.add_parser("read-pdf")
    drp.add_argument("--file-id", required=True, help="ID do arquivo PDF no Drive")
    drp.add_argument("--output", "-o", default=None, help="Salvar JSON no caminho (opcional; senão imprime texto)")

    args = parser.parse_args()
    if not args.service:
        parser.print_help()
        return

    dispatch = {
        ("gmail", "list"): gmail_list,
        ("gmail", "read"): gmail_read,
        ("calendar", "list"): calendar_list,
        ("calendar", "create"): calendar_create,
        ("drive", "search"): drive_search,
        ("drive", "download"): drive_download,
        ("drive", "read-pdf"): drive_read_pdf,
    }
    fn = dispatch.get((args.service, args.action))
    if fn:
        fn(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
