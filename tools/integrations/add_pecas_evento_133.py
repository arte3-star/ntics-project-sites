#!/usr/bin/env python3
"""
add_pecas_evento_133.py
Adiciona secao "Pecas do Container / Evento" ao Sheet existente do Projeto 133.
Sheet: 1THxXD1Eus85T0T7j95QKzdHPFcXWTdTmwhhaWlAgIZo
Posicao: append apos linha 59 (header + 5 secoes + 54 itens)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "gws"))
from gws_auth import get_credentials
from googleapiclient.discovery import build

SS_ID = "1THxXD1Eus85T0T7j95QKzdHPFcXWTdTmwhhaWlAgIZo"
SHEET_ETAPAS = 0
START_ROW = 60  # 0-based: linha 61 na planilha (apos header + 5 secoes + 54 itens)

def rgb(hex_color):
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return {"red": r/255, "green": g/255, "blue": b/255}

TEAL    = rgb("00A5B8")
GRAFITE = rgb("2D2D2D")
BRANCO  = rgb("FFFFFF")
CINZA   = rgb("F4F4F4")

# Estrutura: ("tipo", "nome", "desc_ou_tipo", "cidade", "link_ref_id")
# tipo: "header_principal" | "header_sub" | "item"
SECAO_DATA = [
    # Header principal
    ("header_principal", "PECAS DO CONTAINER / EVENTO", "", "", ""),

    # A. Identidade Visual
    ("header_sub", "A. Identidade Visual", "", "", ""),
    ("item", "Logomarca do Projeto", "Arquivo fonte da logomarca Ecoarte Vibra", "Ambas", "1PsXpAcRi93eCB5-egV9BIrMn4s-S8E0R"),
    ("item", "Logomarca Parcerias / Co-assinatura NTICS+Vibra", "Versao com logo NTICS + Vibra co-assinados", "Ambas", "1k8yMrtwrC2KFn3Wzk6uTnj7aNYNiQh_7"),
    ("item", "Assinatura de E-mail Institucional", "Assinatura HTML para e-mails da equipe", "Ambas", "1yRSiHYSOdOe9Rne3ayJMduFwrXzO5sa6"),

    # B. Sinalizacao do Container
    ("header_sub", "B. Sinalizacao do Container", "", "", ""),
    ("item", "Envelopamento do Container (arte lateral/traseira)", "Arte full-wrap para container 20pe ou 40pe", "Ambas", "1abp4KsXv5KTKjmEt-6-uJ7Jwh48HWqz5"),
    ("item", "Lona Testeira Principal", "Banner frontal de identidade do evento", "Ambas", "1xuChsLSc0YPtK33x-JuE5JpJH7NnPWcY"),
    ("item", "Backdrop Entrada / Painel de Abertura", "Painel de foto + boas-vindas na entrada", "Ambas", "16DzuDDz1aEouJwOCu9BvEK-3ZMIppvVD"),
    ("item", "Totens de Sinalizacao", "Totens direcional e tematicos internos", "Ambas", "1nzJOXZ7cmutGz7nyIncXuZonPaom2KFY"),
    ("item", "Plaquinhas Internas", "Identificacao de estacoes e areas", "Ambas", "1tvYdBRco3xlYdyTgqz_n-rY3LwryEMYN"),
    ("item", "Wide Banner / Faixa Externa", "Faixa horizontal para area externa", "Ambas", "1R6gHlaaNzrR4s9jhAfn7R_bilpML0_sR"),
    ("item", "Banners ODS / Bandeiras Tematicas", "Banners com os 17 ODS e tema do projeto", "Ambas", "11h31i0vnClKYLxMaABXuj9L2xeiZWxB0"),
    ("item", "Banners Parceiros / Patrocinadores", "Faixa ou painel com logos Vibra e parceiros", "Ambas", "1vX1aqRW3vp8YfTgHaVg8X-d85uFAz-mb"),
    ("item", "Lona Area de Atividade (tema Ecoarte)", "Grafica para parede de atividade educacional", "Ambas", "1kiEAVczWEL0NsrDtzVe1HpPCQgJRIATf"),

    # C. Impressos do Evento
    ("header_sub", "C. Impressos do Evento", "", "", ""),
    ("item", "Cartaz do Evento", "A2 ou A3, para escolas e pontos de divulgacao", "Ambas", "13akTex84PIrf1IZHAaTbHIf0T1u8_VRc"),
    ("item", "Folder / Programacao do Dia", "Dobrado A4 com programacao completa", "Ambas", "12iSCvcRwT3E5FjC78L9WH2d_yOIRUAJ8"),
    ("item", "Mapa do Evento / Layout do Espaco", "Planta baixa do container com estacoes", "Ambas", "1ulavfp7JM3Wfju6GjlG0Uj9pQKArRRKJ"),
    ("item", "Certificado de Participacao", "Certificado para estudantes e professores", "Ambas", "1TkPKbCwAEvw8PM-DAXWt_f3HG6gpxdsv"),
    ("item", "Imantado / Brinde Lembranca", "Imantado de geladeira com arte do projeto", "Ambas", "1THMqcDtuGmPNqeOrnB2ef4BemKgJdfEI"),

    # D. Vestuario e Uniformes
    ("header_sub", "D. Vestuario e Uniformes", "", "", ""),
    ("item", "Camisetas da Equipe", "Arte para silk/sublimacao — equipe NTICS", "Ambas", "1p39yoI5XIe13fYQPfndCnDVikhCSaYba"),
    ("item", "Coletes de Identificacao", "Colete colorido para monitores/equipe", "Ambas", "1diPSiBIhqQZf_rvSL6xAQrJSHRyU7FiD"),

    # E. Materiais Educacionais
    ("header_sub", "E. Materiais Educacionais", "", "", ""),
    ("item", "Kit Pedagogico / Material do Professor", "Apostila ou guia de atividades para docentes", "Ambas", "1yOboTs-axkTh4jk1AFLkc5n0iRW1gkYz"),
    ("item", "Jogo Conhecendo os ODS (adaptado para Ecoarte)", "Jogo de tabuleiro/cartas com ODS do projeto", "Ambas", "17N0qY-ig2CxuG5XXHNXANxFjXguk92xW"),
    ("item", "Jogo Ecoarte / Atividade Interativa", "Dinamica ludica sobre educacao ambiental", "Ambas", "1XQVFnkO9ykS6JcWmRXEcDk-4rtn7yWzZ"),
    ("item", "Rota dos ODS / Trilha Tematica do Container", "Percurso sinalizacao por cada ODS no evento", "Ambas", "1ndBAj1LVm95XYBO1X7y2UiexbQVNRlo5"),

    # F. Brindes
    ("header_sub", "F. Brindes", "", "", ""),
    ("item", "Copo / Brinde do Evento", "Copo personalizado com arte Ecoarte Vibra", "Ambas", "1niGvs5xqrQblNY6F1n6Wgqu4uClJ7uWG"),

    # G. Institucional
    ("header_sub", "G. Institucional", "", "", ""),
    ("item", "Apresentacao Institucional do Projeto", "Deck PPT/Google Slides para parceiros e sec", "Ambas", "1g3TobtJwgynYYFf2TiqeRc-LtjZ4w-0r"),
    ("item", "Convite Oficial para Secretarias de Educacao", "Convite impresso ou PDF para gestores", "Ambas", "1QwpBkDaGRr2jfaFEonjwZS4CM3KPHUTo"),
    ("item", "Talks / Agenda de Palestras e Paineis", "Programacao de talks e grade de palestrantes", "Ambas", "1sm1VrsiZZc7H5vwO4nCyngy9GGAzAlBN"),
    ("item", "Relatorio de Impacto do Evento", "Relatorio pos-evento com numeros e fotos", "Ambas", "15D2khnHu1Bs1MO_BBJhofWOi0F-gtCnP"),
    ("item", "Plano de Midia", "Documento de estrategia e compra de midia", "Ambas", "1VM0IIgle-RDmLm-Dj9j-TS4qzb26dSE1"),
]

REF_BASE = "https://drive.google.com/drive/folders/"

def build_rows():
    """Converte SECAO_DATA em linhas para values.append (18 colunas)."""
    rows = []
    for entry in SECAO_DATA:
        tipo = entry[0]
        nome = entry[1]
        desc = entry[2]
        cidade = entry[3]
        ref_id = entry[4]
        if tipo in ("header_principal", "header_sub"):
            rows.append([nome] + [""] * 17)
        else:
            ref_link = f"{REF_BASE}{ref_id}" if ref_id else ""
            # colunas: Nome | DataBriefing | BriefingEnv | Arte | AprovInterna |
            #          AprovVibra | Postagem | Checagem | Descricao | Publico |
            #          Cidade | Fluxo | Notas | RespAprov | RespPostagem |
            #          LinkBriefing | LinkArte | LinkRef2019
            rows.append([nome, "", "", "", "", "", "", "", desc, "", cidade,
                         "", "", "", "", "", "", ref_link])
    return rows

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

FIELDS_FULL = "userEnteredFormat(backgroundColor,textFormat,wrapStrategy,horizontalAlignment,verticalAlignment)"
FIELDS_BG   = "userEnteredFormat(backgroundColor,verticalAlignment)"
N_COLS = 18

def main():
    creds = get_credentials()
    svc = build("sheets", "v4", credentials=creds)

    rows = build_rows()

    # 1) Append dados
    svc.spreadsheets().values().append(
        spreadsheetId=SS_ID,
        range="Etapas de Produção!A1",
        valueInputOption="USER_ENTERED",
        insertDataOption="INSERT_ROWS",
        body={"values": rows}
    ).execute()

    print(f"Dados inseridos: {len(rows)} linhas")

    # 2) Formatacao — primeiro descobrir o indice real da primeira linha appended
    # As linhas comecam em START_ROW (0-based) = linha 61 da planilha (1-based)
    row_idx = START_ROW
    reqs = []

    for entry in SECAO_DATA:
        tipo = entry[0]
        if tipo == "header_principal":
            reqs.append(rc(SHEET_ETAPAS, row_idx, row_idx+1, 0, N_COLS,
                cf(bg=GRAFITE, fg=BRANCO, bold=True, size=11,
                   halign="LEFT", valign="MIDDLE"), FIELDS_FULL))
            reqs.append(row_h(SHEET_ETAPAS, row_idx, 36))
        elif tipo == "header_sub":
            reqs.append(rc(SHEET_ETAPAS, row_idx, row_idx+1, 0, N_COLS,
                cf(bg=TEAL, fg=BRANCO, bold=True, size=10,
                   halign="LEFT", valign="MIDDLE"), FIELDS_FULL))
            reqs.append(row_h(SHEET_ETAPAS, row_idx, 32))
        else:
            # Alternancia BRANCO / CINZA baseada em posicao relativa
            bg = CINZA if (row_idx % 2 == 0) else BRANCO
            reqs.append(rc(SHEET_ETAPAS, row_idx, row_idx+1, 0, N_COLS,
                cf(bg=bg, valign="MIDDLE"), FIELDS_BG))
        row_idx += 1

    svc.spreadsheets().batchUpdate(
        spreadsheetId=SS_ID,
        body={"requests": reqs}
    ).execute()

    print(f"Formatacao aplicada em {row_idx - START_ROW} linhas")
    print(f"URL: https://docs.google.com/spreadsheets/d/{SS_ID}/edit")

if __name__ == "__main__":
    main()
