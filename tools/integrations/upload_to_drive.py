"""
upload_to_drive.py — Upload de pasta local para Google Drive via API.

Retorna link publico imediatamente (sem depender de sync desktop).

Usage:
  python tools/integrations/upload_to_drive.py --source output/marketing/carrosseis/noticias/semana-2026-04-06/ --dest "Carrosseis/Noticias/semana-2026-04-06"
  python tools/integrations/upload_to_drive.py --source output/marketing/artigos/ --dest "Artigos" --pattern "*.html"

PRE-REQUISITO:
  1. credentials.json em tools/gws/ (OAuth 2.0 Desktop app)
  2. Na primeira execucao, o browser abre para autorizar → token.json salvo
"""
import argparse
import json
import os
import sys
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

SCOPES = ["https://www.googleapis.com/auth/drive"]

# Pasta raiz no Drive: output/marketing (AUTOMAÇÕES/output/marketing)
CONTEUDO_FOLDER_ID = "1VtQ28qDWYdp1c3obv53e_JV3eizMyzgG"

# Auth paths — compartilha credentials.json com tools/gws/
GWS_DIR = Path(__file__).parent.parent / "gws"
TOKEN_PATH = GWS_DIR / "token_drive.json"  # token separado (scope diferente)
CREDS_PATH = GWS_DIR / "credentials.json"

MIME_MAP = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".pdf": "application/pdf",
    ".html": "text/html",
    ".txt": "text/plain",
    ".md": "text/markdown",
    ".json": "application/json",
    ".mp3": "audio/mpeg",
    ".mp4": "video/mp4",
}


def get_drive_service():
    creds = None
    if TOKEN_PATH.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not CREDS_PATH.exists():
                print(
                    f"ERRO: credentials.json nao encontrado em {CREDS_PATH}\n"
                    "Baixe em console.cloud.google.com → APIs & Services → Credentials",
                    file=sys.stderr,
                )
                sys.exit(1)
            flow = InstalledAppFlow.from_client_secrets_file(str(CREDS_PATH), SCOPES)
            creds = flow.run_local_server(port=0)
        TOKEN_PATH.write_text(creds.to_json())

    return build("drive", "v3", credentials=creds)


def get_or_create_folder(service, name, parent_id):
    """Retorna ID de pasta existente ou cria nova."""
    q = (
        f"name='{name}' and mimeType='application/vnd.google-apps.folder' "
        f"and '{parent_id}' in parents and trashed=false"
    )
    res = service.files().list(q=q, fields="files(id,name)").execute()
    files = res.get("files", [])
    if files:
        return files[0]["id"]

    meta = {
        "name": name,
        "mimeType": "application/vnd.google-apps.folder",
        "parents": [parent_id],
    }
    folder = service.files().create(body=meta, fields="id").execute()
    return folder["id"]


def upload_file(service, local_path: Path, parent_id: str):
    """Faz upload de arquivo e retorna ID. Pula se ja existe."""
    mime = MIME_MAP.get(local_path.suffix.lower(), "application/octet-stream")
    q = f"name='{local_path.name}' and '{parent_id}' in parents and trashed=false"
    existing = service.files().list(q=q, fields="files(id)").execute().get("files", [])
    if existing:
        print(f"    (ja existe) {local_path.name}")
        return existing[0]["id"]

    media = MediaFileUpload(str(local_path), mimetype=mime, resumable=True)
    meta = {"name": local_path.name, "parents": [parent_id]}
    f = service.files().create(body=meta, media_body=media, fields="id").execute()
    print(f"    + {local_path.name}")
    return f["id"]


def make_shareable(service, folder_id):
    """Torna a pasta publica para leitura e retorna o link."""
    try:
        service.permissions().create(
            fileId=folder_id,
            body={"type": "anyone", "role": "reader"},
        ).execute()
    except Exception:
        pass  # Permissao ja existe
    meta = service.files().get(fileId=folder_id, fields="webViewLink").execute()
    return meta["webViewLink"]


def upload_folder(service, source: Path, dest: str, pattern: str = "*"):
    """Upload de pasta local para caminho no Drive.

    Args:
        source: pasta local com arquivos
        dest: caminho relativo dentro de Marketing/Conteudo (ex: "Carrosseis/Noticias/semana-2026-04-06")
        pattern: glob pattern para filtrar arquivos (ex: "*.jpg")

    Returns:
        dict com folder_id e link
    """
    if not source.exists():
        print(f"ERRO: pasta nao encontrada: {source}", file=sys.stderr)
        sys.exit(1)

    # Criar subpastas no Drive
    parent_id = CONTEUDO_FOLDER_ID
    for part in dest.split("/"):
        part = part.strip()
        if part:
            parent_id = get_or_create_folder(service, part, parent_id)

    drive_folder_id = parent_id
    print(f"\nUpload: {source} → Marketing/Conteudo/{dest}")

    # Upload de arquivos
    uploaded = 0
    files = sorted(source.glob(pattern))
    # Tambem incluir subpastas (ex: fotos/)
    for item in sorted(source.iterdir()):
        if item.is_file() and item.suffix.lower() in MIME_MAP:
            if pattern == "*" or item.match(pattern):
                upload_file(service, item, drive_folder_id)
                uploaded += 1
        elif item.is_dir():
            # Criar subpasta e upload recursivo
            sub_id = get_or_create_folder(service, item.name, drive_folder_id)
            for sub_file in sorted(item.iterdir()):
                if sub_file.is_file() and sub_file.suffix.lower() in MIME_MAP:
                    upload_file(service, sub_file, sub_id)
                    uploaded += 1

    link = make_shareable(service, drive_folder_id)
    print(f"    {uploaded} arquivos enviados")
    print(f"    Link: {link}")

    return {"folder_id": drive_folder_id, "link": link, "files_uploaded": uploaded}


def main():
    parser = argparse.ArgumentParser(description="Upload pasta local para Google Drive")
    parser.add_argument("--source", required=True, help="Pasta local com arquivos")
    parser.add_argument(
        "--dest",
        required=True,
        help="Caminho relativo dentro de Marketing/Conteudo/ no Drive",
    )
    parser.add_argument("--pattern", default="*", help="Glob pattern para filtrar (default: *)")
    parser.add_argument("--json", action="store_true", help="Output em JSON (para scripts)")
    args = parser.parse_args()

    service = get_drive_service()
    result = upload_folder(service, Path(args.source), args.dest, args.pattern)

    if args.json:
        print(json.dumps(result, ensure_ascii=False))
    else:
        # Salvar resultado em .tmp
        out = Path("G:/O meu disco/AUTOMAÇÕES/.tmp/drive_upload_result.json")
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"\nResultado salvo em: {out}")


if __name__ == "__main__":
    main()
