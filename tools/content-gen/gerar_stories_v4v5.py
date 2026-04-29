"""
Gera 4 stories 9:16 (1080x1920) estilo hibrido v4-mascara + v5-grid para divulgar artigo.

Caracteristicas:
- Mascara hexagonal na foto (v4)
- Estrutura de paineis organizados (v5)
- Engrenagens decorativas translucidas (NTICS)
- Paleta: teal #005F73, verde #3DAA35, amarelo #F5B800, rosa #D41A6A, branco

Uso:
    python tools/content-gen/gerar_stories_v4v5.py

Output: output/marketing/stories/artigo-5-sinais-responsabilidade-social/
"""
import os
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter
from pathlib import Path
import math

# === Config ===
W, H = 1080, 1920
OUT = Path("output/marketing/stories/artigo-5-sinais-responsabilidade-social")
OUT.mkdir(parents=True, exist_ok=True)

# Paleta NTICS
TEAL = (0, 95, 115)
VERDE = (61, 170, 53)
AMARELO = (245, 184, 0)
ROSA = (212, 26, 106)
TEAL_DARK = (0, 60, 73)
CINZA_CLARO = (244, 244, 244)

# Fontes
F_BOLD = "C:/Windows/Fonts/arialbd.ttf"
F_BLACK = "C:/Windows/Fonts/ariblk.ttf" if Path("C:/Windows/Fonts/ariblk.ttf").exists() else F_BOLD
F_REGULAR = "C:/Windows/Fonts/arial.ttf"

def font(size, bold=True, black=False):
    path = F_BLACK if black else (F_BOLD if bold else F_REGULAR)
    return ImageFont.truetype(path, size)

# === Utils ===
def hexagon_mask(size):
    """Cria mascara hexagonal apontando para cima."""
    w, h = size, size
    mask = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(mask)
    cx, cy = w // 2, h // 2
    r = w // 2 - 6
    pts = [(cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a))) for a in (-60, 0, 60, 120, 180, 240)]
    d.polygon(pts, fill=255)
    return mask

def hex_photo(img_path, size=900, border_color=None, border_w=0):
    """Recorta foto em hexagono."""
    img = Image.open(img_path).convert("RGB")
    # Crop quadrado central
    w, h = img.size
    s = min(w, h)
    img = img.crop(((w - s) // 2, (h - s) // 2, (w + s) // 2, (h + s) // 2))
    img = img.resize((size, size), Image.LANCZOS)
    # Mascara hexagonal
    mask = hexagon_mask(size)
    result = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    result.paste(img, (0, 0), mask)
    # Borda opcional
    if border_color and border_w > 0:
        d = ImageDraw.Draw(result)
        cx, cy = size // 2, size // 2
        r = size // 2 - 6
        pts = [(cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a))) for a in (-60, 0, 60, 120, 180, 240)]
        pts.append(pts[0])
        d.line(pts, fill=border_color, width=border_w, joint="curve")
    return result

def paste_gear(base, pos, size, angle=0, opacity=60):
    """Cola engrenagem decorativa."""
    gear = Image.open("brand-book/site/assets/engrenagens.png").convert("RGBA")
    gear = gear.resize((size, size), Image.LANCZOS)
    gear = gear.rotate(angle, resample=Image.BICUBIC)
    # Ajusta opacidade
    alpha = gear.split()[3]
    alpha = alpha.point(lambda p: int(p * (opacity / 100)))
    gear.putalpha(alpha)
    base.alpha_composite(gear, pos)

def draw_pill(d, text, x, y, fnt, bg, fg, pad_x=40, pad_y=18, radius=40):
    """Desenha pill (badge arredondada)."""
    bbox = d.textbbox((0, 0), text, font=fnt)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    d.rounded_rectangle([x, y, x + tw + pad_x * 2, y + th + pad_y * 2], radius=radius, fill=bg)
    d.text((x + pad_x, y + pad_y - bbox[1]), text, font=fnt, fill=fg)
    return x + tw + pad_x * 2, y + th + pad_y * 2

def draw_multiline(d, text, xy, fnt, fill, line_h=None, max_w=None):
    """Desenha texto multilinha (quebra manual ou automatica por max_w)."""
    x, y = xy
    if isinstance(text, str) and max_w:
        words = text.split(" ")
        lines = []
        cur = ""
        for w in words:
            test = (cur + " " + w).strip()
            bbox = d.textbbox((0, 0), test, font=fnt)
            if bbox[2] - bbox[0] > max_w and cur:
                lines.append(cur)
                cur = w
            else:
                cur = test
        if cur:
            lines.append(cur)
    elif isinstance(text, list):
        lines = text
    else:
        lines = [text]
    lh = line_h or (fnt.size + 10)
    for i, line in enumerate(lines):
        d.text((x, y + i * lh), line, font=fnt, fill=fill)
    return y + len(lines) * lh

