"""
fetch_images_google.py — Download contextual photos via Serper.dev (Google Images).

Searches Google Images via Serper.dev API for high-quality real photographs matching
each story's theme. Falls back to Leonardo Nano Banana 2 if Serper returns no results.

Serper.dev: 2.500 queries/mês grátis, sem cartão de crédito.
  Cadastro: https://serper.dev

Usage:
  python tools/media/fetch_images_google.py \\
    --stories .tmp/stories_2026-04-04.json \\
    --output-dir .tmp/images/2026-04-04-google

  python tools/media/fetch_images_google.py \\
    --prompt "solar farm renewable energy Brazil" \\
    --filename test_solar \\
    --output-dir .tmp/images

  python tools/media/fetch_images_google.py \\
    --story-title "ISA Energia constrói linha subterrânea" \\
    --story-cena "Underground cable installation workers urban street Brazil" \\
    --filename isa_energia \\
    --output-dir .tmp/images

Environment:
  SERPER_API_KEY=...   — from serper.dev (2.500 free queries/month, no credit card)
  LEONARDO_API_KEY=... — fallback if Serper returns no downloadable results

Rate limits: 2.500 queries/month free. ~312 carrosseis/year at 6 stories each.

Estratégia de query usada no pipeline:
  1. título da notícia (tenta foto do artigo real)
  2. cena_foto do Perplexity (descrição de cena específica)
  → fallback Leonardo se ambas falharem
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

load_dotenv()

SERPER_API = "https://google.serper.dev/images"

# Keyword → query de fallback (usada quando não há título/cena disponíveis)
TOPIC_QUERIES = [
    (["renewable", "solar", "eólica", "wind", "energia renovável", "clean energy", "energia limpa"],
     "solar energy farm aerial photo Brazil"),
    (["agriculture", "farm", "fazenda", "regenerat", "agricult", "solo", "crop"],
     "regenerative agriculture sustainable farm photo"),
    (["forest", "floresta", "amazon", "amazônia", "biodiversity", "cerrado"],
     "Amazon rainforest aerial photography Brazil"),
    (["education", "digital", "skill", "capacit", "learn", "fellowship"],
     "digital education technology students classroom photo"),
    (["supplier", "supply", "fornecedor", "cadeia", "chain"],
     "diverse professional team office collaboration photo"),
    (["carbon", "emissão", "emission", "net zero", "neutralidade", "climate"],
     "green corporate sustainability building photo"),
    (["women", "gender", "gênero", "female", "mulher", "liderança feminina"],
     "women leadership business diversity photo"),
    (["finance", "bank", "banco", "invest", "crédito", "bond", "green bond"],
     "sustainable finance ESG investment photo"),
    (["ocean", "water", "sea", "marine", "mar", "oceano"],
     "ocean conservation clean water aerial photo"),
    (["city", "urban", "transport", "mobility", "cidade"],
     "sustainable city green urban transport photo"),
    (["circular", "waste", "residuo", "recycl", "reciclagem"],
     "circular economy recycling sustainable manufacturing photo"),
    (["health", "saúde", "medical", "well-being"],
     "healthcare hospital diverse professionals photo"),
    (["water", "água", "sanitation", "saneamento"],
     "clean water treatment engineering photo"),
    (["social", "community", "comunidade", "impacto social"],
     "community social impact people photo Brazil"),
    (["ods", "sdg", "objetivo", "desenvolvimento sustentável"],
     "sustainable development goals community photo Brazil"),
]

CATEGORY_QUERIES = {
    "environment": "environmental sustainability green nature photo",
    "social": "diverse community people partnership photo",
    "governance": "corporate leadership modern office professionals photo",
}

MIN_WIDTH = 600
MIN_HEIGHT = 400


def get_topic_query(story: dict) -> str:
    """Fallback: mapeia keywords da story para uma query temática."""
    combined = f"{story.get('title', '')} {story.get('summary', '')} {story.get('company', '')}".lower()
    for keywords, query in TOPIC_QUERIES:
        if any(k in combined for k in keywords):
            return query
    return CATEGORY_QUERIES.get(story.get("category", "environment"), "corporate sustainability photo")


def search_serper(query: str, api_key: str, num: int = 5, gl: str = "br") -> list[dict]:
    """
    Busca imagens no Google Images via Serper.dev.
    Retorna lista de items: {imageUrl, imageWidth, imageHeight, title, source, link}
    """
    try:
        resp = requests.post(
            SERPER_API,
            headers={"X-API-KEY": api_key, "Content-Type": "application/json"},
            json={"q": query, "num": num, "gl": gl, "hl": "pt"},
            timeout=15,
        )
        if not resp.ok:
            print(f"    Serper {resp.status_code}: {resp.text[:150]}")
            return []
        return resp.json().get("images", [])
    except Exception as e:
        print(f"    Serper request failed: {e}")
        return []


def _is_usable(item: dict) -> bool:
    """Descarta imagens muito pequenas (provavelmente logos ou thumbnails)."""
    w = item.get("imageWidth", 0)
    h = item.get("imageHeight", 0)
    return w >= MIN_WIDTH and h >= MIN_HEIGHT


def download_image(url: str, output_path: Path) -> Path:
    """Download image from URL to local file."""
    resp = requests.get(url, timeout=60, headers={"User-Agent": "Mozilla/5.0"})
    resp.raise_for_status()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "wb") as f:
        f.write(resp.content)
    return output_path


def search_and_download(query: str, api_key: str, output_path: Path, num: int = 5) -> dict | None:
    """
    Busca no Serper e baixa a melhor imagem disponível (com retry em até 3 URLs).
    Retorna {image_url, local_path, query} ou None.
    """
    items = search_serper(query, api_key, num=num)
    # Prioriza itens com tamanho adequado
    usable = [i for i in items if _is_usable(i)]
    candidates = usable if usable else items

    for item in candidates[:3]:
        url = item.get("imageUrl", "")
        if not url:
            continue
        try:
            local = download_image(url, output_path)
            return {"image_url": url, "local_path": str(local), "query": query}
        except Exception as e:
            print(f"    Download falhou ({url[:60]}...): {e}")
    return None


def fetch_story_image(story: dict, api_key: str, output_path: Path) -> dict:
    """
    Busca imagem para uma story usando duas estratégias em sequência:
      1. título da notícia (tenta pegar foto real do artigo)
      2. cena_foto do Perplexity (descrição de cena específica)
    Fallback: Leonardo Nano Banana 2.

    Retorna manifest dict: {source, image_url, local_path, query}
    """
    titulo = story.get("titulo") or story.get("title", "")
    cena = story.get("cena_foto", "")

    # Estratégia 1: título da notícia
    if titulo:
        print(f"  [1/2] Serper query (título): '{titulo[:70]}'")
        result = search_and_download(titulo, api_key, output_path)
        if result:
            print(f"  ✓ Serper (título): {result['image_url'][:80]}...")
            return {"source": "serper", **result}

    # Estratégia 2: cena_foto
    query2 = cena[:120] if cena else get_topic_query(story)
    print(f"  [2/2] Serper query (cena): '{query2[:70]}'")
    result = search_and_download(query2, api_key, output_path)
    if result:
        print(f"  ✓ Serper (cena): {result['image_url'][:80]}...")
        return {"source": "serper", **result}

    # Fallback: Leonardo AI
    print(f"  Serper sem resultado — fallback Leonardo AI")
    leo_key = os.getenv("LEONARDO_API_KEY")
    if not leo_key:
        print("  ✗ LEONARDO_API_KEY não configurada; sem imagem")
        return {"source": "none", "image_url": "", "local_path": "", "query": query2}

    sys.path.insert(0, str(Path(__file__).parent))
    from generate_images_leonardo import build_prompt, generate_image

    result = generate_image(leo_key, build_prompt(story), "nanobanana", output_path)
    result["source"] = "leonardo"
    result["query"] = query2
    return result


def main():
    parser = argparse.ArgumentParser(
        description="Fetch contextual photos from Google Images via Serper.dev"
    )
    parser.add_argument("--stories", help="Path to stories JSON file")
    parser.add_argument("--prompt", help="Single search query")
    parser.add_argument("--story-title", help="Título da notícia (query primária)")
    parser.add_argument("--story-cena", help="Descrição de cena (query secundária)")
    parser.add_argument("--filename", default="image", help="Nome do arquivo de saída (sem extensão)")
    parser.add_argument("--output-dir", default=".tmp/images", help="Diretório de saída")
    parser.add_argument("--num", type=int, default=5, help="Resultados por query (max 10)")
    args = parser.parse_args()

    api_key = os.getenv("SERPER_API_KEY")
    if not api_key:
        print("ERROR: SERPER_API_KEY não encontrada no .env")
        print("  Cadastre-se em https://serper.dev (gratuito, sem cartão)")
        print("  Depois adicione: SERPER_API_KEY=sua_chave ao .env")
        sys.exit(1)

    output_dir = Path(args.output_dir)
    results = []

    if args.prompt:
        # Busca simples por query direta
        output_path = output_dir / f"{args.filename}.jpg"
        print(f"\nBuscando imagem para: '{args.prompt}'")
        result = search_and_download(args.prompt, api_key, output_path, num=args.num)
        if result:
            results.append({"source": "serper", **result})
            print(f"  ✓ Salvo: {output_path}")
        else:
            print("  ✗ Sem resultados")

    elif args.story_title or args.story_cena:
        # Busca com título + cena (simula o fluxo do pipeline)
        story = {"titulo": args.story_title or "", "cena_foto": args.story_cena or ""}
        output_path = output_dir / f"{args.filename}.jpg"
        print(f"\nBuscando imagem (título + cena)...")
        result = fetch_story_image(story, api_key, output_path)
        results.append(result)
        if result.get("image_url"):
            print(f"  ✓ Salvo: {output_path}")

    elif args.stories:
        raw = json.loads(Path(args.stories).read_text(encoding="utf-8"))
        stories = raw.get("stories", raw) if isinstance(raw, dict) else raw
        total = len(stories)
        print(f"\nBuscando {total} imagens via Serper.dev...")

        for i, story in enumerate(stories, 1):
            # Suporta tanto schema "titulo" (noticias) quanto "title" (genérico)
            titulo = story.get("titulo") or story.get("title", f"story_{i}")
            company = story.get("company", f"story_{i}").lower()
            slug = re.sub(r"[^a-z0-9]", "_", company).strip("_") or f"story_{i}"
            filename = f"{i:02d}_{slug}"
            output_path = output_dir / f"{filename}.jpg"

            print(f"\n[{i}/{total}] {titulo[:65]}")
            try:
                result = fetch_story_image(story, api_key, output_path)
                result["story_index"] = i
                result["story_title"] = titulo
                results.append(result)
            except Exception as e:
                print(f"  ✗ Erro: {e}")
                results.append({"story_index": i, "story_title": titulo, "error": str(e)})

    else:
        parser.error("--stories, --prompt ou --story-title é obrigatório")

    # Salvar manifest
    manifest_path = output_dir / "images_manifest.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    successful = sum(1 for r in results if "error" not in r and r.get("image_url"))
    serper_count = sum(1 for r in results if r.get("source") == "serper")
    leo_count = sum(1 for r in results if r.get("source") == "leonardo")
    print(f"\n✓ Concluído: {successful}/{len(results)} imagens")
    if results:
        print(f"  Fontes: {serper_count} Serper (Google Images), {leo_count} Leonardo AI")
    print(f"  Manifest: {manifest_path}")
    return str(manifest_path)


if __name__ == "__main__":
    main()
