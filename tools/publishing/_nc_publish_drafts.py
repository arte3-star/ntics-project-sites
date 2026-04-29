"""Publish the 8 remaining drafts (2 homes + 6 subpages for Uibaí and Ibipeba)."""
import urllib.request, ssl, json

WP = "https://negociocultural.com.br"
TOKEN = "nc_claude_8x4Kp2mZqRvTnJwL9dYsQf"
CTX = ssl.create_default_context(); CTX.check_hostname=False; CTX.verify_mode=ssl.CERT_NONE
H = {"X-WP-Token": TOKEN, "Content-Type": "application/json"}

DRAFTS = [
    (4986, "home-uibai"),
    (4988, "oficinas-uibai"),
    (4989, "palestra-uibai"),
    (4990, "exposicao-uibai"),
    (4991, "home-ibipeba"),
    (4993, "oficinas-ibipeba"),
    (4994, "palestra-ibipeba"),
    (4995, "exposicao-ibipeba"),
]

def http(method, url, data=None):
    if data is not None and not isinstance(data, (bytes, str)):
        data = json.dumps(data).encode()
    req = urllib.request.Request(url, data=data, method=method, headers=H)
    with urllib.request.urlopen(req, context=CTX, timeout=60) as r:
        return json.loads(r.read()) if r.status != 204 else {}

for pid, slug in DRAFTS:
    try:
        r = http("POST", f"{WP}/wp-json/wp/v2/pages/{pid}", {"status": "publish"})
        print(f"  OK {slug:<20} ({pid}) -> {r['status']} @ {r['link']}")
    except Exception as e:
        print(f"  FAIL {slug} ({pid}): {e}")
