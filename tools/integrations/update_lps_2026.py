"""Cria aba 'LPs 2026' e atualiza 'Lista de LPs' com URLs dos 7 novos sites publicados."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "gws"))
from gws_auth import get_credentials
from googleapiclient.discovery import build

SHEET_ID = "1K0J9n19mJzj8WsNvb9WsyMxW6pSNilIPG9Fh0Stttfg"

SITES_2026 = [
    # numero, projeto, patrocinador, cidade, slug, url_publicada
    ("116", "Cultura Robótica",                      "Áster Máquinas", "—",                "cultura-robotica-aster",                  "https://cultura-robotica-2026.lovable.app"),
    ("117", "Teatro e Oficina Robótica 4ª Edição",   "Whirlpool",      "Rio Claro/Joinville", "teatro-oficina-robotica-4ed-whirlpool",   "https://teatro-e-oficina-robotica-2026.lovable.app"),
    ("119", "PEC Eu Faço Parte 2ª Edição",           "Sylvamo",        "Mogi Guaçu/Guataparã", "pec-eu-faco-parte-2ed-sylvamo",           "https://ntics.com.br/pec-eu-faco-parte-2ed-sylvamo/"),
    ("124", "Gastronomia também é Arte",             "Compagás",       "Lapa/PR",           "gastronomia-tambem-e-arte-compagas",      "—"),
    ("125", "Gastronomia também é Arte 2ª Edição",   "GRU Airport",    "Guarulhos/SP",      "gastronomia-tambem-e-arte-2ed-gru",       "https://gastronomia-tambem-e-arte-2ed-2026.lovable.app"),
    ("127G","PIE Empreendedorismo é Arte 2ª Ed (GRU)","GRU Airport",   "Guarulhos/SP",      "pie-empreendedorismo-e-arte-2ed-gru",     "https://pie-empreendedorismo-gru.lovable.app"),
    ("127S","PIE Empreendedorismo é Arte 2ª Ed (Sotreq)","Sotreq",     "Serra/ES",          "pie-empreendedorismo-e-arte-2ed-sotreq",  "https://pie-empreendedorismo-serra.lovable.app"),
]

def main():
    creds = get_credentials()
    svc = build("sheets", "v4", credentials=creds)

    # 1. Criar aba "LPs 2026"
    meta = svc.spreadsheets().get(spreadsheetId=SHEET_ID).execute()
    existing_sheets = {s["properties"]["title"]: s["properties"]["sheetId"] for s in meta["sheets"]}
    if "LPs 2026" not in existing_sheets:
        req = {"requests": [{"addSheet": {"properties": {"title": "LPs 2026"}}}]}
        resp = svc.spreadsheets().batchUpdate(spreadsheetId=SHEET_ID, body=req).execute()
        print(f"✓ Aba 'LPs 2026' criada (sheetId={resp['replies'][0]['addSheet']['properties']['sheetId']})")
    else:
        print(f"  Aba 'LPs 2026' já existe")

    # 2. Header + dados na aba LPs 2026
    rows = [["Número", "Projeto", "Patrocinador", "Cidade(s)", "URL ntics.com.br", "URL Lovable", "Status"]]
    for num, proj, patroc, cidade, slug, lovable in SITES_2026:
        rows.append([num, proj, patroc, cidade, f"https://ntics.com.br/{slug}/", lovable, "✓ Publicado"])
    body = {"values": rows}
    svc.spreadsheets().values().update(
        spreadsheetId=SHEET_ID,
        range="LPs 2026!A1",
        valueInputOption="RAW",
        body=body,
    ).execute()
    print(f"✓ {len(rows)-1} linhas escritas em 'LPs 2026!A1:G{len(rows)}'")

    # 3. Formatação: header bold + freeze + autoresize
    sheet_id = svc.spreadsheets().get(spreadsheetId=SHEET_ID).execute()
    sid = next(s["properties"]["sheetId"] for s in sheet_id["sheets"] if s["properties"]["title"] == "LPs 2026")
    fmt_reqs = [
        {"repeatCell": {
            "range": {"sheetId": sid, "startRowIndex": 0, "endRowIndex": 1},
            "cell": {"userEnteredFormat": {"textFormat": {"bold": True}, "backgroundColor": {"red": 0.85, "green": 0.92, "blue": 1.0}}},
            "fields": "userEnteredFormat(textFormat,backgroundColor)",
        }},
        {"updateSheetProperties": {
            "properties": {"sheetId": sid, "gridProperties": {"frozenRowCount": 1}},
            "fields": "gridProperties.frozenRowCount",
        }},
        {"autoResizeDimensions": {
            "dimensions": {"sheetId": sid, "dimension": "COLUMNS", "startIndex": 0, "endIndex": 7}
        }},
    ]
    svc.spreadsheets().batchUpdate(spreadsheetId=SHEET_ID, body={"requests": fmt_reqs}).execute()
    print("✓ Formatação aplicada (header bold, freeze, autoresize)")

    print(f"\nPlanilha: https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit")

if __name__ == "__main__":
    main()
