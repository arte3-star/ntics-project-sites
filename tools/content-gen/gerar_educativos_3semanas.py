"""
gerar_educativos_3semanas.py
Gera carrosseis educativos para S03, S04, S05 via Leonardo AI.
8 cards por semana (capa + 5 conteudo + metodo + CTA).

📚 Ref: workflows/marketing/referencia/leonardo_ai_core.md — consulte em caso de erro ou
dúvida sobre payloads, pipeline híbrido, erros conhecidos.

PADRÃO VISUAL DEFINITIVO (desde S03):
- Todos os cards 01–07 usam abordagem HÍBRIDA 2 passos:
    Passo 1: Leonardo gera foto de fundo limpa (sem texto) — build_bg_photo_prompt(cena)
    Pillow:  aplica película teal ~62% opacidade — aplicar_pelicula_teal()
    Upload:  foto filtrada como init_image — upload_init_image()
    Passo 2: Leonardo gera card final com texto por cima — init_strength=0.70
- Card 08 CTA: Leonardo puro + logo NTICS colado via Pillow — apply_logo_cta()

REGRAS DE PROMPT:
- Gradiente: sempre "from LEFT to RIGHT: green on the far left, transitioning to teal,
  then pink, ending with orange on the far right" — nunca só listar cores
- Números decimais: usar ponto no prompt (11.4M, 9.32) — vírgula vira espaço no render
- Textos fonte: sem travessão (—), sem ponto final, sem palavras inglesas isoladas
- Fotos de fundo: sempre incluir _NO_TEXT ao final do prompt

CAMPO "cena" NO DICIONÁRIO SEMANAS:
- Todo card de conteúdo (02-06) deve ter campo "cena" com descrição da foto de fundo
- "metodo_cena" para o card 07
- "capa_cena" para o card 01
- Evitar mencionar telas, monitores, TVs, projetores em qualquer cena
"""
import os, sys, time
from io import BytesIO
from pathlib import Path
import requests
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

load_dotenv()
LEO_KEY = os.getenv("LEONARDO_API_KEY")
BASE_V2 = "https://cloud.leonardo.ai/api/rest/v2"
BASE_V1 = "https://cloud.leonardo.ai/api/rest/v1"

# ─── Conteúdo dos carrosseis ─────────────────────────────────────────────────

