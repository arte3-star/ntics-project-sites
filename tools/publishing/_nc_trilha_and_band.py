"""Two tasks:
A) Clone page 4253 (trilha-de-artes-visuais-itapoa) for Uibaí and Ibipeba, swap régua.
   Then update menu-uibai and menu-ibipeba to point 'Trilha de Artes Visuais' to the new pages.
B) Remove the top band (first section) from all 4 headers: 4851, 5082, 5083, 138.
"""
import urllib.request, ssl, json, copy, secrets

WP = "https://negociocultural.com.br"
TOKEN = "nc_claude_8x4Kp2mZqRvTnJwL9dYsQf"
CTX = ssl.create_default_context(); CTX.check_hostname=False; CTX.verify_mode=ssl.CERT_NONE
H = {"X-WP-Token": TOKEN, "Content-Type": "application/json"}

OLD_REGUA = "https://negociocultural.com.br/wp-content/uploads/2025/09/regua-94porto.jpg"
NEW_REGUA_URL = "https://negociocultural.com.br/wp-content/uploads/2026/04/regua-statkraft-scaled.png"
NEW_REGUA_ID = 4985

def new_id(): return secrets.token_hex(4)[:7]

def http(method, url, data=None):
    if data is not None and not isinstance(data, (bytes, str)):
        data = json.dumps(data, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(url, data=data, method=method, headers=H)
    try:
        with urllib.request.urlopen(req, context=CTX, timeout=60) as r:
            body = r.read()
            return json.loads(body) if body else {}
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"HTTP {e.code}: {e.read().decode('utf-8','ignore')[:400]}")

# ========== A) Clone trilha-de-artes-visuais-itapoa ==========
print("A) Cloning trilha-de-artes-visuais-itapoa (4253)...")
src = http("GET", f"{WP}/wp-json/wp/v2/pages/4253?context=edit")
src_meta = src["meta"]
src_data = json.loads(src_meta["_elementor_data"])

def swap_regua(node):
    if isinstance(node, list):
        for x in node: swap_regua(x)
        return
    if not isinstance(node, dict): return
    s = node.get("settings", {}) or {}
    img = s.get("image") if isinstance(s, dict) else None
    if isinstance(img, dict) and img.get("url") == OLD_REGUA:
        img["url"] = NEW_REGUA_URL
        img["id"] = NEW_REGUA_ID
        img["alt"] = "Régua patrocínio Statkraft"
    for c in (node.get("elements") or []): swap_regua(c)

def regen_ids(n):
    if isinstance(n, list):
        for x in n: regen_ids(x)
    elif isinstance(n, dict):
        if "id" in n and isinstance(n["id"], str): n["id"] = new_id()
        for c in (n.get("elements") or []): regen_ids(c)

CITIES = [
    ("uibai",   "Uibaí",   20),   # menu id
    ("ibipeba", "Ibipeba", 21),
]

created_pages = {}
for city_slug, city_label, menu_id in CITIES:
    data = copy.deepcopy(src_data)
    swap_regua(data)
    # regen ids to avoid collisions
    regen_ids(data)
    payload = {
        "title": f"Trilha de Artes Visuais – {city_label}",
        "slug": f"trilha-de-artes-visuais-{city_slug}",
        "status": "publish",
        "template": src.get("template",""),
        "meta": {
            "_elementor_data": json.dumps(data, ensure_ascii=False),
            "_elementor_edit_mode": src_meta.get("_elementor_edit_mode","builder"),
            "_elementor_template_type": src_meta.get("_elementor_template_type","wp-page"),
            "_elementor_page_settings": src_meta.get("_elementor_page_settings",""),
            "_elementor_conditions": src_meta.get("_elementor_conditions",""),
        },
    }
    r = http("POST", f"{WP}/wp-json/wp/v2/pages", payload)
    created_pages[city_slug] = {"id": r["id"], "slug": r["slug"], "link": r["link"]}
    print(f"   created page {r['id']}: {r['slug']} -> {r['link']}")

# ========== Update menu items ==========
print("\nUpdating menu items to point Trilha -> new city page...")
for city_slug, city_label, menu_id in CITIES:
    # Find the "Trilha de Artes Visuais" item in this menu
    items = http("GET", f"{WP}/wp-json/wp/v2/menu-items?menus={menu_id}&per_page=20")
    target = next((it for it in items if "Trilha" in (it["title"]["rendered"] if isinstance(it["title"], dict) else it["title"])), None)
    if target:
        new_url = created_pages[city_slug]["link"]
        http("POST", f"{WP}/wp-json/wp/v2/menu-items/{target['id']}", {"url": new_url})
        print(f"   menu {menu_id} item {target['id']} -> {new_url}")

# Also include new pages in their respective headers
print("\nAdding new pages to header conditions...")
for header_id, city_slug in [(5082,"uibai"),(5083,"ibipeba")]:
    h = http("GET", f"{WP}/wp-json/wp/v2/elementor_library/{header_id}?context=edit")
    conds = h.get("meta",{}).get("_elementor_conditions",[]) or []
    if not isinstance(conds, list): conds = []
    new_cond = f"include/singular/page/{created_pages[city_slug]['id']}"
    if new_cond not in conds:
        conds.append(new_cond)
        http("POST", f"{WP}/wp-json/wp/v2/elementor_library/{header_id}",
             {"meta": {"_elementor_conditions": conds}})
        print(f"   header {header_id}: added {new_cond}")

# Also exclude new pages from header 138
h138 = http("GET", f"{WP}/wp-json/wp/v2/elementor_library/138?context=edit")
conds138 = h138.get("meta",{}).get("_elementor_conditions",[]) or []
if not isinstance(conds138, list): conds138 = []
for city_slug, info in created_pages.items():
    cond = f"exclude/singular/page/{info['id']}"
    if cond not in conds138: conds138.append(cond)
http("POST", f"{WP}/wp-json/wp/v2/elementor_library/138",
     {"meta": {"_elementor_conditions": conds138}})
print("   header 138: excludes updated")

# ========== B) Remove top band from all 4 headers ==========
print("\nB) Removing top band section from all 4 headers...")
BAND_SECTIONS = {
    4851: "f8ac630",
    5082: "5aca107",
    5083: "0762614",
    138:  "08902c3",
}
for hid, sec_id in BAND_SECTIONS.items():
    d = http("GET", f"{WP}/wp-json/wp/v2/elementor_library/{hid}?context=edit")
    el = json.loads(d["meta"]["_elementor_data"])
    before = len(el)
    el = [s for s in el if s.get("id") != sec_id]
    after = len(el)
    if before == after:
        print(f"   header {hid}: section {sec_id} not found, skipping")
        continue
    http("POST", f"{WP}/wp-json/wp/v2/elementor_library/{hid}",
         {"meta": {"_elementor_data": json.dumps(el, ensure_ascii=False)}})
    print(f"   header {hid}: removed section {sec_id} ({before} -> {after} sections)")

print("\nDone. Now flush Elementor caches.")
