"""
drive_import_designer_assets.py — Importa peças gráficas (KV, capas, banners,
wind banner, pantojet, dropdown) da pasta "NTICS - DESIGNERS - ESCRITÓRIO DE
PROJETOS" no Google Drive para assets/projetos/{slug}/identidade-visual/{fmt}/.

Escopo: só projetos ativos 2026, só PNG/JPG, dry-run por padrão.

Usage:
  python tools/integrations/drive_import_designer_assets.py                   # dry-run
  python tools/integrations/drive_import_designer_assets.py --apply           # baixa de fato
  python tools/integrations/drive_import_designer_assets.py --project 127 --apply
  python tools/integrations/drive_import_designer_assets.py --format kv,banner --apply
"""
import argparse
import io
import json
import re
import sys
from pathlib import Path

from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload

sys.path.insert(0, str(Path(__file__).parent))
from upload_to_drive import get_drive_service  # noqa: E402

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

DESIGNERS_ROOT_ID = "1RJozv6fthIPn83U5_s1119HPegaxcY0G"
REPO_ROOT = Path(__file__).resolve().parents[2]
ASSETS_PROJETOS = REPO_ROOT / "assets" / "projetos"
LOG_PATH = REPO_ROOT / ".tmp" / "drive_designer_import.json"
FOLDER_MIME = "application/vnd.google-apps.folder"
IMAGE_MIMES = {"image/png", "image/jpeg"}

# Projetos ativos 2026 → slug de pasta em assets/projetos/
# Um código pode ter múltiplos slugs (venda por sponsor).
ACTIVE_PROJECTS = {
    "74": ["74. GLOBAL GOALS EDUCA"],
    "109": ["109. PEC EU FAÇO PARTE 2ªED"],
    "115": ["115. PEROXIDOS"],
    "116": ["116. CULTURA ROBÓTICA (ÁSTER)"],
    "117": ["117. TEATRO E OFICINA ROBÓTICA 4ED (WHIRLPOOL)"],
    "119": ["119. PEC EU FAÇO PARTE 2ªED (SYLVAMO)"],
    "120": [
        "120. NEGÓCIO CULTURAL 2ªED (PORTO ITAPOÁ)",
        "120. NEGÓCIO CULTURAL 2ªED (STATKRAFT)",
    ],
    "121": ["121. NEGÓCIO CULTURAL (TAG)"],
    "124": ["124. EXPOSIÇÃO - GASTRONOMIA TAMBÉM É ARTE (COMPAGAS)"],
    "125": ["125. EXPOSIÇÃO - GASTRONOMIA TAMBÉM É ARTE 2ED (GRU)"],
    "126": ["126. ECOARTE (GRU)"],
    "127": [
        "127. PIE EMPREENDEDORISMO É ARTE 2ED (GRU)",
        "127. PIE EMPREENDEDORISMO É ARTE 2ED (SOTREQ)",
    ],
    "132": ["132. ESTAÇÃO SÃO MARCO (SAMARCO)"],
}

# Keywords de formato → subpasta destino (ordem importa: mais específico primeiro)
# Alguns formatos redirecionam para pastas existentes fora de identidade-visual/
FORMAT_RULES = [
    ("wind-banner", ("wind banner", "wind-banner", "windbanner")),
    ("pantojet", ("pantojet", "panto jet", "panto-jet")),
    ("dropdown", ("dropdown", "drop down", "drop-down", "backdrop", "fundo palco", "fundo de palco")),
    ("banners", ("banner", "roll up", "rollup", "roll-up")),
    ("placas", ("placa",)),
    ("capas", ("capa", "cover", "thumb")),
    ("kv", ("kv", "key visual", "keyvisual")),
    # redirects: caem em pasta fora de identidade-visual/ (legado)
    ("__LOGOS__", ("logo",)),
    ("__REGUAS__", ("régua", "regua")),
]

# Pastas-pai (nomes) que NÃO devem ser importadas
SKIP_PARENT_NAMES = {
    "FOTOS REFERENCIA",
    "FOTOS REFERÊNCIA",
    "FOTOS DE REFERENCIA",
    "FOTOS DE REFERÊNCIA",
    "MOCKUP",
    "MOCKUPS",
    "APRESENTAÇÃO",
    "APRESENTACAO",
    "PPT",
}

# Formatos visíveis para o CLI --format (redirects ficam ocultos)
ALL_FORMATS = [f for f, _ in FORMAT_RULES if not f.startswith("__")] + ["_outros"]


