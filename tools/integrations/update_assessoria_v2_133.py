#!/usr/bin/env python3
"""
update_assessoria_v2_133.py
Atualiza secao Assessoria de Imprensa na planilha v2 do Projeto 133
com base no Plano de Divulgacao, Imprensa e Media Kit (ClickUp doc 8cje8p1-46031).

Releases definidos no documento:
  Release 1 - Save the Date e Itinerancia Geral (~18/05/2026)
  Release 2 - Especifico Manaus (09/06/2026)
  Release Pos-Evento - Condicional (apenas se houver historia de desdobramento)

Demais acoes de assessoria conforme doc:
  Convite para Imprensa Manaus (Credencial)
  Media Kit Fisico - Garrafa ODS (10-12 unidades, envio 04-07/06)
  Clipping de Midia - Manaus
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "gws"))
from gws_auth import get_credentials
from googleapiclient.discovery import build

SS_ID    = "1fccNKRv-OVwlk9Y4OyUNI3TzXN32GRqCC-qj-cgQ8c0"
SID1     = 1150580728   # Assessoria + Midia Kit
N_COMM   = 16

def rgb(h):
    h = h.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return {"red": r/255, "green": g/255, "blue": b/255}

BRANCO  = rgb("FFFFFF")
PRE_COR = rgb("E8F5E9")
DUR_COR = rgb("FFF3E0")
POS_COR = rgb("E3F2FD")
FASE_COR = {"Pre": PRE_COR, "Durante": DUR_COR, "Pos": POS_COR}

FIELDS_BG   = "userEnteredFormat(backgroundColor,verticalAlignment)"
FIELDS_WRAP = "userEnteredFormat(wrapStrategy)"

# ── Novos itens de Assessoria baseados no ClickUp doc ─────────────────────────
# (nome, fase, descricao, publico)
NEW_ASSESSORIA = [
    (
        "Release 1 - Save the Date e Itinerancia Geral",
        "Pre",
        "Anunciar Caminhao ODS chegando a Manaus. 7o ano de itinerancia, 3a vez na Amazonia, 2a vez em Manaus. Data: 14/06/2026 Praia de Ponta Negra. Proxima parada: Rio 28/08. Mencao institucional Vibra. Publicar por volta de 18/05/2026. Tom: leve, convite e save the date — nao detalhar programacao ainda.",
        "Imprensa Manaus / Nacional"
    ),
    (
        "Release 2 - Especifico Manaus",
        "Pre",
        "Programacao completa do dia 14/06 em tres turnos (manha regenerativa, tarde escolar, noite com shows MPB e influenciadores). Talk ODS 12/06 (universidade a confirmar). Escolas publicas atendidas. Tendas ODS, exposicao fotografica, VR, Central de Cidadania. Tema: protecao de criancas e adolescentes. Impacto esperado: 6.000 pessoas na praca, 400+ alunos. Publicar na semana do evento (09/06/2026). Vai para aprovacao quando programacao estiver consolidada.",
        "Imprensa Manaus"
    ),
    (
        "Convite para Imprensa Manaus / Credencial",
        "Pre",
        "Angelo convida formalmente jornalistas locais de Manaus: jornais, portais regionais e TV local. Contato previo para solicitar enderecos de entrega do media kit fisico. Convite via grupo do projeto.",
        "Jornalistas AM"
    ),
    (
        "Media Kit Fisico - Garrafa ODS (10-12 unidades)",
        "Pre",
        "Envio fisico para jornalistas selecionados de Manaus. Conteudo: garrafa de vidro 2-3L com adesivo Caminhao ODS + ODS3 / tag linkando garrafa ao ODS 3 / release impresso e dobrado dentro / adesivos para personalizacao. Envio entre 04/06 e 07/06/2026. Angelo: contato e enderecos. Abilio: orca e aprova custo. Designer NTICS: adesivos e tag.",
        "Jornalistas AM"
    ),
    (
        "Release Pos-Evento - Condicional",
        "Pos",
        "Publicar SOMENTE se houver historia de desdobramento com destaque real (ex: palestra que gerou repercussao, depoimento marcante, dado imprevisto positivo). Nao publicar apenas para reafirmar numeros do Release 2 — nao acrescenta valor jornalistico.",
        "Imprensa Manaus"
    ),
    (
        "Clipping de Midia - Manaus",
        "Pos",
        "Compilacao de todas as publicacoes e mencoes na imprensa de Manaus durante e apos o evento.",
        "Interno / Vibra"
    ),
]

N_NEW = len(NEW_ASSESSORIA)  # 6

# Posicoes na planilha (Aba 2):
# Row 0: COMM_HEADER
# Row 1: ASSESSORIA DE IMPRENSA (section header)
# Rows 2-13: assessoria items (atualmente 12)
# Row 14: MIDIA KIT VIBRA
# ...
ASSOC_ITEM_START = 2
ASSOC_ITEM_OLD_END = 14   # 12 itens antigos (rows 2..13)
ASSOC_ITEM_NEW_END = ASSOC_ITEM_START + N_NEW  # 8


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

def clear_validation(sid, r0, r1, c0, c1):
    return {"setDataValidation": {"range": {"sheetId": sid, "startRowIndex": r0,
        "endRowIndex": r1, "startColumnIndex": c0, "endColumnIndex": c1}}}


def main():
    creds = get_credentials()
    svc = build("sheets", "v4", credentials=creds)

    # ── 1. Deletar as 12 linhas antigas de assessoria e inserir 6 ─────────────
    # (12 - 6 = 6 linhas a menos)
    rows_to_delete = ASSOC_ITEM_OLD_END - ASSOC_ITEM_NEW_END  # 6

    svc.spreadsheets().batchUpdate(
        spreadsheetId=SS_ID,
        body={"requests": [{"deleteDimension": {"range": {
            "sheetId": SID1, "dimension": "ROWS",
            "startIndex": ASSOC_ITEM_NEW_END,
            "endIndex": ASSOC_ITEM_OLD_END
        }}}]}
    ).execute()
    print(f"Deletadas {rows_to_delete} linhas de assessoria antigas.")

    # ── 2. Escrever novos dados nas linhas 2..7 ───────────────────────────────
    new_rows = []
    for i, (nome, fase, desc, pub) in enumerate(NEW_ASSESSORIA, start=1):
        new_rows.append([str(i), nome, fase, "", "", "", "", "", "", "", desc, pub, "", "", "", ""])

    svc.spreadsheets().values().update(
        spreadsheetId=SS_ID,
        range="'Assessoria + Midia Kit'!A3",
        valueInputOption="USER_ENTERED",
        body={"values": new_rows}
    ).execute()
    print(f"Novos dados escritos: {N_NEW} itens de assessoria.")

    # ── 3. Formatar as 6 novas linhas ─────────────────────────────────────────
    fmt = []
    for i, item in enumerate(NEW_ASSESSORIA):
        ri = ASSOC_ITEM_START + i
        fmt.append(rc(SID1, ri, ri+1, 0, N_COMM,
            cf(bg=FASE_COR.get(item[1], BRANCO), valign="MIDDLE"), FIELDS_BG))
    # Checkboxes cols 4-9
    fmt.append(checkbox(SID1, ASSOC_ITEM_START, ASSOC_ITEM_NEW_END, 4, 10))
    # Dropdown Fase
    fmt.append(dropdown(SID1, ASSOC_ITEM_START, ASSOC_ITEM_NEW_END, 2, 3, ["Pre", "Durante", "Pos"]))
    # Wrap Nome(1) e Descricao(10)
    fmt.append(rc(SID1, ASSOC_ITEM_START, ASSOC_ITEM_NEW_END, 1, 2, cf(wrap="WRAP"), FIELDS_WRAP))
    fmt.append(rc(SID1, ASSOC_ITEM_START, ASSOC_ITEM_NEW_END, 10, 11, cf(wrap="WRAP"), FIELDS_WRAP))

    svc.spreadsheets().batchUpdate(
        spreadsheetId=SS_ID, body={"requests": fmt}
    ).execute()
    print(f"Formatacao aplicada.")
    print(f"\nURL: https://docs.google.com/spreadsheets/d/{SS_ID}/edit")


if __name__ == "__main__":
    main()
