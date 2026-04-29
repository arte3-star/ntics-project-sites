"""Update Fluent Form 3 (Formulário de Registro) dropdown 'Cidade do Participante'.
Fix RS→SC for Itapoá; add Uibaí (BA) and Ibipeba (BA); keep São Paulo (SP).
"""
import urllib.request, ssl, json

WP = "https://negociocultural.com.br"
TOKEN = "nc_claude_8x4Kp2mZqRvTnJwL9dYsQf"
CTX = ssl.create_default_context(); CTX.check_hostname=False; CTX.verify_mode=ssl.CERT_NONE
H = {"X-WP-Token": TOKEN, "Content-Type": "application/json"}

NEW_OPTS = [
    {"label": "Itapoá (SC)",  "value": "Itapoá (SC)",  "calc_value": ""},
    {"label": "São Paulo (SP)", "value": "São Paulo (SP)", "calc_value": ""},
    {"label": "Uibaí (BA)",   "value": "Uibaí (BA)",   "calc_value": ""},
    {"label": "Ibipeba (BA)", "value": "Ibipeba (BA)", "calc_value": ""},
]

def http(method, url, data=None):
    if data is not None and not isinstance(data, (bytes, str)):
        data = json.dumps(data, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(url, data=data, method=method, headers=H)
    with urllib.request.urlopen(req, context=CTX, timeout=60) as r:
        return json.loads(r.read()) if r.status != 204 else {}

d = http("GET", f"{WP}/wp-json/fluentform/v1/forms/3")
ff = json.loads(d["form_fields"])

# Navigate: fields[1] = container, columns[0].fields -> find dropdown with name dropdown_4
container = ff["fields"][1]
found = False
for col in container.get("columns", []):
    for f in col.get("fields", []):
        if f.get("element") == "select" and (f.get("attributes") or {}).get("name") == "dropdown_4":
            # Replace options, preserve other settings
            f["settings"]["advanced_options"] = NEW_OPTS
            # Keep label as-is or improve:
            f["settings"]["label"] = "Cidade do Participante"
            found = True
            print("Updated dropdown_4 with options:")
            for o in NEW_OPTS: print(f"  - {o['label']}")
            break
    if found: break

assert found, "dropdown_4 not found"

# PUT/POST back
new_form_fields = json.dumps(ff, ensure_ascii=False)
r = http("POST", f"{WP}/wp-json/fluentform/v1/forms/3",
         {"form_fields": new_form_fields})
print("\nSave response:", json.dumps(r, ensure_ascii=False)[:300])

# Verify
d2 = http("GET", f"{WP}/wp-json/fluentform/v1/forms/3")
ff2 = json.loads(d2["form_fields"])
for col in ff2["fields"][1].get("columns", []):
    for f in col.get("fields", []):
        if (f.get("attributes") or {}).get("name") == "dropdown_4":
            opts = f.get("settings", {}).get("advanced_options", [])
            print("\nVerification — current options:")
            for o in opts: print(f"  - {o.get('label')}")