def list_children(service, folder_id):
    items, page_token = [], None
    while True:
        res = service.files().list(
            q=f"'{folder_id}' in parents and trashed=false",
            fields="nextPageToken, files(id,name,mimeType,size,modifiedTime)",
            pageSize=1000,
            pageToken=page_token,
            supportsAllDrives=True,
            includeItemsFromAllDrives=True,
            corpora="allDrives",
        ).execute()
        items.extend(res.get("files", []))
        page_token = res.get("nextPageToken")
        if not page_token:
            break
    return items


def extract_sponsor(slug):
    """Extrai sponsor entre parênteses do slug, em UPPER sem acento parcial."""
    m = re.search(r"\(([^)]+)\)", slug)
    return m.group(1).strip().upper() if m else None


def filter_slugs_by_path(slugs, src_path):
    """Se o path contém o sponsor de um slug e não de outros, retorna só o matching."""
    if len(slugs) <= 1:
        return slugs
    hay = src_path.upper()
    matched = []
    for s in slugs:
        sp = extract_sponsor(s)
        if sp and any(token in hay for token in _sponsor_tokens(sp)):
            matched.append(s)
    return matched if matched else slugs


def _sponsor_tokens(sponsor):
    """Tokens alternativos para um sponsor — variantes com/sem acento."""
    s = sponsor.upper()
    tokens = {s}
    # normaliza acentos comuns para matching em paths
    norm = (
        s.replace("Á", "A").replace("É", "E").replace("Í", "I").replace("Ó", "O").replace("Ú", "U")
        .replace("Ã", "A").replace("Õ", "O").replace("Â", "A").replace("Ê", "E").replace("Ô", "O")
        .replace("Ç", "C")
    )
    tokens.add(norm)
    # "PORTO ITAPOÁ" → também casa "PORTO ITAPOA"
    tokens.add(norm.replace(" ", ""))
    tokens.add(s.replace(" ", ""))
    return tokens


def extract_project_code(folder_name):
    """Extrai código NTICS do início do nome da pasta (ex: '127. PIE ...' → '127')."""
    m = re.match(r"^(\d{1,3})[\s.\-_]", folder_name.strip())
    return m.group(1) if m else None


def classify_format(file_name, parent_folder_name):
    # checa file name primeiro (mais específico), depois parent
    for source in (file_name, parent_folder_name):
        hay = source.lower()
        for fmt, keywords in FORMAT_RULES:
            if any(k in hay for k in keywords):
                return fmt
    return "_outros"


def resolve_redirect(fmt, slug):
    """Para formatos __LOGOS__ / __REGUAS__, retorna pasta externa existente."""
    if fmt == "__LOGOS__":
        return ASSETS_PROJETOS / slug / "LOGOS", "logos"
    if fmt == "__REGUAS__":
        return ASSETS_PROJETOS / slug / "REGUAS", "reguas"
    return None, None


def walk_files(service, folder_id, path_parts):
    """Gera (file_meta, path_parts) para todo arquivo (não-pasta) na subárvore."""
    for item in list_children(service, folder_id):
        new_path = path_parts + [item["name"]]
        if item["mimeType"] == FOLDER_MIME:
            yield from walk_files(service, item["id"], new_path)
        else:
            yield item, new_path


def download_file(service, file_id, dest_path):
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    request = service.files().get_media(fileId=file_id, supportsAllDrives=True)
    buf = io.BytesIO()
    downloader = MediaIoBaseDownload(buf, request)
    done = False
    while not done:
        _, done = downloader.next_chunk()
    dest_path.write_bytes(buf.getvalue())


