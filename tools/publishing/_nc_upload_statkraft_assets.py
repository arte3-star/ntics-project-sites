"""One-shot: upload Statkraft logo + régua to WP Media Library.
HISTORICAL: already executed. Assets now at SecondBrain/projetos/120-negocio-cultural-statkraft-itapoa/assets/STATKRAFT/
"""
import os, ssl, json, mimetypes, pathlib, urllib.request
from urllib.parse import quote

WP_URL = "https://negociocultural.com.br"
TOKEN = "nc_claude_8x4Kp2mZqRvTnJwL9dYsQf"
CTX = ssl.create_default_context(); CTX.check_hostname = False; CTX.verify_mode = ssl.CERT_NONE

ASSETS = [
    ("logo-statkraft.png",
     r"assets/projetos/120. NEGÓCIO CULTURAL 2ªED (STATKRAFT)/LOGO/logo Statkraft (1).png",
     "Logo Statkraft — Negócio Cultural 2ªED"),
    ("regua-statkraft.png",
     r"assets/projetos/120. NEGÓCIO CULTURAL 2ªED (STATKRAFT)/REGUAS/Régua - 120 - Statkraft@4x (1).png",
     "Régua patrocínio Statkraft — Negócio Cultural 2ªED"),
]

def upload(filename, path, title):
    data = pathlib.Path(path).read_bytes()
    mime = mimetypes.guess_type(filename)[0] or "image/png"
    req = urllib.request.Request(
        f"{WP_URL}/wp-json/wp/v2/media",
        data=data,
        method="POST",
        headers={
            "X-WP-Token": TOKEN,
            "Content-Type": mime,
            "Content-Disposition": f'attachment; filename="{filename}"',
        },
    )
    with urllib.request.urlopen(req, context=CTX, timeout=120) as r:
        res = json.loads(r.read())
    # set title
    req2 = urllib.request.Request(
        f"{WP_URL}/wp-json/wp/v2/media/{res['id']}",
        data=json.dumps({"title": title, "alt_text": title}).encode(),
        method="POST",
        headers={"X-WP-Token": TOKEN, "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req2, context=CTX, timeout=60) as r:
        res2 = json.loads(r.read())
    return {"id": res["id"], "source_url": res["source_url"], "title": res2["title"]["rendered"]}

out = {}
for fn, path, title in ASSETS:
    try:
        r = upload(fn, path, title)
        out[fn] = r
        print(f"OK {fn} -> id={r['id']} url={r['source_url']}")
    except Exception as e:
        print(f"FAIL {fn}: {e}")

pathlib.Path("tools/publishing/_nc_statkraft_media.json").write_text(json.dumps(out, indent=2))
print("saved to tools/publishing/_nc_statkraft_media.json")
