#!/usr/bin/env python3
"""
find_reguas.py — Navega para cada site RF via CDP e baixa as réguas do footer.

Estratégia: baixa TODAS as imagens do site RF, verifica aspect ratio com PIL,
e salva as que são landscape amplo (ratio >= 2.5) como régua.
"""

import asyncio
import io
import json
import os
import re
import ssl
import sys
import urllib.request
from pathlib import Path
from urllib.parse import urlparse

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from PIL import Image
from playwright.async_api import async_playwright

ROOT = Path(__file__).resolve().parents[2]
UA = "Mozilla/5.0"
_ssl = ssl.create_default_context()
_ssl.check_hostname = False
_ssl.verify_mode = ssl.CERT_NONE


def download_img(url, dest, referer):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA, "Referer": referer})
        data = urllib.request.urlopen(req, context=_ssl, timeout=25).read()
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
        return True
    except Exception as e:
        print(f"    DL ERR: {e}")
        return False


def check_is_regua(path: Path) -> bool:
    """Abre, verifica ratio, fecha. Retorna True se parece régua."""
    try:
        with Image.open(path) as img:
            w, h = img.size
        ratio = w / max(h, 1)
        return ratio >= 2.5 and w > 400
    except Exception:
        return False


async def main():
    sites = json.loads((ROOT / 'tools/migration/sites_pendentes.json').read_text(encoding='utf-8'))

    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp('http://localhost:9222')
        ctx = browser.contexts[0]
        page = ctx.pages[0]

        for s in sites:
            num = s['numero_ntics']
            rf_url = s['rf_url']
            folder = None
            for d in os.listdir(ROOT / 'assets' / 'projetos'):
                if d.startswith(f'{num}. '):
                    folder = d
                    break
            if not folder:
                continue

            reguas_dir = ROOT / 'assets' / 'projetos' / folder / 'REGUAS'
            reguas_dir.mkdir(parents=True, exist_ok=True)

            # Check if already has a real regua
            existing = [f for f in reguas_dir.iterdir()
                        if f.name != 'desktop.ini' and f.suffix.lower() in ('.jpg', '.jpeg', '.png', '.webp')]
            if existing:
                print(f"{num}: already has {len(existing)} reguas")
                continue

            print(f"\n=== {num} {s['nome_planilha'][:35]} ===")

            await page.goto(rf_url, wait_until='domcontentloaded', timeout=60000)
            await asyncio.sleep(5)
            # Scroll
            for _ in range(5):
                await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
                await asyncio.sleep(1.5)

            # ALL image URLs
            all_urls = await page.evaluate(r'''() => {
                const urls = new Set();
                document.querySelectorAll('img').forEach(i => {
                    if (i.src && !i.src.startsWith('data:') && !i.src.includes('rfstat'))
                        urls.add(i.src);
                });
                document.querySelectorAll('*').forEach(el => {
                    const bg = window.getComputedStyle(el).backgroundImage;
                    if (bg && bg !== 'none' && bg.includes('url(')) {
                        const m = bg.match(/url\(["']?([^"')]+)["']?\)/);
                        if (m && !m[1].startsWith('data:') && !m[1].includes('rfstat'))
                            urls.add(m[1]);
                    }
                });
                return [...urls];
            }''')

            print(f"  {len(all_urls)} unique image URLs")

            # Download each, check if regua
            found = 0
            for url in all_urls:
                name = urlparse(url).path.split('/')[-1]
                tmp = reguas_dir / f"_check_{name}"
                if not download_img(url, tmp, rf_url):
                    continue
                if check_is_regua(tmp):
                    final = reguas_dir / f"regua_{name}"
                    tmp.rename(final)
                    found += 1
                    with Image.open(final) as im:
                        print(f"    REGUA: {final.name} ({im.size[0]}x{im.size[1]})")
                else:
                    try:
                        tmp.unlink()
                    except Exception:
                        pass

            print(f"  Found {found} reguas")

    print("\nDone.")


if __name__ == '__main__':
    asyncio.run(main())
