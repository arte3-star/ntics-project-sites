#!/usr/bin/env python3
"""
update_midiakit_v2_133.py
Atualiza secao MIDIA KIT na planilha v2 do Projeto 133.

Baseado no ClickUp doc 8cje8p1-46031, secao 3 "Media Kit para Imprensa":
  4 itens fisicos que compoe o kit enviado a jornalistas de Manaus.

Posicoes apos update_assessoria_v2_133.py (que deletou 6 linhas de assessoria):
  Row 0:   COMM_HEADER
  Row 1:   ASSESSORIA section header
  Rows 2-7: 6 itens assessoria
  Row 8:   MIDIA KIT section header  ← posicao atual
  Rows 9-18: 10 itens midia kit (a substituir por 4)
  Row 19:  spacer
  Row 20:  MAILING title
  ...
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "gws"))
from gws_auth import get_credentials
from googleapiclient.discovery import build

SS_ID  = "1fccNKRv-OVwlk9Y4OyUNI3TzXN32GRqCC-qj-cgQ8c0"
SID1   = 1150580728
N_COMM = 16

def rgb(h):
    h = h.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return {"red": r/255, "green": g/255, "blue": b/255}

PRE_COR = rgb("E8F5E9")
BRANCO  = rgb("FFFFFF")
FASE_COR = {"Pre": PRE_COR}
FIELDS_BG   = "userEnteredFormat(backgroundColor,verticalAlignment)"
FIELDS_WRAP = "userEnteredFormat(wrapStrategy)"

# ── 4 itens do Media Kit fisico para imprensa (ClickUp doc, secao 3) ──────────
# (nome, fase, descricao, publico)
NEW_MIDIAKIT = [
    (
        "Garrafa de Agua Personalizada",
        "Pre",
        "2L ou 3L, de vidro, com adesivo do Caminhao ODS e ODS 3 (saude e bem-estar). 10 a 12 unidades — comprar volume unico pensando Manaus + Rio de Janeiro para otimizar custo. Abilio orca e aprova quantitativo e custo total.",
        "Jornalistas AM"
    ),
    (
        "Tag de Identificacao ODS 3",
        "Pre",
        "Texto curto linkando a garrafa ao ODS 3 e a missao do projeto Caminhao ODS / Ecoarte. Producao: designer NTICS.",
        "Jornalistas AM"
    ),
    (
        "Release de Imprensa Impresso",
        "Pre",
        "Release (Release 1 ou Release 2) impresso, dobrado e colocado fisicamente dentro da garrafa. Angelo define qual release vai no kit conforme timing de envio.",
        "Jornalistas AM"
    ),
    (
        "Adesivos para Personalizacao da Garrafa",
        "Pre",
        "Adesivos brandados do projeto para o jornalista personalizar a garrafa. Producao: designer NTICS. Parte do conjunto do kit fisico.",
        "Jornalistas AM"
    ),
]

N_NEW = len(NEW_MIDIAKIT)   # 4
N_OLD = 10

MK_ITEM_START = 9
MK_ITEM_NEW_END = MK_ITEM_START + N_NEW   # 13
MK_ITEM_OLD_END = MK_ITEM_START + N_OLD   # 19


def rc(sid, r0, r1, c0, c1, fmt, fields):
    return {"repeatCell": {"range": {"sheetId": sid, "startRowIndex": r0,
        "endRowIndex": r1, "startColumnIndex": c0, "endColumnIndex": c1},
        "cell": {"userEnteredFormat": fmt}, "fields": fields}}

def cf(bg=None, bold=False, fg=None, size=None, wrap=None, halign=None, valign=None):
    fmt = {}
    if bg:   fmt["backgroundColor"] = bg
    txt = {}
    if bold: txt["bold"] = True
    if size: txt["fontSize"] = size
    if fg:   txt["foregroundColor"] = fg
    if txt:  fmt["textFormat"] = txt
    if wrap: fmt["wrapStrategy"] = wrap
    if halign: fmt["horizontalAlignment"] = halign
    if valign: fmt["verticalAlignment"] = valign
    return fmt

def checkbox(sid, r0, r1, c0, c1):
    return {"setDataValidation": {"range": {"sheetId": sid, "startRowIndex": r0,
        "endRowIndex": r1, "startColumnIndex": c0, "endColumnIndex": c1},
        "rule": {"condition": {"type": "BOOLEAN"}, "showCustomUi": True}}}

def dropdown(sid, r0, r1, c0, c1, vals):
    return {"setDataValidation": {"range": {"sheetId": sid, "startRowIndex": r0,
        "endRowIndex": r1, "startColumnIndex": c0, "endColumnIndex": c1},
        "rule": {"condition": {"type": "ONE_OF_LIST",
            "values": [{"userEnteredValue": v} for v in vals]},
            "showCustomUi": True, "strict": False}}}


def main():
    creds = get_credentials()
    svc = build("sheets", "v4", credentials=creds)

    # ── 1. Deletar as 6 linhas extras (10 - 4 = 6) ────────────────────────────
    svc.spreadsheets().batchUpdate(
        spreadsheetId=SS_ID,
        body={"requests": [{"deleteDimension": {"range": {
            "sheetId": SID1, "dimension": "ROWS",
            "startIndex": MK_ITEM_NEW_END,
            "endIndex": MK_ITEM_OLD_END
        }}}]}
    ).execute()
    print(f"Deletadas {N_OLD - N_NEW} linhas do midia kit antigo.")

    # ── 2. Escrever os 4 novos itens (rows 9..12) ──────────────────────────────
    new_rows = []
    for i, (nome, fase, desc, pub) in enumerate(NEW_MIDIAKIT, start=1):
        new_rows.append([str(i), nome, fase, "", "", "", "", "", "", "", desc, pub, "", "", "", ""])

    svc.spreadsheets().values().update(
        spreadsheetId=SS_ID,
        range="'Assessoria + Midia Kit'!A10",
        valueInputOption="USER_ENTERED",
        body={"values": new_rows}
    ).execute()
    print(f"Novos dados escritos: {N_NEW} itens de midia kit.")

    # ── 3. Formatar ────────────────────────────────────────────────────────────
    fmt = []
    for i in range(N_NEW):
        ri = MK_ITEM_START + i
        fmt.append(rc(SID1, ri, ri+1, 0, N_COMM,
            cf(bg=PRE_COR, valign="MIDDLE"), FIELDS_BG))
    fmt.append(checkbox(SID1, MK_ITEM_START, MK_ITEM_NEW_END, 4, 10))
    fmt.append(dropdown(SID1, MK_ITEM_START, MK_ITEM_NEW_END, 2, 3, ["Pre", "Durante", "Pos"]))
    fmt.append(rc(SID1, MK_ITEM_START, MK_ITEM_NEW_END, 1, 2, cf(wrap="WRAP"), FIELDS_WRAP))
    fmt.append(rc(SID1, MK_ITEM_START, MK_ITEM_NEW_END, 10, 11, cf(wrap="WRAP"), FIELDS_WRAP))

    svc.spreadsheets().batchUpdate(
        spreadsheetId=SS_ID, body={"requests": fmt}
    ).execute()
    print("Formatacao aplicada.")
    print(f"\nURL: https://docs.google.com/spreadsheets/d/{SS_ID}/edit")


if __name__ == "__main__":
    main()
