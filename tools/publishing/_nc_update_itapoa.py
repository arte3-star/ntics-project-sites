"""Update existing Itapoã pages: new Porto Itapoá bio + new régua image.
HISTORICAL: already executed. Assets now at SecondBrain/projetos/120-negocio-cultural-statkraft-itapoa/assets/PORTO-ITAPOA/
"""
import urllib.request, ssl, json, mimetypes, pathlib

WP = "https://negociocultural.com.br"
TOKEN = "nc_claude_8x4Kp2mZqRvTnJwL9dYsQf"
CTX = ssl.create_default_context(); CTX.check_hostname=False; CTX.verify_mode=ssl.CERT_NONE
H = {"X-WP-Token": TOKEN}
JSON_H = {**H, "Content-Type": "application/json"}

OLD_REGUA_URL = "https://negociocultural.com.br/wp-content/uploads/2025/09/regua-94porto.jpg"

NEW_BIO = (
    "<p>O Porto Itapoá iniciou suas operações em junho de 2011 e é considerado um dos "
    "terminais mais ágeis e eficientes da América Latina e um dos maiores e mais "
    "importantes do País na movimentação de cargas conteinerizadas, segundo a Agência "
    "Nacional de Transportes Aquaviários (ANTAQ). Localizado no Litoral Norte de Santa "
    "Catarina, o Porto Itapoá está posicionado entre as regiões mais produtivas do "
    "Brasil, contemplando importadores e exportadores de diversos segmentos empresariais.</p>"
    "<p>Sua localização privilegiada, na Baía da Babitonga, proporciona condições seguras "
    "e facilitadas para a atracação dos navios. Com águas calmas e profundas, a Babitonga "
    "é ideal para receber embarcações de grande porte, uma tendência cada vez mais adotada "
    "na navegação mundial.</p>"
    "<h4>Terceiro maior porto do Brasil</h4>"
    "<p>O Porto Itapoá encerrou 2025 com um marco histórico ao alcançar a movimentação de "
    "1,5 milhão de TEUs, atingindo a meta estabelecida para o ano e consolidando sua "
    "posição entre os principais e, hoje, o terceiro maior porto do Brasil em movimentação "
    "de contêineres.</p>"
    "<p>A trajetória de crescimento tende a se intensificar nos próximos anos com uma nova "
    "fase de expansão do Porto Itapoá, que prevê investimentos de R$ 500 milhões. O projeto "
    "contempla a ampliação de 120 mil metros quadrados de pátio, sendo 60 mil m² entregues "
    "no primeiro trimestre de 2026 e os outros 60 mil m² concluídos até o fim do mesmo ano, "
    "ampliando de forma significativa a capacidade operacional do terminal.</p>"
)

REGUA_FILE = pathlib.Path(r"assets/projetos/120. NEGÓCIO CULTURAL 2ªED (PORTO ITAPOÁ)/REGUAS/Régua - 120 - Itapoa (1).png")

def http(method, url, data=None, hdrs=None):
    hdr = dict(hdrs or JSON_H)
    if data is not None and not isinstance(data, (bytes, str)):
        data = json.dumps(data, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(url, data=data, method=method, headers=hdr)
    with urllib.request.urlopen(req, context=CTX, timeout=120) as r:
        return json.loads(r.read()) if r.status != 204 else {}

def upload(filename, path, title):
    data = pathlib.Path(path).read_bytes()
    mime = mimetypes.guess_type(filename)[0] or "image/png"
    req = urllib.request.Request(
        f"{WP}/wp-json/wp/v2/media",
        data=data, method="POST",
        headers={"X-WP-Token": TOKEN, "Content-Type": mime,
                 "Content-Disposition": f'attachment; filename="{filename}"'},
    )
    with urllib.request.urlopen(req, context=CTX, timeout=120) as r:
        res = json.loads(r.read())
    http("POST", f"{WP}/wp-json/wp/v2/media/{res['id']}",
         {"title": title, "alt_text": title})
    return {"id": res["id"], "source_url": res["source_url"]}

# 1) Upload new régua
print("1) Uploading new Porto Itapoá régua...")
r = upload("regua-itapoa-2026.png", REGUA_FILE, "Régua patrocínio Porto Itapoá — Negócio Cultural 2ªED")
NEW_REGUA_URL = r["source_url"]; NEW_REGUA_ID = r["id"]
print(f"   OK id={NEW_REGUA_ID} url={NEW_REGUA_URL}")

# 2) Page updaters
def swap_regua(node):
    if isinstance(node, list):
        for x in node: swap_regua(x)
        return
    if not isinstance(node, dict): return
    s = node.get("settings", {})
    if isinstance(s, dict):
        img = s.get("image")
        if isinstance(img, dict) and img.get("url") == OLD_REGUA_URL:
            img["url"] = NEW_REGUA_URL
            img["id"] = NEW_REGUA_ID
            img["alt"] = "Régua patrocínio Porto Itapoá"
    for c in (node.get("elements") or []): swap_regua(c)

def swap_bio(node):
    if isinstance(node, list):
        for x in node: swap_bio(x)
        return
    if not isinstance(node, dict): return
    if node.get("widgetType") == "text-editor":
        s = node.get("settings", {}) or {}
        ed = s.get("editor", "")
        if "Porto Itapoá iniciou suas operações em junho de 2011" in ed:
            s["editor"] = NEW_BIO
    for c in (node.get("elements") or []): swap_bio(c)

def update_page(pid, do_bio=False):
    d = http("GET", f"{WP}/wp-json/wp/v2/pages/{pid}?context=edit")
    el = json.loads(d["meta"]["_elementor_data"])
    swap_regua(el)
    if do_bio:
        swap_bio(el)
    meta = {"_elementor_data": json.dumps(el, ensure_ascii=False)}
    http("POST", f"{WP}/wp-json/wp/v2/pages/{pid}", {"meta": meta})
    # verify
    d2 = http("GET", f"{WP}/wp-json/wp/v2/pages/{pid}?context=edit")
    blob = d2["meta"]["_elementor_data"]
    checks = {
        "new_regua_present": NEW_REGUA_URL in blob,
        "old_regua_gone": OLD_REGUA_URL not in blob,
    }
    if do_bio:
        checks["new_bio_present"] = "1,5 milhão de TEUs" in blob
        checks["old_bio_gone"] = "sustentáveis da América Latina" not in blob
    return checks

# 3) Run updates
PAGES = [
    (4725, "home-itapoa",       True),
    (4743, "o-programa-itapoa", False),
    (4767, "oficinas-itapoa",   False),
    (4776, "palestra-itapoa",   False),
    (4788, "exposicao-itapoa",  False),
]
print("\n2) Updating pages...")
for pid, slug, do_bio in PAGES:
    try:
        c = update_page(pid, do_bio)
        mark = "OK" if all(c.values()) else "PARTIAL"
        print(f"   {mark} {slug} ({pid}) -> {c}")
    except Exception as e:
        print(f"   FAIL {slug} ({pid}): {e}")

print("\nDone. Remember to clear W3 Total Cache.")