SEMANAS = {
    "S01": {
        "tema": "Responsabilidade Social que gera resultado de negócio",
        "cta_pergunta": "Pronto para transformar propósito em resultado?",
        "capa_cena": "bright modern corporate office interior with large windows and natural light, printed documents and reports on a wooden desk in the foreground, warm professional atmosphere, no people no screens no monitors",
        "capa_subtitulo": "Como empresas líderes usam a RS como vantagem competitiva",
        "metodo_frase": "24 ANOS TRANSFORMANDO PROPÓSITO EM RESULTADO",
        "metodo_cena": "diverse professionals in a collaborative meeting reviewing printed project results and impact data, bright modern office, authentic candid moment, no screens no monitors",
        "metodo_metricas": [
            ("1.060+", "projetos executados"),
            ("11.4M", "pessoas impactadas"),
            ("9.32", "nota média satisfação"),
            ("88", "NPS dos clientes"),
        ],
        "cards": [
            {
                "slug": "02-esg",
                "titulo": "FORTALECE O RATING ESG",
                "texto": "Empresas com programas estruturados de RS sobem nos rankings ESG. Isso atrai investidores, reduz custo de capital e abre portas em cadeias de fornecimento cada vez mais exigentes",
                "frase": "ESG não é relatório. É reputação que gera negócio",
                "cena": "business professional reviewing printed ESG rating documents on a conference table, focused and confident, warm office light, no screens no monitors",
            },
            {
                "slug": "03-talentos",
                "titulo": "ATRAI E RETÉM TALENTOS",
                "texto": "Profissionais de alto nível escolhem empresas com propósito. Uma estratégia de RS sólida reduz rotatividade, fortalece a cultura interna e se torna argumento de recrutamento",
                "frase": "Propósito é o melhor benefício que uma empresa pode oferecer",
                "cena": "young diverse professionals in a casual team meeting, engaged and motivated, bright collaborative workspace, natural light, no screens no monitors",
            },
            {
                "slug": "04-clientes",
                "titulo": "ABRE PORTAS COM CLIENTES",
                "texto": "Grandes empresas exigem postura ESG de seus fornecedores. Ter um programa de RS documentado e auditável vira critério de homologação em processos comerciais cada vez mais frequentes",
                "frase": "Quem documenta impacto vende mais",
                "cena": "two professionals shaking hands after a successful business meeting, printed documents on the table, professional warm atmosphere, no screens no monitors",
            },
            {
                "slug": "05-incentivo",
                "titulo": "INCENTIVO FISCAL QUE JÁ EXISTE",
                "texto": "Leis de incentivo como a Rouanet, Lei do Esporte e FIA permitem redirecionar imposto já devido para projetos de impacto. O recurso existe. A diferença é onde ele vai",
                "frase": "Seu imposto pode transformar comunidades",
                "cena": "accountant or financial professional reviewing printed tax incentive documents at a desk, focused expression, clean professional office, natural light, no screens no monitors",
            },
            {
                "slug": "06-mensuravel",
                "titulo": "IMPACTO MENSURÁVEL E AUDITÁVEL",
                "texto": "RS sem indicador não tem credibilidade. Programas com metodologia GRI e ISO 9001 geram dados auditáveis que sustentam relatórios de sustentabilidade",
                "frase": "Dado verificável é convite a investir de novo",
                "cena": "analyst presenting printed impact measurement charts to colleagues around a table, professional and engaged atmosphere, warm natural light, no screens no monitors",
            },
        ],
    },
    "S02": {
        "tema": "Educação como motor",
        "cta_pergunta": "Pronto para transformar investimento em educação mensurável?",
        "capa_cena": "education program manager reviewing curriculum materials at a large wooden desk in a bright modern office, printed documents and binders in foreground, warm professional atmosphere, no screens no monitors no projectors",
        "capa_subtitulo": "Por que empresas que investem em educação constroem mercados mais fortes",
        "metodo_frase": "24 ANOS CONSTRUINDO EDUCAÇÃO COM IMPACTO REAL",
        "metodo_cena": "NTICS social program managers collaborating in a warm modern workspace, reviewing educational program results together, authentic professional candid moment, no screens no monitors",
        "metodo_metricas": [
            ("201 mil", "alunos impactados"),
            ("10.300", "professores capacitados"),
            ("1.060+", "projetos executados"),
            ("88", "NPS dos clientes"),
        ],
        "cards": [
            {
                "slug": "02-territorios",
                "titulo": "TERRITÓRIOS PRÓSPEROS INVESTEM EM EDUCAÇÃO",
                "texto": "As regiões com maior desenvolvimento têm algo em comum: empresas que tratam educação como investimento, não custo. Qualificação local gera mercado consumidor mais forte e cadeia de fornecimento mais robusta",
                "frase": "Empresa que investe em educação investe no próprio mercado",
                "cena": "wide shot of a thriving Brazilian neighborhood with a public school building prominent in the landscape, community life visible around the school, warm golden afternoon light, no screens",
            },
            {
                "slug": "03-permanencia",
                "titulo": "PERMANÊNCIA ESCOLAR: O INDICADOR",
                "texto": "Programas com foco em competências humanas e projeto de vida reduzem a evasão escolar. Aluno que permanece aprende mais, sai mais preparado e contribui mais para a comunidade e para o mercado de trabalho",
                "frase": "Evasão zero é o indicador que muda tudo",
                "cena": "business professional writing in a notebook at a bright modern office desk, reviewing printed documents, focused and motivated expression, warm natural light, no screens no monitors",
            },
            {
                "slug": "04-mao-de-obra",
                "titulo": "MÃO DE OBRA QUALIFICADA NO TERRITÓRIO",
                "texto": "Quando a empresa investe na educação da comunidade local, constrói o talento que precisará amanhã. Não é filantropia. É estratégia de longo prazo com retorno verificável em produtividade e engajamento",
                "frase": "O talento de amanhã está na escola de hoje",
                "cena": "young adults in a vocational or skills training program, practicing hands-on activities in a workshop or classroom, bright environment, focused and motivated expressions, no screens",
            },
            {
                "slug": "05-incentivo",
                "titulo": "LEI DE INCENTIVO PARA EDUCAÇÃO",
                "texto": "Programas educacionais via FIA, Lei Rouanet e outras leis de incentivo permitem redirecionar tributos já devidos para transformação social real nas escolas públicas. O recurso já existe. A diferença é onde ele vai",
                "frase": "Seu imposto pode qualificar uma comunidade inteira",
                "cena": "program coordinator presenting printed educational initiative documents to corporate partners around a conference table, professional B2B meeting, warm office light, no screens no monitors",
            },
            {
                "slug": "06-indicadores",
                "titulo": "IMPACTO MENSURÁVEL EM EDUCAÇÃO",
                "texto": "Programas com metodologia estruturada entregam indicadores reais: aprovação, frequência, competências desenvolvidas, projeto de vida construído. Dados auditáveis que sustentam relatórios de sustentabilidade e justificam o investimento",
                "frase": "Dado educacional é prova de impacto real",
                "cena": "data analyst reviewing printed charts and measurement reports on a conference table, multiple documents spread around, professional bright office, warm natural light, no screens no monitors",
            },
        ],
    },
    "S03": {
        "tema": "5 sinais de maturidade em Responsabilidade Social",
        "cta_pergunta": "Quer aplicar esses 5 sinais na sua empresa?",
        # NOTA: evitar mencionar telas, monitores, projeções, TVs — sempre ambientes naturais com pessoas
        "capa_cena": "a professional team of diverse people collaborating around a conference table, planning and reviewing documents together, relaxed candid office environment with large windows and natural light",
        "capa_subtitulo": "Como identificar se sua empresa está no caminho certo",
        "metodo_frase": "24 ANOS DE MÉTODO QUE ENTREGA",
        "metodo_cena": "experienced social impact professionals collaborating in a warm modern workspace, reviewing results together, authentic candid moment, no screens no monitors",
        "metodo_metricas": [
            ("1.060+", "projetos executados"),
            ("11,4M", "pessoas impactadas"),
            ("9,32", "nota média satisfação"),
            ("88", "NPS dos clientes"),
        ],
        "cards": [
            {
                "slug": "02-programa",
                "titulo": "TRATA COMO PROGRAMA, NÃO EVENTO",
                "icone": "a calendar with recurring circular arrows showing continuity",
                "texto": "Empresas maduras não fazem ações pontuais. Elas constroem programas contínuos com começo, meio e legado. Cada ciclo aprende com o anterior e aprofunda o impacto.",
                "frase": "Ação pontual passa. Programa transforma.",
                "cena": "diverse professional team in a recurring planning meeting, sticky notes and printed roadmaps on a table, collaborative atmosphere, natural office light, no screens no monitors",
            },
            {
                "slug": "03-envolve",
                "titulo": "ENVOLVE QUEM SERÁ IMPACTADO",
                "icone": "two hands working together building something, symbol of collaboration",
                "texto": "A comunidade é parceira desde o primeiro dia. Não um objeto do projeto, mas agente de mudança. Quando as pessoas participam da construção, o resultado é delas",
                "frase": "Co-criar é respeitar",
                "cena": "diverse community members sitting together around a table reviewing printed documents and plans, bright airy community space, candid authentic moment, no screens no monitors",
            },
            {
                "slug": "04-mede",
                "titulo": "MEDE O QUE REALMENTE IMPORTA",
                "icone": "a gauge or compass pointing to the word impact, measurement symbol",
                "texto": "Número de participantes é só o começo. O que muda na vida das pessoas? O que elas fazem diferente depois? Essas perguntas guiam os indicadores que importam",
                "frase": "Indicadores de transformação, não de presença",
                "cena": "researcher or analyst reviewing printed impact reports and data documents on a desk, close-up candid shot, warm natural light, no screens no monitors",
            },
            {
                "slug": "05-comunica",
                "titulo": "COMUNICA COM TRANSPARÊNCIA",
                "icone": "a megaphone with data charts floating around it, representing clear communication",
                "texto": "Resultados reais são compartilhados — os bons e os aprendizados. Transparência não é vulnerabilidade. É autoridade. Quem compartilha dados, constrói confiança.",
                "frase": "Quem tem dados, tem credibilidade.",
                "cena": "two professionals in a bright modern office reviewing printed reports together, relaxed and focused, natural window light, no screens no monitors no laptops",
            },
            {
                "slug": "06-conecta",
                "titulo": "CONECTA AO NEGÓCIO",
                "icone": "interlocking gears with a green leaf growing from the center, ESG and business",
                "texto": "Responsabilidade Social madura faz parte da estratégia. Melhora o rating ESG, fortalece a marca e cria valor para o negócio. Propósito e resultado andam juntos",
                "frase": "RS não é custo. É diferencial competitivo",
                "cena": "business executives in a boardroom discussion, reviewing printed strategic documents, confident collaborative atmosphere, natural light through large windows, no screens no monitors",
            },
        ],
    },
    "S04": {
        "tema": "O poder do territorio",
        "cta_pergunta": "Pronto para construir projetos que pertencem ao territorio?",
        "capa_cena": "a group of community members and corporate professionals sitting in a circle in an open-air space in a Brazilian neighborhood, co-creating together with maps and materials spread around",
        "capa_subtitulo": "Por que o lugar e o ponto de partida do impacto real",
        "metodo_frase": "24 ANOS CONSTRUINDO COM OS TERRITORIOS",
        "metodo_cena": "NTICS team members and community partners working together outdoors in Brazilian territory, authentic documentary moment, warm golden light, no screens",
        "metodo_metricas": [
            ("165+", "cidades atendidas"),
            ("868", "cidades Conhecendo ODS"),
            ("1.060+", "projetos executados"),
            ("11,4M", "pessoas impactadas"),
        ],
        "cards": [
            {
                "slug": "02-diagnostico",
                "titulo": "DIAGNOSTICO TERRITORIAL",
                "icone": "a map with pins and a magnifying glass, exploring territory",
                "texto": "Antes de qualquer acao, entender o contexto: quem vive aqui, o que ja existe, quais sao as necessidades reais. O diagnostico e a fundacao de tudo.",
                "frase": "Nao se pode transformar o que nao se conhece.",
            },
            {
                "slug": "03-escuta",
                "titulo": "ESCUTA ATIVA",
                "icone": "a large ear with sound waves and a heart inside, representing deep listening",
                "texto": "Rodas de conversa, visitas, entrevistas com liderancas locais. A escuta ativa nao e protocolo — e o gesto que gera confianca e abre espaco para a mudanca real.",
                "frase": "Quem escuta, constroi junto.",
                "cena": "community leader listening attentively to neighborhood residents in an open-air gathering in a Brazilian community, authentic candid documentary moment, no screens",
            },
            {
                "slug": "04-cocriacao",
                "titulo": "COCRIACAO COM A COMUNIDADE",
                "icone": "multiple hands placing puzzle pieces together, building collaboratively",
                "texto": "A comunidade nao e publico-alvo do projeto. Ela e coautora. Quando as pessoas participam da construcao, o projeto tem raizes — e as raizes dao sustentabilidade.",
                "frase": "Parceria real. Impacto real.",
            },
            {
                "slug": "05-legitimidade",
                "titulo": "LEGITIMIDADE QUE DURA",
                "icone": "a strong tree with deep roots growing from the ground, symbol of durability",
                "texto": "Projetos territoriais geram engajamento que nao precisa de incentivo externo. A propria comunidade se torna guardia do projeto — porque ele tambem e dela.",
                "frase": "Pertencimento e o maior indicador de sucesso.",
                "cena": "proud community members standing together in front of their community space, genuine belonging and joy, warm natural light, candid authentic portrait, no screens",
            },
            {
                "slug": "06-resultados",
                "titulo": "RESULTADOS MAIS PROFUNDOS",
                "icone": "a upward arrow growing from soil into a plant, representing sustainable growth",
                "texto": "Quando o projeto nasce do territorio, o impacto e mais duradouro. A transformacao nao termina com o financiamento — ela continua sendo cultivada pela propria comunidade.",
                "frase": "Impacto real comeca quando voce conhece o lugar onde esta.",
            },
        ],
    },
    "S05": {
        "tema": "Impacto que multiplica",
        "cta_pergunta": "Seu projeto tem uma historia que merece ser contada?",
        "capa_cena": "a documentary filmmaker interviewing a smiling woman in a community garden who is telling her story of transformation, golden hour light, authentic candid moment",
        "capa_subtitulo": "Por que projetos bem comunicados geram mais valor",
        "metodo_frase": "COMO O IMPACTO NTICS SE MULTIPLICA",
        "metodo_cena": "diverse people from different communities whose lives were changed by social programs, warm authentic group moment, documentary style, no screens",
        "metodo_metricas": [
            ("326 mil", "pessoas diretas ODS"),
            ("1,19M", "impacto indireto"),
            ("868", "cidades alcancadas"),
            ("4x", "multiplicador de alcance"),
        ],
        "cards": [
            {
                "slug": "02-multiplicam",
                "titulo": "PROGRAMAS QUE SE MULTIPLICAM",
                "icone": "a single point of light dividing into many, cascade multiplication symbol",
                "texto": "Projetos que terminam deixam uma lembranca. Programas que se multiplicam deixam uma transformacao — passada de pessoa para pessoa, de escola para escola.",
                "frase": "Impacto que nao precisa de autorizacao para crescer.",
            },
            {
                "slug": "03-historia",
                "titulo": "A HISTORIA RECRUTA NOVOS PARCEIROS",
                "icone": "a microphone with speech bubbles spreading outward, storytelling symbol",
                "texto": "Quando um beneficiario conta sua historia, outros se reconhecem nela. O relato autentico e o melhor instrumento de captacao — porque nao vende, inspira.",
                "frase": "Historia verdadeira vale mais que qualquer anuncio.",
                "cena": "woman sharing her personal transformation story with genuine emotion, warm golden hour light, intimate documentary portrait, no screens no monitors",
            },
            {
                "slug": "04-dados",
                "titulo": "DADOS REAIS INSPIRAM INVESTIMENTOS",
                "icone": "a bar chart with upward trend and a lightbulb above it, data inspiring action",
                "texto": "Uma empresa que documenta resultados com indicadores verificaveis inspira outras a seguir o mesmo caminho. Transparencia gera emulacao — e o impacto se multiplica.",
                "frase": "Dado verificavel e convite a agir.",
            },
            {
                "slug": "05-celebrar",
                "titulo": "CELEBRAR MANTEM A NARRATIVA VIVA",
                "icone": "people raising hands in celebration with stars around them, community joy",
                "texto": "Comunidades que celebram sua transformacao sao comunidades que continuam transformando. A celebracao nao e vaidade — e renovacao de proposito coletivo.",
                "frase": "Celebrar e comprometer-se de novo.",
                "cena": "diverse group of people celebrating together at a community outdoor event, genuine joy and collective energy, candid warm moment, no screens",
            },
            {
                "slug": "06-cascata",
                "titulo": "IMPACTO EM CASCATA",
                "icone": "concentric ripple circles in water spreading outward, cascade effect",
                "texto": "Cada pessoa diretamente impactada leva o aprendizado para sua familia, trabalho e escola. O alcance real de um programa e sempre muito maior do que os numeros diretos mostram.",
                "frase": "1 pessoa transformada impacta muitas outras.",
            },
        ],
    },
}


