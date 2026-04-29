"""Quick scan: check if Itapoã subpages have local content vs only sponsor section."""
import urllib.request, ssl, json, re

WP = "https://negociocultural.com.br"
TOKEN = "nc_claude_8x4Kp2mZqRvTnJwL9dYsQf"
CTX = ssl.create_default_context(); CTX.check_hostname=False; CTX.verify_mode=ssl.CERT_NONE
H = {"X-WP-Token": TOKEN}

PAGES = [
    (4743, "o-programa-itapoa"),
    (4767, "oficinas-itapoa"),
    (4776, "palestra-itapoa"),
    (4788, "exposicao-itapoa"),
]

def walk(node, hits):
    if isinstance(node, list):
        for x in node: walk(x, hits)
        return
    if not isinstance(node, dict): return
    settings = node.get("settings", {}) or {}
    for k in ("title", "editor", "text", "heading", "caption"):
        v = settings.get(k)
        if isinstance(v, str) and v.strip():
            hits.append((node.get("widgetType"), k, v))
    img = settings.get("image")
    bg = settings.get("background_image")
    for src in (img, bg):
        if isinstance(src, dict) and src.get("url"):
            hits.append(("image_url", "url", src["url"]))
    for c in (node.get("elements") or []): walk(c, hits)

for pid, slug in PAGES:
    req = urllib.request.Request(f"{WP}/wp-json/wp/v2/pages/{pid}?context=edit", headers=H)
    d = json.loads(urllib.request.urlopen(req, context=CTX).read())
    try:
        el = json.loads(d["meta"]["_elementor_data"])
    except Exception as e:
        print(f"\n=== {slug} (id={pid}) — no elementor data ({e})")
        continue
    hits = []
    walk(el, hits)
    print(f"\n=== {slug} (id={pid}) — {len(hits)} content items ===")
    # Count sponsor/local/generic signals
    local_hits = []
    sponsor_hits = []
    for wt, k, v in hits:
        vl = v.lower()
        if any(t in vl for t in ["itapo", "porto", "santa catarina", "patrocinador"]):
            sponsor_hits.append((wt, k, v[:120]))
        if any(t in vl for t in ["rua ", "av.", "avenida", "endereço", "endereco", "horário", "horario", "às ", "03/", "/2024", "/2025", "/2026"]):
            local_hits.append((wt, k, v[:120]))
    print(f"  Sponsor/city mentions: {len(sponsor_hits)}")
    for h in sponsor_hits[:5]: print("   S>", h)
    print(f"  Local-date/address candidates: {len(local_hits)}")
    for h in local_hits[:8]: print("   L>", h)
