#!/usr/bin/env python3
"""
link_briefings_pecas_133.py
Popula coluna L "Link Briefing" na aba "Pecas do Evento"
com os links dos 39 briefing Google Docs criados.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "gws"))
from gws_auth import get_credentials
from googleapiclient.discovery import build

SS_ID     = "1fccNKRv-OVwlk9Y4OyUNI3TzXN32GRqCC-qj-cgQ8c0"
TAB       = "Pecas do Evento"
FOLDER_ID = "1n6nvn0CWSzcidtjKlGGqMHIyccvCF09G"


def extract_peca_nome(doc_title: str) -> str:
    """Extrai o nome da peca a partir do titulo do doc 'BRIEFING — Nome'."""
    # O em-dash pode aparecer como — ou como seu codepoint u2014
    for sep in [" — ", " -- ", " - "]:
        if sep in doc_title:
            return doc_title.split(sep, 1)[-1].strip()
    # fallback: remover prefixo BRIEFING
    return doc_title.replace("BRIEFING ", "").strip()


def main():
    creds = get_credentials()
    sheets_svc = build("sheets", "v4", credentials=creds)
    drive_svc  = build("drive", "v3", credentials=creds)

    # 1. Buscar todos os docs na pasta de briefings
    q = f"'{FOLDER_ID}' in parents and mimeType='application/vnd.google-apps.document'"
    results = drive_svc.files().list(
        q=q, fields="files(id,name)", pageSize=50
    ).execute()
    docs = results.get("files", [])
    print(f"{len(docs)} docs encontrados na pasta.")

    # 2. Ler nomes da coluna A da aba
    result = sheets_svc.spreadsheets().values().get(
        spreadsheetId=SS_ID,
        range=f"'{TAB}'!A:A"
    ).execute()
    sheet_rows = result.get("values", [])
    sheet_names = [r[0].strip() if r else "" for r in sheet_rows]

    # 3. Escrever cabecalho L1
    sheets_svc.spreadsheets().values().update(
        spreadsheetId=SS_ID,
        range=f"'{TAB}'!L1",
        valueInputOption="USER_ENTERED",
        body={"values": [["Link Briefing"]]}
    ).execute()
    print("Cabecalho L1 escrito.")

    # 4. Mapear doc → linha da planilha
    value_data = []
    not_matched = []

    for doc in docs:
        peca_nome = extract_peca_nome(doc["name"])
        url = f"https://docs.google.com/document/d/{doc['id']}/edit"

        matched = False
        for i, sheet_nome in enumerate(sheet_names):
            if sheet_nome == peca_nome:
                value_data.append({
                    "range": f"'{TAB}'!L{i + 1}",
                    "values": [[url]]
                })
                matched = True
                break

        if not matched:
            not_matched.append(peca_nome)

    print(f"\nMapeados: {len(value_data)}/{len(docs)}")
    if not_matched:
        print("NAO mapeados:")
        for n in not_matched:
            print(f"  - {repr(n)}")

    # 5. Escrever links
    if value_data:
        sheets_svc.spreadsheets().values().batchUpdate(
            spreadsheetId=SS_ID,
            body={"valueInputOption": "USER_ENTERED", "data": value_data}
        ).execute()
        print(f"{len(value_data)} links escritos na coluna L.")

    print(f"\nURL Planilha: https://docs.google.com/spreadsheets/d/{SS_ID}/edit")


if __name__ == "__main__":
    main()
