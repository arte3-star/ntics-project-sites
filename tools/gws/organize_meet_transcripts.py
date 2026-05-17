#!/usr/bin/env python3
"""
tools/gws/organize_meet_transcripts.py

Copia transcrições do Google Meet ("Anotações do Gemini") dos Drives de cada
membro da equipe para a pasta centralizada "Atas de Reunião" no Drive de Lucas.

Estrutura de destino:
  Atas de Reunião/                    (ID: 1maClYRTiY1uvEzd16gsjespciMBScSnx)
    Lucas Rotta (lucas.rotta@...)     (ID: 11W2IQeWitYsbeqKO2wL14tZBZK40O45D)
    Ana Carolina Xavier (ana....)     (ID: 1jy7i-ikDa5bh8mVTdixCwre-ivR1yZbZ)
    ...

Modos de execução:
  --mode oauth          Escaneia só o Drive do usuário autenticado (funciona agora)
  --mode service        Escaneia toda a equipe via domain-wide delegation (requer setup)

Uso:
  python organize_meet_transcripts.py --mode oauth --days 7
  python organize_meet_transcripts.py --mode service --days 1
  python organize_meet_transcripts.py --mode service --dry-run
"""
import argparse
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# ── Caminhos ──────────────────────────────────────────────────────────────────
ROOT_DIR = Path(__file__).parent.parent.parent
CACHE_FILE = ROOT_DIR / ".tmp" / "organized_transcripts.json"
SERVICE_ACCOUNT_JSON = Path(__file__).parent / "service_account.json"

# ── Pasta raiz centralizada ────────────────────────────────────────────────────
ROOT_FOLDER_ID = "1maClYRTiY1uvEzd16gsjespciMBScSnx"

# ── Mapeamento equipe: email → folder_id ──────────────────────────────────────
TEAM = {
    "lucas.rotta@ntics.com.br":        "11W2IQeWitYsbeqKO2wL14tZBZK40O45D",
    "ana.xavier@ntics.com.br":         "1jy7i-ikDa5bh8mVTdixCwre-ivR1yZbZ",
    "abilio.martins@ntics.com.br":     "1bRie45RUAX8wHVZGXREBTUBMRcBvUSaS",
    "bruna.seibel@ntics.com.br":       "1puDC7B1N_Oo2MmZ-Xmq4lOcaCAPeZk8g",
    "raiza.araujo@ntics.com.br":       "1zem9ogYFqRwU6qFd1BhEMUQyOAEA8OLM",
    "jessica.lora@ntics.com.br":       "1NgNIkBW_07IBhdm0i93JmnoaSlOeEKW-",
    "mayara.ferreira@ntics.com.br":    "1oQUtgIFaRVkeIoK45kzQwt_4FCC-iA5D",
    "vera.carvalho@ntics.com.br":      "1K8qb8Mtm6aWoOJfq-9zZ71dcVGpGa4dV",
    "cristina.ygiro@ntics.com.br":     "1ukQ7fZ4QgvtgdhfQ3DWSCsRgf8-cJr5r",
    "fernando.clark@ntics.com.br":     "1Yo-WzJ3M19-t4eNeeAVzO7U0xqbolKyW",
    "luizfelipe.deffune@ntics.com.br": "18Mv8lIYAcDeq5o0s71RWsnHFYv9rJngm",
    "ariadne.canaver@ntics.com.br":    "1Bbs2vKXu2Uoa9CITU-mq12noWEzVbPlC",
    "angelo.miguel@ntics.com.br":      "12EU1GZql_TYbNFyPrOOFdkcKvCHWarO0",
    "luisa.moreira@ntics.com.br":      "1SIeKh-TrjOlJ-NPESi6O-KarvP9Jyv9a",
}

TRANSCRIPT_KEYWORDS = [
    "Anotações do Gemini",
    "Anotacoes do Gemini",
    "Meet Transcript",
]


# ── Autenticação ───────────────────────────────────────────────────────────────

def get_oauth_service():
    sys.path.insert(0, str(Path(__file__).parent))
    from gws_auth import get_credentials
    creds = get_credentials()
    return build("drive", "v3", credentials=creds)


def get_service_account_service(impersonate_email: str):
    """Autentica como service account impersonando um usuário do domínio."""
    from google.oauth2 import service_account

    if not SERVICE_ACCOUNT_JSON.exists():
        print(
            f"ERRO: {SERVICE_ACCOUNT_JSON} não encontrado.\n"
            "Configure um Service Account com domain-wide delegation.\n"
            "Instruções: https://developers.google.com/admin-sdk/directory/v1/guides/delegation",
            file=sys.stderr,
        )
        sys.exit(1)

    scopes = [
        "https://www.googleapis.com/auth/drive.readonly",
        "https://www.googleapis.com/auth/drive.file",
    ]
    creds = service_account.Credentials.from_service_account_file(
        str(SERVICE_ACCOUNT_JSON), scopes=scopes
    )
    delegated = creds.with_subject(impersonate_email)
    return build("drive", "v3", credentials=delegated)


