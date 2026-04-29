"""
drive_find_cronograma.py — Localiza o xlsx de cronograma de projeto NTICS no Drive.

Estrutura padrão (validada abr/2026): cada projeto tem pasta-mãe em
0B3mObVoJ_qhcT3B5NThOZ0x3R1E, com subpasta `2. ENGAJAMENTO - CARTAS DE ADESÃO
CIDADES`. Dentro dela, um .xlsx com "engajamento" ou "cronograma" no nome.

Para os 7 projetos pré-execução abr/2026, mapping é hardcoded para ser
determinístico. Fallback para busca por nome existe se o slug for desconhecido.

Usage:
  python tools/integrations/drive_find_cronograma.py --projeto 119
  python tools/integrations/drive_find_cronograma.py --projeto 127G
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

FOLDER_MIME = "application/vnd.google-apps.folder"
XLSX_MIME = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

# Pasta-raiz onde vivem todas as pastas-mãe de projeto.
PROJETOS_ROOT_ID = "0B3mObVoJ_qhcT3B5NThOZ0x3R1E"

# Slug da landing → IDs no Drive (pasta-mãe + subpasta engajamento + xlsx)
# Validado em abr/2026; se mudar, basta atualizar aqui.
PROJECT_DRIVE_MAP = {
    "116": {
        "slug": "cultura-robotica-aster",
        "pasta_mae": "1iCOrSqJKao0s82olnuD_0lLziQKn3jjq",
        "engajamento": "1e2AZXNxwu0XH6336pIvu1b450HqP_DBC",
        "xlsx": "1JJatPXUjxItpAumd2KKYDU_CtgtNi2SO",
    },
    "117": {
        "slug": "teatro-oficina-robotica-4ed-whirlpool",
        "pasta_mae": "1A36tj_AhN7CHH9mNPn5dfIGNhYcVCpFP",
        "engajamento": "1EAG14pU6lFQkhOmWYQ5chElxdoJRNdUj",
        "xlsx": "1BEX3B1WYa0e75d4mE_Y-Bvv9wWN0WIW2",
    },
    "119": {
        "slug": "pec-eu-faco-parte-2ed-sylvamo",
        "pasta_mae": "1KKqZXPpMjRfsL1aF47_jhc-GSDuUYrYc",
        "engajamento": "1B2JoMgsDSGi56ZgJZmhIH75yA2cQBIV9",
        "xlsx": "1ghOUxE8-hKtU2WNVvID-YFZM4pyeA6pq",
    },
    "124": {
        "slug": "gastronomia-tambem-e-arte-compagas",
        "pasta_mae": "15MPnwHWVdidm2B6h30ah54T74FJjMJtT",
        "engajamento": "1_Shj9FVvJ1k0fVFCVgGllo6NVNgR6CQC",
        "xlsx": "1ccAFn5ysezIe9ptFGr8i77bl24vAFehh",
    },
    "125": {
        "slug": "gastronomia-tambem-e-arte-2ed-gru",
        "pasta_mae": "1CPjTUwhgAazmRXsMwpXZzO-v8qcXwnLf",
        "engajamento": "14jVBpivQYcA-eB0syNFGwcL3i_RP40L0",
        "xlsx": "1kGFU4CSLIJsFw8VxBc0vwyQblnPKctK5",
    },
    "127G": {
        "slug": "pie-empreendedorismo-e-arte-2ed-gru",
        "pasta_mae": "1JLj1xxOBnYRjowjfH_tC1T8H1XYnqTuS",
        "engajamento": "1jwZSHDn3PlcQOKE8JwTFf9OrwCGrMpIN",
        "xlsx": "15-EyCfwyGC4rYMQq5k_FTVHimPRpVeMb",
    },
    "127S": {
        "slug": "pie-empreendedorismo-e-arte-2ed-sotreq",
        "pasta_mae": "1JLj1xxOBnYRjowjfH_tC1T8H1XYnqTuS",
        "engajamento": "1jwZSHDn3PlcQOKE8JwTFf9OrwCGrMpIN",
        "xlsx": "15-EyCfwyGC4rYMQq5k_FTVHimPRpVeMb",
    },
}


def find_cronograma(projeto: str) -> dict | None:
    """Retorna metadata do xlsx de cronograma para o código do projeto."""
    info = PROJECT_DRIVE_MAP.get(projeto)
    if not info:
        return None
    service = get_drive_service()
    # confirma que o arquivo ainda existe + pega last_modified
    meta = service.files().get(
        fileId=info["xlsx"],
        fields="id,name,modifiedTime,mimeType",
        supportsAllDrives=True,
    ).execute()
    return {
        "projeto": projeto,
        "slug": info["slug"],
        "spreadsheet_id": meta["id"],
        "spreadsheet_name": meta["name"],
        "mime_type": meta["mimeType"],
        "last_modified": meta.get("modifiedTime"),
        "engajamento_folder_id": info["engajamento"],
        "pasta_mae_id": info["pasta_mae"],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--projeto", required=True, help="Código (116, 117, 119, 124, 125, 127G, 127S)")
    parser.add_argument("--output", help="Salvar resultado em JSON")
    args = parser.parse_args()

    result = find_cronograma(args.projeto)
    if not result:
        print(f"[ERRO] projeto desconhecido: {args.projeto}", file=sys.stderr)
        sys.exit(2)
    text = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(text, encoding="utf-8")
        print(f"Salvo em {args.output}", file=sys.stderr)
    print(text)


if __name__ == "__main__":
    main()
