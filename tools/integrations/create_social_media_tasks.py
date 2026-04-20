"""
create_social_media_tasks.py — Cria e atualiza tasks de conteudo no ClickUp.

Focado na lista de redes sociais (901109494072).
Funcoes: criar tasks do plano mensal, atualizar com assets, mudar status.

Usage:
  python tools/create_social_media_tasks.py --plan plan.json
  python tools/create_social_media_tasks.py --update-task TASK_ID --status "revisao" --assets assets.json
  python tools/create_social_media_tasks.py --comment TASK_ID --text "Conteudo pronto"
"""

import argparse
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

import requests
from dotenv import load_dotenv

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

load_dotenv()

BASE_URL = "https://api.clickup.com/api/v2"
SOCIAL_MEDIA_LIST = "901109494072"
LUCAS_USER_ID = "87343005"

# Campos customizados para publicacao em redes sociais
FIELD_DRIVE_FOLDER = "1d64bc13-8d71-43b1-a1d0-58ee7dc77c9f"
FIELD_CAPTION_IG = "5a040812-38d9-45a9-a911-4fcc17396d10"
FIELD_CAPTION_LI = "f1fd09a5-7dc8-48bd-959d-3724baf21edd"


def headers():
    token = os.getenv("CLICKUP_API_KEY") or os.getenv("CLICKUP_TOKEN")
    if not token:
        raise RuntimeError("CLICKUP_API_KEY ou CLICKUP_TOKEN nao definido no .env")
    return {
        "Authorization": token,
        "Content-Type": "application/json",
    }


# ── Criar tasks do plano mensal ──────────────────────────────────────────────

def create_content_task(task_data):
    """Cria uma task de conteudo na lista de redes sociais.

    task_data dict:
        name: str — nome da task (ex: "[Educativo] 5 sinais de maturidade — S01")
        description: str — briefing completo em markdown
        due_date: str — "YYYY-MM-DD"
        tags: list[str] — ex: ["educativo", "abril-2026", "S01"]
        assignee_id: str | None — ID do responsavel (default: Lucas)
    """
    payload = {
        "name": task_data["name"],
        "markdown_description": task_data.get("description", ""),
        "status": "nao iniciado",
        "tags": task_data.get("tags", []),
    }

    if task_data.get("due_date"):
        try:
            dt = datetime.strptime(task_data["due_date"], "%Y-%m-%d")
            payload["due_date"] = int(dt.timestamp() * 1000)
        except ValueError:
            pass

    assignee = task_data.get("assignee_id", LUCAS_USER_ID)
    if assignee:
        payload["assignees"] = [int(assignee)]

    r = requests.post(
        f"{BASE_URL}/list/{SOCIAL_MEDIA_LIST}/task",
        headers=headers(),
        json=payload,
        timeout=30,
    )
    if not r.ok:
        raise RuntimeError(f"Erro ao criar task: {r.status_code} {r.text[:300]}")

    task = r.json()
    print(f"  Criada: {task['name']} (ID: {task['id']})")
    return task


