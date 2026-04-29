"""Create the 9 remaining pages (home-uibai already exists as id 4986)."""
import importlib.util, json, pathlib, urllib.error
spec = importlib.util.spec_from_file_location("nc", "tools/publishing/_nc_create_statkraft_pages.py")
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)

# Tasks remaining: all 4 subpages for uibai + all 5 pages for ibipeba
TASKS = [
    ("uibai",   ["o-programa", "oficinas", "palestra", "exposicao"]),
    ("ibipeba", ["home", "o-programa", "oficinas", "palestra", "exposicao"]),
]
city_by_slug = {c["slug"]: c for c in m.CITIES}

# Fetch sources once
sources = {k: m.fetch_source(pid) for k, pid in m.SOURCES.items()}
print("sources:", {k: s["id"] for k, s in sources.items()})

results = [{"kind":"home","city":"uibai","id":4986,"slug":"home-uibai","link":"https://negociocultural.com.br/?page_id=4986","status":"draft"}]
for city_slug, kinds in TASKS:
    city = city_by_slug[city_slug]
    print(f"\n--- {city['name']} ---")
    for kind in kinds:
        try:
            r = m.create_draft(kind, sources[kind], city)
            print(f"  OK {kind:<11} id={r['id']} slug={r['slug']}")
            results.append(r)
        except urllib.error.HTTPError as e:
            body = e.read().decode(errors='ignore')[:300]
            print(f"  FAIL {kind} {e.code}: {body}")
            results.append({"kind":kind,"city":city_slug,"error":str(e),"body":body})
        except Exception as e:
            print(f"  FAIL {kind}: {e}")
            results.append({"kind":kind,"city":city_slug,"error":str(e)})

pathlib.Path("tools/publishing/_nc_statkraft_pages.json").write_text(
    json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"\n{len([r for r in results if 'id' in r])}/10 pages created.")