# ─── Constantes Pillow ───────────────────────────────────────────────────────

_W, _H = 1856, 2304
_TEAL      = (0, 95, 115)
_TEAL_DARK = (0, 72, 88)
_TEAL_BAR  = (0, 165, 184)
_YELLOW    = (245, 184, 0)
_WHITE     = (255, 255, 255)
_GREEN     = (61, 170, 53)
_PINK      = (212, 26, 106)
_ORANGE    = (232, 100, 40)
_LGRAY     = (200, 200, 200)
_BAR_START = 0.975

_FONT_BOLD    = "C:/Windows/Fonts/segoeuib.ttf"
_FONT_REGULAR = "C:/Windows/Fonts/segoeui.ttf"
_FONT_ITALIC  = "C:/Windows/Fonts/segoeuii.ttf"


def _load_font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return ImageFont.load_default()


def _wrap_text(text, font, max_width):
    words = text.split()
    lines, current = [], ""
    for word in words:
        test = f"{current} {word}".strip()
        tw = font.getbbox(test)[2] - font.getbbox(test)[0]
        if tw <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def _draw_centered_text(draw, text, y, font, fill=None, max_width=None):
    if fill is None:
        fill = _WHITE
    if max_width is None:
        max_width = _W - 200
    lines = _wrap_text(text, font, max_width)
    line_h = int(font.size * 1.3)
    for line in lines:
        bbox = font.getbbox(line)
        tw = bbox[2] - bbox[0]
        x = (_W - tw) // 2
        draw.text((x, y), line, fill=fill, font=font)
        y += line_h
    return y


