"""
Unifica assets/melhores-fotos + assets/mehlores-fotos2 em assets/melhores-fotos-unificado.

Regra:
- mehlores-fotos2 e a base (copia intacta).
- melhores-fotos e mesclada nas subpastas temáticas correspondentes.
- 6 pastas orfas viram pastas numeradas 9-13 (gastronomia mescla em "7. CULINARIA SUSTENTAVEL").
- _thumbs e scoring-results.json sao descartados.
- Colisoes: mantem o arquivo de mehlores-fotos2, renomeia o de melhores-fotos com sufixo " (dup).{ext}".
- Registra colisoes em DST/_merge-log.txt.
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

ROOT = Path(r"g:\O meu disco\AUTOMAÇÕES")
SRC1 = ROOT / "assets" / "melhores-fotos"
SRC2 = ROOT / "assets" / "mehlores-fotos2"
DST = ROOT / "assets" / "melhores-fotos-unificado"

MAPPING = {
    "ods-escolas": "1. CONHECENDO OS ODS NAS ESCOLAS",
    "festival": "4. FESTIVAL CONHECENDO OS ODS",
    "robotica": "5. ROBÓTICA NAS ESCOLAS",
    "caminhao-itinerante": "6. CAMINHAO CONHECENDO OS ODS",
    "gastronomia": "7. CULINÁRIA SUSTENTÁVEL",
    "cinegastroarte": "8. FESTIVAL CINEGASTROARTE",
    "circo": "CIRCO",
    "teatro": "9. TEATRO",
    "artes-literarias": "10. ARTES LITERÁRIAS",
    "empreendedorismo-cultura": "11. EMPREENDEDORISMO CULTURA",
    "hub-agro": "12. HUB AGRO",
    "negocio-cultural": "13. NEGÓCIO CULTURAL",
}

SKIP_DIRS = {"_thumbs"}
SKIP_FILES = {"scoring-results.json"}


def main() -> int:
    if DST.exists():
        print(f"ERRO: pasta de destino ja existe: {DST}")
        print("Apague ou renomeie antes de rodar novamente.")
        return 1

    if not SRC1.exists():
        print(f"ERRO: pasta origem 1 nao encontrada: {SRC1}")
        return 1
    if not SRC2.exists():
        print(f"ERRO: pasta origem 2 nao encontrada: {SRC2}")
        return 1

    print(f"[1/3] Copiando base de {SRC2.name} -> {DST.name} ...")
    shutil.copytree(SRC2, DST)
    base_count = sum(1 for _ in DST.rglob("*") if _.is_file())
    print(f"       {base_count} arquivos copiados da base.")

    log_path = DST / "_merge-log.txt"
    log_lines: list[str] = []
    copied = 0
    collisions = 0
    skipped_thumbs = 0
    skipped_files = 0

    print(f"[2/3] Mesclando {SRC1.name} nas pastas temáticas ...")
    for slug, dest_name in MAPPING.items():
        src_folder = SRC1 / slug
        if not src_folder.is_dir():
            log_lines.append(f"[AVISO] pasta origem nao encontrada: {src_folder}")
            continue

        dst_folder = DST / dest_name
        dst_folder.mkdir(parents=True, exist_ok=True)

        for item in src_folder.iterdir():
            if item.is_dir():
                if item.name in SKIP_DIRS:
                    skipped_thumbs += sum(1 for _ in item.rglob("*") if _.is_file())
                    continue
                for sub in item.rglob("*"):
                    if sub.is_file():
                        if sub.name in SKIP_FILES:
                            skipped_files += 1
                            continue
                        rel = sub.relative_to(src_folder)
                        target = _resolve_collision(dst_folder / rel, log_lines)
                        target.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(sub, target)
                        copied += 1
                        if "(dup)" in target.name:
                            collisions += 1
                continue

            if item.name in SKIP_FILES:
                skipped_files += 1
                continue

            target = _resolve_collision(dst_folder / item.name, log_lines)
            shutil.copy2(item, target)
            copied += 1
            if "(dup)" in target.name:
                collisions += 1

    log_path.write_text(
        "Log de merge - unify_best_photos.py\n"
        f"Copiados de melhores-fotos: {copied}\n"
        f"Colisoes renomeadas com (dup): {collisions}\n"
        f"Arquivos em _thumbs ignorados: {skipped_thumbs}\n"
        f"scoring-results.json ignorados: {skipped_files}\n\n"
        + "\n".join(log_lines),
        encoding="utf-8",
    )

    print(f"[3/3] Concluido.")
    print("")
    print(f"   Base (mehlores-fotos2):          {base_count} arquivos")
    print(f"   Mesclados (melhores-fotos):      {copied} arquivos")
    print(f"   Colisoes renomeadas (dup):       {collisions}")
    print(f"   Ignorados (_thumbs):             {skipped_thumbs}")
    print(f"   Ignorados (scoring-results.json):{skipped_files}")
    print(f"   Total na pasta unificada:        {base_count + copied}")
    print("")
    print(f"   Destino: {DST}")
    print(f"   Log:     {log_path}")
    return 0


def _resolve_collision(target: Path, log_lines: list[str]) -> Path:
    if not target.exists():
        return target
    new_name = f"{target.stem} (dup){target.suffix}"
    new_target = target.with_name(new_name)
    counter = 2
    while new_target.exists():
        new_name = f"{target.stem} (dup {counter}){target.suffix}"
        new_target = target.with_name(new_name)
        counter += 1
    log_lines.append(f"[COLISAO] {target.name} -> {new_target.name} em {target.parent.name}")
    return new_target


if __name__ == "__main__":
    sys.exit(main())
