#!/usr/bin/env python3
"""
upload_ntics.py — Sobe HTML + assets de um projeto NTICS usando REST API customizado.

Uso:
  python tools/migration/upload_ntics.py --only 87
  python tools/migration/upload_ntics.py  # todos os 9
"""

import argparse
import base64
import io
import json
import ssl
import sys
import urllib.request
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = Path(__file__).resolve().parents[2]

env = dict(
    l.split('=', 1) for l in (ROOT / '.env').read_text(encoding='utf-8').splitlines()
    if '=' in l and not l.startswith('#')
)
WP_URL = env['WP_URL']
creds = base64.b64encode(f"{env['WP_USER']}:{env['WP_APP_PASSWORD']}".encode()).decode()
AUTH_HEADER = f"Basic {creds}"
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE


def upload_file(remote_path: str, local_file: Path) -> dict:
    """Upload um arquivo binary (base64) ou texto."""
    is_binary = local_file.suffix.lower() in ('.jpg', '.jpeg', '.png', '.webp', '.gif', '.mp4')
    content = local_file.read_bytes()
    if is_binary:
        content_str = base64.b64encode(content).decode('ascii')
        payload = {'path': remote_path, 'content': content_str, 'base64': True}
    else:
        content_str = content.decode('utf-8', errors='replace')
        payload = {'path': remote_path, 'content': content_str, 'base64': False}

    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(
        f"{WP_URL}/wp-json/nticsfiles/v1/write",
        data=data,
        headers={'Authorization': AUTH_HEADER, 'Content-Type': 'application/json'},
        method='POST',
    )
    try:
        r = urllib.request.urlopen(req, context=ctx, timeout=60).read()
        return json.loads(r)
    except urllib.error.HTTPError as e:
        return {'error': f'HTTP {e.code}: {e.read().decode()[:200]}'}


def upload_project(num: int, slug_override: str = None) -> dict:
    """Sobe index.html + FOTOS/ + LOGOS/ + REGUAS/ de um projeto."""
    # Find project folder
    folder = None
    for d in (ROOT / 'assets/projetos').iterdir():
        if d.name.startswith(f'{num}. '):
            folder = d
            break
    if not folder:
        return {'error': f'Project {num} folder not found'}

    # Determine remote slug (the URL path)
    # Use github_slug from sites_pendentes.json to match convention
    sites = json.loads((ROOT / 'tools/migration/sites_pendentes.json').read_text(encoding='utf-8'))
    site_info = next((s for s in sites if s['numero_ntics'] == num), None)
    if not site_info:
        return {'error': f'Site info not found for {num}'}

    # Use a clean slug for URL (remove prefix numbers)
    remote_slug = slug_override or site_info['subdomain']  # ex: exposicao-culinaria-sustentavel-imetame

    print(f"\n=== {num} {site_info['nome_planilha']} ===")
    print(f"Remote slug: /{remote_slug}/")

    # Generate index.html with LOCAL paths (not GitHub)
    # Read current HTML, replace GitHub URLs with relative paths
    html_local = (folder / 'index.html').read_text(encoding='utf-8')
    gh_base = f"https://raw.githubusercontent.com/arte3-star/ntics-project-sites/master/{site_info['github_slug']}/"
    html_local = html_local.replace(gh_base, '')  # Now uses FOTOS/, LOGOS/, REGUAS/

    # Upload index.html
    result = upload_file(f'{remote_slug}/index.html', folder / 'index.html')
    # Actually write the local-path version
    import tempfile
    with tempfile.NamedTemporaryFile('w', suffix='.html', delete=False, encoding='utf-8') as f:
        f.write(html_local)
        tmp_html = Path(f.name)
    result = upload_file(f'{remote_slug}/index.html', tmp_html)
    tmp_html.unlink()
    if result.get('error'):
        return result
    print(f"  ✓ index.html: {result.get('bytes')} bytes → {result.get('url')}")

    # Upload FOTOS/
    fotos_dir = folder / 'FOTOS'
    uploaded_fotos = 0
    if fotos_dir.exists():
        for f in fotos_dir.iterdir():
            if f.name == 'desktop.ini' or f.suffix.lower() not in ('.jpg', '.jpeg', '.png', '.webp'):
                continue
            r = upload_file(f'{remote_slug}/FOTOS/{f.name}', f)
            if not r.get('error'):
                uploaded_fotos += 1
    print(f"  ✓ FOTOS: {uploaded_fotos} uploaded")

    # Upload LOGOS/
    logos_dir = folder / 'LOGOS'
    uploaded_logos = 0
    if logos_dir.exists():
        for f in logos_dir.iterdir():
            if f.name == 'desktop.ini' or f.suffix.lower() not in ('.jpg', '.jpeg', '.png', '.webp', '.svg'):
                continue
            r = upload_file(f'{remote_slug}/LOGOS/{f.name}', f)
            if not r.get('error'):
                uploaded_logos += 1
    print(f"  ✓ LOGOS: {uploaded_logos} uploaded")

    # Upload REGUAS/
    reguas_dir = folder / 'REGUAS'
    uploaded_reguas = 0
    if reguas_dir.exists():
        for f in reguas_dir.iterdir():
            if f.name == 'desktop.ini' or f.suffix.lower() not in ('.jpg', '.jpeg', '.png', '.webp'):
                continue
            r = upload_file(f'{remote_slug}/REGUAS/{f.name}', f)
            if not r.get('error'):
                uploaded_reguas += 1
    print(f"  ✓ REGUAS: {uploaded_reguas} uploaded")

    return {
        'num': num,
        'slug': remote_slug,
        'url': f"https://ntics.com.br/{remote_slug}/",
        'fotos': uploaded_fotos,
        'logos': uploaded_logos,
        'reguas': uploaded_reguas,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--only', type=int, default=None)
    args = ap.parse_args()

    targets = [86, 106, 87, 82, 104, 91, 89, 98, 110]
    if args.only:
        targets = [args.only]

    results = []
    for num in targets:
        r = upload_project(num)
        results.append(r)

    print(f'\n=== SUMMARY ===')
    for r in results:
        if r.get('error'):
            print(f"  {r.get('num', '?')}: ERROR {r['error']}")
        else:
            print(f"  {r['num']}: {r['url']} ({r['fotos']} fotos + {r['logos']} logos + {r['reguas']} reguas)")


if __name__ == '__main__':
    main()
