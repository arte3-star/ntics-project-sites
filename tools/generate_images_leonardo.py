"""
generate_images_leonardo.py — Generates ultra-realistic images via Leonardo AI API.

Uses Phoenix 1.0 by default (flagship Leonardo model, best photorealism).
Each image prompt is built from the story's actual title, company, summary and category
to ensure contextual relevance. Images are saved to .tmp/images/.

Usage:
  python tools/generate_images_leonardo.py \
    --stories .tmp/stories_2026-03-20.json \
    --output-dir .tmp/images/2026-03-20

  python tools/generate_images_leonardo.py \
    --prompt "Custom prompt here" \
    --filename my_image \
    --output-dir .tmp/images

  python tools/generate_images_leonardo.py \
    --stories .tmp/stories_2026-03-20.json \
    --model flux      # or: phoenix, lucid, reality, kino

Environment:
  LEONARDO_API_KEY=... (in .env)

Available models (--model flag):
  phoenix     Phoenix 1.0 — flagship, best overall quality (default)
  lucid       Lucid Realism — dedicated photorealism
  flux        Flux Dev — state-of-the-art realism
  reality     Absolute Reality v1.6 — realistic photography
  kino        Leonardo Kino XL — cinematic style
  lightning   Leonardo Lightning XL — fastest generation
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path

import requests
from dotenv import load_dotenv

# Fix Windows console encoding for Unicode output
import sys
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

load_dotenv()

# ── Leonardo model IDs (verified from account) ────────────────────────────────
MODELS = {
    "nanobanana": "nano-banana-2",                         # Nano Banana 2 — v2 API (ultra-realistic)
    "phoenix":    "de7d3faf-762f-48e0-b3b7-9d0ac3a3fcf3", # Phoenix 1.0 — flagship v1
    "lucid":      "05ce0082-2d80-4a2d-8653-4d1c85e2418e", # Lucid Realism
    "flux":       "b2614463-296c-462a-9586-aafdb8f00e36", # Flux Dev
    "reality":    "e316348f-7773-490e-adcd-46757c738eb7", # Absolute Reality v1.6
    "kino":       "aa77f04e-3eec-4034-9c07-d0f619684628", # Leonardo Kino XL
    "lightning":  "b24e16ff-06e3-43eb-8d33-4416c2d75876", # Lightning XL (fastest)
}
DEFAULT_MODEL = "nanobanana"

BASE_URL_V1 = "https://cloud.leonardo.ai/api/rest/v1"
BASE_URL_V2 = "https://cloud.leonardo.ai/api/rest/v2"

# Models that use the v2 API (different endpoint + payload schema)
V2_MODELS = {"nanobanana"}
V2_MODEL_NAMES = {"nanobanana": "nano-banana-2"}

# ── Category → cinematic style suffix ────────────────────────────────────────
CATEGORY_STYLE = {
    "environment": "lush natural light, vibrant greens, sense of hope and renewal, wide landscape",
    "social":      "warm golden light, human connection, diverse faces, community atmosphere",
    "governance":  "clean corporate environment, professional confidence, modern architecture",
}

# ── Keyword → specific scene description ─────────────────────────────────────
TOPIC_HINTS = [
    (["renewable", "solar", "eólica", "wind", "energia renovável", "clean energy", "energia limpa"],
     "vast solar farm or wind turbine field at golden hour, aerial view, technology meets nature"),
    (["carbon", "emissão", "emission", "net zero", "neutralidade", "neutral", "climate", "clima"],
     "modern corporate campus surrounded by trees, green rooftop gardens, clean air cityscape"),
    (["agriculture", "farm", "fazenda", "regenerat", "agricult", "food", "alimentar", "solo", "crop"],
     "farmer walking through lush regenerative crops at dawn, rich soil, sustainable harvest"),
    (["forest", "floresta", "amazon", "amazônia", "biodiversity", "biodiversidade", "cerrado", "nature"],
     "breathtaking aerial view of Amazon rainforest, winding river, morning mist over canopy"),
    (["women", "gender", "gênero", "female", "paridade", "mulher", "liderança feminina"],
     "confident diverse professional women in a modern boardroom, warm natural light"),
    (["education", "digital", "skill", "capacit", "learn"],
     "diverse young people learning on laptops in a bright modern space, collaborative atmosphere"),
    (["finance", "bank", "banco", "invest", "crédito", "credit", "bond", "green bond"],
     "modern sustainable finance hub, glass towers with green facades, ESG signage, prosperity"),
    (["supplier", "supply", "fornecedor", "diversity", "diversidade", "inclusion", "inclusão"],
     "diverse multicultural team of professionals collaborating in a bright modern office"),
    (["ocean", "water", "sea", "marine", "mar", "oceano"],
     "pristine ocean waters from aerial view, coral reef visible below, clean coastline"),
    (["city", "urban", "transport", "mobility", "cidade"],
     "modern sustainable city with green rooftops, cyclists, electric buses, clean air"),
    (["circular", "waste", "residuo", "recycl", "reciclagem"],
     "circular economy concept, clean modern recycling facility, workers sorting materials"),
    (["health", "saúde", "medical", "well-being", "bem-estar"],
     "bright modern healthcare facility, diverse medical professionals, patient care"),
    (["water", "água", "sanitation", "saneamento"],
     "clean water treatment facility, engineers monitoring systems, clear blue water"),
]

BASE_PROMPT_SUFFIX = (
    ", ultra-realistic photography, 8K resolution, professional photojournalism, "
    "sharp focus, dramatic natural lighting, award-winning editorial photo, "
    "hyperrealistic detail, no text, no logos, no watermarks, no people holding signs"
)

NEGATIVE_PROMPT = (
    "cartoon, illustration, painting, drawing, animation, CGI, render, "
    "unrealistic, blurry, low quality, watermark, text, logo, banner, "
    "distorted faces, extra limbs, bad anatomy"
)


def get_topic_hint(title: str, summary: str, company: str, category: str) -> str:
    """Match story content to the most specific visual scene description."""
    combined = f"{title} {summary} {company}".lower()
    for keywords, hint in TOPIC_HINTS:
        if any(k in combined for k in keywords):
            return hint
    return CATEGORY_STYLE.get(category, "corporate sustainability initiative, modern workplace")


def build_prompt(story: dict) -> str:
    """Build a contextual ultra-realistic prompt from the story's actual content."""
    title   = story.get("title", "")
    company = story.get("company", "")
    summary = story.get("summary", "")
    category = story.get("category", "environment")

    scene = get_topic_hint(title, summary, company, category)
    style = CATEGORY_STYLE.get(category, "")

    # Incorporate company name for extra specificity when it adds visual context
    company_context = ""
    if company and len(company) < 30:
        company_context = f", real-world corporate setting representing {company}'s work"

    return f"{scene}{company_context}, {style}{BASE_PROMPT_SUFFIX}"


