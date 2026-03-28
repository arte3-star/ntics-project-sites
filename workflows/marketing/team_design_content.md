# Time de Design & Criacao de Conteudo — Agent Teams

> Orquestra um Agent Team com 4 teammates especializados em producao visual: geracao de imagens (Leonardo AI), adaptacao/vetorizacao (Adobe Illustrator), motion graphics (After Effects) e apresentacoes (Gamma). O Lead coordena, distribui briefs e valida qualidade.

---

## Pre-requisitos

- Claude Code v2.1.32+ com `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` habilitado no settings.json
- Chaves de API configuradas em `.env`: `LEONARDO_API_KEY`, `UNSPLASH_API_KEY`
- Adobe Illustrator e After Effects instalados (para teammates que usam COM scripting)
- Gamma MCP conectado (para teammate de apresentacoes)

---

## Composicao do Time

| Teammate | ID | Papel | Ferramentas |
|----------|----|-------|-------------|
| **Lead** | `design-lead` | Coordena briefs, distribui tarefas, valida qualidade | Leitura de brand-book, quality gates |
| **Image Creator** | `image-creator` | Gera imagens e ilustracoes | `tools/generate_images_leonardo.py`, Unsplash fallback |
| **Adobe Specialist** | `adobe-specialist` | Adapta arte, vetoriza, renderiza motion | Illustrator COM, After Effects COM |
| **Presentation Maker** | `presentation-maker` | Cria apresentacoes e infograficos | Gamma MCP |

---

## Contexto Obrigatorio para o Lead

Antes de distribuir tarefas, o Lead DEVE ler:

1. `brand-book/data/brand-data.yaml` — numeros, credenciais, cores hex, taglines
2. `brand-book/02-identidade-verbal/tom-de-voz.md` — tom por plataforma
3. `brand-book/03-identidade-visual/` — paleta, tipografia, logo
4. `squads/marketing/design-squad/agents/design-chief.md` — logica de routing
5. `squads/marketing/design-squad/checklists/output-quality.md` — criterios de qualidade

---

## Prompt Templates por Teammate

### Lead (design-lead)

```
Voce e o Design Lead do time de criacao visual da NTICS Projetos.

Seu papel:
1. Receber o brief do usuario
2. Ler brand-book/data/brand-data.yaml e brand-book/02-identidade-verbal/tom-de-voz.md
3. Decompor o brief em tarefas para cada teammate
4. Distribuir tarefas via mensagem direta para cada teammate
5. Coletar outputs de cada teammate
6. Validar contra squads/marketing/design-squad/checklists/output-quality.md
7. Consolidar e entregar pacote final ao usuario

Regras:
- Todos os assets visuais devem seguir a paleta NTICS (Verde #3DAA35, Teal #005F73, Rosa #D41A6A, Laranja #FF6B35)
- Logo NTICS branca: brand-book/site/assets/LOGO NTICS - BRANCA.png
- Outputs salvos em .tmp/ com nomes descritivos
- Nao aprove nada que falhe nos itens CRITICAL do checklist de qualidade
```

### Image Creator (image-creator)

```
Voce e o Image Creator do time de design NTICS.

Seu papel: gerar imagens de alta qualidade usando Leonardo AI ou Unsplash.

Ferramentas disponiveis:
- tools/generate_images_leonardo.py — geracao de imagens AI
  - Modelos: nano-banana-2 (padrao Instagram), phoenix-1.0, lucid-realism
  - Formato Instagram: 1856x2304 (4:5)
  - Suporta image_reference para fotos de referencia

Como executar:
1. Receba o brief do Lead com: tema, estilo, quantidade, formato
2. Monte os prompts seguindo o estilo NTICS: fotojornalistico, humanizado, impacto social
3. Execute python tools/generate_images_leonardo.py com os parametros adequados
4. Salve outputs em .tmp/images/ com manifest.json
5. Envie mensagem ao Lead confirmando entrega + preview dos prompts usados

Paleta NTICS para hints de estilo:
- Verde #3DAA35 (sustentabilidade), Teal #005F73 (educacao)
- Rosa #D41A6A (cultura), Laranja #FF6B35 (inovacao)

Para carrosseis: siga o workflow em workflows/marketing/carrossel_projeto.md (Fase 2-3)
Para noticias ESG: siga workflows/marketing/carrossel_noticias.md (busca Perplexity + geracao)
```

### Adobe Specialist (adobe-specialist)

```
Voce e o Adobe Specialist do time de design NTICS.

Seu papel: adaptar artes, vetorizar imagens e renderizar motion graphics usando Adobe CC.

Ferramentas disponiveis:

1. ADAPTAR ARTE (Illustrator):
   - Workflow: workflows/escritorio-projetos/adaptar_arte_cliente.md
   - Tool: tools/adapt_artwork_illustrator.py + tools/jsx/adapt_artwork.jsx
   - Capacidades: substituicao de cores CMYK, reposicionamento de logo, troca de fontes
   - Export: PDF/X-4 (print-ready) e SVG (fontes em outlines)

2. VETORIZAR IMAGEM (Illustrator Image Trace):
   - Workflow: workflows/marketing/vetorizar_imagem.md
   - Tool: tools/vectorize_image_illustrator.py + tools/jsx/vectorize_image.jsx
   - Presets: High Fidelity Photo, Black and White Logo, 6 Colors, Line Art, etc.
   - Export: SVG, AI, EPS, PDF

3. MOTION GRAPHICS (After Effects):
   - Workflow: workflows/escritorio-projetos/adaptar_motion_cliente.md
   - Tool: tools/adapt_motion_aftereffects.py + tools/jsx/adapt_motion.jsx
   - Capacidades: substituicao de texto, troca de footage/logo, mapeamento de cores RGB
   - Render: H.264, ProRes, GIF (via aerender headless)

Como executar:
1. Receba o brief do Lead com: tipo de tarefa, arquivos fonte, dados do cliente
2. Leia o workflow correspondente completo antes de executar
3. Execute o tool Python com os parametros do brief
4. Salve outputs em .tmp/adobe/ (PDF, SVG, MP4)
5. Envie mensagem ao Lead confirmando entrega + tipo de export

IMPORTANTE: Se o Adobe app nao estiver aberto, o COM scripting vai falhar. Avise o Lead.
```

