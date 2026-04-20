#!/usr/bin/env python3
"""
lovable_recover.py — Recupera publish de projetos que falharam no batch.

Para cada project_id em lovable_batch_results.json:
  1. Navega pro projeto
  2. Tenta publish com subdomain correto
  3. Salva URL final

Uso: python tools/migration/lovable_recover.py
"""

import asyncio
import json
import ssl
import sys
import urllib.request
from pathlib import Path

from playwright.async_api import async_playwright


async def publish_one(page, project_id: str, subdomain: str, lovable_name: str) -> str | None:
    # Navega pro projeto (se já não estiver)
    if project_id not in page.url:
        await page.goto(f'https://lovable.dev/projects/{project_id}', wait_until='domcontentloaded', timeout=30000)
        await asyncio.sleep(6)
    await page.bring_to_front()

    # 1. Primeiro fecha qualquer popover existente com Escape
    await page.keyboard.press('Escape')
    await asyncio.sleep(1)

    # 2. Verifica nome — se não for o correto, faz rename
    current_name = await page.evaluate(
        '() => { const btns = Array.from(document.querySelectorAll("button")); const m = btns.find(b => { const r = b.getBoundingClientRect(); return r.y < 30 && r.x < 400 && b.textContent.trim().length > 5; }); return m ? m.textContent.trim() : null; }'
    )
    print(f'  current name: {current_name!r}', flush=True)
    needs_rename = not current_name or not current_name.startswith(lovable_name[:8])
    if needs_rename:
        print(f'  renaming to: {lovable_name}', flush=True)
        await page.goto(f'https://lovable.dev/projects/{project_id}/settings', wait_until='domcontentloaded', timeout=30000)
        await asyncio.sleep(4)
        clicked = await page.evaluate(
            '() => { const b = Array.from(document.querySelectorAll("button")).find(x => x.textContent.trim() === "Rename"); if (b) { b.click(); return true; } return false; }'
        )
        if clicked:
            await asyncio.sleep(1.5)
            try:
                inp = page.locator('input[name="displayName"]').first
                await inp.click(timeout=5000)
                await inp.fill(lovable_name)
                await asyncio.sleep(0.5)
                await page.evaluate(
                    '() => { const dlg = document.querySelector("[role=dialog]"); if (!dlg) return; const save = Array.from(dlg.querySelectorAll("button")).find(b => b.textContent.trim() === "Save"); if (save) save.click(); }'
                )
                await asyncio.sleep(2)
            except Exception as e:
                print(f'    rename err: {e}', flush=True)
        # Volta pro projeto
        await page.goto(f'https://lovable.dev/projects/{project_id}', wait_until='domcontentloaded', timeout=30000)
        await asyncio.sleep(5)

    # 3. Click Publish
    try:
        await page.locator('button[aria-label="Publish"]').first.click(timeout=15000)
    except Exception as e:
        print(f'    ERR publish click: {e}', flush=True)
        return None
    await asyncio.sleep(3)

    # 4. Edit subdomain — clica no botão que contém .lovable.app
    await page.evaluate(
        '() => { const ws = Array.from(document.querySelectorAll("[data-radix-popper-content-wrapper], [role=menu]")); for (const w of ws) { const btns = Array.from(w.querySelectorAll("button")); for (const b of btns) { if (b.textContent.includes(".lovable.app")) { b.click(); return; } } } }'
    )
    await asyncio.sleep(1.5)

    # 5. Procura input visível com subdomain atual (não "/") e substitui
    try:
        all_inputs = await page.query_selector_all('input[type="text"]')
        edited = False
        for inp in all_inputs:
            try:
                val = await inp.input_value()
                visible = await inp.is_visible()
                if visible and val and val != '/' and '.app' not in val and len(val) > 2 and subdomain not in val:
                    await inp.click()
                    await page.keyboard.press('Control+a')
                    await page.keyboard.press('Delete')
                    await page.keyboard.type(subdomain)
                    await asyncio.sleep(0.8)
                    edited = True
                    print(f'    subdomain typed: {subdomain}', flush=True)
                    break
            except Exception:
                continue
    except Exception as e:
        print(f'    subdomain err: {e}', flush=True)

    # 6. Steps: Continue → Public → Continue → Continue → Publish
    clicks = []
    for step in range(6):
        await asyncio.sleep(2)
        clicked = await page.evaluate(
            '() => { const ws = Array.from(document.querySelectorAll("[data-radix-popper-content-wrapper], [role=menu]")); for (const w of ws) { const btns = Array.from(w.querySelectorAll("button")); const c = btns.find(b => { const t = b.textContent.trim(); return (t === "Continue" || t === "Publish") && !b.disabled; }); if (c) { c.click(); return t_val(c.textContent.trim()); } } function t_val(v) { return v; } return null; }'
        )
        # Handle undefined t_val fallback via simpler version
        if clicked is None:
            clicked = await page.evaluate(
                '() => { const ws = Array.from(document.querySelectorAll("[data-radix-popper-content-wrapper], [role=menu]")); for (const w of ws) { const btns = Array.from(w.querySelectorAll("button")); for (const b of btns) { const t = b.textContent.trim(); if ((t === "Continue" || t === "Publish") && !b.disabled) { b.click(); return t; } } } return null; }'
            )
        clicks.append(clicked)
        print(f'    step {step+1}: {clicked}', flush=True)
        if clicked == 'Publish':
            await asyncio.sleep(18)
            break
        if clicked is None and step >= 2:
            break

    # 7. Verify live
    ctx = ssl.create_default_context(); ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
    url = f'https://{subdomain}.lovable.app/'
    for attempt in range(5):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            r = urllib.request.urlopen(req, context=ctx, timeout=10)
            if r.status == 200:
                return url
        except Exception:
            await asyncio.sleep(6)
    return None


