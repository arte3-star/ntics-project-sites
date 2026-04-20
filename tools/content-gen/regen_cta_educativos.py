"""
regen_cta_educativos.py
Regenera SÓ o card 08 (CTA) dos carrosseis educativos S01, S02, S03.

Pipeline híbrido para o CTA:
  1. Leonardo gera foto bg limpa (cta_cena)
  2. Pillow aplica película teal
  3. Upload como init_image
  4. Leonardo gera CTA completo: pergunta, "Fale com a NTICS", botão, handle,
     stripes gradiente topo/rodapé — tudo desenhado pelo Leonardo com layout próprio
  5. Pillow cola logo NTICS no topo (única intervenção, garantia de brand)
  6. Reescreve descricao.txt com legendas expandidas (Instagram + LinkedIn)

Os cards 01-07 existentes NÃO são tocados.

Uso:
  python tools/content-gen/regen_cta_educativos.py              # todas (S01, S02, S03)
  python tools/content-gen/regen_cta_educativos.py --semana S01 # uma só
"""
import os, sys, time, shutil
from io import BytesIO
from pathlib import Path
import requests
from dotenv import load_dotenv
from PIL import Image

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Reutiliza funções e constantes do script principal
sys.path.insert(0, str(Path(__file__).parent))
from gerar_educativos_3semanas import (  # noqa: E402
    SEMANAS,
    aplicar_pelicula_teal,
    upload_init_image,
    start_gen,
    poll_gen,
    download,
    BASE_V2,
)

load_dotenv()
LEO_KEY = os.getenv("LEONARDO_API_KEY")

W, H = 1856, 2304

# ─── Cenas de CTA por semana ─────────────────────────────────────────────────

CTA_CENAS = {
    "S01": (
        "two business professionals shaking hands after a productive meeting in a bright "
        "modern corporate office, printed project reports and documents on the conference "
        "table in the foreground, warm golden natural light through large windows, "
        "sense of partnership and successful agreement, no screens no monitors"
    ),
    "S02": (
        "a classroom scene with a teacher warmly engaging with a group of focused Brazilian "
        "students around a table with open notebooks and books, bright welcoming school "
        "environment with large windows and natural golden afternoon light, "
        "authentic candid educational moment, no screens no monitors"
    ),
    "S03": (
        "a diverse professional team in a confident collaborative planning session around a "
        "conference table, reviewing printed documents and strategy notes together, "
        "bright modern office with large windows and warm natural light, "
        "sense of maturity and cohesion, no screens no monitors"
    ),
}


# ─── Prompts ─────────────────────────────────────────────────────────────────

_NO_TEXT = (
    " Important: absolutely NO text, NO words, NO letters, NO numbers, "
    "NO watermarks anywhere on the image."
)


def build_cta_bg_prompt(cena):
    """Foto de fundo limpa para o CTA — sem texto."""
    return (
        f"A full-bleed hyperrealistic photograph, 1856x2304px Instagram 4:5 format. "
        f"Scene: {cena}. Candid unposed moment, Canon EOS R5 35mm lens, natural warm light, "
        f"photojournalistic documentary style, visible film grain ISO 800. "
        f"No screens, no monitors, no TVs, no digital displays. Fill the entire frame edge to edge."
        + _NO_TEXT
    )


def build_cta_prompt_hybrid(cta_pergunta):
    """
    Step 2 do CTA híbrido: Leonardo desenha o card completo sobre a foto filtrada.
    Tudo rigorosamente centralizado, espaço reservado no topo para o logo que
    será colado via Pillow.
    """
    return (
        f"A social media educational carousel CTA card Instagram 4:5 format. "
        f"Keep the existing teal-filtered photo background exactly as provided, "
        f"it must remain visible with a soft dark teal overlay for text readability. "
        f"At the very top, a subtle thin gradient stripe from green to teal, no text. "
        f"The top 18 percent of the card must be clean empty teal space reserved for a logo — "
        f"no text, no elements, no decorations in this top area. "
        f"In the middle-upper region, strictly centered horizontally, a very large bold white "
        f"sans-serif question headline wrapped in maximum 3 lines: {cta_pergunta} "
        f"Below the question, strictly centered, a medium white sans-serif line: Fale com a NTICS. "
        f"Below that, strictly centered, a white rounded rectangle button outline with thin white "
        f"border containing centered white text inside: ntics.com.br. "
        f"Below the button, strictly centered, a small white sans-serif text: @nticsprojetos. "
        f"All text elements must be perfectly centered horizontally on the same vertical axis, "
        f"with generous consistent spacing between each element, creating a clean calm hierarchy. "
        f"At the very bottom a thick horizontal gradient stripe — from LEFT to RIGHT: "
        f"green on the far left, transitioning to teal, then pink, ending with orange on the far right. "
        f"No text on the gradient stripe. Professional elegant editorial CTA design, "
        f"minimalist, lots of breathing room, very well centered and balanced layout."
    )


