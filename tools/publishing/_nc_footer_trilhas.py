"""Replace footer Edições Anteriores + single Trilha with 3 city-specific Trilha links + Entrar."""
import urllib.request, ssl, json

WP = "https://negociocultural.com.br"
H = {"X-WP-Token": "nc_claude_8x4Kp2mZqRvTnJwL9dYsQf", "Content-Type": "application/json"}
CTX = ssl.create_default_context(); CTX.check_hostname=False; CTX.verify_mode=ssl.CERT_NONE

def http(m, u, data=None):
    if data is not None and not isinstance(data, (bytes, str)):
        data = json.dumps(data, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(u, data=data, method=m, headers=H)
    with urllib.request.urlopen(req, context=CTX, timeout=60) as r:
        return json.loads(r.read()) if r.status != 204 else {}

NEW_ITEMS = [
    {"text":"Trilha de Artes Visuais — Itapoá", "link":{"url":f"{WP}/trilha-de-artes-visuais-itapoa/","is_external":"","nofollow":""}},
    {"text":"Trilha de Artes Visuais — Uibaí",  "link":{"url":f"{WP}/trilha-de-artes-visuais-uibai/","is_external":"","nofollow":""}},
    {"text":"Trilha de Artes Visuais — Ibipeba","link":{"url":f"{WP}/trilha-de-artes-visuais-ibipeba/","is_external":"","nofollow":""}},
    {"text":"Entrar ou Registrar",              "link":{"url":f"{WP}/login-ou-registro/","is_external":"","nofollow":""}},
]

d = http("GET", f"{WP}/wp-json/wp/v2/elementor_library/430?context=edit")
el = json.loads(d["meta"]["_elementor_data"])

def patch(n):
    if isinstance(n, list):
        for x in n: patch(x)
        return
    if not isinstance(n, dict): return
    if n.get("widgetType") == "icon-list" and n.get("id") == "7c2dee5":
        # Copy icon from existing first item if present, to keep style
        existing = n["settings"].get("icon_list", [])
        template_icon = existing[0].get("selected_icon") if existing else None
        items = []
        for i, ni in enumerate(NEW_ITEMS):
            entry = {
                "text": ni["text"],
                "link": ni["link"],
                "selected_icon": template_icon or {"value":"fas fa-chevron-right","library":"fa-solid"},
                "_id": f"item{i+1:03d}",
            }
            items.append(entry)
        n["settings"]["icon_list"] = items
        print(f"Updated icon-list: {len(items)} items")
    for c in (n.get("elements") or []): patch(c)

patch(el)
http("POST", f"{WP}/wp-json/wp/v2/elementor_library/430",
     {"meta": {"_elementor_data": json.dumps(el, ensure_ascii=False)}})

# Verify
d2 = http("GET", f"{WP}/wp-json/wp/v2/elementor_library/430?context=edit")
el2 = json.loads(d2["meta"]["_elementor_data"])
def find(n, tid):
    if isinstance(n, list):
        for x in n:
            r = find(x, tid)
            if r: return r
    elif isinstance(n, dict):
        if n.get("id") == tid: return n
        for c in (n.get("elements") or []):
            r = find(c, tid)
            if r: return r
il = find(el2, "7c2dee5")
print("\nFooter now:")
for i, it in enumerate(il["settings"]["icon_list"]):
    print(f"  [{i}] {it.get('text'):<38} -> {(it.get('link',{}) or {}).get('url')}")
