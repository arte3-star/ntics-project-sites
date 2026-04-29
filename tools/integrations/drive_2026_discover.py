"""
drive_2026_discover.py - Inventário read-only da pasta Marketing/2026 no Drive.

Lista recursivamente tudo dentro de 2026/ e grava inventário em
.tmp/drive_2026_inventory.json com {id, name, mimeType, path, parentId, size}.

Usage:
  python tools/integrations/drive_2026_discover.py
  python tools/integrations/drive_2026_discover.py --root-id <folder_id>
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

ROOT_2026 = "1mOX2HbTfM30WV1umXOu4gfrYV5WZdJEU"
OUT_PATH = Path("G:/O meu disco/AUTOMAÇÕES/.tmp/drive_2026_inventory.json")
FOLDER_MIME = "application/vnd.google-apps.folder"


def list_children(service, folder_id):
    items = []
    page_token = None
    while True:
        res = service.files().list(
            q=f"'{folder_id}' in parents and trashed=false",
            fields="nextPageToken, files(id,name,mimeType,size,parents,modifiedTime)",
            pageSize=1000,
            pageToken=page_token,
        ).execute()
        items.extend(res.get("files", []))
        page_token = res.get("nextPageToken")
        if not page_token:
            break
    return items


def walk(service, folder_id, prefix=""):
    out = []
    for f in list_children(service, folder_id):
        path = f"{prefix}/{f['name']}" if prefix else f["name"]
        entry = {
            "id": f["id"],
            "name": f["name"],
            "mimeType": f["mimeType"],
            "path": path,
            "parentId": folder_id,
            "size": int(f.get("size", 0)) if f.get("size") else None,
            "modifiedTime": f.get("modifiedTime"),
        }
        out.append(entry)
        if f["mimeType"] == FOLDER_MIME:
            out.extend(walk(service, f["id"], path))
    return out


def print_tree(entries):
    """Imprime árvore textual ordenada por path."""
    for e in sorted(entries, key=lambda x: x["path"]):
        depth = e["path"].count("/")
        indent = "  " * depth
        is_folder = e["mimeType"] == FOLDER_MIME
        icon = "📁" if is_folder else "📄"
        size = f" ({e['size']:,}B)" if e["size"] else ""
        print(f"{indent}{icon} {e['name']}{size}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root-id", default=ROOT_2026)
    parser.add_argument("--out", default=str(OUT_PATH))
    args = parser.parse_args()

    service = get_drive_service()
    print(f"Listando recursivamente folder {args.root_id}...")
    entries = walk(service, args.root_id)

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        json.dumps(
            {"root_id": args.root_id, "count": len(entries), "entries": entries},
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    folders = sum(1 for e in entries if e["mimeType"] == FOLDER_MIME)
    files = len(entries) - folders
    print(f"\n{folders} pastas, {files} arquivos")
    print(f"Inventário: {out}\n")
    print_tree(entries)


if __name__ == "__main__":
    main()
