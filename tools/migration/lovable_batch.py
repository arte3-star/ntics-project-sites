#!/usr/bin/env python3
"""
lovable_batch.py — Cria, renomeia e publica múltiplos projetos no Lovable via Playwright CDP.

Pré-requisito: Chrome aberto com porta 9222 debug e logado no Lovable.

Uso:
  python tools/migration/lovable_batch.py --only 86  # só um projeto
  python tools/migration/lovable_batch.py             # todos os pendentes

Cada projeto:
  1. Nova aba pra dashboard folder URL
  2. Criar projeto com prompt focado
  3. Aguardar geração + allow popups
  4. Rename para nome correto
  5. Publish com subdomain customizado
  6. Retornar URL pública
"""

import argparse
import asyncio
import json
import sys
from pathlib import Path

from playwright.async_api import async_playwright

FOLDER_URL = 'https://lovable.dev/dashboard?folderId=fold_01kjt0cdwdf8v8w7ywhntmsmz4'
GITHUB_BASE = 'https://raw.githubusercontent.com/arte3-star/ntics-project-sites/master/'


def build_prompt(site: dict) -> str:
    base = f'{GITHUB_BASE}{site["github_slug"]}/'
    return (
        f'Crie uma landing page React + Tailwind do projeto NTICS "{site["nome_projeto"].title()}" '
        f'({site["patrocinador"] or "sem patrocinador"}) copiando EXATAMENTE este HTML estático:\n'
        f'{base}index.html\n\n'
        f'Use as imagens do mesmo repositório: logo em {base}LOGOS/, '
        f'fotos em {base}FOTOS/, régua em {base}REGUAS/. '
        f'Mantenha textos em português EXATAMENTE como estão no HTML. '
        f'Paleta: azul #1E3A8A + azul-escuro #0F1F4D + magenta #E91E63. Fonte: Poppins. '
        f'Estrutura: Header sticky, Hero 80vh com logo + título, Sobre, seções, '
        f'Galeria grid 3x3, Footer com régua. '
        f'IMPORTANTE: Use Tailwind via classes inline. NÃO use @apply dentro de pseudo-elementos (::before/::after) '
        f'porque o PostCSS não processa bem. Se precisar de gradientes ou overlays, use CSS puro inline. '
        f'Não invente conteúdo novo. Não substitua imagens.'
    )


async def wait_for(page, cond_fn, timeout=120, interval=3):
    """Espera até cond_fn retornar truthy ou timeout."""
    elapsed = 0
    while elapsed < timeout:
        result = await cond_fn()
        if result:
            return result
        await asyncio.sleep(interval)
        elapsed += interval
    return None


async def click_allow_popups(page, iterations=3):
    """Clica em 'Allow' se aparecer popup de permissão."""
    for _ in range(iterations):
        clicked = await page.evaluate(
            '() => { const b = Array.from(document.querySelectorAll("button")).find(x => x.textContent.trim() === "Allow"); if (b) { b.click(); return true; } return false; }'
        )
        if clicked:
            print('    [allow]', flush=True)
            await asyncio.sleep(3)
        else:
            break


async def create_project(page, prompt: str) -> str | None:
    """Cria projeto novo com o prompt. Retorna project URL."""
    # URL já abre direto a tela de criação (TipTap editor) no contexto da pasta
    await page.goto(FOLDER_URL, wait_until='domcontentloaded', timeout=30000)
    await asyncio.sleep(6)

    # Aceita cookies se aparecer
    await page.evaluate(
        '() => { const b = Array.from(document.querySelectorAll("button")).find(x => x.textContent.trim() === "OK"); if (b) b.click(); }'
    )
    await asyncio.sleep(1)

    # Localiza o editor TipTap (já está visível)
    editor = page.locator('div.tiptap.ProseMirror').first
    try:
        await editor.click(timeout=20000)
    except Exception as e:
        print(f'    [ERR] click editor: {e}', flush=True)
        return None
    await asyncio.sleep(0.5)
    await page.keyboard.insert_text(prompt)
    await asyncio.sleep(1)
    await page.keyboard.press('Control+Enter')
    print('    [submitted]', flush=True)
    await asyncio.sleep(5)

    # Wait for project URL
    project_url = None
    for _ in range(12):
        if '/projects/' in page.url:
            project_url = page.url
            break
        await asyncio.sleep(2)
    return project_url


