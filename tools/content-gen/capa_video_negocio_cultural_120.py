"""
Capa de video, projeto 120 Negocio Cultural 2a Edicao (Porto Itapoa).
Vídeo "Ainda dá tempo" (Durante #2). Foto Rejane apresentando aula Imagem Profissional.
3 versoes via Leonardo AI seguindo workflow capa_video.md.
"""
import json, os, sys, time, requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(r"g:\O meu disco\AUTOMAÇÕES\.env")
API = os.environ["LEONARDO_API_KEY"]
HEADERS = {"Authorization": f"Bearer {API}", "Content-Type": "application/json"}

ROOT = Path(r"g:\O meu disco\AUTOMAÇÕES")
OUT = ROOT / "output/marketing/carrosseis/projetos/120-negocio-cultural-itapoa/capa-video"
OUT.mkdir(parents=True, exist_ok=True)

PROJECT_BASE = next(ROOT.glob("assets/projetos/120. NEG*PORTO*"))
PROJECT_LOGO = PROJECT_BASE / "LOGOS" / "negocio_cultural_logo.png"
SPONSOR_LOGO = PROJECT_BASE / "LOGOS" / "porto_itapoa_logo.png"
PHOTO = Path(r"C:\Users\lucas\Downloads\Rejane - Imagem Profissional-4.jpg")

W, H = 1856, 2304
LOG = OUT / "geracao.log"


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


def generate(prompt: str, refs: list[str], slug: str) -> str:
    assert len(refs) <= 3, "max 3 image_references no nano-banana-2"
    assert len(prompt) < 1500, f"prompt too long: {len(prompt)} chars"
    payload = {
        "model": "nano-banana-2",
        "parameters": {
            "prompt": prompt,
            "width": W, "height": H,
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


# Paleta Negocio Cultural (do banner BANNER - Porto Itapoá.png):
# Azul-marinho #1B3A5C (primario), Vermelho #E2342A, Amarelo #FFB800, Verde #5BA749, Branco

# v1 Foto-topo + curva + circulo logo + painel branco bottom
PROMPT_V1 = (
    "Vertical 4:5 Instagram video cover, project sponsored by Porto Itapoa. "
    "Palette: navy blue #1B3A5C primary, red #E2342A, yellow #FFB800, green #5BA749, white. "
    "NO BLACK for any text. "

    "TOP 6 percent white: small navy uppercase 'PORTO ITAPOA APRESENTA'. "
    "Only label at the top, do not repeat. "

    "From 6 to 50 percent: FIRST reference image, full-bleed photograph, no overlay. "

    "Smooth wave curve transitions to a navy #1B3A5C area from 50 to 75 percent with "
    "floating yellow gears, red speech bubbles, green leaves and small white pencil icons "
    "as decorative confetti. Centered in this area, a large white circle holding the SECOND "
    "reference image (project logo: blue and red handshake with NEGOCIO CULTURAL wordmark) "
    "preserved pixel-for-pixel with original colors. "

    "BOTTOM 25 percent: clean white rounded panel. Bold navy #1B3A5C headline in two lines, "
    "centered: 'AINDA DÁ TEMPO' / 'DE PARTICIPAR'. Below in smaller red italic: "
    "'em Itapoá'. At the very bottom, centered small navy uppercase 'PATROCÍNIO' followed "
    "by the THIRD reference image (Porto Itapoa logo with green and red architectural icon) "
    "preserved pixel-for-pixel. No tricolor stripe. Clean editorial design."
)

# v2 Bloco cor topo + logo dominante + foto bottom + painel branco
PROMPT_V2 = (
    "Vertical 4:5 Instagram video cover, project sponsored by Porto Itapoa. "
    "Palette: navy blue #1B3A5C primary, red #E2342A, yellow #FFB800, green #5BA749, white. "
    "NO BLACK for any text. "

    "TOP 6 percent white: small navy uppercase 'PORTO ITAPOA APRESENTA'. "
    "Only label at the top, do not repeat. "

    "From 6 to 48 percent: solid navy #1B3A5C area with floating yellow gears, red speech "
    "bubbles, green leaves and small pencil icons as confetti. Centered in this area, a "
    "large white circle holding the SECOND reference image (project logo with blue and red "
    "handshake) preserved pixel-for-pixel. "

    "Wave curve transitions to FIRST reference image, full-bleed photograph from 48 to 82 "
    "percent, no overlay. "

    "BOTTOM 18 percent: clean white rounded panel. Bold navy #1B3A5C headline centered in "
    "two lines, project name: 'NEGÓCIO' / 'CULTURAL'. Below in smaller red uppercase: "
    "'2ª EDIÇÃO - ITAPOÁ'. At the very bottom, centered small navy 'PATROCÍNIO' and below "
    "the THIRD reference image (Porto Itapoa logo) preserved pixel-for-pixel. "
    "No tricolor stripe. Clean editorial design."
)

# v3 Foto fullbleed + logo flutuando + painel branco bottom dominante
PROMPT_V3 = (
    "Vertical 4:5 Instagram video cover, project sponsored by Porto Itapoa. "
    "Palette: navy blue #1B3A5C primary, red #E2342A, yellow #FFB800, green #5BA749, white. "
    "NO BLACK for any text. "

    "TOP 6 percent white: small navy uppercase 'PORTO ITAPOA APRESENTA'. "
    "Only label at the top, do not repeat. "

    "From 6 to 55 percent: FIRST reference image, full-bleed photograph. In the lower-left "
    "corner of the photo area, the SECOND reference image (project logo with blue and red "
    "handshake) sized at 26 percent of card width with soft white circular backing, "
    "preserved pixel-for-pixel. Floating yellow gears, red speech bubbles and green leaves "
    "scattered around the logo as confetti. "

    "BOTTOM 45 percent: solid white rounded panel with generous padding and a navy top border. "
    "Very large bold navy #1B3A5C headline centered, project name: 'NEGÓCIO CULTURAL'. "
    "Below in smaller red #E2342A uppercase: '2ª EDIÇÃO'. Below in smaller navy italic: "
    "'ainda dá tempo de participar em Itapoá'. At the very bottom centered, small navy "
    "uppercase 'PATROCÍNIO' and below it the THIRD reference image (Porto Itapoa logo) "
    "preserved pixel-for-pixel. No tricolor stripe. Clean editorial design."
)

CARDS = [
    ("capa-video-v1.jpg", PROMPT_V1),
    ("capa-video-v2.jpg", PROMPT_V2),
    ("capa-video-v3.jpg", PROMPT_V3),
]


def main():
    only = sys.argv[1] if len(sys.argv) > 1 else None
    print("Uploading...")
    ids = {
        "photo": upload(PHOTO),
        "project_logo": upload(PROJECT_LOGO),
        "sponsor_logo": upload(SPONSOR_LOGO),
    }
    refs = [ids["photo"], ids["project_logo"], ids["sponsor_logo"]]

    for filename, prompt in CARDS:
        if only and only not in filename:
            continue
        out_path = OUT / filename
        if out_path.exists() and not only:
            print(f"\n{filename} exists, skip")
            continue
        print(f"\nGenerating {filename}... (prompt {len(prompt)} chars)")
        gid = generate(prompt, refs, filename)
        url = poll(gid, filename)
        download(url, out_path)


if __name__ == "__main__":
    main()
