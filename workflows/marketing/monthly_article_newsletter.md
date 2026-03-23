# Workflow: Newsletter Mensal com Artigo NTICS + Notícias ESG

## Objetivo

Produzir o email marketing mensal da NTICS que:
1. **Abre com o artigo do mês** — herói visual com imagem, título, excerpt e CTA para o site
2. **Traz as notícias ESG da semana** — curadoria positiva com imagens contextuais
3. **Inclui a seção de Leis & Incentivos** — oportunidades fiscais para empresários patrocinadores

---

## Quando usar este workflow

- Uma vez por mês, após a publicação de um novo artigo CSR/ESG no site da NTICS
- Combinar com a newsletter semanal da semana de publicação do artigo

---

## Entradas necessárias

| Campo | Descrição | Obrigatório |
|-------|-----------|-------------|
| `article.title` | Título exato do artigo publicado | ✅ |
| `article.url` | URL completa do artigo no site | ✅ |
| `article.excerpt` | 2–3 frases do argumento central | ✅ |
| `article.image_url` | Imagem destacada do artigo (URL pública) | Recomendado |
| `article.author` | Autor (ex: "Equipe NTICS") | Opcional |
| `article.read_time` | Tempo de leitura (ex: "5 min") | Opcional |
| `article.category` | Categoria para o label (ex: "Legislação & Incentivos") | Opcional |

---

## Passos

### 1. Publicar o artigo no site

- Publicar o artigo CSR no WordPress/site NTICS
- Garantir que há uma imagem destacada (featured image) de boa qualidade
- Copiar: título, URL, excerpt (2–3 frases), URL da imagem

### 2. Coletar notícias ESG da semana

Executar a busca no Perplexity:
```bash
python tools/search_perplexity.py --days 7 --output .tmp/raw_search_YYYY-MM-DD.json
```

Depois curar e estruturar as histórias:
```bash
python tools/research_csr_news.py \
  --input .tmp/raw_search_YYYY-MM-DD.json \
  --output .tmp/stories_YYYY-MM-DD.json
```

### 3. Buscar imagens para as notícias

```bash
python tools/fetch_images_unsplash.py \
  --stories .tmp/stories_YYYY-MM-DD.json \
  --output .tmp/stories_with_images_YYYY-MM-DD.json
```

### 4. Montar o arquivo de dados

Copiar `.tmp/newsletter_data_with_images.json` como base e atualizar:

```json
{
  "newsletter_name": "ESG em Foco",
  "tagline": "Notícias que transformam — curadoria ESG/CSR semanal da NTICS Projetos",
  "edition": "20 de Março, 2026",
  "logo_url": "https://ntics.com.br/wp-content/uploads/2023/05/logo-ntics-branco-01.svg",
  "trend_watch": "...",
  "article": {
    "title": "Como a Lei Rouanet pode transformar o impacto social da sua empresa",
    "url": "https://ntics.com.br/blog/...",
    "excerpt": "2–3 frases do argumento central do artigo",
    "image_url": "https://...",
    "author": "Equipe NTICS",
    "read_time": "5 min",
    "category": "Legislação & Incentivos"
  },
  "stories": [...],
  "incentives": [...],
  "infographics": [...]
}
```

Salvar como `.tmp/newsletter_YYYY-MM.json`

### 5. Gerar o HTML

```bash
python tools/build_newsletter.py \
  --data .tmp/newsletter_YYYY-MM.json \
  --output .tmp/newsletter_YYYY-MM.html
```

Verificar output:
- Bloco "Artigo do Mês" aparece no topo, antes do Destaque da Semana
- Imagem do artigo renderiza (240px de altura)
- Título grande e excerpt legível
- Botão "Ler artigo completo →" visível em verde
- Seção "Leis & Incentivos" presente (se incentives não vazio)
- Restante da newsletter intacto

### 6. Criar draft no Gmail

```bash
python tools/send_newsletter.py \
  --html-file .tmp/newsletter_YYYY-MM.html \
  --subject "ESG em Foco | [Título curto do artigo] — [Data]" \
  --to "lucas@ntics.com.br" \
  --mode draft
```

> Alternativa se credentials.json não disponível: usar agente Claude com o MCP Gmail para criar o draft

### 7. Revisar e enviar

- Abrir o draft em https://mail.google.com/mail/u/0/#drafts
- Verificar visual no webmail (imagens, botões, layout mobile)
- Adicionar lista de destinatários (ou configurar `NEWSLETTER_RECIPIENTS` no `.env`)
- Enviar

---

## Estrutura do email (ordem das seções)

1. **Header** — Logo NTICS + nome da newsletter + data
2. **Artigo do Mês** ← novo bloco (só aparece quando `article` está presente)
3. **Destaque da Semana** — stat hero da história principal
4. **Story da Semana** — história featured com imagem
5. **Wins da Semana** — Meio Ambiente / Social / Governança
6. **Leis & Incentivos** — incentivos fiscais para patrocinadores
7. **Dados & Infográficos**
8. **Trend Watch**
9. **Footer**

---

## Notas de campo

- **Sem `article`**: o email funciona normalmente sem o bloco do artigo (retrocompatível)
- **Imagem do artigo**: usar proporção ~16:9, mínimo 600×240px, fundo não branco
- **Excerpt**: 2–3 frases, evitar bullet points — tom editorial/narrativo
- **Categoria**: aparece como badge verde ao lado do label "📝 Artigo do Mês"
- **Preheader**: quando `article` está presente, o preheader usa o excerpt (não o trend_watch)
- **CSS warnings de premailer** (`object-fit`, `-ms-*`): normais e inofensivos — são propriedades de email client que o premailer não conhece mas passa intactas

---

## Arquivos chave

| Arquivo | Papel |
|---------|-------|
| `tools/build_newsletter.py` | Renderiza o HTML a partir dos dados |
| `tools/templates/newsletter.html` | Template Jinja2 (inclui bloco `{% if article %}`) |
| `.tmp/newsletter_data_with_images.json` | Exemplo de dados completo com `article` |
| `tools/send_newsletter.py` | Envia ou cria draft via Gmail API |
