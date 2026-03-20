# Weekly CSR/ESG Newsletter — SOP

## Objetivo

Produzir e enviar uma newsletter semanal sobre notícias positivas de CSR (Responsabilidade Social Corporativa) e ESG (Ambiental, Social e Governança) no mundo. A newsletter deve ser bem fundamentada em dados reais, visualmente rica, e enviada toda semana como rascunho no Gmail para revisão humana antes do disparo.

---

## Quando Executar

- **Frequência:** semanal (toda segunda-feira de manhã, ou quando acionado manualmente)
- **Janela de notícias:** últimos 7 dias
- **Saída esperada:** rascunho no Gmail pronto para revisão e envio

---

## Pré-requisitos

Antes de começar, verifique:

- [ ] `PERPLEXITY_API_KEY` está no `.env`
- [ ] `LEONARDO_API_KEY` está no `.env` (obter em app.leonardo.ai/settings/api-keys)
- [ ] `credentials.json` e `token.json` estão na raiz do projeto (Gmail API)
- [ ] `NEWSLETTER_RECIPIENTS` está no `.env` (lista de emails separada por vírgulas)
- [ ] Dependências instaladas: `pip install jinja2 premailer python-dotenv openai requests google-api-python-client google-auth-oauthlib`

---

## Inputs Necessários

| Input | Fonte | Obrigatório |
|---|---|---|
| Notícias da semana | Perplexity API | Sim |
| Nome da newsletter | `.env` ou parâmetro | Sim |
| Nome da edição | Data atual | Sim |
| Trend Watch commentary | Gerado pelo agente | Sim |
| Infográficos | Gamma MCP | Recomendado |
| Lista de destinatários | `.env` | Sim |

---

## Fase 1 — Pesquisa de Notícias

**Tool:** `tools/search_perplexity.py`

```bash
python tools/search_perplexity.py --days 7 --output .tmp/raw_search_$(date +%Y-%m-%d).json
```

Este script roda 6 queries padrão no Perplexity (modelo `sonar-pro`) e salva os resultados brutos.

**O que o agente deve fazer com o output:**

1. Leia o arquivo `.tmp/raw_search_YYYY-MM-DD.json`
2. Analise o conteúdo de cada query result
3. Identifique as 10-15 melhores histórias seguindo os critérios:
   - Publicada nos últimos 7 dias
   - Framing positivo (conquista real, não promessa vaga)
   - Dado quantitativo presente (%, $, toneladas, nº de empresas)
   - Fonte verificável com URL
   - Diversidade de categorias (minimum: 3 Environment, 3 Social, 2 Governance)
4. Para cada história, extraia:
   - `title`: manchete da história
   - `company`: nome da empresa (pode estar vazio se for setor/índice)
   - `source`: nome da publicação
   - `url`: link do artigo
   - `date`: data no formato YYYY-MM-DD
   - `summary`: 2-3 frases resumindo o que aconteceu
   - `category`: "environment" | "social" | "governance"
   - `headline_stat`: o número mais impactante (ex: "34% de redução em emissões Scope 1")
   - `stat_label`: descrição do stat (ex: "redução de emissões de carbono")
   - `what_it_means`: 1 frase sobre a relevância (só para a 1ª história — Story da Semana)
5. Ordene as histórias: a mais impactante primeiro (vira Story da Semana)

**Critérios de descarte:**
- Greenwashing ou promessas sem métricas
- Artigos de opinião sem dados
- Notícias negativas ou controvérsias
- Histórias sem URL verificável

**Edge case:** Se menos de 5 histórias qualificadas forem encontradas, amplie para 14 dias:
```bash
python tools/search_perplexity.py --days 14
```

---

## Fase 2 — Persistência das Histórias

**Tool:** `tools/research_csr_news.py`

Após curar as histórias manualmente, passe o JSON array para o script:

```bash
python tools/research_csr_news.py \
  --stories '[
    {
      "title": "Microsoft atinge neutralidade de carbono em todas as operações",
      "company": "Microsoft",
      "source": "ESG Today",
      "url": "https://esgtoday.com/...",
      "date": "2026-03-18",
      "summary": "A Microsoft anunciou que atingiu a neutralidade de carbono em 100% de suas operações globais...",
      "category": "environment",
      "headline_stat": "100% das operações com carbono neutro",
      "stat_label": "das operações globais com carbono neutro",
      "what_it_means": "Isso demonstra que empresas de grande escala podem atingir metas climáticas dentro do prazo prometido."
    }
  ]'
```

Output: `.tmp/stories_YYYY-MM-DD.json`

---

## Fase 3 — Geração de Imagens (Leonardo AI)

**Tool:** `tools/generate_images_leonardo.py`

```bash
python tools/generate_images_leonardo.py \
  --stories .tmp/stories_2026-03-20.json \
  --output-dir .tmp/images/2026-03-20 \
  --model kino
```

O script gera automaticamente 1 imagem ultra-realista por story baseado no tema detectado (energia renovável, diversidade, floresta, etc.). Usa o modelo **Leonardo Kino XL** por padrão (melhor para fotorrealismo cinemático).

**Modelos disponíveis:**
| Flag | Modelo | Melhor para |
|---|---|---|
| `kino` (padrão) | Leonardo Kino XL | Fotorrealismo cinemático, editorial |
| `photoreal` | Leonardo PhotoReal v2 | Qualidade fotojornalismo |
| `lightning` | Lightning XL | Geração rápida |

**Output:** `.tmp/images/2026-03-20/` com arquivos JPG + `images_manifest.json`

**Como usar no build:**
Após gerar, passe os caminhos para `build_newsletter.py` (o script lerá o `images_manifest.json` automaticamente se estiver na mesma pasta das stories).

---

## Fase 4 — Infográficos (Gamma MCP)

