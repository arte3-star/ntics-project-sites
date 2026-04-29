"""Find CTA buttons + 'Conheça mais' section in home-itapoa to map removal targets."""
import urllib.request, ssl, json

WP = "https://negociocultural.com.br"
TOKEN = "nc_claude_8x4Kp2mZqRvTnJwL9dYsQf"
CTX = ssl.create_default_context(); CTX.check_hostname=False; CTX.verify_mode=ssl.CERT_NONE
H = {"X-WP-Token": TOKEN}

req = urllib.request.Request(f"{WP}/wp-json/wp/v2/pages/4725?context=edit", headers=H)
d = json.loads(urllib.request.urlopen(req, context=CTX).read())
el = json.loads(d["meta"]["_elementor_data"])

# Top-level sections count and their first heading/button text
def first_texts(section):
    texts = []
    def walk(n):
        if isinstance(n, list):
            for x in n: walk(x)
            return
        if not isinstance(n, dict): return
        s = n.get("settings", {}) or {}
        wt = n.get("widgetType")
        for k in ("title","text","editor"):
            v = s.get(k)
            if isinstance(v, str) and v.strip():
                texts.append((wt, k, v[:130]))
        for c in (n.get("elements") or []): walk(c)
    walk(section)
    return texts

for i, sec in enumerate(el):
    sid = sec.get("id")
    texts = first_texts(sec)
    head = texts[0] if texts else None
    print(f"\n=== Section [{i}] id={sid} ({len(texts)} text items) ===")
    for wt, k, v in texts[:8]:
        print(f"  {wt:<14} {k:<7} {v}")

# Also find all button widgets & their texts
print("\n\n--- ALL buttons across page ---")
def walk_btns(n, path=""):
    if isinstance(n, list):
        for i, x in enumerate(n): walk_btns(x, f"{path}[{i}]")
        return
    if not isinstance(n, dict): return
    if n.get("widgetType") == "button":
        s = n.get("settings", {}) or {}
        t = s.get("text","")
        link = s.get("link",{}).get("url","") if isinstance(s.get("link"), dict) else ""
        print(f"  btn id={n.get('id')} text={t!r} link={link}")
    for c in (n.get("elements") or []): walk_btns(c, path+".elements")
walk_btns(el)
