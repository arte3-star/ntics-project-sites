#!/usr/bin/env python3
"""
format_plano_comunicacao_133.py
Aplica formatação na planilha já criada (1THxXD1Eus85T0T7j95QKzdHPFcXWTdTmwhhaWlAgIZo).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "gws"))
from gws_auth import get_credentials
from googleapiclient.discovery import build

SS_ID = "1THxXD1Eus85T0T7j95QKzdHPFcXWTdTmwhhaWlAgIZo"
SHEET_ETAPAS = 0
SHEET_FLUXO  = 1

def rgb(hex_color):
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return {"red": r/255, "green": g/255, "blue": b/255}

AZUL    = rgb("005F73")
VERDE   = rgb("128C7E")
ROSA    = rgb("D41A6A")
LARANJA = rgb("E86428")
ROXO    = rgb("6B2D7B")
GRAFITE = rgb("2D2D2D")
CINZA   = rgb("F4F4F4")
BRANCO  = rgb("FFFFFF")
PRE_COR = rgb("E8F5E9")
DUR_COR = rgb("FFF3E0")
POS_COR = rgb("E3F2FD")

CANAL_CORES = {"email": AZUL, "whatsapp": VERDE, "social": ROSA, "imprensa": LARANJA, "kit": ROXO}

# Mapa exato de linhas (1-based no sheet = 0-based no API)
# Linha 1 = header (row 0), depois seções e itens
# Precisa corresponder ao que build_etapas_data() produz
SECOES_META = [
    {"canal": "email",    "n_items": 14},
    {"canal": "whatsapp", "n_items": 8},
    {"canal": "social",   "n_items": 15},
    {"canal": "imprensa", "n_items": 13},
    {"canal": "kit",      "n_items": 4},
]

FASE_SEQUENCE = [
    # email (14)
    "Pré","Pré","Pré","Pré","Pré","Durante","Pós",
    "Pré","Pré","Pré","Pré","Durante","Pós","Pós",
    # whatsapp (8)
    "Pré","Pré","Durante","Pós","Pré","Pré","Durante","Pós",
    # social (15)
    "Pré","Pré","Pré","Pré","Durante","Durante","Pós","Pós","Pré","Pré","Durante","Durante","Pós","Pós","Pós",
    # imprensa (13)
    "Pré","Pré","Pré","Pré","Durante","Pós","Pré","Pré","Pré","Pré","Durante","Pós","Pós",
    # kit (4)
    "Pré","Pré","Pré","Pré",
]

FASE_COR = {"Pré": PRE_COR, "Durante": DUR_COR, "Pós": POS_COR}

def build_row_map():
    """Reconstrói mapa row_idx → (tipo, canal/fase)."""
    row = 1  # row 0 = header
    section_rows = {}
    item_rows = {}
    fase_idx = 0
    for sec in SECOES_META:
        section_rows[row] = sec["canal"]
        row += 1
        for _ in range(sec["n_items"]):
            item_rows[row] = FASE_SEQUENCE[fase_idx]
            fase_idx += 1
            row += 1
    return section_rows, item_rows

def rc(sheet_id, r0, r1, c0, c1, fmt, fields):
    return {"repeatCell": {"range": {"sheetId": sheet_id, "startRowIndex": r0, "endRowIndex": r1,
        "startColumnIndex": c0, "endColumnIndex": c1}, "cell": {"userEnteredFormat": fmt}, "fields": fields}}

def cf(bg=None, bold=False, fg=None, size=None, wrap=None, halign=None, valign=None):
    fmt = {}
    if bg: fmt["backgroundColor"] = bg
    txt = {}
    if bold: txt["bold"] = True
    if size: txt["fontSize"] = size
    if fg:   txt["foregroundColor"] = fg
    if txt:  fmt["textFormat"] = txt
    if wrap: fmt["wrapStrategy"] = wrap
    if halign: fmt["horizontalAlignment"] = halign
    if valign: fmt["verticalAlignment"] = valign
    return fmt

def col_w(sid, ci, px):
    return {"updateDimensionProperties": {"range": {"sheetId": sid, "dimension": "COLUMNS",
        "startIndex": ci, "endIndex": ci+1}, "properties": {"pixelSize": px}, "fields": "pixelSize"}}

def row_h(sid, ri, px):
    return {"updateDimensionProperties": {"range": {"sheetId": sid, "dimension": "ROWS",
        "startIndex": ri, "endIndex": ri+1}, "properties": {"pixelSize": px}, "fields": "pixelSize"}}

def freeze(sid, rows=1, cols=0):
    return {"updateSheetProperties": {"properties": {"sheetId": sid,
        "gridProperties": {"frozenRowCount": rows, "frozenColumnCount": cols}},
        "fields": "gridProperties.frozenRowCount,gridProperties.frozenColumnCount"}}

def checkbox(sid, r0, r1, c0, c1):
    return {"setDataValidation": {"range": {"sheetId": sid, "startRowIndex": r0, "endRowIndex": r1,
        "startColumnIndex": c0, "endColumnIndex": c1},
        "rule": {"condition": {"type": "BOOLEAN"}, "showCustomUi": True}}}

def dropdown(sid, r0, r1, c0, c1, vals):
    return {"setDataValidation": {"range": {"sheetId": sid, "startRowIndex": r0, "endRowIndex": r1,
        "startColumnIndex": c0, "endColumnIndex": c1},
        "rule": {"condition": {"type": "ONE_OF_LIST",
            "values": [{"userEnteredValue": v} for v in vals]}, "showCustomUi": True, "strict": True}}}

N_COLS = 18
FIELDS_FULL = "userEnteredFormat(backgroundColor,textFormat,wrapStrategy,horizontalAlignment,verticalAlignment)"
FIELDS_BG   = "userEnteredFormat(backgroundColor,verticalAlignment)"
FIELDS_WRAP = "userEnteredFormat(wrapStrategy)"

def main():
    creds = get_credentials()
    svc = build("sheets", "v4", credentials=creds)

    section_rows, item_rows = build_row_map()
    reqs = []

    # Cabeçalho Etapas
    reqs.append(rc(SHEET_ETAPAS, 0, 1, 0, N_COLS,
        cf(bg=GRAFITE, fg=BRANCO, bold=True, size=10, wrap="WRAP", halign="CENTER", valign="MIDDLE"),
        FIELDS_FULL))
    reqs.append(freeze(SHEET_ETAPAS, rows=1, cols=1))

    # Linhas de seção
    for ri, canal in section_rows.items():
        cor = CANAL_CORES[canal]
        reqs.append(rc(SHEET_ETAPAS, ri, ri+1, 0, N_COLS,
            cf(bg=cor, fg=BRANCO, bold=True, size=11, halign="LEFT", valign="MIDDLE"),
            FIELDS_FULL))
        reqs.append(row_h(SHEET_ETAPAS, ri, 36))

    # Linhas de item
    for ri, fase in item_rows.items():
        cor = FASE_COR.get(fase, BRANCO)
        reqs.append(rc(SHEET_ETAPAS, ri, ri+1, 0, N_COLS,
            cf(bg=cor, valign="MIDDLE"), FIELDS_BG))

    # Larguras colunas Etapas
    for ci, w in enumerate([40,280,70,65,80,70,70,70,70,70,70,200,200,110,130,160,160,160]):
        reqs.append(col_w(SHEET_ETAPAS, ci, w))

    # Checkboxes F..K (idx 5..10)
    all_item = list(item_rows.keys())
    min_r, max_r = min(all_item), max(all_item)+1
    reqs.append(checkbox(SHEET_ETAPAS, min_r, max_r, 5, 11))

    # Dropdowns
    reqs.append(dropdown(SHEET_ETAPAS, min_r, max_r, 2, 3, ["Pré", "Durante", "Pós"]))
    reqs.append(dropdown(SHEET_ETAPAS, min_r, max_r, 3, 4, ["Manaus", "RJ", "Ambas"]))

    # Wrap col B (nome) e L, M
    total_rows = max(all_item) + 2
    for ci in [1, 11, 12]:
        reqs.append(rc(SHEET_ETAPAS, 1, total_rows, ci, ci+1, cf(wrap="WRAP"), FIELDS_WRAP))

    # ── Aba Fluxo
    reqs.append(rc(SHEET_FLUXO, 0, 1, 0, 5,
        cf(bg=AZUL, fg=BRANCO, bold=True, size=11, wrap="WRAP", halign="CENTER", valign="MIDDLE"),
        FIELDS_FULL))
    reqs.append(freeze(SHEET_FLUXO, rows=1))
    fluxo_cores = [PRE_COR, CINZA, DUR_COR, rgb("FFF9E6"), POS_COR]
    for ri, cor in enumerate(fluxo_cores):
        reqs.append(rc(SHEET_FLUXO, ri+1, ri+2, 0, 5,
            cf(bg=cor, wrap="WRAP", valign="MIDDLE"), FIELDS_BG))
        reqs.append(row_h(SHEET_FLUXO, ri+1, 60))
    reqs.append(col_w(SHEET_FLUXO, 0, 110))
    for ci in range(1, 5):
        reqs.append(col_w(SHEET_FLUXO, ci, 210))

    svc.spreadsheets().batchUpdate(
        spreadsheetId=SS_ID,
        body={"requests": reqs}
    ).execute()

    print(f"\nFormatacao aplicada com sucesso!")
    print(f"URL: https://docs.google.com/spreadsheets/d/{SS_ID}/edit")

if __name__ == "__main__":
    main()
