#!/usr/bin/env python3
"""
lovable_screenshot_full.py — Captura full-page screenshot do preview iframe.

Para cada projeto, abre a URL .lovableproject.com diretamente em uma nova aba
e tira screenshot full_page.
"""

import asyncio
import io
import json
import sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from playwright.async_api import async_playwright


async def main():
    projects = json.loads(Path('.tmp/migration/fix_inputs.json').read_text(encoding='utf-8'))
    review = json.loads(Path('.tmp/migration/final_review.json').read_text(encoding='utf-8'))
    iframe_urls = {r['numero']: r.get('iframe', {}).get('src') for r in review if r.get('iframe')}

    async with async_playwright() as p:
        b = await p.chromium.connect_over_cdp('http://localhost:9222')
        ctx = b.contexts[0]
        page = await ctx.new_page()

        for proj in projects:
            num = proj['numero']
            url = iframe_urls.get(num)
            if not url:
                # fallback: revisit lovable project to get fresh iframe
                print(f'  {num}: no iframe URL, skipping', flush=True)
                continue
            print(f'\n--- {num} {proj["name"][:35]} ---', flush=True)
            try:
                await page.goto(url, wait_until='domcontentloaded', timeout=30000)
                await asyncio.sleep(5)
                await page.screenshot(path=f'.tmp/migration/preview-{num}.png', full_page=True)
                print(f'    saved preview-{num}.png', flush=True)
            except Exception as e:
                print(f'    ERR: {e}', flush=True)

        await page.close()


if __name__ == '__main__':
    asyncio.run(main())
