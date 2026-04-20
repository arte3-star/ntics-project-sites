#!/usr/bin/env python3
"""
lovable_redo_one.py — Envia prompt para Lovable refazer projeto a partir do HTML no GitHub.

Para cada projeto, manda um prompt claro pedindo para apagar tudo e reconstruir
baseado no index.html do repositório GitHub.

Uso:
  python tools/migration/lovable_redo_one.py --only 87
  python tools/migration/lovable_redo_one.py           # todos os 9
"""

import argparse
import asyncio
import io
import json
import sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from playwright.async_api import async_playwright

ROOT = Path(__file__).resolve().parents[2]
GITHUB_BASE = 'https://raw.githubusercontent.com/arte3-star/ntics-project-sites/master/'


def build_prompt(site: dict) -> str:
    slug = site['github_slug']
    base = f'{GITHUB_BASE}{slug}/'
    html_url = f'{base}index.html'

    return (
        f'REFAÇA COMPLETAMENTE este projeto. Apague todo o código existente e reconstrua do zero.\n\n'
        f'Copie EXATAMENTE o HTML desta URL:\n{html_url}\n\n'
        f'Este HTML já contém:\n'
        f'- Estrutura completa: header sticky, hero 80vh, seção Sobre, seções temáticas, galeria, footer\n'
        f'- Cores CSS inline específicas deste projeto (NÃO mude as cores)\n'
        f'- Todas as imagens referenciando URLs do GitHub\n'
        f'- Régua de patrocinadores no footer\n'
        f'- Logo do projeto no header e na seção Sobre\n\n'
        f'Regras:\n'
        f'1. Recrie o HTML tal como está — mesmas cores, mesma estrutura, mesmas imagens\n'
        f'2. Use React + Tailwind (padrão Lovable)\n'
        f'3. As imagens estão em:\n'
        f'   - Fotos: {base}FOTOS/\n'
        f'   - Logo: {base}LOGOS/\n'
        f'   - Régua: {base}REGUAS/\n'
        f'4. NÃO invente conteúdo. NÃO mude cores. NÃO substitua imagens.\n'
        f'5. O <title> deve ser: {site["lovable_name"]} | NTICS Projetos\n'
        f'6. O <meta description> deve descrever o projeto em português\n\n'
        f'Comece imediatamente, sem perguntar nada.'
    )


async def click_allow(page):
    for _ in range(3):
        clicked = await page.evaluate(
            '() => { const b = Array.from(document.querySelectorAll("button")).find(x => x.textContent.trim() === "Allow"); if (b) { b.click(); return true; } return false; }'
        )
        if clicked:
            await asyncio.sleep(2)
        else:
            break


async def wait_idle(page, max_wait=300):
    elapsed = 0
    while elapsed < max_wait:
        await click_allow(page)
        busy = await page.evaluate(
            '() => { const t = document.body.innerText; return t.includes("Building") || t.includes("Working") || t.includes("Generating") || t.includes("Editing") || t.includes("Thinking"); }'
        )
        if not busy:
            await asyncio.sleep(4)
            busy2 = await page.evaluate(
                '() => { const t = document.body.innerText; return t.includes("Building") || t.includes("Working") || t.includes("Generating") || t.includes("Editing") || t.includes("Thinking"); }'
            )
            if not busy2:
                return True
        await asyncio.sleep(5)
        elapsed += 5
    return False


async def redo_one(page, site: dict, pid: str) -> dict:
    res = {'numero': site['numero_ntics'], 'pid': pid, 'submitted': False, 'idle': False, 'error': None}
    num = site['numero_ntics']
    print(f"\n--- {num} {site['nome_planilha'][:35]} ({pid[:8]}) ---", flush=True)

    try:
        await page.goto(f'https://lovable.dev/projects/{pid}', wait_until='domcontentloaded', timeout=30000)
        await asyncio.sleep(8)
        await page.bring_to_front()
        await page.keyboard.press('Escape')
        await asyncio.sleep(1)

        # Click editor
        editor = page.locator('div.tiptap.ProseMirror').first
        try:
            await editor.click(timeout=15000)
        except Exception as e:
            res['error'] = f'editor click: {e}'
            print(f'    ERR editor: {e}', flush=True)
            return res
        await asyncio.sleep(0.5)

        prompt = build_prompt(site)
        await page.keyboard.insert_text(prompt)
        await asyncio.sleep(1)
        await page.keyboard.press('Control+Enter')
        res['submitted'] = True
        print('    [submitted]', flush=True)

        # Wait
        await asyncio.sleep(10)
        idle = await wait_idle(page, max_wait=300)
        res['idle'] = idle
        print(f'    [idle: {idle}]', flush=True)

        # Check for build error
        build_err = await page.evaluate(
            '() => document.body.innerText.includes("Build unsuccessful")'
        )
        if build_err:
            print('    [BUILD FAILED - clicking Try to fix]', flush=True)
            clicked = await page.evaluate(
                '() => { const b = Array.from(document.querySelectorAll("button")).find(x => x.textContent.trim() === "Try to fix"); if (b) { b.click(); return true; } return false; }'
            )
            if clicked:
                await asyncio.sleep(10)
                await wait_idle(page, max_wait=240)
            res['build_error'] = True

    except Exception as e:
        res['error'] = f'{type(e).__name__}: {e}'
        print(f'    EXCEPTION: {res["error"]}', flush=True)

    return res


async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--only', type=int, default=None)
    args = ap.parse_args()

    sites = json.loads((ROOT / 'tools/migration/sites_pendentes.json').read_text(encoding='utf-8'))
    batch = json.loads((ROOT / '.tmp/migration/lovable_batch_results.json').read_text(encoding='utf-8'))
    pid_map = {b['site']: b['project_id'] for b in batch}
    # Add 86 manually
    pid_map['Teatro dos Bons Hábitos'] = 'fed8254b-bbfd-42ad-9b74-9cf6a6a918a7'

    if args.only:
        sites = [s for s in sites if s['numero_ntics'] == args.only]

    print(f'Redo {len(sites)} projects...', flush=True)
    results = []

    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp('http://localhost:9222')
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else await ctx.new_page()

        for site in sites:
            pid = pid_map.get(site['nome_planilha'])
            if not pid:
                print(f"  SKIP {site['numero_ntics']}: no project_id found")
                continue
            r = await redo_one(page, site, pid)
            results.append(r)
            (ROOT / '.tmp/migration/lovable_redo_results.json').write_text(
                json.dumps(results, indent=2, ensure_ascii=False), encoding='utf-8'
            )

    print('\n=== SUMMARY ===', flush=True)
    for r in results:
        st = 'OK ' if r.get('submitted') and r.get('idle') and not r.get('build_error') else 'WARN' if r.get('submitted') else 'ERR'
        print(f'  {st} {r["numero"]}: {r.get("error") or "submitted"}', flush=True)


if __name__ == '__main__':
    asyncio.run(main())
