#!/usr/bin/env python3
"""
create_planilha_v2_133.py
Nova planilha organizada — Projeto 133 Ecoarte Vibra 2026 (Manaus).

3 abas:
  1. Comunicacao Digital   — Email (7) + WhatsApp (4) + Redes Sociais (15)
  2. Assessoria + Midia Kit — Assessoria (12) + Midia Kit (10) + Mailing Manaus (22)
  3. Pecas do Evento        — A-H: 39 itens fisicos + producao
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "gws"))
from gws_auth import get_credentials
from googleapiclient.discovery import build

DRIVE_FOLDER = "1rHKvCogQ4pczO8JHqeYTmYUoTTaYMex0"
REF_BASE = "https://drive.google.com/drive/folders/"

# ── Cores ──────────────────────────────────────────────────────────────────────
def rgb(h):
    h = h.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return {"red": r/255, "green": g/255, "blue": b/255}

AZUL    = rgb("005F73")
VERDE   = rgb("128C7E")
ROSA    = rgb("D41A6A")
LARANJA = rgb("E86428")
ROXO    = rgb("6B2D7B")
GRAFITE = rgb("2D2D2D")
TEAL    = rgb("00A5B8")
BRANCO  = rgb("FFFFFF")
CINZA   = rgb("F4F4F4")
PRE_COR = rgb("E8F5E9")
DUR_COR = rgb("FFF3E0")
POS_COR = rgb("E3F2FD")
FASE_COR = {"Pre": PRE_COR, "Durante": DUR_COR, "Pos": POS_COR}

N_COMM    = 16
N_PECAS   = 11
N_MAILING = 9

COMM_HEADER = [
    "#", "Nome", "Fase", "Data Prevista", "Briefing", "Arte",
    "Aprov. Interna", "Aprov. Vibra", "Postagem", "Checagem",
    "Descricao", "Publico / Distribuicao", "Responsavel",
    "Link Briefing", "Link Arte", "Link Publicado"
]
PECAS_HEADER = [
    "Nome", "Categoria", "Status", "Responsavel", "Fornecedor",
    "Data Solicitacao", "Data Entrega", "Observacoes",
    "Link Arte", "Link Aprovado", "Link Ref 2019"
]
MAILING_HEADER = [
    "CIDADE", "VEICULO", "DATA DE ENVIO", "EMAIL", "TELEFONE",
    "TIPO DE MIDIA", "STATUS", "DATA DE PUBLICACAO", "LINK / NOTAS"
]

# ── Conteudo Aba 1 ─────────────────────────────────────────────────────────────
# (nome, fase, descricao, publico)
EMAIL_ITEMS = [
    ("Chamada para Participacao - Escolas", "Pre", "Email convite para diretores e professores das escolas parceiras", "Escolas / Gestores"),
    ("Chamada para Participacao - Comunidade", "Pre", "Email convite para comunidade e publico geral de Manaus", "Comunidade"),
    ("Confirmacao de Inscricao (automatico)", "Pre", "Email automatico disparado apos inscricao no evento", "Inscritos"),
    ("Lembrete - 1 semana antes", "Pre", "Lembrete com programacao e informacoes praticas do evento", "Inscritos"),
    ("Lembrete - Amanha comeca", "Pre", "Ultimo lembrete com horario, endereco e como chegar", "Inscritos"),
    ("Estamos ao vivo!", "Durante", "Email no dia D com link de transmissao e engajamento em tempo real", "Inscritos / Parceiros"),
    ("Melhores momentos + Obrigado", "Pos", "Agradecimento pos-evento com fotos, numeralha e proximo passo", "Todos"),
]
WHATSAPP_ITEMS = [
    ("Card Convite Escolas", "Pre", "Card visual de convite para grupos de professores e gestores", "Escolas"),
    ("Card Convite Comunidade", "Pre", "Card convite para grupos gerais e canais de comunidade de Manaus", "Comunidade"),
    ("Card Programacao do Dia", "Durante", "Card com programacao do dia D para compartilhamento rapido", "Geral"),
    ("Card Agradecimento + Numeralha", "Pos", "Card pos-evento com numero de participantes e agradecimento", "Geral"),
]
REDES_ITEMS = [
    ("Vem ai! - Stories Contagem Regressiva (Manaus)", "Pre", "Serie de stories diaria ate o Dia D com countdown", "Instagram"),
    ("Faltam 15 dias - Post + Story (Manaus)", "Pre", "Post de antecipacao 15 dias antes do evento", "Instagram"),
    ("Faltam 7 dias / Semana do Evento (Manaus)", "Pre", "Sequencia de posts na semana que antecede o evento", "Instagram"),
    ("Apresentacao: Vibra Energia - Post Patrocinador", "Pre", "Post apresentando a Vibra como patrocinadora do projeto", "Instagram"),
    ("Apresentacao Parceiros Institucionais - Carrossel", "Pre", "Carrossel apresentando cada parceiro institucional do projeto", "Instagram"),
    ("Vem ai! Ecoarte em Manaus (1)", "Pre", "Post de antecipacao com identidade visual do evento", "Instagram"),
    ("Vem ai! Ecoarte em Manaus (2) - Carrossel", "Pre", "Carrossel com destaques do que vai ter no evento", "Instagram"),
    ("O que esperar: tema Ecoarte - Carrossel educativo", "Pre", "Carrossel sobre educacao ambiental e os ODS do projeto", "Instagram"),
    ("Os ODS do Ecoarte - Carrossel", "Pre", "Serie sobre os Objetivos de Desenvolvimento Sustentavel", "Instagram"),
    ("LinkedIn: Vibra + Ecoarte (institucional)", "Pre", "Post institucional com foco em ESG e impacto social", "LinkedIn"),
    ("Comeca hoje! - Post + Story Abertura (Manaus)", "Durante", "Post de lancamento no Dia D em Manaus", "Instagram"),
    ("Programacao do Dia D Manaus - Post/Story", "Durante", "Post com grade horaria e atratividades do dia", "Instagram"),
    ("Cobertura ao vivo Manaus (Stories)", "Durante", "Stories de cobertura em tempo real durante o evento", "Instagram Stories"),
    ("Melhores Momentos Manaus - Carrossel", "Pos", "Carrossel com fotos e destaques do evento em Manaus", "Instagram"),
    ("Numeralha de Impacto Manaus - Post", "Pos", "Post com numeros finais: participantes, escolas, visitas", "Instagram"),
]

# ── Conteudo Aba 2 ─────────────────────────────────────────────────────────────
ASSESSORIA_ITEMS = [
    ("Save the Date / Nota de Imprensa", "Pre", "Nota curta de lancamento inicial para os veiculos de Manaus", "Imprensa Manaus"),
    ("Release Tematico: Educacao Ambiental + ODS", "Pre", "Release segmentado para editoria de educacao e meio ambiente", "Imprensa Manaus"),
    ("Release Tematico: Impacto Social + ESG", "Pre", "Release para veiculos de negocios e ESG corporativo", "Imprensa / Corp"),
    ("Release Tematico: Inovacao Educacional", "Pre", "Release para secretarias de educacao e imprensa especializada", "Secretarias / Ed"),
    ("Audio / Nota para Radio - Porta-Vozes", "Pre", "Nota ou audio de 30s adaptado para radios locais de Manaus", "Radios AM"),
    ("Release: Anuncio do Ecoarte Manaus", "Pre", "Release oficial de lancamento do evento em Manaus", "Imprensa AM"),
    ("Convite para Imprensa Manaus", "Pre", "Email-convite para jornalistas cobrirem o evento presencialmente", "Jornalistas AM"),
    ("Nota Exclusiva Manaus (1 veiculo local)", "Pre", "Nota exclusiva para veiculo de maior alcance (G1 AM ou A Critica)", "G1 / A Critica"),
    ("Esqueleto de Release Diario (Dia D)", "Durante", "Template de release com numeralha parcial para uso no dia D", "Imprensa Manaus"),
    ("Release do Dia D Manaus", "Durante", "Release completo com programacao e primeiros numeros do evento", "Imprensa AM"),
    ("Release Pos-Evento Manaus (com numeralha)", "Pos", "Release final com dados de impacto completos do evento Manaus", "Imprensa AM"),
    ("Clipping de Midia - Manaus", "Pos", "Compilacao de todas as publicacoes e mencoes na imprensa de AM", "Interno / Vibra"),
]
MIDIAKIT_ITEMS = [
    ("Tutorial de Uso do Midia Kit", "Pre", "Instrucoes de como usar cada peca do kit e quando postar", "Parceiros"),
    ("Video Institucional / Vinheta do Projeto (60s)", "Pre", "Video curto para parceiros e imprensa compartilharem nas redes", "Parceiros / Imprensa"),
    ("Fotos Oficiais + Pack de Imagens para Imprensa", "Pre", "Pack com fotos em alta resolucao aprovadas para publicacao", "Imprensa / Parceiros"),
    ("Release Oficial (versao para distribuicao no Kit)", "Pre", "Release formatado para inclusao no midia kit dos parceiros", "Parceiros"),
    ("Filtros e Frames para Stories (3 variacoes)", "Pre", "Filtros e molduras brandados do evento para stories", "Parceiros / Influ"),
    ("Pecas Instagram para Vibra compartilhar", "Pre", "3 posts prontos com tag @VibraEnergia para uso nas redes da Vibra", "Vibra"),
    ("Card LinkedIn para Vibra", "Pre", "Texto + arte para post collab no LinkedIn da Vibra Energia", "Vibra"),
    ("Texto sugerido para Vibra (redes)", "Pre", "Copy pronto para a Vibra usar nas proprias redes sociais", "Vibra"),
    ("Pecas Adicionais para Parceiros - Carrossel", "Pre", "Carrossel extra pronto para parceiros institucionais compartilharem", "Parceiros"),
    ("Logo co-assinatura NTICS + Vibra", "Pre", "Arquivo fonte com co-assinatura oficial do projeto", "Interno"),
]
MANAUS_MEDIA = [
    ("Manaus", "G1 Amazonas / TV Amazonas", "", "", "", "Site / TV", "A enviar", "", "Publicou 3x em 2019 - maior alcance AM"),
    ("Manaus", "A Critica", "", "", "", "Site + Jornal", "A enviar", "", "Publicou em 2019 - principal jornal de Manaus"),
    ("Manaus", "Amazonas Em Tempo", "", "", "", "Site", "A enviar", "", "Publicou em 2019"),
    ("Manaus", "Portal do Holanda", "", "", "", "Site", "A enviar", "", "Publicou 2x em 2019 - alto engajamento"),
    ("Manaus", "Portal Amazonia", "", "", "", "Site", "A enviar", "", "Publicou 3x em 2019"),
    ("Manaus", "D24Am / Diario do Amazonas", "", "", "", "Site", "A enviar", "", "Publicou em 2019"),
    ("Manaus", "Amazonas Noticias", "", "", "", "Site", "A enviar", "", "Publicou 2x em 2019"),
    ("Manaus", "CBN Amazonas", "", "", "", "Radio", "A enviar", "", "Contato em 2019"),
    ("Manaus", "Conexao Amazonas", "", "", "", "Site", "A enviar", "", "Publicou em 2019"),
    ("Manaus", "Amazonas Atual", "", "", "", "Site", "A enviar", "", "Publicou em 2019"),
    ("Manaus", "Blitz Amazonico", "", "", "", "Site", "A enviar", "", "Publicou em 2019"),
    ("Manaus", "Fato Amazonico", "", "", "", "Site", "A enviar", "", "Publicou 2x em 2019"),
    ("Manaus", "Diversidade Amazonica", "", "", "", "Site", "A enviar", "", "Publicou em 2019"),
    ("Manaus", "Manaus Online", "", "", "", "Site", "A enviar", "", "Publicou em 2019"),
    ("Manaus", "Portal do Generoso", "", "", "", "Site", "A enviar", "", "Publicou em 2019"),
    ("Manaus", "Plantao Diario", "", "", "", "Site", "A enviar", "", "Publicou em 2019"),
    ("Manaus", "Amazonas News", "", "", "", "Site", "A enviar", "", "Publicou em 2019"),
    ("Manaus", "Reporter Parintins", "", "", "", "Site", "A enviar", "", "Publicou em 2019"),
    ("Manaus", "Pagina 1 AM", "", "", "", "Site", "A enviar", "", "Publicou em 2019"),
    ("Manaus", "UFAM (Atlas ODS Amazonia)", "", "", "", "Site Institucional", "A enviar", "", "Parceiro em 2019 - alta credibilidade"),
    ("Manaus", "Prefeitura de Manaus (SEMED)", "", "", "", "Site + Newsletter", "A enviar", "", "Participou em 2019"),
    ("Manaus", "Virada Sustentavel Manaus", "", "", "", "Site + Redes Sociais", "A enviar", "", "Parceiro organizador em 2019 - reativar relacao"),
]

# ── Conteudo Aba 3 ─────────────────────────────────────────────────────────────
# (nome, categoria_ou_tipo, observacoes, ref_id_drive)
PECAS_DATA = [
    ("A. Identidade Visual", "header_sub", "", ""),
    ("Logomarca do Projeto", "Identidade Visual", "Arquivo fonte da logomarca Ecoarte Vibra", "1PsXpAcRi93eCB5-egV9BIrMn4s-S8E0R"),
    ("Logomarca Parcerias / Co-assinatura NTICS+Vibra", "Identidade Visual", "Versao com logo NTICS + Vibra co-assinados", "1k8yMrtwrC2KFn3Wzk6uTnj7aNYNiQh_7"),
    ("Assinatura de E-mail Institucional", "Identidade Visual", "Assinatura HTML para e-mails da equipe", "1yRSiHYSOdOe9Rne3ayJMduFwrXzO5sa6"),
    ("B. Sinalizacao do Container", "header_sub", "", ""),
    ("Envelopamento do Container (arte lateral/traseira)", "Sinalizacao", "Arte full-wrap para container 20pe ou 40pe", "1abp4KsXv5KTKjmEt-6-uJ7Jwh48HWqz5"),
    ("Lona Testeira Principal", "Sinalizacao", "Banner frontal de identidade do evento", "1xuChsLSc0YPtK33x-JuE5JpJH7NnPWcY"),
    ("Backdrop Entrada / Painel de Abertura", "Sinalizacao", "Painel de foto + boas-vindas na entrada do container", "16DzuDDz1aEouJwOCu9BvEK-3ZMIppvVD"),
    ("Totens de Sinalizacao", "Sinalizacao", "Totens direcional e tematicos internos", "1nzJOXZ7cmutGz7nyIncXuZonPaom2KFY"),
    ("Plaquinhas Internas", "Sinalizacao", "Identificacao de estacoes e areas internas", "1tvYdBRco3xlYdyTgqz_n-rY3LwryEMYN"),
    ("Wide Banner / Faixa Externa", "Sinalizacao", "Faixa horizontal para area externa do container", "1R6gHlaaNzrR4s9jhAfn7R_bilpML0_sR"),
    ("Banners ODS / Bandeiras Tematicas", "Sinalizacao", "Banners com os 17 ODS e tema do projeto", "11h31i0vnClKYLxMaABXuj9L2xeiZWxB0"),
    ("Banners Parceiros / Patrocinadores", "Sinalizacao", "Faixa ou painel com logos Vibra e parceiros", "1vX1aqRW3vp8YfTgHaVg8X-d85uFAz-mb"),
    ("Lona Area de Atividade (tema Ecoarte)", "Sinalizacao", "Grafica para parede de atividade educacional", "1kiEAVczWEL0NsrDtzVe1HpPCQgJRIATf"),
    ("C. Impressos do Evento", "header_sub", "", ""),
    ("Cartaz do Evento", "Impresso", "A2 ou A3, para escolas e pontos de divulgacao", "13akTex84PIrf1IZHAaTbHIf0T1u8_VRc"),
    ("Folder / Programacao do Dia", "Impresso", "Dobrado A4 com programacao completa do evento", "12iSCvcRwT3E5FjC78L9WH2d_yOIRUAJ8"),
    ("Mapa do Evento / Layout do Espaco", "Impresso", "Planta baixa do container com estacoes marcadas", "1ulavfp7JM3Wfju6GjlG0Uj9pQKArRRKJ"),
    ("Certificado de Participacao", "Impresso", "Certificado para estudantes e professores participantes", "1TkPKbCwAEvw8PM-DAXWt_f3HG6gpxdsv"),
    ("Imantado / Brinde Lembranca", "Impresso", "Imantado de geladeira com arte do projeto Ecoarte Vibra", "1THMqcDtuGmPNqeOrnB2ef4BemKgJdfEI"),
    ("D. Vestuario e Uniformes", "header_sub", "", ""),
    ("Camisetas da Equipe", "Vestuario", "Arte para silk/sublimacao para equipe NTICS", "1p39yoI5XIe13fYQPfndCnDVikhCSaYba"),
    ("Coletes de Identificacao", "Vestuario", "Colete colorido para monitores e equipe no evento", "1diPSiBIhqQZf_rvSL6xAQrJSHRyU7FiD"),
    ("E. Materiais Educacionais", "header_sub", "", ""),
    ("Kit Pedagogico / Material do Professor", "Mat. Educacional", "Apostila ou guia de atividades para docentes", "1yOboTs-axkTh4jk1AFLkc5n0iRW1gkYz"),
    ("Jogo Conhecendo os ODS (adaptado para Ecoarte)", "Mat. Educacional", "Jogo de tabuleiro/cartas adaptado do projeto 2019", "17N0qY-ig2CxuG5XXHNXANxFjXguk92xW"),
    ("Jogo Ecoarte / Atividade Interativa", "Mat. Educacional", "Dinamica ludica sobre educacao ambiental", "1XQVFnkO9ykS6JcWmRXEcDk-4rtn7yWzZ"),
    ("Rota dos ODS / Trilha Tematica do Container", "Mat. Educacional", "Percurso de sinalizacao por cada ODS dentro do evento", "1ndBAj1LVm95XYBO1X7y2UiexbQVNRlo5"),
    ("F. Brindes", "header_sub", "", ""),
    ("Copo / Brinde do Evento", "Brinde", "Copo personalizado com arte Ecoarte Vibra", "1niGvs5xqrQblNY6F1n6Wgqu4uClJ7uWG"),
    ("G. Institucional", "header_sub", "", ""),
    ("Apresentacao Institucional do Projeto", "Institucional", "Deck PPT/Google Slides para parceiros e secretarias", "1g3TobtJwgynYYFf2TiqeRc-LtjZ4w-0r"),
    ("Convite Oficial para Secretarias de Educacao", "Institucional", "Convite impresso ou PDF para gestores e secretarias", "1QwpBkDaGRr2jfaFEonjwZS4CM3KPHUTo"),
    ("Talks / Agenda de Palestras e Paineis", "Institucional", "Programacao de talks e grade de palestrantes do evento", "1sm1VrsiZZc7H5vwO4nCyngy9GGAzAlBN"),
    ("Relatorio de Impacto do Evento", "Institucional", "Relatorio pos-evento com numeros e fotos para Vibra", "15D2khnHu1Bs1MO_BBJhofWOi0F-gtCnP"),
    ("Plano de Midia", "Institucional", "Documento de estrategia e compra de midia do projeto", "1VM0IIgle-RDmLm-Dj9j-TS4qzb26dSE1"),
    ("H. Elementos de Producao", "header_sub", "", ""),
    ("Apresentacao / Deck Executivo do Projeto", "Producao", "Deck PPT/Slides para apresentar a parceiros e secretarias", ""),
    ("Video de Abertura (para telas no container)", "Producao", "Video institucional exibido continuamente durante o evento", ""),
    ("Kit de Onboarding da Equipe / Voluntarios", "Producao", "Material de boas-vindas, instrucoes e fluxos para a equipe", ""),
    ("PPT de Capacitacao da Equipe", "Producao", "Apresentacao de treinamento pre-evento para monitores", ""),
    ("Programacao Completa do Evento (doc oficial)", "Producao", "Documento com grade horaria e descricao de todas atividades", ""),
    ("Registro Fotografico Profissional", "Producao", "Cobertura por fotografo profissional no Dia D", ""),
    ("Registro em Video / Filmagem do Evento", "Producao", "Captacao de video para aftermovie e material pos-evento", ""),
    ("Clipping de Midia (monitoramento de mencoes)", "Producao", "Compilacao de publicacoes e mencoes na imprensa", ""),
    ("Relatorio Parcial (para Vibra - durante evento)", "Producao", "Relatorio intermediario com primeiros numeros para o patrocinador", ""),
    ("Relatorio Final de Impacto (com fotos e dados)", "Producao", "Documento final consolidando o evento de Manaus para Cota 2", ""),
]

# ── Helpers ────────────────────────────────────────────────────────────────────
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

def col_w(sid, ci, px):
    return {"updateDimensionProperties": {"range": {"sheetId": sid, "dimension": "COLUMNS",
        "startIndex": ci, "endIndex": ci+1}, "properties": {"pixelSize": px}, "fields": "pixelSize"}}

def row_h(sid, ri, px):
    return {"updateDimensionProperties": {"range": {"sheetId": sid, "dimension": "ROWS",
        "startIndex": ri, "endIndex": ri+1}, "properties": {"pixelSize": px}, "fields": "pixelSize"}}

def freeze(sid, rows=1, cols=1):
    return {"updateSheetProperties": {"properties": {"sheetId": sid,
        "gridProperties": {"frozenRowCount": rows, "frozenColumnCount": cols}},
        "fields": "gridProperties.frozenRowCount,gridProperties.frozenColumnCount"}}

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

def tab_color(sid, color):
    return {"updateSheetProperties": {"properties": {"sheetId": sid,
        "tabColor": color}, "fields": "tabColor"}}

FIELDS_FULL = "userEnteredFormat(backgroundColor,textFormat,wrapStrategy,horizontalAlignment,verticalAlignment)"
FIELDS_BG   = "userEnteredFormat(backgroundColor,verticalAlignment)"
FIELDS_WRAP = "userEnteredFormat(wrapStrategy)"

def comm_row(num, nome, fase, desc, publico):
    return [str(num), nome, fase, "", "", "", "", "", "", "", desc, publico, "", "", "", ""]

def pecas_row(nome, categoria, obs, ref_id):
    ref = f"{REF_BASE}{ref_id}" if ref_id else ""
    return [nome, categoria, "A briefar", "", "", "", "", obs, "", "", ref]


def main():
    creds = get_credentials()
    svc = build("sheets", "v4", credentials=creds)
    drv = build("drive", "v3", credentials=creds)

    # ── 1. Criar planilha com 3 abas ──────────────────────────────────────────
    result = svc.spreadsheets().create(body={
        "properties": {"title": "Plano de Comunicacao - Ecoarte Vibra Manaus 2026"},
        "sheets": [
            {"properties": {"title": "Comunicacao Digital", "index": 0,
                "gridProperties": {"rowCount": 60, "columnCount": N_COMM}}},
            {"properties": {"title": "Assessoria + Midia Kit", "index": 1,
                "gridProperties": {"rowCount": 70, "columnCount": N_COMM}}},
            {"properties": {"title": "Pecas do Evento", "index": 2,
                "gridProperties": {"rowCount": 60, "columnCount": N_PECAS}}},
        ]
    }).execute()

    ss_id = result["spreadsheetId"]
    sid0  = result["sheets"][0]["properties"]["sheetId"]
    sid1  = result["sheets"][1]["properties"]["sheetId"]
    sid2  = result["sheets"][2]["properties"]["sheetId"]
    print(f"Planilha criada: {ss_id}")
    print(f"SheetIds: {sid0}, {sid1}, {sid2}")

    # ── 2. Mover para pasta Drive ─────────────────────────────────────────────
    drv.files().update(
        fileId=ss_id,
        addParents=DRIVE_FOLDER,
        removeParents="root",
        fields="id, parents"
    ).execute()
    print(f"Movida para: {DRIVE_FOLDER}")

    # ── 3. Dados Aba 1: Comunicacao Digital ───────────────────────────────────
    rows1 = [COMM_HEADER]
    rows1.append(["EMAIL MARKETING"] + [""] * (N_COMM - 1))
    n = 1
    for item in EMAIL_ITEMS:
        rows1.append(comm_row(n, *item)); n += 1
    rows1.append(["WHATSAPP"] + [""] * (N_COMM - 1))
    for item in WHATSAPP_ITEMS:
        rows1.append(comm_row(n, *item)); n += 1
    rows1.append(["REDES SOCIAIS (Instagram + LinkedIn)"] + [""] * (N_COMM - 1))
    for item in REDES_ITEMS:
        rows1.append(comm_row(n, *item)); n += 1

    svc.spreadsheets().values().update(
        spreadsheetId=ss_id, range="'Comunicacao Digital'!A1",
        valueInputOption="USER_ENTERED", body={"values": rows1}
    ).execute()
    print(f"Aba 1: {len(rows1)} linhas")

    # ── 4. Dados Aba 2: Assessoria + Midia Kit ────────────────────────────────
    rows2 = [COMM_HEADER]
    rows2.append(["ASSESSORIA DE IMPRENSA"] + [""] * (N_COMM - 1))
    n2 = 1
    for item in ASSESSORIA_ITEMS:
        rows2.append(comm_row(n2, *item)); n2 += 1
    rows2.append(["MIDIA KIT VIBRA"] + [""] * (N_COMM - 1))
    for item in MIDIAKIT_ITEMS:
        rows2.append(comm_row(n2, *item)); n2 += 1
    rows2.append([""] * N_COMM)  # spacer
    rows2.append(["MAILING DE IMPRENSA - MANAUS AM"] + [""] * (N_COMM - 1))
    rows2.append(list(MAILING_HEADER) + [""] * (N_COMM - N_MAILING))
    for contact in MANAUS_MEDIA:
        rows2.append(list(contact) + [""] * (N_COMM - N_MAILING))

    svc.spreadsheets().values().update(
        spreadsheetId=ss_id, range="'Assessoria + Midia Kit'!A1",
        valueInputOption="USER_ENTERED", body={"values": rows2}
    ).execute()
    print(f"Aba 2: {len(rows2)} linhas")

    # ── 5. Dados Aba 3: Pecas do Evento ───────────────────────────────────────
    rows3 = [PECAS_HEADER]
    for entry in PECAS_DATA:
        nome, tipo, obs, ref_id = entry
        if tipo == "header_sub":
            rows3.append([nome] + [""] * (N_PECAS - 1))
        else:
            rows3.append(pecas_row(nome, tipo, obs, ref_id))

    svc.spreadsheets().values().update(
        spreadsheetId=ss_id, range="'Pecas do Evento'!A1",
        valueInputOption="USER_ENTERED", body={"values": rows3}
    ).execute()
    print(f"Aba 3: {len(rows3)} linhas")

    # ── 6. Formatacao ─────────────────────────────────────────────────────────
    fmt = []

    # Posicoes Aba 1
    em_sec  = 1
    em_s    = 2
    em_e    = em_s + len(EMAIL_ITEMS)        # 9
    wa_sec  = em_e                            # 9
    wa_s    = wa_sec + 1                      # 10
    wa_e    = wa_s + len(WHATSAPP_ITEMS)      # 14
    rd_sec  = wa_e                            # 14
    rd_s    = rd_sec + 1                      # 15
    rd_e    = rd_s + len(REDES_ITEMS)         # 30

    # === ABA 1 ===
    fmt += [
        rc(sid0, 0, 1, 0, N_COMM, cf(bg=GRAFITE, fg=BRANCO, bold=True, size=10,
            wrap="WRAP", halign="CENTER", valign="MIDDLE"), FIELDS_FULL),
        row_h(sid0, 0, 36),
        freeze(sid0, rows=1, cols=1),
        tab_color(sid0, AZUL),
        rc(sid0, em_sec, em_sec+1, 0, N_COMM,
            cf(bg=AZUL, fg=BRANCO, bold=True, size=11, halign="LEFT", valign="MIDDLE"), FIELDS_FULL),
        row_h(sid0, em_sec, 36),
        rc(sid0, wa_sec, wa_sec+1, 0, N_COMM,
            cf(bg=VERDE, fg=BRANCO, bold=True, size=11, halign="LEFT", valign="MIDDLE"), FIELDS_FULL),
        row_h(sid0, wa_sec, 36),
        rc(sid0, rd_sec, rd_sec+1, 0, N_COMM,
            cf(bg=ROSA, fg=BRANCO, bold=True, size=11, halign="LEFT", valign="MIDDLE"), FIELDS_FULL),
        row_h(sid0, rd_sec, 36),
    ]
    # Item colors
    for i, item in enumerate(EMAIL_ITEMS):
        ri = em_s + i
        fmt.append(rc(sid0, ri, ri+1, 0, N_COMM, cf(bg=FASE_COR.get(item[1], BRANCO), valign="MIDDLE"), FIELDS_BG))
    for i, item in enumerate(WHATSAPP_ITEMS):
        ri = wa_s + i
        fmt.append(rc(sid0, ri, ri+1, 0, N_COMM, cf(bg=FASE_COR.get(item[1], BRANCO), valign="MIDDLE"), FIELDS_BG))
    for i, item in enumerate(REDES_ITEMS):
        ri = rd_s + i
        fmt.append(rc(sid0, ri, ri+1, 0, N_COMM, cf(bg=FASE_COR.get(item[1], BRANCO), valign="MIDDLE"), FIELDS_BG))
    # Checkboxes cols 4-9
    fmt += [
        checkbox(sid0, em_s, em_e, 4, 10),
        checkbox(sid0, wa_s, wa_e, 4, 10),
        checkbox(sid0, rd_s, rd_e, 4, 10),
    ]
    # Dropdowns Fase
    fmt += [
        dropdown(sid0, em_s, em_e, 2, 3, ["Pre", "Durante", "Pos"]),
        dropdown(sid0, wa_s, wa_e, 2, 3, ["Pre", "Durante", "Pos"]),
        dropdown(sid0, rd_s, rd_e, 2, 3, ["Pre", "Durante", "Pos"]),
    ]
    # Wrap Nome(1) e Descricao(10)
    fmt += [
        rc(sid0, 1, rd_e, 1, 2, cf(wrap="WRAP"), FIELDS_WRAP),
        rc(sid0, 1, rd_e, 10, 11, cf(wrap="WRAP"), FIELDS_WRAP),
    ]
    # Larguras
    for ci, w in enumerate([30, 250, 70, 90, 60, 60, 60, 60, 60, 60, 200, 150, 100, 130, 130, 130]):
        fmt.append(col_w(sid0, ci, w))

    # Posicoes Aba 2
    as_sec = 1
    as_s   = 2
    as_e   = as_s + len(ASSESSORIA_ITEMS)    # 14
    mk_sec = as_e                             # 14
    mk_s   = mk_sec + 1                       # 15
    mk_e   = mk_s + len(MIDIAKIT_ITEMS)      # 25
    spacer = mk_e                             # 25
    ml_ttl = spacer + 1                       # 26
    ml_hdr = ml_ttl + 1                       # 27
    ml_s   = ml_hdr + 1                       # 28
    ml_e   = ml_s + len(MANAUS_MEDIA)         # 50

    # === ABA 2 ===
    fmt += [
        rc(sid1, 0, 1, 0, N_COMM, cf(bg=GRAFITE, fg=BRANCO, bold=True, size=10,
            wrap="WRAP", halign="CENTER", valign="MIDDLE"), FIELDS_FULL),
        row_h(sid1, 0, 36),
        freeze(sid1, rows=1, cols=1),
        tab_color(sid1, LARANJA),
        rc(sid1, as_sec, as_sec+1, 0, N_COMM,
            cf(bg=LARANJA, fg=BRANCO, bold=True, size=11, halign="LEFT", valign="MIDDLE"), FIELDS_FULL),
        row_h(sid1, as_sec, 36),
        rc(sid1, mk_sec, mk_sec+1, 0, N_COMM,
            cf(bg=ROXO, fg=BRANCO, bold=True, size=11, halign="LEFT", valign="MIDDLE"), FIELDS_FULL),
        row_h(sid1, mk_sec, 36),
    ]
    for i, item in enumerate(ASSESSORIA_ITEMS):
        ri = as_s + i
        fmt.append(rc(sid1, ri, ri+1, 0, N_COMM, cf(bg=FASE_COR.get(item[1], BRANCO), valign="MIDDLE"), FIELDS_BG))
    for i, item in enumerate(MIDIAKIT_ITEMS):
        ri = mk_s + i
        fmt.append(rc(sid1, ri, ri+1, 0, N_COMM, cf(bg=FASE_COR.get(item[1], BRANCO), valign="MIDDLE"), FIELDS_BG))
    fmt += [
        checkbox(sid1, as_s, as_e, 4, 10),
        checkbox(sid1, mk_s, mk_e, 4, 10),
        dropdown(sid1, as_s, as_e, 2, 3, ["Pre", "Durante", "Pos"]),
        dropdown(sid1, mk_s, mk_e, 2, 3, ["Pre", "Durante", "Pos"]),
        rc(sid1, 1, mk_e, 1, 2, cf(wrap="WRAP"), FIELDS_WRAP),
        rc(sid1, 1, mk_e, 10, 11, cf(wrap="WRAP"), FIELDS_WRAP),
    ]
    # Mailing section
    fmt += [
        rc(sid1, ml_ttl, ml_ttl+1, 0, N_COMM,
            cf(bg=GRAFITE, fg=BRANCO, bold=True, size=11, halign="LEFT", valign="MIDDLE"), FIELDS_FULL),
        row_h(sid1, ml_ttl, 36),
        rc(sid1, ml_hdr, ml_hdr+1, 0, N_MAILING,
            cf(bg=AZUL, fg=BRANCO, bold=True, size=10, halign="CENTER", valign="MIDDLE"), FIELDS_FULL),
        row_h(sid1, ml_hdr, 32),
    ]
    for i in range(len(MANAUS_MEDIA)):
        ri = ml_s + i
        bg = CINZA if (i % 2 == 0) else BRANCO
        fmt.append(rc(sid1, ri, ri+1, 0, N_MAILING, cf(bg=bg, valign="MIDDLE"), FIELDS_BG))
    fmt += [
        dropdown(sid1, ml_s, ml_e, 6, 7, ["A enviar", "Enviado", "Em andamento", "Publicado", "Sem retorno", "Nao aplicavel"]),
        dropdown(sid1, ml_s, ml_e, 5, 6, ["Site", "TV", "Radio", "Jornal", "Revista", "Newsletter", "Portal", "Outro"]),
        rc(sid1, ml_s, ml_e, 1, 2, cf(wrap="WRAP"), FIELDS_WRAP),
        rc(sid1, ml_s, ml_e, 8, 9, cf(wrap="WRAP"), FIELDS_WRAP),
    ]
    for ci, w in enumerate([30, 250, 70, 90, 60, 60, 60, 60, 60, 60, 200, 150, 100, 130, 130, 130]):
        fmt.append(col_w(sid1, ci, w))

    # === ABA 3 ===
    fmt += [
        rc(sid2, 0, 1, 0, N_PECAS, cf(bg=GRAFITE, fg=BRANCO, bold=True, size=10,
            wrap="WRAP", halign="CENTER", valign="MIDDLE"), FIELDS_FULL),
        row_h(sid2, 0, 36),
        freeze(sid2, rows=1, cols=1),
        tab_color(sid2, TEAL),
    ]
    ri = 1
    item_cnt = 0
    for entry in PECAS_DATA:
        if entry[1] == "header_sub":
            fmt += [
                rc(sid2, ri, ri+1, 0, N_PECAS,
                    cf(bg=TEAL, fg=BRANCO, bold=True, size=10, halign="LEFT", valign="MIDDLE"), FIELDS_FULL),
                row_h(sid2, ri, 32),
            ]
        else:
            bg = CINZA if (item_cnt % 2 == 0) else BRANCO
            fmt.append(rc(sid2, ri, ri+1, 0, N_PECAS, cf(bg=bg, valign="MIDDLE"), FIELDS_BG))
            item_cnt += 1
        ri += 1

    total3 = ri
    fmt += [
        dropdown(sid2, 1, total3, 2, 3, ["A briefar", "Em producao", "Em aprovacao", "Aprovado", "Produzido", "Entregue"]),
        rc(sid2, 1, total3, 0, 1, cf(wrap="WRAP"), FIELDS_WRAP),
        rc(sid2, 1, total3, 7, 8, cf(wrap="WRAP"), FIELDS_WRAP),
    ]
    for ci, w in enumerate([250, 120, 100, 100, 120, 90, 90, 200, 130, 130, 130]):
        fmt.append(col_w(sid2, ci, w))

    # Aplicar tudo
    svc.spreadsheets().batchUpdate(
        spreadsheetId=ss_id, body={"requests": fmt}
    ).execute()
    print(f"Formatacao aplicada ({len(fmt)} requests)")
    print(f"\nURL: https://docs.google.com/spreadsheets/d/{ss_id}/edit")


if __name__ == "__main__":
    main()
