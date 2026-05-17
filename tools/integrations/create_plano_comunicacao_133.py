#!/usr/bin/env python3
"""
create_plano_comunicacao_133.py
Cria o Google Sheet "Etapas de Produção 133 Vibra 2026" no Drive de comunicação do projeto.

Usage:
  python tools/integrations/create_plano_comunicacao_133.py

Output: URL da planilha criada.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "gws"))
from gws_auth import get_credentials
from googleapiclient.discovery import build

# Drive comunicação do projeto 133
DRIVE_FOLDER_ID = "1rHKvCogQ4pczO8JHqeYTmYUoTTaYMex0"

# ── Cores NTICS ──────────────────────────────────────────────────────────────
def rgb(hex_color: str) -> dict:
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return {"red": r / 255, "green": g / 255, "blue": b / 255}

AZUL      = rgb("005F73")   # Email Marketing
VERDE     = rgb("128C7E")   # WhatsApp
ROSA      = rgb("D41A6A")   # Redes Sociais
LARANJA   = rgb("E86428")   # Assessoria de Imprensa
ROXO      = rgb("6B2D7B")   # Mídia Kit Vibra
GRAFITE   = rgb("2D2D2D")
CINZA_CLR = rgb("F4F4F4")
BRANCO    = rgb("FFFFFF")

# Cores de fase (fundo leve para linhas)
FASE_PRE     = rgb("E8F5E9")  # verde claro
FASE_DUR     = rgb("FFF3E0")  # laranja claro
FASE_POS     = rgb("E3F2FD")  # azul claro

# Cor de seção (cabeçalho de cada canal)
CANAL_CORES = {
    "email":     AZUL,
    "whatsapp":  VERDE,
    "social":    ROSA,
    "imprensa":  LARANJA,
    "kit":       ROXO,
}


# ── Dados ──────────────────────────────────────────────────────────────────

FLUXO_HEADER = ["Dia da Semana", "Email Marketing", "WhatsApp", "Redes Sociais", "Assessoria de Imprensa"]
FLUXO_ROWS = [
    ["Sexta-Feira",   "Briefing\n(Lucas / Bruna)",      "Briefing\n(Lucas / Bruna)",  "Briefing\n(Lucas / Bruna)",  "Briefing\n(Lucas / Ângelo)"],
    ["Quarta-Feira",  "Layout / Arte\n(Designer)",      "Layout / Arte\n(Designer)", "Layout / Arte\n(Designer)", "Redação\n(Ângelo)"],
    ["Quinta-Feira",  "Aprovação Interna\n(Bruna)",     "Aprovação Interna\n(Bruna)", "Aprovação Interna\n(Bruna)", "Aprovação Interna\n(Bruna)"],
    ["Sexta-Feira",   "⚡ Aprovação Vibra\n(se aplic.)", "⚡ Aprovação Vibra\n(se aplic.)", "⚡ Aprovação Vibra\n(se aplic.)", "⚡ Aprovação Vibra\n(se aplic.)"],
    ["Segunda-Feira", "Disparo\n(Designer / Lucas)",    "Envio\n(Equipe)",            "Postagem\n(Designer)",       "Envio Imprensa\n(Ângelo)"],
]

ETAPAS_HEADER = [
    "#", "Nome", "Fase", "Cidade", "Data Prevista",
    "Briefing\nEnviado", "Conteúdo/\nArte", "Aprov.\nInterna", "Aprov.\nVibra",
    "Postagem/\nDisparo", "Checagem",
    "Descrição / Referência", "Distribuição / Público",
    "Resp. Aprovação", "Resp. Postagem/Envio",
    "Link Briefing", "Link Arte", "Link Publicado"
]

# Seções: (label, canal_key, cor_fundo, lista de items)
# Item: (num, nome, fase, cidade, data, desc, distribuicao, resp_aprov, resp_post)
SECOES = [
    {
        "label": "✉  EMAIL MARKETING  —  14 peças",
        "canal": "email",
        "items": [
            (1,  "Chamada p/ Participação — Escolas (Manaus)",     "Pré",     "Manaus", "mai/26", "", "Diretores e coordenadores", "Bruna", "Lucas / Designer"),
            (2,  "Chamada p/ Participação — Comunidade (Manaus)",  "Pré",     "Manaus", "mai/26", "", "Lista geral Manaus", "Bruna", "Lucas / Designer"),
            (3,  "Confirmação de Inscrição (automático — Manaus)", "Pré",     "Manaus", "mai/26", "Fluxo automático pós-inscrição", "Inscritos", "Bruna", "Lucas / Designer"),
            (4,  "Lembrete — 1 semana antes (Manaus)",             "Pré",     "Manaus", "07/jun", "", "Inscritos confirmados", "Bruna", "Lucas / Designer"),
            (5,  "Lembrete — Amanhã começa (Manaus)",              "Pré",     "Manaus", "13/jun", "", "Inscritos confirmados", "Bruna", "Lucas / Designer"),
            (6,  "Estamos ao vivo! (Manaus)",                      "Durante", "Manaus", "14/jun", "", "Inscritos + lista geral", "Bruna", "Lucas / Designer"),
            (7,  "Melhores momentos + Obrigado (Manaus)",          "Pós",     "Manaus", "16/jun", "", "Participantes + lista geral", "Bruna", "Lucas / Designer"),
            (8,  "Chamada p/ Participação — Escolas (RJ)",         "Pré",     "RJ",     "jul/26", "", "Diretores e coordenadores RJ", "Bruna", "Lucas / Designer"),
            (9,  "Chamada p/ Participação — Comunidade (RJ)",      "Pré",     "RJ",     "jul/26", "", "Lista geral RJ", "Bruna", "Lucas / Designer"),
            (10, "Lembrete — 1 semana antes (RJ)",                 "Pré",     "RJ",     "22/ago", "", "Inscritos confirmados RJ", "Bruna", "Lucas / Designer"),
            (11, "Lembrete — Amanhã começa (RJ)",                  "Pré",     "RJ",     "28/ago", "", "Inscritos confirmados RJ", "Bruna", "Lucas / Designer"),
            (12, "Estamos ao vivo! (RJ)",                          "Durante", "RJ",     "29/ago", "", "Inscritos + lista geral RJ", "Bruna", "Lucas / Designer"),
            (13, "Melhores momentos + Obrigado (RJ)",              "Pós",     "RJ",     "31/ago", "", "Participantes + lista geral RJ", "Bruna", "Lucas / Designer"),
            (14, "Relatório de Impacto Final (Vibra)",             "Pós",     "Ambas",  "out/26", "One Page Report + numeralha Cota 2", "Equipe Vibra (patrocínio)", "Bruna", "Lucas / Designer"),
        ]
    },
    {
        "label": "💬  WHATSAPP  —  8 peças",
        "canal": "whatsapp",
        "items": [
            (15, "Card Convite Escolas (Manaus)",              "Pré",     "Manaus", "mai/26", "", "Grupos de diretores/professores", "Bruna", "Equipe"),
            (16, "Card Convite Comunidade (Manaus)",           "Pré",     "Manaus", "mai/26", "", "Grupos comunitários Manaus", "Bruna", "Equipe"),
            (17, "Card Programação do Dia D (Manaus)",         "Durante", "Manaus", "14/jun", "", "Todos os grupos Manaus", "Bruna", "Equipe"),
            (18, "Card Agradecimento + Numeralha (Manaus)",    "Pós",     "Manaus", "15/jun", "", "Todos os grupos Manaus", "Bruna", "Equipe"),
            (19, "Card Convite Escolas (RJ)",                  "Pré",     "RJ",     "jul/26", "", "Grupos de diretores/professores RJ", "Bruna", "Equipe"),
            (20, "Card Convite Comunidade (RJ)",               "Pré",     "RJ",     "jul/26", "", "Grupos comunitários RJ", "Bruna", "Equipe"),
            (21, "Card Programação do Dia D (RJ)",             "Durante", "RJ",     "29/ago", "", "Todos os grupos RJ", "Bruna", "Equipe"),
            (22, "Card Agradecimento + Numeralha (RJ)",        "Pós",     "RJ",     "30/ago", "", "Todos os grupos RJ", "Bruna", "Equipe"),
        ]
    },
    {
        "label": "📱  REDES SOCIAIS (Instagram + LinkedIn)  —  15 peças",
        "canal": "social",
        "items": [
            (23, "Vem aí! Ecoarte em Manaus — post (1)",                  "Pré",     "Manaus", "mai/26", "Post único", "Seguidores Instagram", "Bruna", "Designer"),
            (24, "Vem aí! Ecoarte em Manaus — carrossel (2)",             "Pré",     "Manaus", "mai/26", "Carrossel 8 cards", "Seguidores Instagram", "Bruna", "Designer"),
            (25, "O que esperar: Meu Corpo, Minhas Regras",               "Pré",     "Ambas",  "jun/26", "Carrossel educativo — tema sensível", "Seguidores Instagram", "Bruna", "Designer"),
            (26, "Os ODS do Ecoarte (carrossel educativo)",               "Pré",     "Ambas",  "jun/26", "17 ODS atendidos", "Seguidores Instagram", "Bruna", "Designer"),
            (27, "Programação do Dia D Manaus",                           "Durante", "Manaus", "14/jun", "Post + Story", "Seguidores Instagram", "Bruna", "Designer"),
            (28, "Cobertura ao vivo Manaus (Stories)",                    "Durante", "Manaus", "14/jun", "Stories em tempo real", "Seguidores Instagram", "Bruna", "Designer / Equipe"),
            (29, "Melhores Momentos Manaus (carrossel pós)",              "Pós",     "Manaus", "16/jun", "Carrossel 8-10 cards", "Seguidores Instagram", "Bruna", "Designer"),
            (30, "Numeralha de Impacto Manaus",                           "Pós",     "Manaus", "jun/26", "Post único com números", "Seguidores Instagram", "Bruna", "Designer"),
            (31, "LinkedIn: Vibra + Ecoarte (institucional)",             "Pré",     "Ambas",  "jun/26", "Post institucional collab", "Seguidores LinkedIn", "Bruna", "Designer"),
            (32, "Vem aí! Ecoarte no Rio de Janeiro",                     "Pré",     "RJ",     "jul/26", "Post + carrossel", "Seguidores Instagram", "Bruna", "Designer"),
            (33, "Programação do Dia D RJ",                               "Durante", "RJ",     "29/ago", "Post + Story", "Seguidores Instagram", "Bruna", "Designer"),
            (34, "Cobertura ao vivo RJ (Stories)",                        "Durante", "RJ",     "29/ago", "Stories em tempo real", "Seguidores Instagram", "Bruna", "Designer / Equipe"),
            (35, "Melhores Momentos RJ (carrossel pós)",                  "Pós",     "RJ",     "ago/set","Carrossel 8-10 cards", "Seguidores Instagram", "Bruna", "Designer"),
            (36, "Numeralha de Impacto Total — Cota 2",                   "Pós",     "Ambas",  "set/26", "Post único + LinkedIn", "Seguidores Instagram + LinkedIn", "Bruna", "Designer"),
            (37, "LinkedIn: Resultados finais para Vibra",                "Pós",     "Ambas",  "set/26", "Post institucional ESG", "Seguidores LinkedIn", "Bruna", "Designer"),
        ]
    },
    {
        "label": "📰  ASSESSORIA DE IMPRENSA  —  13 peças",
        "canal": "imprensa",
        "items": [
            (38, "Release: Anúncio do Ecoarte Manaus",               "Pré",     "Manaus", "mai/26", "Distribuição para veículos AM", "Veículos regionais Manaus", "Bruna", "Ângelo"),
            (39, "Convite para Imprensa — Manaus",                   "Pré",     "Manaus", "jun/26", "E-mail de convite credenciado", "Jornalistas Manaus", "Bruna", "Ângelo"),
            (40, "Mailing de Imprensa — Manaus",                     "Pré",     "Manaus", "mai/26", "Lista de contatos da imprensa AM", "Interno", "Bruna", "Ângelo"),
            (41, "Nota Exclusiva (1 veículo local) — Manaus",        "Pré",     "Manaus", "jun/26", "1 veículo estratégico AM", "1 veículo exclusivo", "Bruna", "Ângelo"),
            (42, "Release do Dia D — Manaus",                        "Durante", "Manaus", "14/jun", "Release com numeralha parcial", "Veículos AM + nacionais", "Bruna", "Ângelo"),
            (43, "Release Pós-Evento com Numeralha — Manaus",        "Pós",     "Manaus", "15/jun", "Numeralha completa + fotos", "Veículos AM + nacionais", "Bruna", "Ângelo"),
            (44, "Release: Anúncio do Ecoarte RJ",                   "Pré",     "RJ",     "jul/26", "Distribuição para veículos RJ", "Veículos regionais RJ", "Bruna", "Ângelo"),
            (45, "Mailing de Imprensa — RJ",                         "Pré",     "RJ",     "jul/26", "Lista de contatos da imprensa RJ", "Interno", "Bruna", "Ângelo"),
            (46, "Convite para Imprensa — RJ",                       "Pré",     "RJ",     "ago/26", "E-mail de convite credenciado RJ", "Jornalistas RJ", "Bruna", "Ângelo"),
            (47, "Nota Exclusiva (1 veículo) — RJ",                  "Pré",     "RJ",     "ago/26", "1 veículo estratégico RJ", "1 veículo exclusivo RJ", "Bruna", "Ângelo"),
            (48, "Release do Dia D — RJ",                            "Durante", "RJ",     "29/ago", "Release com numeralha parcial", "Veículos RJ + nacionais", "Bruna", "Ângelo"),
            (49, "Release Pós-Evento com Numeralha — RJ",            "Pós",     "RJ",     "ago/set","Numeralha completa + fotos", "Veículos RJ + nacionais", "Bruna", "Ângelo"),
            (50, "Release Final Cota 2 — Impacto Total",             "Pós",     "Ambas",  "set/26", "Resultado consolidado 2 cidades", "Nacional + Vibra", "Bruna", "Ângelo"),
        ]
    },
    {
        "label": "🎯  MÍDIA KIT VIBRA ENERGIA  —  4 peças",
        "canal": "kit",
        "items": [
            (51, "Posts Instagram para Vibra compartilhar (3 posts)", "Pré", "Ambas", "jun/26", "Co-assinatura: Realização NTICS / Patrocínio Vibra", "Canal Vibra Energia", "Bruna / Vibra", "Vibra"),
            (52, "Card LinkedIn para Vibra (collab)",                 "Pré", "Ambas", "jun/26", "Post collab Vibra + NTICS", "Canal Vibra LinkedIn", "Bruna / Vibra", "Vibra"),
            (53, "Copy sugerido para Vibra (redes)",                  "Pré", "Ambas", "jun/26", "Texto pronto para uso da equipe Vibra", "Equipe comun. Vibra", "Bruna / Vibra", "Vibra"),
            (54, "Logo co-assinatura Realização NTICS / Patrocínio Vibra", "Pré", "Ambas", "mai/26", "Arquivo fonte (PNG + AI)", "Designer / Vibra", "Bruna / Vibra", "—"),
        ]
    },
]

# Mapeamento fase → cor de linha
FASE_COR = {
    "Pré":     FASE_PRE,
    "Durante": FASE_DUR,
    "Pós":     FASE_POS,
}


# ── Helpers API ───────────────────────────────────────────────────────────────

def cell_format(bg=None, bold=False, fg=None, size=None, wrap=None, halign=None, valign=None):
    fmt = {}
    if bg:
        fmt["backgroundColor"] = bg
    txt = {}
    if bold:
        txt["bold"] = True
    if size:
        txt["fontSize"] = size
    if fg:
        txt["foregroundColor"] = fg
    if txt:
        fmt["textFormat"] = txt
    if wrap:
        fmt["wrapStrategy"] = wrap
    if halign:
        fmt["horizontalAlignment"] = halign
    if valign:
        fmt["verticalAlignment"] = valign
    return fmt


def repeat_cell(sheet_id, row_start, row_end, col_start, col_end, fmt: dict, fields: str):
    return {
        "repeatCell": {
            "range": {
                "sheetId": sheet_id,
                "startRowIndex": row_start,
                "endRowIndex": row_end,
                "startColumnIndex": col_start,
                "endColumnIndex": col_end,
            },
            "cell": {"userEnteredFormat": fmt},
            "fields": fields,
        }
    }


def merge(sheet_id, r0, r1, c0, c1):
    return {
        "mergeCells": {
            "range": {
                "sheetId": sheet_id,
                "startRowIndex": r0,
                "endRowIndex": r1,
                "startColumnIndex": c0,
                "endColumnIndex": c1,
            },
            "mergeType": "MERGE_ALL",
        }
    }


def freeze(sheet_id, rows=1, cols=0):
    return {
        "updateSheetProperties": {
            "properties": {
                "sheetId": sheet_id,
                "gridProperties": {
                    "frozenRowCount": rows,
                    "frozenColumnCount": cols,
                },
            },
            "fields": "gridProperties.frozenRowCount,gridProperties.frozenColumnCount",
        }
    }


def set_col_width(sheet_id, col_idx, pixels):
    return {
        "updateDimensionProperties": {
            "range": {
                "sheetId": sheet_id,
                "dimension": "COLUMNS",
                "startIndex": col_idx,
                "endIndex": col_idx + 1,
            },
            "properties": {"pixelSize": pixels},
            "fields": "pixelSize",
        }
    }


def set_row_height(sheet_id, row_idx, pixels):
    return {
        "updateDimensionProperties": {
            "range": {
                "sheetId": sheet_id,
                "dimension": "ROWS",
                "startIndex": row_idx,
                "endIndex": row_idx + 1,
            },
            "properties": {"pixelSize": pixels},
            "fields": "pixelSize",
        }
    }


def checkbox_validation(sheet_id, r0, r1, c0, c1):
    return {
        "setDataValidation": {
            "range": {
                "sheetId": sheet_id,
                "startRowIndex": r0,
                "endRowIndex": r1,
                "startColumnIndex": c0,
                "endColumnIndex": c1,
            },
            "rule": {
                "condition": {"type": "BOOLEAN"},
                "showCustomUi": True,
            },
        }
    }


def dropdown_validation(sheet_id, r0, r1, c0, c1, values: list):
    return {
        "setDataValidation": {
            "range": {
                "sheetId": sheet_id,
                "startRowIndex": r0,
                "endRowIndex": r1,
                "startColumnIndex": c0,
                "endColumnIndex": c1,
            },
            "rule": {
                "condition": {
                    "type": "ONE_OF_LIST",
                    "values": [{"userEnteredValue": v} for v in values],
                },
                "showCustomUi": True,
                "strict": True,
            },
        }
    }


# ── Construção ──────────────────────────────────────────────────────────────

def build_etapas_data():
    """
    Retorna (rows_values, section_row_map, item_row_map)
    rows_values: lista de listas para values.update
    section_row_map: {row_index: canal_key}   — linhas de seção
    item_row_map: {row_index: fase}            — linhas de item
    """
    rows = [ETAPAS_HEADER]
    section_rows = {}   # row_idx → canal_key
    item_rows = {}      # row_idx → fase

    for secao in SECOES:
        sec_row = len(rows)
        section_rows[sec_row] = secao["canal"]
        rows.append([secao["label"]] + [""] * (len(ETAPAS_HEADER) - 1))

        for item in secao["items"]:
            num, nome, fase, cidade, data, desc, dist, resp_a, resp_p = item
            # checkboxes: FALSE inicialmente (6 colunas: F G H I J K = idx 5..10)
            row = [
                num, nome, fase, cidade, data,
                False, False, False, False, False, False,
                desc, dist,
                resp_a, resp_p,
                "", "", "",  # links em branco
            ]
            r_idx = len(rows)
            item_rows[r_idx] = fase
            rows.append(row)

    return rows, section_rows, item_rows


def build_fluxo_data():
    rows = [FLUXO_HEADER] + FLUXO_ROWS
    return rows


# ── Main ────────────────────────────────────────────────────────────────────

def main():
    creds = get_credentials()
    sheets_svc = build("sheets", "v4", credentials=creds)
    drive_svc  = build("drive",  "v3", credentials=creds)

    # 1. Criar planilha (skip se já existir — passar EXISTING_ID)
    import os
    existing_id = os.environ.get("EXISTING_SHEET_ID", "")
    if existing_id:
        ss_id = existing_id
        print(f"[sheets] Usando planilha existente: {ss_id}")
        # Apenas formatar (dados já estão lá)
        goto_format = True
    else:
        goto_format = False

    if not goto_format:
        print("[sheets] Criando planilha...")
        spreadsheet = sheets_svc.spreadsheets().create(body={
        "properties": {"title": "Etapas de Produção 133 — Ecoarte Vibra 2026"},
        "sheets": [
            {
                "properties": {
                    "sheetId": 0,
                    "title": "Etapas de Produção",
                    "tabColor": {"red": 0, "green": 0.373, "blue": 0.451},  # Azul Petróleo
                    "gridProperties": {"rowCount": 200, "columnCount": 18},
                }
            },
            {
                "properties": {
                    "sheetId": 1,
                    "title": "Fluxo de Produção",
                    "tabColor": {"red": 0.239, "green": 0.667, "blue": 0.208},  # Verde
                    "gridProperties": {"rowCount": 20, "columnCount": 6},
                }
            },
        ],
    }).execute()

    ss_id = spreadsheet["spreadsheetId"]
    sheet_etapas = 0
    sheet_fluxo  = 1

    print(f"[sheets] Planilha criada: {ss_id}")

    # 2. Mover para o Drive de comunicação
    file = drive_svc.files().get(fileId=ss_id, fields="parents").execute()
    prev_parents = ",".join(file.get("parents", []))
    drive_svc.files().update(
        fileId=ss_id,
        addParents=DRIVE_FOLDER_ID,
        removeParents=prev_parents,
        fields="id,parents",
    ).execute()
    print(f"[sheets] Movida para pasta Drive comunicação.")

    # 3. Escrever dados — Fluxo de Produção
    fluxo_rows = build_fluxo_data()
    sheets_svc.spreadsheets().values().update(
        spreadsheetId=ss_id,
        range="Fluxo de Produção!A1",
        valueInputOption="USER_ENTERED",
        body={"values": fluxo_rows},
    ).execute()
    print("[sheets] Fluxo de Produção preenchido.")

    # 4. Escrever dados — Etapas de Produção
    etapas_rows, section_row_map, item_row_map = build_etapas_data()
    sheets_svc.spreadsheets().values().update(
        spreadsheetId=ss_id,
        range="Etapas de Produção!A1",
        valueInputOption="USER_ENTERED",
        body={"values": etapas_rows},
    ).execute()
    print("[sheets] Etapas de Produção preenchidas.")

    # 5. Formatação em lote
    requests = []

    # ── Aba Etapas: cabeçalho (linha 1)
    requests.append(repeat_cell(
        sheet_etapas, 0, 1, 0, len(ETAPAS_HEADER),
        cell_format(bg=GRAFITE, fg=BRANCO, bold=True, size=10, wrap="WRAP", halign="CENTER", valign="MIDDLE"),
        "userEnteredFormat(backgroundColor,foregroundColor,textFormat,wrapStrategy,horizontalAlignment,verticalAlignment)"
    ))
    # Freeze linha 1 + coluna A
    requests.append(freeze(sheet_etapas, rows=1, cols=1))

    # ── Aba Etapas: linhas de seção
    for row_idx, canal_key in section_row_map.items():
        cor = CANAL_CORES[canal_key]
        requests.append(repeat_cell(
            sheet_etapas, row_idx, row_idx + 1, 0, len(ETAPAS_HEADER),
            cell_format(bg=cor, fg=BRANCO, bold=True, size=11, halign="LEFT", valign="MIDDLE"),
            "userEnteredFormat(backgroundColor,foregroundColor,textFormat,horizontalAlignment,verticalAlignment)"
        ))
        requests.append(set_row_height(sheet_etapas, row_idx, 36))

    # ── Aba Etapas: linhas de item (cor de fase)
    for row_idx, fase in item_row_map.items():
        cor = FASE_COR.get(fase, BRANCO)
        requests.append(repeat_cell(
            sheet_etapas, row_idx, row_idx + 1, 0, len(ETAPAS_HEADER),
            cell_format(bg=cor, valign="MIDDLE"),
            "userEnteredFormat(backgroundColor,verticalAlignment)"
        ))

    # ── Aba Etapas: larguras de colunas (A=40, B=280, C=70, D=65, E=80, F-K=70 cada, L=200, M=200, N=100, O=120, P-R=160)
    col_widths = [40, 280, 70, 65, 80, 70, 70, 70, 70, 70, 70, 200, 200, 100, 130, 160, 160, 160]
    for ci, w in enumerate(col_widths):
        requests.append(set_col_width(sheet_etapas, ci, w))

    # ── Aba Etapas: checkboxes para colunas F..K (idx 5..10) em todas as linhas de item
    all_item_rows = list(item_row_map.keys())
    if all_item_rows:
        min_r = min(all_item_rows)
        max_r = max(all_item_rows) + 1
        requests.append(checkbox_validation(sheet_etapas, min_r, max_r, 5, 11))

    # ── Aba Etapas: dropdown Fase (col C = idx 2) e Cidade (col D = idx 3)
    if all_item_rows:
        requests.append(dropdown_validation(sheet_etapas, min_r, max_r, 2, 3, ["Pré", "Durante", "Pós"]))
        requests.append(dropdown_validation(sheet_etapas, min_r, max_r, 3, 4, ["Manaus", "RJ", "Ambas"]))

    # ── Aba Etapas: wrap na col B (nome) e L,M (descrição, distribuição)
    requests.append(repeat_cell(
        sheet_etapas, 1, len(etapas_rows), 1, 2,
        cell_format(wrap="WRAP"),
        "userEnteredFormat(wrapStrategy)"
    ))
    for ci in [11, 12]:
        requests.append(repeat_cell(
            sheet_etapas, 1, len(etapas_rows), ci, ci + 1,
            cell_format(wrap="WRAP"),
            "userEnteredFormat(wrapStrategy)"
        ))

    # ── Aba Fluxo: cabeçalho (linha 1)
    requests.append(repeat_cell(
        sheet_fluxo, 0, 1, 0, 5,
        cell_format(bg=AZUL, fg=BRANCO, bold=True, size=11, wrap="WRAP", halign="CENTER", valign="MIDDLE"),
        "userEnteredFormat(backgroundColor,foregroundColor,textFormat,wrapStrategy,horizontalAlignment,verticalAlignment)"
    ))
    requests.append(freeze(sheet_fluxo, rows=1))

    # ── Aba Fluxo: linhas alternadas + wrap
    fluxo_row_colors = [FASE_PRE, CINZA_CLR, FASE_DUR, rgb("FFF9E6"), FASE_POS]
    for ri, cor in enumerate(fluxo_row_colors):
        row_idx = ri + 1
        requests.append(repeat_cell(
            sheet_fluxo, row_idx, row_idx + 1, 0, 5,
            cell_format(bg=cor, wrap="WRAP", valign="MIDDLE"),
            "userEnteredFormat(backgroundColor,wrapStrategy,verticalAlignment)"
        ))
        # Largura col A (dia)
    requests.append(set_col_width(sheet_fluxo, 0, 110))
    for ci in range(1, 5):
        requests.append(set_col_width(sheet_fluxo, ci, 200))
    for ri in range(1, 6):
        requests.append(set_row_height(sheet_fluxo, ri, 60))

    # ── Enviar formatação
    sheets_svc.spreadsheets().batchUpdate(
        spreadsheetId=ss_id,
        body={"requests": requests},
    ).execute()
    print("[sheets] Formatação aplicada.")

    url = f"https://docs.google.com/spreadsheets/d/{ss_id}/edit"
    print(f"\n[sheets] ✅ Planilha criada com sucesso!")
    print(f"[sheets] URL: {url}")
    return url


if __name__ == "__main__":
    main()
