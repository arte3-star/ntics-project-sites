#!/usr/bin/env python3
"""
add_assessoria_tab_133.py
Cria aba "Plano de Assessoria — Manaus" no Sheet do Projeto 133.
Pre-popula com veiculos de midia de Manaus que tiveram contato no projeto 2019.

Estrutura:
  Linha 1: header (colunas: CIDADE | VEICULO | DATA ENVIO | EMAIL | TELEFONE | TIPO | STATUS | DATA PUBLICACAO | LINK / NOTAS)
  Linha 2: section header MANAUS — AM
  Linhas 3+: veiculos de Manaus (22 contatos do projeto 2019)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "gws"))
from gws_auth import get_credentials
from googleapiclient.discovery import build

SS_ID = "1THxXD1Eus85T0T7j95QKzdHPFcXWTdTmwhhaWlAgIZo"
N_COLS_ASSOC = 9

def rgb(hex_color):
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return {"red": r/255, "green": g/255, "blue": b/255}

GRAFITE  = rgb("2D2D2D")
LARANJA  = rgb("E86428")
AZUL     = rgb("005F73")
BRANCO   = rgb("FFFFFF")
CINZA    = rgb("F4F4F4")
AMARELO  = rgb("FFF9C4")

# ─── Veiculos de Manaus (do projeto 2019 Conhecendo os ODS) ───────────────────
# (veiculo, email, telefone, tipo, status_inicial, notas)
MANAUS_MEDIA = [
    ("G1 Amazonas / TV Amazonas", "", "", "Site / TV", "A enviar", "Publicou 3x em 2019 — maior alcance AM"),
    ("A Critica", "", "", "Site + Jornal", "A enviar", "Publicou em 2019 — principal jornal de Manaus"),
    ("Amazonas Em Tempo", "", "", "Site", "A enviar", "Publicou em 2019"),
    ("Portal do Holanda", "", "", "Site", "A enviar", "Publicou 2x em 2019 — alto engajamento"),
    ("Portal Amazonia", "", "", "Site", "A enviar", "Publicou 3x em 2019"),
    ("D24Am / Diario do Amazonas", "", "", "Site", "A enviar", "Publicou em 2019"),
    ("Amazonas Noticias", "", "", "Site", "A enviar", "Publicou 2x em 2019"),
    ("CBN Amazonas", "", "", "Radio", "A enviar", "Contato em 2019"),
    ("Conexao Amazonas", "", "", "Site", "A enviar", "Publicou em 2019"),
    ("Amazonas Atual", "", "", "Site", "A enviar", "Publicou em 2019"),
    ("Blitz Amazonico", "", "", "Site", "A enviar", "Publicou em 2019"),
    ("Fato Amazonico", "", "", "Site", "A enviar", "Publicou 2x em 2019"),
    ("Diversidade Amazonica", "", "", "Site", "A enviar", "Publicou em 2019"),
    ("Manaus Online", "", "", "Site", "A enviar", "Publicou em 2019 (via Virada Sustentavel)"),
    ("Portal do Generoso", "", "", "Site", "A enviar", "Publicou em 2019"),
    ("Plantao Diario", "", "", "Site", "A enviar", "Publicou em 2019"),
    ("Amazonas News", "", "", "Site", "A enviar", "Publicou em 2019"),
    ("Reporter Parintins", "", "", "Site", "A enviar", "Publicou em 2019"),
    ("Pagina 1 AM", "", "", "Site", "A enviar", "Publicou em 2019"),
    ("UFAM (Atlas ODS Amazonia)", "", "", "Site Institucional", "A enviar", "Parceiro em 2019 — alta credibilidade"),
    ("Prefeitura de Manaus (SEMED)", "", "", "Site + Newsletter", "A enviar", "Participou em 2019 — abertura para parceria"),
    ("Virada Sustentavel Manaus", "", "", "Site + Redes Sociais", "A enviar", "Parceiro organizador em 2019 — reativar relacao"),
]

HEADER_ROW = [
    "CIDADE", "VEICULO", "DATA DE ENVIO", "EMAIL", "TELEFONE",
    "TIPO DE MIDIA", "STATUS", "DATA DE PUBLICACAO", "LINK / NOTAS"
]

# ─── Helpers ──────────────────────────────────────────────────────────────────

def rc(sheet_id, r0, r1, c0, c1, fmt, fields):
    return {"repeatCell": {"range": {"sheetId": sheet_id, "startRowIndex": r0,
        "endRowIndex": r1, "startColumnIndex": c0, "endColumnIndex": c1},
        "cell": {"userEnteredFormat": fmt}, "fields": fields}}

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
        "startIndex": ci, "endIndex": ci+1}, "properties": {"pixelSize": px},
        "fields": "pixelSize"}}

def row_h(sid, ri, px):
    return {"updateDimensionProperties": {"range": {"sheetId": sid, "dimension": "ROWS",
        "startIndex": ri, "endIndex": ri+1}, "properties": {"pixelSize": px},
        "fields": "pixelSize"}}

def freeze(sid, rows=1, cols=0):
    return {"updateSheetProperties": {"properties": {"sheetId": sid,
        "gridProperties": {"frozenRowCount": rows, "frozenColumnCount": cols}},
        "fields": "gridProperties.frozenRowCount,gridProperties.frozenColumnCount"}}

def dropdown(sid, r0, r1, c0, c1, vals):
    return {"setDataValidation": {"range": {"sheetId": sid, "startRowIndex": r0,
        "endRowIndex": r1, "startColumnIndex": c0, "endColumnIndex": c1},
        "rule": {"condition": {"type": "ONE_OF_LIST",
            "values": [{"userEnteredValue": v} for v in vals]},
            "showCustomUi": True, "strict": False}}}

def tab_color(sid, color):
    return {"updateSheetProperties": {"properties": {"sheetId": sid,
        "tabColor": color}, "fields": "tabColor"}}

FIELDS_FULL = "userEnteredFormat(backgroundColor,textFormat,wrapStrategy,horizontalAlignment,verticalAlignment)"
FIELDS_BG   = "userEnteredFormat(backgroundColor,verticalAlignment)"
FIELDS_WRAP = "userEnteredFormat(wrapStrategy)"

STATUS_OPTIONS = ["A enviar", "Enviado", "Em andamento", "Publicado", "Sem retorno", "Nao aplicavel"]
TIPO_OPTIONS   = ["Site", "TV", "Radio", "Jornal", "Revista", "Newsletter", "Portal", "Outro"]

def main():
    creds = get_credentials()
    svc = build("sheets", "v4", credentials=creds)

    # ── 1. Criar nova aba ──────────────────────────────────────────────────────
    resp = svc.spreadsheets().batchUpdate(
        spreadsheetId=SS_ID,
        body={"requests": [{"addSheet": {"properties": {
            "title": "Plano de Assessoria — Manaus",
            "gridProperties": {"rowCount": 60, "columnCount": N_COLS_ASSOC}
        }}}]}
    ).execute()
    new_sid = resp["replies"][0]["addSheet"]["properties"]["sheetId"]
    print(f"Nova aba criada — sheetId: {new_sid}")

    # ── 2. Escrever dados ──────────────────────────────────────────────────────
    rows = []
    # Linha 1: header
    rows.append(HEADER_ROW)
    # Linha 2: section header Manaus
    rows.append(["MANAUS — AM"] + [""] * (N_COLS_ASSOC - 1))
    # Linhas 3+: veiculos
    for v in MANAUS_MEDIA:
        veiculo, email, telefone, tipo, status, notas = v
        rows.append(["AM", veiculo, "", email, telefone, tipo, status, "", notas])

    svc.spreadsheets().values().update(
        spreadsheetId=SS_ID,
        range=f"'Plano de Assessoria — Manaus'!A1",
        valueInputOption="USER_ENTERED",
        body={"values": rows}
    ).execute()
    print(f"Dados escritos: {len(rows)} linhas.")

    # ── 3. Formatacao ──────────────────────────────────────────────────────────
    fmt_reqs = []
    total_rows = len(rows)

    # Header (linha 0)
    fmt_reqs.append(rc(new_sid, 0, 1, 0, N_COLS_ASSOC,
        cf(bg=AZUL, fg=BRANCO, bold=True, size=10, wrap="WRAP",
           halign="CENTER", valign="MIDDLE"), FIELDS_FULL))
    fmt_reqs.append(row_h(new_sid, 0, 36))
    fmt_reqs.append(freeze(new_sid, rows=1, cols=1))

    # Section header Manaus (linha 1)
    fmt_reqs.append(rc(new_sid, 1, 2, 0, N_COLS_ASSOC,
        cf(bg=LARANJA, fg=BRANCO, bold=True, size=11, halign="LEFT", valign="MIDDLE"),
        FIELDS_FULL))
    fmt_reqs.append(row_h(new_sid, 1, 36))

    # Linhas de veiculos: alternando BRANCO / CINZA
    for i in range(len(MANAUS_MEDIA)):
        ri = 2 + i
        bg = CINZA if (i % 2 == 0) else BRANCO
        fmt_reqs.append(rc(new_sid, ri, ri+1, 0, N_COLS_ASSOC,
            cf(bg=bg, valign="MIDDLE"), FIELDS_BG))

    # Linha extra de nota no fim (amarelo claro)
    nota_row = total_rows
    fmt_reqs.append(rc(new_sid, nota_row, nota_row+1, 0, N_COLS_ASSOC,
        cf(bg=AMARELO, valign="MIDDLE"), FIELDS_BG))

    # Larguras das colunas
    widths = [80, 220, 90, 240, 110, 90, 120, 120, 320]
    for ci, w in enumerate(widths):
        fmt_reqs.append(col_w(new_sid, ci, w))

    # Wrap nas colunas VEICULO (1) e LINK/NOTAS (8)
    fmt_reqs.append(rc(new_sid, 0, total_rows+1, 1, 2, cf(wrap="WRAP"), FIELDS_WRAP))
    fmt_reqs.append(rc(new_sid, 0, total_rows+1, 8, 9, cf(wrap="WRAP"), FIELDS_WRAP))

    # Dropdowns STATUS (col 6) e TIPO (col 5) para as linhas de veiculos
    data_rows_start = 2
    data_rows_end   = 2 + len(MANAUS_MEDIA)
    fmt_reqs.append(dropdown(new_sid, data_rows_start, data_rows_end, 6, 7, STATUS_OPTIONS))
    fmt_reqs.append(dropdown(new_sid, data_rows_start, data_rows_end, 5, 6, TIPO_OPTIONS))

    # Cor da tab
    fmt_reqs.append(tab_color(new_sid, rgb("E86428")))

    svc.spreadsheets().batchUpdate(
        spreadsheetId=SS_ID, body={"requests": fmt_reqs}
    ).execute()

    # Linha de rodape com instrucoes
    svc.spreadsheets().values().update(
        spreadsheetId=SS_ID,
        range=f"'Plano de Assessoria — Manaus'!A{total_rows+1}",
        valueInputOption="USER_ENTERED",
        body={"values": [["PROXIMOS PASSOS: Preencher emails e telefones. Adicionar novos veiculos na proxima linha. RJ: ver aba dedicada a criar."]]}
    ).execute()

    print("Formatacao aplicada.")
    print(f"URL: https://docs.google.com/spreadsheets/d/{SS_ID}/edit")

if __name__ == "__main__":
    main()
