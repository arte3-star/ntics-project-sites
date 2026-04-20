"""
gerar_carrossel_educativo.py — Gera carrossel educativo NTICS (Opcao B).

📚 Ref: workflows/marketing/referencia/leonardo_ai_core.md — consulte em caso de erro ou
dúvida sobre payloads, pipeline híbrido, NO_TEXT_SUFFIX, erros conhecidos.

Leonardo AI gera os fundos visuais de TODOS os cards (sem texto).
Pillow sobrepoe titulo, corpo e frase destaque com precisao.

Cards de conteudo (2-6) suportam 3 tipos de fundo via campo bg_type:
  foto     — foto hiper-realista da cena
  icone    — icone flat estilizado sobre fundo teal
  infografico — visualizacao abstrata; Pillow sobrepoe dados reais

Usage:
  python tools/content-gen/gerar_carrossel_educativo.py --semana 2026-04-07 --briefing briefing.json
  python tools/content-gen/gerar_carrossel_educativo.py --semana 2026-04-07 --briefing briefing.json --skip-backgrounds
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime
from io import BytesIO
from pathlib import Path

import requests
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

load_dotenv()

# ── Constantes visuais ────────────────────────────────────────────────────────

W, H = 1856, 2304

TEAL     = (0, 95, 115)
YELLOW   = (245, 184, 0)
WHITE    = (255, 255, 255)
GREEN    = (61, 170, 53)
TEAL_BAR = (0, 165, 184)
PINK     = (212, 26, 106)
ORANGE   = (232, 100, 40)
LIGHT_GRAY = (200, 200, 200)

FONT_BOLD    = "C:/Windows/Fonts/segoeuib.ttf"
FONT_REGULAR = "C:/Windows/Fonts/segoeui.ttf"
FONT_ITALIC  = "C:/Windows/Fonts/segoeuii.ttf"

BAR_START = 0.975

OUTPUT_DIR = Path(".tmp/marketing/carrosseis/educativos")

# ── Leonardo AI ───────────────────────────────────────────────────────────────

LEO_KEY = os.getenv("LEONARDO_API_KEY")
BASE_V2 = "https://cloud.leonardo.ai/api/rest/v2"
BASE_V1 = "https://cloud.leonardo.ai/api/rest/v1"

NO_TEXT_SUFFIX = (
    " Important: absolutely NO text, NO words, NO letters, NO numbers, "
    "NO watermarks anywhere on the image."
)


def leo_headers():
    return {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": f"Bearer {LEO_KEY}",
    }


# ── Construtores de prompt ────────────────────────────────────────────────────

def build_capa_prompt(briefing):
    cena = briefing.get("capa_cena", "corporate team reviewing ESG impact data in modern office")
    return (
        f"A social media card background, Instagram 4:5 format 1856x2304px. "
        f"Full-bleed hyperrealistic photograph of {cena}, "
        f"candid unposed moment, Canon EOS R5 35mm lens, natural warm sunlight, "
        f"photojournalistic documentary style, visible film grain ISO 800, "
        f"NOT AI generated NOT illustration. Pure photograph, no graphics."
        + NO_TEXT_SUFFIX
    )


def build_bg_prompt_foto(card):
    cena = card.get("cena", "professionals collaborating in a bright modern office")
    return (
        f"A social media card background, Instagram 4:5 format 1856x2304px. "
        f"Full-bleed hyperrealistic photograph of {cena}, "
        f"candid unposed moment, Canon EOS R5 35mm lens, natural warm sunlight, "
        f"photojournalistic documentary style, visible film grain ISO 800. "
        f"Pure photograph, no graphics."
        + NO_TEXT_SUFFIX
    )


def build_bg_prompt_icone(card):
    icone = card.get("icone", "a glowing lightbulb with connected nodes around it")
    return (
        f"A social media card background, Instagram 4:5 format 1856x2304px. "
        f"Solid dark teal background color hex 005F73 filling the entire card. "
        f"In the upper center area from 15 percent to 50 percent of card height, "
        f"a large minimalist flat icon of {icone}, "
        f"using white and yellow-gold F5B800 tones only, modern design, simple geometric shapes. "
        f"The bottom 50 percent of the card must remain completely clean solid teal 005F73 with no elements. "
        f"At the very top a subtle thin gradient stripe from green 3DAA35 to teal 00A5B8."
        + NO_TEXT_SUFFIX
    )


def build_bg_prompt_infografico(card):
    viz_type = card.get("viz_type", "horizontal bar chart")
    viz_desc = card.get("viz_desc", "comparison between different metrics")
    return (
        f"A social media card background, Instagram 4:5 format 1856x2304px. "
        f"Solid dark teal background color hex 005F73. "
        f"In the center area from 28 percent to 72 percent of card height, "
        f"an abstract clean {viz_type} visualization using "
        f"yellow-gold F5B800, white, and teal 00A5B8 colors. "
        f"Style: modern corporate infographic, geometric, minimalist. "
        f"The visualization should suggest {viz_desc} "
        f"but must contain only abstract shapes, bars, lines, circles — no text, no numbers, no labels. "
        f"Leave top 20 percent and bottom 25 percent of card as clean solid teal 005F73. "
        f"At the very top a subtle thin gradient stripe from green 3DAA35 to teal 00A5B8."
        + NO_TEXT_SUFFIX
    )


def build_bg_prompt_padrao():
    return (
        f"A social media card background, Instagram 4:5 format 1856x2304px. "
        f"Solid dark teal background color hex 005F73 filling the entire card. "
        f"At the very top a subtle thin gradient stripe from green 3DAA35 to teal 00A5B8. "
        f"Clean minimal design."
        + NO_TEXT_SUFFIX
    )


def build_metodo_bg_prompt():
    return (
        f"A social media card background, Instagram 4:5 format 1856x2304px. "
        f"Solid dark teal background color hex 005F73. "
        f"Four rounded rectangular cards arranged in a 2x2 grid "
        f"in the center area from 35 percent to 75 percent of card height, "
        f"each with subtle slightly darker teal fill and thin yellow-gold F5B800 top border accent. "
        f"Small geometric decorative dots and thin lines in corners using yellow-gold and teal 00A5B8. "
        f"At the very top a subtle thin gradient stripe from green 3DAA35 to teal 00A5B8. "
        f"Clean professional data card design."
        + NO_TEXT_SUFFIX
    )


def build_cta_bg_prompt():
    return (
        f"A social media card background, Instagram 4:5 format 1856x2304px. "
        f"Solid dark teal background 005F73. "
        f"Subtle decorative elements: thin geometric lines in yellow-gold F5B800, "
        f"small abstract teal 00A5B8 circle shapes in bottom corners, "
        f"a faint rounded rectangle outline in the center area suggesting a button shape. "
        f"Clean, spacious, professional. Top 18 percent reserved as empty teal space. "
        f"At the very bottom a thick gradient stripe from green 3DAA35 to teal 00A5B8 "
        f"to pink D41A6A to orange E86428."
        + NO_TEXT_SUFFIX
    )


def build_bg_prompt(card):
    """Dispatcher: monta prompt Leonardo de acordo com bg_type do card."""
    bg_type = card.get("bg_type", "padrao")
    if bg_type == "foto":
        return build_bg_prompt_foto(card)
    elif bg_type == "icone":
        return build_bg_prompt_icone(card)
    elif bg_type == "infografico":
        return build_bg_prompt_infografico(card)
    else:
        return build_bg_prompt_padrao()


# ── Geracao paralela de backgrounds ──────────────────────────────────────────

def _start_gen(prompt):
    payload = {
        "model": "nano-banana-2",
        "parameters": {
            "prompt": prompt,
            "width": W,
            "height": H,
            "quantity": 1,
            "prompt_enhance": "OFF",
        },
        "public": False,
    }
    r = requests.post(f"{BASE_V2}/generations", headers=leo_headers(), json=payload, timeout=30)
    if not r.ok:
        raise RuntimeError(f"{r.status_code}: {r.text[:200]}")
    data = r.json()
    for key in ["generationId", "id"]:
        if data.get(key):
            return data[key]
    for v in data.values():
        if isinstance(v, dict):
            for k in ["generationId", "id"]:
                if v.get(k):
                    return v[k]
    raise RuntimeError(f"Sem ID na resposta: {str(data)[:200]}")


def _poll_gen(gen_id, max_wait=180):
    url = f"{BASE_V1}/generations/{gen_id}"
    waited = 0
    while waited < max_wait:
        r = requests.get(url, headers=leo_headers(), timeout=30)
        r.raise_for_status()
        job = r.json().get("generations_by_pk", {})
        status = job.get("status", "")
        if status == "COMPLETE":
            imgs = job.get("generated_images", [])
            if imgs:
                return imgs[0]["url"]
            raise RuntimeError("COMPLETE mas sem imagens")
        if status == "FAILED":
            raise RuntimeError("Geracao FAILED no Leonardo AI")
        time.sleep(8)
        waited += 8
        print(f"    ...{waited}s aguardando", flush=True)
    raise TimeoutError(f"Timeout apos {max_wait}s")


def _download(img_url):
    r = requests.get(img_url, timeout=60)
    r.raise_for_status()
    return r.content


def generate_all_backgrounds(briefing, skip_backgrounds=False):
    """
    Submete todos os prompts em paralelo, aguarda e retorna dict {slug: image_bytes}.
    Com skip_backgrounds=True retorna dict vazio (fundos solidos em todos os cards).
    """
    if not LEO_KEY:
        print("  AVISO: LEONARDO_API_KEY nao definida. Usando fundos solidos.")
        return {}

    if skip_backgrounds:
        print("  --skip-backgrounds ativo. Pulando geracao Leonardo AI.")
        return {}

    jobs = {}
    jobs["01-capa"] = build_capa_prompt(briefing)
    for card in briefing["cards"]:
        jobs[card["slug"]] = build_bg_prompt(card)
    jobs["07-metodo"] = build_metodo_bg_prompt()
    jobs["08-cta"]    = build_cta_bg_prompt()

    gen_ids = {}
    print(f"\n  Submetendo {len(jobs)} geracao(oes) ao Leonardo AI...", flush=True)
    for slug, prompt in jobs.items():
        try:
            gen_id = _start_gen(prompt)
            gen_ids[slug] = gen_id
            print(f"    >> {slug}: ID {gen_id}", flush=True)
            time.sleep(0.5)
        except Exception as e:
            print(f"    >> {slug}: FALHOU ao submeter — {e}", flush=True)

    if not gen_ids:
        return {}

    print(f"\n  Aguardando ~65s para {len(gen_ids)} geracao(oes)...", flush=True)
    time.sleep(65)

    backgrounds = {}
    for slug, gen_id in gen_ids.items():
        print(f"  Baixando: {slug}...", flush=True)
        try:
            img_url = _poll_gen(gen_id)
            backgrounds[slug] = _download(img_url)
            print(f"    OK: {slug}", flush=True)
        except Exception as e:
            print(f"    FALHOU: {slug} — {e}", flush=True)

    return backgrounds


# ── Helpers Pillow ────────────────────────────────────────────────────────────

def load_font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return ImageFont.load_default()


def open_bg(bg_bytes):
    """Abre bytes de imagem como RGBA 1856x2304 (crop centralizado)."""
    img = Image.open(BytesIO(bg_bytes)).convert("RGBA")
    scale = max(W / img.width, H / img.height)
    resized = img.resize((int(img.width * scale), int(img.height * scale)), Image.LANCZOS)
    cx = (resized.width - W) // 2
    cy = (resized.height - H) // 2
    return resized.crop((cx, cy, cx + W, cy + H))


def solid_bg():
    return Image.new("RGBA", (W, H), (*TEAL, 255))


def draw_gradient_bar(img):
    """Barra gradiente no rodape (verde → teal → rosa → laranja)."""
    bar_y = int(BAR_START * H)
    draw = ImageDraw.Draw(img)
    colors = [GREEN, TEAL_BAR, PINK, ORANGE]
    segment_w = W / (len(colors) - 1)
    for x in range(W):
        seg_idx = min(int(x / segment_w), len(colors) - 2)
        progress = (x - seg_idx * segment_w) / segment_w
        c1, c2 = colors[seg_idx], colors[seg_idx + 1]
        r = int(c1[0] + (c2[0] - c1[0]) * progress)
        g = int(c1[1] + (c2[1] - c1[1]) * progress)
        b = int(c1[2] + (c2[2] - c1[2]) * progress)
        draw.line([(x, bar_y), (x, H)], fill=(r, g, b))


def draw_gradient_overlay(img, y_start, y_end, color):
    """Degrade transparente → cor solida (de cima para baixo)."""
    overlay = Image.new("RGBA", (W, y_end - y_start), (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    for y in range(overlay.height):
        alpha = int(255 * y / max(overlay.height - 1, 1))
        d.line([(0, y), (W, y)], fill=(*color, alpha))
    region = img.crop((0, y_start, W, y_end)).convert("RGBA")
    img.paste(Image.alpha_composite(region, overlay), (0, y_start))


def draw_solid_overlay(img, y_start, y_end, color, alpha=255):
    """Bloco colorido sobre a imagem, com alpha opcional."""
    overlay = Image.new("RGBA", (W, y_end - y_start), (*color, alpha))
    region  = img.crop((0, y_start, W, y_end)).convert("RGBA")
    img.paste(Image.alpha_composite(region, overlay), (0, y_start))


def draw_top_stripe(draw):
    """Faixa gradiente decorativa no topo (para cards sem foto)."""
    stripe_h = int(H * 0.008)
    colors = [GREEN, TEAL_BAR]
    for x in range(W):
        progress = x / max(W - 1, 1)
        c1, c2 = colors[0], colors[1]
        r = int(c1[0] + (c2[0] - c1[0]) * progress)
        g = int(c1[1] + (c2[1] - c1[1]) * progress)
        b = int(c1[2] + (c2[2] - c1[2]) * progress)
        draw.line([(x, 0), (x, stripe_h)], fill=(r, g, b))


def wrap_text(text, font, max_width):
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


def draw_centered_text(draw, text, y, font, fill=WHITE, max_width=None):
    if max_width is None:
        max_width = W - 200
    lines = wrap_text(text, font, max_width)
    line_h = int(font.size * 1.3)
    for line in lines:
        bbox = font.getbbox(line)
        tw = bbox[2] - bbox[0]
        x = (W - tw) // 2
        draw.text((x, y), line, fill=fill, font=font)
        y += line_h
    return y


def draw_text_block(draw, card_data, y_start, margin_x=120):
    """
    Bloco de texto padrao: titulo + separador + corpo + frase destaque.
    Retorna y apos o ultimo elemento.
    """
    max_w = W - margin_x * 2

    font_title = load_font(FONT_BOLD, 72)
    y = y_start
    lines = wrap_text(card_data["titulo"].upper(), font_title, max_w)
    for line in lines:
        draw.text((margin_x, y), line, fill=WHITE, font=font_title)
        y += int(72 * 1.25)

    y += 30
    draw.line([(margin_x, y), (margin_x + 200, y)], fill=YELLOW, width=6)
    y += 50

    if card_data.get("texto"):
        font_body = load_font(FONT_REGULAR, 50)
        for line in wrap_text(card_data["texto"], font_body, max_w):
            draw.text((margin_x, y), line, fill=WHITE, font=font_body)
            y += int(50 * 1.45)

    if card_data.get("frase"):
        y += 50
        font_frase = load_font(FONT_ITALIC, 46)
        frase_lines = wrap_text(card_data["frase"], font_frase, max_w - 40)
        frase_h = len(frase_lines) * int(46 * 1.35)
        draw.rectangle([(margin_x, y), (margin_x + 8, y + frase_h + 20)], fill=YELLOW)
        fy = y + 10
        for line in frase_lines:
            draw.text((margin_x + 30, fy), line, fill=YELLOW, font=font_frase)
            fy += int(46 * 1.35)

    return y


def draw_infografico_barras_overlay(draw, card_data, y_start, margin_x=120):
    """
    Sobrepoe labels e valores sobre a visualizacao de barras gerada pelo Leonardo.
    Posiciona os textos reais sobre as formas abstratas do fundo.
    """
    dados = card_data.get("dados_overlay", {})
    items = dados.get("items", [])
    if not items:
        return y_start

    available_h = int(H * 0.40)
    spacing = available_h // max(len(items), 1)
    font_label = load_font(FONT_REGULAR, 44)
    font_valor = load_font(FONT_BOLD, 64)

    y = y_start
    for item in items:
        label  = item.get("label", "")
        valor  = str(item.get("valor", ""))
        sufixo = item.get("sufixo", "")

        draw.text((margin_x, y), label, fill=WHITE, font=font_label)

        val_text = f"{valor}{sufixo}"
        bbox = font_valor.getbbox(val_text)
        vw = bbox[2] - bbox[0]
        draw.text((W - margin_x - vw, y - 10), val_text, fill=YELLOW, font=font_valor)

        y += spacing

    return y


# ── Composicao dos Cards ──────────────────────────────────────────────────────

def compor_capa(briefing, bg_bytes, output_path):
    """Card 01: Capa — foto + gradiente teal + badge + titulo + subtitulo."""
    card = open_bg(bg_bytes) if bg_bytes else solid_bg()

    draw_gradient_overlay(card, int(H * 0.42), int(H * 0.65), TEAL)
    draw_solid_overlay(card, int(H * 0.65), int(H * BAR_START), TEAL)

    draw = ImageDraw.Draw(card)

    # Badge
    font_badge = load_font(FONT_BOLD, 36)
    badge_text = "RESPONSABILIDADE SOCIAL QUE RESOLVE"
    bbox = font_badge.getbbox(badge_text)
    bw = bbox[2] - bbox[0]
    bx = (W - bw - 40) // 2
    by = int(H * 0.67)
    draw.rounded_rectangle([(bx, by), (bx + bw + 40, by + 52)], radius=26, fill=GREEN)
    draw.text((bx + 20, by + 8), badge_text, fill=WHITE, font=font_badge)

    # Titulo
    font_title = load_font(FONT_BOLD, 80)
    y = int(H * 0.74)
    y = draw_centered_text(draw, briefing["tema"].upper(), y, font_title, fill=WHITE, max_width=W - 200)

    # Subtitulo
    font_sub = load_font(FONT_ITALIC, 48)
    draw_centered_text(draw, briefing.get("capa_subtitulo", ""), y + 20, font_sub, fill=LIGHT_GRAY)

    draw_gradient_bar(card)
    card.convert("RGB").save(output_path, "JPEG", quality=95)
    print(f"  Salvo: {output_path}")


def compor_card_conteudo(card_data, bg_bytes, output_path):
    """
    Cards 02-06: overlay de texto sobre fundo Leonardo AI.

    bg_type:
      foto        — texto na zona inferior (abaixo de 58%)
      icone       — texto abaixo do icone (abaixo de 52%)
      infografico — titulo no topo + dados no centro + frase na base
      padrao/None — fundo solido teal (backward compat)
    """
    bg_type = card_data.get("bg_type", "padrao")
    card = open_bg(bg_bytes) if bg_bytes else solid_bg()

    if bg_type == "foto":
        draw_gradient_overlay(card, int(H * 0.40), int(H * 0.60), TEAL)
        draw_solid_overlay(card, int(H * 0.60), int(H * BAR_START), TEAL)
        draw = ImageDraw.Draw(card)
        draw_text_block(draw, card_data, y_start=int(H * 0.62))

    elif bg_type == "icone":
        draw_solid_overlay(card, int(H * 0.50), int(H * BAR_START), TEAL)
        draw = ImageDraw.Draw(card)
        draw_text_block(draw, card_data, y_start=int(H * 0.53))

    elif bg_type == "infografico":
        # Topo solido para titulo legivel
        draw_solid_overlay(card, 0, int(H * 0.26), TEAL)
        # Overlay semitransparente sobre a zona de dados (ajuda leitura dos labels)
        draw_solid_overlay(card, int(H * 0.26), int(H * 0.71), TEAL, alpha=150)
        # Base solida para frase
        draw_solid_overlay(card, int(H * 0.73), int(H * BAR_START), TEAL)

        draw = ImageDraw.Draw(card)
        margin_x = 120
        max_w = W - margin_x * 2

        # Titulo
        font_title = load_font(FONT_BOLD, 72)
        y = int(H * 0.08)
        for line in wrap_text(card_data["titulo"].upper(), font_title, max_w):
            draw.text((margin_x, y), line, fill=WHITE, font=font_title)
            y += int(72 * 1.25)
        y += 20
        draw.line([(margin_x, y), (margin_x + 200, y)], fill=YELLOW, width=6)

        # Labels e valores sobre a viz do Leonardo
        draw_infografico_barras_overlay(draw, card_data, y_start=int(H * 0.30))

        # Frase destaque
        if card_data.get("frase"):
            font_frase = load_font(FONT_ITALIC, 46)
            fy = int(H * 0.76)
            frase_lines = wrap_text(card_data["frase"], font_frase, max_w - 40)
            frase_h = len(frase_lines) * int(46 * 1.35)
            draw.rectangle([(margin_x, fy), (margin_x + 8, fy + frase_h + 20)], fill=YELLOW)
            frase_y = fy + 10
            for line in frase_lines:
                draw.text((margin_x + 30, frase_y), line, fill=YELLOW, font=font_frase)
                frase_y += int(46 * 1.35)

    else:  # padrao — backward compat (fundo solido teal)
        draw = ImageDraw.Draw(card)
        if not bg_bytes:
            draw_top_stripe(draw)
        draw_text_block(draw, card_data, y_start=int(H * 0.12))

    draw_gradient_bar(card)
    card.convert("RGB").save(output_path, "JPEG", quality=95)
    print(f"  Salvo: {output_path}")


def compor_metodo(briefing, bg_bytes, output_path):
    """Card 07: Metodo NTICS — label + frase + grid 2x2 metricas + selos."""
    card = open_bg(bg_bytes) if bg_bytes else solid_bg()

    # Overlay no topo e base para legibilidade
    draw_solid_overlay(card, 0, int(H * 0.36), TEAL)
    draw_solid_overlay(card, int(H * 0.78), int(H * BAR_START), TEAL)
    # Overlay semitransparente na zona do grid (os retangulos do Leonardo ficam visiveis)
    draw_solid_overlay(card, int(H * 0.36), int(H * 0.78), TEAL, alpha=160)

    draw = ImageDraw.Draw(card)

    font_label = load_font(FONT_REGULAR, 42)
    y = int(H * 0.10)
    draw_centered_text(draw, "METODO NTICS", y, font_label, fill=TEAL_BAR)

    font_title = load_font(FONT_BOLD, 68)
    y = int(H * 0.16)
    y = draw_centered_text(draw, briefing.get("metodo_frase", ""), y, font_title, fill=WHITE, max_width=W - 200)

    y += 30
    draw.line([((W - 300) // 2, y), ((W + 300) // 2, y)], fill=YELLOW, width=4)

    metricas  = briefing.get("metodo_metricas", [])
    font_num  = load_font(FONT_BOLD, 100)
    font_desc = load_font(FONT_REGULAR, 40)

    grid_y = int(H * 0.38)
    cell_w = W // 2
    cell_h = int(H * 0.19)

    for i, metrica in enumerate(metricas[:4]):
        valor, descricao = metrica[0], metrica[1]
        col = i % 2
        row = i // 2
        cx = col * cell_w + cell_w // 2
        cy = grid_y + row * cell_h

        bbox = font_num.getbbox(valor)
        nw = bbox[2] - bbox[0]
        draw.text((cx - nw // 2, cy), valor, fill=YELLOW, font=font_num)

        desc_y = cy + int(100 * 1.2)
        bbox_d = font_desc.getbbox(descricao)
        dw = bbox_d[2] - bbox_d[0]
        draw.text((cx - dw // 2, desc_y), descricao, fill=WHITE, font=font_desc)

    font_selo = load_font(FONT_REGULAR, 34)
    draw_centered_text(draw, "Certificacao ISO 9001  |  Pacto Global ONU  |  GRI Standards",
                       int(H * 0.82), font_selo, fill=LIGHT_GRAY)

    draw_gradient_bar(card)
    card.convert("RGB").save(output_path, "JPEG", quality=95)
    print(f"  Salvo: {output_path}")


def compor_cta(briefing, bg_bytes, output_path):
    """Card 08: CTA — logo + pergunta + botao + handle."""
    card = open_bg(bg_bytes) if bg_bytes else solid_bg()

    # Overlay semitransparente para garantir legibilidade sobre o fundo decorativo
    draw_solid_overlay(card, 0, int(H * BAR_START), TEAL, alpha=185)

    draw = ImageDraw.Draw(card)

    # Logo NTICS
    logo_path = Path("brand-book/site/assets/LOGO NTICS - BRANCA.png")
    if logo_path.exists():
        logo = Image.open(logo_path).convert("RGBA")
        logo_max_h = int(H * 0.14)
        ratio = logo_max_h / logo.height
        logo_w = int(logo.width * ratio)
        logo_resized = logo.resize((logo_w, logo_max_h), Image.LANCZOS)
        lx = (W - logo_w) // 2
        card.paste(logo_resized, (lx, int(H * 0.06)), logo_resized)

    font_cta = load_font(FONT_BOLD, 68)
    y = int(H * 0.35)
    cta_text = briefing.get("cta_pergunta", "Quer levar esse conhecimento para sua empresa?")
    y = draw_centered_text(draw, cta_text, y, font_cta, fill=WHITE, max_width=W - 200)

    font_action = load_font(FONT_REGULAR, 52)
    y += 50
    draw_centered_text(draw, "Fale com a NTICS", y, font_action, fill=WHITE)

    y += 100
    font_btn = load_font(FONT_BOLD, 48)
    btn_text = "ntics.com.br"
    bbox = font_btn.getbbox(btn_text)
    bw = bbox[2] - bbox[0]
    bx = (W - bw - 80) // 2
    draw.rounded_rectangle([(bx, y), (bx + bw + 80, y + 80)], radius=40, outline=WHITE, width=4)
    draw.text((bx + 40, y + 12), btn_text, fill=WHITE, font=font_btn)

    y += 130
    draw_centered_text(draw, "@nticsprojetos", y, load_font(FONT_REGULAR, 44), fill=LIGHT_GRAY)
    y += 70
    draw_centered_text(draw, "Novo olhar para o mundo", y, load_font(FONT_ITALIC, 40), fill=LIGHT_GRAY)

    draw_gradient_bar(card)
    card.convert("RGB").save(output_path, "JPEG", quality=95)
    print(f"  Salvo: {output_path}")


# ── Descricao e Manifest ──────────────────────────────────────────────────────

def build_descricao(briefing, semana):
    cards_list = ["01-capa.jpg — Capa: " + briefing["tema"]]
    for card in briefing["cards"]:
        bg_label = card.get("bg_type", "padrao")
        cards_list.append(f"{card['slug']}.jpg — [{bg_label}] {card['titulo']}")
    cards_list.append(f"07-metodo.jpg — Metodo NTICS: {briefing.get('metodo_frase', '')}")
    cards_list.append(f"08-cta.jpg — CTA: {briefing.get('cta_pergunta', '')}")

    caption_ig = (
        f"Como sua empresa pode evoluir em {briefing['tema']}?\n\n"
        f"Este carrossel traz os conceitos essenciais para voce aplicar hoje mesmo.\n"
        f"Salve para consultar sempre que precisar!\n\n"
        f"@nticsprojetos\n"
        f"#ResponsabilidadeSocial #ESG #ImpactoSocial #ODS #NTICS"
    )
    caption_li = (
        f"Compartilhando nosso framework sobre: {briefing['tema']}\n\n"
        f"Em 8 cards, os conceitos fundamentais para empresas que querem ir alem do discurso.\n\n"
        f"O que mais ressoou com a realidade da sua empresa? Comente abaixo.\n\n"
        f"#ResponsabilidadeSocial #ESG #NTICS #ImpactoSocial"
    )

    return f"""========================================