def _draw_top_stripe(draw):
    stripe_h = int(_H * 0.008)
    for x in range(_W):
        progress = x / max(_W - 1, 1)
        r = int(_GREEN[0] + (_TEAL_BAR[0] - _GREEN[0]) * progress)
        g = int(_GREEN[1] + (_TEAL_BAR[1] - _GREEN[1]) * progress)
        b = int(_GREEN[2] + (_TEAL_BAR[2] - _GREEN[2]) * progress)
        draw.line([(x, 0), (x, stripe_h)], fill=(r, g, b))


def _draw_gradient_bar(img):
    bar_y = int(_BAR_START * _H)
    draw = ImageDraw.Draw(img)
    colors = [_GREEN, _TEAL_BAR, _PINK, _ORANGE]
    segment_w = _W / (len(colors) - 1)
    for x in range(_W):
        seg_idx = min(int(x / segment_w), len(colors) - 2)
        progress = (x - seg_idx * segment_w) / segment_w
        c1, c2 = colors[seg_idx], colors[seg_idx + 1]
        r = int(c1[0] + (c2[0] - c1[0]) * progress)
        g = int(c1[1] + (c2[1] - c1[1]) * progress)
        b = int(c1[2] + (c2[2] - c1[2]) * progress)
        draw.line([(x, bar_y), (x, _H)], fill=(r, g, b))


def _open_bg(bg_bytes):
    img = Image.open(BytesIO(bg_bytes)).convert("RGBA")
    scale = max(_W / img.width, _H / img.height)
    img = img.resize((int(img.width * scale), int(img.height * scale)), Image.LANCZOS)
    cx = (img.width - _W) // 2
    cy = (img.height - _H) // 2
    return img.crop((cx, cy, cx + _W, cy + _H))


def aplicar_pelicula_teal(bg_bytes):
    """
    Aplica filtro/película teal (~62% opacidade) sobre a foto.
    Retorna bytes JPEG prontos para upload como init_image no Leonardo.
    """
    img = _open_bg(bg_bytes)
    pelicula = Image.new("RGBA", (_W, _H), (*_TEAL, 158))
    img = Image.alpha_composite(img, pelicula)
    buf = BytesIO()
    img.convert("RGB").save(buf, "JPEG", quality=95)
    return buf.getvalue()


def upload_init_image(img_bytes):
    """Faz upload de bytes JPEG como init_image no Leonardo. Retorna image_id ou None."""
    import json as _json
    import tempfile
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": f"Bearer {LEO_KEY}",
    }
    resp = requests.post(
        f"{BASE_V1}/init-image",
        headers=headers,
        json={"extension": "jpg"},
        timeout=15,
    )
    if not resp.ok:
        print(f"     upload init-image falhou: {resp.status_code}", flush=True)
        return None
    data = resp.json().get("uploadInitImage", {})
    image_id = data.get("id")
    upload_url = data.get("url")
    fields = data.get("fields", {})
    if not image_id or not upload_url:
        return None
    if isinstance(fields, str):
        try:
            fields = _json.loads(fields)
        except Exception:
            fields = {}
    form_data = {k: v for k, v in fields.items()} if isinstance(fields, dict) else {}
    # Salva bytes em arquivo temp para enviar como multipart
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
        tmp.write(img_bytes)
        tmp_path = tmp.name
    with open(tmp_path, "rb") as f:
        up = requests.post(upload_url, data=form_data,
                           files={"file": ("image.jpg", f, "image/jpeg")}, timeout=30)
    import os as _os
    _os.unlink(tmp_path)
    if up.status_code not in (200, 204):
        print(f"     S3 upload falhou: {up.status_code}", flush=True)
        return None
    return image_id


