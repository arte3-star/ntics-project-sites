#!/usr/bin/env python3
"""
init_tasks_yaml_batch.py — Gera tasks.yaml mínimo para cada projeto em
SecondBrain/projetos/ que ainda não tem um.

Lê a pasta ClickUp "🟢 Projetos Ativos NTICS" (90115187061), cruza pelo
prefixo numérico com os slugs locais, e gera:

  list_projeto.id / .nome / .folder
  gmail_query  (heurístico a partir do nome da lista)
  planilhas_monitoradas: []

Uso:
    python tools/sync/init_tasks_yaml_batch.py          # preview
    python tools/sync/init_tasks_yaml_batch.py --write  # escreve os arquivos
    python tools/sync/init_tasks_yaml_batch.py --only 115-peroxidos,116-aster
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

ROOT = Path(__file__).resolve().parents[2]
SB = ROOT / "SecondBrain" / "projetos"
CLICKUP_BASE = "https://api.clickup.com/api/v2"
FOLDER_ID = "90115187061"
FOLDER_NOME = "🟢 Projetos Ativos NTICS"


def load_env() -> None:
    load_dotenv(ROOT / ".env", override=True)


def clickup_get(path: str) -> dict:
    token = os.environ.get("CLICKUP_API_KEY", "")
    if not token:
        print("[erro] CLICKUP_API_KEY não encontrada em .env", file=sys.stderr)
        sys.exit(1)
    r = requests.get(
        CLICKUP_BASE + path,
        headers={"Authorization": token, "Content-Type": "application/json"},
        timeout=30,
    )
    r.raise_for_status()
    return r.json()


def list_folder_lists(folder_id: str) -> list[dict]:
    data = clickup_get(f"/folder/{folder_id}/list")
    return [{"id": lst["id"], "name": lst["name"]} for lst in data.get("lists", [])]


def extract_num(s: str) -> str | None:
    m = re.match(r"^(\d+)[.\s]", s.strip())
    return m.group(1) if m else None


def find_slug(num: str) -> str | None:
    for child in SB.iterdir():
        if child.is_dir() and child.name.startswith(num + "-"):
            return child.name
    return None


_NOISE = re.compile(
    r"\b(projeto|ntics|gru|sp|rj|rs|sc|pr|mg|es|ba|pe|am|df|go|ms|mt|pa|pi|rn|ce|al|ap|rr|ro|to|se|ma|pb|ac|av|rua|ltda|eireli|s\.?a\.?)\b",
    re.IGNORECASE,
)
_NUM_PREFIX = re.compile(r"^\d+[.\s]*")


def gmail_query_heuristic(list_name: str) -> str:
    """Gera query Gmail a partir do nome da lista ClickUp."""
    base = _NUM_PREFIX.sub("", list_name).strip()
    tokens = re.split(r"[\s\-_/]+", base)

    # Termos longos (>= 4 chars) e não-ruído viram keywords
    keywords: list[str] = []
    for t in tokens:
        clean = re.sub(r"[^\w]", "", t).strip()
        if len(clean) >= 4 and not _NOISE.match(clean):
            keywords.append(clean)

    if not keywords:
        keywords = [t for t in tokens if len(re.sub(r"[^\w]", "", t)) >= 3]

    # subject: com as palavras mais ricas + número do projeto
    num = re.match(r"^\d+", list_name.strip())
    num_str = num.group() if num else ""

    parts = [f'subject:"{k}"' for k in keywords[:3]]
    if num_str:
        parts.append(f'subject:"{num_str}"')

    query_terms = " OR ".join(parts) if parts else f'subject:"{base}"'
    return f"({query_terms}) newer_than:7d"


YAML_TEMPLATE = """\
clickup_workspace: NTICS

list_projeto:
  id: "{list_id}"
  nome: "{list_nome}"
  folder: "{folder_nome} ({folder_id})"
  url: "https://app.clickup.com/9011929793/v/li/{list_id}"
{extras}
# Query usada pelo projeto_sync.py para puxar threads Gmail relevantes.
gmail_query: >-
  {gmail_query}

