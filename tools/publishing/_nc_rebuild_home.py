"""Rebuild home principal (4206): 3 Statkraft cities instead of Itapoã+SP, + final CTA text updated.

Target section: cf9104a (cities row)
 - Column 3232af0 (Itapoã) KEPT with icon-box bc740f2
 - Column f1595bb (SP) REMOVED with icon-box 23ff8b8
 - Adds 2 new columns cloning Itapoã → Uibaí, Ibipeba (new widget ids)
 - Changes structure 20 → 30 (3 equal columns)
 - Changes each column _column_size 50 → 33.33

Final CTA text (widget 7ddcbcc): update from "Edições Anteriores" to
"Ver todas as cidades onde o programa já aconteceu →"
"""
import urllib.request, ssl, json, copy, secrets

WP = "https://negociocultural.com.br"
TOKEN = "nc_claude_8x4Kp2mZqRvTnJwL9dYsQf"
CTX = ssl.create_default_context(); CTX.check_hostname=False; CTX.verify_mode=ssl.CERT_NONE
H = {"X-WP-Token": TOKEN, "Content-Type": "application/json"}

def http(method, url, data=None):
    if data is not None and not isinstance(data, (bytes, str)):
        data = json.dumps(data, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(url, data=data, method=method, headers=H)
    with urllib.request.urlopen(req, context=CTX, timeout=60) as r:
        return json.loads(r.read()) if r.status != 204 else {}

def new_id():
    return secrets.token_hex(4)[:7]

def regen_ids(node):
    """Deep-regen all 'id' fields under a node to avoid collisions with source."""
    if isinstance(node, list):
        for x in node: regen_ids(x)
        return
    if not isinstance(node, dict): return
    if "id" in node and isinstance(node["id"], str):
        node["id"] = new_id()
    for c in (node.get("elements") or []): regen_ids(c)

def find_parent(root, target_id, parent=None, key=None, idx=None):
    """Find node with id=target_id; return (node, parent, key, idx)."""
    if isinstance(root, list):
        for i, x in enumerate(root):
            r = find_parent(x, target_id, root, None, i)
            if r: return r
        return None
    if isinstance(root, dict):
        if root.get("id") == target_id:
            return (root, parent, key, idx)
        kids = root.get("elements")
        if isinstance(kids, list):
            for i, x in enumerate(kids):
                r = find_parent(x, target_id, kids, "elements", i)
                if r: return r
    return None

# 1) Load
d = http("GET", f"{WP}/wp-json/wp/v2/pages/4206?context=edit")
el = json.loads(d["meta"]["_elementor_data"])

# 2) Grab row section and its 2 columns
row_node, row_parent, *_ = find_parent(el, "cf9104a")
# Current children: column 3232af0 (Itapoã), column f1595bb (SP)
cols = row_node["elements"]
assert len(cols) == 2, f"Expected 2 columns, got {len(cols)}"
itapoa_col = cols[0]
sp_col = cols[1]
assert itapoa_col["id"] == "3232af0"
assert sp_col["id"] == "f1595bb"

# 3) Clone Itapoã col for Uibaí and Ibipeba
def make_city_col(template, city_label, city_url):
    col = copy.deepcopy(template)
    # Regenerate ids to avoid collision with the original
    regen_ids(col)
    # Update icon-box inside (first widget of the column)
    def update_iconbox(n):
        if isinstance(n, dict) and n.get("widgetType") == "icon-box":
            s = n["settings"]
            s["title_text"] = city_label
            if "link" not in s or not isinstance(s.get("link"), dict):
                s["link"] = {}
            s["link"]["url"] = city_url
            return True
        for c in (n.get("elements") or []):
            if update_iconbox(c): return True
        return False
    update_iconbox(col)
    # Adjust column width
    col["settings"]["_column_size"] = 33
    col["settings"]["_inline_size"] = None
    return col

# Adjust Itapoã column width
itapoa_col["settings"]["_column_size"] = 33
itapoa_col["settings"]["_inline_size"] = None

uibai_col = make_city_col(itapoa_col, "Uibaí", "https://negociocultural.com.br/home-uibai/")
ibipeba_col = make_city_col(itapoa_col, "Ibipeba", "https://negociocultural.com.br/home-ibipeba/")

# 4) Replace columns: [itapoa, uibai, ibipeba]
row_node["elements"] = [itapoa_col, uibai_col, ibipeba_col]
row_node["settings"]["structure"] = "30"

# 5) Update final CTA text (widget 7ddcbcc)
cta_node, *_ = find_parent(el, "7ddcbcc")
cta_node["settings"]["editor"] = (
    '<p style="text-align: center; margin-top: 24px;">'
    '<a href="https://negociocultural.com.br/edicoes-anteriores/" '
    'style="color: rgba(255,255,255,0.7); text-decoration: underline; font-size: 13px;">'
    'Ver todas as cidades onde o programa já aconteceu →</a></p>'
)

# 6) Save
new_blob = json.dumps(el, ensure_ascii=False)
http("POST", f"{WP}/wp-json/wp/v2/pages/4206",
     {"meta": {"_elementor_data": new_blob}})

# 7) Verify
d2 = http("GET", f"{WP}/wp-json/wp/v2/pages/4206?context=edit")
blob = d2["meta"]["_elementor_data"]
checks = {
    "itapoa_present": '"title_text":"Itapoá"' in blob or '"title_text":"Itapoã"' in blob or 'Itapo' in blob,
    "uibai_present": '"title_text":"Uibaí"' in blob,
    "ibipeba_present": '"title_text":"Ibipeba"' in blob,
    "sao_paulo_gone": '"title_text":"São Paulo"' not in blob,
    "home_saopaulo_link_gone": 'home-saopaulo/' not in blob,
    "structure_30": '"structure":"30"' in blob,
    "new_cta_text": "Ver todas as cidades onde o programa já aconteceu" in blob,
    "old_cta_text_gone": blob.count("Edições Anteriores") == 0,
}
print("Verify:")
for k, v in checks.items():
    print(f"  {'OK' if v else 'FAIL'} {k}")
