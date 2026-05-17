#!/usr/bin/env python3
"""
fix_missing_sections_133.py
Corrige secoes com itens faltando e adiciona nova secao "Elementos de Producao".

Insercoes (processadas de baixo para cima numa unica batchUpdate):
  R1: 11 linhas na pos 60 → Elementos de Producao (1 header + 10 itens)
  R2:  6 linhas na pos 60 → novos itens Midia Kit (antes de Elementos)
  R3:  6 linhas na pos 55 → novos itens Assessoria (antes do header Midia Kit)
  R4: 10 linhas na pos 41 → novos itens Redes Sociais (antes do header Imprensa)

Posicoes finais das linhas inseridas (0-based):
  41-50  : 10 novos Redes Sociais
  65-70  :  6 novos Assessoria de Imprensa
  76-81  :  6 novos Midia Kit
  82     :  header Elementos de Producao
  83-92  : 10 itens Elementos de Producao
  93+    :  Pecas do Container (deslocado de 60 → +33)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "gws"))
from gws_auth import get_credentials
from googleapiclient.discovery import build

SS_ID = "1THxXD1Eus85T0T7j95QKzdHPFcXWTdTmwhhaWlAgIZo"
SHEET_ETAPAS = 0
N_COLS = 18

def rgb(hex_color):
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return {"red": r/255, "green": g/255, "blue": b/255}

GRAFITE = rgb("2D2D2D")
BRANCO  = rgb("FFFFFF")
PRE_COR = rgb("E8F5E9")
DUR_COR = rgb("FFF3E0")
POS_COR = rgb("E3F2FD")
CINZA   = rgb("F4F4F4")

FASE_COR = {"Pre": PRE_COR, "Durante": DUR_COR, "Pos": POS_COR}

# ─── Novos itens: Redes Sociais (+10) ─────────────────────────────────────────
# (nome, desc, fase, cidade)
NEW_SOCIAL = [
    ("Vem ai! — Stories de Contagem Regressiva (Manaus)", "Serie de stories diaria ate o Dia D", "Pre", "Manaus"),
    ("Faltam 15 dias — Post + Story (Manaus)", "Post de antecipacao 15 dias antes do evento", "Pre", "Manaus"),
    ("Faltam 7 dias / Semana do Evento (Manaus)", "Sequencia de posts da semana pre-evento", "Pre", "Manaus"),
    ("Apresentacao: Vibra Energia — Post Patrocinador", "Post apresentando a Vibra como patrocinadora", "Pre", "Ambas"),
    ("Apresentacao Parceiros Institucionais — Carrossel", "Serie de posts apresentando cada parceiro do projeto", "Pre", "Ambas"),
    ("Comeca hoje! — Post + Story Abertura (Manaus)", "Post de lancamento no Dia D — Manaus", "Durante", "Manaus"),
    ("Faltam 15 dias — Post + Story (RJ)", "Post de antecipacao 15 dias antes — Rio", "Pre", "RJ"),
    ("Faltam 7 dias / Semana do Evento (RJ)", "Sequencia de posts da semana pre-evento — Rio", "Pre", "RJ"),
    ("Vem ai! Ecoarte no Rio de Janeiro (2) — Carrossel", "Segundo carrossel de antecipacao para o RJ", "Pre", "RJ"),
    ("Comeca hoje! — Post + Story Abertura (RJ)", "Post de lancamento no Dia D — Rio de Janeiro", "Durante", "RJ"),
]

# ─── Novos itens: Assessoria de Imprensa (+6) ─────────────────────────────────
NEW_ASSESSORIA = [
    ("Save the Date / Nota de Imprensa", "Nota curta para lancamento inicial nos veiculos", "Pre", "Ambas"),
    ("Release Tematico: Educacao Ambiental + ODS", "Release segmentado para editoria de educacao e meio ambiente", "Pre", "Ambas"),
    ("Release Tematico: Impacto Social + ESG", "Release segmentado para veiculos de negocios e ESG", "Pre", "Ambas"),
    ("Release Tematico: Inovacao Educacional", "Release para secretarias de educacao e imprensa especializada", "Pre", "Ambas"),
    ("Audio / Nota para Radio — Porta-Vozes", "Nota ou audio de 30s adaptado para radios locais", "Pre", "Ambas"),
    ("Esqueleto de Release Diario (Dia D)", "Template de release para o dia do evento com numeralha parcial", "Durante", "Ambas"),
]

# ─── Novos itens: Midia Kit Vibra (+6) ────────────────────────────────────────
NEW_MIDIAKIT = [
    ("Tutorial de Uso do Midia Kit", "Instrucoes de como usar cada peca e quando postar", "Pre", "Ambas"),
    ("Video Institucional / Vinheta do Projeto (60s)", "Video curto para parceiros e imprensa compartilharem", "Pre", "Ambas"),
    ("Fotos Oficiais + Pack de Imagens para Imprensa", "Pack com fotos em alta resolucao aprovadas para veiculos", "Pre", "Ambas"),
    ("Release Oficial (versao para distribuicao no Kit)", "Release formatado para inclusao no midia kit dos parceiros", "Pre", "Ambas"),
    ("Filtros e Frames para Stories (3 variacoes)", "Filtros e molduras brandados para o evento", "Pre", "Ambas"),
    ("Pecas Adicionais de Instagram para Parceiros (carrossel)", "Carrossel extra pronto para parceiros compartilharem", "Pre", "Ambas"),
]

# ─── Elementos de Producao (1 header + 10 itens) ─────────────────────────────
# Primeiro elemento e o header
ELEMENTOS = [
    ("ELEMENTOS DE PRODUCAO", "", "header", ""),
    ("Apresentacao / Deck Executivo do Projeto", "Deck PPT/Slides para apresentar a parceiros e secretarias", "Pre", "Ambas"),
    ("Video de Abertura (para telas no container)", "Video institucional exibido continuamente durante o evento", "Pre", "Ambas"),
    ("Kit de Onboarding da Equipe / Voluntarios", "Material de boas-vindas, instrucoes e fluxos para a equipe", "Pre", "Ambas"),
    ("PPT de Capacitacao da Equipe", "Apresentacao de treinamento pre-evento para monitores", "Pre", "Ambas"),
    ("Programacao Completa do Evento (doc oficial)", "Documento com grade horaria e descricao das atividades", "Pre", "Ambas"),
    ("Registro Fotografico Profissional", "Cobertura fotografica por fotografo profissional no Dia D", "Durante", "Ambas"),
    ("Registro em Video / Filmagem do Evento", "Captacao de video para aftermovie e pos-evento", "Durante", "Ambas"),
    ("Clipping de Midia (monitoramento de mencoes)", "Compilacao de todas as publicacoes e mencoes na imprensa", "Durante", "Ambas"),
    ("Relatorio Parcial (para Vibra — durante evento)", "Relatorio intermediario com primeiros numeros para o patrocinador", "Durante", "Ambas"),
    ("Relatorio Final de Impacto (com fotos e dados)", "Documento final consolidando ambos os eventos — Cota 2", "Pos", "Ambas"),
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

def row_h(sid, ri, px):
    return {"updateDimensionProperties": {"range": {"sheetId": sid,
        "dimension": "ROWS", "startIndex": ri, "endIndex": ri+1},
        "properties": {"pixelSize": px}, "fields": "pixelSize"}}

def insert_dim(sid, start, end):
    return {"insertDimension": {"range": {"sheetId": sid, "dimension": "ROWS",
        "startIndex": start, "endIndex": end}, "inheritFromBefore": False}}

def checkbox(sid, r0, r1, c0, c1):
    return {"setDataValidation": {"range": {"sheetId": sid, "startRowIndex": r0,
        "endRowIndex": r1, "startColumnIndex": c0, "endColumnIndex": c1},
        "rule": {"condition": {"type": "BOOLEAN"}, "showCustomUi": True}}}

def dropdown(sid, r0, r1, c0, c1, vals):
    return {"setDataValidation": {"range": {"sheetId": sid, "startRowIndex": r0,
        "endRowIndex": r1, "startColumnIndex": c0, "endColumnIndex": c1},
        "rule": {"condition": {"type": "ONE_OF_LIST",
            "values": [{"userEnteredValue": v} for v in vals]},
            "showCustomUi": True, "strict": True}}}

FIELDS_FULL = "userEnteredFormat(backgroundColor,textFormat,wrapStrategy,horizontalAlignment,verticalAlignment)"
FIELDS_BG   = "userEnteredFormat(backgroundColor,verticalAlignment)"
FIELDS_WRAP = "userEnteredFormat(wrapStrategy)"

def make_row(nome, desc, fase, cidade):
    """Formato principal: col0=#, col1=nome, col2=fase, col3=cidade."""
    return ["", nome, fase, cidade, "", "", "", "", "", "", "", desc, "", "", "", "", "", ""]