def start_generation_v1(api_key: str, prompt: str, model_id: str, width: int = 1024, height: int = 512) -> str:
    """Start a generation using Leonardo v1 API. Returns generation_id."""
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": f"Bearer {api_key}",
    }
    payload = {
        "prompt": prompt,
        "negative_prompt": NEGATIVE_PROMPT,
        "modelId": model_id,
        "width": width,
        "height": height,
        "num_images": 1,
        "public": False,
    }
    resp = requests.post(f"{BASE_URL_V1}/generations", headers=headers, json=payload, timeout=30)
    resp.raise_for_status()
    return resp.json()["sdGenerationJob"]["generationId"]


def start_generation_v2(api_key: str, prompt: str, width: int = 1856, height: int = 2304, prompt_enhance: str = "OFF") -> str:
    """Start a generation using Leonardo v2 API (Nano Banana 2). Returns generation_id."""
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": f"Bearer {api_key}",
    }
    # v2 wraps all generation params inside "parameters"
    payload = {
        "model": "nano-banana-2",
        "parameters": {
            "prompt": prompt,
            "width": width,
            "height": height,
            "quantity": 1,
            "prompt_enhance": prompt_enhance,
        },
        "public": False,
    }
    resp = requests.post(f"{BASE_URL_V2}/generations", headers=headers, json=payload, timeout=30)
    if not resp.ok:
        raise RuntimeError(f"v2 API error {resp.status_code}: {resp.text[:400]}")
    data = resp.json()
    # Direct keys
    if data.get("generationId"):
        return data["generationId"]
    if data.get("id"):
        return data["id"]
    # Response may be nested under a wrapper key (e.g. {"job": {"generationId": "..."}})
    for val in data.values():
        if isinstance(val, dict) and val.get("generationId"):
            return val["generationId"]
        if isinstance(val, dict) and val.get("id"):
            return val["id"]
    raise RuntimeError(f"Could not extract generationId from v2 response: {data}")


