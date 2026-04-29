"""
Carrossel PIE Guarulhos - Pré-projeto - v1
Leonardo AI puro (sem Pillow).

Estrategia:
- Template visual PIE (Prancheta 1 (3).png) como image_reference em TODOS os cards
  -> trava paleta (magenta #D6116D, teal #1BA9B7, orange #E68427, lime #C7D435),
     blocos verticais coloridos, quadradinhos flutuantes, circulo branco central.
- Cards 02-07 ganham tambem a foto real do projeto como segunda image_reference.
- Card 01 e 08 usam apenas o template + descricao de cena.
"""
import json, os, sys, time, requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(r"g:\O meu disco\AUTOMACOES\.env")
load_dotenv(r"g:\O meu disco\AUTOMAÇÕES\.env")

API = os.environ["LEONARDO_API_KEY"]
HEADERS = {"Authorization": f"Bearer {API}", "Content-Type": "application/json"}

ROOT = Path(r"g:\O meu disco\AUTOMAÇÕES\output\marketing\carrosseis\projetos\pie")
OUT = ROOT / "v1"
OUT.mkdir(parents=True, exist_ok=True)

TEMPLATE = ROOT / "Design referencia" / "Prancheta 1 (3).png"
GRU_LOGO = ROOT / "Design referencia" / "gru_logo_descritivo.png"
NTICS_LOGO = Path(r"g:\O meu disco\AUTOMAÇÕES\brand-book\site\assets\LOGO NTICS.png")

