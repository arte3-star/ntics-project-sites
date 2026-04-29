"""Remove 3 city-specific items from footer icon-list (id 7c2dee5).
Keep: Trilha de Artes Visuais, Edições Anteriores, Entrar ou Registrar.
Remove: Sobre, O Programa, Patrocinador (all pointing to /home-itapoa/#...).
"""
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

REMOVE_LABELS = {"Sobre", "O Programa", "Patrocinador"}

d = http("GET", f"{WP}/wp-json/wp/v2/elementor_library/430?context=edit")
el = json.loads(d["meta"]["_elementor_data"])

def patch(n):
    if isinstance(n, list):
        for x in n: patch(x)
        return
    if not isinstance(n, dict): return
    if n.get("widgetType") == "icon-list" and n.get("id") == "7c2dee5":
        items = n.get("settings", {}).get("icon_list", [])
        kept = [it for it in items if it.get("text") not in REMOVE_LABELS]
        print(f"Icon-list {n['id']}: {len(items)} -> {len(kept)} items")
        for it in kept: print(f"  KEEP: {it.get('text')!r} -> {(it.get('link',{}) or {}).get('url')}")
        n["settings"]["icon_list"] = kept
    for c in (n.get("elements") or []): patch(c)

patch(el)
http("POST", f"{WP}/wp-json/wp/v2/elementor_library/430",
     {"meta": {"_elementor_data": json.dumps(el, ensure_ascii=False)}})

# Verify
d2 = http("GET", f"{WP}/wp-json/wp/v2/elementor_library/430?context=edit")
blob = d2["meta"]["_elementor_data"]
checks = {
    "Sobre_gone": '"text":"Sobre"' not in blob,
    "OPrograma_gone": '"text":"O Programa"' not in blob,
    "Patrocinador_gone": '"text":"Patrocinador"' not in blob,
    "Trilha_kept": "Trilha de Artes Visuais" in blob,
    "Edicoes_kept": "Edições Anteriores" in blob,
    "Entrar_kept": "Entrar ou Registrar" in blob,
}
print("\nVerify:", checks)
print("OK" if all(checks.values()) else "PARTIAL")
