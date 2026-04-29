"""
Carrossel PIE Guarulhos - Pre-projeto - v2
Sem cor preta em nenhum texto. Apenas paleta PIE.
Sem regua tricolor no rodape.
Brand logos (GRU AIRPORT, NTICS) preservados como sao.
"""
import json, os, sys, time, requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(r"g:\O meu disco\AUTOMACOES\.env")
load_dotenv(r"g:\O meu disco\AUTOMAÇÕES\.env")

API = os.environ["LEONARDO_API_KEY"]
HEADERS = {"Authorization": f"Bearer {API}", "Content-Type": "application/json"}

ROOT = Path(r"g:\O meu disco\AUTOMAÇÕES\output\marketing\carrosseis\projetos\pie")
OUT = ROOT / "v2"
OUT.mkdir(parents=True, exist_ok=True)

TEMPLATE = ROOT / "Design referencia" / "Prancheta 1 (3).png"
GRU_LOGO = ROOT / "Design referencia" / "gru_logo_descritivo.png"
NTICS_LOGO = Path(r"g:\O meu disco\AUTOMAÇÕES\brand-book\site\assets\LOGO NTICS.png")

PHOTOS = {
    "capa":         ROOT / "WhatsApp Image 2026-04-18 at 11.17.33 (1).jpeg",
    "projeto":      ROOT / "WhatsApp Image 2026-04-18 at 11.17.37.jpeg",
    "empresa":      ROOT / "WhatsApp Image 2026-04-18 at 11.17.37 (2).jpeg",
    "alcance":      ROOT / "WhatsApp Image 2026-04-23 at 17.01.57.jpeg",
    "como_funciona":ROOT / "WhatsApp Image 2026-04-18 at 11.17.37 (1).jpeg",
    "expectativa":  ROOT / "WhatsApp Image 2026-04-23 at 08.57.10.jpeg",
    "impacto":      ROOT / "WhatsApp Image 2026-04-18 at 11.17.33.jpeg",
}

W, H = 1856, 2304


def upload(path: Path) -> str:
    r = requests.post(
        "https://cloud.leonardo.ai/api/rest/v1/init-image",
        headers=HEADERS,
        json={"extension": path.suffix.lstrip(".").lower().replace("jpeg", "jpg")},
    )
    r.raise_for_status()
    up = r.json()["uploadInitImage"]
    init_id = up["id"]
    fields = json.loads(up["fields"])
    with open(path, "rb") as f:
        r2 = requests.post(up["url"], data=fields, files={"file": (path.name, f)})
    r2.raise_for_status()
    print(f"  uploaded {path.name} -> {init_id}")
    return init_id


