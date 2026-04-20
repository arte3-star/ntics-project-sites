#!/usr/bin/env python3
"""
organize_all_assets.py — Para cada site RF:
1. Navega via CDP e mapeia seções → fotos (DOM analysis)
2. Baixa fotos faltantes do RF hosting
3. Salva section_map.json no diretório do projeto
4. Salva lista de fotos por seção para o gerador HTML usar
"""

import asyncio
import io
import json
import os
import re
import ssl
import sys
import urllib.request
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from playwright.async_api import async_playwright

ROOT = Path(__file__).resolve().parents[2]
UA = "Mozilla/5.0"
_ssl = ssl.create_default_context()
_ssl.check_hostname = False
_ssl.verify_mode = ssl.CERT_NONE


def download_img(url, dest, referer):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA, "Referer": referer})
        data = urllib.request.urlopen(req, context=_ssl, timeout=25).read()
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
        return len(data)
    except Exception as e:
        print(f"      DL ERR: {e}")
        return 0


async def map_one_site(page, site: dict) -> dict:
    num = site['numero_ntics']
    rf_url = site['rf_url']
    rf_id = re.search(r'24321761-(\d+)', rf_url).group(1)

    print(f"\n{'='*50}")
    print(f" {num} — {site['nome_planilha']}")
    print(f"{'='*50}")

    # Navigate to public site
    await page.goto(rf_url, wait_until='domcontentloaded', timeout=60000)
    await asyncio.sleep(5)

    # Scroll to load all lazy content
    for i in range(30):
        await page.mouse.wheel(0, 300)
        await asyncio.sleep(0.3)
    await asyncio.sleep(3)
    await page.evaluate('window.scrollTo(0, 0)')
    await asyncio.sleep(1)

    # Extract section-by-section photo map
    section_map = await page.evaluate(r'''() => {
        const sections = Array.from(document.querySelectorAll('section'));
        return sections.map((s, i) => {
            const h = s.querySelector('h1, h2, h3');
            const imgs = Array.from(s.querySelectorAll('img'))
                .filter(img => img.src && !img.src.startsWith('data:') && !img.src.includes('rfstat'))
                .map(img => ({
                    fname: img.src.split('/').pop(),
                    fullUrl: img.src,
                    w: img.naturalWidth,
                    h: img.naturalHeight,
                    displayW: Math.round(img.getBoundingClientRect().width),
                    displayH: Math.round(img.getBoundingClientRect().height),
                }));
            const bgs = [];
            s.querySelectorAll('*').forEach(el => {
                const bg = window.getComputedStyle(el).backgroundImage;
                if (bg && bg !== 'none' && bg.includes('url(')) {
                    const re = /url\(["']?([^"')]+)["']?\)/g;
                    let m;
                    while ((m = re.exec(bg)) !== null) {
                        if (!m[1].startsWith('data:') && !m[1].includes('rfstat')) {
                            bgs.push({ fname: m[1].split('/').pop(), fullUrl: m[1] });
                        }
                    }
                }
            });
            // Get section heading colors
            const headingColor = h ? window.getComputedStyle(h).color : '';
            const sectionBg = window.getComputedStyle(s).backgroundColor;
            // Get paragraphs
            const paragraphs = Array.from(s.querySelectorAll('p'))
                .map(p => p.innerText.trim())
                .filter(t => t.length > 10 && !t.includes('Renderforest'));
            return {
                idx: i,
                title: h ? h.innerText.trim() : '',
                imgs,
                bgs,
                headingColor,
                sectionBg,
                paragraphs: paragraphs.slice(0, 3),
                height: Math.round(s.getBoundingClientRect().height),
            };
        });
    }''')

    # Also get video from editor
    editor_url = f'https://www.renderforest.com/website-maker/{rf_id}/lang/edit'
    await page.goto(editor_url, wait_until='domcontentloaded', timeout=30000)
    await asyncio.sleep(8)
    editor_html = await page.content()
    yt_ids = list(set(re.findall(r'youtube\.com/embed/([a-zA-Z0-9_-]{11})', editor_html)))

    # Find project folder
    folder = None
    for d in os.listdir(ROOT / 'assets' / 'projetos'):
        if d.startswith(f'{num}. '):
            folder = d
            break
    if not folder:
        print(f"  NO FOLDER for {num}")
        return {}

    project_dir = ROOT / 'assets' / 'projetos' / folder
    fotos_dir = project_dir / 'FOTOS'
    gh_dir = ROOT / '.tmp' / 'ntics-project-sites' / site['github_slug'] / 'FOTOS'

    # Collect ALL photo URLs from RF sections
    all_rf_photos = []
    for s in section_map:
        for img in s['imgs']:
            all_rf_photos.append(img)
        for bg in s['bgs']:
            all_rf_photos.append(bg)

    # Download missing photos
    existing_gh = set(f.name for f in gh_dir.iterdir() if f.name != 'desktop.ini') if gh_dir.exists() else set()
    existing_local = set(f.name for f in fotos_dir.iterdir() if f.name != 'desktop.ini') if fotos_dir.exists() else set()

    downloaded = 0
    for photo in all_rf_photos:
        hash_part = photo['fname'].split('.')[0]
        ext = '.' + photo['fname'].split('.')[-1] if '.' in photo['fname'] else '.jpg'
        gh_name = f"rf-{rf_id}-{hash_part}{ext}"

        if gh_name not in existing_gh:
            url = photo.get('fullUrl', f'https://hosting.renderforestsites.com/24321761/{rf_id}/media/{hash_part}{ext}')
            dest_local = fotos_dir / gh_name
            dest_gh = gh_dir / gh_name
            gh_dir.mkdir(parents=True, exist_ok=True)

            size = download_img(url, dest_local, rf_url)
            if size > 0:
                import shutil
                shutil.copy2(dest_local, dest_gh)
                downloaded += 1
                existing_gh.add(gh_name)

    # Build clean section map with GitHub filenames
    def to_gh_name(rf_fname):
        hash_part = rf_fname.split('.')[0]
        ext = '.' + rf_fname.split('.')[-1] if '.' in rf_fname else '.jpg'
        return f"rf-{rf_id}-{hash_part}{ext}"

    clean_map = []
    for s in section_map:
        clean_imgs = [to_gh_name(img['fname']) for img in s['imgs']]
        clean_bgs = [to_gh_name(bg['fname']) for bg in s['bgs']]
        # Verify they exist
        clean_imgs = [f for f in clean_imgs if f in existing_gh]
        clean_bgs = [f for f in clean_bgs if f in existing_gh]

        clean_map.append({
            'idx': s['idx'],
            'title': s['title'],
            'imgs': clean_imgs,
            'bgs': clean_bgs,
            'headingColor': s.get('headingColor', ''),
            'paragraphs': s.get('paragraphs', []),
        })

    result = {
        'numero': num,
        'nome': site['nome_planilha'],
        'slug': site['github_slug'],
        'rf_url': rf_url,
        'sections': clean_map,
        'youtube_ids': yt_ids,
        'logo': next((f.name for f in (project_dir / 'LOGOS').iterdir() if f.suffix.lower() == '.png' and f.name != 'desktop.ini'), ''),
        'regua': next((f.name for f in (project_dir / 'REGUAS').iterdir() if f.name.startswith('regua_') and f.name != 'desktop.ini'), ''),
    }

    # Save section map
    (project_dir / 'section_map.json').write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding='utf-8')

    # Report
    total_photos = sum(len(s['imgs']) + len(s['bgs']) for s in clean_map)
    print(f"  Sections: {len(clean_map)} | Photos: {total_photos} | Downloaded: {downloaded} new")
    print(f"  YouTube: {yt_ids}")
    print(f"  Logo: {result['logo']} | Regua: {result['regua']}")
    for s in clean_map:
        n = len(s['imgs']) + len(s['bgs'])
        if n > 0 or s['title']:
            print(f"    [{s['idx']}] {s['title'][:40]}: {n} photos")

    return result


async def main():
    sites = json.loads((ROOT / 'tools/migration/sites_pendentes.json').read_text(encoding='utf-8'))

    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp('http://localhost:9222')
        ctx = browser.contexts[0]
        page = ctx.pages[0]

        all_results = []
        for site in sites:
            result = await map_one_site(page, site)
            if result:
                all_results.append(result)

    # Save master index
    (ROOT / '.tmp/migration/all_section_maps.json').write_text(
        json.dumps(all_results, indent=2, ensure_ascii=False), encoding='utf-8'
    )

    print(f"\n{'='*50}")
    print(f" RESUMO: {len(all_results)} sites mapeados")
    print(f"{'='*50}")
    for r in all_results:
        total = sum(len(s['imgs']) + len(s['bgs']) for s in r['sections'])
        print(f"  {r['numero']:>3}: {total:>2} fotos | {len(r['youtube_ids'])} vídeos | {r['nome'][:35]}")


if __name__ == '__main__':
    asyncio.run(main())
