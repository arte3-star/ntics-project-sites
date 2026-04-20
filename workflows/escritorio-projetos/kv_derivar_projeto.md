# Workflow: Derivar KV do Projeto

## Objetivo
A partir do manual de marca oficial do cliente, derivar um KV próprio para o sub-programa/projeto (subbrand): gerar variações do logo do projeto aplicando identidade do cliente, paleta, tipografia e construir uma biblioteca de ícones temáticos via Leonardo AI. Entregar pacote completo para toda produção visual do projeto usar.

## Quando Executar
Após TAP aprovado e antes de qualquer produção de peça (rollup, convite, certificado). **Peça bloqueante**.

## Inputs Necessários

| Input | Fonte | Obrigatório |
|---|---|---|
| Manual de marca do cliente (.PDF) | Cliente via Drive | Sim |
| Nome do projeto | TAP | Sim |
| Temas para ícones | Brief (lista) | Sim |
| Hierarquia de marcas | Brief (qual soberana) | Sim |
| Quantidade de ícones | Default: 12 | Sim |
| Estilo dos ícones | flat · linear · geométrico · preenchido | Sim |
| Pasta Drive destino | Folder KV do projeto | Sim |

## Passo a Passo

### Fase 1 — Coleta do manual cliente
1. Ler manual de marca (.PDF) via MCP Drive ou upload.
2. Extrair:
   - **Paleta CMYK + hex** de todas as cores principais e secundárias
   - **Tipografia** (família, pesos permitidos, tipografia secundária)
   - **Regras de aplicação do logo cliente** (área de proteção, versões, restrições)
   - **Regras gerais** (o que pode e o que não pode)
3. Salvar em `.tmp/kv_cliente_extrato.json`.

### Fase 2 — Gate de design
Invocar `/design-briefing` para confirmar com o usuário:
- Estilo dos ícones (flat · linear · gradient · isométrico)
- Paleta derivada (qual cor vai ser a de destaque do projeto)
- Tipografia do projeto (mesma do cliente? secundária?)
- Formato do manual PDF (A4 horizontal é o default)

### Fase 3 — Logo do projeto
Gerar via Illustrator (`tools/adobe/kv_derivar.py`):
1. Variações: positiva, negativa, colorida, monocromática
2. Orientações: horizontal, vertical
3. Se o projeto tem subtítulo/edição (ex: "Estação Samarco" sem subtítulo vs. "Negócio Cultural 3ª Edição"), gerar com e sem.

Camadas nomeadas no `.AI`: `LOGO_PRINCIPAL`, `LOGO_NEGATIVO`, `LOGO_MONO`, `LOGO_HORIZONTAL`, `LOGO_VERTICAL`.

### Fase 4 — Biblioteca de ícones via Leonardo AI
Consultar `workflows/marketing/referencia/leonardo_ai_core.md` para payload atualizado.

**Estratégia:**
1. Gerar 1 ícone-referência com estilo desejado (prompt explícito: "flat icon, single color, minimalist, [tema]", color reference = cor de destaque do KV).
2. Usar esse ícone como **style reference** para os demais 11.
3. Temas comuns para projetos NTICS:
   - empreendedorismo (lâmpada, gráfico de crescimento)
   - inteligência artificial (chip, neural)
   - vendas e marketing digital (megafone, grafismo social)
   - atendimento ao cliente (headset, aperto de mão)
   - turismo e hospitalidade (mala, pin de mapa)
   - culinária sustentável (panela, folha)
   - aproveitamento integral (ingredientes, ciclo)
   - precificação (etiqueta, balança)
   - beleza — cabelo (tesoura)
   - beleza — maquiagem (pincel, paleta)
   - beleza — manicure (esmalte, mão)
   - capacitação profissionalizante (certificado, formatura)

**Não gerar texto** nos ícones (Leonardo erra em palavras).

### Fase 5 — Vetorizar ícones
Leonardo entrega PNG. Converter para SVG vetorial via `/vetorizar` (Image Trace do Illustrator).

Entregar:
- `.PNG 512×512 px` transparente
- `.SVG` vetorial

### Fase 6 — Manual PDF
Montar manual de aplicação visual em A4 horizontal (297×210 mm, 300 dpi):
- Capa: logo do projeto grande
- Página 2: variações do logo
- Página 3: paleta (CMYK + hex + nome)
- Página 4: tipografia (famílias + pesos + uso)
- Página 5: área de proteção do logo
- Página 6-7: aplicações corretas e incorretas
- Página 8: hierarquia de marcas (cliente soberana + NTICS realização)
- Página 9-10: biblioteca de ícones (grid com todos os 12)
- Página 11: restrições gerais
- Contracapa: créditos

Template base: `templates/manual_kv_a4.ai` (se existir) ou gerar do zero.

### Fase 7 — Entrega
Subir no folder destino:
```
KV ESTACAO SAMARCO EMPREENDEDORISMO/
├── logos/
│   ├── logo_projeto.ai
│   ├── logo_projeto_negativo.ai
│   ├── logo_projeto_horizontal.ai
│   ├── logo_projeto_vertical.ai
│   └── logo_projeto.png (preview)
├── icones/
│   ├── empreendedorismo.svg + .png
│   ├── inteligencia_artificial.svg + .png
│   ├── ... (12 ícones)
├── manual.pdf
└── README.md (como usar)
```

Comentar na task ClickUp do KV com os links.

## Output Esperado
- Pacote completo (logos + ícones + manual) na pasta Drive do projeto
- Nomenclatura em snake_case para arquivos internos, MAIÚSCULAS para pasta destino

## Tool Utilizado
`tools/adobe/kv_derivar.py` + Leonardo AI API + `tools/adobe/jsx/manual_pdf.jsx`

## Dependências
- Leonardo AI: `workflows/marketing/referencia/leonardo_ai_core.md`
- Adobe Illustrator: reusa `tools/adobe/adapt_artwork_illustrator.py` como base

## Regras críticas
- **Logo cliente soberana** — não inventar cores/tipografia se o manual existe
- **Ícones coerentes** — mesma cor-assinatura, mesmo peso visual, mesmo estilo em todos
- **Biblioteca reutilizável** — entregar como modelo NTICS para programas do mesmo tipo
- **Sem régua MinC** quando projeto não é Lei de Incentivo
- **Nunca usar sigla "IA"** — ícone "inteligência artificial" é OK, mas escrito por extenso