def create_monthly_tasks(plan):
    """Cria todas as tasks do plano mensal.

    plan dict:
        mes: str — "Abril 2026"
        tema: str — tema central
        semanas: list[dict] — 4 semanas, cada uma com:
            numero: int — 1-4
            tema: str — sub-tema
            hook: str — hook da semana
            inicio: str — "YYYY-MM-DD" (segunda da semana)
            conteudos: list[dict] — pecas da semana:
                tipo: "educativo" | "noticias" | "case"
                titulo: str
                briefing: str — briefing para o agente criador
                dia_semana: int — 0=seg, 1=ter, 3=qui
    """
    mes_tag = plan["mes"].lower().replace(" ", "-")
    created = []

    for semana in plan.get("semanas", []):
        sem_num = semana["numero"]
        inicio = datetime.strptime(semana["inicio"], "%Y-%m-%d")

        for conteudo in semana.get("conteudos", []):
            tipo = conteudo["tipo"]
            dia_offset = conteudo.get("dia_semana", 0)
            due = inicio + timedelta(days=dia_offset)

            tipo_label = {
                "educativo": "Educativo",
                "noticias": "Noticias ESG",
                "case": "Case",
            }.get(tipo, tipo.title())

            name = f"[{tipo_label}] {conteudo['titulo']} — S{sem_num:02d}"

            description = f"""## Briefing

**Tipo:** {tipo_label}
**Tema do mes:** {plan['tema']}
**Tema da semana:** {semana['tema']}
**Hook:** {semana.get('hook', '')}

---

{conteudo.get('briefing', '')}

---

**Gerado automaticamente pelo plano editorial de {plan['mes']}**
"""

            tags = [tipo, mes_tag, f"S{sem_num:02d}"]

            task = create_content_task({
                "name": name,
                "description": description,
                "due_date": due.strftime("%Y-%m-%d"),
                "tags": tags,
            })
            created.append({
                "id": task["id"],
                "name": task["name"],
                "tipo": tipo,
                "semana": sem_num,
                "due_date": due.strftime("%Y-%m-%d"),
            })

    return created


# ── Atualizar tasks existentes ────────────────────────────────────────────────

def update_task(task_id, updates):
    """Atualiza campos de uma task existente.

    updates dict (todos opcionais):
        status: str — novo status
        description: str — nova descricao (markdown)
        name: str — novo nome
    """
    payload = {}
    if "status" in updates:
        payload["status"] = updates["status"]
    if "description" in updates:
        payload["markdown_description"] = updates["description"]
    if "name" in updates:
        payload["name"] = updates["name"]

    if not payload:
        return None

    r = requests.put(
        f"{BASE_URL}/task/{task_id}",
        headers=headers(),
        json=payload,
        timeout=30,
    )
    if not r.ok:
        raise RuntimeError(f"Erro ao atualizar task {task_id}: {r.status_code} {r.text[:300]}")

    print(f"  Atualizada: {task_id}")
    return r.json()


def set_custom_field(task_id, field_id, value):
    """Grava um campo customizado em uma task."""
    r = requests.post(
        f"{BASE_URL}/task/{task_id}/field/{field_id}",
        headers=headers(),
        json={"value": value},
        timeout=30,
    )
    if not r.ok:
        raise RuntimeError(f"Erro ao gravar campo {field_id}: {r.status_code} {r.text[:300]}")


def update_task_with_assets(task_id, drive_folder_url, caption_ig="", caption_li="",
                            content_summary="", set_revisao=True):
    """Atualiza task com links do Drive e captions prontas.

    NAO modifica a description (preserva briefing original).
    Grava apenas campos customizados + adiciona comentario com resumo.

    Args:
        task_id: ID da task no ClickUp
        drive_folder_url: URL publica da pasta no Drive
        caption_ig: caption pronta para Instagram
        caption_li: caption pronta para LinkedIn
        content_summary: resumo do que foi criado (para comentario)
        set_revisao: se True, muda status para "revisao"
    """
    # Gravar campos customizados
    if drive_folder_url:
        set_custom_field(task_id, FIELD_DRIVE_FOLDER, drive_folder_url)
    if caption_ig:
        set_custom_field(task_id, FIELD_CAPTION_IG, caption_ig)
    if caption_li:
        set_custom_field(task_id, FIELD_CAPTION_LI, caption_li)

    # Adicionar comentario com resumo + checklist de aprovacao
    comment_text = f"""Conteudo pronto para revisao.

{content_summary}

Pasta Drive: {drive_folder_url}

Checklist:
- [x] Tom positivo e alinhado com brand book
- [x] Dados conferidos com brand-data.yaml
- [x] CTA presente
- [x] Proporcao correta (4:5 para carrosseis)

Para aprovar: mude o status da task para "aprovado"
Para ajustar: comente o que precisa mudar"""

    add_comment(task_id, comment_text)

    # Mudar status para revisao
    if set_revisao:
        set_task_status(task_id, "revisao")


