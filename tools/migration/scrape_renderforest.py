#!/usr/bin/env python3
"""
scrape_renderforest.py — Baixa HTML + imagens + estrutura de uma landing page do Render Forest.

Uso:
  python tools/migration/scrape_renderforest.py \
    --url https://24321761-1313139.renderforestsites.com/ \
    --slug cultura-robotica-ferroporte \
    --out-root assets/projetos \
    --folder-name "81. CULTURA ROBÓTICA (FERROPORTE)"

Output (convenção NTICS):
  assets/projetos/{folder-name}/
    ├── FOTOS/         → rf-{site_id}-{hash}.jpg (todas as fotos do projeto)
    ├── LOGOS/         → {slug}.png (logo principal se detectado)
    ├── REGUAS/        → {slug}_regua.jpg (régua de patrocinadores se detectada)
    ├── site.html      → HTML original do RF (referência)
    └── scrape.json    → estrutura textual + metadados

Estratégia:
  1. Playwright renderiza JS (captura lazy-loaded + CSS background-image)
  2. Scrolla a página inteira pra forçar lazy load
  3. Download com header Referer (evita 403 do hotlink protection do RF)
  4. Estrutura textual: títulos, parágrafos, links, seções

Aprendizados incorporados:
  - Regex no HTML cru perde imagens lazy-loaded → usa Playwright DOM
  - Downloads diretos dão 403 no hotlink → precisa Referer
  - Imagens podem estar em CSS background-image → computed style
"""

import argparse
import asyncio
import json
import re
import ssl
import sys
import urllib.request
from html import unescape
from pathlib import Path
from urllib.parse import urlparse

from playwright.async_api import async_playwright

ROOT = Path(__file__).resolve().parents[2]

_ctx = ssl.create_default_context()
_ctx.check_hostname = False
_ctx.verify_mode = ssl.CERT_NONE

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36"


