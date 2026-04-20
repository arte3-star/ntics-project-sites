# Workflow: Uso de Squads de Marketing

## Objetivo
Guiar o agente no uso dos squads de marketing para produzir entregas de alta qualidade em branding, copy, tráfego, storytelling e estratégia.

## Quando usar
- Pedidos de conteúdo de marketing (posts, artigos, newsletters, carrosséis)
- Trabalho de marca (posicionamento, naming, identidade, arquétipo)
- Copywriting (emails, VSL, sales letters, headlines, landing pages)
- Estratégia de tráfego pago (Facebook, Google, YouTube Ads)
- Ofertas e precificação (frameworks Hormozi)
- Narrativa e storytelling (roteiros, pitches, manifestos)
- Decisões estratégicas de negócio (advisory board, c-level)
- Design systems e UX/UI

## Processo

### Passo 1: Identificar o squad certo

Analise o pedido e identifique o domínio:

| Domínio | Squad | Chief |
|---------|-------|-------|
| Texto persuasivo, copy, emails | `copy-squad` | `copy-chief` |
| Marca, posicionamento, identidade | `brand-squad` | `brand-chief` |
| Anúncios, tráfego pago | `traffic-masters` | `traffic-chief` |
| Ofertas, pricing, vendas | `hormozi-squad` | `hormozi-chief` |
| Narrativas, roteiros, pitches | `storytelling` | `story-chief` |
| Dados, métricas, growth | `data-squad` | `data-chief` |
| Design, UI/UX, componentes | `design-squad` | `design-chief` |
| Decisões estratégicas | `advisory-board` | `board-chair` |
| Planejamento executivo | `c-level-squad` | `vision-chief` |
| Movimentos, comunidade | `movement` | `movement-chief` |

**Se o pedido cruza domínios:** Use múltiplos squads em sequência. Ex: novo produto = `brand-squad` (posicionamento) → `copy-squad` (landing page) → `traffic-masters` (campanha).

### Passo 2: Ler o squad

1. Leia `squads/marketing/{squad}/squad.yaml` para entender componentes disponíveis
2. Leia `squads/marketing/{squad}/agents/{chief}.md` para entender o routing interno
3. O chief vai indicar qual especialista é melhor para o caso

### Passo 3: Consultar o especialista

1. Leia o agente especialista indicado pelo chief
2. Use os frameworks e metodologias do especialista para produzir a entrega
3. Siga o tom e estilo do especialista (cada um tem personalidade e approach únicos)

### Passo 4: Executar a task (se aplicável)

Se existe uma task definida em `squads/marketing/{squad}/tasks/`:
1. Leia a task para entender inputs, fases de execução e outputs esperados
2. Siga as fases na ordem
3. Verifique as condições de veto (quando parar)

### Passo 5: Validar qualidade

1. Leia `squads/marketing/{squad}/checklists/output-quality.md`
2. Avalie a entrega contra cada critério
3. Score mínimo: 7.0/10
4. Refine até atingir o padrão

## Skills como atalhos

Para produção de conteúdo recorrente, use os skills (slash commands) que já encapsulam o fluxo completo:

- `/plano-mensal` — Planejamento editorial
- `/roteiro-video` — Script de vídeo 1 min
- `/carrossel-projeto` — Cards de projeto (Leonardo AI)
- `/carrossel-noticias` — Cards de notícias ESG (Perplexity + Leonardo)
- `/artigo-mensal` — Artigo integrado do mês
- `/email-marketing` — Conteúdo de newsletter
- `/newsletter` — HTML + draft Gmail
- `/artigo-site` — Página completa para site

## Referências obrigatórias

Antes de produzir qualquer conteúdo NTICS:
- **Tom de voz:** `brand-book/02-identidade-verbal/tom-de-voz.md`
- **Mensagens-chave:** `brand-book/02-identidade-verbal/mensagens-chave.md`
- **Dados da empresa:** `brand-book/data/brand-data.yaml`
- **Cores e visual:** `brand-book/03-identidade-visual/cores.md`

## Edge Cases

- **Pedido ambíguo entre squads:** Pergunte ao usuário antes de escolher. Ex: "Isso é mais sobre posicionamento (brand-squad) ou sobre o texto da landing page (copy-squad)?"
- **Pedido que precisa de dados reais da NTICS:** Sempre consulte `brand-data.yaml` — nunca invente números
- **Geração de imagens:** Use os padrões Leonardo AI documentados nos skills (nano-banana-2, 4:5 para Instagram, 1152x896 para artigos)
- **Newsletter/email:** Sempre use `contentType: "text/html"` no Gmail draft
