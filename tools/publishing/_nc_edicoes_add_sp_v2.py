"""Add São Paulo card to edicoes-anteriores by cloning one icon-box column from an existing row.
Adds a new row section after the last city row with a single card aligned like the grid (25% width).
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

def new_id(): return secrets.token_hex(4)[:7]

def regen_ids(node):
    if isinstance(node, list):
        for x in node: regen_ids(x)
        return
    if not isinstance(node, dict): return
    if "id" in node and isinstance(node["id"], str):
        node["id"] = new_id()
    for c in (node.get("elements") or []): regen_ids(c)

d = http("GET", f"{WP}/wp-json/wp/v2/pages/1083?context=edit")
el = json.loads(d["meta"]["_elementor_data"])

def find_node(root, nid):
    if isinstance(root, list):
        for x in root:
            r = find_node(x, nid)
            if r: return r
    elif isinstance(root, dict):
        if root.get("id") == nid: return root
        for c in (root.get("elements") or []):
            r = find_node(c, nid)
            if r: return r
    return None

# Source row with 4 icon-boxes
src_row = find_node(el, "54dd162")
assert src_row, "Source row 54dd162 not found"

# Clone entire row, keep 1 column only
new_row = copy.deepcopy(src_row)
# Keep first column only
first_col = copy.deepcopy(new_row["elements"][0])
new_row["elements"] = [first_col]
# Update structure to "10" (single column, full-width row) but keep column width at 25% so it visually aligns
new_row["settings"]["structure"] = "10"
# Column width stays 25 to align with grid above
first_col["settings"]["_column_size"] = 25
# Regen all ids
regen_ids(new_row)

# Update the icon-box inside to São Paulo
def update_iconbox(n):
    if isinstance(n, dict) and n.get("widgetType") == "icon-box":
        s = n["settings"]
        s["title_text"] = "São Paulo"
        if not isinstance(s.get("link"), dict): s["link"] = {}
        s["link"]["url"] = "https://negociocultural.com.br/home-saopaulo/"
        return True
    for c in (n.get("elements") or []):
        if update_iconbox(c): return True
    return False
update_iconbox(new_row)

# Locate target: insert after last city-row section (54dd162), before the CTA section (414abd6)
# Find top-level index of 414abd6
tl_idx = next(i for i, s in enumerate(el) if s.get("id") == "414abd6")
el.insert(tl_idx, new_row)

http("POST", f"{WP}/wp-json/wp/v2/pages/1083",
     {"meta": {"_elementor_data": json.dumps(el, ensure_ascii=False)}})

# Verify
d2 = http("GET", f"{WP}/wp-json/wp/v2/pages/1083?context=edit")
blob = d2["meta"]["_elementor_data"]
checks = {
    "sp_title": '"title_text":"S\\u00e3o Paulo"' in blob or '"title_text":"São Paulo"' in blob,
    "sp_link": "home-saopaulo" in blob,
}
print("Verify:", checks)