def download_image(url: str, dest: Path, referer: str) -> bool:
    """Download com header Referer. Retorna True se sucesso."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA, "Referer": referer, "Accept": "image/avif,image/webp,*/*"})
        data = urllib.request.urlopen(req, context=_ctx, timeout=25).read()
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
        return True
    except Exception as e:
        print(f"  ERR {dest.name}: {e}", file=sys.stderr)
        return False


async def scrape(url: str, out_dir: Path, slug: str) -> dict:
    """Scrape completo com Playwright: DOM + CSS bg + download assets."""
    fotos_dir = out_dir / "FOTOS"
    logos_dir = out_dir / "LOGOS"
    reguas_dir = out_dir / "REGUAS"
    fotos_dir.mkdir(parents=True, exist_ok=True)
    logos_dir.mkdir(parents=True, exist_ok=True)
    reguas_dir.mkdir(parents=True, exist_ok=True)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        ctx = await browser.new_context(viewport={"width": 1440, "height": 900}, user_agent=UA)
        page = await ctx.new_page()
        print(f"Fetching {url}...", file=sys.stderr)
        await page.goto(url, wait_until="networkidle", timeout=60000)
        await asyncio.sleep(3)

        # Scroll pra forçar lazy load
        await page.evaluate(
            """async () => {
                await new Promise(resolve => {
                    let total = 0;
                    const distance = 200;
                    const timer = setInterval(() => {
                        window.scrollBy(0, distance);
                        total += distance;
                        if (total >= document.body.scrollHeight) {
                            clearInterval(timer);
                            resolve();
                        }
                    }, 100);
                });
            }"""
        )
        await asyncio.sleep(2)
        await page.evaluate("window.scrollTo(0, 0)")
        await asyncio.sleep(1)

        # Salva HTML renderizado
        html = await page.content()
        (out_dir / "site.html").write_text(html, encoding="utf-8")

        # Captura tudo via JS
        scraped = await page.evaluate(
            """() => {
                const imgs = [];
                document.querySelectorAll('img').forEach(img => {
                    if (img.src && !img.src.startsWith('data:')) {
                        imgs.push({type: 'img', src: img.src, w: img.naturalWidth, h: img.naturalHeight, alt: img.alt || ''});
                    }
                });
                document.querySelectorAll('*').forEach(el => {
                    const bg = window.getComputedStyle(el).backgroundImage;
                    if (bg && bg !== 'none' && bg.includes('url(')) {
                        const matches = bg.matchAll(/url\\(["']?([^"')]+)["']?\\)/g);
                        for (const m of matches) {
                            if (!m[1].startsWith('data:')) {
                                imgs.push({type: 'bg', src: m[1], w: 0, h: 0, alt: ''});
                            }
                        }
                    }
                });
                const links = [];
                document.querySelectorAll('a').forEach(a => {
                    if (a.href && !a.href.startsWith('javascript:') && !a.href.startsWith('mailto:') && !a.href.includes('renderforest.com')) {
                        links.push({href: a.href, text: (a.textContent || '').trim().substring(0, 80)});
                    }
                });
                const title = document.title || '';
                const h1 = Array.from(document.querySelectorAll('h1')).map(el => el.innerText.trim()).filter(Boolean);
                const h2 = Array.from(document.querySelectorAll('h2')).map(el => el.innerText.trim()).filter(Boolean);
                const h3 = Array.from(document.querySelectorAll('h3')).map(el => el.innerText.trim()).filter(Boolean);
                const paragraphs = Array.from(document.querySelectorAll('p')).map(el => el.innerText.trim()).filter(t => t.length > 5).slice(0, 80);
                const sections = [];
                document.querySelectorAll('section').forEach(s => {
                    const h = s.querySelector('h1, h2, h3');
                    if (h) sections.push({title: h.innerText.trim().substring(0, 100), text: s.innerText.trim().substring(0, 500)});
                });
                return {imgs, links, title, h1, h2, h3, paragraphs, sections};
            }"""
        )
        await browser.close()

    # Dedup images por src
    seen = set()
    unique_imgs = []
    for im in scraped["imgs"]:
        if im["src"] in seen or "renderforest_logo" in im["src"] or "rfstat.com" in im["src"]:
            continue
        seen.add(im["src"])
        unique_imgs.append(im)

    print(f"  Found {len(unique_imgs)} unique images, downloading with Referer...", file=sys.stderr)
    downloaded = []
    logo_found = None
    reguas_found = []
    for im in unique_imgs:
        parsed = urlparse(im["src"])
        # Nome padrão: rf-{site_id}-{hash}.ext
        parts = parsed.path.strip("/").split("/")
        if len(parts) >= 4 and parts[0].isdigit() and parts[1].isdigit():
            name = f"rf-{parts[1]}-{parts[-1]}"
        else:
            name = parts[-1] if parts else "img"
        dest = fotos_dir / name
        if download_image(im["src"], dest, url):
            size = dest.stat().st_size
            downloaded.append({"src": im["src"], "local": str(dest.relative_to(ROOT)).replace("\\", "/"), "size": size, "w": im.get("w", 0), "h": im.get("h", 0), "alt": im.get("alt", "")})
            # Heurística: logos são PNG pequenos (< 50KB) e quadrados/landscape pequenos
            ext = dest.suffix.lower()
            if ext == ".png" and size < 50_000 and logo_found is None:
                import shutil
                logo_name = f"{slug}.png"
                shutil.copy(dest, logos_dir / logo_name)
                logo_found = logo_name
            # Heurística: réguas são horizontais largas com aspect > 3:1 E geralmente pequenas
            w, h = im.get("w", 0), im.get("h", 0)
            if w > 0 and h > 0 and w / max(h, 1) >= 3 and w >= 800 and size < 200_000:
                import shutil
                regua_name = f"{slug}_regua_{len(reguas_found)}.{ext.lstrip('.')}"
                shutil.copy(dest, reguas_dir / regua_name)
                reguas_found.append(regua_name)

    result = {
        "source_url": url,
        "slug": slug,
        "title": scraped["title"],
        "h1": scraped["h1"],
        "h2": scraped["h2"],
        "h3": scraped["h3"],
        "paragraphs": scraped["paragraphs"],
        "sections": scraped["sections"][:20],
        "external_links": scraped["links"],
        "images": downloaded,
        "logo_detected": logo_found,
        "reguas_detected": reguas_found,
    }
    (out_dir / "scrape.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    return result


async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", required=True)
    ap.add_argument("--slug", required=True, help="Slug snake_case do projeto (ex: cultura_robotica_ferroporte)")
    ap.add_argument("--out-root", default="assets/projetos", help="Raiz (padrão: assets/projetos)")
    ap.add_argument("--folder-name", required=True, help='Nome da pasta (ex: "81. CULTURA ROBÓTICA (FERROPORTE)")')
    args = ap.parse_args()

    out_dir = ROOT / args.out_root / args.folder_name
    print(f"Output dir: {out_dir}", file=sys.stderr)
    result = await scrape(args.url, out_dir, args.slug)
    print(f"\n✓ {len(result['images'])} images downloaded", file=sys.stderr)
    print(f"  Logo: {result['logo_detected']}", file=sys.stderr)
    print(f"  Reguas: {result['reguas_detected']}", file=sys.stderr)
    print(f"  H1: {result['h1'][:3]}", file=sys.stderr)
    print(f"  Sections: {len(result['sections'])}", file=sys.stderr)
    print(json.dumps({"slug": args.slug, "folder": str(out_dir), "n_images": len(result["images"]), "logo": result["logo_detected"]}))


if __name__ == "__main__":
    asyncio.run(main())
