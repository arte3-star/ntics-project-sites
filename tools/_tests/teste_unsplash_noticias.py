"""
teste_unsplash_noticias.py — Testa busca de imagens Unsplash para carrossel de noticias.
Busca 5 resultados por keyword, baixa thumbnails para revisao visual.

Usage:
  python tools/teste_unsplash_noticias.py
"""

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

OUTPUT_DIR = Path(".tmp/teste-unsplash")

# Simulando as 6 noticias do ultimo carrossel com keywords do Perplexity
NOTICIAS = [
    {
        "card": "02-biodiversidade",
        "titulo": "Tratado do Alto Mar da ONU entra em vigor",
        "resumo": "Tratado historico cria reservas marinhas e regula uso sustentavel dos oceanos alem das jurisdicoes nacionais.",
        "keyword_original": "ocean treaty",
        "keywords_alternativas": ["UN high seas treaty", "marine conservation research", "ocean biodiversity protection"],
    },
    {
        "card": "03-energia",
        "titulo": "Portugal alcanca 80% de eletricidade renovavel",
        "resumo": "Em janeiro de 2026 Portugal gerou 80,7% de sua eletricidade a partir de fontes renovaveis.",
        "keyword_original": "wind turbines portugal",
        "keywords_alternativas": ["renewable energy europe", "wind farm coast", "portugal clean energy"],
    },
    {
        "card": "04-cooperacao-global",
        "titulo": "ONU declara 2026 Ano Internacional do Voluntariado",
        "resumo": "Nacoes Unidas reconhecem voluntariado como forca motriz para Agenda 2030.",
        "keyword_original": "volunteering community",
        "keywords_alternativas": ["UN volunteers global", "community garden volunteers", "international volunteering"],
    },
    {
        "card": "05-financas-verdes",
        "titulo": "Descarbonizacao gera retorno de US$221 milhoes por empresa",
        "resumo": "82% das empresas obtem beneficios economicos diretos com a descarbonizacao.",
        "keyword_original": "corporate sustainability",
        "keywords_alternativas": ["green finance boardroom", "ESG investment returns", "corporate decarbonization"],
    },
    {
        "card": "06-tecnologia",
        "titulo": "Brasil se posiciona como hub de data centers sustentaveis",
        "resumo": "Com 87% de matriz renovavel, Brasil atrai investimentos em data centers verdes.",
        "keyword_original": "sustainable data center",
        "keywords_alternativas": ["green data center solar", "brazil technology infrastructure", "renewable energy server farm"],
    },
    {
        "card": "07-estrategia-corporativa",
        "titulo": "UE ativa diretiva anti-greenwashing em 2026",
        "resumo": "Regulamentacao europeia obriga empresas a fornecer informacoes verificaveis sobre sustentabilidade.",
        "keyword_original": "EU parliament regulation",
        "keywords_alternativas": ["european union sustainability law", "corporate transparency regulation", "greenwashing legislation europe"],
    },
]


def search_unsplash(query, per_page=5):
    """Search Unsplash photos. Returns list of photo dicts."""
    api_key = os.getenv("UNSPLASH_API_KEY")
    resp = requests.get(
        "https://api.unsplash.com/search/photos",
        params={
            "query": query,
            "per_page": per_page,
            "orientation": "landscape",
            "content_filter": "high",
        },
        headers={"Authorization": f"Client-ID {api_key}"},
        timeout=15,
    )
    if not resp.ok:
        print(f"  ERROR {resp.status_code}: {resp.text[:200]}")
        return []
    data = resp.json()
    results = []
    for photo in data.get("results", []):
        results.append({
            "id": photo["id"],
            "description": photo.get("description") or photo.get("alt_description") or "sem descricao",
            "url_small": photo["urls"]["small"],       # 400px - para preview
            "url_regular": photo["urls"]["regular"],   # 1080px - para uso
            "url_full": photo["urls"]["full"],         # original
            "photographer": photo["user"]["name"],
            "download_link": photo["links"]["download_location"],
        })
    return results


def download_image(url, path):
    """Download image to local path."""
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    path.write_bytes(resp.content)
    return len(resp.content)


def main():
    api_key = os.getenv("UNSPLASH_API_KEY")
    if not api_key:
        print("ERROR: UNSPLASH_API_KEY not set in .env")
        sys.exit(1)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    all_results = {}

    for noticia in NOTICIAS:
        card = noticia["card"]
        card_dir = OUTPUT_DIR / card
        card_dir.mkdir(parents=True, exist_ok=True)

        print(f"\n{'='*60}")
        print(f"CARD: {card}")
        print(f"NOTICIA: {noticia['titulo']}")
        print(f"RESUMO: {noticia['resumo']}")

        # Busca com keyword original
        all_keywords = [noticia["keyword_original"]] + noticia["keywords_alternativas"]
        card_results = []

        for i, kw in enumerate(all_keywords):
            print(f"\n  Buscando: '{kw}'")
            photos = search_unsplash(kw, per_page=3)
            print(f"  Encontradas: {len(photos)} fotos")

            for j, photo in enumerate(photos):
                fname = f"kw{i}_opt{j}_{photo['id']}.jpg"
                fpath = card_dir / fname
                size = download_image(photo["url_small"], fpath)
                print(f"    [{j}] {photo['description'][:80]} ({size//1024}KB) by {photo['photographer']}")
                card_results.append({
                    **photo,
                    "keyword_used": kw,
                    "local_preview": str(fpath),
                })

        all_results[card] = {
            "noticia": noticia,
            "options": card_results,
        }

    # Save manifest
    manifest = OUTPUT_DIR / "manifest.json"
    with open(manifest, "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)

    print(f"\n{'='*60}")
    print(f"TESTE CONCLUIDO")
    print(f"Pasta: {OUTPUT_DIR}")
    print(f"Total de imagens baixadas: {sum(len(v['options']) for v in all_results.values())}")
    print(f"Manifest: {manifest}")


if __name__ == "__main__":
    main()
