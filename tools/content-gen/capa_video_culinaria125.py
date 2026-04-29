"""
Capa de video - Gastronomia Tambem E Arte 2a Edicao (Projeto 125, GRU Airport).
Estilo: mesmo template PIE com curva onda, mas identidade do projeto Culinaria Sustentavel.
Paleta primaria: teal #1BA9B7 (cor da panela do logo), magenta #D6116D, orange #E68427, lime #C7D435.
"""
import json, os, time, requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(r"g:\O meu disco\AUTOMAÇÕES\.env")

API = os.environ["LEONARDO_API_KEY"]
HEADERS = {"Authorization": f"Bearer {API}", "Content-Type": "application/json"}

ROOT = Path(r"g:\O meu disco\AUTOMAÇÕES")
OUT = ROOT / "output/marketing/carrosseis/projetos/culinaria-125/capa-video"
OUT.mkdir(parents=True, exist_ok=True)

PROJECT_LOGO = ROOT / "assets/projetos/125. EXPOSIÇÃO - GASTRONOMIA TAMBÉM É ARTE 2ED (GRU)/PECAS_COMUNICACAO/LOGO (2).png"
GRU_LOGO = ROOT / "assets/projetos/125. EXPOSIÇÃO - GASTRONOMIA TAMBÉM É ARTE 2ED (GRU)/LOGOS/grulogo_gru_DESCRITIVO.png"
REFERENCE_PIECE = ROOT / "assets/projetos/125. EXPOSIÇÃO - GASTRONOMIA TAMBÉM É ARTE 2ED (GRU)/PECAS_COMUNICACAO/culinaria2.png"
PHOTO = ROOT / "assets/melhores-fotos/7. CULINÁRIA SUSTENTÁVEL/102_culinaria-sustentavel_culinaria_mulher-servindo-prato-culinario-para-grupo.jpg"

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
    print(f"  uploaded {path.name} -> {init_id}")
    return init_id


def generate(prompt: str, refs: list[str]) -> str:
    payload = {
        "model": "nano-banana-2",
        "parameters": {
            "prompt": prompt,
            "width": W, "height": H,
            "quantity": 1, "prompt_enhance": "OFF",
            "guidances": {
                "image_reference": [
                    {"image": {"id": rid, "type": "UPLOADED"}, "strength": "HIGH"}
                    for rid in refs
                ]
            },
        },
        "public": False,
    }
    r = requests.post(
        "https://cloud.leonardo.ai/api/rest/v2/generations", headers=HEADERS, json=payload
    )
    if r.status_code >= 400:
        print(f"  ERROR {r.status_code}: {r.text[:600]}")
    body = r.json()
    if isinstance(body, list) or "generate" not in (body if isinstance(body, dict) else {}):
        print(f"  BODY: {json.dumps(body)[:600]}")
        raise RuntimeError("bad body")
    gid = (body.get("generate") or {}).get("generationId")
    print(f"  gen id: {gid}")
    return gid


def poll(gid: str) -> str:
    for i in range(30):
        time.sleep(8 if i == 0 else 5)
        r = requests.get(
            f"https://cloud.leonardo.ai/api/rest/v1/generations/{gid}", headers=HEADERS
        )
        r.raise_for_status()
        gen = r.json()["generations_by_pk"]
        s = gen.get("status")
        if s == "COMPLETE":
            return gen["generated_images"][0]["url"]
        if s == "FAILED":
            raise RuntimeError(f"FAILED: {gen}")
        print(f"  {s}... ({i+1})")
    raise TimeoutError()


def download(url: str, path: Path):
    r = requests.get(url, timeout=60)
    r.raise_for_status()
    path.write_bytes(r.content)
    print(f"  saved -> {path.name}")


PROMPT_V1 = (
    "Vertical 4:5 Instagram video cover, project 'Gastronomia Também é Arte' sponsored by "
    "GRU Airport. Palette: teal #1BA9B7 primary, magenta #D6116D, lime #C7D435, orange "
    "#E68427, white. NO BLACK for any text. "

    "Top 7 percent white: small teal uppercase 'GRU AIRPORT APRESENTA'. "

    "From 7 to 50 percent: FIRST reference image, full-bleed photograph, no overlay. "

    "Smooth wave curve transitions to a teal #1BA9B7 area from 50 to 75 percent with "
    "floating lime leaves, magenta cherries and open orange arcs as confetti. Centered in "
    "this teal area, a large white circle holding the SECOND reference image (project logo "
    "with teal pot and ingredients) preserved pixel-for-pixel with original colors. "

    "Bottom 25 percent: clean white rounded panel. Bold teal #1BA9B7 headline in two lines, "
    "centered: 'SABORES QUE' / 'TRANSFORMAM'. Below in smaller magenta italic: "
    "'a 2ª edição chegou a Guarulhos'. At the very bottom of this panel, centered small "
    "magenta uppercase 'PATROCÍNIO' and below it the THIRD reference image (GRU AIRPORT "
    "logo) preserved pixel-for-pixel with original colors. "

    "No tricolor stripe at the bottom edge. Clean editorial design."
)

