"""
fetch_images_unsplash.py — Download contextual editorial photos from Unsplash API.

Searches Unsplash for high-quality editorial photos matching each story's theme.
Falls back to Leonardo Nano Banana 2 if Unsplash doesn't find a match.

Usage:
  python tools/fetch_images_unsplash.py \
    --stories .tmp/stories_2026-03-20.json \
    --output-dir .tmp/images/2026-03-20

  python tools/fetch_images_unsplash.py \
    --prompt "solar farm renewable energy" \
    --filename test_image \
    --output-dir .tmp/images

Environment:
  UNSPLASH_API_KEY=... (in .env) — free key at https://unsplash.com/developers
  LEONARDO_API_KEY=... (fallback if Unsplash returns no results)
"""

import argparse
import json
import os
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

load_dotenv()

UNSPLASH_API = "https://api.unsplash.com/search/photos"

# Keyword → Unsplash search query mapping (specific, editorial-quality queries)
TOPIC_QUERIES = [
    (["renewable", "solar", "eólica", "wind", "energia renovável", "clean energy", "energia limpa"],
     "solar farm renewable energy golden hour aerial"),
    (["agriculture", "farm", "fazenda", "regenerat", "agricult", "solo", "crop", "pesticida"],
     "sustainable agriculture regenerative farm sunrise field"),
    (["forest", "floresta", "amazon", "amazônia", "biodiversity", "biodiversidade", "cerrado"],
     "amazon rainforest aerial river mist canopy"),
    (["education", "digital", "skill", "capacit", "habilidade", "learn", "fellowship"],
     "diverse students laptops technology education modern"),
    (["supplier", "supply", "fornecedor", "fornecedores", "cadeia", "chain"],
     "multicultural diverse team office collaboration"),
    (["carbon", "emissão", "emission", "net zero", "neutralidade", "climate", "clima"],
     "green corporate building sustainability trees"),
    (["women", "gender", "gênero", "female", "mulher", "liderança feminina", "paridade"],
     "diverse professional women leadership boardroom"),
    (["finance", "bank", "banco", "invest", "crédito", "credit", "bond", "green bond"],
     "sustainable finance green building glass architecture"),
    (["ocean", "water", "sea", "marine", "mar", "oceano"],
     "pristine ocean aerial blue water coral reef coastline"),
    (["city", "urban", "transport", "mobility", "cidade"],
     "sustainable green city rooftop gardens electric transport"),
    (["circular", "waste", "residuo", "recycl", "reciclagem"],
     "recycling circular economy sustainable manufacturing"),
    (["health", "saúde", "medical", "well-being", "bem-estar"],
     "modern hospital healthcare diverse medical professionals"),
    (["water", "água", "sanitation", "saneamento"],
     "clean water treatment facility engineering blue"),
]

CATEGORY_QUERIES = {
    "environment": "environmental sustainability green nature aerial",
    "social": "diverse community people partnership connection",
    "governance": "professional corporate leadership modern office",
}


def get_search_query(story: dict) -> str:
    """Map story content to the best Unsplash search query."""
    combined = f"{story.get('title', '')} {story.get('summary', '')} {story.get('company', '')}".lower()
    for keywords, query in TOPIC_QUERIES:
        if any(k in combined for k in keywords):
            return query
    return CATEGORY_QUERIES.get(story.get("category", "environment"), "corporate sustainability")


def search_unsplash(query: str, api_key: str) -> str | None:
    """Search Unsplash and return the URL of the best match (regular ~1080px)."""
    try:
        resp = requests.get(
            UNSPLASH_API,
            params={
                "query": query,
                "orientation": "landscape",
                "per_page": 5,
                "content_filter": "high",
            },
            headers={"Authorization": f"Client-ID {api_key}"},
            timeout=15,
        )
        if not resp.ok:
            print(f"    Unsplash {resp.status_code}: {resp.text[:150]}")
            return None
        results = resp.json().get("results", [])
        if not results:
            return None
        # Pick the result with the highest likes (most relevant/high-quality)
        best = max(results, key=lambda r: r.get("likes", 0))
        return best["urls"]["regular"]
    except Exception as e:
        print(f"    Unsplash request failed: {e}")
        return None