def generate(prompt: str, refs: list[str], slug: str) -> str:
    image_reference = [
        {"image": {"id": rid, "type": "UPLOADED"}, "strength": "HIGH"} for rid in refs
    ]
    payload = {
        "model": "nano-banana-2",
        "parameters": {
            "prompt": prompt,
            "width": W,
            "height": H,
            "quantity": 1,
            "prompt_enhance": "OFF",
            "guidances": {"image_reference": image_reference},
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
    gid = None
    if isinstance(body, dict):
        gid = (body.get("generate") or {}).get("generationId") or (
            body.get("sdGenerationJob") or {}
        ).get("generationId")
    if not gid:
        print(f"  [{slug}] body: {json.dumps(body)[:600]}")
        raise RuntimeError(f"no generation id for {slug}")
    print(f"  [{slug}] gen id: {gid}")
    return gid


def poll(gid: str, slug: str) -> str:
    for attempt in range(30):
        time.sleep(8 if attempt == 0 else 5)
        r = requests.get(
            f"https://cloud.leonardo.ai/api/rest/v1/generations/{gid}", headers=HEADERS
        )
        r.raise_for_status()
        gen = r.json()["generations_by_pk"]
        status = gen.get("status")
        if status == "COMPLETE":
            url = gen["generated_images"][0]["url"]
            print(f"  [{slug}] DONE")
            return url
        if status == "FAILED":
            raise RuntimeError(f"{slug} FAILED: {gen}")
        print(f"  [{slug}] {status}... ({attempt+1})")
    raise TimeoutError(f"{slug} timeout")


def download(url: str, path: Path):
    r = requests.get(url, timeout=60)
    r.raise_for_status()
    path.write_bytes(r.content)
    print(f"  saved -> {path.name}")


PALETTE_RULE = (
    "STRICT COLOR RULE: NO BLACK COLOR ANYWHERE in this card. All text MUST use the PIE "
    "palette only: magenta #D6116D, teal #1BA9B7, vivid orange #E68427, lime green #C7D435, "
    "or white. NEVER use black for text, badges, headlines, or labels. The only exception is "
    "brand logos provided as reference images (those keep their original colors). "
    "Use small floating colored squares (magenta, lime, orange, teal) as decorative confetti. "
    "DO NOT add any tricolor stripe, ruler, footer bar, partner-logo bar, or government "
    "sponsor strip at the bottom edge. The card ends with the white panel or the colored blocks."
)

PROMPTS = {
    "01-capa": (
        "Instagram carousel cover 4:5. Match the visual identity of the FIRST reference image "
        "(PIE brand template) exactly: vertical color blocks magenta, teal and orange across "
        "the card with floating colored squares, large white center circle holding the P.I.E logo. "
        f"{PALETTE_RULE} "
        "Top thin label in MAGENTA #D6116D sans-serif: 'GRU AIRPORT APRESENTA'. "
        "UPPER 45 percent: SECOND reference image, full bleed photograph, no overlay. "
        "Below the photo, on the colored blocks, a large white center circle with bold magenta "
        "P.I.E logo and small magenta text 'EMPREENDEDORISMO É ARTE - 2ª EDIÇÃO'. "
        "BOTTOM 22 percent: a clean white rounded panel with generous padding holding the "
        "headline in three lines, bold sans-serif in MAGENTA #D6116D: "
        "'CHEGOU EM' / 'GUARULHOS' (large), and below in smaller TEAL #1BA9B7 text 'em sua 2ª edição'. "
        "Clean editorial design."
    ),
    "02-projeto": (
        "Instagram carousel content card 4:5. Match the visual identity of the FIRST reference "
        "image (PIE brand template) exactly: vertical color blocks magenta, teal and orange, "
        "floating colored squares. "
        f"{PALETTE_RULE} "
        "UPPER 55 percent: SECOND reference image, full bleed photograph, no overlay. "
        "Small MAGENTA #D6116D pill badge below photo with WHITE text 'O PROJETO'. "
        "Then bold MAGENTA #D6116D headline: 'ARTE, EMPREENDEDORISMO E IA NA ESCOLA'. "
        "Below in smaller TEAL #1BA9B7 text: 'Estudantes e professores da rede pública de "
        "Guarulhos vivem um novo jeito de aprender.'"
    ),
    "03-empresa": (
        "Instagram carousel content card 4:5. Match the visual identity of the FIRST reference "
        "image (PIE brand template) exactly: vertical color blocks magenta, teal and orange, "
        "floating colored squares. Same layout as the other cards in this carousel. "
        f"{PALETTE_RULE} "
        "UPPER 55 percent: SECOND reference image, full bleed photograph, no overlay. "
        "MIDDLE: the THIRD reference image is the GRU AIRPORT logo. Place it centered on a "
        "small white pill, perfectly preserved pixel-for-pixel exactly as the reference, "
        "keeping its original logo colors. "
        "BOTTOM 30 percent: clean white rounded panel with bold MAGENTA #D6116D headline "
        "'O PATROCÍNIO QUE TORNA O PIE POSSÍVEL', and below in smaller TEAL #1BA9B7 text "
        "'A GRU Airport patrocina a 2ª edição do PIE em Guarulhos.'"
    ),
    "04-alcance": (
        "Instagram carousel content card 4:5. Match the visual identity of the FIRST reference "
        "image (PIE brand template) exactly: vertical color blocks magenta, teal and orange, "
        "floating colored squares. "
        f"{PALETTE_RULE} "
        "UPPER 50 percent: SECOND reference image, full bleed photograph, no overlay. "
        "Small TEAL #1BA9B7 pill badge below photo with WHITE text 'ALCANCE'. "
        "Then huge bold MAGENTA #D6116D numbers stacked: '3.000' estudantes and '100' "
        "professores, with the labels 'estudantes' and 'professores' in smaller TEAL #1BA9B7 "
        "text under each number. At the bottom: 'em Guarulhos' in ORANGE #E68427."
    ),
    "05-como-funciona": (
        "Instagram carousel content card 4:5. Match the visual identity of the FIRST reference "
        "image (PIE brand template) exactly: vertical color blocks magenta, teal and orange, "
        "floating colored squares. "
        f"{PALETTE_RULE} "
        "UPPER 45 percent: SECOND reference image, full bleed photograph, no overlay. "
        "Small ORANGE #E68427 pill badge below photo with WHITE text 'COMO FUNCIONA'. "
        "Then a vertical numbered list, four lines in bold MAGENTA #D6116D, with the numbers "
        "'1.', '2.', '3.', '4.' in TEAL #1BA9B7: "
        "'1. Palestra de abertura', '2. Formação de professores', "
        "'3. Oficinas em sala de aula', '4. Feira de Ideias'."
    ),
    "06-expectativa": (
        "Instagram carousel content card 4:5. Match the visual identity of the FIRST reference "
        "image (PIE brand template) exactly: vertical color blocks magenta, teal and orange, "
        "floating colored squares. "
        f"{PALETTE_RULE} "
        "UPPER 55 percent: SECOND reference image, full bleed photograph, no overlay. "
        "Small LIME GREEN #C7D435 pill badge below photo with MAGENTA #D6116D text 'EXPECTATIVA'. "
        "Then bold MAGENTA #D6116D headline: 'CADA TURMA, UM DESAFIO REAL'. "
        "Below in smaller TEAL #1BA9B7 text: 'Os estudantes criam projetos a partir de "
        "desafios do próprio cotidiano e apresentam na Feira de Ideias.'"
    ),
    "07-impacto": (
        "Instagram carousel content card 4:5. Match the visual identity of the FIRST reference "
        "image (PIE brand template) exactly: vertical color blocks magenta, teal and orange, "
        "floating colored squares. "
        f"{PALETTE_RULE} "
        "UPPER 50 percent: SECOND reference image, full bleed photograph, no overlay. "
        "Small MAGENTA #D6116D pill badge below photo with WHITE text 'IMPACTO'. "
        "Then bold MAGENTA #D6116D headline: 'ARTE, TECNOLOGIA E EMPREENDEDORISMO NA SALA DE AULA'. "
        "Below in smaller TEAL #1BA9B7 text: 'Guarulhos vai mostrar o que acontece quando "
        "essas três linguagens entram juntas na escola pública.'"
    ),
    "08-cta": (
        "Instagram carousel final CTA card 4:5. Match the visual identity of the FIRST "
        "reference image (PIE brand template) exactly: vertical color blocks magenta, teal "
        "and orange with floating colored squares, large white center circle. "
        f"{PALETTE_RULE} "
        "Upper-middle: a large white center circle holding the bold magenta P.I.E logo with "
        "small magenta text 'EMPREENDEDORISMO É ARTE - 2ª EDIÇÃO'. "
        "Above the circle, large bold MAGENTA #D6116D headline centered on a white strip: "
        "'EM BREVE, O PIE COMEÇA'. "
        "BOTTOM 24 percent: a clean white footer panel divided in two columns side by side. "
        "LEFT column label in small MAGENTA #D6116D uppercase 'REALIZAÇÃO' and below it the "
        "SECOND reference image which is the NTICS Projetos logo (green lightbulb with gears "
        "plus NTICS PROJETOS wordmark), preserved pixel-for-pixel exactly as the reference, "
        "keeping its original colors. "
        "RIGHT column label in small MAGENTA #D6116D uppercase 'PATROCÍNIO' and below it the "
        "THIRD reference image which is the GRU AIRPORT logo, preserved pixel-for-pixel "
        "exactly as the reference, keeping its original colors. "
        "Minimalist clean design."
    ),
}

CARDS = [
    ("01-capa",         ["template", "capa"]),
    ("02-projeto",      ["template", "projeto"]),
    ("03-empresa",      ["template", "empresa", "gru_logo"]),
    ("04-alcance",      ["template", "alcance"]),
    ("05-como-funciona",["template", "como_funciona"]),
    ("06-expectativa",  ["template", "expectativa"]),
    ("07-impacto",      ["template", "impacto"]),
    ("08-cta",          ["template", "ntics_logo", "gru_logo"]),
]


def main():
    only = sys.argv[1] if len(sys.argv) > 1 else None
    print("Uploading template + photos + logos...")
    ids = {
        "template": upload(TEMPLATE),
        "gru_logo": upload(GRU_LOGO),
        "ntics_logo": upload(NTICS_LOGO),
    }
    for k, p in PHOTOS.items():
        ids[k] = upload(p)

    print("\nGenerating v2 cards...")
    for slug, ref_keys in CARDS:
        if only and only not in slug:
            continue
        out_path = OUT / f"{slug}.jpg"
        if out_path.exists() and not only:
            print(f"  [{slug}] already exists, skip")
            continue
        refs = [ids[k] for k in ref_keys]
        prompt = PROMPTS[slug]
        gid = generate(prompt, refs, slug)
        url = poll(gid, slug)
        download(url, out_path)


if __name__ == "__main__":
    main()
