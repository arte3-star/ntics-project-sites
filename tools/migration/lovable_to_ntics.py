#!/usr/bin/env python3
"""
lovable_to_ntics.py — Migra site do Lovable para ntics.com.br/{slug}/

Pipeline:
1. Renderiza página Lovable via Playwright (SPA React → HTML final)
2. Baixa todas as imagens do CDN Lovable
3. Reescreve paths para relativos
4. Upload via REST API nticsfiles
"""

import argparse
import asyncio
import base64
import io
import json
import re
import ssl
import sys
import urllib.request
from pathlib import Path
from urllib.parse import urlparse

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from playwright.async_api import async_playwright

ROOT = Path(__file__).resolve().parents[2]
env = dict(
    l.split('=', 1) for l in (ROOT / '.env').read_text(encoding='utf-8').splitlines()
    if '=' in l and not l.startswith('#')
)
creds = base64.b64encode(f"{env['WP_USER']}:{env['WP_APP_PASSWORD']}".encode()).decode()
AUTH = f"Basic {creds}"
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
UA = "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36"


def download_img(url: str, dest: Path) -> int:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        data = urllib.request.urlopen(req, context=ctx, timeout=30).read()
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
        return len(data)
    except Exception as e:
        print(f"    DL ERR {dest.name}: {e}")
        return 0


def upload_file(remote_path: str, content_bytes: bytes, is_binary=True) -> dict:
    if is_binary:
        content_str = base64.b64encode(content_bytes).decode('ascii')
        payload = {'path': remote_path, 'content': content_str, 'base64': True}
    else:
        content_str = content_bytes.decode('utf-8', errors='replace')
        payload = {'path': remote_path, 'content': content_str, 'base64': False}

    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(
        f"{env['WP_URL']}/wp-json/nticsfiles/v1/write",
        data=data,
        headers={'Authorization': AUTH, 'Content-Type': 'application/json'},
        method='POST',
    )
    try:
        r = urllib.request.urlopen(req, context=ctx, timeout=120).read()
        return json.loads(r)
    except urllib.error.HTTPError as e:
        return {'error': f'HTTP {e.code}: {e.read().decode()[:200]}'}
    except Exception as e:
        return {'error': str(e)}


