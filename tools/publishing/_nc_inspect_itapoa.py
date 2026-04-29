"""Inspect home-itapoa Elementor JSON to map replacement points."""
import urllib.request, ssl, json, re

WP = "https://negociocultural.com.br"
TOKEN = "nc_claude_8x4Kp2mZqRvTnJwL9dYsQf"
CTX = ssl.create_default_context(); CTX.check_hostname=False; CTX.verify_mode=ssl.CERT_NONE
H = {"X-WP-Token": TOKEN}

req = urllib.request.Request(f"{WP}/wp-json/wp/v2/pages/4725?context=edit", headers=H)
d = json.loads(urllib.request.urlopen(req, context=CTX).read())
el = json.loads(d["meta"]["_elementor_data"])

# Walk entire tree, collect every widget with: id, widgetType, key snippets
hits = []
def walk(node, path=""):
    if isinstance(node, list):
        for i, x in enumerate(node):
            walk(x, f"{path}[{i}]")
        return
    if not isinstance(node, dict): return
    wt = node.get("widgetType") or node.get("elType")
    settings = node.get("settings", {}) or {}
    # image URLs
    img = settings.get("image", {}) if isinstance(settings.get("image"), dict) else {}
    bg = settings.get("background_image", {}) if isinstance(settings.get("background_image"), dict) else {}
    text_fields = []
    for k in ("title", "editor", "text", "heading", "caption"):
        v = settings.get(k)
        if isinstance(v, str) and v.strip():
            text_fields.append((k, v[:180]))
    urls = []
    for src in (img, bg):
        u = src.get("url") if isinstance(src, dict) else None
        if u: urls.append(u)
    if wt in ("image", "heading", "text-editor", "icon-box") or urls or text_fields:
        hits.append({
            "path": path,
            "id": node.get("id"),
            "widgetType": wt,
            "urls": urls,
            "texts": text_fields,
        })
    for child in (node.get("elements") or []):
        walk(child, f"{path}.elements")

walk(el, "root")

# Filter: just the ones that mention Itapoã/Itapoá/Porto or image URLs containing those, or image/heading widgets near sponsor section
print(f"Total widgets with content: {len(hits)}")
print("\n--- Any mention of Itapoá / Itapoã / Porto / sponsor ---")
for h in hits:
    blob = json.dumps(h, ensure_ascii=False).lower()
    if any(t in blob for t in ["itapo", "porto", "patrocinador", "regua", "régua", "patrocinio", "patrocínio"]):
        print(json.dumps(h, ensure_ascii=False, indent=2)[:800])
        print("---")

# Print all image URLs found
print("\n\n--- All image URLs in page ---")
all_urls = set()
for h in hits:
    for u in h["urls"]:
        all_urls.add(u)
for u in sorted(all_urls):
    print(u)