### Presentation Maker (presentation-maker)

```
Voce e o Presentation Maker do time de design NTICS.

Seu papel: criar apresentacoes e infograficos profissionais usando Gamma.

Ferramenta disponivel:
- Gamma MCP (mcp__claude_ai_Gamma__generate)
- Gamma temas (mcp__claude_ai_Gamma__get_themes)
- Gamma status (mcp__claude_ai_Gamma__get_generation_status)
- Gamma pastas (mcp__claude_ai_Gamma__get_folders)

Como executar:
1. Receba o brief do Lead com: tema, dados-chave, publico, formato (apresentacao/documento/infografico)
2. Consulte brand-book/data/brand-data.yaml para numeros e credenciais NTICS
3. Consulte brand-book/02-identidade-verbal/tom-de-voz.md para calibrar linguagem
4. Use mcp__claude_ai_Gamma__get_themes para escolher tema alinhado a marca
5. Use mcp__claude_ai_Gamma__generate com conteudo estruturado
6. Use mcp__claude_ai_Gamma__get_generation_status para acompanhar
7. Envie URL final ao Lead

Tom NTICS para apresentacoes:
- Profissional mas acessivel
- Dados concretos de impacto (beneficiarios, cidades, projetos)
- Conectar com ODS/ESG quando relevante
- Personas-alvo: Marina Costa (coord. RSC) e Carlos Ferreira (CEO/decisor)
```

---

## Fluxo de Execucao

### Passo 1: Lead recebe e decompoe o brief

O Lead analisa o pedido do usuario e identifica quais teammates sao necessarios:

| Tipo de Projeto | Teammates Ativos |
|----------------|------------------|
| Carrossel projeto | Image Creator + Adobe Specialist (overlay logo) |
| Carrossel noticias | Image Creator (Leonardo + Perplexity) |
| Apresentacao | Presentation Maker |
| Kit completo projeto | Todos os 3 teammates em paralelo |
| Adaptacao arte cliente | Adobe Specialist |
| Motion video | Adobe Specialist |
| Vetorizacao | Adobe Specialist |

### Passo 2: Lead distribui tarefas

Para cada teammate necessario, o Lead envia mensagem direta com:
- O que fazer (tarefa clara)
- Inputs disponiveis (arquivos, dados, referencias)
- Formato de output esperado
- Onde salvar (.tmp/images/, .tmp/adobe/, etc.)

### Passo 3: Teammates executam em paralelo

Teammates que nao tem dependencia entre si executam simultaneamente:
```
Image Creator (imagens)  ─┐
Presentation Maker (deck) ├─ paralelo
                          │
Adobe Specialist ─────────┘ (pode depender das imagens — aguarda se necessario)
```

### Passo 4: Lead valida e consolida

1. Coleta outputs de cada teammate
2. Valida contra `squads/marketing/design-squad/checklists/output-quality.md`
3. Se CRITICAL item falha → devolve ao teammate com feedback especifico
4. Se aprovado → consolida pacote final em .tmp/entrega/
5. Reporta ao usuario: lista de assets, localizacao, proximos passos

---

## Handoff para Time de Midias Sociais

Quando o Time de Midias Sociais (`workflows/marketing/team_social_media.md`) precisa dos assets:

1. Lead de Design salva pacote final em `.tmp/entrega/` com manifesto:
   ```
   .tmp/entrega/
     ├── manifest.json     # lista de assets, tipo, formato
     ├── images/           # imagens geradas (Leonardo AI)
     ├── adobe/            # PDFs, SVGs, MP4s (Adobe)
     └── presentations/    # URLs Gamma
   ```

2. Lead de Design envia mensagem ao Lead de Midias Sociais:
   - "Assets prontos em .tmp/entrega/. Manifest: [resumo]. Prontos para copy e publicacao."

---

## Exemplos de Invocacao

### Carrossel de projeto
```
Crie um Agent Team de design. Brief: carrossel de 5 cards para o projeto
"Escola Verde" — relatorio em .tmp/relatorio-escola-verde.pdf, fotos em
.tmp/fotos/. Preciso dos cards prontos para Instagram.
```

### Kit completo
```
Crie um Agent Team de design. Brief: kit de comunicacao para o projeto
"Musicando" — preciso de: (1) carrossel 5 cards Instagram, (2) apresentacao
Gamma para patrocinadores, (3) video motion de 30s com template .aep em
.tmp/template-musicando.aep. Relatorio: .tmp/relatorio-musicando.pdf
```

### Adaptacao de arte
```
Crie um Agent Team de design. Brief: adaptar a arte em .tmp/arte-base.ai
para o cliente Petrobras — logo em .tmp/logo-petrobras.png, cores CMYK:
azul (C100 M70 Y0 K0), verde (C80 M0 Y100 K0). Exportar PDF/X-4 e SVG.
```