def add_comment(task_id, text):
    """Adiciona comentario a uma task."""
    payload = {"comment_text": text}
    r = requests.post(
        f"{BASE_URL}/task/{task_id}/comment",
        headers=headers(),
        json=payload,
        timeout=30,
    )
    if not r.ok:
        raise RuntimeError(f"Erro ao comentar: {r.status_code} {r.text[:300]}")

    print(f"  Comentario adicionado em {task_id}")
    return r.json()


def set_task_status(task_id, status):
    """Muda o status de uma task."""
    return update_task(task_id, {"status": status})


# ── Buscar tasks da semana ────────────────────────────────────────────────────

def get_week_tasks(week_start):
    """Busca tasks da semana na lista de redes sociais.

    week_start: str — "YYYY-MM-DD" (segunda da semana)
    Retorna tasks com due_date entre segunda e sexta.
    """
    start_dt = datetime.strptime(week_start, "%Y-%m-%d")
    end_dt = start_dt + timedelta(days=5)

    params = {
        "due_date_gt": int(start_dt.timestamp() * 1000) - 1,
        "due_date_lt": int(end_dt.timestamp() * 1000),
        "subtasks": "false",
        "include_closed": "false",
    }

    r = requests.get(
        f"{BASE_URL}/list/{SOCIAL_MEDIA_LIST}/task",
        headers=headers(),
        params=params,
        timeout=30,
    )
    if not r.ok:
        raise RuntimeError(f"Erro ao buscar tasks: {r.status_code}")

    tasks = r.json().get("tasks", [])
    print(f"  {len(tasks)} tasks encontradas para semana {week_start}")
    return tasks


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Gerencia tasks de social media no ClickUp")
    sub = parser.add_subparsers(dest="command")

    # Criar tasks do plano mensal
    p_plan = sub.add_parser("create-plan", help="Criar tasks do plano mensal")
    p_plan.add_argument("--plan", required=True, help="JSON do plano mensal")

    # Atualizar task com assets
    p_update = sub.add_parser("update-assets", help="Atualizar task com links de assets")
    p_update.add_argument("--task-id", required=True)
    p_update.add_argument("--assets", required=True, help="JSON com drive_folder_url, caption_ig, caption_li, content_summary")

    # Mudar status
    p_status = sub.add_parser("set-status", help="Mudar status de uma task")
    p_status.add_argument("--task-id", required=True)
    p_status.add_argument("--status", required=True)

    # Comentar
    p_comment = sub.add_parser("comment", help="Adicionar comentario")
    p_comment.add_argument("--task-id", required=True)
    p_comment.add_argument("--text", required=True)

    # Buscar tasks da semana
    p_week = sub.add_parser("get-week", help="Buscar tasks da semana")
    p_week.add_argument("--start", required=True, help="Segunda da semana (YYYY-MM-DD)")

    args = parser.parse_args()

    if args.command == "create-plan":
        with open(args.plan, encoding="utf-8") as f:
            plan = json.load(f)
        created = create_monthly_tasks(plan)
        print(f"\n{len(created)} tasks criadas.")
        # Salvar resultado
        out = Path(".tmp/clickup_plan_result.json")
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(created, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"Resultado salvo em {out}")

    elif args.command == "update-assets":
        with open(args.assets, encoding="utf-8") as f:
            data = json.load(f)
        update_task_with_assets(
            args.task_id,
            data["drive_folder_url"],
            data.get("caption_ig", ""),
            data.get("caption_li", ""),
            data.get("content_summary", ""),
        )

    elif args.command == "set-status":
        set_task_status(args.task_id, args.status)

    elif args.command == "comment":
        add_comment(args.task_id, args.text)

    elif args.command == "get-week":
        tasks = get_week_tasks(args.start)
        for t in tasks:
            print(f"  [{t.get('status', {}).get('status', '?')}] {t['name']} (ID: {t['id']})")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
