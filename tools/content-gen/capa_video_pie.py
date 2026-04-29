"""
Capa de video PIE Guarulhos - estilo CTA com curva onda.
Mesma referencia visual do CTA card 08 mas como capa de video standalone.
"""
import json, os, sys, time, requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(r"g:\O meu disco\AUTOMACOES\.env")
load_dotenv(r"g:\O meu disco\AUTOMAÇÕES\.env")

API = os.environ["LEONARDO_API_KEY"]
HEADERS = {"Authorization": f"Bearer {API}", "Content-Type": "application/json"}

ROOT = Path(r"g:\O meu disco\AUTOMAÇÕES\output\marketing\carrosseis\projetos\pie")
OUT = ROOT / "capa-video"
OUT.mkdir(parents=True, exist_ok=True)

TEMPLATE = ROOT / "Design referencia" / "Prancheta 1 (3).png"
GRU_LOGO = ROOT / "Design referencia" / "gru_logo_descritivo.png"
NTICS_LOGO = Path(r"g:\O meu disco\AUTOMAÇÕES\brand-book\site\assets\LOGO NTICS.png")

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
        requests.post(up["url"], data=fields, files={"file": (path.name, f)}).raise_for_status()
    print(f"  uploaded {path.name} -> {init_id}")
    return init_id


def generate(prompt: str, refs: list[str]) -> str:
    payload = {
        "model": "nano-banana-2",
        "parameters": {
            "prompt": prompt,
            "width": W, "height": H,
            "quantity": 1,
            "prompt_enhance": "OFF",
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
    r.raise_for_status()
    body = r.json()
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


PROMPT = (
    "Vertical 4:5 video cover for Instagram. Visual identity from FIRST reference image (PIE "
    "brand template): top half is clean white, bottom half is a vertical color block panel "
    "split into magenta #D6116D, teal #1BA9B7 and orange #E68427 stripes with floating "
    "decorative squares (magenta, lime green #C7D435, orange, white) scattered as confetti. "
    "The transition between the white top and the colored bottom is a smooth WAVE CURVE going "
    "across the full width, exactly like the reference template. "

    "TOP white area: at the very top centered, the 'GRU AIRPORT' wordmark from the SECOND "
    "reference image, preserved pixel-for-pixel exactly as the reference logo, in its "
    "original solid black, with the small text 'AEROPORTO INTERNACIONAL DE SÃO PAULO' next to it. "
    "Below it in smaller magenta text: 'APRESENTA'. "

    "MIDDLE on top of the curve: large white center circle holding the bold magenta P.I.E "
    "logo with small magenta text below 'EMPREENDEDORISMO É ARTE - 2ª EDIÇÃO'. "

    "BOTTOM colored area below the circle: huge bold WHITE sans-serif headline in two lines, "
    "centered: 'CHEGOU EM' / 'GUARULHOS'. Below it in smaller white text: 'arte + "
    "empreendedorismo + IA na escola pública'. "

    "Use ONLY the PIE palette colors (magenta, teal, orange, lime, white) — no black except "
    "the brand logo. Clean editorial design, no other text, no other elements. "
    "DO NOT add any tricolor stripe ruler or partner-logo footer at the bottom edge."
)


def main():
    print("Uploading...")
    ids = {
        "template": upload(TEMPLATE),
        "gru_logo": upload(GRU_LOGO),
    }
    print("\nGenerating capa de video...")
    gid = generate(PROMPT, [ids["template"], ids["gru_logo"]])
    url = poll(gid)
    download(url, OUT / "capa-video-v1.jpg")


if __name__ == "__main__":
    main()