def download_image(url: str, output_path: Path) -> Path:
    """Download image from URL to local file."""
    resp = requests.get(url, timeout=60)
    resp.raise_for_status()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "wb") as f:
        f.write(resp.content)
    return output_path


def fetch_story_image(story: dict, unsplash_key: str, output_path: Path) -> dict:
    """Try Unsplash first, then fall back to Leonardo Nano Banana 2."""
    query = get_search_query(story)
    print(f"  Unsplash query: '{query}'")

    url = search_unsplash(query, unsplash_key)
    if url:
        local = download_image(url, output_path)
        print(f"  ✓ Unsplash: {url[:80]}...")
        return {
            "source": "unsplash",
            "image_url": url,
            "local_path": str(local),
            "query": query,
        }

    # Fallback: Leonardo Nano Banana 2
    print(f"  Unsplash found nothing — falling back to Leonardo AI")
    leo_key = os.getenv("LEONARDO_API_KEY")
    if not leo_key:
        print("  ✗ LEONARDO_API_KEY not set; skipping image")
        return {"source": "none", "image_url": "", "local_path": ""}

    # Import Leonardo functions from sibling module
    sys.path.insert(0, str(Path(__file__).parent))
    from generate_images_leonardo import build_prompt, generate_image

    result = generate_image(leo_key, build_prompt(story), "nanobanana", output_path)
    result["source"] = "leonardo"
    return result


def main():
    parser = argparse.ArgumentParser(description="Fetch contextual images from Unsplash (+ Leonardo fallback)")
    parser.add_argument("--stories", help="Path to stories JSON")
    parser.add_argument("--prompt", help="Single custom search query")
    parser.add_argument("--filename", default="image", help="Output filename (no extension)")
    parser.add_argument("--output-dir", default=".tmp/images", help="Output directory")
    args = parser.parse_args()

    api_key = os.getenv("UNSPLASH_API_KEY")
    if not api_key:
        print("ERROR: UNSPLASH_API_KEY not set in .env")
        print("Get a free key at: https://unsplash.com/developers")
        sys.exit(1)

    output_dir = Path(args.output_dir)
    results = []

    if args.prompt:
        output_path = output_dir / f"{args.filename}.jpg"
        print(f"\nFetching 1 image for query: '{args.prompt}'")
        url = search_unsplash(args.prompt, api_key)
        if url:
            local = download_image(url, output_path)
            results.append({"source": "unsplash", "image_url": url, "local_path": str(local), "query": args.prompt})
            print(f"  ✓ Saved: {local}")
        else:
            print("  ✗ No results found")

    elif args.stories:
        raw = json.loads(Path(args.stories).read_text(encoding="utf-8"))
        stories = raw.get("stories", raw) if isinstance(raw, dict) else raw
        print(f"\nFetching {len(stories)} images from Unsplash...")

        for i, story in enumerate(stories, 1):
            company = story.get("company", f"story_{i}").lower().replace(" ", "_").replace("&", "")
            filename = f"{i:02d}_{company or 'story'}"
            output_path = output_dir / f"{filename}.jpg"

            print(f"\n[{i}/{len(stories)}] {story.get('title', '')[:60]}")
            try:
                result = fetch_story_image(story, api_key, output_path)
                result["story_index"] = i
                result["story_title"] = story.get("title")
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

    successful = sum(1 for r in results if "error" not in r and r.get("image_url"))
    print(f"\n✓ Done: {successful}/{len(results)} images fetched")
    print(f"  Manifest: {manifest_path}")
    return str(manifest_path)


if __name__ == "__main__":
    main()