# ─── Prompts Leonardo ─────────────────────────────────────────────────────────

_NO_TEXT = (
    " Important: absolutely NO text, NO words, NO letters, NO numbers, "
    "NO watermarks anywhere on the image."
)


def build_bg_photo_prompt(cena):
    """Fundo fotográfico limpo para cards híbridos — SEM nenhum texto."""
    return (
        f"A full-bleed hyperrealistic photograph, 1856x2304px Instagram 4:5 format. "
        f"Scene: {cena}. Candid unposed moment, Canon EOS R5 35mm lens, natural warm light, "
        f"photojournalistic documentary style, visible film grain ISO 800. "
        f"No screens, no monitors, no TVs, no digital displays. Fill the entire frame edge to edge."
        + _NO_TEXT
    )


def build_capa_prompt(s):
    return (
        f"A social media educational carousel cover card Instagram 4:5 format. "
        f"The top 50 percent is a full-bleed hyperrealistic photograph of {s['capa_cena']}, "
        f"candid unposed moment, Canon EOS R5 35mm lens, natural warm light, photojournalistic "
        f"documentary style, visible film grain ISO 800, NOT AI generated NOT illustration. "
        f"No screens, no monitors, no TVs, no projectors, no digital displays anywhere. "
        f"From 50 to 68 percent smooth dark gradient from transparent to solid dark teal. "
        f"From 68 to 78 percent over solid dark teal centered small bold white uppercase sans-serif "
        f"text: RESPONSABILIDADE SOCIAL QUE RESOLVE. "
        f"From 78 to 92 percent large bold white uppercase text: {s['tema'].upper()}. "
        f"From 92 to 97 percent smaller white italic text: {s['capa_subtitulo']}. "
        f"At the very bottom a thick horizontal gradient stripe — from LEFT to RIGHT: "
        f"green on the far left, transitioning to teal, then pink, ending with orange on the far right. "
        f"No text, no labels. Professional editorial design."
    )


def build_card_prompt(card):
    return (
        f"A social media educational carousel card Instagram 4:5 format. "
        f"Clean solid dark teal background filling the entire card. "
        f"At the very top a subtle thin gradient stripe from green to teal, no text. "
        f"In the upper quarter, centered large flat icon illustration of {card['icone']}, "
        f"white and yellow tones on teal background, modern minimalist style. "
        f"Below the icon, bold large white uppercase sans-serif text centered: "
        f"{card['titulo']}. "
        f"Below the title, regular white sans-serif body text centered with generous "
        f"line spacing: {card['texto']}. "
        f"Near the bottom, a highlighted rectangle with yellow left border and "
        f"yellow italic text: {card['frase']}. "
        f"At the very bottom a thick horizontal gradient stripe — from LEFT to RIGHT: "
        f"green on the far left, transitioning to teal, then pink, ending with orange on the far right. "
        f"No text, no labels. Professional clean educational card design."
    )


def build_capa_prompt_hybrid(s):
    """
    Prompt para capa híbrida (foto full-bleed + película teal via init_image).
    Não menciona fundo — a foto filtrada já ocupa o card inteiro.
    Leonardo só adiciona os elementos de texto por cima.
    """
    # Tema curto para caber em no máximo 2 linhas
    tema = s['tema'].upper()
    return (
        f"A social media educational carousel cover card Instagram 4:5 format. "
        f"Keep the existing teal-filtered photo background filling the entire card. "
        f"At the very top a subtle thin gradient stripe from green to teal, no text. "
        f"In the center of the card, all text strictly centered horizontally: "
        f"First, a small white uppercase label with a subtle dark background pill, centered: RESPONSABILIDADE SOCIAL QUE RESOLVE. "
        f"Second, immediately below, a very large bold white uppercase headline centered in maximum 2 lines: {tema}. "
        f"Third, below the headline, a smaller white italic subtitle centered with no period at the end: {s['capa_subtitulo']}. "
        f"At the very bottom a thick horizontal gradient stripe — from LEFT to RIGHT: "
        f"green on the far left, transitioning to teal, then pink, ending with orange on the far right. "
        f"No text on the gradient stripe. Professional editorial cover design."
    )


def build_card_prompt_hybrid(card):
    """
    Prompt para cards híbridos (foto bg + película teal via init_image).
    Não menciona fundo sólido nem ícone — a foto filtrada já é o visual.
    Só pede os elementos de texto que o Leonardo deve colocar por cima.
    """
    return (
        f"A social media educational carousel card Instagram 4:5 format. "
        f"Keep the existing teal-filtered photo background exactly as provided. "
        f"At the very top a subtle thin gradient stripe from green to teal, no text. "
        f"In the upper portion, centered large bold white uppercase sans-serif title: "
        f"{card['titulo']}. "
        f"Below the title, regular white sans-serif body text centered with generous "
        f"line spacing: {card['texto']}. "
        f"Near the bottom, a semi-transparent dark rectangle with a yellow left border "
        f"and yellow italic text: {card['frase']}. "
        f"At the very bottom a thick horizontal gradient stripe — from LEFT to RIGHT: "
        f"green on the far left, transitioning to teal, then pink, ending with orange on the far right. "
        f"No text, no labels. Professional clean educational card design. No additional background elements."
    )


