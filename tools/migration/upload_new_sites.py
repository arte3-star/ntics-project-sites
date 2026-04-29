"""Upload dos 6 novos sites pré-projeto para ntics.com.br.

Cada site sobe:
  {slug}/index.html (renomeado de site.html)
  {slug}/FOTOS/*.jpg
  {slug}/LOGOS/*
  {slug}/REGUAS/*

Usa o mesmo Code Snippet REST API (id=6) do upload_ntics.py.
"""
import argparse
import base64
import io
import json
import ssl
import sys
import urllib.request
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

ROOT = Path(__file__).resolve().parents[2]

env = dict(
    l.split("=", 1) for l in (ROOT / ".env").read_text(encoding="utf-8").splitlines()
    if "=" in l and not l.startswith("#")
)
WP_URL = env["WP_URL"]
creds = base64.b64encode(f"{env['WP_USER']}:{env['WP_APP_PASSWORD']}".encode()).decode()
AUTH_HEADER = f"Basic {creds}"
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE


SITES = [
    {
        "id": "116", "folder": "116. CULTURA ROBÓTICA (ÁSTER)",
        "slug": "cultura-robotica-aster",
    },
    {
        "id": "124", "folder": "124. EXPOSIÇÃO - GASTRONOMIA TAMBÉM É ARTE (COMPAGAS)",
        "slug": "gastronomia-tambem-e-arte-compagas",
    },
    {
        "id": "117", "folder": "117. TEATRO E OFICINA ROBÓTICA 4ED (WHIRLPOOL)",
        "slug": "teatro-oficina-robotica-4ed-whirlpool",
    },
    {
        "id": "119", "folder": "119. PEC EU FAÇO PARTE 2ªED (SYLVAMO)",
        "slug": "pec-eu-faco-parte-2ed-sylvamo",
    },
    {
        "id": "125", "folder": "125. EXPOSIÇÃO - GASTRONOMIA TAMBÉM É ARTE 2ED (GRU)",
        "slug": "gastronomia-tambem-e-arte-2ed-gru",
    },
    {
        "id": "127G", "folder": "127. PIE EMPREENDEDORISMO É ARTE 2ED (GRU)",
        "slug": "pie-empreendedorismo-e-arte-2ed-gru",
    },
    {
        "id": "127S", "folder": "127. PIE EMPREENDEDORISMO É ARTE 2ED (SOTREQ)",
        "slug": "pie-empreendedorismo-e-arte-2ed-sotreq",
    },
]


def upload_file(remote_path, local_file):
    is_binary = local_file.suffix.lower() in (".jpg", ".jpeg", ".png", ".webp", ".gif", ".mp4", ".svg")
    content = local_file.read_bytes()
    if is_binary:
        payload = {"path": remote_path, "content": base64.b64encode(content).decode("ascii"), "base64": True}
    else:
        payload = {"path": remote_path, "content": content.decode("utf-8", errors="replace"), "base64": False}
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        f"{WP_URL}/wp-json/nticsfiles/v1/write",
        data=data,
        headers={"Authorization": AUTH_HEADER, "Content-Type": "application/json"},
        method="POST",
    )
    try:
        r = urllib.request.urlopen(req, context=ctx, timeout=60).read()
        return json.loads(r)
    except urllib.error.HTTPError as e:
        return {"error": f"HTTP {e.code}: {e.read().decode()[:300]}"}
    except Exception as e:
        return {"error": f"{type(e).__name__}: {e}"}


def upload_site(site):
    folder = ROOT / "assets/projetos" / site["folder"]
    if not folder.exists():
        return {"error": f"folder not found: {folder}"}
    slug = site["slug"]
    print(f"\n==== [{site['id']}] {site['folder']} → /{slug}/ ====")

    # 1. HTML (site.html uploaded as index.html)
    html_path = folder / "site.html"
    if not html_path.exists():
        return {"error": f"site.html not found in {folder}"}
    r = upload_file(f"{slug}/index.html", html_path)
    if "error" in r:
        print(f"  ✗ index.html: {r['error']}")
        return r
    print(f"  ✓ index.html: {r.get('bytes','?')} bytes")

    # 2. FOTOS, LOGOS, REGUAS
    counts = {"FOTOS": 0, "LOGOS": 0, "REGUAS": 0}
    for sub in counts:
        subdir = folder / sub
        if not subdir.exists(): continue
        for f in subdir.iterdir():
            if f.name == "desktop.ini" or not f.is_file(): continue
            r = upload_file(f"{slug}/{sub}/{f.name}", f)
            if "error" in r:
                print(f"  ✗ {sub}/{f.name}: {r['error']}")
            else:
                counts[sub] += 1
    for k, v in counts.items():
        print(f"  ✓ {k}/: {v} arquivos")
    return {"ok": True, "slug": slug, "url": f"https://ntics.com.br/{slug}/", "counts": counts}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", help="ID do site (116, 117, 119, 125, 127G, 127S)")
    args = ap.parse_args()
    targets = [s for s in SITES if not args.only or s["id"] == args.only]
    results = []
    for s in targets:
        r = upload_site(s)
        results.append({"id": s["id"], **r})
    print("\n==== RESUMO ====")
    for r in results:
        if r.get("error"):
            print(f"  [{r['id']}] ERROR: {r['error']}")
        else:
            print(f"  [{r['id']}] {r['url']}")

if __name__ == "__main__":
    main()