async def main():
    sites = json.loads(Path('tools/migration/sites_pendentes.json').read_text(encoding='utf-8'))
    results_prev = json.loads(Path('.tmp/migration/lovable_batch_results.json').read_text(encoding='utf-8'))

    # Inclui o 86 manualmente
    results_prev.insert(0, {
        'site': 'Teatro dos Bons Hábitos',
        'url': None,
        'project_id': 'fed8254b-bbfd-42ad-9b74-9cf6a6a918a7',
        'error': 'Publish failed (previous run)',
    })

    by_site = {s['nome_planilha']: s for s in sites}

    final_results = []
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp('http://localhost:9222')
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else await ctx.new_page()

        for res in results_prev:
            site = by_site.get(res['site'])
            if not site:
                print(f'SKIP unknown site: {res["site"]}', flush=True)
                continue
            pid = res['project_id']
            print(f'\n--- {site["numero_ntics"]} {site["nome_planilha"]} ({pid[:8]}) ---', flush=True)
            url = await publish_one(page, pid, site['subdomain'], site['lovable_name'])
            if url:
                print(f'  LIVE: {url}', flush=True)
                final_results.append({**res, 'url': url, 'error': None, 'numero': site['numero_ntics']})
            else:
                print(f'  FAIL publish', flush=True)
                final_results.append({**res, 'numero': site['numero_ntics']})
            Path('.tmp/migration/lovable_recover_results.json').write_text(
                json.dumps(final_results, indent=2, ensure_ascii=False), encoding='utf-8'
            )

    print('\n=== SUMMARY ===', flush=True)
    ok = sum(1 for r in final_results if r.get('url'))
    print(f'Published: {ok}/{len(final_results)}', flush=True)
    for r in final_results:
        status = 'OK ' if r.get('url') else 'ERR'
        print(f'  {status} {r["numero"]}: {r.get("url") or "not published"}', flush=True)


if __name__ == '__main__':
    asyncio.run(main())
