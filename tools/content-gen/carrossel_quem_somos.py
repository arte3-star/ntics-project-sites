"""
Carrossel institucional QUEM SOMOS - NTICS Projetos.
7 cards 4:5, identidade NTICS (teal/verde/amarelo), via Leonardo nano-banana-2.
"""
import json, os, sys, time, requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(r"g:\O meu disco\AUTOMAÇÕES\.env")

API = os.environ["LEONARDO_API_KEY"]
HEADERS = {"Authorization": f"Bearer {API}", "Content-Type": "application/json"}

ROOT = Path(r"g:\O meu disco\AUTOMAÇÕES")
OUT = ROOT / "output" / "marketing" / "carrosseis" / "quem-somos"
OUT.mkdir(parents=True, exist_ok=True)

FOTOS = ROOT / "assets" / "melhores-fotos"
NTICS_LOGO = ROOT / "brand-book" / "site" / "assets" / "LOGO NTICS - BRANCA.png"

PHOTOS = {
    "capa":     FOTOS / "6. CAMINHAO CONHECENDO OS ODS" / "753_caminhao-ods_evento_grupo-grande-maos-levantadas-celebracao_eneva.jpg",
    "desde":    FOTOS / "2. PEC   PIE   PED" / "059_pec-pie-ped_oficina_criancas-sorrindo-mesa-atividade-colaborativa.jpg",
    "proposito":FOTOS / "9 - HUB ESG no AGRO" / "04_hub-agro_debate_A_painel-quatro-painelistas.jpg",
    "nacional": FOTOS / "1. CONHECENDO OS ODS NAS ESCOLAS" / "113_ods-escolas_evento_educador-apresentando-ods-criancas-ao-ar-livre.jpg",
    "numeros":  FOTOS / "5. ROBÓTICA NAS ESCOLAS" / "072_robotica-escolas_robotica_criancas-apresentando-robo-feito-papelao.jpg",
    "ods":      FOTOS / "4. FESTIVAL CONHECENDO OS ODS" / "004_festival-ods_evento_palestrantes-apresentacao-festival-digital-mainstage.png",
    "cta":      FOTOS / "PEÇAS TEATRAIS" / "055_pecas-teatrais_teatro_criancas-posando-com-atores-palco-teatral.jpg",
}

W, H = 1856, 2304


def upload(path: Path) -> str:
    ext = path.suffix.lstrip(".").lower().replace("jpeg", "jpg")
    r = requests.post(
        "https://cloud.leonardo.ai/api/rest/v1/init-image",
        headers=HEADERS, json={"extension": ext},
    )
    r.raise_for_status()
    up = r.json()["uploadInitImage"]
    init_id = up["id"]
    fields = json.loads(up["fields"])
    with open(path, "rb") as f:
        r2 = requests.post(up["url"], data=fields, files={"file": (path.name, f)})
    r2.raise_for_status()
    print(f"  uploaded {path.name[:60]} -> {init_id}")
    return init_id


def generate(prompt: str, refs: list[str], slug: str) -> str:
    payload = {
        "model": "nano-banana-2",
        "parameters": {
            "prompt": prompt,
            "width": W, "height": H,
            "quantity": 1, "prompt_enhance": "OFF",
            "guidances": {"image_reference": [
                {"image": {"id": rid, "type": "UPLOADED"}, "strength": "HIGH"} for rid in refs
            ]},
        },
        "public": False,
    }
    r = requests.post("https://cloud.leonardo.ai/api/rest/v2/generations",
                      headers=HEADERS, json=payload)
    if r.status_code >= 400:
        print(f"  ERROR {r.status_code}: {r.text[:400]}")
        r.raise_for_status()
    body = r.json()
    gid = (body.get("generate") or {}).get("generationId") or \
          (body.get("sdGenerationJob") or {}).get("generationId")
    if not gid:
        raise RuntimeError(f"no gen id: {json.dumps(body)[:400]}")
    print(f"  [{slug}] gen id: {gid} (prompt {len(prompt)} chars)")
    return gid


def poll(gid: str, slug: str) -> str:
    for attempt in range(40):
        time.sleep(8 if attempt == 0 else 5)
        r = requests.get(f"https://cloud.leonardo.ai/api/rest/v1/generations/{gid}",
                         headers=HEADERS)
        r.raise_for_status()
        gen = r.json()["generations_by_pk"]
        s = gen.get("status")
        if s == "COMPLETE":
            url = gen["generated_images"][0]["url"]
            print(f"  [{slug}] DONE")
            return url
        if s == "FAILED":
            raise RuntimeError(f"{slug} FAILED")
        print(f"  [{slug}] {s}... ({attempt+1})")
    raise TimeoutError(slug)


