"""
drive_2026_reorg.py - Reorganiza conteúdo existente da pasta 2026 para a estrutura nova.

Aplica movimentos explícitos (não heurísticos), baseados no inventário read em
discover.py e no folder_map gerado pelo scaffold.py.

Usage:
  python tools/integrations/drive_2026_reorg.py --dry-run
  python tools/integrations/drive_2026_reorg.py
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from upload_to_drive import get_drive_service  # noqa: E402

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

BASE = Path("G:/O meu disco/AUTOMAÇÕES/.tmp")
INVENTORY_PATH = BASE / "drive_2026_inventory.json"
FOLDER_MAP_PATH = BASE / "drive_2026_folder_map.json"
LOG_PATH = BASE / "drive_2026_reorg_log.json"

# Movimentos explícitos: (source_path_in_inventory, dest_folder_path_in_map, optional_new_name)
MOVES = [
    # Top-level folders movendo inteiras pra 7. DESIGN ASSETS/ (renomeadas)
    ("Assinaturas", "7. DESIGN ASSETS/ASSINATURAS", "_merge"),
    ("Frames", "7. DESIGN ASSETS/FRAMES", "_merge"),
    ("Icones", "7. DESIGN ASSETS/ICONES", "_merge"),
    ("Regua dos Projetos", "7. DESIGN ASSETS/REGUAS", "_merge"),

    # Carrossel ODS → EDUCATIVOS
    (
        "Comunicação Institucional/Carrossel/Carrossel 1",
        "1. REDES SOCIAIS/CARROSSEIS/EDUCATIVOS",
        "conhecendo-os-ods",
    ),

    # Vídeo institucional → 4. VIDEOS/INSTITUCIONAL
    (
        "Comunicação Institucional/Videos/RSC com consciencia.mp4",
        "4. VIDEOS/INSTITUCIONAL",
        None,
    ),

    # Pastas containers agora vazias → _ARQUIVO
    ("Comunicação Institucional/Carrossel", "_ARQUIVO", "Carrossel (vazio)"),
    ("Comunicação Institucional/Videos", "_ARQUIVO", "Videos (vazio)"),
    ("Comunicação Institucional", "_ARQUIVO", "Comunicacao Institucional (vazio)"),
]


def find_by_path(inventory, path):
    for e in inventory["entries"]:
        if e["path"] == path:
            return e
    return None


def rename_file(service, file_id, new_name):
    service.files().update(fileId=file_id, body={"name": new_name}).execute()


def move_file(service, file_id, new_parent_id, old_parent_id, new_name=None, dry_run=False):
    if dry_run:
        print(f"    [dry] move {file_id}: {old_parent_id} → {new_parent_id}"
              f"{' (rename: ' + new_name + ')' if new_name else ''}")
        return
    body = {}
    service.files().update(
        fileId=file_id,
        addParents=new_parent_id,
        removeParents=old_parent_id,
        body=body,
    ).execute()
    if new_name:
        rename_file(service, file_id, new_name)


def merge_folder_contents(service, src_folder_id, dest_folder_id, dry_run=False):
    """Move todo conteúdo de src pra dest, depois deleta src (na verdade manda pra trash)."""
    # Lista children do src
    res = service.files().list(
        q=f"'{src_folder_id}' in parents and trashed=false",
        fields="files(id,name,mimeType)",
        pageSize=1000,
    ).execute()
    children = res.get("files", [])
    print(f"    {len(children)} itens a mover de src p/ dest")
    for c in children:
        move_file(service, c["id"], dest_folder_id, src_folder_id, dry_run=dry_run)
    # Trash o src vazio
    if dry_run:
        print(f"    [dry] trash src folder {src_folder_id}")
    else:
        service.files().update(fileId=src_folder_id, body={"trashed": True}).execute()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if not INVENTORY_PATH.exists():
        sys.exit(f"ERRO: rode drive_2026_discover.py primeiro. Falta {INVENTORY_PATH}")
    if not FOLDER_MAP_PATH.exists():
        sys.exit(f"ERRO: rode drive_2026_scaffold.py primeiro. Falta {FOLDER_MAP_PATH}")

    inventory = json.loads(INVENTORY_PATH.read_text(encoding="utf-8"))
    folder_map = json.loads(FOLDER_MAP_PATH.read_text(encoding="utf-8"))["folders"]

    service = get_drive_service()
    log = []

    for src_path, dest_path, opt in MOVES:
        print(f"\n→ {src_path}  ⇒  {dest_path}" + (f"  [{opt}]" if opt else ""))
        src_entry = find_by_path(inventory, src_path)
        if not src_entry:
            print(f"    (skip) não encontrado no inventário")
            continue
        dest_id = folder_map.get(dest_path)
        if not dest_id:
            print(f"    ERRO: dest path '{dest_path}' não está no folder_map")
            continue

        if opt == "_merge":
            # Merge: move conteúdo do src pra dest (que já existe com nome canônico)
            merge_folder_contents(service, src_entry["id"], dest_id, args.dry_run)
            log.append({"action": "merge", "src": src_path, "dest": dest_path})
        else:
            # Move direto: opt é novo nome (ou None)
            move_file(
                service,
                src_entry["id"],
                dest_id,
                src_entry["parentId"],
                new_name=opt,
                dry_run=args.dry_run,
            )
            log.append({
                "action": "move",
                "src": src_path,
                "dest": dest_path,
                "rename_to": opt,
                "file_id": src_entry["id"],
                "old_parent": src_entry["parentId"],
                "new_parent": dest_id,
            })

    if not args.dry_run:
        LOG_PATH.write_text(
            json.dumps({"moves": log}, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        print(f"\nLog: {LOG_PATH}")
    else:
        print("\n(dry-run — nada foi movido)")


if __name__ == "__main__":
    main()