# ─── Pillow: cola só o logo ──────────────────────────────────────────────────

def paste_logo(cta_path):
    """
    Cola o logo NTICS branco no topo-centro do card 08 gerado pelo Leonardo.
    Posição: centralizado horizontalmente, ~6% do topo.
    Altura: ~10% do card.
    """
    logo_candidates = [
        Path("brand-book/site/assets/LOGO NTICS - BRANCA.png"),
        Path("G:/O meu disco/AUTOMAÇÕES/brand-book/site/assets/LOGO NTICS - BRANCA.png"),
    ]
    logo_path = next((p for p in logo_candidates if p.exists()), None)
    if not logo_path:
        print(f"     LOGO NAO ENCONTRADO — card salvo sem logo", flush=True)
        return

    card = Image.open(cta_path).convert("RGBA")
    logo = Image.open(logo_path).convert("RGBA")

    logo_max_h = int(H * 0.10)
    ratio = logo_max_h / logo.height
    logo_w = int(logo.width * ratio)
    logo_resized = logo.resize((logo_w, logo_max_h), Image.LANCZOS)

    lx = (W - logo_w) // 2
    ly = int(H * 0.055)

    card.paste(logo_resized, (lx, ly), logo_resized)
    card.convert("RGB").save(cta_path, "JPEG", quality=95)
    print(f"     Logo aplicado ao CTA: {cta_path}", flush=True)


# ─── Descrições expandidas ───────────────────────────────────────────────────

def expanded_descricao(semana_key, s):
    """
    Legendas longas que permitem a pessoa absorver o conteúdo só pela caption,
    sem precisar abrir o carrossel. Instagram até ~2200 chars, LinkedIn até ~3000.
    """
    tema = s["tema"]
    cta = s["cta_pergunta"]
    cards = s["cards"]
    metodo = s["metodo_frase"]

    # Resumo condensado de cada card em 1 frase só
    def card_linha(c):
        titulo = c["titulo"].strip(".").strip()
        frase = c.get("frase", "").strip(".").strip()
        return f"• {titulo}. {frase}."

    resumo_cards = "\n".join(card_linha(c) for c in cards)
    cards_list_footer = "\n".join(
        [f"0{i+2}-{c['slug'].split('-', 1)[1]}.jpg — {c['titulo']}" for i, c in enumerate(cards)]
    )

    # Instagram — tom informal, acessível, com emojis suaves
    caption_ig = (
        f"{tema}.\n\n"
        f"Empresas que fazem responsabilidade social com consistência não estão apenas "
        f"cumprindo agenda. Estão construindo ativos reais: reputação, engajamento de "
        f"talentos, rating ESG, portas abertas em grandes contas e impacto mensurável "
        f"que sustenta relatórios auditáveis.\n\n"
        f"Neste carrossel, os pontos essenciais:\n\n"
        f"{resumo_cards}\n\n"
        f"{metodo}. Este é o nosso método.\n\n"
        f"{cta} Comente aqui ou fala com a gente pelo site.\n\n"
        f"Salve este carrossel para consultar sempre que precisar defender o "
        f"investimento em responsabilidade social dentro da sua empresa.\n\n"
        f"@nticsprojetos | ntics.com.br\n\n"
        f"#ResponsabilidadeSocial #ESG #ImpactoSocial #ODS #LeisDeIncentivo #NTICS "
        f"#Sustentabilidade #Rouanet #EducacaoCorporativa"
    )

    # LinkedIn — tom profissional, estrutura argumentativa
    caption_li = (
        f"{tema}.\n\n"
        f"Quem trabalha com responsabilidade social sabe: o discurso é fácil, o "
        f"resultado exige método. Investimento social com retorno real, rating ESG "
        f"sólido e reputação de marca não acontecem por acaso. Eles são fruto de um "
        f"programa estruturado, mensurável e conectado à estratégia do negócio.\n\n"
        f"Compilei aqui os conceitos que usamos com mais de 1.060 projetos executados "
        f"ao longo de 24 anos para avaliar a maturidade de um programa de RS:\n\n"
        f"{resumo_cards}\n\n"
        f"No final do carrossel, um panorama do método NTICS: {metodo}. "
        f"Certificação ISO 9001, GRI Standards, Pacto Global ONU — governança real "
        f"por trás dos números.\n\n"
        f"{cta} Deixe um comentário com a sua visão sobre o tema ou acesse ntics.com.br "
        f"para conversar sobre como estruturar um programa assim na sua empresa.\n\n"
        f"#ResponsabilidadeSocial #ESG #ImpactoSocial #Sustentabilidade #LeisDeIncentivo "
        f"#NTICS #Rouanet"
    )

    return f"""========================================
CARROSSEL EDUCATIVO
Tema: {tema}
Semana {semana_key}
========================================

--- CAPTION INSTAGRAM ---
{caption_ig}

--- CAPTION LINKEDIN ---
{caption_li}

--- ORDEM DOS CARDS ---
01-capa.jpg — Capa: {tema}
{cards_list_footer}
07-metodo.jpg — Método NTICS: {metodo}
08-cta.jpg — CTA: {cta}
"""


