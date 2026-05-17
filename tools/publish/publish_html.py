#!/usr/bin/env python3
"""
publish_html.py
Publica um arquivo HTML no repositório GitHub Pages arte3-star/ntics-project-sites.

Uso com dest automático (recomendado):
  python tools/publish/publish_html.py --src output/marketing/briefings-videomaker/2026-05-04/index.html

  O destino é derivado do --src: strip do prefixo output/ + pasta pai do arquivo.
  Ex: output/marketing/briefings-videomaker/2026-05-04/index.html
      -> briefings-videomaker/2026-05-04 (na URL)

Uso com dest explícito:
  python tools/publish/publish_html.py --src output/marketing/briefings-videomaker/2026-05-04/index.html --dest briefings/videomaker/2026-05-04

Saída:
  URL pública do arquivo publicado no GitHub Pages.

Requisitos:
  - gh CLI autenticado (gh auth login)
  - git configurado com nome e e-mail
"""

import sys
import argparse
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

REPO = "arte3-star/ntics-project-sites"
PAGES_BASE = "https://arte3-star.github.io/ntics-project-sites"
CLONE_DIR = ROOT / ".tmp" / "ntics-pages"


def run(cmd: list[str], cwd=None, check=True) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=cwd, check=check, capture_output=True, text=True)


def ensure_repo() -> Path:
    """Clona ou atualiza o repositorio local."""
    if (CLONE_DIR / ".git").exists():
        print("[pages] Atualizando repositorio local...")
        run(["git", "restore", "."], cwd=CLONE_DIR, check=False)
        run(["git", "clean", "-fd"], cwd=CLONE_DIR, check=False)
        result = run(["git", "pull"], cwd=CLONE_DIR, check=False)
        if result.returncode != 0:
            # Clone corrompido: deletar e re-clonar
            import shutil as _shutil
            print("[pages] Clone corrompido. Re-clonando...")
            _shutil.rmtree(CLONE_DIR, ignore_errors=True)
            CLONE_DIR.parent.mkdir(parents=True, exist_ok=True)
            run(["git", "clone", "--single-branch", "--branch", "master",
                 f"https://github.com/{REPO}.git", str(CLONE_DIR)])
    else:
        print(f"[pages] Clonando {REPO}...")
        CLONE_DIR.parent.mkdir(parents=True, exist_ok=True)
        run(["git", "clone", "--single-branch", "--branch", "master",
             f"https://github.com/{REPO}.git", str(CLONE_DIR)])
    return CLONE_DIR


def derive_dest(src: Path) -> str:
    """
    Deriva o dest a partir do src, removendo o prefixo output/ e o nome do arquivo.
    Ex: output/marketing/briefings-videomaker/2026-05-04/index.html
        -> marketing/briefings-videomaker/2026-05-04
    """
    try:
        rel = src.relative_to(ROOT / "output")
    except ValueError:
        rel = src.relative_to(ROOT)
    return str(rel.parent).replace("\\", "/")


def publish(src: Path, dest_rel: str) -> str:
    """
    Copia src para dest_rel dentro do repo, faz commit e push.
    Retorna a URL publica.
    """
    repo = ensure_repo()

    dest_dir = repo / dest_rel
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest_file = dest_dir / src.name

    print(f"[pages] Copiando {src.name} -> {dest_rel}/")
    shutil.copy2(src, dest_file)

    run(["git", "add", str(dest_file.relative_to(repo))], cwd=repo)

    status = run(["git", "status", "--porcelain"], cwd=repo)
    if not status.stdout.strip():
        print("[pages] Nenhuma alteracao detectada - arquivo ja esta atualizado.")
    else:
        commit_msg = f"publish: {dest_rel}/{src.name}"
        run(["git", "commit", "-m", commit_msg], cwd=repo)
        run(["git", "push"], cwd=repo)
        print("[pages] Push concluido.")

    url = f"{PAGES_BASE}/{dest_rel}/{src.name}"
    if src.name == "index.html":
        url = f"{PAGES_BASE}/{dest_rel}/"

    return url


def main():
    parser = argparse.ArgumentParser(description="Publica HTML no GitHub Pages NTICS.")
    parser.add_argument("--src", required=True, help="Caminho local do arquivo HTML")
    parser.add_argument(
        "--dest",
        default=None,
        help="Caminho de destino dentro do repo (opcional; derivado do --src se omitido)",
    )
    args = parser.parse_args()

    src = Path(args.src)
    if not src.is_absolute():
        src = ROOT / src
    if not src.exists():
        print(f"[pages] ERRO: arquivo nao encontrado: {src}", file=sys.stderr)
        sys.exit(1)

    dest = args.dest.strip("/") if args.dest else derive_dest(src)

    url = publish(src, dest)
    print(f"\n[pages] Publicado com sucesso!")
    print(f"[pages] URL: {url}")
    return url


if __name__ == "__main__":
    main()