def base_canvas():
    """Fundo teal + engrenagens decorativas (translucidas)."""
    img = Image.new("RGBA", (W, H), TEAL + (255,))
    # engrenagens amarelas + brancas em posicoes/tamanhos/angulos variados
    gears = [
        ((-180, -200), 520, -15, 18),
        ((780, 120), 380, 25, 15),
        ((-100, 1500), 440, 40, 14),
        ((700, 1620), 350, -30, 16),
    ]
    for pos, sz, ang, op in gears:
        g = Image.open("brand-book/site/assets/engrenagens.png").convert("RGBA")
        g = g.resize((sz, sz), Image.LANCZOS).rotate(ang, resample=Image.BICUBIC, expand=True)
        # Branco com opacidade baixa
        r, gch, b, a = g.split()
        white = Image.new("L", g.size, 255)
        a = a.point(lambda p: int(p * (op / 100)))
        g_white = Image.merge("RGBA", (white, white, white, a))
        img.alpha_composite(g_white, pos)
    return img

# === STORY 1 — CAPA ===
def story_1_capa():
    img = base_canvas()
    d = ImageDraw.Draw(img)

    # Pill topo "ARTIGO · NTICS NOTES"
    draw_pill(d, "ARTIGO · NTICS NOTES", 80, 120, font(32, bold=True), VERDE, (255, 255, 255), pad_x=34, pad_y=14, radius=30)

    # Foto hexagonal central
    photo_path = "assets/melhores-fotos/5. ROBÓTICA NAS ESCOLAS/23_robotica-escolas-2ed_oficina_B_aluna-apresenta-robo-cartolina.jpg"
    hx = hex_photo(photo_path, size=880)
    img.alpha_composite(hx, ((W - 880) // 2, 300))

    # Title
    d.text((80, 1280), "OS 5 SINAIS", font=font(112, black=True), fill=(255, 255, 255))
    d.text((80, 1385), "DE MATURIDADE", font=font(94, black=True), fill=(255, 255, 255))
    d.text((80, 1490), "EM RESPONSABILIDADE", font=font(60, black=True), fill=AMARELO)
    d.text((80, 1558), "SOCIAL", font=font(60, black=True), fill=AMARELO)

    # Sub/stub
    d.text((80, 1680), "Sua empresa está no caminho certo?", font=font(34, bold=False), fill=(255, 255, 255))

    # Arrow next
    d.text((80, 1800), "ARRASTA PRO LADO  →", font=font(28, bold=True), fill=AMARELO)

    out = OUT / "story-1-capa.jpg"
    img.convert("RGB").save(out, "JPEG", quality=92, optimize=True)
    print(f"  [OK] {out}")

# === STORY 2 — GANCHO ===
def story_2_gancho():
    img = base_canvas()
    d = ImageDraw.Draw(img)

    # Pill topo
    draw_pill(d, "5 SINAIS", 80, 120, font(34, bold=True), AMARELO, TEAL, pad_x=40, pad_y=16, radius=30)

    # Pergunta grande (compactada pra liberar espaço pra lista embaixo)
    d.text((80, 260), "VOCÊ", font=font(140, black=True), fill=(255, 255, 255))
    d.text((80, 400), "RECONHECE", font=font(110, black=True), fill=(255, 255, 255))
    d.text((80, 530), "ESSES 5", font=font(110, black=True), fill=AMARELO)
    d.text((80, 660), "SINAIS?", font=font(110, black=True), fill=AMARELO)

    # Linha verde separadora
    d.rectangle([80, 1030, 400, 1038], fill=VERDE)

    # Lista dos 5 sinais com numero + nome
    sinais_curto = [
        ("01", "Estratégia"),
        ("02", "Métricas"),
        ("03", "Engajamento"),
        ("04", "Território"),
        ("05", "Aprendizado"),
    ]
    y_list = 1110
    for i, (num, nome) in enumerate(sinais_curto):
        y_item = y_list + i * 110
        # Badge circular verde com número
        d.rounded_rectangle([80, y_item, 180, y_item + 90], radius=18, fill=VERDE)
        bbox = d.textbbox((0, 0), num, font=font(48, black=True))
        tw = bbox[2] - bbox[0]
        d.text((80 + (100 - tw) // 2, y_item + 18), num, font=font(48, black=True), fill=(255, 255, 255))
        # Nome ao lado
        d.text((210, y_item + 20), nome, font=font(52, black=True), fill=(255, 255, 255))

    # CTA
    d.text((80, 1780), "ARRASTA PRA VER  →", font=font(32, bold=True), fill=AMARELO)

    out = OUT / "story-2-gancho.jpg"
    img.convert("RGB").save(out, "JPEG", quality=92, optimize=True)
    print(f"  [OK] {out}")

# === STORY 3 — LISTA DOS 5 SINAIS (v2 cards coloridos) ===
def story_3_lista():
    img = base_canvas()
    d = ImageDraw.Draw(img)

    # Header: pill + foto hexagonal ao lado
    draw_pill(d, "OS 5 SINAIS", 80, 120, font(34, bold=True), VERDE, (255, 255, 255), pad_x=40, pad_y=16, radius=30)
    photo_path = "assets/melhores-fotos/1. CONHECENDO OS ODS NAS ESCOLAS/002_ods-cultural-escolas_tecnologia_A_menino-vr-espanto-educador-mural-oceano.jpg"
    hx = hex_photo(photo_path, size=360)
    img.alpha_composite(hx, (680, 60))

    # Subtitulo enxuto abaixo do header
    d.text((80, 290), "DE MATURIDADE", font=font(56, black=True), fill=(255, 255, 255))
    d.text((80, 360), "em Responsabilidade Social", font=font(38, bold=False), fill=AMARELO)

    # 5 cards, cada um com borda lateral colorida e fundo translucido
    sinais = [
        ("01", "Integração à estratégia", "no planejamento, não só no relatório", VERDE),
        ("02", "Métricas de longo prazo", "medem transformação real, não evento", (0, 165, 184)),  # teal futuro
        ("03", "Engajamento interno", "propósito compartilhado com o time", (107, 45, 123)),  # roxo inovacao
        ("04", "Diálogo com o território", "projetos COM a comunidade, não PARA", AMARELO),
        ("05", "Aprendizado contínuo", "dados viram combustível, não só relato", ROSA),
    ]

    y = 470
    card_h = 200
    gap = 20
    for num, titulo, desc, cor in sinais:
        # Fundo translucido do card
        card = Image.new("RGBA", (W - 160, card_h), (255, 255, 255, 18))
        img.alpha_composite(card, (80, y))
        # Borda lateral grossa colorida
        d.rectangle([80, y, 96, y + card_h], fill=cor)
        # Numero grande colorido
        d.text((130, y + 50), num, font=font(96, black=True), fill=cor)
        # Titulo
        d.text((300, y + 50), titulo, font=font(46, black=True), fill=(255, 255, 255))
        # Descricao
        d.text((300, y + 118), desc, font=font(30, bold=False), fill=(220, 240, 245))
        y += card_h + gap

    # CTA final em caixa verde (igual story 4)
    cta_y = 1770
    d.rounded_rectangle([80, cta_y, W - 80, cta_y + 110], radius=28, fill=VERDE)
    bbox = d.textbbox((0, 0), "LEIA O ARTIGO COMPLETO", font=font(42, black=True))
    tw = bbox[2] - bbox[0]
    d.text(((W - tw) // 2, cta_y + 32), "LEIA O ARTIGO COMPLETO", font=font(42, black=True), fill=(255, 255, 255))

    out = OUT / "story-3-lista.jpg"
    img.convert("RGB").save(out, "JPEG", quality=92, optimize=True)
    print(f"  [OK] {out}")

# === STORY 4 — CTA ===
def story_4_cta():
    img = base_canvas()
    d = ImageDraw.Draw(img)

    # Pill topo
    draw_pill(d, "NTICS NOTES", 80, 120, font(34, bold=True), AMARELO, TEAL, pad_x=40, pad_y=16, radius=30)

    # Foto hexagonal centralizada grande
    photo_path = "assets/melhores-fotos/5. ROBÓTICA NAS ESCOLAS/06_robotica-escolas-3ed_grupo_A_equipe-plateia-ginasio-celebracao.jpg"
    hx = hex_photo(photo_path, size=780)
    img.alpha_composite(hx, ((W - 780) // 2, 280))

    # Title
    d.text((80, 1140), "LEIA O ARTIGO", font=font(100, black=True), fill=(255, 255, 255))
    d.text((80, 1240), "COMPLETO", font=font(100, black=True), fill=AMARELO)

    # Faixa verde
    d.rectangle([80, 1380, W - 80, 1392], fill=VERDE)

    # Descricao
    d.text((80, 1420), "Os 5 sinais, o método NTICS", font=font(40, bold=False), fill=(255, 255, 255))
    d.text((80, 1475), "e como identificar a maturidade", font=font(40, bold=False), fill=(255, 255, 255))
    d.text((80, 1530), "em Responsabilidade Social.", font=font(40, bold=False), fill=(255, 255, 255))

    # Instrucao forte pro link
    d.rounded_rectangle([80, 1640, W - 80, 1780], radius=30, fill=VERDE)
    bbox = d.textbbox((0, 0), "TOQUE NO LINK  ↑", font=font(54, black=True))
    tw = bbox[2] - bbox[0]
    d.text(((W - tw) // 2, 1665), "TOQUE NO LINK  ↑", font=font(54, black=True), fill=(255, 255, 255))

    # URL amigavel
    d.text((80, 1820), "ntics.com.br  ·  @nticsprojetos", font=font(28, bold=True), fill=(220, 240, 245))

    out = OUT / "story-4-cta.jpg"
    img.convert("RGB").save(out, "JPEG", quality=92, optimize=True)
    print(f"  [OK] {out}")

if __name__ == "__main__":
    print(f"Gerando 4 stories em {OUT}...")
    story_1_capa()
    story_2_gancho()
    story_3_lista()
    story_4_cta()
    print("Pronto.")