async def scrape_and_migrate(page, slug: str) -> dict:
    url = f'https://{slug}.lovable.app/'
    print(f"\n=== {slug} ===")
    print(f"  URL: {url}")

    try:
        await page.goto(url, wait_until='domcontentloaded', timeout=60000)
    except Exception as e:
        return {'slug': slug, 'error': f'goto: {e}'}

    await asyncio.sleep(6)
    # Scroll to trigger lazy load
    h = await page.evaluate('() => document.body.scrollHeight')
    for y in range(0, h + 1000, 400):
        await page.evaluate(f'window.scrollTo(0, {y})')
        await asyncio.sleep(0.4)
    await page.evaluate('window.scrollTo(0, 0)')
    await asyncio.sleep(3)

    # Wait for all images to load
    try:
        await page.wait_for_function(
            '() => Array.from(document.querySelectorAll("img")).every(i => i.complete)',
            timeout=60000
        )
    except:
        pass

    # Capture rendered static HTML (strip React scripts - keep only final DOM)
    static_result = await page.evaluate(r'''() => {
        // Get all stylesheets inline
        const styles = [];
        document.querySelectorAll('style').forEach(s => styles.push(s.outerHTML));
        // Get <link rel=stylesheet> for inline fonts/CSS
        document.querySelectorAll('link[rel=stylesheet]').forEach(l => styles.push(l.outerHTML));
        const bodyHtml = document.body.innerHTML;
        const title = document.title;
        const meta = Array.from(document.querySelectorAll('meta')).map(m => m.outerHTML).join('\n');
        return { bodyHtml, title, meta, styles: styles.join('\n') };
    }''')
    # Rebuild HTML without the React root scripts, just rendered DOM
    html = f'''<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{static_result['title']}</title>
{static_result['meta']}
{static_result['styles']}
</head>
<body>
{static_result['bodyHtml']}
</body>
</html>
'''
    # Remove any <script> tags that might break (React runtime, Lovable badge, etc.)
    html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
    html = re.sub(r'<script[^>]*/>', '', html)

    imgs_data = await page.evaluate(r'''() => {
        const imgs = new Set();
        const bgElements = [];  // elements with bg-image: [el_xpath, url]
        document.querySelectorAll('img').forEach(i => {
            if (i.src && !i.src.startsWith('data:')) imgs.add(i.src);
        });
        document.querySelectorAll('*').forEach(el => {
            const bg = window.getComputedStyle(el).backgroundImage;
            if (bg && bg !== 'none' && bg.includes('url(')) {
                const re = /url\(["']?([^"')]+)["']?\)/g;
                let m;
                while ((m = re.exec(bg)) !== null) {
                    if (!m[1].startsWith('data:')) imgs.add(m[1]);
                }
            }
        });
        return [...imgs];
    }''')
    imgs = imgs_data

    print(f"  HTML: {len(html)} chars")
    print(f"  Unique imgs: {len(imgs)}")

    # Build local assets dir
    assets_dir = ROOT / '.tmp' / 'lovable_migrate' / slug
    assets_dir.mkdir(parents=True, exist_ok=True)
    images_dir = assets_dir / 'images'
    images_dir.mkdir(exist_ok=True)

    # Download each image and build URL→local mapping
    url_map = {}  # remote URL → local relative path
    for i, img_url in enumerate(imgs):
        parsed = urlparse(img_url)
        # Get filename
        fname = parsed.path.split('/')[-1]
        if not fname or '.' not in fname:
            fname = f'img{i}.jpg'
        # Ensure unique
        dest = images_dir / fname
        counter = 1
        while dest.exists() and dest.read_bytes() != urllib.request.urlopen(
            urllib.request.Request(img_url, headers={"User-Agent": UA}), context=ctx, timeout=30
        ).read() if False else False:
            dest = images_dir / f"{Path(fname).stem}_{counter}{Path(fname).suffix}"
            counter += 1

        size = download_img(img_url, dest)
        if size > 0:
            url_map[img_url] = f'images/{dest.name}'

    # Also download assets/* (JS, CSS) and favicon
    # Extract asset URLs from HTML
    asset_urls = set()
    for m in re.finditer(r'(?:src|href)=["\']?(/assets/[^"\'>\s]+)', html):
        asset_urls.add(m.group(1))
    for m in re.finditer(r'(?:src|href)=["\']?(/[^"\'>\s/]+\.(?:svg|png|ico|jpg|webp))', html):
        asset_urls.add(m.group(1))

    for asset_path in asset_urls:
        remote_url = f'https://{slug}.lovable.app{asset_path}'
        dest = assets_dir / asset_path.lstrip('/')
        dest.parent.mkdir(parents=True, exist_ok=True)
        if download_img(remote_url, dest) > 0:
            print(f"    asset: {asset_path}")

    # Rewrite HTML: replace all image URLs with local paths
    new_html = html
    for remote, local in url_map.items():
        new_html = new_html.replace(remote, local)

    # Convert absolute paths (/images/xxx, /assets/xxx) to relative (images/xxx, assets/xxx)
    # Only for paths that exist locally
    new_html = re.sub(r'(src|href)="/(images|assets)/', r'\1="\2/', new_html)
    new_html = re.sub(r"(src|href)='/(images|assets)/", r"\1='\2/", new_html)
    # Also favicon etc at root
    new_html = re.sub(r'(href|src)="/([^/"][^"]*\.(svg|ico|png))"', r'\1="\2"', new_html)

    # Save local HTML
    (assets_dir / 'index.html').write_text(new_html, encoding='utf-8')
    print(f"  Downloaded: {len(url_map)} imgs")

    # Upload index.html
    upload_file(f'{slug}/index.html', new_html.encode('utf-8'), is_binary=False)

    # Upload all images
    uploaded = 0
    for local_rel in set(url_map.values()):
        local_path = assets_dir / local_rel
        if local_path.exists():
            r = upload_file(f'{slug}/{local_rel}', local_path.read_bytes())
            if not r.get('error'):
                uploaded += 1
    # Upload all other assets (js, css, favicon)
    uploaded_assets = 0
    for asset_path in asset_urls:
        local_asset = assets_dir / asset_path.lstrip('/')
        if local_asset.exists():
            is_text = local_asset.suffix in ('.js', '.css', '.svg', '.html')
            r = upload_file(f'{slug}/{asset_path.lstrip("/")}', local_asset.read_bytes(), is_binary=not is_text)
            if not r.get('error'):
                uploaded_assets += 1
    print(f"  Uploaded: index.html + {uploaded} imgs + {uploaded_assets} assets")

    return {
        'slug': slug,
        'url': f'https://ntics.com.br/{slug}/',
        'imgs_total': len(imgs),
        'imgs_uploaded': uploaded,
    }


async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--only', type=str, default=None, help='Single slug')
    args = ap.parse_args()

    sites = [
        'circo-no-brasil',
        'festival-de-circo',
        'museu-intinerante',
        'festivalcine',
        'programa-das-artes-literarias',
        'cultura-na-comunidade',
        'teatro-nas-escolas-objetivo-de-desenvol-sust',
    ]
    if args.only:
        sites = [args.only]

    results = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={'width': 1440, 'height': 900})
        for slug in sites:
            r = await scrape_and_migrate(page, slug)
            results.append(r)
        await browser.close()

    print('\n=== SUMMARY ===')
    for r in results:
        if r.get('error'):
            print(f"  {r['slug']}: ERROR {r['error']}")
        else:
            print(f"  {r['slug']}: {r['url']} ({r['imgs_uploaded']}/{r['imgs_total']} imgs)")


if __name__ == '__main__':
    asyncio.run(main())
