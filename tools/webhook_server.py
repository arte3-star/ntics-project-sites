#!/usr/bin/env python3
"""
tools/webhook_server.py
Receives Make trigger → runs the WAT workflow via subprocess
"""

import os, sys, json, threading, subprocess
from pathlib import Path
from flask import Flask, request, jsonify

app    = Flask(__name__)
ROOT   = Path(__file__).parent.parent
SECRET = os.environ.get("WEBHOOK_SECRET", "ntics-secret-2026")
# REVIEW_MODE: when True, only classifies and creates a single review task
# instead of creating all individual tasks. Set to False when confident.
REVIEW_MODE = os.environ.get("REVIEW_MODE", "true").lower() == "true"

def run_workflow(payload: dict):
    arquivo  = payload.get("arquivo", {})
    conteudo = arquivo.get("conteudo", "")
    url      = arquivo.get("url", "")
    nome     = arquivo.get("nome", "Ata")

    # Save transcript to .tmp if content provided
    tmp = ROOT / ".tmp"
    tmp.mkdir(exist_ok=True)

    if conteudo and len(conteudo) > 100:
        (tmp / "transcript.txt").write_text(conteudo, encoding="utf-8")
        text_arg = conteudo[:200]
    else:
        text_arg = ""

    print(f"\n📥 Running WAT workflow for: {nome}")

    # Step 1: read google doc if no content
    if not text_arg and url:
        print("  📄 Step 1: Reading Google Doc...")
        subprocess.run(
            [sys.executable, "tools/read_google_doc.py", "--url", url],
            cwd=ROOT, check=False
        )

    # Step 2: classify
    print("  🤖 Step 2: Classifying...")
    subprocess.run([
        sys.executable, "tools/classify_meeting.py",
        "--text", text_arg,
        "--url", url,
        "--name", nome
    ], cwd=ROOT, check=True)

    # Load result to check type
    result_file = tmp / "meeting_result.json"
    meeting = json.loads(result_file.read_text(encoding="utf-8"))

    # Step 3: create ClickUp tasks
    if REVIEW_MODE:
        # Only create a review task with summary — don't create individual tasks
        tasks = meeting.get("tasks", [])
        task_list = "\n".join(f"  - {t['title']}" for t in tasks)
        meeting["triage"] = True
        meeting["confidence"] = meeting.get("confidence", 0)
        # Override the review context with full summary
        result_file.write_text(json.dumps(meeting, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"  🔍 Step 3: REVIEW MODE — creating review task with {len(tasks)} proposed tasks")
        subprocess.run([
            sys.executable, "tools/create_clickup_tasks.py",
            "--input", str(result_file),
            "--url", url
        ], cwd=ROOT, check=True)
    else:
        print(f"  📋 Step 3: Creating ClickUp tasks ({len(meeting.get('tasks', []))} tasks)...")
        subprocess.run([
            sys.executable, "tools/create_clickup_tasks.py",
            "--input", str(result_file),
            "--url", url
        ], cwd=ROOT, check=True)

    # Step 4: Pipedrive (SALES only, skip if key not configured)
    pipedrive_key = os.environ.get("PIPEDRIVE_API_KEY", "")
    if meeting.get("meeting_type") == "SALES" and meeting.get("confidence", 0) >= 80 and pipedrive_key:
        print("  💼 Step 4: Creating Pipedrive note...")
        subprocess.run([
            sys.executable, "tools/create_pipedrive_note.py",
            "--input", str(result_file),
            "--url", url
        ], cwd=ROOT, check=False)
    else:
        reason = "no API key" if not pipedrive_key else meeting.get('meeting_type')
        print(f"  ⭐ Step 4: Skipping Pipedrive ({reason})")

    # Step 5: learning registry
    if meeting.get("learning"):
        print("  📚 Step 5: Updating Learning Registry...")
        subprocess.run([
            sys.executable, "tools/update_learning_registry.py",
            "--learning", meeting["learning"],
            "--meeting", meeting.get("title", nome)
        ], cwd=ROOT, check=False)
    else:
        print("  ⭐ Step 5: No new learning detected")

    print(f"\n✅ Workflow complete: {nome}")
    print(f"   Type: {meeting['meeting_type']} ({meeting['confidence']}%)")
    print(f"   Tasks: {len(meeting.get('tasks', []))}")

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    if not data or data.get("secret") != SECRET:
        return jsonify({"error": "Unauthorized"}), 401

    if data.get("evento") == "teste":
        return jsonify({"ok": True, "msg": "Webhook working!"}), 200

    if data.get("evento") == "nova_ata":
        t = threading.Thread(target=run_workflow, args=(data,), daemon=True)
        t.start()
        nome = data.get("arquivo", {}).get("nome", "?")
        return jsonify({"ok": True, "msg": f"Processing: {nome}"}), 200

    return jsonify({"error": "Unknown event"}), 400

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "agent": "NTICS WAT Agent"}), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    print(f"🚀 NTICS WAT Webhook Server — port {port}")
    app.run(host="0.0.0.0", port=port)