PHOTOS = {
    "capa":         ROOT / "WhatsApp Image 2026-04-18 at 11.17.33 (1).jpeg",  # turma com placas PIE
    "projeto":      ROOT / "WhatsApp Image 2026-04-18 at 11.17.37.jpeg",       # facilitadora ensinando
    "empresa":      ROOT / "WhatsApp Image 2026-04-18 at 11.17.37 (2).jpeg",   # banner GRU+PIE descritivo
    "alcance":      ROOT / "WhatsApp Image 2026-04-23 at 17.01.57.jpeg",       # turma cheia
    "como_funciona":ROOT / "WhatsApp Image 2026-04-18 at 11.17.37 (1).jpeg",   # vista ampla oficina
    "expectativa":  ROOT / "WhatsApp Image 2026-04-23 at 08.57.10.jpeg",       # alunos com projetos
    "impacto":      ROOT / "WhatsApp Image 2026-04-18 at 11.17.33.jpeg",       # facilitadora + alunos
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
            print(f"  [{slug}] DONE -> {url}")
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


# Color reminder used in every prompt to lock palette
PALETTE = (
    "PIE color palette: magenta pink #D6116D, teal cyan #1BA9B7, "
    "vivid orange #E68427, lime green #C7D435, white background. "
    "Use small floating colored squares (magenta, lime, orange) as decorative confetti."
)

PROMPTS = {
    "01-capa": (
        "Instagram carousel cover 4:5. Match the visual identity of the FIRST reference image "
        "(PIE brand template) exactly: vertical color blocks magenta, teal and orange across "
        "the card with floating colored squares, large white center circle holding the P.I.E logo. "
        f"{PALETTE} "
        "Top thin label in black sans-serif: 'GRU AIRPORT APRESENTA'. "
        "UPPER 45 percent: SECOND reference image, full bleed photograph, no overlay. "
        "Below the photo, on the colored blocks, a large white center circle with bold magenta "
        "P.I.E logo and small magenta text 'EMPREENDEDORISMO É ARTE - 2ª EDIÇÃO'. "
        "BOTTOM 22 percent: a clean white rounded panel with generous padding holding the "
        "headline in three lines, bold sans-serif, magenta color #D6116D: "
        "'CHEGOU EM' / 'GUARULHOS' (large), and below in smaller black text 'em sua 2ª edição'. "
        "Tricolor stripe magenta-teal-orange flush at the very bottom edge. "
        "No other text. Clean editorial design."
    ),
    "02-projeto": (
        "Instagram carousel content card 4:5. Match the visual identity of the FIRST reference "
        "image (PIE brand template) exactly: vertical color blocks magenta, teal and orange, "
        "floating colored squares, white rounded panel for text. "
        f"{PALETTE} "
        "UPPER 55 percent: SECOND reference image, full bleed photograph, no overlay. "
        "Small magenta pill badge below photo with white text 'O PROJETO'. "
        "Then bold black headline: 'ARTE, EMPREENDEDORISMO E IA NA ESCOLA'. "
        "Below in smaller black text: 'Estudantes e professores da rede pública de Guarulhos "
        "vivem um novo jeito de aprender.' Bottom edge: thin tricolor stripe magenta-teal-orange."
    ),
    "03-empresa": (
        "Instagram carousel content card 4:5. Match the visual identity of the FIRST reference "
        "image (PIE brand template) exactly: vertical color blocks magenta, teal and orange, "
        "floating colored squares. Same layout as the other cards in this carousel: photo on "
        "top, white rounded panel with text on the bottom. "
        f"{PALETTE} "
        "UPPER 55 percent: SECOND reference image, full bleed photograph, no overlay. "
        "MIDDLE: the THIRD reference image is the GRU AIRPORT logo. Place it centered, "
        "perfectly preserved pixel-for-pixel exactly as the reference, in solid black on a "
        "small white pill, no recoloring, no redrawing, no font substitution. "
        "BOTTOM 30 percent: clean white rounded panel with bold black headline "
        "'O PATROCÍNIO QUE TORNA O PIE POSSÍVEL', and below in smaller black text "
        "'A GRU Airport patrocina a 2ª edição do PIE em Guarulhos.' "
        "Bottom edge: thin tricolor stripe magenta-teal-orange."
    ),
    "04-alcance": (
        "Instagram carousel content card 4:5. Match the visual identity of the FIRST reference "
        "image (PIE brand template) exactly: vertical color blocks magenta, teal and orange, "
        "floating colored squares. "
        f"{PALETTE} "
        "UPPER 50 percent: SECOND reference image, full bleed photograph, no overlay. "
        "Small teal pill badge below photo with white text 'ALCANCE'. "
        "Then huge bold magenta numbers stacked: '3.000' estudantes and '100' professores, "
        "with the labels in smaller black text under each number. "
        "At the bottom: 'em Guarulhos' in black. Tricolor stripe magenta-teal-orange at the very bottom."
    ),
    "05-como-funciona": (
        "Instagram carousel content card 4:5. Match the visual identity of the FIRST reference "
        "image (PIE brand template) exactly: vertical color blocks magenta, teal and orange, "
        "floating colored squares. "
        f"{PALETTE} "
        "UPPER 45 percent: SECOND reference image, full bleed photograph, no overlay. "
        "Small orange pill badge below photo with white text 'COMO FUNCIONA'. "
        "Then a vertical numbered list in bold black, four lines: "
        "'1. Palestra de abertura', '2. Formação de professores', "
        "'3. Oficinas em sala de aula', '4. Feira de Ideias'. "
        "Tricolor stripe magenta-teal-orange at the bottom edge."
    ),
    "06-expectativa": (
        "Instagram carousel content card 4:5. Match the visual identity of the FIRST reference "
        "image (PIE brand template) exactly: vertical color blocks magenta, teal and orange, "
        "floating colored squares. "
        f"{PALETTE} "
        "UPPER 55 percent: SECOND reference image, full bleed photograph, no overlay. "
        "Small lime green pill badge below photo with black text 'EXPECTATIVA'. "
        "Then bold black headline: 'CADA TURMA, UM DESAFIO REAL'. "
        "Below in smaller black text: 'Os estudantes criam projetos a partir de desafios "
        "do próprio cotidiano e apresentam na Feira de Ideias.' "
        "Tricolor stripe magenta-teal-orange at the bottom edge."
    ),
    "07-impacto": (
        "Instagram carousel content card 4:5. Match the visual identity of the FIRST reference "
        "image (PIE brand template) exactly: vertical color blocks magenta, teal and orange, "
        "floating colored squares. "
        f"{PALETTE} "
        "UPPER 50 percent: SECOND reference image, full bleed photograph, no overlay. "
        "Small magenta pill badge below photo with white text 'IMPACTO'. "
        "Then bold black headline: 'ARTE, TECNOLOGIA E EMPREENDEDORISMO NA SALA DE AULA'. "
        "Below in smaller black text: 'Guarulhos vai mostrar o que acontece quando essas "
        "três linguagens entram juntas na escola pública.' "
        "Tricolor stripe magenta-teal-orange at the bottom edge."
    ),
    "08-cta": (
        "Instagram carousel final CTA card 4:5. Match the visual identity of the FIRST "
        "reference image (PIE brand template) exactly: vertical color blocks magenta, teal "
        "and orange with floating colored squares, large white center circle. "
        f"{PALETTE} "
        "Upper-middle: a large white center circle holding the bold magenta P.I.E logo with "
        "small magenta text 'EMPREENDEDORISMO É ARTE - 2ª EDIÇÃO'. "
        "Above the circle, large bold magenta headline #D6116D centered on a white strip: "
        "'EM BREVE, O PIE COMEÇA'. "
        "BOTTOM 22 percent: a clean white footer panel divided in two columns side by side. "
        "LEFT column label in small black uppercase 'REALIZAÇÃO' and below it the SECOND "
        "reference image which is the NTICS Projetos logo (green lightbulb with gears plus "
        "NTICS PROJETOS wordmark), preserved pixel-for-pixel exactly as the reference, "
        "no recoloring, no redrawing. RIGHT column label in small black uppercase 'PATROCÍNIO' "
        "and below it the THIRD reference image which is the GRU AIRPORT logo in solid black, "
        "preserved pixel-for-pixel exactly as the reference, no recoloring, no redrawing. "
        "Tricolor stripe magenta-teal-orange flush at the very bottom edge. "
        "Minimalist clean design, no other elements, no other text."
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
    print("Uploading template + photos...")
    ids = {
        "template": upload(TEMPLATE),
        "gru_logo": upload(GRU_LOGO),
        "ntics_logo": upload(NTICS_LOGO),
    }
    for k, p in PHOTOS.items():
        ids[k] = upload(p)

    print("\nGenerating cards...")
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