# ── Cache de arquivos já processados ──────────────────────────────────────────

def load_cache() -> set:
    if CACHE_FILE.exists():
        return set(json.loads(CACHE_FILE.read_text(encoding="utf-8")))
    return set()


def save_cache(processed: set):
    CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
    CACHE_FILE.write_text(json.dumps(sorted(processed), indent=2), encoding="utf-8")


# ── Busca de transcrições ──────────────────────────────────────────────────────

def find_transcripts(service, since_iso: str) -> list[dict]:
    """Busca arquivos de transcrição no Drive do usuário autenticado."""
    keyword_clauses = " or ".join(
        f"name contains '{kw}'" for kw in TRANSCRIPT_KEYWORDS
    )
    query = f"({keyword_clauses}) and modifiedTime > '{since_iso}' and trashed = false"

    results = []
    page_token = None
    while True:
        resp = service.files().list(
            q=query,
            fields="nextPageToken, files(id, name, owners, createdTime, modifiedTime, webViewLink)",
            pageToken=page_token,
            pageSize=50,
        ).execute()
        results.extend(resp.get("files", []))
        page_token = resp.get("nextPageToken")
        if not page_token:
            break
    return results


# ── Cópia para pasta centralizada ─────────────────────────────────────────────

def copy_to_central(src_service, file_id: str, file_name: str, dest_folder_id: str, dry_run: bool) -> bool:
    """Copia o arquivo para a subpasta correspondente. Retorna True se copiou."""
    if dry_run:
        print(f"    [DRY-RUN] Copiaria: {file_name} → folder {dest_folder_id}")
        return True
    try:
        src_service.files().copy(
            fileId=file_id,
            body={"name": file_name, "parents": [dest_folder_id]},
        ).execute()
        return True
    except HttpError as e:
        print(f"    ERRO ao copiar {file_name}: {e}", file=sys.stderr)
        return False


# ── Lógica principal por usuário ──────────────────────────────────────────────

def process_user(email: str, folder_id: str, mode: str, since_iso: str, processed: set, dry_run: bool) -> int:
    print(f"\n→ {email}")
    try:
        service = get_oauth_service() if mode == "oauth" else get_service_account_service(email)
        transcripts = find_transcripts(service, since_iso)
    except Exception as e:
        print(f"  Erro ao acessar Drive: {e}", file=sys.stderr)
        return 0

    new_count = 0
    for f in transcripts:
        file_id = f["id"]
        if file_id in processed:
            print(f"  - {f['name']} [já processado, pulando]")
            continue

        print(f"  + {f['name']} ({f.get('createdTime','')[:10]})")
        ok = copy_to_central(service, file_id, f["name"], folder_id, dry_run)
        if ok:
            processed.add(file_id)
            new_count += 1

    if not transcripts:
        print("  (nenhuma transcrição encontrada)")
    return new_count


# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Organiza transcrições do Meet por pessoa no Drive")
    parser.add_argument("--mode", choices=["oauth", "service"], default="oauth",
                        help="oauth=só seu Drive | service=toda equipe (requer service account)")
    parser.add_argument("--days", type=int, default=1,
                        help="Quantos dias atrás varrer (padrão: 1)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Mostra o que faria sem copiar nada")
    args = parser.parse_args()

    since = (datetime.now(timezone.utc) - timedelta(days=args.days)).isoformat()
    processed = load_cache()

    print(f"Modo: {args.mode} | Janela: últimos {args.days} dia(s) | Dry-run: {args.dry_run}")
    print(f"Pasta raiz: https://drive.google.com/drive/folders/{ROOT_FOLDER_ID}")
    print(f"Cache: {len(processed)} arquivo(s) já processados")

    total = 0
    if args.mode == "oauth":
        # Só processa o usuário autenticado (Lucas)
        email = "lucas.rotta@ntics.com.br"
        folder_id = TEAM[email]
        total += process_user(email, folder_id, "oauth", since, processed, args.dry_run)
    else:
        # Processa toda a equipe via service account
        for email, folder_id in TEAM.items():
            total += process_user(email, folder_id, "service", since, processed, args.dry_run)

    if not args.dry_run:
        save_cache(processed)

    print(f"\nConcluído. {total} transcrição(ões) nova(s) copiada(s).")


if __name__ == "__main__":
    main()
