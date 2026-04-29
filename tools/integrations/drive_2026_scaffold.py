"""
drive_2026_scaffold.py - Cria estrutura padrão em Marketing/2026 (idempotente).

Estrutura:
  1. REDES SOCIAIS/
    CARROSSEIS/ (CASES, NOTICIAS, EDUCATIVOS, CLIENTES)
    POSTS/
    STORIES/
    REELS/
  2. WEBSITE/
    ARTIGOS BLOG/
    LANDING PAGES/
  3. EMAIL/
    NEWSLETTERS/
  4. VIDEOS/
    CASES/
    PRE-PROJETO/
    INSTITUCIONAL/
  5. IMPRESSOS/
  6. APRESENTACOES/
  _ARQUIVO/

Usage:
  python tools/integrations/drive_2026_scaffold.py
  python tools/integrations/drive_2026_scaffold.py --dry-run
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from upload_to_drive import get_drive_service, get_or_create_folder  # noqa: E402

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

ROOT_2026 = "1mOX2HbTfM30WV1umXOu4gfrYV5WZdJEU"
MAP_PATH = Path("G:/O meu disco/AUTOMAÇÕES/.tmp/drive_2026_folder_map.json")

STRUCTURE = {
    "1. REDES SOCIAIS": {
        "CARROSSEIS": ["CASES", "NOTICIAS", "EDUCATIVOS", "CLIENTES"],
        "POSTS": [],
        "STORIES": [],
        "REELS": [],
    },
    "2. WEBSITE": {
        "ARTIGOS BLOG": [],
        "LANDING PAGES": [],
    },
    "3. EMAIL": {
        "NEWSLETTERS": [],
    },
    "4. VIDEOS": {
        "CASES": [],
        "PRE-PROJETO": [],
        "INSTITUCIONAL": [],
    },
    "5. IMPRESSOS": {},
    "6. APRESENTACOES": {},
    "7. DESIGN ASSETS": {
        "ASSINATURAS": [],
        "FRAMES": [],
        "ICONES": [],
        "REGUAS": [],
    },
    "_ARQUIVO": {},
}


def check_folder(service, name, parent_id):
    """Retorna ID se já existe, senão None."""
    q = (
        f"name='{name}' and mimeType='application/vnd.google-apps.folder' "
        f"and '{parent_id}' in parents and trashed=false"
    )
    res = service.files().list(q=q, fields="files(id,name)").execute()
    files = res.get("files", [])
    return files[0]["id"] if files else None


def scaffold(service, root_id, dry_run=False):
    folder_map = {"": root_id}

    def ensure(path, name, parent_id):
        full_path = f"{path}/{name}" if path else name
        existing = check_folder(service, name, parent_id)
        if existing:
            print(f"  (existe) {full_path}")
            folder_map[full_path] = existing
            return existing
        if dry_run:
            print(f"  [dry] criaria {full_path}")
            folder_map[full_path] = f"<dry-{full_path}>"
            return None
        new_id = get_or_create_folder(service, name, parent_id)
        print(f"  + criada {full_path}")
        folder_map[full_path] = new_id
        return new_id

    for top, subs in STRUCTURE.items():
        top_id = ensure("", top, root_id)
        if isinstance(subs, dict):
            for sub, leaves in subs.items():
                sub_id = ensure(top, sub, top_id) if top_id else None
                for leaf in leaves:
                    if sub_id:
                        ensure(f"{top}/{sub}", leaf, sub_id)

    return folder_map


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root-id", default=ROOT_2026)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    service = get_drive_service()
    print(f"Scaffold em {args.root_id} (dry-run={args.dry_run})\n")
    folder_map = scaffold(service, args.root_id, args.dry_run)

    if not args.dry_run:
        MAP_PATH.parent.mkdir(parents=True, exist_ok=True)
        MAP_PATH.write_text(
            json.dumps({"root_id": args.root_id, "folders": folder_map}, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        print(f"\nFolder map: {MAP_PATH}")


if __name__ == "__main__":
    main()
