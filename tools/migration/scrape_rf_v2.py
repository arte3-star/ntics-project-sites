#!/usr/bin/env python3
"""
scrape_rf_v2.py — Scrape completo do Render Forest via Chrome CDP.

Captura:
- Cores CSS reais (header bg, hero bg, sections, buttons)
- TODAS as imagens (fotos, logo, régua do footer)
- Vídeos embed (YouTube/Vimeo iframes)
- Estrutura completa: sections com título, parágrafos, imagens vinculadas
- Footer com régua de patrocinadores

Uso:
  python tools/migration/scrape_rf_v2.py --only 87
  python tools/migration/scrape_rf_v2.py          # todos os 9
"""

import argparse
import asyncio
import io
import json
import os
import re
import shutil
import ssl
import sys
import urllib.request
from pathlib import Path
from urllib.parse import urlparse

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from PIL import Image, ExifTags
from playwright.async_api import async_playwright

ROOT = Path(__file__).resolve().parents[2]
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36"

_ssl = ssl.create_default_context()
_ssl.check_hostname = False
_ssl.verify_mode = ssl.CERT_NONE


def download_img(url: str, dest: Path, referer: str) -> bool:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA, "Referer": referer, "Accept": "image/*,*/*"})
        data = urllib.request.urlopen(req, context=_ssl, timeout=25).read()
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
        return True
    except Exception as e:
        print(f"    DL ERR {dest.name}: {e}")
        return False


def fix_exif_rotation(path: Path):
    """Aplica rotação EXIF e re-salva."""
    try:
        img = Image.open(path)
        exif = img._getexif()
        if not exif:
            return
        orientation = None
        for tag, val in exif.items():
            if ExifTags.TAGS.get(tag) == 'Orientation':
                orientation = val
                break
        if orientation and orientation != 1:
            rotations = {3: Image.ROTATE_180, 6: Image.ROTATE_270, 8: Image.ROTATE_90}
            if orientation in rotations:
                img = img.transpose(rotations[orientation])
                img.save(path)
    except Exception:
        pass


