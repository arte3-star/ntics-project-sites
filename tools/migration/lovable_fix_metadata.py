#!/usr/bin/env python3
"""
lovable_fix_metadata.py — Manda 1 prompt de correção para cada projeto Lovable.

Corrige:
- <title> e <meta description> (para o Publish dialog não cair em "Lovable Generated Project")
- h1 principal
- Galeria: remove duplicatas e logo
- Aspect ratio das imagens

Uso: python tools/migration/lovable_fix_metadata.py [--only NUMERO]
"""

import argparse
import asyncio
import io
import json
import sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from playwright.async_api import async_playwright


def build_prompt(p: dict) -> str:
    return f"""Faça estas correções no site (uma única edição, não pergunte nada antes):

1. No <head> do index.html, defina:
   <title>{p['page_title']}</title>
   <meta name="description" content="{p['description']}">

2. O h1 principal do hero deve ser EXATAMENTE: "{p['h1']}"

3. Galeria de fotos:
   - Remova fotos duplicadas (cada imagem deve aparecer 1 única vez)
   - NÃO inclua nenhum arquivo da pasta LOGOS/ na galeria
   - NÃO inclua nenhum arquivo cujo nome contenha "logo"
   - Use apenas fotos da pasta FOTOS/

4. Imagens horizontais devem ficar em containers horizontais com object-cover, sem distorcer.

5. NÃO altere cores, estrutura ou conteúdo de texto. Apenas o que está acima."""


async def click_allow_popups(page, iterations=3):
    for _ in range(iterations):
        clicked = await page.evaluate(
            '() => { const b = Array.from(document.querySelectorAll("button")).find(x => x.textContent.trim() === "Allow"); if (b) { b.click(); return true; } return false; }'
        )
        if clicked:
            print('    [allow popup]', flush=True)
            await asyncio.sleep(2)
        else:
            break


async def wait_for_idle(page, max_wait=180):
    """Espera Lovable terminar de gerar (sem 'Building' / 'Working')."""
    elapsed = 0
    while elapsed < max_wait:
        await click_allow_popups(page, 2)
        busy = await page.evaluate(
            '() => { const t = document.body.innerText; return t.includes("Building") || t.includes("Working") || t.includes("Generating") || t.includes("Editing"); }'
        )
        if not busy:
            await asyncio.sleep(3)
            busy2 = await page.evaluate(
                '() => { const t = document.body.innerText; return t.includes("Building") || t.includes("Working") || t.includes("Generating") || t.includes("Editing"); }'
            )
            if not busy2:
                return True
        await asyncio.sleep(5)
        elapsed += 5
    return False


async def fix_project(page, p: dict) -> dict:
    res = {'numero': p['numero'], 'pid': p['pid'], 'submitted': False, 'error': None}
    print(f"\n--- {p['numero']} {p['name'][:40]} ({p['pid'][:8]}) ---", flush=True)
    try:
        await page.goto(f"https://lovable.dev/projects/{p['pid']}", wait_until='domcontentloaded', timeout=30000)
        await asyncio.sleep(7)
        await page.bring_to_front()
        await page.keyboard.press('Escape')
        await asyncio.sleep(1)

        # Click in the TipTap editor (chat input)
        editor = page.locator('div.tiptap.ProseMirror').first
        try:
            await editor.click(timeout=15000)
        except Exception as e:
            res['error'] = f'editor click: {e}'
            print(f'    ERR editor: {e}', flush=True)
            return res
        await asyncio.sleep(0.5)

        prompt = build_prompt(p)
        await page.keyboard.insert_text(prompt)
        await asyncio.sleep(1)
        await page.keyboard.press('Control+Enter')
        res['submitted'] = True
        print('    [submitted]', flush=True)

        # Wait for generation to complete
        await asyncio.sleep(8)
        idle = await wait_for_idle(page, max_wait=240)
        res['idle'] = idle
        print(f'    [idle: {idle}]', flush=True)

    except Exception as e:
        res['error'] = f'{type(e).__name__}: {e}'
        print(f'    EXCEPTION: {res["error"]}', flush=True)
    return res


async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--only', type=int, default=None)
    ap.add_argument('--skip', type=str, default='', help='Comma-separated numeros to skip')
    args = ap.parse_args()

    projects = json.loads(Path('.tmp/migration/fix_inputs.json').read_text(encoding='utf-8'))
    if args.only:
        projects = [p for p in projects if p['numero'] == args.only]
    skip = {int(x) for x in args.skip.split(',') if x.strip().isdigit()}
    if skip:
        projects = [p for p in projects if p['numero'] not in skip]

    print(f'Fixing {len(projects)} projects...', flush=True)
    results = []
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp('http://localhost:9222')
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else await ctx.new_page()

        for proj in projects:
            r = await fix_project(page, proj)
            results.append(r)
            Path('.tmp/migration/fix_metadata_results.json').write_text(
                json.dumps(results, indent=2, ensure_ascii=False), encoding='utf-8'
            )

    print('\n=== SUMMARY ===', flush=True)
    for r in results:
        st = 'OK ' if r.get('submitted') and r.get('idle') else 'PARTIAL' if r.get('submitted') else 'ERR'
        print(f'  {st} {r["numero"]}: {r.get("error") or "submitted"}', flush=True)


if __name__ == '__main__':
    asyncio.run(main())
