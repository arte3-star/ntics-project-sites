#!/usr/bin/env python3
"""
lovable_review_final.py — Verifica cada projeto Lovable após o fix.

Para cada projeto:
- Navega
- Espera carregar
- Lê iframe de preview
- Extrai: <title>, h1, meta description, lista de imgs únicas, total de imgs
- Captura screenshot
- Detecta: duplicatas, logo no grid, título errado
"""

import asyncio
import io
import json
import sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from playwright.async_api import async_playwright


async def review_one(page, p: dict) -> dict:
    res = {'numero': p['numero'], 'name': p['name'], 'pid': p['pid']}
    print(f"\n--- {p['numero']} {p['name'][:35]} ---", flush=True)
    try:
        await page.goto(f"https://lovable.dev/projects/{p['pid']}", wait_until='domcontentloaded', timeout=30000)
        await asyncio.sleep(8)
        await page.bring_to_front()

        # Find preview iframe
        iframe_info = await page.evaluate('''() => {
            const f = document.querySelector('iframe');
            if (!f) return null;
            return { src: f.src, hasContent: !!f.contentDocument };
        }''')
        res['iframe'] = iframe_info
        if not iframe_info:
            res['error'] = 'no iframe'
            print('    ERR no iframe')
            return res

        # Find frame and extract data
        frame = None
        for f in page.frames:
            if 'lovableproject.com' in f.url or 'lovable.app' in f.url:
                frame = f
                break

        if not frame:
            res['error'] = 'no preview frame'
            print('    ERR no preview frame')
            return res

        try:
            data = await frame.evaluate('''() => {
                const title = document.title;
                const desc = document.querySelector('meta[name="description"]')?.content || '';
                const h1s = Array.from(document.querySelectorAll('h1')).map(h => h.innerText.trim());
                const imgs = Array.from(document.querySelectorAll('img')).map(i => ({
                    src: i.src,
                    alt: i.alt,
                    w: i.naturalWidth,
                    h: i.naturalHeight,
                }));
                return { title, desc, h1s, imgs };
            }''')
        except Exception as e:
            res['error'] = f'frame eval: {e}'
            print(f'    ERR frame eval: {e}')
            return res

        # Analysis
        srcs = [i['src'] for i in data['imgs']]
        unique_srcs = set(srcs)
        dupes = {s: srcs.count(s) for s in unique_srcs if srcs.count(s) > 1}
        logo_in_grid = [i for i in data['imgs'] if 'logo' in i['src'].lower() or 'LOGOS' in i['src']]
        # Filter logo_in_grid: only count if likely in gallery section (not header/sobre)
        # Heuristic: if there are 2+ logo refs, the extras are probably in the grid
        logo_count = len(logo_in_grid)

        res['title'] = data['title']
        res['desc'] = data['desc']
        res['h1s'] = data['h1s']
        res['img_total'] = len(srcs)
        res['img_unique'] = len(unique_srcs)
        res['dupes'] = dupes
        res['logo_refs'] = logo_count
        res['title_ok'] = 'Lovable' not in data['title']
        res['desc_ok'] = 'Lovable Generated' not in data['desc'] and len(data['desc']) > 30

        print(f"    title: {data['title'][:60]}")
        print(f"    desc:  {data['desc'][:80]}")
        print(f"    h1[0]: {data['h1s'][0] if data['h1s'] else '(none)'}")
        print(f"    imgs:  {len(srcs)} total, {len(unique_srcs)} únicas, {len(dupes)} duplicadas")
        print(f"    logo refs: {logo_count}")
        print(f"    [{'OK' if res['title_ok'] else 'BAD'} title] [{'OK' if res['desc_ok'] else 'BAD'} desc]")

        await page.screenshot(path=f'.tmp/migration/final-{p["numero"]}.png', full_page=False)

    except Exception as e:
        res['error'] = f'{type(e).__name__}: {e}'
        print(f'    EXCEPTION: {res["error"]}')

    return res


async def main():
    projects = json.loads(Path('.tmp/migration/fix_inputs.json').read_text(encoding='utf-8'))
    print(f'Reviewing {len(projects)} projects...', flush=True)

    results = []
    async with async_playwright() as p:
        b = await p.chromium.connect_over_cdp('http://localhost:9222')
        ctx = b.contexts[0]
        page = ctx.pages[0] if ctx.pages else await ctx.new_page()

        for proj in projects:
            r = await review_one(page, proj)
            results.append(r)

    Path('.tmp/migration/final_review.json').write_text(
        json.dumps(results, indent=2, ensure_ascii=False), encoding='utf-8'
    )

    print('\n=== ISSUES ===', flush=True)
    for r in results:
        issues = []
        if r.get('error'):
            issues.append(f'ERROR={r["error"]}')
        if not r.get('title_ok'):
            issues.append(f'title="{r.get("title","")[:30]}"')
        if not r.get('desc_ok'):
            issues.append(f'desc bad')
        if r.get('dupes'):
            issues.append(f'{len(r["dupes"])} duplicadas')
        if r.get('logo_refs', 0) > 1:
            issues.append(f'{r["logo_refs"]} logo refs')
        marker = 'OK ' if not issues else 'WARN'
        print(f'  {marker} {r["numero"]:>3}: {", ".join(issues) if issues else "all good"}')


if __name__ == '__main__':
    asyncio.run(main())
