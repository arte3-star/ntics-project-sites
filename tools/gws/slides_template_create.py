"""
Google Slides Template Creator

Cria um template editável em Google Slides com placeholders nomeados
({CIDADE}, {TRILHA}, {DATA}, {NOME}, etc.) a partir de config JSON.
Exporta também um PNG de exemplo preenchido.

Workflow: workflows/marketing/producao/google_slides_template.md
Skill:    .claude/skills/google-slides-template/SKILL.md

Uso:
    python tools/gws/slides_template_create.py --config path/config.json

Config JSON (exemplo):
    {
      "type": "convite-cidade",
      "size": { "width_px": 1080, "height_px": 1350 },
      "palette": { "primary": "#003A70", "accent": "#F5A623" },
      "font_family": "Montserrat",
      "logos": { "soberana": "logo_esa.png", "realizacao": "logo_ntics.png" },
      "placeholders": [
        { "name": "CIDADE", "max_chars": 25, "example": "Santa Rita Durão" },
        { "name": "DATA",   "max_chars": 30, "example": "15 de maio de 2026" }
      ],
      "fixed_content": {
        "headline": "Estação Samarco em {CIDADE}",
        "subhead":  "Inscrições abertas"
      },
      "drive_folder_id": "1wDNy7rve_uK-cBZa3aP529q9GHtL0cf6",
      "file_name": "CONVITE POST CIDADE"
    }

Output:
    {
      "slides_url": "https://docs.google.com/presentation/d/.../edit",
      "file_id": "...",
      "png_preview_path": ".tmp/slides_preview/CONVITE_POST_CIDADE.png"
    }

Status: STUB — implementação base a fazer.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Auth compartilhada com forms_create.py
sys.path.insert(0, str(Path(__file__).parent))
from gws_auth import get_credentials  # noqa: E402

try:
    from googleapiclient.discovery import build
except ImportError:
    print("[ERRO] google-api-python-client não instalado. pip install google-api-python-client")
    sys.exit(1)


# Conversão hex -> RGB 0-1 usado pela API Slides
def hex_to_rgb_float(hex_color: str) -> dict:
    h = hex_color.lstrip("#")
    return {
        "red":   int(h[0:2], 16) / 255,
        "green": int(h[2:4], 16) / 255,
        "blue":  int(h[4:6], 16) / 255,
    }


def px_to_emu(px: int) -> int:
    """Google Slides usa EMU (English Metric Units). 1 px ≈ 9525 EMU."""
    return px * 9525


def create_template(config: dict) -> dict:
    """
    Cria Google Slides template a partir do config.
    Retorna dict com slides_url, file_id, png_preview_path.

    TODO (implementação completa):
      1. Autenticar via get_credentials()
      2. Criar presentation via Slides API (presentations.create)
      3. Ajustar tamanho do slide (presentations.batchUpdate com updatePageProperties)
      4. Inserir text boxes com placeholders {CAMPO} nas posições da config
      5. Aplicar cores (palette) e fonte (font_family)
      6. Inserir logos (via Drive API + insertImage do Slides)
      7. Duplicar o slide e preencher com valores de exemplo
      8. Exportar slide preenchido como PNG (presentations.pages.getThumbnail)
      9. Mover o arquivo para drive_folder_id
      10. Retornar URLs e paths
    """
    creds = get_credentials()
    slides_service = build("slides", "v1", credentials=creds)
    drive_service  = build("drive",  "v3", credentials=creds)

    # Passo 1 — criar presentation
    body = {"title": config["file_name"]}
    presentation = slides_service.presentations().create(body=body).execute()
    file_id = presentation["presentationId"]

    # Passo 2 — mover para folder destino
    if config.get("drive_folder_id"):
        drive_service.files().update(
            fileId=file_id,
            addParents=config["drive_folder_id"],
            removeParents="root",
            fields="id, parents",
        ).execute()

    # TODO: implementar passos 3-9
    # Por enquanto retorna a presentation vazia já criada na pasta correta
    raise NotImplementedError(
        "slides_template_create.py — implementação completa pendente.\n"
        "Presentation criada (id=" + file_id + "), mas placeholders, cores, logos e PNG preview ainda não aplicados.\n"
        "Ver TODO no docstring de create_template() para os passos a implementar."
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Cria Google Slides template com placeholders.")
    parser.add_argument("--config", required=True, help="Caminho JSON de config.")
    args = parser.parse_args()

    config_path = Path(args.config)
    if not config_path.exists():
        print(f"[ERRO] Config não encontrado: {config_path}")
        sys.exit(1)

    with config_path.open("r", encoding="utf-8") as f:
        config = json.load(f)

    result = create_template(config)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