CARROSSEL EDUCATIVO
Tema: {briefing['tema']}
Semana {semana}
========================================

--- CAPTION INSTAGRAM ---
{caption_ig}

--- CAPTION LINKEDIN ---
{caption_li}

--- ORDEM DOS CARDS ---
{chr(10).join(cards_list)}
"""


def build_manifest(briefing, semana, card_files, backgrounds):
    return {
        "tipo":                "educativo",
        "versao":              "opcao-b",
        "tema":                briefing["tema"],
        "semana":              semana,
        "gerado_em":           datetime.now().isoformat(),
        "cards":               [str(f.name) for f in card_files],
        "total_cards":         len(card_files),
        "leonardo_api_calls":  len(backgrounds),
        "bg_types":            {c["slug"]: c.get("bg_type", "padrao") for c in briefing["cards"]},
    }


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Gera carrossel educativo NTICS (Opcao B: Leonardo backgrounds + Pillow texto)"
    )
    parser.add_argument("--semana",            required=True, help="Data da semana (ex: 2026-04-07)")
    parser.add_argument("--briefing",          required=True, help="Caminho do JSON de briefing")
    parser.add_argument("--skip-backgrounds",  action="store_true",
                        help="Pular geracao Leonardo AI — usa fundos solidos (teste rapido)")
    parser.add_argument("--output",            help="Pasta de saida customizada")
    args = parser.parse_args()

    briefing_path = Path(args.briefing)
    if not briefing_path.exists():
        print(f"ERRO: Briefing nao encontrado: {briefing_path}")
        sys.exit(1)

    with open(briefing_path, "r", encoding="utf-8") as f:
        briefing = json.load(f)

    for field in ["tema", "cards"]:
        if field not in briefing:
            print(f"ERRO: Campo obrigatorio ausente: {field}")
            sys.exit(1)

    if len(briefing["cards"]) < 5:
        print(f"AVISO: Briefing tem {len(briefing['cards'])} cards (esperado 5)")

    out_dir = Path(args.output) if args.output else OUTPUT_DIR / args.semana
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*60}")
    print(f"CARROSSEL EDUCATIVO (Opcao B): {briefing['tema']}")
    print(f"Semana: {args.semana}  |  Output: {out_dir}")
    print(f"{'='*60}\n")

    # PASSO 1: Gerar todos os backgrounds em paralelo
    backgrounds = generate_all_backgrounds(briefing, skip_backgrounds=args.skip_backgrounds)

    # PASSO 2: Compor cards com overlay Pillow
    card_files = []
    print("\nComposicao dos cards...")

    print("Card 01 — Capa")
    capa_path = out_dir / "01-capa.jpg"
    compor_capa(briefing, backgrounds.get("01-capa"), str(capa_path))
    card_files.append(capa_path)

    for card_data in briefing["cards"][:5]:
        slug    = card_data.get("slug", "02-card")
        bg_type = card_data.get("bg_type", "padrao")
        print(f"Card {slug} [{bg_type}]")
        card_path = out_dir / f"{slug}.jpg"
        compor_card_conteudo(card_data, backgrounds.get(slug), str(card_path))
        card_files.append(card_path)

    print("Card 07 — Metodo NTICS")
    metodo_path = out_dir / "07-metodo.jpg"
    compor_metodo(briefing, backgrounds.get("07-metodo"), str(metodo_path))
    card_files.append(metodo_path)

    print("Card 08 — CTA")
    cta_path = out_dir / "08-cta.jpg"
    compor_cta(briefing, backgrounds.get("08-cta"), str(cta_path))
    card_files.append(cta_path)

    # PASSO 3: PDF, descricao, manifest
    print("\nGerando PDF LinkedIn...")
    images = [Image.open(str(f)).convert("RGB") for f in card_files]
    pdf_path = out_dir / "linkedin-carrossel.pdf"
    images[0].save(str(pdf_path), save_all=True, append_images=images[1:], quality=95)
    print(f"  Salvo: {pdf_path}")

    desc = build_descricao(briefing, args.semana)
    (out_dir / "descricao.txt").write_text(desc, encoding="utf-8")

    manifest = build_manifest(briefing, args.semana, card_files, backgrounds)
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"\n{'='*60}")
    print(f"CARROSSEL COMPLETO: {len(card_files)} cards + PDF")
    print(f"Leonardo AI: {len(backgrounds)} backgrounds gerados")
    print(f"Output: {out_dir}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