def build_metodo_prompt(s):
    m = s["metodo_metricas"]
    # Formata os números sem vírgulas decimais no prompt para evitar que Leonardo
    # interprete como separador de lista e adicione espaços (ex: "11, 4M" errado)
    def fmt_num(v):
        return v.replace(",", ".").replace(" ", "")
    return (
        f"A social media educational carousel metrics card Instagram 4:5 format. "
        f"Keep the existing teal-filtered photo background exactly as provided. "
        f"At the very top a subtle thin gradient stripe from green to teal, no text. "
        f"Below the stripe, small white uppercase label centered: MÉTODO NTICS. "
        f"Below the label, large bold white headline centered: {s['metodo_frase']}. "
        f"In the center of the card, a clean 2x2 grid of four dark rounded metric boxes, "
        f"each with a large bold yellow number at the top and a small white description below. "
        f"Box one shows number {fmt_num(m[0][0])} and label {m[0][1]}. "
        f"Box two shows number {fmt_num(m[1][0])} and label {m[1][1]}. "
        f"Box three shows number {fmt_num(m[2][0])} and label {m[2][1]}. "
        f"Box four shows number {fmt_num(m[3][0])} and label {m[3][1]}. "
        f"Each number must appear exactly as written above with no extra spaces or punctuation. "
        f"Near the bottom, small white text centered: "
        f"Certificacao ISO 9001 | Pacto Global ONU | GRI Standards. "
        f"At the very bottom a thick horizontal gradient stripe — from LEFT to RIGHT: "
        f"green on the far left, transitioning to teal, then pink, ending with orange on the far right. "
        f"No text, no labels, no percentage annotations. Professional data visualization card."
    )


def build_cta_prompt(s):
    return (
        f"A social media educational carousel CTA card Instagram 4:5 format. "
        f"Clean solid dark teal background throughout. "
        f"At the very top, empty clean teal space reserved for a logo. "
        f"In the upper center, centered large bold white sans-serif question text: "
        f"{s['cta_pergunta']}. "
        f"Below, centered medium white text: Fale com a NTICS. "
        f"Below that, centered white rounded button outline shape with "
        f"white text inside: ntics.com.br. "
        f"Below the button, small white text centered: @nticsprojetos. "
        f"At the very bottom a thick horizontal gradient stripe — from LEFT to RIGHT: "
        f"green on the far left, transitioning to teal, then pink, ending with orange on the far right. "
        f"No text, no labels. Minimalist professional CTA design."
    )


def start_gen(prompt):
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": f"Bearer {LEO_KEY}",
    }
    payload = {
        "model": "nano-banana-2",
        "parameters": {
            "prompt": prompt,
            "width": 1856,
            "height": 2304,
            "quantity": 1,
            "prompt_enhance": "OFF",
        },
        "public": False,
    }
    r = requests.post(f"{BASE_V2}/generations", headers=headers, json=payload, timeout=30)
    if not r.ok:
        raise RuntimeError(f"{r.status_code}: {r.text[:200]}")
    data = r.json()
    # handle both dict and list responses
    if isinstance(data, list):
        raise RuntimeError(f"API error list: {str(data)[:200]}")
    # try direct key
    for key in ["generationId", "id"]:
        if data.get(key):
            return data[key]
    # try nested dict
    for v in data.values():
        if isinstance(v, dict):
            for k in ["generationId", "id"]:
                if v.get(k):
                    return v[k]
    raise RuntimeError(f"No ID in: {str(data)[:200]}")


def poll_gen(gen_id, max_wait=180):
    headers = {"accept": "application/json", "authorization": f"Bearer {LEO_KEY}"}
    url = f"{BASE_V1}/generations/{gen_id}"
    waited = 0
    while waited < max_wait:
        r = requests.get(url, headers=headers, timeout=30)
        r.raise_for_status()
        job = r.json().get("generations_by_pk", {})
        status = job.get("status", "")
        if status == "COMPLETE":
            imgs = job.get("generated_images", [])
            if imgs:
                return imgs[0]["url"]
            raise RuntimeError("Complete but no images")
        if status == "FAILED":
            raise RuntimeError(f"FAILED")
        time.sleep(8)
        waited += 8
        print(f"    ...{waited}s", flush=True)
    raise TimeoutError(f"Timeout {max_wait}s")


def download(url, path):
    r = requests.get(url, timeout=60)
    r.raise_for_status()
    path.write_bytes(r.content)


def build_descricao(semana_key, s):
    cards_list = "\n".join([f"0{i+2}-{c['slug'].split('-', 1)[1]}.jpg — {c['titulo']}" for i, c in enumerate(s["cards"])])
    caption_ig = (
        f"Como sua empresa pode evoluir em {s['tema']}? "
        f"Este carrossel traz os conceitos essenciais para você aplicar hoje mesmo. "
        f"Salve para consultar sempre que precisar!\n\n"
        f"@nticsprojetos | #ResponsabilidadeSocial #ESG #ImpactoSocial #ODS #NTICS"
    )
    caption_li = (
        f"Compartilhando nosso framework sobre: {s['tema']}\n\n"
        f"Em 6 cards, os conceitos fundamentais para empresas que querem ir além do discurso.\n\n"
        f"O que mais ressoou com a realidade da sua empresa? Comente abaixo.\n\n"
        f"#ResponsabilidadeSocial #ESG #NTICS #ImpactoSocial"
    )
    return f"""========================================
CARROSSEL EDUCATIVO
Tema: {s['tema']}
Semana {semana_key}
========================================

--- CAPTION INSTAGRAM ---
{caption_ig}

--- CAPTION LINKEDIN ---
{caption_li}

--- ORDEM DOS CARDS ---
01-capa.jpg — Capa: {s['tema']}
{cards_list}
07-metodo.jpg — Método NTICS: {s['metodo_frase']}
08-cta.jpg — CTA: {s['cta_pergunta']}
"""


