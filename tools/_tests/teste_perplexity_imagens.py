"""
teste_perplexity_imagens.py — Testa se o Perplexity consegue retornar URLs de imagens
das materias junto com as noticias.

Usage:
  python tools/teste_perplexity_imagens.py
"""

import json
import os
import sys

import requests
from dotenv import load_dotenv

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

load_dotenv()


def search_news_with_images(api_key):
    """Ask Perplexity to find ESG news AND their article images."""

    prompt = """Quais sao as 6 noticias positivas mais recentes (ultimos 7 dias) sobre ESG, sustentabilidade e responsabilidade social corporativa no Brasil e no mundo?

Para cada noticia, forneca:
1) Titulo curto (maximo 10 palavras)
2) Paragrafo resumo (3-4 frases)
3) Fonte (nome do veiculo)
4) URL da materia original
5) URL da imagem principal da materia (a foto/imagem que aparece no topo do artigo ou no compartilhamento em redes sociais - og:image). Se nao conseguir encontrar a imagem exata, retorne null.
6) Categoria (ESTRATEGIA CORPORATIVA, INFRAESTRUTURA, RECURSOS HIDRICOS, EDUCACAO, COOPERACAO GLOBAL, FINANCAS VERDES, ENERGIA, BIODIVERSIDADE ou TECNOLOGIA)

IMPORTANTE sobre a imagem: Preciso da URL direta da imagem (terminando em .jpg, .png, .webp ou similar) que o veiculo usa como capa da materia.

Responda em portugues brasileiro. Formate como JSON array com campos: titulo, resumo, fonte, url, imagem_url, categoria."""

    resp = requests.post(
        "https://api.perplexity.ai/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": "sonar",
            "messages": [{"role": "user", "content": prompt}],
            "search_recency_filter": "week",
        },
        timeout=30,
    )

    if not resp.ok:
        print(f"ERROR {resp.status_code}: {resp.text[:400]}")
        return None

    data = resp.json()
    content = data["choices"][0]["message"]["content"]
    citations = data.get("citations", [])

    return content, citations


def main():
    api_key = os.getenv("PERPLEXITY_API_KEY")
    if not api_key:
        print("ERROR: PERPLEXITY_API_KEY not set")
        sys.exit(1)

    print("Buscando noticias ESG com imagens via Perplexity...\n")
    result = search_news_with_images(api_key)

    if not result:
        print("Falhou.")
        sys.exit(1)

    content, citations = result

    print("=" * 60)
    print("RESPOSTA DO PERPLEXITY:")
    print("=" * 60)
    print(content)
    print("\n" + "=" * 60)
    print("CITATIONS:")
    print("=" * 60)
    for i, c in enumerate(citations):
        print(f"  [{i+1}] {c}")

    # Try to parse JSON from the response
    print("\n" + "=" * 60)
    print("ANALISE DAS IMAGENS:")
    print("=" * 60)

    # Extract JSON from markdown code block if present
    json_text = content
    if "```json" in content:
        json_text = content.split("```json")[1].split("```")[0]
    elif "```" in content:
        json_text = content.split("```")[1].split("```")[0]

    try:
        noticias = json.loads(json_text)
        for n in noticias:
            titulo = n.get("titulo", "?")
            img = n.get("imagem_url") or n.get("image_url") or n.get("imagem")
            print(f"\n  {titulo}")
            if img and img != "null" and img != "None":
                print(f"    IMAGEM: {img}")
            else:
                print(f"    SEM IMAGEM")
    except json.JSONDecodeError as e:
        print(f"  Nao foi possivel parsear JSON: {e}")
        print(f"  Resposta bruta salva para analise manual.")

    # Save raw response
    out = {"content": content, "citations": citations}
    with open(".tmp/teste-og-image/perplexity_response.json", "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"\nResposta salva em .tmp/teste-og-image/perplexity_response.json")


if __name__ == "__main__":
    main()
