#!/usr/bin/env python3
"""
tools/create_clickup_tasks.py
Creates ClickUp tasks from meeting_result.json.
Supports subtask creation when city or phase is identified.
"""

import os, sys, json, argparse, requests
from pathlib import Path
from datetime import datetime

BASE_URL = "https://api.clickup.com/api/v2"
TRIAGE_LIST = "901113425673"

def headers():
    return {
        "Authorization": os.environ["CLICKUP_API_KEY"],
        "Content-Type": "application/json"
    }

def find_parent_task(list_id: str, reference: str) -> str | None:
    """Search for a parent task by city or phase name."""
    r = requests.get(
        f"{BASE_URL}/list/{list_id}/task",
        headers=headers(),
        params={"subtasks": "false", "include_closed": "false"}
    )
    if not r.ok:
        return None

    ref_lower = reference.lower()
    best_id, best_score = None, 0

    for task in r.json().get("tasks", []):
        name = (task.get("name") or "").lower()
        score = sum(1 for word in ref_lower.split() if word in name)
        if score > best_score:
            best_score = score
            best_id = task["id"]

    return best_id if best_score > 0 else None

def priority_num(p: str) -> int:
    return {"urgent": 1, "high": 2, "normal": 3, "low": 4}.get(p, 3)

def create_task(list_id: str, task: dict, meeting: dict, file_url: str) -> dict:
    description = f"""**Reunião:** {meeting.get('title', 'Sem título')}
**Tipo:** {meeting.get('meeting_type', '?')}
**Data:** {datetime.now().strftime('%d/%m/%Y')}
**Ata:** {file_url}

**Contexto:**
{task.get('context', '')}"""

    payload = {
        "name": task["title"],
        "markdown_description": description,
        "status": "planejamento",
        "priority": priority_num(task.get("priority", "normal"))
    }

    if task.get("assignee_id"):
        payload["assignees"] = [int(task["assignee_id"])]

    if task.get("due_date"):
        try:
            dt = datetime.strptime(task["due_date"], "%Y-%m-%d")
            payload["due_date"] = int(dt.timestamp() * 1000)
        except ValueError:
            pass

    # Find parent task for subtask creation
    parent_ref = task.get("city") or task.get("phase")
    if parent_ref:
        parent_id = find_parent_task(list_id, parent_ref)
        if parent_id:
            payload["parent"] = parent_id
            print(f"     ↳ Subtask of: {parent_ref}")

    r = requests.post(
        f"{BASE_URL}/list/{list_id}/task",
        headers=headers(),
        json=payload
    )
    r.raise_for_status()
    return r.json()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default=".tmp/meeting_result.json")
    parser.add_argument("--url", default="")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        # Try relative to project root
        root = Path(__file__).parent.parent
        input_path = root / args.input

    meeting = json.loads(input_path.read_text(encoding="utf-8"))

    list_id   = meeting.get("list_id") or TRIAGE_LIST
    tasks     = meeting.get("tasks", [])
    file_url  = args.url or ""
    triage    = meeting.get("triage", False)

    if triage:
        # Create a single review task with summary of all proposed tasks
        print("⚠️  Triage/Review mode — creating review task")
        task_summary = "\n".join(
            f"- **{t['title']}** → {t.get('assignee_id', 'sem responsável')} | {t.get('priority', 'normal')} | {t.get('due_date', 'sem prazo')}"
            for t in tasks
        )
        review = {
            "title": f"📋 Revisar ata — {meeting.get('title', 'Reunião')}",
            "assignee_id": "81513300",
            "priority": "high",
            "context": f"Tipo: {meeting.get('meeting_type')} ({meeting.get('confidence')}% confiança)\nProjeto: {meeting.get('project_number', 'N/A')} → list {list_id}\n\n**{len(tasks)} tarefas propostas:**\n{task_summary}\n\n⚠️ Nenhuma tarefa foi criada automaticamente. Revise e crie manualmente ou desative REVIEW_MODE."
        }
        result = create_task(TRIAGE_LIST, review, meeting, file_url)
        print(f"✅ Review task created: {result.get('url', result.get('id'))}")
        return

    print(f"📋 Creating {len(tasks)} tasks in list {list_id}...")
    created = []

    for task in tasks:
        print(f"  • {task['title'][:60]}")
        result = create_task(list_id, task, meeting, file_url)
        created.append({
            "title": task["title"],
            "url": result.get("url", ""),
            "id": result.get("id", "")
        })
        print(f"     ✅ {result.get('url', result.get('id', '?'))}")

    # Save results
    root = Path(__file__).parent.parent
    output = root / ".tmp" / "created_tasks.json"
    output.write_text(json.dumps(created, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"\n✅ {len(created)} tasks created")
    print(f"   Output: {output}")

if __name__ == "__main__":
    main()
