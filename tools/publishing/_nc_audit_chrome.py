"""Audit header (nav menu items) and footer of every relevant page on negociocultural.com.br."""
import urllib.request, ssl, re, time, json

ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE

PAGES = [
    ("/",                                          "home principal"),
    ("/home-itapoa/",                              "Itapoá: home"),
    ("/o-programa-itapoa/",                        "Itapoá: o-programa (TRASHED?)"),
    ("/trilha-de-artes-visuais-itapoa/",           "Itapoá: trilha"),
    ("/oficinas-itapoa/",                          "Itapoá: oficinas"),
    ("/palestra-itapoa/",                          "Itapoá: palestra"),
    ("/exposicao-itapoa/",                         "Itapoá: exposição"),
    ("/home-uibai/",                               "Uibaí: home"),
    ("/trilha-de-artes-visuais-uibai/",            "Uibaí: trilha"),
    ("/oficinas-uibai/",                           "Uibaí: oficinas"),
    ("/palestra-uibai/",                           "Uibaí: palestra"),
    ("/exposicao-uibai/",                          "Uibaí: exposição"),
    ("/home-ibipeba/",                             "Ibipeba: home"),
    ("/trilha-de-artes-visuais-ibipeba/",          "Ibipeba: trilha"),
    ("/oficinas-ibipeba/",                         "Ibipeba: oficinas"),
    ("/palestra-ibipeba/",                         "Ibipeba: palestra"),
    ("/exposicao-ibipeba/",                        "Ibipeba: exposição"),
    ("/home-saopaulo/",                            "SP: home"),
    ("/o-programa-sao-paulo/",                     "SP: o-programa"),
    ("/trilha-de-artes-visuais-sao-paulo/",        "SP: trilha"),
    ("/oficinas-sao-paulo/",                       "SP: oficinas"),
    ("/palestra-sao-paulo/",                       "SP: palestra"),
    ("/exposicao-sao-paulo/",                      "SP: exposição"),
    ("/edicoes-anteriores/",                       "Edições Anteriores"),
    ("/login-ou-registro/",                        "Login/Registro"),
    ("/painel/",                                   "Painel do aluno"),
]

ts = int(time.time())
def fetch(path):
    url = f"https://negociocultural.com.br{path}?nocache={ts}"
    req = urllib.request.Request(url, headers={'Cache-Control':'no-cache','User-Agent':'Mozilla/5.0'})
    try:
        return urllib.request.urlopen(req, context=ctx, timeout=30).read().decode('utf-8','ignore'), None
    except urllib.error.HTTPError as e:
        return None, f"HTTP {e.code}"
    except Exception as e:
        return None, str(e)[:50]

def get_header_items(html):
    m = re.search(r'<ul[^>]*elementor-nav-menu[^>]*>(.*?)</ul>', html, re.DOTALL | re.I)
    if not m: return None
    items = re.findall(r'href="([^"]+)"[^>]*>\s*([^<]+?)\s*<', m.group(1))
    return [(t.strip(), h) for h, t in items if t.strip()]

def get_footer_items(html):
    # Find Navegar block
    m = re.search(r'Navegar(.*?)(?:</section>|</footer>)', html, re.DOTALL)
    if not m: return None
    blk = m.group(1)
    items = re.findall(r'href="([^"]+)"[^>]*>[^<]*<span[^>]*>([^<]+)</span>', blk)
    if not items:
        items = re.findall(r'href="([^"]+)"[^>]*>([^<]+)</a>', blk)
    return [(t.strip(), h) for h, t in items if t.strip()]

def get_template_marker(html):
    if 'elementor-location-header' not in html and 'elementor-location-footer' not in html:
        if html: return "elementor_canvas (no header/footer)"
    has_h = 'elementor-location-header' in html
    has_f = 'elementor-location-footer' in html
    return f"H={'Y' if has_h else 'N'} F={'Y' if has_f else 'N'}"

print(f"{'Path':<42} {'Page':<30} {'Chrome':<24} {'Header items':<55} {'Footer items'}")
print('-'*230)
for path, label in PAGES:
    html, err = fetch(path)
    if err:
        print(f"{path:<42} {label:<30} ERROR: {err}")
        continue
    chrome = get_template_marker(html)
    h_items = get_header_items(html)
    f_items = get_footer_items(html)
    h_str = ', '.join(t for t,_ in h_items) if h_items else '—'
    f_str = ', '.join(t for t,_ in f_items) if f_items else '—'
    print(f"{path:<42} {label:<30} {chrome:<24} {h_str[:54]:<55} {f_str}")