def download(url: str, path: Path):
    r = requests.get(url, timeout=60); r.raise_for_status()
    path.write_bytes(r.content)
    print(f"  saved -> {path.name}")


PALETTE = (
    "NTICS palette: dark teal #005F73 base, bright green #3DAA35 badges, "
    "yellow #F5B800 number highlights, pink #D41A6A and orange #E86428 accents, "
    "white text. Bottom edge: a single thin smooth gradient stripe going left to right, "
    "blending green into teal into pink into orange. The stripe is PURELY DECORATIVE "
    "and contains NO TEXT, NO HEX CODES, NO LABELS, NO COLOR NAMES, NO HASHTAGS, NO NUMBERS. "
    "DO NOT print color codes anywhere on the card. DO NOT add tricolor ruler, sponsor logo bar, "
    "watermark, color-swatch labels, or layout markers."
)

PROMPTS = {
    # Tela 1 - capa: fullbleed cinematografico, overlay teal nos 40% inferiores
    "01-capa": (
        "Instagram carousel cover 4:5, edge to edge no white borders. "
        "FULLBLEED: the FIRST reference image, a real photo of a large crowd "
        "with hands raised celebrating, full bleed, vivid natural colors, faces preserved. "
        "Apply a dark teal #005F73 overlay over the BOTTOM 45 percent only, smooth gradient transition. "
        "On that overlay: monumental headline in bold sans-serif uppercase WHITE, three lines: "
        "'VIABILIZAMOS PROJETOS' / 'DE IMPACTO SOCIAL' / 'HÁ MAIS DE 20 ANOS'. "
        "Below the headline a small green #3DAA35 pill badge with WHITE uppercase 'QUEM SOMOS'. "
        "Top-right corner: small white NTICS Projetos wordmark. "
        f"{PALETTE} Editorial institutional design, high contrast."
    ),
    # Tela 2 - desde 2002: layout invertido (top 45% teal, bottom foto)
    "02-desde": (
        "Instagram card 4:5 inverted layout. "
        "TOP 50 percent: solid dark teal #005F73 block. On it, large bold sans-serif "
        "uppercase WHITE headline three lines: 'DESDE 2002,' / 'CONECTAMOS EDUCAÇÃO,' / "
        "'SUSTENTABILIDADE E INOVAÇÃO'. Below in smaller WHITE light text: "
        "'ao propósito de grandes empresas.'. Small yellow #F5B800 highlight strip under the year 2002. "
        "Subtle white gear icons at 12 percent opacity decorating the teal area. "
        "BOTTOM 50 percent: the FIRST reference image, real photo of children smiling at a "
        "collaborative workshop table, full bleed, faces preserved, vivid colors. "
        "Smooth horizontal transition between the two halves. "
        f"{PALETTE}"
    ),
    # Tela 3 - proposito empresas: diagonal 30°
    "03-proposito": (
        "Instagram card 4:5 with a diagonal split at about 30 degrees. "
        "LEFT-LOWER triangle: the FIRST reference image, real photo of four panelists at a "
        "corporate ESG debate panel, full bleed, faces preserved. "
        "RIGHT-UPPER triangle: solid dark teal #005F73 with subtle white gear icons at 15 percent opacity. "
        "On the teal triangle: small green #3DAA35 pill badge with WHITE uppercase 'PROPÓSITO'. "
        "Below it bold sans-serif uppercase WHITE headline three lines: 'TRANSFORMAMOS' / "
        "'O PROPÓSITO DAS EMPRESAS' / 'EM IMPACTO REAL'. Smaller WHITE body text: "
        "'Projetos de impacto social com resultados mensuráveis.'. "
        f"{PALETTE}"
    ),
    # Tela 4 - atuacao nacional: foto a esquerda 60% + 3 blocos solidos a direita
    "04-nacional": (
        "Instagram card 4:5 with two columns. "
        "LEFT column 58 percent width, full height: the FIRST reference image, real photo of "
        "an educator presenting SDG concepts to children outdoors, faces preserved, vivid colors, "
        "with rounded outer corners on the right edge. "
        "RIGHT column 42 percent width: three stacked solid blocks of equal height. "
        "Top block GREEN #3DAA35: bold uppercase WHITE 'ATUAÇÃO' / 'NACIONAL' centered, two lines. "
        "Middle block TEAL #005F73: smaller WHITE text 'Projetos em todo o Brasil' centered. "
        "Bottom block PINK #D41A6A: smaller WHITE text 'conectando empresas e comunidades' centered. "
        f"{PALETTE}"
    ),
    # Tela 5 - numeros: grid de stats sobre fundo teal com foto integrada
    "05-numeros": (
        "Instagram card 4:5 stats layout. "
        "TOP 35 percent: the FIRST reference image, real photo of children proudly presenting "
        "a cardboard robot, full bleed, faces preserved, vivid colors. "
        "BOTTOM 65 percent: solid dark teal #005F73 background with subtle white gear icons "
        "at 10 percent opacity. On it, four stat lines stacked, each with a HUGE bold YELLOW "
        "#F5B800 number on the left and a smaller WHITE label on the right: "
        "'+1.108 projetos realizados', '+11 milhões de pessoas impactadas', "
        "'+48 mil professores capacitados', '+4.230 empregos gerados'. "
        "Small green #3DAA35 pill badge above the numbers with WHITE uppercase 'NOSSOS NÚMEROS'. "
        f"{PALETTE} Numbers use a period for thousands and the plus sign before each."
    ),
    # Tela 6 - Pacto Global / ODS
    "06-ods": (
        "Instagram card 4:5. "
        "UPPER 55 percent: the FIRST reference image, real photo of speakers on a digital "
        "main stage about sustainable development goals, full bleed, faces preserved. "
        "LOWER 45 percent: solid dark teal #005F73 panel. On it: small green #3DAA35 pill "
        "badge with WHITE uppercase 'COMPROMISSO'. Bold sans-serif uppercase WHITE headline "
        "two lines: 'SIGNATÁRIA DO' / 'PACTO GLOBAL DA ONU'. Below in smaller WHITE text: "
        "'Atuação alinhada aos Objetivos de Desenvolvimento Sustentável.'. "
        "A small horizontal row of 4 colored squares (green, teal, pink, orange) decorating the panel. "
        f"{PALETTE}"
    ),
    # Tela 7 - CTA
    "07-cta": (
        "Instagram card 4:5 final CTA. "
        "Full background dark teal #005F73 with subtle white gear icons at 12 percent opacity "
        "orbiting around the center. "
        "CENTER: the FIRST reference image cropped into a circular frame, real photo of "
        "children and actors posing on a colorful theatrical stage, faces preserved, vivid colors, "
        "with a thin white outline around the circle. "
        "ABOVE the circle, bold sans-serif uppercase WHITE small label: 'PRAZER, SOMOS A'. "
        "Then huge bold YELLOW #F5B800 wordmark 'NTICS PROJETOS' centered, one line. "
        "BELOW the circle, large bold sans-serif uppercase WHITE headline two lines: "
        "'VAMOS' / 'TRANSFORMAR JUNTOS?'. "
        "Bottom: small WHITE handle '@nticsprojetos' centered. "
        f"{PALETTE}"
    ),
}