async def wait_for_generation(page, max_wait=240):
    """Aguarda Lovable terminar generation, clicando Allow quando necessário."""
    elapsed = 0
    while elapsed < max_wait:
        await click_allow_popups(page, 2)
        # Check se existe iframe de preview com URL válida
        has_preview = await page.evaluate(
            '() => { const iframe = document.querySelector("iframe"); return iframe && iframe.src && iframe.src.includes("lovableproject.com"); }'
        )
        # Check status "Deploying"
        status_done = await page.evaluate(
            '() => { const txt = document.body.innerText; return txt.includes("Deploying final layout updates") || txt.includes("Edited") && !txt.includes("Building"); }'
        )
        if has_preview and status_done:
            return True
        await asyncio.sleep(5)
        elapsed += 5
    return False


async def rename_project(page, new_name: str) -> bool:
    """Vai em settings, renomeia, volta."""
    current = page.url
    settings_url = current.split('?')[0].rstrip('/') + '/settings'
    await page.goto(settings_url, wait_until='domcontentloaded', timeout=30000)
    await asyncio.sleep(3)

    clicked = await page.evaluate(
        '() => { const b = Array.from(document.querySelectorAll("button")).find(x => x.textContent.trim() === "Rename"); if (b) { b.click(); return true; } return false; }'
    )
    if not clicked:
        print('    [ERR] Rename button not found', flush=True)
        return False
    await asyncio.sleep(1.5)

    inp = page.locator('input[name="displayName"]').first
    await inp.click()
    await inp.fill(new_name)
    await asyncio.sleep(0.5)

    saved = await page.evaluate(
        '() => { const dlg = document.querySelector("[role=dialog]"); if (!dlg) return false; const btns = Array.from(dlg.querySelectorAll("button")); const save = btns.find(b => b.textContent.trim() === "Save"); if (save) { save.click(); return true; } return false; }'
    )
    await asyncio.sleep(2)
    return saved


async def publish_project(page, subdomain: str) -> str | None:
    """Publica projeto com subdomain customizado. Retorna URL."""
    # Volta para main page do projeto
    current = page.url
    main_url = current.split('/settings')[0]
    await page.goto(main_url, wait_until='domcontentloaded', timeout=30000)
    await asyncio.sleep(3)

    # Click Publish (canto superior direito) com retry
    published_opened = False
    for attempt in range(3):
        try:
            await page.locator('button[aria-label="Publish"]').first.click(timeout=15000)
            await asyncio.sleep(2.5)
            # Verifica se o popover abriu
            popup = await page.evaluate(
                '() => Array.from(document.querySelectorAll("[data-radix-popper-content-wrapper], [role=menu]")).some(w => w.offsetParent && w.textContent.includes("Your website URL"))'
            )
            if popup:
                published_opened = True
                break
            print(f'    [publish retry {attempt+1}] popover not opened', flush=True)
            await asyncio.sleep(3)
        except Exception as e:
            print(f'    [publish click attempt {attempt+1}]: {e}', flush=True)
            await asyncio.sleep(5)

    if not published_opened:
        print(f'    [ERR] Publish popover did not open after retries', flush=True)
        return None

    # Edit subdomain input
    try:
        inputs = await page.evaluate(
            '() => Array.from(document.querySelectorAll("input")).filter(i => i.offsetParent !== null && i.type === "text" && i.value && !i.value.includes("/")).map(i => i.value)'
        )
    except Exception:
        inputs = []

    # Localiza o input editável do subdomain — pode precisar clicar num pencil button primeiro
    # Vamos tentar clicar no botão que contém ".lovable.app"
    await page.evaluate(
        '() => { const wrappers = Array.from(document.querySelectorAll("[data-radix-popper-content-wrapper], [role=menu]")); for (const w of wrappers) { const btns = Array.from(w.querySelectorAll("button")); for (const b of btns) { if (b.textContent.includes(".lovable.app")) { b.click(); return; } } } }'
    )
    await asyncio.sleep(1)

    # Procura input com valor não-vazio no popover
    try:
        # Seleciona o primeiro input text visível que NÃO seja o path "/"
        all_inputs = await page.query_selector_all('input[type="text"]')
        target_input = None
        for inp in all_inputs:
            val = await inp.input_value()
            visible = await inp.is_visible()
            if visible and val and val != '/' and '.app' not in val:
                target_input = inp
                break
        if target_input:
            await target_input.click()
            await page.keyboard.press('Control+a')
            await page.keyboard.press('Delete')
            await page.keyboard.type(subdomain)
            await asyncio.sleep(0.5)
            await page.keyboard.press('Enter')
            await asyncio.sleep(1)
    except Exception as e:
        print(f'    [WARN] Subdomain edit: {e}', flush=True)

    # Click sequentially: Continue → Public → Continue → Continue → Publish
    for step in range(5):
        await asyncio.sleep(1.5)
        clicked = await page.evaluate(
            '() => { const wrappers = Array.from(document.querySelectorAll("[data-radix-popper-content-wrapper], [role=menu]")); for (const w of wrappers) { if (!w.offsetParent) continue; const btns = Array.from(w.querySelectorAll("button")); const c = btns.find(b => (b.textContent.trim() === "Continue" || b.textContent.trim() === "Publish") && !b.disabled); if (c) { c.click(); return c.textContent.trim(); } } return null; }'
        )
        print(f'    [publish step {step+1}] {clicked}', flush=True)
        if clicked == 'Publish':
            await asyncio.sleep(15)
            break

    # Verify URL is live
    import urllib.request, ssl
    ctx = ssl.create_default_context(); ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
    url = f'https://{subdomain}.lovable.app/'
    for attempt in range(4):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            r = urllib.request.urlopen(req, context=ctx, timeout=10)
            if r.status == 200:
                return url
        except Exception as e:
            print(f'    [live check {attempt+1}] {e}', flush=True)
            await asyncio.sleep(8)
    return None


