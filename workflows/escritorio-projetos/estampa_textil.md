# Workflow: Estampa Têxtil

## Objetivo
Gerar arte vetorial para estampa/bordado em peça têxtil (avental, dolma, camiseta, jaleco, capa) com cores Pantone especificadas, áreas de aplicação demarcadas e mockup visual aplicado para aprovação antes da confecção.

## Quando Executar
Após KV pronto, quando for preciso enviar arte para confecção de uniformes, aventais, dolmas, camisetas de equipe ou qualquer peça têxtil.

## Tipos de peça suportados

| Peça | Áreas de aplicação | Tipo de aplicação | Tecido padrão |
|---|---|---|---|
| Avental culinária participante | Peito 25×30 cm | estampa/bordado | Brim ou algodão |
| Dolma culinarista | Peito esq. 10×10 cm + peito dir. nome | bordado | Algodão técnico |
| Uniforme/Jaleco beleza | Peito esq. 10×10 cm + nome | bordado | Poliéster-algodão |
| Avental corte cabelo | Peito ou bolso 15×20 cm | estampa | PU impermeável |
| Camiseta equipe | Peito 10×10 cm + costas 30×20 cm | estampa DTF ou silk | Algodão |

## Inputs Necessários

| Input | Fonte | Obrigatório |
|---|---|---|
| Tipo de peça | Lista acima | Sim |
| Áreas de aplicação | Tabela ou custom | Sim |
| Tipo de aplicação | bordado · silk · DTF · sublimática · vinil | Sim |
| Logo/arte a aplicar (.AI) | KV do projeto | Sim |
| Cores Pantone | KV + tecido (TPX para bordado, TCX para estampa) | Sim |
| Tipo de tecido | Afeta cor final e tipo de aplicação | Sim |
| Tamanhos do vestuário | PP a GG (padrão adulto) | Sim |
| Mockup da peça | Template AI/PSD da peça (se existir) | Não (default genérico) |

## Passo a Passo

### Fase 1 — Coleta
1. Tipo de peça → carregar defaults.
2. Receber arte/logo a aplicar (validar vetor, não PNG).
3. Definir cores Pantone:
   - Para **bordado**: usar Pantone TPX (tecido poliéster) ou TCX (algodão) — bordadeira precisa da nomenclatura específica para comprar linha
   - Para **estampa DTF/silk**: CMYK ou Pantone C equivalente
   - Para **sublimação**: CMYK direto (só em poliéster)

### Fase 2 — Montagem da arte
```bash
python tools/adobe/estampa_textil.py --config .tmp/estampa_config.json
```

Config exemplo:
```json
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
      "font": "Helvetica-Bold",
      "pantone_tpx": "19-4052 TPX"
    }
  ],
  "tecido": { "tipo": "algodão técnico", "cor_base": "branco" },
  "tamanhos": ["PP", "P", "M", "G", "GG"],
  "output_dir": ".tmp/estampa/dolma_culinaria/"
}
```

O tool:
1. Abre Illustrator.
2. Cria artboard com áreas de aplicação como **guias nomeadas** (`AREA_PEITO_ESQ`, `AREA_PEITO_DIR`, `AREA_COSTAS`).
3. Posiciona a arte dentro de cada área com dimensões corretas.
4. Converte fontes para outline (obrigatório para bordado).
5. Atribui cores Pantone via swatches nomeados.
6. Exporta:
   - `.AI` com áreas demarcadas e swatches Pantone nomeados
   - `.PDF 300 dpi` com cores Pantone preservadas
   - `.PNG preview` do mockup da peça com arte aplicada (para validação visual)

### Fase 3 — Mockup visual
Aplicar arte gerada em mockup da peça (template PSD ou AI) via `tools/adobe/estampa_mockup.py`:
- Dolma branca com bordado peito
- Avental brim com estampa peito
- Camiseta preta com estampa peito + costas
- etc.

Output: PNG 1200 px simulando a peça pronta.

### Fase 4 — Regras de legibilidade
Validar antes de entregar:
- **Bordado**: letra mínima 8 mm · traço mínimo 1 mm
- **Estampa silk**: letra mínima 5 mm · traço mínimo 0,5 mm
- **DTF**: letra mínima 4 mm · traço mínimo 0,3 mm
- **Logo em peça pequena** (bolso, manga): não descer de 3 cm largura

Se não atender, retornar erro para ajustar tamanho antes de mandar à confecção.

### Fase 5 — Entrega
Upload dos 3 arquivos + mockup no folder do projeto.

Relatório para o usuário:
- Peças geradas (com dimensão)
- Cores Pantone especificadas (para compra de linha/tinta)
- Observações do tecido (cor base afeta cor da estampa)
- Tamanhos de vestuário
- Preview visual na peça

## Output Esperado
- `.AI` com áreas de aplicação demarcadas + swatches Pantone nomeados
- `.PDF 300 dpi` com cores Pantone preservadas
- `.PNG` mockup visual da peça com arte aplicada

## Tool Utilizado
`tools/adobe/estampa_textil.py` + `tools/adobe/estampa_mockup.py`

## Regras críticas NTICS
- **Cores Pantone obrigatórias** para bordado (bordadeira não reproduz CMYK direto)
- **Áreas demarcadas** com guias nomeadas
- **Tipografia em outline** sempre
- **Tamanho mínimo legibilidade** por tipo de aplicação
- **Tecido-referência** no preview — mostrar cor base real
- **Não usar plástico ilustrado** em kits participante (regra NTICS)
- **Uniformes versáteis** — evitar excesso de personalização que limite reuso em projetos futuros
- **Sempre "inteligência artificial" por extenso** se texto falar sobre o tema
