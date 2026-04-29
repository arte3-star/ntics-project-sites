"""
publicar_drive.py - Publica output final aprovado no Drive Marketing/2026.

Recebe --source apontando para pasta em output/marketing/ e resolve destino
automaticamente via mapeamento local→Drive.

Usage:
  python tools/integrations/publicar_drive.py --source output/marketing/carrosseis/cases/samarco-estacao/
  python tools/integrations/publicar_drive.py --source output/marketing/artigos/2026-04-23-gamification/
  python tools/integrations/publicar_drive.py --source output/marketing/carrosseis/noticias/semana-S03/ --categoria custom --dest "1. REDES SOCIAIS/CARROSSEIS/NOTICIAS/semana-S03"

Categorias resolvidas automaticamente por prefixo do path:
  carrosseis/cases/         → 1. REDES SOCIAIS/CARROSSEIS/CASES/
  carrosseis/noticias/      → 1. REDES SOCIAIS/CARROSSEIS/NOTICIAS/
  carrosseis/educacional/   → 1. REDES SOCIAIS/CARROSSEIS/EDUCATIVOS/
  posts-avulsos/            → 1. REDES SOCIAIS/POSTS/
  stories/                  → 1. REDES SOCIAIS/STORIES/
  artigos/                  → 2. WEBSITE/ARTIGOS BLOG/
  sites/                    → 2. WEBSITE/LANDING PAGES/
  newsletters/              → 3. EMAIL/NEWSLETTERS/
  videos/                   → 4. VIDEOS/ (subcategoria detectada pelo nome)
  impressos/                → 5. IMPRESSOS/
  apresentacoes/            → 6. APRESENTACOES/
"""
import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from upload_to_drive import get_drive_service, upload_folder  # noqa: E402

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

ROOT_2026 = "1mOX2HbTfM30WV1umXOu4gfrYV5WZdJEU"
LOG_PATH = Path("G:/O meu disco/AUTOMAÇÕES/.tmp/drive_publish_log.jsonl")

# Mapeamento: prefixo local (dentro de output/marketing/) → caminho no Drive 2026
MAPPING = [
    ("carrosseis/cases", "1. REDES SOCIAIS/CARROSSEIS/CASES"),
    ("carrosseis/noticias", "1. REDES SOCIAIS/CARROSSEIS/NOTICIAS"),
    ("carrosseis/educacional", "1. REDES SOCIAIS/CARROSSEIS/EDUCATIVOS"),
    ("carrosseis/clientes", "1. REDES SOCIAIS/CARROSSEIS/CLIENTES"),
    ("carrosseis", "1. REDES SOCIAIS/CARROSSEIS"),  # fallback
    ("posts-avulsos", "1. REDES SOCIAIS/POSTS"),
    ("posts", "1. REDES SOCIAIS/POSTS"),
    ("stories", "1. REDES SOCIAIS/STORIES"),
    ("reels", "1. REDES SOCIAIS/REELS"),
    ("artigos", "2. WEBSITE/ARTIGOS BLOG"),
    ("sites", "2. WEBSITE/LANDING PAGES"),
    ("newsletters", "3. EMAIL/NEWSLETTERS"),
    ("videos/cases", "4. VIDEOS/CASES"),
    ("videos/pre-projeto", "4. VIDEOS/PRE-PROJETO"),
    ("videos/institucional", "4. VIDEOS/INSTITUCIONAL"),
    ("videos", "4. VIDEOS/INSTITUCIONAL"),  # fallback
    ("impressos", "5. IMPRESSOS"),
    ("apresentacoes", "6. APRESENTACOES"),
]


def resolve_dest(source: Path, marketing_root: Path) -> str:
    """Retorna caminho no Drive a partir de pasta local.

    Ex: output/marketing/carrosseis/cases/samarco-estacao/
        → 1. REDES SOCIAIS/CARROSSEIS/CASES/samarco-estacao
    """
    rel = source.resolve().relative_to(marketing_root.resolve())
    rel_str = str(rel).replace("\\", "/")
    parts = rel_str.split("/")

    for prefix, drive_path in MAPPING:
        prefix_parts = prefix.split("/")
        if parts[: len(prefix_parts)] == prefix_parts:
            remainder = "/".join(parts[len(prefix_parts):])
            if remainder:
                return f"{drive_path}/{remainder}"
            return drive_path

    raise ValueError(
        f"Não consegui resolver destino para '{rel_str}'. "
        f"Use --dest para especificar manualmente."
    )


def log_publish(source, dest, result):
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "timestamp": datetime.now().isoformat(),
        "source": str(source),
        "dest": dest,
        "folder_id": result["folder_id"],
        "link": result["link"],
        "files_uploaded": result["files_uploaded"],
    }
    with LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True, help="Pasta local (output/marketing/...)")
    parser.add_argument("--dest", default=None, help="Override do caminho no Drive")
    parser.add_argument("--marketing-root", default="output/marketing", help="Raiz dos outputs")
    parser.add_argument("--root-id", default=ROOT_2026, help="Folder ID raiz no Drive")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    source = Path(args.source)
    if not source.exists():
        sys.exit(f"ERRO: pasta não encontrada: {source}")

    if args.dest:
        dest = args.dest
    else:
        dest = resolve_dest(source, Path(args.marketing_root))

    print(f"Source:  {source}")
    print(f"Destino: 2026/{dest}")

    service = get_drive_service()
    result = upload_folder(service, source, dest, pattern="*", root_id=args.root_id)
    log_publish(source, dest, result)

    if args.json:
        print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
