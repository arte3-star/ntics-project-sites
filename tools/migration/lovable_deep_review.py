#!/usr/bin/env python3
"""
lovable_deep_review.py — Análise profunda de cada site Lovable vs RF original.

Para cada projeto:
1. Lê scrape.json do RF (seções, vídeos, imagens)
2. Inspeciona o DOM do preview Lovable
3. Compara: seções faltando, vídeos, logo na galeria, régua na galeria, imagens erradas
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


async def analyze_one(page, site: dict, pid: str) -> dict:
    num = site['numero_ntics']
    result = {'numero': num, 'name': site['nome_planilha'], 'pid': pid, 'issues': []}

    # Load RF scrape data
    folder = None
    for d in os.listdir(ROOT / 'assets' / 'projetos'):
        if d.startswith(f'{num}. '):
            folder = d
            break
    if not folder:
        result['issues'].append('NO LOCAL FOLDER')
        return result

    scrape_path = ROOT / 'assets' / 'projetos' / folder / 'scrape.json'
    if not scrape_path.exists():
        result['issues'].append('NO SCRAPE.JSON')
        return result

    scrape = json.loads(scrape_path.read_text(encoding='utf-8'))

    # RF data
    rf_sections = scrape.get('sections', [])
    rf_videos = scrape.get('videos', [])
    rf_h1 = scrape.get('h1', [])
    rf_h2 = scrape.get('h2', [])
    rf_imgs = scrape.get('images', [])
    rf_links = scrape.get('external_links', [])

    # Check for democratização section in RF
    has_democratizacao_rf = any(
        'democra' in (s.get('title', '') + ' '.join(s.get('paragraphs', []))).lower()
        for s in rf_sections
    )
    has_video_rf = len(rf_videos) > 0
    # Also check if paragraphs mention video/democratização
    has_video_text_rf = any('vídeo' in p.lower() or 'video' in p.lower() or 'democra' in p.lower()
                           for p in scrape.get('paragraphs', []))
    # Check for YouTube/Vimeo links
    video_links_rf = [l for l in rf_links if 'youtube' in l.get('href', '') or 'youtu.be' in l.get('href', '') or 'vimeo' in l.get('href', '')]

    result['rf'] = {
        'sections': len(rf_sections),
        'h1': rf_h1[:3],
        'h2': rf_h2[:8],
        'images': len(rf_imgs),
        'videos': rf_videos,
        'video_links': video_links_rf,
        'has_democratizacao': has_democratizacao_rf,
        'has_video_text': has_video_text_rf,
    }

    # Navigate to Lovable
    await page.goto(f'https://lovable.dev/projects/{pid}', wait_until='domcontentloaded', timeout=30000)
    await asyncio.sleep(12)

    # Find preview frame
    frame = None
    for f in page.frames:
        if 'lovableproject.com' in f.url or 'id-preview' in f.url:
            frame = f
            break

    if not frame:
        result['issues'].append('NO PREVIEW FRAME (build may have failed)')
        # Check build status
        build_err = await page.evaluate('() => document.body.innerText.includes("Build unsuccessful")')
        if build_err:
            result['issues'].append('BUILD FAILED')
        return result

    try:
        lovable_data = await frame.evaluate('''() => {
            const data = {
                title: document.title,
                h1s: Array.from(document.querySelectorAll('h1')).map(h => h.innerText.trim()),
                h2s: Array.from(document.querySelectorAll('h2')).map(h => h.innerText.trim()),
                sections: [],
                images: [],
                videos: [],
                iframes: [],
                hasRegua: false,
                galleryImgs: [],
            };

            // All sections
            document.querySelectorAll('section').forEach((s, i) => {
                const h = s.querySelector('h1, h2, h3');
                data.sections.push({
                    idx: i,
                    title: h ? h.innerText.trim() : '',
                    imgCount: s.querySelectorAll('img').length,
                    hasVideo: s.querySelectorAll('iframe, video, [class*="video"]').length > 0,
                    text: s.innerText.trim().slice(0, 100),
                });
            });

            // All images with context
            document.querySelectorAll('img').forEach(img => {
                const src = img.src || '';
                const inGallery = !!img.closest('[id*="galer"], [class*="galler"], [class*="gallery"]')
                    || !!img.closest('section')?.querySelector('h1, h2')?.innerText?.toLowerCase()?.includes('galeria');

                // Check parent section
                let sectionTitle = '';
                const sec = img.closest('section');
                if (sec) {
                    const h = sec.querySelector('h1, h2');
                    sectionTitle = h ? h.innerText.trim() : '';
                }

                const isLogo = src.toLowerCase().includes('logo') || src.includes('LOGOS/');
                const isRegua = src.toLowerCase().includes('regua') || src.includes('REGUAS/');

                data.images.push({
                    src: src.split('/').slice(-2).join('/'),
                    isLogo,
                    isRegua,
                    inGallery,
                    sectionTitle: sectionTitle.slice(0, 40),
                });
            });

            // Check gallery specifically
            const galSection = Array.from(document.querySelectorAll('section')).find(s => {
                const h = s.querySelector('h1, h2');
                return h && h.innerText.toLowerCase().includes('galeria');
            });
            if (galSection) {
                galSection.querySelectorAll('img').forEach(img => {
                    data.galleryImgs.push({
                        src: img.src.split('/').slice(-2).join('/'),
                        isLogo: img.src.toLowerCase().includes('logo') || img.src.includes('LOGOS/'),
                        isRegua: img.src.toLowerCase().includes('regua') || img.src.includes('REGUAS/'),
                    });
                });
            }

            // Videos/iframes
            document.querySelectorAll('iframe').forEach(f => {
                data.iframes.push(f.src);
            });
            document.querySelectorAll('video').forEach(v => {
                data.videos.push(v.src);
            });

            // Regua in footer
            const footer = document.querySelector('footer');
            if (footer) {
                data.hasRegua = Array.from(footer.querySelectorAll('img')).some(
                    i => i.src.toLowerCase().includes('regua') || i.src.includes('REGUAS/')
                );
            }

            // Header
            const header = document.querySelector('header');
            data.headerBg = header ? window.getComputedStyle(header).backgroundColor : '';
            data.headerHasLogo = header ? header.querySelectorAll('img').length > 0 : false;

            return data;
        }''')
    except Exception as e:
        result['issues'].append(f'FRAME EVAL ERROR: {e}')
        return result

    result['lovable'] = {
        'title': lovable_data['title'],
        'sections': len(lovable_data['sections']),
        'h1s': lovable_data['h1s'][:5],
        'h2s': lovable_data['h2s'][:8],
        'total_imgs': len(lovable_data['images']),
        'gallery_imgs': len(lovable_data['galleryImgs']),
        'has_regua_footer': lovable_data['hasRegua'],
        'header_has_logo': lovable_data['headerHasLogo'],
        'header_bg': lovable_data['headerBg'],
        'iframes': lovable_data['iframes'],
    }

    # === ISSUES DETECTION ===

    # 1. Logo in gallery
    logo_in_gallery = [g for g in lovable_data['galleryImgs'] if g['isLogo']]
    if logo_in_gallery:
        result['issues'].append(f'LOGO NA GALERIA ({len(logo_in_gallery)}x)')

    # 2. Regua in gallery
    regua_in_gallery = [g for g in lovable_data['galleryImgs'] if g['isRegua']]
    if regua_in_gallery:
        result['issues'].append(f'REGUA NA GALERIA ({len(regua_in_gallery)}x)')

    # 3. Duplicate images
    all_srcs = [i['src'] for i in lovable_data['images']]
    dupes = {s: all_srcs.count(s) for s in set(all_srcs) if all_srcs.count(s) > 1}
    if dupes:
        result['issues'].append(f'{len(dupes)} IMAGENS DUPLICADAS')

    # 4. Missing democratização/video
    if has_democratizacao_rf or has_video_text_rf:
        lovable_text = ' '.join(s['text'] for s in lovable_data['sections']).lower()
        has_demo_lovable = 'democra' in lovable_text
        has_video_lovable = len(lovable_data['iframes']) > 0 or any(s['hasVideo'] for s in lovable_data['sections'])
        if not has_demo_lovable:
            result['issues'].append('FALTA SEÇÃO DEMOCRATIZAÇÃO')
        if (has_video_rf or video_links_rf) and not has_video_lovable:
            result['issues'].append('FALTA VÍDEO EMBED')
        elif has_video_text_rf and not has_video_lovable:
            result['issues'].append('RF MENCIONA VÍDEO MAS LOVABLE NÃO TEM IFRAME')

    # 5. Regua not in footer
    if not lovable_data['hasRegua']:
        result['issues'].append('REGUA NÃO ESTÁ NO FOOTER')

    # 6. Logo not in header
    if not lovable_data['headerHasLogo']:
        result['issues'].append('LOGO NÃO ESTÁ NO HEADER')

    # 7. Wrong title
    if 'Lovable' in lovable_data['title'] or not lovable_data['title']:
        result['issues'].append(f'TITLE ERRADO: "{lovable_data["title"][:40]}"')

    # 8. Section count mismatch
    rf_sec_count = len([s for s in rf_sections if s.get('title')])
    lovable_sec_count = len(lovable_data['sections'])
    if lovable_sec_count < rf_sec_count - 2:
        result['issues'].append(f'FALTAM SEÇÕES (RF={rf_sec_count} vs Lovable={lovable_sec_count})')

    return result


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
            r = await analyze_one(page, site, pid)
            results.append(r)
            n = r['numero']
            issues = r['issues']
            print(f"\n{'='*60}")
            print(f" {n} — {r['name']}")
            print(f"{'='*60}")
            if r.get('rf'):
                rf = r['rf']
                print(f"  RF: {rf['sections']} seções, {rf['images']} imgs, democratização={rf['has_democratizacao']}, vídeo_texto={rf['has_video_text']}")
                if rf['videos']:
                    print(f"  RF vídeos: {rf['videos']}")
                if rf['video_links']:
                    print(f"  RF links vídeo: {[l['href'][:60] for l in rf['video_links']]}")
                print(f"  RF h2: {rf['h2']}")
            if r.get('lovable'):
                lv = r['lovable']
                print(f"  Lovable: {lv['sections']} seções, {lv['total_imgs']} imgs, galeria={lv['gallery_imgs']}, regua_footer={lv['has_regua_footer']}")
                print(f"  Lovable h2: {lv['h2s']}")
                print(f"  Lovable title: {lv['title'][:50]}")
                print(f"  Lovable iframes: {lv['iframes']}")
            if issues:
                print(f"  *** PROBLEMAS: ***")
                for i in issues:
                    print(f"    - {i}")
            else:
                print(f"  OK — sem problemas detectados")

    # Save
    (ROOT / '.tmp/migration/deep_review.json').write_text(
        json.dumps(results, indent=2, ensure_ascii=False), encoding='utf-8'
    )

    # Summary
    print(f"\n{'='*60}")
    print(f" RESUMO")
    print(f"{'='*60}")
    for r in results:
        issues = r['issues']
        marker = 'OK' if not issues else f'{len(issues)} problemas'
        print(f"  {r['numero']:>3} {r['name'][:35]:<35} {marker}")
        for i in issues:
            print(f"       - {i}")


if __name__ == '__main__':
    asyncio.run(main())
