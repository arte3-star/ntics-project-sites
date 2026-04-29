"""Retry lesson creation for new course 5017 using existing topic_map.
Reuses the snapshot from _nc_src_trilha_snapshot.json.
"""
import urllib.request, ssl, json, base64, pathlib

WP = "https://negociocultural.com.br"
KEY = "key_a532df9f6f818bdc2b0f9d324f57579c"
SEC = "secret_a96071db03a62551acb98beec7e922c9393b82aee19a890baa5a7a14b0be2805"
CTX = ssl.create_default_context(); CTX.check_hostname=False; CTX.verify_mode=ssl.CERT_NONE
auth = base64.b64encode(f"{KEY}:{SEC}".encode()).decode()
H = {"Authorization": f"Basic {auth}", "Content-Type": "application/json"}

mapping = json.loads(pathlib.Path("tools/publishing/_nc_trilha_mapping.json").read_text(encoding="utf-8"))
snapshot = json.loads(pathlib.Path("tools/publishing/_nc_src_trilha_snapshot.json").read_text(encoding="utf-8"))
topic_map = mapping["topic_map"]
all_lessons = snapshot["lessons"]

def http(method, url, data=None):
    if data is not None and not isinstance(data, (bytes, str)):
        data = json.dumps(data, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(url, data=data, method=method, headers=H)
    try:
        with urllib.request.urlopen(req, context=CTX, timeout=60) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="ignore")[:400]
        raise RuntimeError(f"HTTP {e.code}: {body}")

created = 0
failed = []
for old_tid, lessons in all_lessons.items():
    new_tid = topic_map[old_tid]
    for lm in lessons:
        title = lm.get("post_title") or ""
        content = lm.get("post_content") or "&nbsp;"
        payload = {
            "topic_id": new_tid,
            "lesson_title": title,
            "lesson_content": content,
            "lesson_author": 1,
        }
        try:
            r = http("POST", f"{WP}/wp-json/tutor/v1/lessons", payload)
            nid = r.get("data")
            if isinstance(nid, dict): nid = nid.get("ID") or nid.get("id")
            created += 1
            print(f"  [{created:>2}/49] topic {old_tid}->{new_tid}: {title[:55]:<57} new id={nid}")
        except Exception as e:
            failed.append({"title": title, "topic": old_tid, "error": str(e)[:300]})
            print(f"  FAIL {title[:55]}: {str(e)[:200]}")

print(f"\n=== {created}/49 created, {len(failed)} failed ===")
mapping["created_lessons"] = created
mapping["failed_lessons"] = failed
pathlib.Path("tools/publishing/_nc_trilha_mapping.json").write_text(
    json.dumps(mapping, ensure_ascii=False, indent=2), encoding="utf-8")
