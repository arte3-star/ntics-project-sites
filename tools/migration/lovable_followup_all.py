#!/usr/bin/env python3
"""
lovable_followup_all.py — Envia follow-up para cada projeto Lovable:
- Corrigir hero com foto real do projeto
- Garantir régua no footer
- Garantir cores corretas (header, seções)
- Logo no hero + Sobre
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
GITHUB_BASE = 'https://raw.githubusercontent.com/arte3-star/ntics-project-sites/master/'


def build_followup(site: dict) -> str:
    slug = site['github_slug']
    base = f'{GITHUB_BASE}{slug}/'

    # Find regua filename
    folder = None
    for d in os.listdir(ROOT / 'assets' / 'projetos'):
        if d.startswith(f"{site['numero_ntics']}. "):
            folder = d
            break
    regua_file = ''
    if folder:
        reguas_dir = ROOT / 'assets' / 'projetos' / folder / 'REGUAS'
        if reguas_dir.exists():
            for f in reguas_dir.iterdir():
                if f.name.startswith('regua_') and f.suffix.lower() in ('.jpg', '.png'):
                    regua_file = f.name
                    break

    # Find logo filename
    logo_file = ''
    if folder:
        logos_dir = ROOT / 'assets' / 'projetos' / folder / 'LOGOS'
        if logos_dir.exists():
            for f in logos_dir.iterdir():
                if f.suffix.lower() == '.png' and f.name != 'desktop.ini':
                    logo_file = f.name
                    break

    # Get colors
    colors = {}
    if folder:
        cores_path = ROOT / 'assets' / 'projetos' / folder / 'cores.json'
        if cores_path.exists():
            colors = json.loads(cores_path.read_text(encoding='utf-8'))

    primary = colors.get('primary', '#1A496C')
    secondary = colors.get('secondary', '#E52A3D')

    return (
        f'Ajustes finais obrigatórios:\n\n'
        f'1. HERO: Use uma foto REAL do projeto no hero (não foto genérica). '
        f'Escolha a primeira foto disponível de: {base}FOTOS/\n\n'
        f'2. RÉGUA DE PATROCINADORES no footer: adicione esta imagem antes do texto de Lei Rouanet:\n'
        f'   {base}REGUAS/{regua_file}\n\n'
        f'3. CORES: o header deve ter background-color {primary}. '
        f'Seções escuras devem usar {colors.get("dark", primary)}. '
        f'Títulos devem alternar entre {primary} e {secondary}.\n\n'
        f'4. LOGO: deve aparecer em:\n'
        f'   - Header (canto superior esquerdo, pequeno)\n'
        f'   - Hero (centralizado, grande, com fundo branco arredondado)\n'
        f'   - Seção "Sobre o Projeto" (lado esquerdo)\n'
        f'   URL: {base}LOGOS/{logo_file}\n\n'
        f'5. GALERIA: NÃO pode conter o logo. Apenas fotos da pasta FOTOS/.\n\n'
        f'6. TITLE: "{site["lovable_name"]} | NTICS Projetos"\n\n'
        f'Faça tudo sem perguntar.'
    )


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
        page = ctx.pages[0] if ctx.pages else await ctx.new_page()

        for site in sites:
            pid = pid_map.get(site['nome_planilha'])
            if not pid:
                continue
            num = site['numero_ntics']
            print(f"\n--- {num} {site['nome_planilha'][:35]} ---", flush=True)

            await page.goto(f'https://lovable.dev/projects/{pid}', wait_until='domcontentloaded', timeout=30000)
            await asyncio.sleep(8)
            await page.bring_to_front()
            await page.keyboard.press('Escape')
            await asyncio.sleep(1)

            # Check for build error first
            build_err = await page.evaluate('() => document.body.innerText.includes("Build unsuccessful")')
            if build_err:
                print('    [BUILD FAILED - Try to fix first]', flush=True)
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
            prompt = build_followup(site)
            await page.keyboard.insert_text(prompt)
            await asyncio.sleep(1)
            await page.keyboard.press('Control+Enter')
            print('    [followup submitted]', flush=True)

            await asyncio.sleep(10)
            idle = await wait_idle(page, max_wait=300)
            print(f'    [idle: {idle}]', flush=True)
            results.append({'numero': num, 'submitted': True, 'idle': idle})

    (ROOT / '.tmp/migration/lovable_followup_results.json').write_text(
        json.dumps(results, indent=2, ensure_ascii=False), encoding='utf-8'
    )
    print('\n=== SUMMARY ===', flush=True)
    for r in results:
        st = 'OK' if r.get('idle') else 'WARN'
        print(f'  {st} {r["numero"]}', flush=True)


if __name__ == '__main__':
    asyncio.run(main())
