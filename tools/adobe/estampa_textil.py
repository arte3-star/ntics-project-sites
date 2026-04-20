"""
Estampa Têxtil (Illustrator)

Gera arte vetorial para estampa/bordado em peça têxtil com cores Pantone especificadas,
áreas de aplicação demarcadas e mockup visual aplicado.

Workflow: workflows/escritorio-projetos/estampa_textil.md
Skill:    .claude/skills/estampa-textil/SKILL.md

Uso:
    python tools/adobe/estampa_textil.py --config path/config.json

Config JSON (exemplo):
    {
      "type": "dolma-culinaria",
      "applications": [
        {
          "area": "peito_esq",
          "dimensions_cm": { "w": 10, "h": 10 },
          "artwork": "logo_estacao_samarco_bordado.ai",
          "application_type": "bordado",
          "pantone": "P 295 C",
          "pantone_tpx": "19-4052 TPX"
        },
        {
          "area": "peito_dir",
          "dimensions_cm": { "w": 10, "h": 3 },
          "artwork_text": "{NOME}",
          "application_type": "bordado",
          "font": "Helvetica-Bold"
        }
      ],
      "tecido": { "tipo": "algodão técnico", "cor_base": "branco" },
      "tamanhos": ["PP", "P", "M", "G", "GG"],
      "output_dir": ".tmp/estampa/dolma_culinaria/"
    }

Output:
    - .AI com áreas demarcadas + swatches Pantone nomeados
    - .PDF 300 dpi com cores Pantone preservadas
    - .PNG mockup aplicado na peça

Regras de legibilidade (validar antes de exportar):
    - Bordado: letra mín 8 mm, traço mín 1 mm
    - Silk: letra mín 5 mm, traço mín 0.5 mm
    - DTF: letra mín 4 mm, traço mín 0.3 mm

Status: STUB — implementação base a fazer.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


LEGIBILIDADE_MIN = {
    "bordado":     {"letra_mm": 8, "traco_mm": 1.0},
    "silk":        {"letra_mm": 5, "traco_mm": 0.5},
    "dtf":         {"letra_mm": 4, "traco_mm": 0.3},
    "sublimatica": {"letra_mm": 3, "traco_mm": 0.3},
    "vinil":       {"letra_mm": 6, "traco_mm": 0.8},
}


def validar_legibilidade(application: dict) -> tuple[bool, str]:
    """Checa se a aplicação respeita tamanhos mínimos para o tipo de processo."""
    tipo = application.get("application_type", "").lower()
    min_specs = LEGIBILIDADE_MIN.get(tipo)
    if not min_specs:
        return False, f"Tipo de aplicação desconhecido: {tipo}"

    # TODO: inspecionar o .AI da arte para checar menor letra e menor traço
    # Por ora retorna True para seguir
    return True, "ok"


def gerar_estampa(config: dict) -> dict:
    """
    Gera arte têxtil.

    TODO:
      1. Validar config (Pantone obrigatório para bordado)
      2. Para cada application:
         a) Validar legibilidade
         b) Criar area demarcada no Illustrator com guia nomeada (AREA_PEITO_ESQ, AREA_COSTAS, etc.)
         c) Importar/posicionar arte dentro da área
         d) Aplicar swatches Pantone nomeados
         e) Converter fontes em outline
      3. Exportar .AI + .PDF + .PNG preview na peça (mockup)
      4. Retornar manifest

    Criar jsx/estampa_textil.jsx com ações Illustrator.
    """
    raise NotImplementedError(
        "estampa_textil.py — implementação pendente.\n"
        "Base: reusar tools/adobe/adapt_artwork_illustrator.py (padrão COM + JSX).\n"
        "Criar jsx/estampa_textil.jsx + jsx/estampa_mockup.jsx."
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Gera arte de estampa têxtil.")
    parser.add_argument("--config", required=True, help="Caminho JSON de config.")
    args = parser.parse_args()

    config_path = Path(args.config)
    if not config_path.exists():
        print(f"[ERRO] Config não encontrado: {config_path}")
        sys.exit(1)

    with config_path.open("r", encoding="utf-8") as f:
        config = json.load(f)

    result = gerar_estampa(config)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