# v2: bloco teal no topo com logo projeto, curva onda, foto no bottom + headline branca.
PROMPT_V2 = (
    "Vertical 4:5 Instagram video cover, project sponsored by GRU Airport. Palette: "
    "teal #1BA9B7 primary, magenta #D6116D, lime #C7D435, orange #E68427, white. "
    "NO BLACK for any text. "

    "TOP 6 percent: clean white area. Centered, small teal uppercase: 'GRU AIRPORT APRESENTA'. "
    "This is the ONLY label at the top — do not repeat it anywhere else. "

    "From 6 to 48 percent: solid teal #1BA9B7 area with floating lime leaves, magenta "
    "cherries with small white stars, and open orange arcs scattered as confetti. Centered "
    "in this area, a large white circle holding the SECOND reference image (project logo "
    "with the teal pot) preserved pixel-for-pixel with original colors. "

    "A smooth wave curve across the full width transitions from the teal area to the photo. "

    "From 48 to 82 percent: FIRST reference image, full-bleed photograph, no overlay. "

    "BOTTOM 18 percent: clean white rounded panel with generous padding. Bold teal #1BA9B7 "
    "headline in two lines, centered, this is the project name: 'GASTRONOMIA' / "
    "'TAMBÉM É ARTE'. Below in smaller magenta uppercase: 'CULINÁRIA SUSTENTÁVEL - 2ª EDIÇÃO'. "
    "At the very bottom, centered small magenta uppercase 'PATROCÍNIO' followed by the "
    "THIRD reference image (GRU AIRPORT logo) preserved pixel-for-pixel with original colors. "

    "No tricolor stripe. Clean editorial design."
)

# v3: foto fullbleed com overlay branco no bottom. Logo projeto dentro da panela + headline grande.
PROMPT_V3 = (
    "Vertical 4:5 Instagram video cover, project sponsored by GRU Airport. Palette: "
    "teal #1BA9B7 primary, magenta #D6116D, lime #C7D435, orange #E68427, white. "
    "NO BLACK for any text. "

    "TOP 6 percent: clean white area. Centered, small teal uppercase: 'GRU AIRPORT APRESENTA'. "
    "This is the ONLY label at the top — do not repeat it anywhere else. "

    "From 6 to 55 percent: FIRST reference image, full-bleed photograph. In the lower-left "
    "corner of the photo area, the SECOND reference image (project logo with teal pot) "
    "sized at about 26 percent of the card width, preserved pixel-for-pixel with original "
    "colors. Small floating lime leaves, magenta cherries and orange arcs scattered around "
    "the logo as decorative confetti. "

    "BOTTOM 45 percent: solid white rounded panel with generous padding and a teal top "
    "border. Very large bold teal #1BA9B7 headline, centered, this is the project name: "
    "'GASTRONOMIA TAMBÉM É ARTE'. Below in smaller magenta #D6116D uppercase: "
    "'CULINÁRIA SUSTENTÁVEL - 2ª EDIÇÃO'. Below in small magenta italic sans-serif: "
    "'está chegando em Guarulhos'. At the very bottom, centered, small magenta uppercase "
    "'PATROCÍNIO' and below it the THIRD reference image (GRU AIRPORT logo) preserved "
    "pixel-for-pixel with original colors. "

    "No tricolor stripe at the bottom edge. Clean editorial design."
)


def main():
    print("Uploading...")
    ids = {
        "photo": upload(PHOTO),
        "project_logo": upload(PROJECT_LOGO),
        "gru": upload(GRU_LOGO),
    }
    refs = [ids["photo"], ids["project_logo"], ids["gru"]]
    versions = [
        ("capa-video-v2.jpg", PROMPT_V2),
        ("capa-video-v3.jpg", PROMPT_V3),
    ]
    for filename, prompt in versions:
        out_path = OUT / filename
        if out_path.exists():
            print(f"\n{filename} exists, skip")
            continue
        print(f"\nGenerating {filename}...")
        gid = generate(prompt, refs)
        url = poll(gid)
        download(url, out_path)


if __name__ == "__main__":
    main()
