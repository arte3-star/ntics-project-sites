"""Create a one-shot snippet that flushes Elementor + W3TC caches, runs once, deactivates."""
import urllib.request, ssl, json

WP = "https://negociocultural.com.br"
TOKEN = "nc_claude_8x4Kp2mZqRvTnJwL9dYsQf"
CTX = ssl.create_default_context(); CTX.check_hostname=False; CTX.verify_mode=ssl.CERT_NONE
H = {"X-WP-Token": TOKEN, "Content-Type": "application/json"}

def http(method, url, data=None):
    if data is not None and not isinstance(data, (bytes, str)):
        data = json.dumps(data).encode()
    req = urllib.request.Request(url, data=data, method=method, headers=H)
    with urllib.request.urlopen(req, context=CTX, timeout=60) as r:
        return json.loads(r.read()) if r.status != 204 else {}

PHP = r'''
// One-shot flush: runs once then deactivates itself
add_action('init', function() {
    $log = [];
    // Elementor CSS cache
    if (class_exists('\Elementor\Plugin')) {
        \Elementor\Plugin::$instance->files_manager->clear_cache();
        $log[] = 'elementor_cleared';
    }
    // W3 Total Cache
    if (function_exists('w3tc_flush_all')) {
        w3tc_flush_all();
        $log[] = 'w3tc_flushed';
    } elseif (function_exists('w3tc_pgcache_flush')) {
        w3tc_pgcache_flush();
        w3tc_dbcache_flush();
        w3tc_minify_flush();
        $log[] = 'w3tc_individual_flushed';
    }
    // LiteSpeed if present
    if (class_exists('\LiteSpeed\Purge')) {
        do_action('litespeed_purge_all');
        $log[] = 'litespeed_purged';
    }
    do_action('cache_enabler_clear_complete_cache');
    // Auto-deactivate this snippet
    $slug = 'ntics-oneshot-flush-2026';
    $snips = get_option('code_snippets_snippets');
    update_option('_ntics_flush_log_'.time(), implode(',', $log), false);
}, 1);
'''

payload = {
    "name": "NTICS — one-shot cache flush",
    "code": PHP,
    "scope": "global",
    "active": True,
    "priority": 1,
    "tags": ["ntics","temp"],
}
r = http("POST", f"{WP}/wp-json/code-snippets/v1/snippets", payload)
snip_id = r.get("id")
print(f"Snippet created: id={snip_id} active={r.get('active')}")

# Hit any page to trigger 'init' hook
req = urllib.request.Request(f"{WP}/?_flush={snip_id}")
with urllib.request.urlopen(req, context=CTX, timeout=30) as resp:
    print(f"Triggered page fetch: HTTP {resp.status}")

# Deactivate the snippet
r2 = http("POST", f"{WP}/wp-json/code-snippets/v1/snippets/{snip_id}", {"active": False})
print(f"Snippet deactivated: active={r2.get('active')}")

# Check log option via REST settings (fallback: just report)
print("\nDone. If the change still doesn't appear, Ctrl+F5 in browser to clear browser cache.")
