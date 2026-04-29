"""Regenerate Elementor conditions cache + CSS cache via snippet."""
import urllib.request, ssl, json

WP = "https://negociocultural.com.br"
TOKEN = "nc_claude_8x4Kp2mZqRvTnJwL9dYsQf"
CTX = ssl.create_default_context(); CTX.check_hostname=False; CTX.verify_mode=ssl.CERT_NONE
H = {"X-WP-Token": TOKEN, "Content-Type": "application/json"}

PHP = r'''
add_action('init', function() {
    // Delete Elementor Pro conditions cache option
    delete_option('elementor_pro_conditions_cache');
    // Regenerate via Theme Builder if available
    if (class_exists('ElementorPro\Modules\ThemeBuilder\Module')) {
        $tb = \ElementorPro\Modules\ThemeBuilder\Module::instance();
        if (method_exists($tb, 'get_conditions_manager')) {
            $cm = $tb->get_conditions_manager();
            if (method_exists($cm, 'get_cache')) {
                $cache = $cm->get_cache();
                if (method_exists($cache, 'regenerate')) $cache->regenerate();
            }
        }
    }
    // Clear Elementor files cache (CSS)
    if (class_exists('\Elementor\Plugin')) {
        \Elementor\Plugin::$instance->files_manager->clear_cache();
    }
    // W3TC flush
    if (function_exists('w3tc_flush_all')) w3tc_flush_all();
    update_option('_nc_elementor_regen_ts', time(), false);
}, 999);
'''

def http(m, u, data=None):
    if data is not None and not isinstance(data, (bytes, str)):
        data = json.dumps(data, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(u, data=data, method=m, headers=H)
    with urllib.request.urlopen(req, context=CTX, timeout=60) as r:
        return json.loads(r.read()) if r.status != 204 else {}

r = http("POST", f"{WP}/wp-json/code-snippets/v1/snippets",
    {"name":"NTICS — regen Elementor conditions","code":PHP,"scope":"global","active":True,"priority":1,"tags":["ntics","temp"]})
sid = r["id"]; print(f"snippet {sid} active")
urllib.request.urlopen(urllib.request.Request(f"{WP}/?_regen={sid}"), context=CTX).read()
http("POST", f"{WP}/wp-json/code-snippets/v1/snippets/{sid}", {"active": False})
print("done")
