#!/usr/bin/env python3
"""
lovable_dedup_gallery.py — Segundo prompt: dedup galeria e logo fora da grid.

Envia 1 prompt focado: cada imagem aparece 1x; logo nunca na galeria.
Para o projeto 89 (build broken), tenta clicar "Try to fix" antes.
"""

import argparse
import asyncio
import io
import json
import sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from playwright.async_api import async_playwright


PROMPT = """Faça uma única correção final no site:

Cada imagem deve aparecer APENAS UMA VEZ na página inteira. Hoje há fotos repetidas — várias fotos que estão no Hero ou em seções temáticas estão também na Galeria. Isso precisa parar.

Regras:
1. A galeria de fotos NÃO pode conter nenhuma imagem que já apareça em outra seção (Hero, Sobre, seções temáticas)
2. A galeria NÃO pode conter nenhum arquivo da pasta LOGOS/ ou cujo nome contenha "logo"
3. O logo do projeto só aparece em: header (canto superior esquerdo) e na seção Sobre — em mais nenhum lugar
4. Use apenas fotos da pasta FOTOS/ na galeria, e cada uma só uma vez
5. Se sobrarem poucas fotos para a galeria após dedup, mostre menos imagens — é melhor 4 únicas do que 9 com repetições

NÃO altere cores, textos, estrutura, h1, title ou meta description. APENAS dedup."""


async def click_try_to_fix(page) -> bool:
    return await page.evaluate(
        '() => { const b = Array.from(document.querySelectorAll("button")).find(x => x.textContent.trim() === "Try to fix"); if (b) { b.click(); return true; } return false; }'
    )


async def click_allow(page):
    for _ in range(2):
        clicked = await page.evaluate(
            '() => { const b = Array.from(document.querySelectorAll("button")).find(x => x.textContent.trim() === "Allow"); if (b) { b.click(); return true; } return false; }'
        )
        if clicked:
            await asyncio.sleep(2)
        else:
            break


async def wait_idle(page, max_wait=240):
    elapsed = 0
    while elapsed < max_wait:
        await click_allow(page)
        busy = await page.evaluate(
            '() => { const t = document.body.innerText; return t.includes("Building") || t.includes("Working") || t.includes("Generating") || t.includes("Editing") || t.includes("Thought for") === false && t.includes("Thinking"); }'
        )
        if not busy:
            await asyncio.sleep(3)
            busy2 = await page.evaluate(
                '() => { const t = document.body.innerText; return t.includes("Building") || t.includes("Working") || t.includes("Generating") || t.includes("Editing") || t.includes("Thinking"); }'
            )
            if not busy2:
                return True
        await asyncio.sleep(5)
        elapsed += 5
    return False


async def fix_one(page, p: dict) -> dict:
    res = {'numero': p['numero'], 'pid': p['pid']}
    print(f"\n--- {p['numero']} {p['name'][:35]} ---", flush=True)
    try:
        await page.goto(f"https://lovable.dev/projects/{p['pid']}", wait_until='domcontentloaded', timeout=30000)
        await asyncio.sleep(8)
        await page.bring_to_front()
        await page.keyboard.press('Escape')
        await asyncio.sleep(1)

        # If project 89 (broken), click "Try to fix" first and wait
        if p['numero'] == 89:
            tried = await click_try_to_fix(page)
            if tried:
                print('    [clicked Try to fix]', flush=True)
                await asyncio.sleep(10)
                await wait_idle(page, max_wait=240)
                # If still broken, send recovery prompt
                still_broken = await page.evaluate(
                    '() => document.body.innerText.includes("Build unsuccessful")'
                )
                if still_broken:
                    print('    [still broken after Try to fix — sending recovery prompt]', flush=True)
                    editor = page.locator('div.tiptap.ProseMirror').first
                    await editor.click(timeout=15000)
                    await asyncio.sleep(0.5)
                    recovery = "O build está falhando. Por favor identifique e corrija o erro de build. Não pergunte nada antes — apenas resolva."
                    await page.keyboard.insert_text(recovery)
                    await asyncio.sleep(1)
                    await page.keyboard.press('Control+Enter')
                    await asyncio.sleep(8)
                    await wait_idle(page, max_wait=240)

        # Click editor
        editor = page.locator('div.tiptap.ProseMirror').first
        try:
            await editor.click(timeout=15000)
        except Exception as e:
            res['error'] = f'editor click: {e}'
            print(f'    ERR editor: {e}', flush=True)
            return res
        await asyncio.sleep(0.5)

        await page.keyboard.insert_text(PROMPT)
        await asyncio.sleep(1)
        await page.keyboard.press('Control+Enter')
        res['submitted'] = True
        print('    [dedup submitted]', flush=True)
        await asyncio.sleep(8)
        idle = await wait_idle(page, max_wait=240)
        res['idle'] = idle
        print(f'    [idle: {idle}]', flush=True)

    except Exception as e:
        res['error'] = f'{type(e).__name__}: {e}'
        print(f'    EXCEPTION: {res["error"]}', flush=True)
    return res


async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--only', type=int, default=None)
    args = ap.parse_args()

    projects = json.loads(Path('.tmp/migration/fix_inputs.json').read_text(encoding='utf-8'))
    if args.only:
        projects = [p for p in projects if p['numero'] == args.only]

    print(f'Dedup pass on {len(projects)} projects...', flush=True)
    results = []
    async with async_playwright() as p:
        b = await p.chromium.connect_over_cdp('http://localhost:9222')
        ctx = b.contexts[0]
        page = ctx.pages[0] if ctx.pages else await ctx.new_page()

        for proj in projects:
            r = await fix_one(page, proj)
            results.append(r)
            Path('.tmp/migration/dedup_results.json').write_text(
                json.dumps(results, indent=2, ensure_ascii=False), encoding='utf-8'
            )

    print('\n=== SUMMARY ===', flush=True)
    for r in results:
        st = 'OK ' if r.get('submitted') and r.get('idle') else 'PARTIAL' if r.get('submitted') else 'ERR'
        print(f'  {st} {r["numero"]}: {r.get("error") or "submitted"}', flush=True)


if __name__ == '__main__':
    asyncio.run(main())
