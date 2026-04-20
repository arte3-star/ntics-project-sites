#!/usr/bin/env python3
"""
lovable_publish_simple.py — Publica projetos pelo caminho mais simples possível.

Estratégia:
- NÃO edita subdomain (aceita o auto-gerado)
- Click Publish → 4x Continue → Publish → wait 20s → check
- Subdomain customizado fica pra refinamento manual depois

Uso: python tools/migration/lovable_publish_simple.py
"""

import asyncio
import json
import re
import ssl
import sys
import urllib.request
from pathlib import Path

from playwright.async_api import async_playwright


async def click_button_in_popover(page, label_options: list[str]) -> str | None:
    """Clica em qualquer botão do popover que tenha texto na lista. Retorna texto clicado."""
    return await page.evaluate(
        f'''(labels) => {{
            const ws = Array.from(document.querySelectorAll("[data-radix-popper-content-wrapper], [role=menu]"));
            for (const w of ws) {{
                if (!w.offsetParent) continue;
                const btns = Array.from(w.querySelectorAll("button"));
                for (const b of btns) {{
                    const t = b.textContent.trim();
                    if (labels.includes(t) && !b.disabled) {{
                        b.click();
                        return t;
                    }}
                }}
            }}
            return null;
        }}''',
        label_options,
    )


async def publish_project(page, project_id: str) -> dict:
    """Publica um projeto. Retorna dict com url e diagnóstico."""
    result = {'project_id': project_id, 'url': None, 'subdomain': None, 'steps': []}

    if project_id not in page.url:
        await page.goto(f'https://lovable.dev/projects/{project_id}', wait_until='domcontentloaded', timeout=30000)
        await asyncio.sleep(7)
    await page.bring_to_front()

    # Garante que não tem popover aberto
    await page.keyboard.press('Escape')
    await asyncio.sleep(1)

    # Click Publish
    try:
        await page.locator('button[aria-label="Publish"]').first.click(timeout=15000)
    except Exception as e:
        result['error'] = f'Publish click: {e}'
        return result
    await asyncio.sleep(3)

    # Captura subdomain auto-gerado para retorno
    domain = await page.evaluate(
        '''() => {
            const ws = Array.from(document.querySelectorAll("[data-radix-popper-content-wrapper], [role=menu]"));
            for (const w of ws) {
                if (!w.offsetParent) continue;
                const btns = Array.from(w.querySelectorAll("button"));
                for (const b of btns) {
                    if (b.textContent.includes(".lovable.app")) return b.textContent.trim();
                }
            }
            return null;
        }'''
    )
    if domain:
        result['subdomain'] = domain.replace('.lovable.app', '')
        print(f'    auto-subdomain: {domain}', flush=True)

    # 4 steps de Continue + 1 Publish
    for step in range(7):
        await asyncio.sleep(2.5)
        clicked = await click_button_in_popover(page, ['Continue', 'Publish'])
        result['steps'].append(clicked)
        print(f'    step {step+1}: {clicked}', flush=True)
        if clicked == 'Publish':
            await asyncio.sleep(20)
            break
        if clicked is None:
            # Se falhou, tenta detectar se popover sumiu
            still_open = await page.evaluate(
                '() => Array.from(document.querySelectorAll("[data-radix-popper-content-wrapper], [role=menu]")).some(w => w.offsetParent && w.textContent.includes("Publish"))'
            )
            if not still_open:
                result['error'] = f'Popover closed at step {step+1}'
                break

    # Verify
    if result['subdomain']:
        url = f'https://{result["subdomain"]}.lovable.app/'
        ctx = ssl.create_default_context(); ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
        for attempt in range(5):
            try:
                req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                r = urllib.request.urlopen(req, context=ctx, timeout=10)
                if r.status == 200:
                    result['url'] = url
                    return result
            except Exception:
                await asyncio.sleep(6)
    return result


async def main():
    sites = json.loads(Path('tools/migration/sites_pendentes.json').read_text(encoding='utf-8'))
    by_site = {s['nome_planilha']: s for s in sites}

    # Lista de projetos a publicar (project_id + nome)
    projects = [
        ('Teatro dos Bons Hábitos', 'fed8254b-bbfd-42ad-9b74-9cf6a6a918a7'),
        ('Teatro e Oficinas Robótica nas Escolas 2ª Edição', '39bc4c93-8cae-4bc0-b681-a8a279928cd7'),
        ('Exposição Culinária Sustentável', '45f83983-0b69-4cf4-b461-7f250eab38c1'),
        ('Robótica Cultural nas Escolas', '241badb1-6881-4d88-b7db-5342b4893612'),
        ('Programa de Empreendedorismo e Cultura 3ª Edição', '18c88394-c9a7-4d9b-bd57-7ca9a2f70518'),
        ('Teatro dos ODS', '3cc86b59-55ed-4b77-be38-9de17e9fd1d4'),
        ('Oficina de Teatro Sustentável', '2179b37f-66dd-4468-9597-f7a1fc8d0582'),
        ('Conhecendo os ODS', 'e77baf7e-55cd-4367-bdf7-52da3284d93e'),
        ('Caminhão da Cultura e Sustentabilidade', 'f509fec9-169a-42a2-b9df-6188466057a4'),
    ]

    final = []
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp('http://localhost:9222')
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else await ctx.new_page()

        for name, pid in projects:
            site = by_site.get(name, {})
            num = site.get('numero_ntics', '?')
            print(f'\n--- {num} {name[:40]} ({pid[:8]}) ---', flush=True)
            res = await publish_project(page, pid)
            res['site_name'] = name
            res['numero'] = num
            final.append(res)
            Path('.tmp/migration/lovable_publish_simple_results.json').write_text(
                json.dumps(final, indent=2, ensure_ascii=False), encoding='utf-8'
            )

    print('\n=== SUMMARY ===', flush=True)
    ok = sum(1 for r in final if r.get('url'))
    print(f'Published: {ok}/{len(final)}', flush=True)
    for r in final:
        status = 'OK ' if r.get('url') else 'ERR'
        print(f'  {status} {r["numero"]:>3}: {r.get("url") or r.get("error", "no url")}', flush=True)


if __name__ == '__main__':
    asyncio.run(main())