# ─── Pipeline ────────────────────────────────────────────────────────────────

SLUG_MAP = {
    "S01": "S01-responsabilidade-social-que-gera-resultado-de-negocio",
    "S02": "S02-educacao-como-motor",
    "S03": "S03-5-sinais-de-maturidade-em-responsabilidade-social",
}


def regenerate_cta(semana_key):
    s = SEMANAS[semana_key]
    cta_pergunta = s["cta_pergunta"]
    cta_cena = CTA_CENAS[semana_key]

    print(f"\n{'=' * 50}")
    print(f"REGEN CTA {semana_key} — {s['tema']}")
    print(f"{'=' * 50}")

    tmp_dir = Path(f".tmp/marketing/carrosseis/educativo/{semana_key}")
    tmp_dir.mkdir(parents=True, exist_ok=True)

    final_dir = Path(f"output/marketing/carrosseis/educacional/{SLUG_MAP[semana_key]}")
    # S01 e S03 têm subpasta final/, S02 tem os jpgs direto na raiz
    final_subdir = final_dir / "final"
    if final_subdir.exists():
        target_final = final_subdir
    else:
        target_final = final_dir

    # Step 1 — foto bg
    print(f"  >> Step 1: gerando foto bg", flush=True)
    gen_id = start_gen(build_cta_bg_prompt(cta_cena))
    print(f"     ID step1: {gen_id}", flush=True)
    time.sleep(60)
    bg_url = poll_gen(gen_id)
    bg_bytes = requests.get(bg_url, timeout=60).content

    # Step 2 — película teal + upload
    print(f"  >> Step 2: aplicando película e subindo init_image", flush=True)
    filtered = aplicar_pelicula_teal(bg_bytes)
    init_id = upload_init_image(filtered)
    if not init_id:
        raise RuntimeError("upload init_image falhou")
    print(f"     init_image_id: {init_id}", flush=True)

    # Step 3 — Leonardo gera CTA completo com texto
    print(f"  >> Step 3: gerando CTA com texto via Leonardo", flush=True)
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": f"Bearer {LEO_KEY}",
    }
    payload = {
        "model": "nano-banana-2",
        "parameters": {
            "prompt": build_cta_prompt_hybrid(cta_pergunta),
            "width": W,
            "height": H,
            "quantity": 1,
            "prompt_enhance": "OFF",
            "init_image_id": init_id,
            "init_strength": 0.70,
        },
        "public": False,
    }
    r = requests.post(f"{BASE_V2}/generations", headers=headers, json=payload, timeout=30)
    if not r.ok:
        raise RuntimeError(f"{r.status_code}: {r.text[:200]}")
    data = r.json()
    gen_id2 = None
    for key in ["generationId", "id"]:
        if data.get(key):
            gen_id2 = data[key]
            break
    if not gen_id2:
        for v in data.values():
            if isinstance(v, dict):
                for k in ["generationId", "id"]:
                    if v.get(k):
                        gen_id2 = v[k]
    if not gen_id2:
        raise RuntimeError(f"sem gen_id2 em {str(data)[:200]}")
    print(f"     ID step3: {gen_id2}", flush=True)
    time.sleep(60)
    cta_url = poll_gen(gen_id2)

    # Step 4 — download
    cta_tmp = tmp_dir / "08-cta.jpg"
    download(cta_url, cta_tmp)
    print(f"     CTA baixado: {cta_tmp}", flush=True)

    # Step 5 — cola logo
    paste_logo(cta_tmp)

    # Step 6 — copia para final e reescreve descricao.txt
    target_final.mkdir(parents=True, exist_ok=True)
    shutil.copy2(cta_tmp, target_final / "08-cta.jpg")
    (target_final / "descricao.txt").write_text(expanded_descricao(semana_key, s), encoding="utf-8")
    print(f"  >> PRONTO: {target_final / '08-cta.jpg'}", flush=True)
    print(f"  >> DESC:   {target_final / 'descricao.txt'}", flush=True)


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--semana", default=None, help="Processar só uma semana (S01, S02, S03)")
    args = parser.parse_args()

    alvos = [args.semana] if args.semana else ["S01", "S02", "S03"]
    for semana_key in alvos:
        if semana_key not in CTA_CENAS:
            print(f"SKIP {semana_key} — não tem cta_cena definida")
            continue
        try:
            regenerate_cta(semana_key)
        except Exception as e:
            print(f"ERRO {semana_key}: {e}", flush=True)


if __name__ == "__main__":
    main()
