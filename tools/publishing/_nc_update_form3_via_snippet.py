"""Update Fluent Form 3 dropdown cities via a one-shot PHP snippet.
Reads current form_fields from DB, parses JSON, updates advanced_options of dropdown_4,
writes back to DB, auto-deactivates.
"""
import urllib.request, ssl, json

WP = "https://negociocultural.com.br"
TOKEN = "nc_claude_8x4Kp2mZqRvTnJwL9dYsQf"
CTX = ssl.create_default_context(); CTX.check_hostname=False; CTX.verify_mode=ssl.CERT_NONE
H = {"X-WP-Token": TOKEN, "Content-Type": "application/json"}

PHP = r'''
add_action('init', function() {
    global $wpdb;
    $row = $wpdb->get_row("SELECT form_fields FROM {$wpdb->prefix}fluentform_forms WHERE id=3");
    if (!$row) { update_option('_nc_ff_log', 'form 3 not found', false); return; }
    $ff = json_decode($row->form_fields, true);
    if (!$ff) { update_option('_nc_ff_log', 'json decode fail', false); return; }
    $new_opts = [
        ['label'=>'Itapoá (SC)',  'value'=>'Itapoá (SC)',  'calc_value'=>''],
        ['label'=>'São Paulo (SP)','value'=>'São Paulo (SP)','calc_value'=>''],
        ['label'=>'Uibaí (BA)',   'value'=>'Uibaí (BA)',   'calc_value'=>''],
        ['label'=>'Ibipeba (BA)', 'value'=>'Ibipeba (BA)', 'calc_value'=>''],
    ];
    $done = false;
    if (isset($ff['fields'][1]['columns'])) {
        foreach ($ff['fields'][1]['columns'] as $ci => $col) {
            foreach ($col['fields'] as $fi => $f) {
                if (($f['attributes']['name'] ?? '') === 'dropdown_4') {
                    $ff['fields'][1]['columns'][$ci]['fields'][$fi]['settings']['advanced_options'] = $new_opts;
                    $done = true;
                }
            }
        }
    }
    if (!$done) { update_option('_nc_ff_log', 'dropdown_4 not found', false); return; }
    $encoded = json_encode($ff, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
    $updated = $wpdb->update(
        $wpdb->prefix . 'fluentform_forms',
        ['form_fields' => $encoded],
        ['id' => 3]
    );
    update_option('_nc_ff_log', 'updated='.var_export($updated, true).' bytes='.strlen($encoded), false);
    // Invalidate Fluent Forms cache if any
    wp_cache_delete('fluentform_form_3', 'fluentform');
    wp_cache_flush();
}, 999);
'''

def http(m, u, data=None):
    if data is not None and not isinstance(data, (bytes, str)):
        data = json.dumps(data, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(u, data=data, method=m, headers=H)
    with urllib.request.urlopen(req, context=CTX, timeout=60) as r:
        return json.loads(r.read()) if r.status != 204 else {}

r = http("POST", f"{WP}/wp-json/code-snippets/v1/snippets",
    {"name":"NTICS — one-shot FF3 cities","code": PHP, "scope":"global","active":True,"priority":1,"tags":["ntics","temp"]})
sid = r["id"]
print(f"Snippet {sid} created/active")

# Trigger init
urllib.request.urlopen(urllib.request.Request(f"{WP}/?_ff={sid}", headers={"Cache-Control":"no-cache"}), context=CTX).read()
# Deactivate
http("POST", f"{WP}/wp-json/code-snippets/v1/snippets/{sid}", {"active": False})
print("Snippet deactivated")

# Read log
req = urllib.request.Request(f"{WP}/wp-json/wp/v2/settings", headers=H)  # may not work for options
# Verify form state
d2 = json.loads(urllib.request.urlopen(urllib.request.Request(f"{WP}/wp-json/fluentform/v1/forms/3", headers=H), context=CTX).read())
ff2 = json.loads(d2["form_fields"])
print("\nVerification — current options:")
for col in ff2["fields"][1].get("columns", []):
    for f in col.get("fields", []):
        if (f.get("attributes") or {}).get("name") == "dropdown_4":
            for o in f.get("settings", {}).get("advanced_options", []):
                print(f"  - {o.get('label')}")
