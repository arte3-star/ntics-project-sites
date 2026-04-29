"""Clean menu pollution + create city-specific menus and header templates for Uibaí and Ibipeba.

Steps:
1. Delete 8 polluting items from Menu Principal (id=4) and disable auto_add
2. Create menu 'menu-uibai' and 'menu-ibipeba' with 3 items each
3. Clone Elementor header template 4851 → 2 new headers, swap menu reference
4. Set Elementor display conditions on new headers (include city pages)
5. Update header 138 conditions: exclude uibai/ibipeba pages
"""
import urllib.request, ssl, json, copy, secrets, re

WP = "https://negociocultural.com.br"
TOKEN = "nc_claude_8x4Kp2mZqRvTnJwL9dYsQf"
CTX = ssl.create_default_context(); CTX.check_hostname=False; CTX.verify_mode=ssl.CERT_NONE
H = {"X-WP-Token": TOKEN, "Content-Type": "application/json"}

POLLUTING_IDS = [5001, 5002, 5004, 5006, 5008, 5009, 5011, 5013]

UIBAI_PAGES   = {"home":4986, "oficinas":4988, "palestra":4989, "exposicao":4990}
IBIPEBA_PAGES = {"home":4991, "oficinas":4993, "palestra":4994, "exposicao":4995}

COURSE_URL = f"{WP}/courses/trilha-do-conhecimento-uibai-e-ibipeba-ba/"

def http(method, url, data=None):
    if data is not None and not isinstance(data, (bytes, str)):
        data = json.dumps(data, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(url, data=data, method=method, headers=H)
    try:
        with urllib.request.urlopen(req, context=CTX, timeout=60) as r:
            body = r.read()
            return json.loads(body) if body else {}
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8','ignore')
        raise RuntimeError(f"HTTP {e.code}: {body[:400]}")

def new_id(): return secrets.token_hex(4)[:7]

# -------- Step 1: clean Menu Principal --------
print("1) Cleaning Menu Principal (id=4)...")
for mid in POLLUTING_IDS:
    try:
        r = http("DELETE", f"{WP}/wp-json/wp/v2/menu-items/{mid}?force=true")
        print(f"   deleted menu-item {mid}")
    except Exception as e:
        print(f"   skip {mid}: {e}")
# Disable auto_add
try:
    http("POST", f"{WP}/wp-json/wp/v2/menus/4", {"auto_add": False})
    print("   auto_add disabled on Menu Principal")
except Exception as e:
    print(f"   auto_add disable failed: {e}")

# -------- Step 2: create city menus --------
def create_menu(name, slug):
    r = http("POST", f"{WP}/wp-json/wp/v2/menus", {"name": name, "slug": slug})
    return r["id"]

def add_menu_item(menu_id, title, url, order):
    payload = {
        "title": title,
        "url": url,
        "menus": menu_id,
        "menu_order": order,
        "status": "publish",
        "type": "custom",
    }
    r = http("POST", f"{WP}/wp-json/wp/v2/menu-items", payload)
    return r["id"]

print("\n2) Creating city menus...")
uibai_menu_id   = create_menu("Menu Uibaí",   "menu-uibai")
ibipeba_menu_id = create_menu("Menu Ibipeba", "menu-ibipeba")
print(f"   menu-uibai: {uibai_menu_id}, menu-ibipeba: {ibipeba_menu_id}")

for menu_id, city_slug, city_label in [
    (uibai_menu_id,   "home-uibai",   "Uibaí"),
    (ibipeba_menu_id, "home-ibipeba", "Ibipeba"),
]:
    home_url = f"{WP}/{city_slug}/"
    add_menu_item(menu_id, "Home",                   home_url,                1)
    add_menu_item(menu_id, "O Programa",             home_url + "#programa",  2)
    add_menu_item(menu_id, "Trilha de Artes Visuais", COURSE_URL,              3)
    print(f"   Added 3 items to menu {menu_id} ({city_label})")

# -------- Step 3: clone header template 4851 --------
print("\n3) Cloning header template 4851 → 2 new templates...")
src = http("GET", f"{WP}/wp-json/wp/v2/elementor_library/4851?context=edit")
src_meta = src.get("meta", {})
src_data_str = src_meta["_elementor_data"]

def clone_header(title, menu_slug, include_page_ids):
    data = json.loads(src_data_str)
    # Regen all ids to avoid collisions
    def regen(n):
        if isinstance(n, list):
            for x in n: regen(x)
        elif isinstance(n, dict):
            if "id" in n and isinstance(n["id"], str):
                n["id"] = new_id()
            for c in (n.get("elements") or []): regen(c)
    regen(data)
    # Swap menu in nav-menu widget
    def swap_menu(n):
        if isinstance(n, list):
            for x in n: swap_menu(x)
        elif isinstance(n, dict):
            if n.get("widgetType") == "nav-menu":
                n.setdefault("settings", {})["menu"] = menu_slug
            for c in (n.get("elements") or []): swap_menu(c)
    swap_menu(data)

    # Conditions: include each page
    conditions = [f"include/singular/page/{pid}" for pid in include_page_ids]

    payload = {
        "title": title,
        "status": "publish",
        "template": src.get("template",""),
        "meta": {
            "_elementor_data": json.dumps(data, ensure_ascii=False),
            "_elementor_edit_mode": src_meta.get("_elementor_edit_mode","builder"),
            "_elementor_template_type": src_meta.get("_elementor_template_type","header"),
            "_elementor_page_settings": src_meta.get("_elementor_page_settings",""),
            "_elementor_conditions": conditions,
        },
    }
    r = http("POST", f"{WP}/wp-json/wp/v2/elementor_library", payload)
    return r["id"]

uibai_header_id   = clone_header("Header Uibaí",   "menu-uibai",   list(UIBAI_PAGES.values()))
ibipeba_header_id = clone_header("Header Ibipeba", "menu-ibipeba", list(IBIPEBA_PAGES.values()))
print(f"   Header Uibaí: {uibai_header_id}")
print(f"   Header Ibipeba: {ibipeba_header_id}")

# -------- Step 4: exclude uibai/ibipeba pages from default header 138 --------
print("\n4) Updating default header 138 to exclude new city pages...")
h138 = http("GET", f"{WP}/wp-json/wp/v2/elementor_library/138?context=edit")
h138_conditions = h138.get("meta", {}).get("_elementor_conditions", [])
if isinstance(h138_conditions, str):
    try: h138_conditions = json.loads(h138_conditions)
    except: pass
if not isinstance(h138_conditions, list): h138_conditions = []

new_excludes = []
for pid in list(UIBAI_PAGES.values()) + list(IBIPEBA_PAGES.values()):
    cond = f"exclude/singular/page/{pid}"
    if cond not in h138_conditions:
        new_excludes.append(cond)
        h138_conditions.append(cond)

http("POST", f"{WP}/wp-json/wp/v2/elementor_library/138",
     {"meta": {"_elementor_conditions": h138_conditions}})
print(f"   Added {len(new_excludes)} excludes to header 138")

print("\n5) Done. Flush caches to see changes.")
print(f"Summary:\n  menu-uibai={uibai_menu_id}, menu-ibipeba={ibipeba_menu_id}")
print(f"  header-uibai={uibai_header_id}, header-ibipeba={ibipeba_header_id}")
