"""
generate_pilula_cover.py — Gera capa Instagram (4:5) para pílulas ESG no Agro.

📚 Ref: workflows/marketing/referencia/leonardo_ai_core.md — consulte em caso de erro ou
dúvida sobre payloads, image_reference (objeto aninhado), erros conhecidos.

Usa Leonardo Nano Banana 2 com DUAS image_references (pessoa + logo) e
renderiza o texto da headline diretamente na imagem via prompt de zonas.

Usage:
  python tools/media/generate_pilula_cover.py \
    --person "SB/ESG no agro/Participantes/DN - Daniele Nazari (1).jpg" \
    --logo   "SB/ESG no agro/Logo/Criar-save-the-date-LOGO (2).png" \
    --headline "NR1 E SAUDE MENTAL: POR QUE TODO MUNDO PRECISA SABER DISSO" \
    --output "SB/ESG no agro/Pirulas/PILULA 3/capa-instagram.jpg"

Environment:
  LEONARDO_API_KEY=... (in .env)
"""

import json
import os
import sys
import time
from pathlib import Path

import requests
from dotenv import load_dotenv

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

load_dotenv()

API_KEY = os.getenv("LEONARDO_API_KEY")
HEADERS = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

BASE_V1 = "https://cloud.leonardo.ai/api/rest/v1"
BASE_V2 = "https://cloud.leonardo.ai/api/rest/v2"

PROMPT_TEMPLATE = """\
Reference images provided: use the person and logo exactly \
as shown — do not alter face, clothing, or logo design.

Shallow depth of field soybean crops field background throughout.

--- COMPOSITION LAYOUT (vertical zones) ---

Zone 1 (top 15%): Background only — sky and field.
No content. This area will be cropped on Instagram.

Zone 2 (15% to 28%): Logo placement area.
Center the event logo (ESG No Agronegocio 4a Edicao)
with subtitle "Tendencias que moldam o futuro do campo" below it.

Zone 3 (28% to 65%): Portrait zone.
Person centered. Surrounded by dynamic glowing neon light
trails forming circular motion around them — green and
yellow energy streaks, luminous particles, motion light
effect, futuristic energy branding style.
Floating thematic icons around the figure: {icons}.

Zone 4 (65% to 85%): Typography zone.
Different colored bold uppercase modern sans-serif text:
"{headline}"
Clean layout, centered.

Zone 5 (bottom 15%): Background only — field ground.
No content. This area will be cropped on Instagram.

--- STYLE ---

High-end corporate advertising look, cinematic lighting,
sharp focus, vibrant colors, modern branding aesthetic.
Marketing campaign visual, high production quality."""


def upload_init_image(photo_path: Path) -> str:
    """Faz upload da imagem de referencia e retorna o init_image_id."""
    ext = photo_path.suffix.lstrip(".").lower()
    if ext == "jpeg":
        ext = "jpg"

    print(f"  Uploading {photo_path.name}...")
    r = requests.post(
        f"{BASE_V1}/init-image",
        headers=HEADERS,
        json={"extension": ext},
        timeout=30,
    )
    r.raise_for_status()
    upload = r.json()["uploadInitImage"]
    fields = json.loads(upload["fields"])
    init_id = upload["id"]

    with open(photo_path, "rb") as f:
        resp = requests.post(upload["url"], data=fields, files={"file": f}, timeout=60)
    resp.raise_for_status()
    print(f"  ✓ {photo_path.name} → id={init_id}")
    return init_id


def generate_card(prompt: str, person_id: str, logo_id: str) -> str:
    """Gera imagem com duas referências (pessoa + logo). Retorna generation_id."""
    payload = {
        "model": "nano-banana-2",
        "parameters": {
            "width": 768,
            "height": 1376,
            "prompt": prompt,
            "quantity": 1,
            "prompt_enhance": "OFF",
            "guidances": {
                "image_reference": [
                    {"image": {"id": person_id, "type": "UPLOADED"}, "strength": "HIGH"},
                    {"image": {"id": logo_id,   "type": "UPLOADED"}, "strength": "HIGH"},
                ]
            }
        },
        "public": False
    }
    r = requests.post(f"{BASE_V2}/generations", headers=HEADERS, json=payload, timeout=30)
    r.raise_for_status()
    data = r.json()
    gen_id = (
        data.get("generate", {}).get("generationId")
        or data.get("sdGenerationJob", {}).get("generationId")
    )
    if not gen_id:
        raise RuntimeError(f"generationId nao encontrado: {data}")
    print(f"  Generation ID: {gen_id}")
    return gen_id


def poll_generation(gen_id: str, timeout: int = 180) -> str:
    """Aguarda conclusao e retorna URL da imagem."""
    print(f"  Aguardando...", end="", flush=True)
    elapsed = 0
    while elapsed < timeout:
        time.sleep(10)
        elapsed += 10
        r = requests.get(f"{BASE_V1}/generations/{gen_id}", headers=HEADERS, timeout=30)
        r.raise_for_status()
        data = r.json().get("generations_by_pk", {})
        status = data.get("status", "PENDING")
        print(f" {elapsed}s({status})", end="", flush=True)
        if status == "COMPLETE":
            imgs = data.get("generated_images", [])
            if imgs:
                print(" ✓")
                return imgs[0]["url"]
        elif status == "FAILED":
            raise RuntimeError(f"Geracao falhou: {gen_id}")
    raise TimeoutError(f"Timeout apos {timeout}s")


def download_image(url: str, out_path: Path):
    r = requests.get(url, timeout=60)
    r.raise_for_status()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "wb") as f:
        f.write(r.content)
    print(f"  ✓ Saved: {out_path} ({len(r.content)//1024} KB)")


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--person",   required=True, help="Foto do palestrante")
    parser.add_argument("--logo",     required=True, help="Logo do evento")
    parser.add_argument("--headline", required=True, help="Texto da headline (Zone 4)")
    parser.add_argument("--icons",    required=True, help="Icones tematicos flutuantes (Zone 3)")
    parser.add_argument("--output",   required=True, help="Caminho de saida .jpg")
    args = parser.parse_args()

    if not API_KEY:
        print("ERROR: LEONARDO_API_KEY nao configurada em .env")
        sys.exit(1)

    person_path = Path(args.person)
    logo_path   = Path(args.logo)
    out_path    = Path(args.output)

    for p in (person_path, logo_path):
        if not p.exists():
            print(f"ERROR: Arquivo nao encontrado: {p}")
            sys.exit(1)

    prompt = PROMPT_TEMPLATE.format(headline=args.headline, icons=args.icons)

    print(f"\n[generate_pilula_cover]")
    print(f"  Person:   {person_path.name}")
    print(f"  Logo:     {logo_path.name}")
    print(f"  Headline: {args.headline[:70]}")
    print(f"  Output:   {out_path}")

    print("\n[1/3] Uploads...")
    person_id = upload_init_image(person_path)
    logo_id   = upload_init_image(logo_path)

    print("\n[2/3] Gerando (nano-banana-2, 768x1376, 2x image_reference HIGH)...")
    gen_id = generate_card(prompt, person_id, logo_id)

    print("\n[3/3] Aguardando resultado...")
    img_url = poll_generation(gen_id)
    download_image(img_url, out_path)

    print(f"\n✓ Concluido: {out_path}")


if __name__ == "__main__":
    main()
