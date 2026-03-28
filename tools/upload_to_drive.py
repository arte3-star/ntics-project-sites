"""
upload_to_drive.py
Faz upload dos carrosseis e roteiros gerados para o Google Drive.

Estrutura criada em Marketing/Conteudo/:
  carrosseis/
    noticias-S03/  noticias-S04/  noticias-S05/
    educativo-S03/ educativo-S04/ educativo-S05/
  videos/
    semana-03/  semana-04/  semana-05/

Saída: links compartilháveis impressos no terminal.

PRÉ-REQUISITO:
  1. Baixar credentials.json em console.cloud.google.com
     → APIs & Services → Credentials → OAuth 2.0 Client IDs
     → Desktop app → Download JSON → renomear para credentials.json
  2. Colocar credentials.json na raiz do projeto (mesmo dir que este script)
  3. Na primeira execução, o browser abre para autorizar → token.json é salvo
"""
import os
import sys
import json
from pathlib import Path

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ["https://www.googleapis.com/auth/drive"]

# Pasta pai no Drive: Marketing/Conteudo (ID fixo)
CONTEUDO_FOLDER_ID = "1V5EbAyF9K8Au5tU0CR4H3t8zpiFmmAa5"

BASE = Path(__file__).parent.parent / ".tmp" / "marketing"

UPLOADS = {
    "carrosseis/noticias-S03": BASE / "carrosseis" / "noticias-S03",
    "carrosseis/noticias-S04": BASE / "carrosseis" / "noticias-S04",
    "carrosseis/noticias-S05": BASE / "carrosseis" / "noticias-S05",
    "carrosseis/educativo-S03": BASE / "carrosseis" / "educativo-S03",
    "carrosseis/educativo-S04": BASE / "carrosseis" / "educativo-S04",
    "carrosseis/educativo-S05": BASE / "carrosseis" / "educativo-S05",
    "videos/semana-03": BASE / "videos" / "semana-03",
    "videos/semana-04": BASE / "videos" / "semana-04",
    "videos/semana-05": BASE / "videos" / "semana-05",
}

# ClickUp task IDs para atualizar depois
CLICKUP_MAP = {
    "carrosseis/noticias-S03": "868hrghtq",
    "carrosseis/noticias-S04": "868hrghtr",
    "carrosseis/noticias-S05": "868j1upxc",
    "carrosseis/educativo-S03": "868hrghrg",
    "carrosseis/educativo-S04": "868hrghrq",
    "carrosseis/educativo-S05": "868hrght1",
    "videos/semana-03": "868hrghrj",
    "videos/semana-04": "868hrghru",
    "videos/semana-05": "868hrght2",
}


def get_drive_service():
    creds = None
    token_path = Path(__file__).parent.parent / "token.json"
    creds_path = Path(__file__).parent.parent / "credentials.json"

    if not creds_path.exists():
        print("ERRO: credentials.json não encontrado.")
        print("Veja as instruções no topo deste arquivo.")
        sys.exit(1)

    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(str(creds_path), SCOPES)
            creds = flow.run_local_server(port=0)
        token_path.write_text(creds.to_json())
        print(f"Token salvo em {token_path}")

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
    """Faz upload de arquivo e retorna ID."""
    mime = "image/jpeg" if local_path.suffix == ".jpg" else "text/plain"
    q = f"name='{local_path.name}' and '{parent_id}' in parents and trashed=false"
    existing = service.files().list(q=q, fields="files(id)").execute().get("files", [])
    if existing:
        print(f"    (já existe) {local_path.name}")
        return existing[0]["id"]

    media = MediaFileUpload(str(local_path), mimetype=mime, resumable=True)
    meta = {"name": local_path.name, "parents": [parent_id]}
    f = service.files().create(body=meta, media_body=media, fields="id").execute()
    print(f"    ✓ {local_path.name}")
    return f["id"]


def make_shareable(service, folder_id):
    """Torna a pasta pública para leitura e retorna o link."""
    service.permissions().create(
        fileId=folder_id,
        body={"type": "anyone", "role": "reader"},
    ).execute()
    meta = service.files().get(fileId=folder_id, fields="webViewLink").execute()
    return meta["webViewLink"]


def main():
    service = get_drive_service()

    # Criar pastas pai
    carrosseis_id = get_or_create_folder(service, "carrosseis", CONTEUDO_FOLDER_ID)
    videos_id = get_or_create_folder(service, "videos", CONTEUDO_FOLDER_ID)
    print(f"Pasta carrosseis: {carrosseis_id}")
    print(f"Pasta videos: {videos_id}")

    results = {}

    for folder_key, local_dir in UPLOADS.items():
        if not local_dir.exists():
            print(f"\n⚠ Pasta local não encontrada: {local_dir}")
            continue

        parts = folder_key.split("/")
        area = parts[0]
        name = parts[1]

        parent_id = carrosseis_id if area == "carrosseis" else videos_id

        print(f"\n>> {folder_key}")
        drive_folder_id = get_or_create_folder(service, name, parent_id)

        files = sorted(local_dir.iterdir())
        for f in files:
            if f.is_file() and f.suffix in (".jpg", ".txt", ".md", ".mp3"):
                upload_file(service, f, drive_folder_id)

        link = make_shareable(service, drive_folder_id)
        results[folder_key] = {"drive_id": drive_folder_id, "link": link}
        print(f"   Link: {link}")

    # Salvar resultado
    out = Path(__file__).parent.parent / ".tmp" / "drive_upload_results.json"
    out.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\n\nResultados salvos em: {out}")

    # Imprimir mapa ClickUp
    print("\n\n=== LINKS PARA CLICKUP ===")
    for folder_key, data in results.items():
        task_id = CLICKUP_MAP.get(folder_key, "?")
        print(f"{folder_key} (task {task_id}):\n  {data['link']}\n")


if __name__ == "__main__":
    main()