def resolve_dest_path(slug, fmt, file_name, remote_size):
    redirect_base, redirect_label = resolve_redirect(fmt, slug)
    if redirect_base is not None:
        base = redirect_base
        fmt_label = redirect_label
    else:
        base = ASSETS_PROJETOS / slug / "identidade-visual" / fmt
        fmt_label = fmt
    candidate = base / file_name
    if not candidate.exists():
        return candidate, "new", fmt_label
    if remote_size and candidate.stat().st_size == remote_size:
        return candidate, "skip_same", fmt_label
    stem, suffix = candidate.stem, candidate.suffix
    i = 2
    while True:
        alt = base / f"{stem}__v{i}{suffix}"
        if not alt.exists():
            return alt, "versioned", fmt_label
        i += 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="baixa de fato (default: dry-run)")
    ap.add_argument("--project", help="código NTICS (ex: 127) — limita a um projeto")
    ap.add_argument(
        "--format",
        help=f"csv de formatos, um de: {','.join(ALL_FORMATS)}",
    )
    args = ap.parse_args()

    format_filter = None
    if args.format:
        format_filter = {f.strip() for f in args.format.split(",")}
        unknown = format_filter - set(ALL_FORMATS)
        if unknown:
            print(f"ERRO: formato(s) desconhecido(s): {unknown}", file=sys.stderr)
            sys.exit(2)

    service = get_drive_service()

    print(f"Listando pastas em {DESIGNERS_ROOT_ID}...")
    top_level = list_children(service, DESIGNERS_ROOT_ID)
    project_folders = [f for f in top_level if f["mimeType"] == FOLDER_MIME]
    print(f"  {len(project_folders)} pastas de nivel 1\n")

    log_entries = []
    counters = {"matched": 0, "downloaded": 0, "skip_same": 0, "versioned": 0, "dry": 0, "errors": 0}

    for folder in project_folders:
        code = extract_project_code(folder["name"])
        if not code or code not in ACTIVE_PROJECTS:
            continue
        if args.project and code != args.project:
            continue

        slugs = ACTIVE_PROJECTS[code]
        print(f"[{code}] {folder['name']}  →  {slugs}")

        # Coleta todos arquivos PNG/JPG da subárvore
        for file_meta, path_parts in walk_files(service, folder["id"], [folder["name"]]):
            if file_meta["mimeType"] not in IMAGE_MIMES:
                continue
            parent_folder_name = path_parts[-2] if len(path_parts) >= 2 else folder["name"]
            # skip pastas-pai irrelevantes (fotos de referência, mockups, PPTs)
            if any(skip in p.upper() for p in path_parts[1:] for skip in SKIP_PARENT_NAMES):
                continue
            fmt = classify_format(file_meta["name"], parent_folder_name)
            if format_filter and fmt not in format_filter and fmt.startswith("__") is False:
                continue

            counters["matched"] += 1
            remote_size = int(file_meta.get("size") or 0)
            src_path = "/".join(path_parts)

            # Se múltiplos slugs, tenta desambiguar pelo sponsor no path.
            # Se não der, copia para todos (material comum).
            target_slugs = filter_slugs_by_path(slugs, src_path)

            for slug in target_slugs:
                dest, action, fmt_label = resolve_dest_path(
                    slug, fmt, file_meta["name"], remote_size
                )

                entry = {
                    "src_id": file_meta["id"],
                    "src_path": src_path,
                    "dest": str(dest.relative_to(REPO_ROOT)),
                    "fmt": fmt_label,
                    "slug": slug,
                    "action": action,
                }

                if action == "skip_same":
                    counters["skip_same"] += 1
                    log_entries.append(entry)
                    continue

                if not args.apply:
                    counters["dry"] += 1
                    log_entries.append(entry)
                    print(f"  [DRY] {src_path} → {entry['dest']}")
                    continue

                try:
                    download_file(service, file_meta["id"], dest)
                    counters[action if action in counters else "downloaded"] += 1
                    if action != "versioned":
                        counters["downloaded"] += 1
                    log_entries.append(entry)
                    print(f"  [OK]  {src_path} → {entry['dest']}")
                except HttpError as e:
                    counters["errors"] += 1
                    entry["error"] = str(e)
                    log_entries.append(entry)
                    print(f"  [ERR] {src_path}: {e}", file=sys.stderr)

    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    LOG_PATH.write_text(json.dumps(log_entries, indent=2, ensure_ascii=False), encoding="utf-8")

    print("\n--- RESUMO ---")
    for k, v in counters.items():
        print(f"  {k}: {v}")

    # distribuição por formato
    by_fmt = {}
    for e in log_entries:
        by_fmt[e["fmt"]] = by_fmt.get(e["fmt"], 0) + 1
    print("\n  Por formato:")
    for fmt in sorted(by_fmt, key=lambda f: (-by_fmt[f], f)):
        print(f"    {fmt}: {by_fmt[fmt]}")

    print(f"\nLog: {LOG_PATH}")
    if not args.apply:
        print("Dry-run. Use --apply para baixar de fato.")


if __name__ == "__main__":
    main()