CARDS = [
    ("01-capa",      ["capa"]),
    ("02-desde",     ["desde"]),
    ("03-proposito", ["proposito"]),
    ("04-nacional",  ["nacional"]),
    ("05-numeros",   ["numeros"]),
    ("06-ods",       ["ods"]),
    ("07-cta",       ["cta"]),
]


def main():
    only = sys.argv[1] if len(sys.argv) > 1 else None

    for k, p in PHOTOS.items():
        if not p.exists():
            raise FileNotFoundError(f"{k}: {p}")

    print(f"Output: {OUT}\n")
    print("Uploading photos...")
    ids = {k: upload(p) for k, p in PHOTOS.items()}

    print("\nGenerating cards...")
    for slug, ref_keys in CARDS:
        if only and only not in slug:
            continue
        out_path = OUT / f"{slug}.jpg"
        if out_path.exists() and not only:
            print(f"  [{slug}] exists, skip")
            continue
        prompt = PROMPTS[slug]
        if len(prompt) >= 1500:
            print(f"  [{slug}] WARN prompt {len(prompt)} chars >= 1500")
        refs = [ids[k] for k in ref_keys]
        gid = generate(prompt, refs, slug)
        url = poll(gid, slug)
        download(url, out_path)


if __name__ == "__main__":
    main()