async def process_site(browser, ctx, site: dict) -> dict:
    """Processa um site do começo ao fim."""
    page = await ctx.new_page()
    result = {'site': site['nome_planilha'], 'url': None, 'project_id': None, 'error': None}

    try:
        prompt = build_prompt(site)
        print(f'\n--- {site["numero_ntics"]} {site["nome_projeto"]} ---', flush=True)
        project_url = await create_project(page, prompt)
        if not project_url:
            result['error'] = 'Failed to create project'
            return result

        result['project_id'] = project_url.split('/projects/')[-1]
        print(f'  Project created: {result["project_id"]}', flush=True)

        print('  Waiting generation...', flush=True)
        await wait_for_generation(page, max_wait=180)

        print('  Renaming...', flush=True)
        await rename_project(page, site['lovable_name'])

        print('  Publishing...', flush=True)
        url = await publish_project(page, site['subdomain'])
        result['url'] = url
        if url:
            print(f'  OK LIVE: {url}', flush=True)
        else:
            result['error'] = 'Publish failed or URL not live'
            print(f'  ERR ERR publish', flush=True)
    except Exception as e:
        result['error'] = f'{type(e).__name__}: {e}'
        print(f'  EXCEPTION: {result["error"]}', flush=True)
    finally:
        # NÃO fecha a page — mantém para eventual retry/inspeção
        await asyncio.sleep(2)
    return result


async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--only', type=int, default=None, help='Processar só um número NTICS')
    ap.add_argument('--skip', type=str, default='', help='Lista de números separada por vírgula')
    args = ap.parse_args()

    sites = json.loads(Path('tools/migration/sites_pendentes.json').read_text(encoding='utf-8'))
    skip_nums = {int(x) for x in args.skip.split(',') if x.strip().isdigit()}
    if args.only:
        sites = [s for s in sites if s['numero_ntics'] == args.only]
    else:
        sites = [s for s in sites if s['numero_ntics'] not in skip_nums]

    print(f'Processing {len(sites)} sites...', flush=True)
    results = []
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp('http://localhost:9222')
        ctx = browser.contexts[0]
        for site in sites:
            result = await process_site(browser, ctx, site)
            results.append(result)
            # Save results incrementally
            Path('.tmp/migration/lovable_batch_results.json').write_text(
                json.dumps(results, indent=2, ensure_ascii=False), encoding='utf-8'
            )

    # Summary
    print('\n=== SUMMARY ===', flush=True)
    ok = sum(1 for r in results if r['url'])
    print(f'Published: {ok}/{len(results)}', flush=True)
    for r in results:
        status = 'OK' if r['url'] else 'ERR'
        print(f'  {status} {r["site"]}: {r.get("url") or r.get("error")}', flush=True)


if __name__ == '__main__':
    asyncio.run(main())