def apply_logo_cta(cta_path, cta_pergunta="", semana_key=""):
    """
    Reconstrói o card 08 CTA inteiro via Pillow.
    Fundo teal sólido uniforme (sem variação de cor), logo no topo,
    pergunta, 'Fale com a NTICS', botão ntics.com.br, @nticsprojetos.
    """
    W, H = 1856, 2304
    TEAL       = (0, 95, 115)
    TEAL_DARK  = (0, 72, 88)
    WHITE      = (255, 255, 255)
    YELLOW     = (245, 184, 0)
    GREEN      = (61, 170, 53)
    TEAL_BAR   = (0, 165, 184)
    PINK       = (212, 26, 106)
    ORANGE     = (232, 100, 40)
    BAR_START  = 0.988

    logo_candidates = [
        Path("brand-book/site/assets/LOGO NTICS - BRANCA.png"),
        Path("G:/O meu disco/AUTOMAÇÕES/brand-book/site/assets/LOGO NTICS - BRANCA.png"),
    ]
    logo_path = next((p for p in logo_candidates if p.exists()), None)

    # Fundo teal sólido uniforme
    card = Image.new("RGB", (W, H), TEAL)
    draw = ImageDraw.Draw(card)

    # Stripe de topo (verde → teal)
    stripe_h = int(H * 0.008)
    for x in range(W):
        p = x / max(W - 1, 1)
        r = int(GREEN[0] + (TEAL_BAR[0] - GREEN[0]) * p)
        g = int(GREEN[1] + (TEAL_BAR[1] - GREEN[1]) * p)
        b = int(GREEN[2] + (TEAL_BAR[2] - GREEN[2]) * p)
        draw.line([(x, 0), (x, stripe_h)], fill=(r, g, b))

    # Logo NTICS
    logo_y = int(H * 0.06)
    if logo_path:
        logo = Image.open(logo_path).convert("RGBA")
        logo_max_h = int(H * 0.12)
        ratio = logo_max_h / logo.height
        logo_w = int(logo.width * ratio)
        logo_resized = logo.resize((logo_w, logo_max_h), Image.LANCZOS)
        lx = (W - logo_w) // 2
        card.paste(logo_resized, (lx, logo_y), logo_resized)
        text_y = logo_y + logo_max_h + int(H * 0.06)
    else:
        text_y = int(H * 0.22)

    # Pergunta principal
    font_bold    = _load_font(_FONT_BOLD, 96)
    font_regular = _load_font(_FONT_REGULAR, 64)
    font_small   = _load_font(_FONT_REGULAR, 52)

    # Wrap e draw da pergunta
    if cta_pergunta:
        words = cta_pergunta.split()
        lines, cur = [], ""
        for w in words:
            test = f"{cur} {w}".strip()
            tw = font_bold.getbbox(test)[2] - font_bold.getbbox(test)[0]
            if tw <= W - 160:
                cur = test
            else:
                if cur: lines.append(cur)
                cur = w
        if cur: lines.append(cur)
        line_h = int(96 * 1.25)
        for line in lines:
            bbox = font_bold.getbbox(line)
            lw = bbox[2] - bbox[0]
            draw.text(((W - lw) // 2, text_y), line, fill=WHITE, font=font_bold)
            text_y += line_h
    else:
        text_y += int(H * 0.15)

    text_y += int(H * 0.05)

    # "Fale com a NTICS"
    fale = "Fale com a NTICS"
    bbox = font_regular.getbbox(fale)
    fw = bbox[2] - bbox[0]
    draw.text(((W - fw) // 2, text_y), fale, fill=WHITE, font=font_regular)
    text_y += int(64 * 1.4) + int(H * 0.03)

    # Botão ntics.com.br
    btn_text = "ntics.com.br"
    bbox = font_regular.getbbox(btn_text)
    bw = bbox[2] - bbox[0]
    bh = 64
    pad_x, pad_y = 80, 28
    btn_x = (W - bw - pad_x * 2) // 2
    btn_rect = [btn_x, text_y, btn_x + bw + pad_x * 2, text_y + bh + pad_y * 2]
    draw.rounded_rectangle(btn_rect, radius=20, outline=WHITE, width=4)
    draw.text((btn_x + pad_x, text_y + pad_y), btn_text, fill=WHITE, font=font_regular)
    text_y = btn_rect[3] + int(H * 0.04)

    # @nticsprojetos
    handle = "@nticsprojetos"
    bbox = font_small.getbbox(handle)
    hw = bbox[2] - bbox[0]
    draw.text(((W - hw) // 2, text_y), handle, fill=WHITE, font=font_small)

    # Barra gradiente
    bar_y = int(BAR_START * H)
    colors = [GREEN, TEAL_BAR, PINK, ORANGE]
    segment_w = W / (len(colors) - 1)
    for x in range(W):
        seg = min(int(x / segment_w), len(colors) - 2)
        prog = (x - seg * segment_w) / segment_w
        c1, c2 = colors[seg], colors[seg + 1]
        r = int(c1[0] + (c2[0] - c1[0]) * prog)
        g = int(c1[1] + (c2[1] - c1[1]) * prog)
        b = int(c1[2] + (c2[2] - c1[2]) * prog)
        draw.line([(x, bar_y), (x, H)], fill=(r, g, b))

    card.save(cta_path, "JPEG", quality=95)
    print(f"     CTA reconstruído em: {cta_path}", flush=True)


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--semana", default=None, help="Processar só uma semana (ex: S03)")
    args = parser.parse_args()

    semanas = {k: v for k, v in SEMANAS.items() if args.semana is None or k == args.semana}
    if not semanas:
        print(f"Semana '{args.semana}' nao encontrada. Opcoes: {list(SEMANAS.keys())}")
        return

    for semana_key, s in semanas.items():
        print(f"\n{'='*50}")
        print(f"EDUCATIVO {semana_key} — {s['tema']}")
        print(f"{'='*50}")

        out_dir = Path(f".tmp/marketing/carrosseis/educativo/{semana_key}")
        out_dir.mkdir(parents=True, exist_ok=True)

        # Todos os cards de conteúdo (01-07) usam abordagem híbrida:
        # Passo 1: Leonardo gera foto bg limpa
        # Passo 2: Pillow aplica película teal → upload init_image → Leonardo gera card com texto
        # Capa (01) sempre híbrida via build_capa_prompt_hybrid
        # Cards com campo "cena" são híbridos; sem "cena" usam build_card_prompt direto
        hibridos = {c["slug"] for c in s["cards"] if c.get("cena")}
        if s.get("metodo_cena"):
            hibridos.add("07-metodo")
        # Capa sempre híbrida
        hibridos.add("01-capa")

        # Build all prompts — Passo 1 (foto bg para híbridos, prompt direto para demais)
        prompts = {}
        prompts["01-capa"] = build_bg_photo_prompt(s["capa_cena"])
        for card in s["cards"]:
            if card["slug"] in hibridos:
                prompts[card["slug"]] = build_bg_photo_prompt(card["cena"])
            else:
                prompts[card["slug"]] = build_card_prompt(card)
        if "07-metodo" in hibridos:
            prompts["07-metodo"] = build_bg_photo_prompt(s["metodo_cena"])
        else:
            prompts["07-metodo"] = build_metodo_prompt(s)
        prompts["08-cta"] = build_cta_prompt(s)

        # Submit all generations
        jobs = {}
        for name, prompt in prompts.items():
            print(f"  >> Starting: {name}", flush=True)
            try:
                gen_id = start_gen(prompt)
                jobs[name] = gen_id
                print(f"     ID: {gen_id}", flush=True)
                time.sleep(1)
            except Exception as e:
                print(f"     FAILED: {e}", flush=True)

        if not jobs:
            continue

        print(f"\n  Waiting 60s for {len(jobs)} generations...", flush=True)
        time.sleep(60)

        # Poll e download — híbridos ficam como bytes para Passo 2
        cards_by_slug = {c["slug"]: c for c in s["cards"]}
        step1_results = {}  # name -> img_url
        for name, gen_id in jobs.items():
            print(f"  >> Polling: {name}", flush=True)
            try:
                img_url = poll_gen(gen_id)
                step1_results[name] = img_url
                if name not in hibridos:
                    path = out_dir / f"{name}.jpg"
                    download(img_url, path)
                    print(f"     SAVED: {path}", flush=True)
            except Exception as e:
                print(f"     FAILED poll: {name} — {e}", flush=True)

        # Passo 2 — híbridos: aplica película, faz upload, submete ao Leonardo com texto
        # Submete todos os híbridos em paralelo
        hibrido_jobs = {}  # name -> gen_id da 2a geração
        for name in hibridos:
            if name not in step1_results:
                continue
            print(f"  >> Hibrido Passo 2: {name}", flush=True)
            try:
                bg_bytes_raw = requests.get(step1_results[name], timeout=60).content
                filtered_bytes = aplicar_pelicula_teal(bg_bytes_raw)
                init_id = upload_init_image(filtered_bytes)
                if not init_id:
                    raise RuntimeError("Upload init_image falhou")

                # Monta prompt do card com texto para Passo 2
                if name == "01-capa":
                    prompt2 = build_capa_prompt_hybrid(s)
                elif name == "07-metodo":
                    prompt2 = build_metodo_prompt(s)
                else:
                    card_data = cards_by_slug[name]
                    prompt2 = build_card_prompt_hybrid(card_data)

                # Gera com init_image — init_strength 0.70 preserva bem o fundo filtrado
                payload2 = {
                    "model": "nano-banana-2",
                    "parameters": {
                        "prompt": prompt2,
                        "width": _W,
                        "height": _H,
                        "quantity": 1,
                        "prompt_enhance": "OFF",
                        "init_image_id": init_id,
                        "init_strength": 0.70,  # preserva fundo fotográfico com película
                    },
                    "public": False,
                }
                headers = {
                    "accept": "application/json",
                    "content-type": "application/json",
                    "authorization": f"Bearer {LEO_KEY}",
                }
                r2 = requests.post(f"{BASE_V2}/generations", headers=headers,
                                   json=payload2, timeout=30)
                if not r2.ok:
                    raise RuntimeError(f"{r2.status_code}: {r2.text[:100]}")
                data2 = r2.json()
                gen_id2 = None
                for key in ["generationId", "id"]:
                    if data2.get(key):
                        gen_id2 = data2[key]
                        break
                for v in data2.values():
                    if isinstance(v, dict):
                        for k in ["generationId", "id"]:
                            if v.get(k):
                                gen_id2 = v[k]
                if not gen_id2:
                    raise RuntimeError(f"Sem ID: {str(data2)[:100]}")
                hibrido_jobs[name] = gen_id2
                print(f"     ID passo2: {gen_id2}", flush=True)
                time.sleep(0.5)
            except Exception as e:
                print(f"     FAILED passo2 submit: {name} — {e}", flush=True)

        if hibrido_jobs:
            print(f"\n  Aguardando ~60s para {len(hibrido_jobs)} hibridos passo 2...", flush=True)
            time.sleep(60)

        results = []
        # Salvar resultados dos não-híbridos
        for name in step1_results:
            if name not in hibridos:
                results.append({"name": name, "ok": True})
        # Poll e salvar híbridos finais
        for name, gen_id2 in hibrido_jobs.items():
            print(f"  >> Polling hibrido final: {name}", flush=True)
            try:
                img_url2 = poll_gen(gen_id2)
                path = out_dir / f"{name}.jpg"
                download(img_url2, path)
                print(f"     SAVED hibrido: {path}", flush=True)
                results.append({"name": name, "ok": True})
            except Exception as e:
                print(f"     FAILED hibrido final: {name} — {e}", flush=True)
                results.append({"name": name, "ok": False, "error": str(e)})

        # Reconstruir card 08 CTA via Pillow (fundo teal sólido uniforme)
        cta_path = out_dir / "08-cta.jpg"
        if cta_path.exists():
            apply_logo_cta(cta_path, cta_pergunta=s.get("cta_pergunta", ""), semana_key=semana_key)

        # Save descricao.txt
        (out_dir / "descricao.txt").write_text(build_descricao(semana_key, s), encoding="utf-8")

        ok = sum(1 for r in results if r["ok"])
        print(f"\n  {semana_key}: {ok}/{len(prompts)} imagens → {out_dir}")

        # Copiar para output/final com prefixo da semana no nome da pasta
        import shutil as _shutil
        import re as _re
        slug_tema = _re.sub(r"[^\w\s-]", "", s["tema"].lower())
        slug_tema = _re.sub(r"[\s_]+", "-", slug_tema).strip("-")
        final_dir = Path(
            f"output/marketing/carrosseis/educacional/{semana_key}-{slug_tema}/final"
        )
        final_dir.mkdir(parents=True, exist_ok=True)
        for f in out_dir.glob("*.jpg"):
            _shutil.copy2(f, final_dir / f.name)
        desc = out_dir / "descricao.txt"
        if desc.exists():
            _shutil.copy2(desc, final_dir / "descricao.txt")
        print(f"  Final: {final_dir}")

    print("\n\nCONCLUIDO!")


if __name__ == "__main__":
    main()
