---
name: estampa-textil
description: "Gera arte vetorial para estampa/bordado têxtil (avental, dolma, camiseta, jaleco, uniforme) com cores Pantone especificadas, áreas de peito/costas demarcadas e mockup visual aplicado na peça. Entrega .AI + .PDF + .PNG preview prontos para envio à confecção."
user-invocable: true
---

Leia e execute o workflow completo em `workflows/escritorio-projetos/estampa_textil.md`.

## Quando usar

- Avental de culinária (participante ou chef)
- Dolma de culinarista
- Jaleco/uniforme de facilitador (beleza, palestrante)
- Camiseta de equipe
- Avental/capa de corte de cabelo
- Qualquer peça têxtil que leva estampa ou bordado

## Inputs

- **Tipo de peça têxtil** (avental, dolma, camiseta, jaleco, capa)
- **Áreas de aplicação** (peito esquerdo, peito direito, costas, manga, bolso) — com dimensões de cada
- **Tipo de aplicação** (bordado, estampa sublimática, silk, DTF)
- **Logo/arte a aplicar** (.AI vetorial)
- **Cores** — Pantone Coated (TPX para tecido) ou CMYK equivalente
- **Tecido** (brim, algodão, poliéster, PU) — afeta cor final
- **Tamanhos do vestuário** (PP a GG)

## Output

- `.AI` vetorial com áreas de aplicação demarcadas (peito 10×10 cm, costas 30×20 cm, etc.)
- `.PDF 300 dpi` com cores Pantone nomeadas (P 293 C, P 7408 C, etc.)
- `.PNG preview` da arte aplicada no mockup da peça (para validação)

## Ferramentas

| Ferramenta | Arquivo | Função |
|---|---|---|
| Gerador estampa | `tools/adobe/estampa_textil.py` | Monta arte vetorial em Illustrator com áreas demarcadas |
| Mockup apply | `tools/adobe/estampa_mockup.py` | Aplica arte em mockup da peça (PSD/AI) para preview |
| Adaptador base | `tools/adobe/adapt_artwork_illustrator.py` | Base de manipulação vetorial |

## Regras críticas

- **Cores Pantone obrigatórias** para bordado — nunca CMYK direto (bordadeira não consegue reproduzir)
- **Áreas demarcadas** no arquivo com guias nomeadas (`AREA_PEITO_ESQ`, `AREA_COSTAS`)
- **Tipografia em outline** (bordado não funciona com fonte não convertida)
- **Tamanho mínimo** de legibilidade: 8 mm para letra em bordado, 5 mm para estampa silk
- **Tecido-referência** no preview: sempre mostrar cor de fundo próxima do tecido final

## Feedback NTICS (aprendizado 2025)

- Aventais de cozinha: brim leve ou algodão (não usar poliéster, manchas de gordura ficam)
- Não usar plástico ilustrado em kits participantes
- Uniformes versáteis (evitar excesso de personalização que limite reuso)
- Backdrop inflável / pantojet (não é têxtil, mas mesma regra de aprendizado: nunca boxtruss)
