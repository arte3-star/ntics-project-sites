"""
Arte para Impressão CMYK (Illustrator)

Gera arte vetorial pronta para gráfica (.AI + .PDF/X-4 CMYK 300 dpi com sangria + .PNG preview)
para rollups, pantojet, wind banner, saia bancada, placa fotos, moldura espelho e qualquer
impresso físico.

Workflow: workflows/escritorio-projetos/arte_impressao_cmyk.md
Skill:    .claude/skills/arte-impressao-cmyk/SKILL.md

Uso:
    python tools/adobe/arte_impressao.py --config path/config.json

Config JSON (exemplo):
    {
      "type": "rollup",
      "models": [
        { "name": "Rollup Patrocinador 1", "title": "A SAMARCO APRESENTA:", "hero_logo": "..." },
        { "name": "Rollup Sabores", "title": "ESTAÇÃO SABORES", "body": "50 horas..." }
      ],
      "dimensions_cm": { "width": 85, "height": 200 },
      "bleed_cm": 3,
      "palette_cmyk": { "primary": [100, 65, 0, 45], "accent": [0, 40, 100, 0] },
      "fonts": { "display": "Montserrat-Black", "body": "OpenSans-Regular" },
      "logos": { "soberana_ai": "...", "realizacao_ai": "..." },
      "hierarchy": { "top": "apresenta", "center": "soberana", "bottom_right": "realizacao" },
      "output_dir": ".tmp/arte_impressao/rollups/"
    }

Output:
    Para cada modelo em config.models:
      - {nome}.ai
      - {nome}.pdf (PDF/X-4 CMYK 300 dpi com sangria e marcas de corte)
      - {nome}_preview.png

Status: STUB — implementação base a fazer.
Reusar lógica de tools/adobe/adapt_artwork_illustrator.py + jsx/adapt_artwork.jsx
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def generate_arte_impressao(config: dict) -> dict:
    """
    Gera arte CMYK para impressão.

    TODO (implementação):
      1. Validar config (CMYK obrigatório, sem RGB)
      2. Validar que logos são vetoriais (.AI/.EPS/.SVG), não PNG
      3. Abrir Illustrator via COM (pywin32) — ver adapt_artwork_illustrator.py
      4. Para cada modelo:
         a) Criar artboard (dimensions_cm + bleed_cm)
         b) Setar documento como CMYK
         c) Criar camadas nomeadas: SANGRIA, LOGO_APRESENTA, LOGO_SOBERANA, LOGO_REALIZACAO, KV_PADRONAGEM, TEXTO
         d) Importar logos vetoriais (placeItem, NÃO rasterPlaceItem)
         e) Aplicar hierarquia de posição
         f) Aplicar tipografia e paleta CMYK
         g) Converter fontes para outline
         h) Exportar:
            - .AI nativo (com camadas)
            - .PDF/X-4 (CMYK, 300 dpi, sangria, trim marks) via ExportOptions PDF
            - .PNG preview via exportFile com PNGExportOptions 1200px
      5. Chamar /revisao-arte-impressao automaticamente sobre cada PDF gerado
      6. Se revisão falhar, retornar erro
      7. Retornar manifest com caminhos dos 3 arquivos por modelo

    Script JSX complementar: tools/adobe/jsx/arte_impressao.jsx (a criar)
    """
    raise NotImplementedError(
        "arte_impressao.py — implementação pendente.\n"
        "Base: reusar tools/adobe/adapt_artwork_illustrator.py (padrão COM + JSX).\n"
        "Criar jsx/arte_impressao.jsx com ações Illustrator (artboard + camadas + export PDF/X-4)."
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Gera arte CMYK para impressão.")
    parser.add_argument("--config", required=True, help="Caminho JSON de config.")
    args = parser.parse_args()

    config_path = Path(args.config)
    if not config_path.exists():
        print(f"[ERRO] Config não encontrado: {config_path}")
        sys.exit(1)

    with config_path.open("r", encoding="utf-8") as f:
        config = json.load(f)

    result = generate_arte_impressao(config)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
