#!/usr/bin/env python3
"""
read_google_sheet.py — Lê dados de Google Sheets via API.

Usage:
  # Ler range específico
  python tools/integrations/read_google_sheet.py \
    --spreadsheet-id 1yzzqOgMghtPRd8PIqvEzZ7qROAbhrbuLajRv9xcPJpw \
    --range "Números gerais!A:Q"

  # Ler aba inteira por nome
  python tools/integrations/read_google_sheet.py \
    --spreadsheet-id 1yzzqOgMghtPRd8PIqvEzZ7qROAbhrbuLajRv9xcPJpw \
    --sheet "2024"

  # Buscar linha por texto (ex: encontrar projeto PEC)
  python tools/integrations/read_google_sheet.py \
    --spreadsheet-id 1yzzqOgMghtPRd8PIqvEzZ7qROAbhrbuLajRv9xcPJpw \
    --sheet "2024" \
    --search "PEC"

Requer: OAuth token de tools/gws/ com scope spreadsheets.readonly
"""

import argparse
import json
import re
import sys
from pathlib import Path

# Add parent dirs for gws_auth import
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "gws"))

from gws_auth import get_credentials
from googleapiclient.discovery import build


def get_sheets_service():
    """Cria serviço Google Sheets autenticado."""
    creds = get_credentials()
    return build("sheets", "v4", credentials=creds)


def read_range(spreadsheet_id: str, range_name: str) -> list:
    """Lê um range da planilha. Retorna lista de listas."""
    service = get_sheets_service()
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range=range_name,
    ).execute()
    return result.get("values", [])


def list_sheets(spreadsheet_id: str) -> list:
    """Lista todas as abas da planilha com nome e gid."""
    service = get_sheets_service()
    meta = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
    return [
        {"title": s["properties"]["title"], "gid": s["properties"]["sheetId"]}
        for s in meta.get("sheets", [])
    ]


def search_rows(rows: list, query: str) -> list:
    """Busca linhas que contenham o texto (case-insensitive)."""
    query_lower = query.lower()
    matches = []
    for i, row in enumerate(rows):
        for cell in row:
            if query_lower in str(cell).lower():
                matches.append({"row_index": i, "data": row})
                break
    return matches


def extract_spreadsheet_id(url_or_id: str) -> str:
    """Extrai spreadsheet ID de URL ou retorna o ID direto."""
    match = re.search(r"/d/([a-zA-Z0-9_-]+)", url_or_id)
    if match:
        return match.group(1)
    if re.match(r"^[a-zA-Z0-9_-]{20,}$", url_or_id):
        return url_or_id
    raise ValueError(f"Cannot extract spreadsheet ID from: {url_or_id}")


def main():
    parser = argparse.ArgumentParser(description="Lê dados de Google Sheets")
    parser.add_argument("--spreadsheet-id", required=True, help="ID ou URL da planilha")
    parser.add_argument("--range", default=None, help="Range A1 notation (ex: 'Sheet1!A1:Z100')")
    parser.add_argument("--sheet", default=None, help="Nome da aba (lê inteira)")
    parser.add_argument("--search", default=None, help="Buscar linhas com este texto")
    parser.add_argument("--list-sheets", action="store_true", help="Listar abas disponíveis")
    parser.add_argument("--output", default=None, help="Salvar JSON no arquivo")
    args = parser.parse_args()

    spreadsheet_id = extract_spreadsheet_id(args.spreadsheet_id)

    if args.list_sheets:
        sheets = list_sheets(spreadsheet_id)
        for s in sheets:
            print(f"  {s['title']} (gid={s['gid']})")
        json.dump(sheets, sys.stdout, ensure_ascii=False)
        return

    # Determinar range
    if args.range:
        range_name = args.range
    elif args.sheet:
        range_name = args.sheet
    else:
        print("[ERRO] Forneça --range, --sheet ou --list-sheets", file=sys.stderr)
        sys.exit(1)

    print(f"Lendo: {range_name}...", file=sys.stderr)
    rows = read_range(spreadsheet_id, range_name)
    print(f"  {len(rows)} linhas lidas", file=sys.stderr)

    # Buscar se pedido
    if args.search:
        matches = search_rows(rows, args.search)
        print(f"  {len(matches)} linhas com '{args.search}'", file=sys.stderr)
        result = {"query": args.search, "matches": matches, "header": rows[0] if rows else []}
    else:
        result = {"rows": rows, "count": len(rows)}

    # Output
    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"  Salvo em: {args.output}", file=sys.stderr)
    else:
        json.dump(result, sys.stdout, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