def main():
    creds = get_credentials()
    svc = build("sheets", "v4", credentials=creds)

    # ── 1. Inserir linhas (ordem bottom-to-top numa unica batchUpdate) ─────────
    insert_reqs = [
        insert_dim(SHEET_ETAPAS, 60, 71),  # R1: 11 linhas para Elementos de Producao
        insert_dim(SHEET_ETAPAS, 60, 66),  # R2:  6 linhas para novos Midia Kit
        insert_dim(SHEET_ETAPAS, 55, 61),  # R3:  6 linhas para novos Assessoria
        insert_dim(SHEET_ETAPAS, 41, 51),  # R4: 10 linhas para novos Redes Sociais
    ]
    svc.spreadsheets().batchUpdate(
        spreadsheetId=SS_ID, body={"requests": insert_reqs}
    ).execute()
    print("Insercoes de linhas concluidas.")

    # ── 2. Escrever dados nas linhas inseridas ─────────────────────────────────
    # Posicoes finais (0-based) apos todas as insercoes:
    #   41-50 : novos Redes Sociais  → planilha A42:R51
    #   65-70 : novos Assessoria     → planilha A66:R71
    #   76-81 : novos Midia Kit      → planilha A77:R82
    #   82    : header Elementos     → planilha A83:R83
    #   83-92 : itens Elementos      → planilha A84:R93

    svc.spreadsheets().values().update(
        spreadsheetId=SS_ID,
        range="'Etapas de Produção'!A42:R51",
        valueInputOption="USER_ENTERED",
        body={"values": [make_row(*item) for item in NEW_SOCIAL]}
    ).execute()

    svc.spreadsheets().values().update(
        spreadsheetId=SS_ID,
        range="'Etapas de Produção'!A66:R71",
        valueInputOption="USER_ENTERED",
        body={"values": [make_row(*item) for item in NEW_ASSESSORIA]}
    ).execute()

    svc.spreadsheets().values().update(
        spreadsheetId=SS_ID,
        range="'Etapas de Produção'!A77:R82",
        valueInputOption="USER_ENTERED",
        body={"values": [make_row(*item) for item in NEW_MIDIAKIT]}
    ).execute()

    elem_rows = []
    for entry in ELEMENTOS:
        if entry[2] == "header":
            elem_rows.append([entry[0]] + [""] * 17)
        else:
            elem_rows.append(make_row(*entry))
    svc.spreadsheets().values().update(
        spreadsheetId=SS_ID,
        range="'Etapas de Produção'!A83:R93",
        valueInputOption="USER_ENTERED",
        body={"values": elem_rows}
    ).execute()

    print("Dados escritos.")

    # ── 3. Formatacao das novas linhas ─────────────────────────────────────────
    fmt_reqs = []

    # Redes Sociais (rows 41-50)
    for i, item in enumerate(NEW_SOCIAL):
        ri = 41 + i
        cor = FASE_COR.get(item[2], BRANCO)
        fmt_reqs.append(rc(SHEET_ETAPAS, ri, ri+1, 0, N_COLS,
            cf(bg=cor, valign="MIDDLE"), FIELDS_BG))

    # Assessoria (rows 65-70)
    for i, item in enumerate(NEW_ASSESSORIA):
        ri = 65 + i
        cor = FASE_COR.get(item[2], BRANCO)
        fmt_reqs.append(rc(SHEET_ETAPAS, ri, ri+1, 0, N_COLS,
            cf(bg=cor, valign="MIDDLE"), FIELDS_BG))

    # Midia Kit (rows 76-81)
    for i, item in enumerate(NEW_MIDIAKIT):
        ri = 76 + i
        cor = FASE_COR.get(item[2], BRANCO)
        fmt_reqs.append(rc(SHEET_ETAPAS, ri, ri+1, 0, N_COLS,
            cf(bg=cor, valign="MIDDLE"), FIELDS_BG))

    # Elementos de Producao: header (row 82) + itens (83-92)
    fmt_reqs.append(rc(SHEET_ETAPAS, 82, 83, 0, N_COLS,
        cf(bg=GRAFITE, fg=BRANCO, bold=True, size=11, halign="LEFT", valign="MIDDLE"),
        FIELDS_FULL))
    fmt_reqs.append(row_h(SHEET_ETAPAS, 82, 36))
    for i, entry in enumerate(ELEMENTOS[1:]):
        ri = 83 + i
        cor = FASE_COR.get(entry[2], BRANCO)
        fmt_reqs.append(rc(SHEET_ETAPAS, ri, ri+1, 0, N_COLS,
            cf(bg=cor, valign="MIDDLE"), FIELDS_BG))

    # Wrap coluna B (nome) para novas linhas de comunicacao
    for r0, r1 in [(41, 51), (65, 71), (76, 82)]:
        fmt_reqs.append(rc(SHEET_ETAPAS, r0, r1, 1, 2, cf(wrap="WRAP"), FIELDS_WRAP))

    # Checkboxes (F-K, idx 5-10) para novas linhas
    all_new_item_ranges = [(41, 51), (65, 71), (76, 82), (83, 93)]
    for r0, r1 in all_new_item_ranges:
        fmt_reqs.append(checkbox(SHEET_ETAPAS, r0, r1, 5, 11))

    # Dropdowns Fase e Cidade para novas linhas de comunicacao
    for r0, r1 in [(41, 51), (65, 71), (76, 82)]:
        fmt_reqs.append(dropdown(SHEET_ETAPAS, r0, r1, 2, 3, ["Pre", "Durante", "Pos"]))
        fmt_reqs.append(dropdown(SHEET_ETAPAS, r0, r1, 3, 4, ["Manaus", "RJ", "Ambas"]))

    svc.spreadsheets().batchUpdate(
        spreadsheetId=SS_ID, body={"requests": fmt_reqs}
    ).execute()

    print("Formatacao aplicada.")
    print(f"URL: https://docs.google.com/spreadsheets/d/{SS_ID}/edit")

if __name__ == "__main__":
    main()
