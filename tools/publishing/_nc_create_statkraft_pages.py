"""Create 10 draft pages for Uibaí+Ibipeba by cloning Itapoã pages with Statkraft swaps.

Swaps applied to every duplicated page (cirurgical, regex on the JSON string):
- Logo Porto Itapoá URL -> Logo Statkraft URL (+ ID ref 4984)
- Régua Porto 94 URL    -> Régua Statkraft URL (+ ID ref 4985)
- Bio Porto Itapoá text (home only, home-itapoa root[13] text-editor id a1a3d43) -> Statkraft bio
- Page title + slug -> city-specific
- Strings 'Itapoã'/'Itapoá' in visible text -> city name (and 'Porto Itapoá' on exposicao -> 'Statkraft')

Creates pages as DRAFT. Publishing happens in a later step after user reviews.
"""
import urllib.request, ssl, json, pathlib, re, copy

WP = "https://negociocultural.com.br"
TOKEN = "nc_claude_8x4Kp2mZqRvTnJwL9dYsQf"
CTX = ssl.create_default_context(); CTX.check_hostname=False; CTX.verify_mode=ssl.CERT_NONE
H = {"X-WP-Token": TOKEN}
JSON_H = {**H, "Content-Type": "application/json"}

# From _nc_statkraft_media.json
LOGO_URL = "https://negociocultural.com.br/wp-content/uploads/2026/04/logo-statkraft.png"
LOGO_ID = 4984
REGUA_URL = "https://negociocultural.com.br/wp-content/uploads/2026/04/regua-statkraft-scaled.png"
REGUA_ID = 4985

STATKRAFT_BIO = (
    "<p>A Statkraft é uma empresa líder em energia hidrelétrica internacionalmente "
    "e a maior geradora de energia renovável da Europa. O grupo produz energia "
    "hidrelétrica, energia eólica, energia solar e energia a gás. A Statkraft é "
    "uma empresa global em operações no mercado de energia. A Statkraft tem "
    "cerca de 7.000 funcionários em mais de 20 países. No Brasil, a empresa "
    "controla ativos renováveis que somam 2,3 GW de capacidade instalada, entre "
    "operações e projetos em construção.</p>"
)

OLD_LOGO_URL = "https://negociocultural.com.br/wp-content/uploads/2025/09/Logotipo-Porto-Itapoa.png"
OLD_REGUA_URL = "https://negociocultural.com.br/wp-content/uploads/2025/09/regua-94porto.jpg"

SOURCES = {
    "home":       4725,  # home-itapoa
    "o-programa": 4743,
    "oficinas":   4767,
    "palestra":   4776,
    "exposicao":  4788,
}

CITIES = [
    {"slug": "uibai",   "name": "Uibaí",   "name_acc": "Uibaí"},
    {"slug": "ibipeba", "name": "Ibipeba", "name_acc": "Ibipeba"},
]