async def scrape_one(page, rf_url: str, out_dir: Path, slug: str) -> dict:
    """Scrape completo de 1 site RF."""
    fotos = out_dir / "FOTOS"
    logos = out_dir / "LOGOS"
    reguas = out_dir / "REGUAS"
    fotos.mkdir(parents=True, exist_ok=True)
    logos.mkdir(parents=True, exist_ok=True)
    reguas.mkdir(parents=True, exist_ok=True)

    print(f"  Navigating to {rf_url}...")
    await page.goto(rf_url, wait_until='domcontentloaded', timeout=60000)
    await asyncio.sleep(6)

    # Scroll lento para forçar lazy load (RF usa loading="lazy")
    for scroll_pass in range(3):
        await page.evaluate('''async () => {
            await new Promise(resolve => {
                let total = 0;
                const dist = 200;
                const timer = setInterval(() => {
                    window.scrollBy(0, dist);
                    total += dist;
                    if (total >= document.body.scrollHeight + 500) { clearInterval(timer); resolve(); }
                }, 150);
            });
        }''')
        await asyncio.sleep(3)
        n = await page.evaluate('() => document.querySelectorAll("img[src]:not([src^=data])").length')
        print(f"    scroll pass {scroll_pass+1}: {n} images loaded")
        if n > 10:
            break
    await page.evaluate("window.scrollTo(0, 0)")
    await asyncio.sleep(2)

    # Salva HTML
    html = await page.content()
    (out_dir / "site.html").write_text(html, encoding="utf-8")

    # Screenshot (viewport only, full-page pode falhar em páginas longas)
    try:
        await page.screenshot(path=str(out_dir / "rf_screenshot.png"), full_page=False)
    except Exception:
        pass

    # ── Captura dados via JS ──
    data = await page.evaluate('''() => {
        const result = {
            title: document.title || '',
            colors: {},
            sections: [],
            images: [],
            videos: [],
            footer_images: [],
            h1: [],
            h2: [],
            paragraphs: [],
            links: [],
        };

        // Cores CSS reais
        function getColors(el) {
            if (!el) return {};
            const cs = window.getComputedStyle(el);
            return {
                bg: cs.backgroundColor,
                color: cs.color,
                bgImage: cs.backgroundImage !== 'none' ? cs.backgroundImage : null,
            };
        }

        // Header
        const header = document.querySelector('header, nav, [class*="header"], [class*="navbar"]');
        if (header) result.colors.header = getColors(header);

        // Primeiro section grande (hero)
        const firstSection = document.querySelector('section, [class*="hero"], [class*="banner"]');
        if (firstSection) result.colors.hero = getColors(firstSection);

        // Buttons
        const btn = document.querySelector('button, a[class*="btn"], [class*="button"]');
        if (btn) result.colors.button = getColors(btn);

        // Body
        result.colors.body = getColors(document.body);

        // Todas as cores de fundo únicas nas sections
        const sectionColors = new Set();
        document.querySelectorAll('section, [class*="section"], div[style]').forEach(el => {
            const bg = window.getComputedStyle(el).backgroundColor;
            if (bg && bg !== 'rgba(0, 0, 0, 0)' && bg !== 'transparent') {
                sectionColors.add(bg);
            }
        });
        result.colors.section_bgs = [...sectionColors];

        // H1, H2
        document.querySelectorAll('h1').forEach(el => {
            const t = el.innerText.trim();
            if (t.length > 2) result.h1.push(t);
        });
        document.querySelectorAll('h2').forEach(el => {
            const t = el.innerText.trim();
            if (t.length > 2) result.h2.push(t);
        });
        document.querySelectorAll('p').forEach(el => {
            const t = el.innerText.trim();
            if (t.length > 10 && !t.includes('Renderforest') && !t.includes('cookie')) {
                result.paragraphs.push(t);
            }
        });

        // Sections estruturadas
        document.querySelectorAll('section').forEach((sec, idx) => {
            const heading = sec.querySelector('h1, h2, h3');
            const ps = Array.from(sec.querySelectorAll('p')).map(p => p.innerText.trim()).filter(t => t.length > 10);
            const imgs = Array.from(sec.querySelectorAll('img')).filter(i => i.src && !i.src.startsWith('data:')).map(i => ({
                src: i.src, w: i.naturalWidth, h: i.naturalHeight, alt: i.alt || ''
            }));
            const bgs = [];
            sec.querySelectorAll('*').forEach(el => {
                const bgImg = window.getComputedStyle(el).backgroundImage;
                if (bgImg && bgImg !== 'none' && bgImg.includes('url(')) {
                    const m = bgImg.match(/url\\(["']?([^"')]+)["']?\\)/);
                    if (m && !m[1].startsWith('data:')) bgs.push(m[1]);
                }
            });
            const secColors = getColors(sec);
            result.sections.push({
                idx,
                title: heading ? heading.innerText.trim() : '',
                paragraphs: ps.slice(0, 5),
                images: imgs,
                bg_images: bgs,
                bg_color: secColors.bg,
                text_color: secColors.color,
            });
        });

        // Todas imagens (incluindo bg-image)
        const seenSrc = new Set();
        document.querySelectorAll('img').forEach(img => {
            if (img.src && !img.src.startsWith('data:') && !seenSrc.has(img.src)) {
                seenSrc.add(img.src);
                result.images.push({
                    src: img.src, w: img.naturalWidth, h: img.naturalHeight,
                    alt: img.alt || '', type: 'img'
                });
            }
        });
        document.querySelectorAll('*').forEach(el => {
            const bg = window.getComputedStyle(el).backgroundImage;
            if (bg && bg !== 'none' && bg.includes('url(')) {
                const matches = [...bg.matchAll(/url\\(["']?([^"')]+)["']?\\)/g)];
                for (const m of matches) {
                    if (!m[1].startsWith('data:') && !seenSrc.has(m[1])) {
                        seenSrc.add(m[1]);
                        result.images.push({src: m[1], w: 0, h: 0, alt: '', type: 'bg'});
                    }
                }
            }
        });

        // Footer images (régua geralmente está aqui)
        const footer = document.querySelector('footer, [class*="footer"]');
        if (footer) {
            footer.querySelectorAll('img').forEach(img => {
                if (img.src && !img.src.startsWith('data:')) {
                    result.footer_images.push({
                        src: img.src, w: img.naturalWidth, h: img.naturalHeight, alt: img.alt || ''
                    });
                }
            });
            // Also bg-images in footer
            footer.querySelectorAll('*').forEach(el => {
                const bg = window.getComputedStyle(el).backgroundImage;
                if (bg && bg !== 'none' && bg.includes('url(')) {
                    const m = bg.match(/url\\(["']?([^"')]+)["']?\\)/);
                    if (m && !m[1].startsWith('data:')) {
                        result.footer_images.push({src: m[1], w: 0, h: 0, alt: '', type: 'bg'});
                    }
                }
            });
        }

        // Videos (YouTube/Vimeo iframes)
        document.querySelectorAll('iframe').forEach(f => {
            if (f.src && (f.src.includes('youtube') || f.src.includes('youtu.be') || f.src.includes('vimeo'))) {
                result.videos.push({src: f.src, w: f.width, h: f.height});
            }
        });

        // Links
        document.querySelectorAll('a').forEach(a => {
            if (a.href && !a.href.includes('renderforest') && !a.href.startsWith('javascript:') && !a.href.startsWith('mailto:')) {
                result.links.push({href: a.href, text: (a.textContent || '').trim().slice(0, 80)});
            }
        });

        return result;
    }''')

    # ── Parse colors ──
    def parse_rgba(s):
        m = re.match(r'rgba?\((\d+),\s*(\d+),\s*(\d+)', s or '')
        if m:
            return f"#{int(m.group(1)):02X}{int(m.group(2)):02X}{int(m.group(3)):02X}"
        return None

    colors_parsed = {}
    for key in ('header', 'hero', 'button', 'body'):
        obj = data['colors'].get(key, {})
        bg = parse_rgba(obj.get('bg'))
        fg = parse_rgba(obj.get('color'))
        if bg:
            colors_parsed[f'{key}_bg'] = bg
        if fg:
            colors_parsed[f'{key}_fg'] = fg

    section_bgs = []
    for s in data['colors'].get('section_bgs', []):
        c = parse_rgba(s)
        if c and c not in ('#000000', '#FFFFFF', '#FAFAFA') and c not in section_bgs:
            section_bgs.append(c)
    colors_parsed['section_bgs'] = section_bgs

    # ── Download images ──
    downloaded = []
    seen_names = set()
    for im in data['images']:
        src = im['src']
        # Skip renderforest logos/stats
        if 'renderforest_logo' in src or 'rfstat.com' in src or 'google' in src:
            continue
        parsed = urlparse(src)
        parts = parsed.path.strip("/").split("/")
        if len(parts) >= 4 and parts[0].isdigit() and parts[1].isdigit():
            name = f"rf-{parts[1]}-{parts[-1]}"
        else:
            name = parts[-1] if parts else "img"
        if name in seen_names:
            continue
        seen_names.add(name)

        dest = fotos / name
        if dest.exists() and dest.stat().st_size > 1000:
            # Already downloaded
            pass
        elif not download_img(src, dest, rf_url):
            continue

        if dest.exists():
            size = dest.stat().st_size
            fix_exif_rotation(dest)
            downloaded.append({
                "src": src, "local": f"FOTOS/{name}", "size": size,
                "w": im.get('w', 0), "h": im.get('h', 0), "alt": im.get('alt', ''),
            })

    # ── Logo detection ──
    logo_found = None
    for im in downloaded:
        name = Path(im['local']).name
        ext = Path(name).suffix.lower()
        if ext == '.png' and im['size'] < 100_000:
            logo_name = f"{slug}.png"
            src_path = fotos / name
            dst_path = logos / logo_name
            if src_path.exists() and not dst_path.exists():
                shutil.copy2(src_path, dst_path)
            logo_found = logo_name
            break

    # ── Régua detection (footer images) ──
    reguas_found = []
    footer_imgs = data.get('footer_images', [])
    for fi in footer_imgs:
        src = fi['src']
        if 'renderforest_logo' in src or 'rfstat.com' in src:
            continue
        parsed = urlparse(src)
        parts = parsed.path.strip("/").split("/")
        name = f"rf-footer-{parts[-1]}" if parts else "regua.jpg"

        dest = reguas / name
        if not dest.exists():
            download_img(src, dest, rf_url)
        if dest.exists() and dest.stat().st_size > 500:
            reguas_found.append(name)
            print(f"    REGUA: {name} ({dest.stat().st_size} bytes)")

    # Se footer não capturou nada, tenta pegar imagens com aspect ratio > 3:1
    if not reguas_found:
        for im in downloaded:
            w, h = im.get('w', 0), im.get('h', 0)
            if w > 800 and h > 0 and w / h >= 3:
                name = Path(im['local']).name
                src_path = fotos / name
                regua_name = f"regua_{name}"
                dst_path = reguas / regua_name
                if src_path.exists() and not dst_path.exists():
                    shutil.copy2(src_path, dst_path)
                reguas_found.append(regua_name)
                print(f"    REGUA (aspect): {regua_name}")

    # ── Result ──
    result = {
        "source_url": rf_url,
        "slug": slug,
        "title": data['title'],
        "h1": data['h1'],
        "h2": data['h2'],
        "paragraphs": data['paragraphs'][:50],
        "sections": data['sections'][:25],
        "colors": colors_parsed,
        "images": downloaded,
        "logo_detected": logo_found,
        "reguas_detected": reguas_found,
        "videos": data.get('videos', []),
        "external_links": data.get('links', []),
        "footer_images_raw": [fi['src'] for fi in footer_imgs],
    }
    (out_dir / "scrape.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    return result


async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--only', type=int, default=None)
    args = ap.parse_args()

    sites = json.loads((ROOT / 'tools/migration/sites_pendentes.json').read_text(encoding='utf-8'))
    if args.only:
        sites = [s for s in sites if s['numero_ntics'] == args.only]

    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp('http://localhost:9222')
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else await ctx.new_page()

        for s in sites:
            num = s['numero_ntics']
            folder = None
            for d in os.listdir(ROOT / 'assets' / 'projetos'):
                if d.startswith(f'{num}. '):
                    folder = d
                    break
            if not folder:
                print(f'{num}: SKIP no folder')
                continue

            out_dir = ROOT / 'assets' / 'projetos' / folder
            print(f"\n=== {num} {s['nome_planilha']} ===")
            result = await scrape_one(page, s['rf_url'], out_dir, s['slug_snake'])
            print(f"  {len(result['images'])} imgs | logo={result['logo_detected']} | reguas={len(result['reguas_detected'])} | videos={len(result['videos'])}")
            print(f"  colors: {result['colors']}")

    print("\nDone.")


if __name__ == '__main__':
    asyncio.run(main())
