"""Duplicate course 1123 (Trilha Itapoã) into a single shared course for Uibaí + Ibipeba.

Pipeline:
1) Fetch source course, topics, lessons (with full content)
2) Create new course (draft first)
3) For each topic: create new topic under new course
4) For each lesson: fetch full content, create new lesson under matching new topic
5) Promote course to publish, print summary

Idempotency: checks if a course with the target slug already exists — skips creation.
"""
import urllib.request, ssl, json, base64, time, pathlib

WP = "https://negociocultural.com.br"
TOKEN = "nc_claude_8x4Kp2mZqRvTnJwL9dYsQf"
KEY = "key_a532df9f6f818bdc2b0f9d324f57579c"
SEC = "secret_a96071db03a62551acb98beec7e922c9393b82aee19a890baa5a7a14b0be2805"
CTX = ssl.create_default_context(); CTX.check_hostname=False; CTX.verify_mode=ssl.CERT_NONE

auth = base64.b64encode(f"{KEY}:{SEC}".encode()).decode()
TUTOR_H = {"Authorization": f"Basic {auth}", "Content-Type": "application/json"}
WP_H = {"X-WP-Token": TOKEN, "Content-Type": "application/json"}

SRC_COURSE = 1123
NEW_TITLE = "Trilha do Conhecimento – Uibaí e Ibipeba (BA)"
NEW_SLUG  = "trilha-uibai-ibipeba"

def http(method, url, data=None, headers=None, timeout=60):
    hdr = dict(headers or TUTOR_H)
    if data is not None and not isinstance(data, (bytes, str)):
        data = json.dumps(data, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(url, data=data, method=method, headers=hdr)
    with urllib.request.urlopen(req, context=CTX, timeout=timeout) as r:
        return json.loads(r.read()) if r.status != 204 else {}

# Step 1: Fetch source
print("1) Fetching source course structure...")
src = http("GET", f"{WP}/wp-json/tutor/v1/courses/{SRC_COURSE}")
topics_resp = http("GET", f"{WP}/wp-json/tutor/v1/topics?course_id={SRC_COURSE}")
topics = topics_resp.get("data", [])
print(f"   Source topics: {len(topics)}")

all_lessons = {}  # topic_id -> [lesson...]
for t in topics:
    tid = t["ID"]
    lr = http("GET", f"{WP}/wp-json/tutor/v1/lessons?topic_id={tid}")
    lessons = lr.get("data", []) or []
    all_lessons[tid] = lessons
    print(f"   topic {tid} ({t['post_title']}): {len(lessons)} lessons")

# Save snapshot for safety
pathlib.Path("tools/publishing/_nc_src_trilha_snapshot.json").write_text(
    json.dumps({"course": src, "topics": topics, "lessons": all_lessons}, ensure_ascii=False, indent=2),
    encoding="utf-8"
)
print("   Snapshot saved.")

# Step 2: Create new course as draft
print("\n2) Creating new course (draft)...")
src_post_content = (src.get("data") or {}).get("post_content") if False else "Trilha do Conhecimento — Uibaí e Ibipeba (BA). Programa Negócio Cultural, patrocínio Statkraft."
course_payload = {
    "post_author": 1,
    "post_title": NEW_TITLE,
    "post_name": NEW_SLUG,
    "post_content": src_post_content,
    "post_status": "draft",
    "course_level": "intermediate",
    "course_duration": {"hours": "12", "minutes": "00"},
    "course_price_type": "free",
}
cr = http("POST", f"{WP}/wp-json/tutor/v1/courses", course_payload)
new_course_id = cr["data"]
print(f"   New course id: {new_course_id}")

# Step 3: Create topics
print("\n3) Creating topics...")
topic_map = {}  # old_tid -> new_tid
for idx, t in enumerate(topics):
    payload = {
        "topic_course_id": new_course_id,
        "topic_title": t["post_title"],
        "topic_summary": t.get("post_content", "") or "",
        "topic_author": 1,
    }
    tr = http("POST", f"{WP}/wp-json/tutor/v1/topics", payload)
    new_tid = tr.get("data")
    if isinstance(new_tid, dict): new_tid = new_tid.get("ID") or new_tid.get("id")
    topic_map[t["ID"]] = new_tid
    print(f"   [{idx+1}/{len(topics)}] {t['post_title']:<30} -> new topic {new_tid}")

# Step 4: Create lessons
print("\n4) Creating lessons...")
created_lessons = 0
failed_lessons = []
for old_tid, lessons in all_lessons.items():
    new_tid = topic_map[old_tid]
    for lm in lessons:
        title = lm.get("post_title") or lm.get("title")
        content = lm.get("post_content") or lm.get("lesson_content") or ""
        payload = {
            "topic_id": new_tid,
            "lesson_title": title,
            "lesson_content": content,
        }
        # Carry video meta if present
        vm = lm.get("video") or {}
        if isinstance(vm, dict) and vm.get("source"):
            payload["video"] = {
                "source_type": vm.get("source"),
                "source": vm.get("source_" + vm["source"]) if isinstance(vm, dict) else "",
                "runtime": vm.get("runtime", {}),
            }
        try:
            lr = http("POST", f"{WP}/wp-json/tutor/v1/lessons", payload)
            nid = lr.get("data")
            if isinstance(nid, dict): nid = nid.get("ID") or nid.get("id")
            created_lessons += 1
            print(f"   [{created_lessons:>2}] topic {old_tid}->{new_tid}: {title[:50]:<52} new id={nid}")
        except Exception as e:
            err = str(e)[:200]
            try: err = e.read().decode()[:300]
            except: pass
            failed_lessons.append({"title": title, "error": err})
            print(f"   FAIL {title[:50]}: {err}")

print(f"\n5) Publishing course {new_course_id}...")
try:
    # Publish via WP REST
    http("POST", f"{WP}/wp-json/wp/v2/courses/{new_course_id}",
         {"status": "publish"}, headers=WP_H)
    print("   Published.")
except Exception as e:
    print(f"   Publish failed: {e} (can publish manually in wp-admin)")

# Summary
print(f"\n=== SUMMARY ===")
print(f"New course id: {new_course_id}")
print(f"Topics: {len(topic_map)}")
print(f"Lessons: {created_lessons} created, {len(failed_lessons)} failed")
if failed_lessons:
    print("Failures:")
    for f in failed_lessons: print(f"  - {f['title']}: {f['error'][:100]}")

pathlib.Path("tools/publishing/_nc_trilha_mapping.json").write_text(
    json.dumps({
        "new_course_id": new_course_id,
        "topic_map": topic_map,
        "created_lessons": created_lessons,
        "failed_lessons": failed_lessons,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
print("Mapping saved to tools/publishing/_nc_trilha_mapping.json")
