"""Single test: create only home-uibai draft, then inspect it."""
import importlib.util, sys, json
spec = importlib.util.spec_from_file_location("nc", "tools/publishing/_nc_create_statkraft_pages.py")
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)

src = m.fetch_source(m.SOURCES["home"])
city = m.CITIES[0]  # uibai
r = m.create_draft("home", src, city)
print("Created:", json.dumps(r, indent=2, ensure_ascii=False))

# Verify: fetch back and check swaps applied
import urllib.request, ssl, json as J
d = m.http("GET", f"{m.WP}/wp-json/wp/v2/pages/{r['id']}?context=edit")
el = J.loads(d["meta"]["_elementor_data"])

# Find swaps
import re
blob = J.dumps(el, ensure_ascii=False)
checks = {
    "logo_statkraft_present": m.LOGO_URL in blob,
    "regua_statkraft_present": m.REGUA_URL in blob,
    "old_logo_gone": m.OLD_LOGO_URL not in blob,
    "old_regua_gone": m.OLD_REGUA_URL not in blob,
    "statkraft_bio_present": "Statkraft é uma empresa líder" in blob,
    "old_porto_bio_gone": "Porto Itapoã iniciou suas operações" not in blob,
}
print("\nVerification:")
for k, v in checks.items():
    mark = "OK " if v else "FAIL"
    print(f"  {mark} {k}")

print(f"\nDraft URL (preview): {r['link']}")
print(f"Admin edit URL: {m.WP}/wp-admin/post.php?post={r['id']}&action=elementor")
