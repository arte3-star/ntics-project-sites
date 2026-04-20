#!/usr/bin/env python3
"""
lovable_fix_final.py — Correção final: democratização + dedup + logo header.

Para cada projeto envia 1 prompt corrigindo:
- Seção "Democratização de Acesso" com texto do RF
- Dedup de imagens (cada foto 1x apenas)
- Logo no header (projeto 89)
- Seção de vídeo com título "ASSISTA O VÍDEO" (placeholder para vídeo futuro)
"""

import asyncio
import io
import json
import os
import sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from playwright.async_api import async_playwright

ROOT = Path(__file__).resolve().parents[2]


def build_fix_prompt(site: dict, scrape: dict) -> str:
    num = site['numero_ntics']

    # Get democratização text
    demo_text = ''
    for p in scrape.get('paragraphs', []):
        if 'democra' in p.lower():
            demo_text = p
            break

    # Get video h2s from RF
    video_h2s = [h for h in scrape.get('h2', [])
                 if 'vídeo' in h.lower() or 'video' in h.lower() or 'assista' in h.lower()]

    parts = []
    parts.append("Correções finais obrigatórias (faça tudo sem perguntar):\n")

    # 1. Democratização
    if demo_text:
        parts.append(f'1. ADICIONE uma seção "DEMOCRATIZAÇÃO DE ACESSO" antes da Galeria de Fotos.')
        parts.append(f'   Texto: "{demo_text[:300]}"')
        parts.append('')

    # 2. Video sections
    if video_h2s:
        parts.append(f'2. ADICIONE seções de vídeo após a seção de Democratização:')
        for vh in video_h2s:
            parts.append(f'   - Seção com título "{vh}" e um placeholder de vídeo (ícone play + texto "Vídeo em breve")')
        parts.append('')

    # 3. Dedup
    parts.append('3. REMOVA imagens duplicadas — cada foto deve aparecer APENAS 1 vez em toda a página.')
    parts.append('   Se uma foto está no hero ou numa seção temática, NÃO repita na galeria.')
    parts.append('')

    # 4. Logo header (especially 89)
    parts.append('4. Garanta que o LOGO do projeto aparece:')
    parts.append('   - No header (canto superior esquerdo)')
    parts.append('   - No hero (centralizado)')
    parts.append('   - Na seção Sobre o Projeto')
    parts.append('   E NUNCA na galeria de fotos.')
    parts.append('')

    # 5. Régua
    parts.append('5. A RÉGUA de patrocinadores deve estar APENAS no footer, nunca na galeria.')

    return '\n'.join(parts)


async def click_allow(page):
    for _ in range(3):
        c = await page.evaluate(
            '() => { const b = Array.from(document.querySelectorAll("button")).find(x => x.textContent.trim() === "Allow"); if (b) { b.click(); return true; } return false; }'
        )
        if c:
            await asyncio.sleep(2)
        else:
            break


async def wait_idle(page, max_wait=300):
    elapsed = 0
    while elapsed < max_wait:
        await click_allow(page)
        busy = await page.evaluate(
            '() => { const t = document.body.innerText; return t.includes("Building") || t.includes("Working") || t.includes("Editing") || t.includes("Generating") || t.includes("Thinking"); }'
        )
        if not busy:
            await asyncio.sleep(3)
            busy2 = await page.evaluate(
                '() => { const t = document.body.innerText; return t.includes("Building") || t.includes("Working") || t.includes("Editing"); }'
            )
            if not busy2:
                return True
        await asyncio.sleep(5)
        elapsed += 5
    return False


async def main():
    sites = json.loads((ROOT / 'tools/migration/sites_pendentes.json').read_text(encoding='utf-8'))
    batch = json.loads((ROOT / '.tmp/migration/lovable_batch_results.json').read_text(encoding='utf-8'))
    pid_map = {b['site']: b['project_id'] for b in batch}
    pid_map['Teatro dos Bons Hábitos'] = 'fed8254b-bbfd-42ad-9b74-9cf6a6a918a7'

    results = []
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp('http://localhost:9222')
        ctx = browser.contexts[0]
        page = ctx.pages[0]

        for site in sites:
            pid = pid_map.get(site['nome_planilha'])
            if not pid:
                continue
            num = site['numero_ntics']

            # Load scrape
            folder = None
            for d in os.listdir(ROOT / 'assets' / 'projetos'):
                if d.startswith(f'{num}. '):
                    folder = d
                    break
            scrape = {}
            if folder:
                sp = ROOT / 'assets' / 'projetos' / folder / 'scrape.json'
                if sp.exists():
                    scrape = json.loads(sp.read_text(encoding='utf-8'))

            print(f"\n--- {num} {site['nome_planilha'][:35]} ---", flush=True)

            await page.goto(f'https://lovable.dev/projects/{pid}', wait_until='domcontentloaded', timeout=30000)
            await asyncio.sleep(8)
            await page.bring_to_front()
            await page.keyboard.press('Escape')
            await asyncio.sleep(1)

            # Check build error
            build_err = await page.evaluate('() => document.body.innerText.includes("Build unsuccessful")')
            if build_err:
                print('    [BUILD FAILED - Try to fix]', flush=True)
                await page.evaluate(
                    '() => { const b = Array.from(document.querySelectorAll("button")).find(x => x.textContent.trim() === "Try to fix"); if (b) { b.click(); return true; } return false; }'
                )
                await asyncio.sleep(10)
                await wait_idle(page, max_wait=240)

            editor = page.locator('div.tiptap.ProseMirror').first
            try:
                await editor.click(timeout=15000)
            except Exception as e:
                print(f'    ERR editor: {e}', flush=True)
                results.append({'numero': num, 'error': str(e)})
                continue

            await asyncio.sleep(0.5)
            prompt = build_fix_prompt(site, scrape)
            await page.keyboard.insert_text(prompt)
            await asyncio.sleep(1)
            await page.keyboard.press('Control+Enter')
            print('    [submitted]', flush=True)

            await asyncio.sleep(10)
            idle = await wait_idle(page, max_wait=300)
            print(f'    [idle: {idle}]', flush=True)
            results.append({'numero': num, 'submitted': True, 'idle': idle})

    (ROOT / '.tmp/migration/fix_final_results.json').write_text(
        json.dumps(results, indent=2, ensure_ascii=False), encoding='utf-8'
    )
    print('\n=== SUMMARY ===', flush=True)
    for r in results:
        st = 'OK' if r.get('idle') else 'WARN'
        print(f'  {st} {r.get("numero")}: {r.get("error", "submitted")}', flush=True)


if __name__ == '__main__':
    asyncio.run(main())
