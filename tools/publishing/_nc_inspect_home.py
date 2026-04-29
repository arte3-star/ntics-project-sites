"""Inspect home principal (4206) structure to map city cards and end-of-page area."""
import urllib.request, ssl, json

WP = "https://negociocultural.com.br"
TOKEN = "nc_claude_8x4Kp2mZqRvTnJwL9dYsQf"
CTX = ssl.create_default_context(); CTX.check_hostname=False; CTX.verify_mode=ssl.CERT_NONE
H = {"X-WP-Token": TOKEN}
req = urllib.request.Request(f"{WP}/wp-json/wp/v2/pages/4206?context=edit", headers=H)
d = json.loads(urllib.request.urlopen(req, context=CTX).read())
el = json.loads(d["meta"]["_elementor_data"])

print(f"Top-level sections: {len(el)}")

def summary(node, depth=0):
    if isinstance(node, list):
        for x in node: summary(x, depth)
        return
    if not isinstance(node, dict): return
    wt = node.get("widgetType") or node.get("elType")
    s = node.get("settings", {}) or {}
    tag = ""
    if wt == "heading": tag = repr(s.get("title",""))[:80]
    elif wt == "text-editor": tag = repr(s.get("editor",""))[:80]
    elif wt == "button":
        tag = repr(s.get("text","")) + " -> " + (s.get("link",{}) or {}).get("url","")
    elif wt == "image":
        tag = (s.get("image",{}) or {}).get("url","").split("/")[-1]
    print(" "*depth + f"{wt} id={node.get('id')} {tag}")
    for c in (node.get("elements") or []): summary(c, depth+2)

for i, sec in enumerate(el):
    print(f"\n==== Section [{i}] id={sec.get('id')} ====")
    summary(sec, 0)
