"""
teste_estilo_mindset.py — Gera 4 variantes de prompt no estilo @mindset.therapy
para testar qual formulação funciona melhor no Leonardo AI (nano-banana-2).

Notícia de teste: "Brasil alcança topo global em sustentabilidade corporativa"
(S&P Global Sustainability Yearbook 2026)

Usage:
  python tools/teste_estilo_mindset.py
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

BASE_URL_V2 = "https://cloud.leonardo.ai/api/rest/v2"
BASE_URL_V1 = "https://cloud.leonardo.ai/api/rest/v1"
OUTPUT_DIR = Path(".tmp/testes-estilo-mindset")

# ── 4 Prompt Variants ──────────────────────────────────────────────────────────

PROMPTS = {
    "teste_A_preto_puro": (
        "A social media card Instagram 4:5 format. The top 65 percent is a full-bleed "
        "hyperrealistic photograph of a confident Brazilian businesswoman in a modern glass "
        "office building celebrating with her diverse team, ESG data dashboards glowing on "
        "large monitors behind them, candid unposed moment, Canon EOS R5 50mm f1.4, natural "
        "warm morning sunlight streaming through floor-to-ceiling windows, shallow depth of field, "
        "visible film grain ISO 800, skin pores visible, NOT AI generated NOT illustration. "
        "In the upper right corner a circular icon bubble approximately 12 percent of image width "
        "showing a glowing blue and green planet Earth from space, surrounded by a glowing golden "
        "amber ring with soft light emanation. "
        "From 65 to 80 percent a smooth dark gradient overlay transitions from transparent to solid black. "
        "At 68 percent center a small elegant golden decorative divider with horizontal lines on each side. "
        "From 78 to 98 percent centered large bold uppercase white sans-serif text reads: "
        "BRAZIL REACHES THE TOP OF GLOBAL CORPORATE SUSTAINABILITY with words SUSTAINABILITY in golden "
        "amber color F5B800 and words GLOBAL in golden amber color F5B800. "
        "No other text. Clean editorial design black and gold."
    ),

    "teste_B_teal_ntics": (
        "A social media card Instagram 4:5 format. The top 65 percent is a full-bleed "
        "hyperrealistic photograph of a confident Brazilian businesswoman in a modern glass "
        "office building celebrating with her diverse team, ESG data dashboards glowing on "
        "large monitors behind them, candid unposed moment, Nikon D850 85mm f1.8, natural "
        "warm morning sunlight streaming through floor-to-ceiling windows, shallow depth of field, "
        "visible film grain ISO 800, natural imperfect lighting with real shadows, skin pores visible, "
        "NOT AI generated NOT illustration. "
        "In the upper right corner a circular icon bubble approximately 12 percent of image width "
        "showing a glowing blue and green planet Earth from space, surrounded by a glowing amber ring "
        "with soft golden light. "
        "From 65 to 80 percent a smooth dark gradient overlay transitions from transparent to solid "
        "very dark teal 003540. "
        "At 68 percent center a small decorative golden divider line. "
        "From 78 to 98 percent centered large bold uppercase white sans-serif text reads: "
        "BRASIL ALCANCA O TOPO GLOBAL EM with words SUSTENTABILIDADE CORPORATIVA in golden amber "
        "color F5B800. "
        "At the very bottom edge flush a thick gradient stripe bar from green 3DAA35 to teal 00A5B8 "
        "to pink D41A6A to orange E86428. No body text. Bold editorial card."
    ),

    "teste_C_hibrido": (
        "A social media carousel card Instagram 4:5 format. The top 60 percent is a full-bleed "
        "hyperrealistic photograph of a confident Brazilian businesswoman in a modern glass office "
        "celebrating with her diverse team, ESG dashboards on monitors behind them, candid unposed "
        "moment, Canon 50mm f1.4 natural bokeh warm tones, visible film grain ISO 800, natural "
        "imperfect lighting, NOT AI generated. "
        "In the upper right corner overlapping the photo a circular bubble icon approximately 12 "
        "percent width showing a glowing planet Earth, surrounded by a glowing golden ring. "
        "From 60 to 75 percent a smooth dark gradient overlay transitions from transparent to solid "
        "dark teal 005F73. "
        "From 75 to 78 percent a small rounded green 3DAA35 badge with white text ESTRATEGIA CORPORATIVA. "
        "From 78 to 95 percent large bold white uppercase sans-serif headline with key words in "
        "yellow F5B800: BRASIL ALCANCA O TOPO GLOBAL EM SUSTENTABILIDADE CORPORATIVA. "
        "At the very bottom edge flush a thick gradient stripe bar green to teal to pink to orange. "
        "Professional editorial card."
    ),

    "teste_D_minimalista": (
        "A social media card Instagram 4:5. Top 70 percent hyperrealistic photograph of a confident "
        "Brazilian businesswoman celebrating with her team in a modern glass office with ESG dashboards "
        "on screens, candid moment, Canon 85mm f1.4, morning sunlight, bokeh, film grain, real "
        "photograph not illustration. "
        "Upper right corner a glowing circular icon with golden ring showing planet Earth from space. "
        "Bottom 30 percent solid black background. "
        "Centered bold uppercase white text with key phrases highlighted in gold: "
        "BRASIL ALCANCA O TOPO GLOBAL EM SUSTENTABILIDADE CORPORATIVA. "
        "Minimalist bold design black and gold only."
    ),
}


def start_generation(api_key: str, prompt: str) -> str:
    """Start nano-banana-2 generation. Returns generation_id."""
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": f"Bearer {api_key}",
    }
    payload = {
        "model": "nano-banana-2",
        "parameters": {
            "prompt": prompt,
            "width": 1856,
            "height": 2304,
            "quantity": 1,
            "prompt_enhance": "OFF",
        },
        "public": False,
    }
    resp = requests.post(f"{BASE_URL_V2}/generations", headers=headers, json=payload, timeout=30)
    if not resp.ok:
        raise RuntimeError(f"API error {resp.status_code}: {resp.text[:400]}")
    data = resp.json()
    if data.get("generationId"):
        return data["generationId"]
    if data.get("id"):
        return data["id"]
    for val in data.values():
        if isinstance(val, dict) and (val.get("generationId") or val.get("id")):
            return val.get("generationId") or val.get("id")
    raise RuntimeError(f"Could not extract generationId: {data}")


def poll_generation(api_key: str, generation_id: str, max_wait: int = 180) -> str:
    """Poll until complete. Returns image URL."""
    headers = {"accept": "application/json", "authorization": f"Bearer {api_key}"}
    url = f"{BASE_URL_V1}/generations/{generation_id}"
    waited = 0
    interval = 5

    while waited < max_wait:
        resp = requests.get(url, headers=headers, timeout=30)
        resp.raise_for_status()
        job = resp.json().get("generations_by_pk", {})
        status = job.get("status", "")
        if status == "COMPLETE":
            images = job.get("generated_images", [])
            if images:
                return images[0]["url"]
            raise RuntimeError("Complete but no images")
        if status == "FAILED":
            raise RuntimeError(f"Generation failed: {job}")
        time.sleep(interval)
        waited += interval
        print(f"    ... waiting ({waited}s)")

    raise TimeoutError(f"Timeout after {max_wait}s")


def download_image(url: str, output_path: Path) -> Path:
    resp = requests.get(url, timeout=60)
    resp.raise_for_status()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "wb") as f:
        f.write(resp.content)
    return output_path


def main():
    api_key = os.getenv("LEONARDO_API_KEY")
    if not api_key:
        print("ERROR: LEONARDO_API_KEY not set in .env")
        sys.exit(1)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    results = []

    # Start all 4 generations
    jobs = {}
    for name, prompt in PROMPTS.items():
        print(f"\n>> Starting: {name}")
        print(f"   Prompt: {prompt[:100]}...")
        try:
            gen_id = start_generation(api_key, prompt)
            jobs[name] = gen_id
            print(f"   Generation ID: {gen_id}")
        except Exception as e:
            print(f"   FAILED to start: {e}")
            results.append({"name": name, "error": str(e)})

    if not jobs:
        print("\nNo generations started. Exiting.")
        sys.exit(1)

    # Wait initial period
    print(f"\n>> Waiting 50s for generations to process...")
    time.sleep(50)

    # Poll and download each
    for name, gen_id in jobs.items():
        print(f"\n>> Polling: {name}")
        try:
            image_url = poll_generation(api_key, gen_id)
            output_path = OUTPUT_DIR / f"{name}.jpg"
            download_image(image_url, output_path)
            print(f"   SAVED: {output_path}")
            results.append({
                "name": name,
                "generation_id": gen_id,
                "image_url": image_url,
                "local_path": str(output_path),
            })
        except Exception as e:
            print(f"   FAILED: {e}")
            results.append({"name": name, "generation_id": gen_id, "error": str(e)})

    # Save manifest
    manifest = OUTPUT_DIR / "manifest.json"
    with open(manifest, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    ok = sum(1 for r in results if "error" not in r)
    print(f"\n{'='*50}")
    print(f"DONE: {ok}/{len(PROMPTS)} images generated")
    print(f"Folder: {OUTPUT_DIR}")
    print(f"Manifest: {manifest}")


if __name__ == "__main__":
    main()