def poll_generation(api_key: str, generation_id: str, use_v2: bool = False, max_wait: int = 180) -> str:
    """Poll until generation is complete. Returns image URL."""
    headers = {
        "accept": "application/json",
        "authorization": f"Bearer {api_key}",
    }
    # v1 endpoint handles both v1 and v2 generation IDs
    url = f"{BASE_URL_V1}/generations/{generation_id}"
    waited = 0
    interval = 4

    while waited < max_wait:
        resp = requests.get(url, headers=headers, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        job = data.get("generations_by_pk", {})
        status = job.get("status", "")
        if status == "COMPLETE":
            images = job.get("generated_images", [])
            if images:
                return images[0]["url"]
            raise RuntimeError("Generation complete but no images returned")
        if status == "FAILED":
            raise RuntimeError(f"Generation failed: {job}")

        time.sleep(interval)
        waited += interval
        print(f"    ⏳ Waiting... ({waited}s)")

    raise TimeoutError(f"Generation timed out after {max_wait}s")


def start_generation(api_key: str, prompt: str, model_key: str, width: int = 1024, height: int = 512) -> tuple:
    """Route to v1 or v2 API based on model. Returns (generation_id, use_v2)."""
    if model_key in V2_MODELS:
        gen_id = start_generation_v2(api_key, prompt, width, height)
        return gen_id, True
    else:
        model_id = MODELS[model_key]
        gen_id = start_generation_v1(api_key, prompt, model_id, width, height)
        return gen_id, False


def download_image(url: str, output_path: Path) -> Path:
    """Download image from URL to local file."""
    resp = requests.get(url, timeout=60)
    resp.raise_for_status()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "wb") as f:
        f.write(resp.content)
    return output_path


def generate_image(api_key: str, prompt: str, model_key: str, output_path: Path) -> dict:
    """Full generate → poll → download cycle. Returns result dict."""
    print(f"  Prompt: {prompt[:90]}...")
    print(f"  Starting generation ({model_key})...")

    gen_id, use_v2 = start_generation(api_key, prompt, model_key)
    print(f"  Generation ID: {gen_id}")

    image_url = poll_generation(api_key, gen_id, use_v2=use_v2)
    print(f"  ✓ Generated: {image_url[:70]}...")

    local_path = download_image(image_url, output_path)
    print(f"  ✓ Saved: {local_path}")

    return {
        "generation_id": gen_id,
        "image_url": image_url,
        "local_path": str(local_path),
        "prompt": prompt,
        "model": model_key,
    }


def main():
    parser = argparse.ArgumentParser(description="Generate images via Leonardo AI")
    parser.add_argument("--stories", help="Path to stories JSON (generates one image per story)")
    parser.add_argument("--prompt", help="Single custom prompt")
    parser.add_argument("--filename", default="image", help="Output filename (no extension)")
    parser.add_argument("--output-dir", default=".tmp/images", help="Output directory")
    parser.add_argument("--model", default=DEFAULT_MODEL, choices=list(MODELS.keys()),
                        help="Model: nanobanana (default), phoenix, lucid, flux, reality, kino, lightning")
    parser.add_argument("--width", type=int, default=1024)
    parser.add_argument("--height", type=int, default=512)
    args = parser.parse_args()

    api_key = os.getenv("LEONARDO_API_KEY")
    if not api_key:
        print("ERROR: LEONARDO_API_KEY not set in .env")
        print("Get your key at: https://app.leonardo.ai/settings/api-keys")
        sys.exit(1)

    model_key = args.model
    output_dir = Path(args.output_dir)
    results = []

    if args.prompt:
        output_path = output_dir / f"{args.filename}.jpg"
        print(f"\nGenerating 1 image with model '{model_key}'...")
        result = generate_image(api_key, args.prompt, model_key, output_path)
        results.append(result)

    elif args.stories:
        raw = json.loads(Path(args.stories).read_text(encoding="utf-8"))
        stories = raw.get("stories", raw) if isinstance(raw, dict) else raw
        print(f"\nGenerating {len(stories)} images with model '{model_key}'...")

        for i, story in enumerate(stories, 1):
            company = story.get("company", f"story_{i}").lower().replace(" ", "_").replace("&", "")
            filename = f"{i:02d}_{company or 'story'}"
            output_path = output_dir / f"{filename}.jpg"

            print(f"\n[{i}/{len(stories)}] {story.get('title', '')[:60]}")
            try:
                prompt = build_prompt(story)
                result = generate_image(api_key, prompt, model_key, output_path)
                result["story_title"] = story.get("title")
                result["story_index"] = i
                results.append(result)
            except Exception as e:
                print(f"  ✗ Failed: {e}")
                results.append({
                    "story_index": i,
                    "story_title": story.get("title"),
                    "error": str(e),
                })

    else:
        parser.error("--stories or --prompt is required")

    # Save manifest
    manifest_path = output_dir / "images_manifest.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    successful = sum(1 for r in results if "error" not in r)
    print(f"\n✓ Done: {successful}/{len(results)} images generated")
    print(f"  Manifest: {manifest_path}")
    print(f"\nNext: update build_newsletter.py to load images from {output_dir}")
    return str(manifest_path)


if __name__ == "__main__":
    main()