def http(method, url, data=None, hdrs=None):
    hdr = dict(hdrs or JSON_H)
    if data is not None and not isinstance(data, (bytes, str)):
        data = json.dumps(data, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(url, data=data, method=method, headers=hdr)
    with urllib.request.urlopen(req, context=CTX, timeout=60) as r:
        return json.loads(r.read()) if r.status != 204 else {}

def fetch_source(pid):
    d = http("GET", f"{WP}/wp-json/wp/v2/pages/{pid}?context=edit")
    return d

def swap_images(node):
    """Walk node tree, swap logo/régua image widgets in-place."""
    if isinstance(node, list):
        for x in node: swap_images(x)
        return
    if not isinstance(node, dict): return
    s = node.get("settings", {})
    if isinstance(s, dict):
        img = s.get("image")
        if isinstance(img, dict):
            u = img.get("url", "")
            if u == OLD_LOGO_URL:
                img["url"] = LOGO_URL
                img["id"] = LOGO_ID
                img["alt"] = "Logo Statkraft"
            elif u == OLD_REGUA_URL:
                img["url"] = REGUA_URL
                img["id"] = REGUA_ID
                img["alt"] = "Régua patrocínio Statkraft"
    for c in (node.get("elements") or []): swap_images(c)

def swap_home_bio(node):
    """In home page only, replace the Porto Itapoá bio text-editor widget with Statkraft bio."""
    if isinstance(node, list):
        for x in node: swap_home_bio(x)
        return
    if not isinstance(node, dict): return
    if node.get("widgetType") == "text-editor":
        s = node.get("settings", {}) or {}
        ed = s.get("editor", "")
        if "Porto Itapo" in ed:
            s["editor"] = STATKRAFT_BIO
    for c in (node.get("elements") or []): swap_home_bio(c)

def swap_exposicao_text(node):
    """Replace 'Porto Itapoá' text on exposicao page with 'Statkraft'."""
    if isinstance(node, list):
        for x in node: swap_exposicao_text(x)
        return
    if not isinstance(node, dict): return
    s = node.get("settings", {}) or {}
    if isinstance(s, dict):
        ed = s.get("editor")
        if isinstance(ed, str) and "Porto Itapoá" in ed:
            s["editor"] = ed.replace("Porto Itapoá", "Statkraft").replace("Porto Itapoã", "Statkraft")
    for c in (node.get("elements") or []): swap_exposicao_text(c)

def create_draft(kind, src_data, city):
    el = json.loads(src_data["meta"]["_elementor_data"])
    # Deep copy so we don't cross-contaminate across iterations
    el = json.loads(json.dumps(el))
    swap_images(el)
    if kind == "home":
        swap_home_bio(el)
    if kind == "exposicao":
        swap_exposicao_text(el)

    # Regenerate stable-enough widget/section ids for the duplicated page (avoid collision risk
    # in case Elementor caches by id). We suffix all 7-char hex ids with a city marker.
    # Simpler: let Elementor rebuild them by leaving ids as-is — duplication normally works.
    # We'll keep them.

    # Title by kind
    title_map = {
        "home":       f"Home {city['name']}",
        "o-programa": f"O Programa - {city['name']}",
        "oficinas":   f"Oficinas - {city['name']}",
        "palestra":   f"Palestra - {city['name']}",
        "exposicao":  f"Exposição - {city['name']}",
    }
    slug_map = {
        "home":       f"home-{city['slug']}",
        "o-programa": f"o-programa-{city['slug']}",
        "oficinas":   f"oficinas-{city['slug']}",
        "palestra":   f"palestra-{city['slug']}",
        "exposicao":  f"exposicao-{city['slug']}",
    }

    # Build meta; include other elementor meta keys to preserve template type / settings
    src_meta = src_data.get("meta", {})
    new_meta = {
        "_elementor_data": json.dumps(el, ensure_ascii=False),
        "_elementor_edit_mode": src_meta.get("_elementor_edit_mode", "builder"),
        "_elementor_template_type": src_meta.get("_elementor_template_type", "wp-page"),
        "_elementor_page_settings": src_meta.get("_elementor_page_settings", ""),
        "_elementor_conditions": src_meta.get("_elementor_conditions", ""),
    }

    payload = {
        "title": title_map[kind],
        "slug":  slug_map[kind],
        "status": "draft",
        "template": src_data.get("template") or "",
        "meta": new_meta,
    }
    r = http("POST", f"{WP}/wp-json/wp/v2/pages", payload)
    return {"kind": kind, "city": city["slug"], "id": r["id"], "slug": r["slug"], "link": r["link"], "status": r["status"]}

def main():
    # Fetch all source pages once
    sources = {k: fetch_source(pid) for k, pid in SOURCES.items()}
    print("Sources fetched:", {k: s["id"] for k, s in sources.items()})

    results = []
    for city in CITIES:
        print(f"\n--- Creating pages for {city['name']} ---")
        for kind, src in sources.items():
            try:
                r = create_draft(kind, src, city)
                print(f"  OK {kind:<11} -> id={r['id']} slug={r['slug']} status={r['status']}")
                results.append(r)
            except urllib.error.HTTPError as e:
                body = e.read().decode(errors="ignore")[:300]
                print(f"  FAIL {kind} ({e.code}): {body}")
                results.append({"kind": kind, "city": city["slug"], "error": str(e), "body": body})
            except Exception as e:
                print(f"  FAIL {kind}: {e}")
                results.append({"kind": kind, "city": city["slug"], "error": str(e)})

    pathlib.Path("tools/publishing/_nc_statkraft_pages.json").write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nSaved to tools/publishing/_nc_statkraft_pages.json — {len(results)} results")

if __name__ == "__main__":
    main()
