# Workflow: Arte para Impressão CMYK

## Objetivo
Gerar arte vetorial pronta para gráfica (.AI + .PDF/X-4 CMYK 300 dpi com sangria + .PNG preview) para impressos físicos de estrutura de campo e peças cenográficas.

## Quando Executar
Após o KV do projeto estar pronto (logo, paleta, tipografia, biblioteca de ícones). Para cada peça física que vai à gráfica.

## Tipos de peça suportados

| Peça | Dimensão padrão | Sangria | Observação |
|---|---|---|---|
| Rollup | 85 × 200 cm | 3 cm lateral e inferior | PDF 91×203 cm |
| Pantojet / Backdrop inflável | 2,0 × 2,0 m | 5 cm cada lado | NUNCA boxtruss |
| Wind banner | 80 × 300 cm | 3 cm | Vertical, leitura à distância |
| Saia de bancada | 90 × 200 cm | 3 cm | Lona ou tecido |
| Placa de fotos | 50 × 30 cm | 2 cm | PVC ou acrílico |
| Moldura espelho (vinil) | variável | faca de corte | Vinil adesivo |

## Inputs Necessários

| Input | Fonte | Obrigatório |
|---|---|---|
| Tipo de peça | Lista acima | Sim |
| Dimensões finais (cm) | Brief | Sim (se custom) |
| Sangria (cm) | Tabela acima ou custom | Sim |
| Paleta CMYK | KV do projeto | Sim |
| Logos vetoriais (.AI/.EPS/.SVG) | KV do projeto | Sim |
| Hierarquia de marcas | Brief (qual soberana, qual realização) | Sim |
| Conteúdo textual | Brief | Sim |
| Ícones do enxoval | KV (opcional) | Não |
| Quantidade de modelos | 1 por default, 6 para rollup, 4 para placa | Sim |

## Passo a Passo

### Fase 1 — Coleta e validação
1. Perguntar tipo de peça → preencher defaults da tabela.
2. Validar que o KV está pronto (paleta CMYK, não RGB).
3. Validar logos — **se vier PNG, abortar e pedir vetor**.
4. Para peças multi-modelo (rollups 6, placas 4), receber conteúdo textual de cada.

### Fase 2 — Preparação config
Montar JSON:
```json
{
  "type": "rollup",
  "models": [
    {
      "name": "Rollup Patrocinador 1",
      "title": "A SAMARCO APRESENTA:",
      "body": null,
      "hero_logo": "estacao_samarco_grande.ai"
    },
    { "name": "Rollup Sabores", "title": "ESTAÇÃO SABORES", "subtitle": "Culinária Sustentável", "body": "50 horas de formação profissionalizante..." },
    ...
  ],
  "dimensions_cm": { "width": 85, "height": 200 },
  "bleed_cm": 3,
  "palette_cmyk": {
    "primary": [100, 65, 0, 45],
    "accent":  [0, 40, 100, 0]
  },
  "fonts": { "display": "Montserrat-Black", "body": "OpenSans-Regular" },
  "logos": {
    "soberana_ai": "logos/estacao_samarco.ai",
    "realizacao_ai": "logos/ntics.ai",
    "apresenta_ai": "logos/samarco_corporativa.ai"
  },
  "hierarchy": {
    "top": "apresenta",
    "center": "soberana",
    "bottom_right": "realizacao"
  },
  "output_dir": ".tmp/arte_impressao/rollups/"
}
```

### Fase 3 — Execução
```bash
python tools/adobe/arte_impressao.py --config .tmp/arte_impressao_config.json
```

O tool:
1. Abre Illustrator via COM (pywin32).
2. Cria artboard no tamanho exato com sangria.
3. Seta espaço de cor CMYK.
4. Para cada modelo:
   - Cria camadas nomeadas: `SANGRIA`, `LOGO_APRESENTA`, `LOGO_SOBERANA`, `LOGO_REALIZACAO`, `KV_PADRONAGEM`, `TEXTO`
   - Importa logos vetoriais (preserva curvas, não rasteriza)
   - Posiciona conforme hierarquia
   - Aplica tipografia e paleta
   - Converte fontes em outline no final
5. Exporta:
   - `.AI` nativo (camadas preservadas para edição futura)
   - `.PDF/X-4` (CMYK, 300 dpi, fontes em outline, sangria preservada, marcas de corte)
   - `.PNG` preview RGB 1200 px maior lado

### Fase 4 — Validação automática
Rodar `/revisao-arte-impressao` sobre o PDF gerado:
- CMYK ✓
- DPI ≥ 300 ✓
- Sangria ≥ mínimo ✓
- Fontes em outline ✓
- Logos vetoriais ✓
- Hierarquia respeitada ✓

Se `🔴 Fail` em algum item crítico, retornar erro e NÃO entregar.

### Fase 5 — Entrega
1. Subir os 3 arquivos (AI + PDF + PNG) na pasta destino do Drive.
2. Reportar ao usuário:
   - Lista dos modelos gerados
   - Links dos arquivos
   - Resultado da revisão
3. Comentar na task ClickUp (se integrado).

## Output Esperado
- N `.AI` (um por modelo)
- N `.PDF/X-4` prontos para gráfica
- N `.PNG` preview

## Tool Utilizado
`tools/adobe/arte_impressao.py` + `tools/adobe/jsx/arte_impressao.jsx`

## Integração
- Depende de: `kv-derivar` (precisa KV pronto)
- Valida com: `revisao-arte-impressao` (obrigatório antes de entregar)
- Pode ser orquestrado por: `time-design`

## Regras críticas NTICS
- **CMYK obrigatório** — RGB aborta
- **Sangria mínima**: 3 mm universal, 3 cm rollup, 5 cm pantojet
- **DPI ≥ 300** em imagens raster (logos devem ser vetoriais)
- **Fontes em outline** no PDF final
- **Sem régua MinC** se projeto não é Lei de Incentivo
- **Sempre "inteligência artificial" por extenso**, nunca sigla
