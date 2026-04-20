"""
teste_og_image.py — Testa extracao de imagens editoriais (og:image) direto das materias.
Cada artigo jornalistico tem uma meta tag og:image com a foto principal da materia.

Usage:
  python tools/teste_og_image.py
"""

import re
import sys
from pathlib import Path

import requests

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

OUTPUT_DIR = Path(".tmp/teste-og-image")

# URLs reais de noticias ESG (simulando o que o Perplexity retornaria)
NOTICIAS_TESTE = [
    {
        "titulo": "Tratado do Alto Mar da ONU entra em vigor",
        "fonte": "Euronews",
        "url": "https://www.euronews.com/green/2025/09/18/un-high-seas-treaty-all-you-need-to-know-about-the-landmark-ocean-agreement",
    },
    {
        "titulo": "Portugal alcanca 80% de eletricidade renovavel",
        "fonte": "Euronews",
        "url": "https://www.euronews.com/green/2025/02/05/portugal-generated-807-of-its-electricity-from-renewables-in-january",
    },
    {
        "titulo": "UE ativa diretiva anti-greenwashing",
        "fonte": "European Commission",
        "url": "https://commission.europa.eu/live-work-travel-eu/consumer-rights-and-complaints/enforcement-consumer-protection/coordinated-actions/greenwashing_en",
    },
    {
        "titulo": "Brasil hub de data centers sustentaveis",
        "fonte": "Reuters",
        "url": "https://www.reuters.com/technology/brazil-becoming-global-data-center-hub-2024-10-15/",
    },
    {
        "titulo": "Descarbonizacao gera retorno financeiro",
        "fonte": "World Economic Forum",
        "url": "https://www.weforum.org/stories/2025/01/decarbonization-business-case-climate-action/",
    },
    {
        "titulo": "ONU declara 2026 Ano do Voluntariado",
        "fonte": "UN Volunteers",
        "url": "https://www.unv.org/news/2026-international-year-volunteerism",
    },
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


def extract_og_image(html):
    """Extract og:image URL from HTML meta tags."""
    # Try og:image first
    patterns = [
        r'<meta\s+property=["\']og:image["\']\s+content=["\'](.*?)["\']',
        r'<meta\s+content=["\'](.*?)["\']\s+property=["\']og:image["\']',
        r'<meta\s+name=["\']twitter:image["\']\s+content=["\'](.*?)["\']',
        r'<meta\s+content=["\'](.*?)["\']\s+name=["\']twitter:image["\']',
        r'<meta\s+property=["\']og:image:url["\']\s+content=["\'](.*?)["\']',
    ]
    for pattern in patterns:
        match = re.search(pattern, html, re.IGNORECASE)
        if match:
            return match.group(1)
    return None


def extract_og_title(html):
    """Extract og:title for context."""
    match = re.search(r'<meta\s+property=["\']og:title["\']\s+content=["\'](.*?)["\']', html, re.IGNORECASE)
    if not match:
        match = re.search(r'<meta\s+content=["\'](.*?)["\']\s+property=["\']og:title["\']', html, re.IGNORECASE)
    return match.group(1) if match else None


def download_image(url, path):
    """Download image to local path. Returns file size."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15, allow_redirects=True)
        resp.raise_for_status()
        content_type = resp.headers.get("content-type", "")
        if "image" in content_type or url.endswith((".jpg", ".jpeg", ".png", ".webp")):
            path.write_bytes(resp.content)
            return len(resp.content)
        else:
            # Some og:image URLs redirect or return HTML - save anyway to inspect
            path.write_bytes(resp.content)
            return len(resp.content)
    except Exception as e:
        print(f"    Download failed: {e}")
        return 0


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    results = []

    for i, noticia in enumerate(NOTICIAS_TESTE):
        print(f"\n{'='*60}")
        print(f"[{i+1}] {noticia['titulo']}")
        print(f"    Fonte: {noticia['fonte']}")
        print(f"    URL: {noticia['url']}")

        try:
            resp = requests.get(noticia["url"], headers=HEADERS, timeout=15, allow_redirects=True)
            print(f"    HTTP: {resp.status_code}")

            if resp.status_code != 200:
                print(f"    FALHOU: HTTP {resp.status_code}")
                results.append({**noticia, "status": "http_error", "code": resp.status_code})
                continue

            html = resp.text
            og_image = extract_og_image(html)
            og_title = extract_og_title(html)

            if og_title:
                print(f"    og:title = {og_title[:80]}")

            if og_image:
                print(f"    og:image = {og_image[:120]}")

                # Download the image
                ext = ".jpg"
                if ".png" in og_image:
                    ext = ".png"
                elif ".webp" in og_image:
                    ext = ".webp"

                fname = f"{i+1:02d}-{noticia['fonte'].lower().replace(' ', '_')}{ext}"
                fpath = OUTPUT_DIR / fname
                size = download_image(og_image, fpath)

                if size > 0:
                    print(f"    SALVO: {fpath} ({size//1024}KB)")
                    results.append({**noticia, "status": "ok", "og_image": og_image, "local": str(fpath), "size_kb": size//1024})
                else:
                    print(f"    FALHOU ao baixar imagem")
                    results.append({**noticia, "status": "download_failed", "og_image": og_image})
            else:
                print(f"    SEM og:image encontrado!")
                results.append({**noticia, "status": "no_og_image"})

        except Exception as e:
            print(f"    ERRO: {e}")
            results.append({**noticia, "status": "error", "error": str(e)})

    # Summary
    print(f"\n{'='*60}")
    print("RESUMO:")
    ok = sum(1 for r in results if r.get("status") == "ok")
    print(f"  Imagens encontradas e baixadas: {ok}/{len(NOTICIAS_TESTE)}")
    for r in results:
        status_icon = "OK" if r["status"] == "ok" else "FALHOU"
        print(f"  [{status_icon}] {r['titulo'][:50]} — {r.get('og_image', 'N/A')[:60]}")


if __name__ == "__main__":
    main()
