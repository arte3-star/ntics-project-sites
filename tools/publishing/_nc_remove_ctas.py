"""Remove 2 CTAs from all 3 homes + trash the 3 o-programa pages.

CTAs to remove:
- button id 33bfc44 ("Saiba mais sobre o Programa") in section [1] ("Programa Negócio Cultural") -- remove button only, keep heading+text
- Entire section id 7981eae (section [12] "Empreender é aprender: comece sua jornada agora!" + button d043135) -- remove whole CTA section

Pages to trash:
- 4743 o-programa-itapoa (LIVE)
- 4987 o-programa-uibai (draft)
- 4992 o-programa-ibipeba (draft)
"""
import urllib.request, ssl, json

WP = "https://negociocultural.com.br"
TOKEN = "nc_claude_8x4Kp2mZqRvTnJwL9dYsQf"
CTX = ssl.create_default_context(); CTX.check_hostname=False; CTX.verify_mode=ssl.CERT_NONE
H = {"X-WP-Token": TOKEN}
JSON_H = {**H, "Content-Type": "application/json"}

HOMES = [
    (4725, "home-itapoa"),
    (4986, "home-uibai"),
    (4991, "home-ibipeba"),
]
OPROGRAMA_PAGES = [
    (4743, "o-programa-itapoa"),
    (4987, "o-programa-uibai"),
    (4992, "o-programa-ibipeba"),
]

BUTTONS_TO_REMOVE = {"33bfc44"}         # Saiba mais sobre o Programa
SECTIONS_TO_REMOVE = {"7981eae"}         # Empreender é aprender + Clique aqui e acesse a trilha

def http(method, url, data=None):
    hdr = dict(JSON_H)
    if data is not None and not isinstance(data, (bytes, str)):
        data = json.dumps(data, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(url, data=data, method=method, headers=hdr)
    with urllib.request.urlopen(req, context=CTX, timeout=60) as r:
        return json.loads(r.read()) if r.status != 204 else {}

def prune(node):
    """Return node or None (if should be removed). For lists, filter out None children."""
    if isinstance(node, list):
        out = []
        for x in node:
            p = prune(x)
            if p is not None:
                out.append(p)
        return out
    if not isinstance(node, dict):
        return node
    nid = node.get("id")
    # Top-level sections or nested: check removal
    if nid in SECTIONS_TO_REMOVE:
        return None
    if node.get("widgetType") == "button" and nid in BUTTONS_TO_REMOVE:
        return None
    # Recurse into children
    kids = node.get("elements")
    if isinstance(kids, list):
        node["elements"] = [x for x in (prune(c) for c in kids) if x is not None]
    return node

def remove_ctas(pid, slug):
    d = http("GET", f"{WP}/wp-json/wp/v2/pages/{pid}?context=edit")
    el = json.loads(d["meta"]["_elementor_data"])
    el = [x for x in (prune(s) for s in el) if x is not None]
    new_blob = json.dumps(el, ensure_ascii=False)
    # Verify
    checks = {
        "section_7981eae_gone": '"id":"7981eae"' not in new_blob,
        "button_33bfc44_gone": '"id":"33bfc44"' not in new_blob,
        "button_d043135_gone_via_section": '"id":"d043135"' not in new_blob,
        "Conheca_mais_kept": "Conheça mais sobre o Negócio Cultural" in new_blob,
        "Programa_heading_kept": "Programa Negócio Cultural" in new_blob,
    }
    http("POST", f"{WP}/wp-json/wp/v2/pages/{pid}",
         {"meta": {"_elementor_data": new_blob}})
    return checks

print("1) Removing CTAs from 3 homes...")
for pid, slug in HOMES:
    try:
        c = remove_ctas(pid, slug)
        ok = all(c.values())
        print(f"   {'OK' if ok else 'PARTIAL'} {slug} ({pid}): {c}")
    except Exception as e:
        print(f"   FAIL {slug} ({pid}): {e}")

print("\n2) Trashing o-programa pages...")
for pid, slug in OPROGRAMA_PAGES:
    try:
        # Move to trash (status=trash)
        r = http("DELETE", f"{WP}/wp-json/wp/v2/pages/{pid}?force=false")
        print(f"   OK {slug} ({pid}) -> status={r.get('status', r)}")
    except Exception as e:
        print(f"   FAIL {slug} ({pid}): {e}")

print("\nDone. Clear W3 Total Cache to see on Itapoã live pages.")