# Planilhas Drive monitoradas. Preencher quando houver.
planilhas_monitoradas: []
"""


def render_yaml(list_id: str, list_nome: str, gmail_query: str, extras: list[dict] | None = None) -> str:
    extras_block = ""
    if extras:
        lines = ["\nlistas_adicionais:"]
        for e in extras:
            lines.append(f'  - id: "{e["id"]}"')
            lines.append(f'    nome: "{e["nome"]}"')
            lines.append(f'    url: "https://app.clickup.com/9011929793/v/li/{e["id"]}"')
        extras_block = "\n".join(lines) + "\n"
    return YAML_TEMPLATE.format(
        list_id=list_id,
        list_nome=list_nome,
        folder_nome=FOLDER_NOME,
        folder_id=FOLDER_ID,
        gmail_query=gmail_query,
        extras=extras_block,
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="Escrever arquivos (sem flag = preview)")
    parser.add_argument("--only", default="", help="Slugs separados por vírgula")
    args = parser.parse_args()

    only = {s.strip() for s in args.only.split(",") if s.strip()} if args.only else set()

    load_env()

    print(f"Buscando listas da pasta {FOLDER_NOME} no ClickUp...", file=sys.stderr)
    listas = list_folder_lists(FOLDER_ID)
    print(f"  {len(listas)} listas encontradas.", file=sys.stderr)

    # slug → [lista, ...] para agrupar múltiplas listas do mesmo projeto
    slug_listas: dict[str, list[dict]] = {}

    for lst in sorted(listas, key=lambda x: x["name"]):
        num = extract_num(lst["name"])
        if not num:
            continue
        slug = find_slug(num)
        if not slug:
            print(f"  [skip] {lst['name']} — nenhum slug {num}-* em SecondBrain/projetos/", file=sys.stderr)
            continue
        if only and slug not in only:
            continue
        tasks_path = SB / slug / "tasks.yaml"
        if tasks_path.exists():
            print(f"  [ok]   {slug} — tasks.yaml já existe, pulando.", file=sys.stderr)
            continue
        slug_listas.setdefault(slug, []).append(lst)

    acoes: list[dict] = []
    for slug, lsts in sorted(slug_listas.items()):
        tasks_path = SB / slug / "tasks.yaml"
        primary = lsts[0]
        extras = [{"id": l["id"], "nome": l["name"]} for l in lsts[1:]]
        gq = gmail_query_heuristic(primary["name"])
        if extras:
            print(f"  [info] {slug} tem {len(lsts)} listas ClickUp — primary: {primary['name']!r}", file=sys.stderr)
        yaml_content = render_yaml(primary["id"], primary["name"], gq, extras or None)
        list_label = primary["name"] + (f" + {len(extras)} mais" if extras else "")
        acoes.append({"slug": slug, "path": tasks_path, "content": yaml_content, "list_name": list_label})

    if not acoes:
        print("\nNada para gerar — todos os projetos já têm tasks.yaml ou não foram encontrados localmente.")
        return

    print(f"\n{'='*60}")
    print(f"{'PREVIEW — ' if not args.write else 'ESCREVENDO — '}{len(acoes)} arquivo(s)")
    print("="*60)

    for a in acoes:
        print(f"\n--- {a['slug']} ({a['list_name']}) ---")
        print(f"Destino: {a['path']}")
        print(a["content"])

    if not args.write:
        print("="*60)
        print(f"[preview] Adicione --write para criar os {len(acoes)} arquivo(s).")
        return

    criados = 0
    for a in acoes:
        a["path"].write_text(a["content"], encoding="utf-8")
        print(f"[ok] {a['path']}", file=sys.stderr)
        criados += 1

    print(f"\n[ok] {criados} tasks.yaml criados. Rode sync_all_active.py para sincronizar.")


if __name__ == "__main__":
    main()
