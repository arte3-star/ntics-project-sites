"""
Carrossel projeto 120 Negocio Cultural 2a Edicao (Porto Itapoa).
Fase Durante - "Acontecendo agora / Ainda da tempo".
8 cards no padrao PIE: template visual + foto + logo por card.
"""
import json, os, sys, time, requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(r"g:\O meu disco\AUTOMAÇÕES\.env")
API = os.environ["LEONARDO_API_KEY"]
HEADERS = {"Authorization": f"Bearer {API}", "Content-Type": "application/json"}

ROOT = Path(r"g:\O meu disco\AUTOMAÇÕES")
OUT = ROOT / "output/marketing/carrosseis/projetos/120-negocio-cultural-itapoa/v1"
OUT.mkdir(parents=True, exist_ok=True)
LOG = OUT / "geracao.log"

PROJECT_BASE = next(ROOT.glob("assets/projetos/120. NEG*PORTO*"))
TEMPLATE = PROJECT_BASE / "identidade-visual" / "banners" / "BANNER - Porto Itapoá.png"
PROJECT_LOGO = PROJECT_BASE / "LOGOS" / "negocio_cultural_logo.png"
SPONSOR_LOGO = PROJECT_BASE / "LOGOS" / "porto_itapoa_logo.png"

PHOTOS_DIR = ROOT / "assets" / "melhores-fotos" / "10 - Negócio Cultural"
PHOTOS = {
    "capa":         PHOTOS_DIR / "07_negocio-cultural_empreendedorismo_A_equipe-aplaudindo-banner.jpg",
    "projeto":      PHOTOS_DIR / "11_negocio-cultural_capacitacao_A_facilitadora-gesticulando-banner.jpg",
    "patrocinador": PHOTOS_DIR / "10_negocio-cultural_empreendedorismo_A_palestrante-convidado-banner.jpg",
    "alcance":      PHOTOS_DIR / "01_negocio-cultural_capacitacao_B_facilitadora-costas-plateia-cheia.jpg",
    "como_funciona":PHOTOS_DIR / "02_negocio-cultural_oficina_A_facilitadora-azul-espaco-rustico.jpg",
    "acontecendo":  Path(r"C:\Users\lucas\Downloads\Rejane - Imagem Profissional-4.jpg"),
    "depoimento":   PHOTOS_DIR / "06_negocio-cultural_capacitacao_B_plateia-sorrindo-conversa.jpg",
    "ainda_da_tempo": PHOTOS_DIR / "03_negocio-cultural_capacitacao_A_facilitadora-amarelo-plateia-sala.jpg",
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
        requests.post(up["url"], data=fields, files={"file": (path.name, f)}).raise_for_status()
    print(f"  uploaded {path.name[:50]} -> {init_id}")
    return init_id


def generate(prompt: str, refs: list[str], slug: str) -> str:
    assert len(refs) <= 3
    assert len(prompt) < 1500, f"prompt {len(prompt)} chars (max 1500)"
    payload = {
        "model": "nano-banana-2",
        "parameters": {
            "prompt": prompt, "width": W, "height": H,
            "quantity": 1, "prompt_enhance": "OFF",
            "guidances": {"image_reference": [
                {"image": {"id": rid, "type": "UPLOADED"}, "strength": "HIGH"}
                for rid in refs
            ]},
        },
        "public": False,
    }
    r = requests.post(
        "https://cloud.leonardo.ai/api/rest/v2/generations", headers=HEADERS, json=payload
    )
    if r.status_code >= 400:
        print(f"  ERROR {r.status_code}: {r.text[:400]}")
        r.raise_for_status()
    body = r.json()
    if not isinstance(body, dict):
        print(f"  BODY: {json.dumps(body)[:600]}")
        raise RuntimeError("validation error")
    gid = (body.get("generate") or {}).get("generationId")
    print(f"  [{slug}] gen id: {gid}")
    with LOG.open("a", encoding="utf-8") as f:
        f.write(f"{slug}\t{gid}\t{int(time.time())}\n")
    return gid


def poll(gid: str, slug: str) -> str:
    for i in range(30):
        time.sleep(8 if i == 0 else 5)
        r = requests.get(
            f"https://cloud.leonardo.ai/api/rest/v1/generations/{gid}", headers=HEADERS
        )
        r.raise_for_status()
        gen = r.json()["generations_by_pk"]
        s = gen.get("status")
        if s == "COMPLETE":
            print(f"  [{slug}] DONE")
            return gen["generated_images"][0]["url"]
        if s == "FAILED":
            raise RuntimeError(f"{slug} FAILED")
        print(f"  [{slug}] {s}... ({i+1})")
    raise TimeoutError()


def download(url: str, path: Path):
    path.write_bytes(requests.get(url, timeout=60).content)
    print(f"  saved -> {path.name}")


# Paleta Negocio Cultural Porto Itapoa: navy #1B3A5C, red #E2342A, yellow #FFB800, green #5BA749
PALETTE = (
    "Project palette: navy #1B3A5C primary, red #E2342A, yellow #FFB800, green #5BA749, white. "
    "Decorative confetti: floating yellow gears, red speech bubbles, green leaves, "
    "small white pencil icons (visual vocabulary of the project). "
    "NO BLACK for any text. DO NOT add any tricolor stripe ruler or sponsor-logo bar at the bottom edge."
)

PROMPTS = {
    "01-capa": (
        f"Vertical 4:5 Instagram carousel cover. {PALETTE} "
        "Top thin label in navy uppercase: 'PORTO ITAPOA APRESENTA'. "
        "UPPER 45 percent: SECOND reference image, full bleed photograph, no overlay. "
        "Below the photo on navy area, large white circle with the THIRD reference image "
        "(Negocio Cultural logo: blue and red handshake) preserved pixel-for-pixel. "
        "BOTTOM 22 percent: clean white rounded panel. Bold navy headline in two lines: "
        "'ACONTECENDO' / 'AGORA EM ITAPOÁ'. Below in smaller red italic: '2ª edição'."
    ),
    "02-projeto": (
        f"Vertical 4:5 Instagram carousel content card. {PALETTE} "
        "UPPER 55 percent: SECOND reference image, full bleed photograph, no overlay. "
        "Small navy pill badge below photo with white text 'O PROJETO'. "
        "Then bold navy headline: 'FORMAÇÃO GRATUITA EM EMPREENDEDORISMO'. "
        "Below in smaller red text: 'O Negócio Cultural conecta empreendedores locais "
        "a especialistas, com conteúdo prático e aplicável ao dia a dia dos negócios.'"
    ),
    "03-patrocinador": (
        f"Vertical 4:5 Instagram carousel content card. {PALETTE} "
        "UPPER 55 percent: FIRST reference image, full bleed photograph, no overlay. "
        "MIDDLE: SECOND reference image (Porto Itapoa logo with green and red icon) on a "
        "small white pill, preserved pixel-for-pixel exactly as the reference, original colors. "
        "BOTTOM 30 percent: clean white rounded panel. Bold navy headline: "
        "'O PATROCÍNIO QUE TORNA O PROJETO POSSÍVEL'. Below in smaller red text: "
        "'A Porto Itapoá apoia a 2ª edição do Negócio Cultural na cidade.'"
    ),
    "04-alcance": (
        f"Vertical 4:5 Instagram carousel content card. {PALETTE} "
        "UPPER 50 percent: SECOND reference image, full bleed photograph, no overlay. "
        "Small red pill badge below photo with white text 'PARA QUEM'. "
        "Then bold navy headline in three lines: 'EMPREENDEDORES,' / 'PRODUTORES' / "
        "'E COMUNIDADE LOCAL'. Below in smaller red text: 'Itapoá - SC'."
    ),
    "05-como-funciona": (
        f"Vertical 4:5 Instagram carousel content card. {PALETTE} "
        "UPPER 45 percent: SECOND reference image, full bleed photograph, no overlay. "
        "Small yellow pill badge below photo with navy text 'COMO FUNCIONA'. "
        "Then a vertical numbered list, four lines bold navy with the numbers in red: "
        "'1. Aulas com especialistas', '2. Trilha prática', '3. Conteúdo aplicável', "
        "'4. Certificado'."
    ),
    "06-acontecendo": (
        f"Vertical 4:5 Instagram carousel content card. {PALETTE} "
        "UPPER 55 percent: SECOND reference image, full bleed photograph, no overlay. "
        "Small green pill badge below photo with white text 'ACONTECENDO'. "
        "Then bold navy headline: 'TRANSFORMANDO IDEIAS EM PRÁTICA'. "
        "Below in smaller red text: 'Os encontros já estão fortalecendo negócios locais "
        "com aprendizado direto e aplicável.'"
    ),
    "07-ainda-da-tempo": (
        f"Vertical 4:5 Instagram carousel content card. {PALETTE} "
        "UPPER 50 percent: SECOND reference image, full bleed photograph, no overlay. "
        "Small red pill badge below photo with white text 'AINDA DÁ TEMPO'. "
        "Then bold navy headline: 'DOIS MÓDULOS IMPERDÍVEIS PELA FRENTE'. "
        "Below in smaller red text: 'Produção Audiovisual que Gera Resultados, "
        "Marketing Digital e Vendas. Inscreva-se gratuitamente.'"
    ),
    "08-cta": (
        f"Vertical 4:5 Instagram carousel final CTA card. {PALETTE} "
        "Upper-middle: large white center circle holding the SECOND reference image "
        "(Negocio Cultural project logo: blue and red handshake) preserved pixel-for-pixel. "
        "Above the circle, large bold navy headline centered on white strip: 'INSCREVA-SE'. "
        "Below in smaller red italic: 'ainda dá tempo de participar'. "
        "BOTTOM 22 percent: clean white footer panel split in two columns. "
        "LEFT label small navy uppercase 'REALIZAÇÃO' below the FIRST reference image "
        "(NTICS Projetos logo with green lightbulb and gears) preserved pixel-for-pixel. "
        "RIGHT label small navy uppercase 'PATROCÍNIO' below the THIRD reference image "
        "(Porto Itapoa logo) preserved pixel-for-pixel."
    ),
}

CARDS = [
    ("01-capa",          ["template", "capa", "project_logo"]),
    ("02-projeto",       ["template", "projeto"]),
    ("03-patrocinador",  ["template", "patrocinador", "sponsor_logo"]),
    ("04-alcance",       ["template", "alcance"]),
    ("05-como-funciona", ["template", "como_funciona"]),
    ("06-acontecendo",   ["template", "acontecendo"]),
    ("07-ainda-da-tempo",["template", "ainda_da_tempo"]),
    ("08-cta",           ["ntics_logo", "project_logo", "sponsor_logo"]),
]


def main():
    only = sys.argv[1] if len(sys.argv) > 1 else None
    print("Uploading...")
    ids = {
        "template": upload(TEMPLATE),
        "project_logo": upload(PROJECT_LOGO),
        "sponsor_logo": upload(SPONSOR_LOGO),
        "ntics_logo": upload(ROOT / "brand-book/site/assets/LOGO NTICS.png"),
    }
    for k, p in PHOTOS.items():
        ids[k] = upload(p)

    print("\nGenerating cards...")
    for slug, ref_keys in CARDS:
        if only and only not in slug:
            continue
        out_path = OUT / f"{slug}.jpg"
        if out_path.exists() and not only:
            print(f"  [{slug}] exists, skip")
            continue
        refs = [ids[k] for k in ref_keys]
        prompt = PROMPTS[slug]
        gid = generate(prompt, refs, slug)
        url = poll(gid, slug)
        download(url, out_path)


if __name__ == "__main__":
    main()
