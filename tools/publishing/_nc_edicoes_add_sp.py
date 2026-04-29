"""Add São Paulo link to edicoes-anteriores page (1083) in the existing links list."""
import urllib.request, ssl, json

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

d = http("GET", f"{WP}/wp-json/wp/v2/pages/1083?context=edit")
el = json.loads(d["meta"]["_elementor_data"])

# Find widgets with editor containing the city links; look for "Camboriú" anchor
def iter_widgets(n):
    if isinstance(n, list):
        for x in n: yield from iter_widgets(x)
    elif isinstance(n, dict):
        yield n
        for c in (n.get("elements") or []): yield from iter_widgets(c)

target = None
for w in iter_widgets(el):
    if isinstance(w, dict) and w.get("widgetType") == "text-editor":
        s = w.get("settings", {}) or {}
        ed = s.get("editor", "")
        if "Camboriú" in ed and "Barra do Garças" in ed:
            target = w
            break

assert target is not None, "Could not find the cities-list widget"
old = target["settings"]["editor"]
print("Found widget id=", target["id"])
print("Len before:", len(old))

# If São Paulo already there, skip
if ">São Paulo<" in old or "home-saopaulo" in old:
    print("São Paulo already present — skipping.")
else:
    # Add São Paulo — insert as a new list item before the closing tag
    # We try to detect an <ul> or <li> pattern to keep consistency
    import re
    # Find the last </li> before the final </ul> and insert a new <li> after it.
    m = re.search(r'(<li[^>]*>.*?Barra do Garças.*?</li>)', old, re.DOTALL)
    if m:
        new_li = '<li><a href="https://negociocultural.com.br/home-saopaulo/">São Paulo</a></li>'
        new_editor = old[:m.end()] + new_li + old[m.end():]
    else:
        # Fallback: append a paragraph with the link
        new_editor = old + '<p><a href="https://negociocultural.com.br/home-saopaulo/">São Paulo</a></p>'
    target["settings"]["editor"] = new_editor
    http("POST", f"{WP}/wp-json/wp/v2/pages/1083",
         {"meta": {"_elementor_data": json.dumps(el, ensure_ascii=False)}})
    print("Updated.")

# Verify
d2 = http("GET", f"{WP}/wp-json/wp/v2/pages/1083?context=edit")
blob = d2["meta"]["_elementor_data"]
print("home-saopaulo link present:", "home-saopaulo" in blob)
print("São Paulo text present:", "São Paulo" in blob)