Use o Gamma MCP para criar 2-3 infográficos visuais.

### Infográfico 1: ESG Momentum Dashboard (fixo toda semana)

Prompt para o Gamma:
```
Create a professional infographic titled "ESG Momentum: Week of [DATA]".

Show a dashboard with 3 metric cards at the top:
- 🌿 Environment: [N] new sustainability commitments
- 🤝 Social: [N] workforce and community initiatives announced
- ⚖️ Governance: [$X] in ESG-linked financing

Below, show a horizontal comparison bar or progress indicators.

Key stories this week: [liste as 3 principais histórias em 1 linha cada]

Color scheme: deep greens (#1a472a) and teals, with amber accent (#f4a261).
Style: clean, data-forward, professional, minimal whitespace.
```

### Infográfico 2: Companies Leading This Week

Prompt para o Gamma:
```
Create an infographic titled "This Week's ESG Leaders".

Show a grid highlighting these companies and their achievements:
[liste empresa + conquista para cada story principal]

Style: bold typography, company names prominent, category color badges
(green for environment, blue for social, purple for governance).
White backgrounds with colored accents. Professional and energetic.
```

### Como usar no email

Após gerar no Gamma, copie o `gammaUrl` de cada infográfico e passe para o build:

```json
[
  {
    "title": "ESG Momentum: Semana de 20 de Março",
    "gamma_url": "https://gamma.app/docs/...",
    "description": "Panorama semanal das iniciativas ESG por categoria, com volume comparativo vs semana anterior."
  }
]
```

---

## Fase 4 — Build da Newsletter

**Tool:** `tools/build_newsletter.py`

```bash
python tools/build_newsletter.py \
  --stories .tmp/stories_2026-03-20.json \
  --infographics '[{"title":"ESG Momentum","gamma_url":"https://gamma.app/...","description":"..."}]' \
  --edition "20 de Março, 2026" \
  --name "Good Signal" \
  --tagline "As notícias mais encorajadoras sobre responsabilidade corporativa" \
  --trend "Esta semana, o setor de energia lidera com [insight]. O padrão que se repete é [observação]. Fique de olho em [tendência para próxima semana]." \
  --output .tmp/newsletter_2026-03-20.html
```

**Verificação:** Abra o arquivo `.tmp/newsletter_2026-03-20.html` no Chrome e verifique:
- [ ] Todas as seções estão renderizando
- [ ] Links estão corretos
- [ ] Paleta de cores está consistente
- [ ] Cards das categorias têm cores distintas
- [ ] Stat da Semana está legível e impactante
- [ ] Botão do Gamma abre corretamente

---

## Fase 5 — Revisão e Envio

**Tool:** `tools/send_newsletter.py`

**Passo 5a — Criar rascunho no Gmail:**
```bash
python tools/send_newsletter.py \
  --html-file .tmp/newsletter_2026-03-20.html \
  --subject "Good Signal: [Headline impactante] — 20 de Março, 2026" \
  --mode draft
```

**Passo 5b — Revisar no Gmail:**
- Abra o Gmail
- Encontre o rascunho criado
- Visualize no navegador (não no compose — clique em "Abrir em nova janela")
- Verifique formatação, links e imagens
- Ajuste o subject line se necessário

**Passo 5c — Enviar:**
Envie manualmente pelo Gmail, ou:
```bash
python tools/send_newsletter.py \
  --html-file .tmp/newsletter_2026-03-20.html \
  --subject "Good Signal: ..." \
  --mode send
```

---

## Fórmula do Subject Line

```
[Nome da Newsletter]: [Stat impactante ou headline] — [Data]
```

Exemplos:
- `Good Signal: $47B em financiamento verde e 23 novas metas net-zero — 20 Mar`
- `Good Signal: O maior compromisso climático corporativo do trimestre — 20 Mar`
- `Impacto Real: Semana recorde em iniciativas ESG globais — 20 Mar`

---

## Edge Cases

| Situação | Ação |
|---|---|
| < 5 histórias qualificadas | Ampliar busca para 14 dias (`--days 14`) |
| Gamma falha ao gerar | Remover seção de infográficos (`--infographics '[]'`) e incluir callout de dados em texto |
| Gmail draft falha | Salvar HTML em `.tmp/` e enviar manualmente via Gmail |
| URL de artigo não abre | Substituir pela URL da publicação raiz; manter o conteúdo |
| Categoria ambígua | Classificar pela área de maior impacto da história |

---

## Checklist de Qualidade

Antes de enviar, confirme:

- [ ] 10-15 histórias curadas (mínimo 5 se semana fraca)
- [ ] Pelo menos 1 história por categoria (Environment, Social, Governance)
- [ ] Story da Semana tem `what_it_means` preenchido
- [ ] Stat da Semana é um número específico e verificável
- [ ] Trend Watch tem 2-3 frases com observação original (não genérico)
- [ ] Todos os links abrindo corretamente
- [ ] Preview de email está ok (preheader text aparece no Gmail)
- [ ] Subject line tem máx. 60 caracteres
- [ ] Infográficos do Gamma são acessíveis pelo link
- [ ] Log salvo em `.tmp/send_log.json`

---

## Outputs Esperados

| Arquivo | Descrição |
|---|---|
| `.tmp/raw_search_YYYY-MM-DD.json` | Output bruto da Perplexity |
| `.tmp/stories_YYYY-MM-DD.json` | Histórias curadas e validadas |
| `.tmp/newsletter_YYYY-MM-DD.html` | Email renderizado |
| `.tmp/send_log.json` | Log de envios (histórico acumulado) |

---

## Aprendizados e Atualizações

> Registre aqui qualquer descoberta, limite de API, ou ajuste de prompt que funcione melhor.

- _[Preencher após primeira execução]_
