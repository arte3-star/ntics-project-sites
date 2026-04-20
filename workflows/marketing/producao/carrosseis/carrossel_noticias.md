# Carrossel de Boas Noticias ESG — NTICS Projetos

> Pesquisa noticias positivas da semana, gera 9 cards visuais (capa + 7 noticias + CTA) via Leonardo AI Nano Banana 2, revisa qualidade, adiciona logo NTICS no CTA via Pillow, cria descricao com links e salva tudo organizado numa pasta da semana.

> 📚 **Referência Leonardo AI:** Este workflow tem estrutura validada — siga-o como fonte primária. Se surgir erro de API, dúvida sobre payload ou resultado visual inesperado, consulte `workflows/marketing/referencia/leonardo_ai_core.md` como base de conhecimento complementar (erros conhecidos, modos, exemplos).

---

## APIs Utilizadas

| API | Uso | Modelo/Config |
|-----|-----|---------------|
| Serper.dev /news | Buscar candidatos de noticias reais com URL verificada | endpoint: `/news`, q: "ESG sustentabilidade responsabilidade social" |
| Claude Haiku | Selecionar 7 melhores noticias e redigir todos os campos | Selecao editorial + redacao de titulo, resumo, texto_card, cena_foto, categoria |
| Leonardo AI | Gerar TODOS os cards (capa + noticias + CTA base) | model: nano-banana-2, 1856x2304 (4:5), v2 API |
| Serper.dev /images | Buscar foto editorial real via Google Images | `fetch_images_google.py` |
| Pillow | APENAS: colar logo NTICS no card CTA | Nao usar para composicao de cards |

> **Arquitetura:** Todo card e gerado pelo Leonardo. Pillow so e chamado uma vez, para aplicar o logo no ultimo card. Cascata de imagens: Serper → Leonardo.

### Chaves (variaveis de ambiente)
- `LEONARDO_API_KEY`
- `SERPER_API_KEY` (busca de noticias /news + Google Images para fotos editoriais)
- `ANTHROPIC_API_KEY` (Claude Haiku para selecao e redacao das noticias)

---

## Script

```bash
python tools/content-gen/gerar_carrossel_noticias_v2.py --semana YYYY-MM-DD
```

**Flags uteis:**
- `--skip-perplexity` — reusa `noticias_raw.json` do cache (nao gasta tokens Perplexity)
- `--skip-images` — reusa fotos originais do cache (nao faz Serper)
- `--skip-capa-leo` — usa capa teal solida (economiza 1 geracao Leonardo)
- `--tematica {tema}` — filtra noticias por tema especifico
- `--cards capa,2,5,cta` — regenera APENAS os cards especificados (economiza creditos Leonardo)

**Correcao cirurgica de cards:**
```bash
# Regenerar so a capa
python tools/content-gen/gerar_carrossel_noticias_v2.py --semana 2026-04-07 --skip-perplexity --skip-images --cards capa

# Regenerar so o card 3 e o CTA
python tools/content-gen/gerar_carrossel_noticias_v2.py --semana 2026-04-07 --skip-perplexity --skip-images --cards 3,cta

# Regenerar cards 2 e 5 (por numero de sequencia)
python tools/content-gen/gerar_carrossel_noticias_v2.py --semana 2026-04-07 --skip-perplexity --skip-images --cards 2,5
```
> **Regra:** Sempre combinar `--cards` com `--skip-perplexity --skip-images` para correcoes pontuais. O numero no `--cards` e a posicao final do card (2 = primeira noticia, 3 = segunda, etc.).

---

## Inputs do Usuario

| Campo | Tipo | Obrigatorio | Descricao |
|-------|------|-------------|-----------|
| `semana` | string | Sim | Data da semana (ex: "2026-03-22") |
| `tematica` | string | Nao | Tema especifico para filtrar noticias. Se vazio, busca noticias gerais ESG |

---

## Execucao

### Fase 1: Verificar Noticias Anteriores (Anti-Repeticao)

Ler `descricao.txt` e `manifest.json` de TODOS os carrosseis anteriores em `output/marketing/carrosseis/noticias/*/` para coletar:
- URLs ja utilizadas
- Titulos ja utilizados
- Empresas/organizacoes ja destacadas

Montar lista de exclusao para passar ao Perplexity.

---

### Fase 2: Pesquisa de Noticias (Serper /news + Claude Haiku)

**Etapa 1a — Serper /news:** Buscar candidatos com URL verificada
- Endpoint: `POST https://google.serper.dev/news`
- Query: `"ESG sustentabilidade responsabilidade social"` + variantes tematicas
- Verificar cada URL com HEAD request — descartar 404s
- Coletar 20-30 candidatos unicos

**Etapa 1b — Claude Haiku seleciona e redige:** A partir dos candidatos verificados, Claude seleciona as 7 melhores e preenche todos os campos abaixo. URLs fabricadas sao impossiveis — toda noticia tem URL verificada do Serper.

**Campos obrigatorios no JSON de resposta:**

| Campo | Descricao |
|-------|-----------|
| `titulo` | Max 10 palavras, sem siglas nao explicadas |
| `resumo` | 3-4 frases: O QUE, QUEM, POR QUE importa |
| `texto_card` | Max 2 frases / 25 palavras — resumo ultra-curto para o card visual |
| `highlight_words` | Array de 1-3 palavras/numeros mais importantes (ex: `["R$30 mi", "biorrefino"]`) |
| `fonte` | Nome do veiculo |
| `url` | URL da materia original |
| `categoria` | Uma de: ESTRATEGIA CORPORATIVA, INFRAESTRUTURA, RECURSOS HIDRICOS, EDUCACAO, COOPERACAO GLOBAL, FINANCAS VERDES, ENERGIA, BIODIVERSIDADE, TECNOLOGIA |
| `cena_foto` | Descricao estruturada em ingles para gerar foto realista (ver formato abaixo) |

**Formato obrigatorio do campo `cena_foto`:**
```
[angulo de camera] + [objeto/local com nome exato] + [elementos visuais concretos] + [condicao de luz]
```
Exemplos:
- `"aerial view of Porto Itapoa container terminal Santa Catarina Brazil at golden hour, large yellow cranes loading colorful shipping containers, calm Atlantic ocean"`
- `"close-up of Petrobras Replan refinery Paulinia Sao Paulo, steel distillation towers and industrial pipelines, workers in yellow hard hats and orange vests, morning blue light"`
- `"wide shot of Wagyu cattle grazing on certified pasture in Mato Grosso Brazil, lush green rolling hills, farmer in straw hat checking herd, afternoon golden light"`

> **REGRA:** Sempre estruturar como [angulo] + [nome exato do local/empresa/objeto] + [elementos especificos] + [luz]. Quanto mais especifico, melhor o resultado. Evitar descricoes genericas como "a professional working" ou "a meeting room".

> **PROIBIDO em cena_foto:** Nunca combinar arquitetura com vegetacao integrada ("modern building with green vegetation on facade", "sustainable architecture with lush greenery"). O Leonardo gera prédios cobertos de plantas impossiveis — resultado parece fantasia, nao fotografia. Tambem evitar a palavra "sustainable" ou "sustainability" ao descrever edificios ou estruturas. Se a noticia e sobre empresa, usar so o predio limpo. Se e sobre natureza/biodiversidade, usar so a paisagem. Nunca misturar os dois no mesmo enquadramento.

**Diversidade de fontes:** Maximo 2 noticias da mesma fonte por edicao.

**Prompt template para Claude Haiku (recebe lista de candidatos Serper):**
```
A partir dos candidatos abaixo (todos com URL verificada), selecione as 7 melhores noticias positivas sobre ESG, sustentabilidade e responsabilidade social corporativa no Brasil e no mundo.

ESCOPO GEOGRAFICO: Brasil e mundo. Noticias internacionais com impacto mensuravel ou licao aplicavel ao mercado brasileiro sao bem-vindas. Fontes como Reuters, Bloomberg Green, GreenBiz, ESG Today, Carbon Brief, UN News, Guardian Environment, Le Monde sao aceitas alem das brasileiras.

CRITERIO EDITORIAL — priorize noticias que:
- Mostrem impacto concreto: dados, numeros, metas alcancadas, projetos lancados
- Sejam positivas, inspiradoras e relevantes para gestores de empresas

REJEICAO AUTOMATICA (nao selecionar):
- Qualquer noticia com framing de problema ou fracasso. Palavras-sinal de rejeicao no titulo/snippet: "trava", "enfrenta", "sofre", "cai", "desacelera", "crise", "problema", "fracasso", "queda", "risco". Na duvida, escolher a noticia mais positiva.
- Noticias puramente especulativas sem dados concretos
- Noticias comerciais sem dimensao social ou ambiental clara

DIVERSIDADE OBRIGATORIA:
- No maximo 2 noticias do mesmo veiculo/fonte
- Cada noticia deve cobrir um TEMA diferente — nao escolher duas sobre energia, ou duas sobre reportes/regulacao. Buscar variedade: biodiversidade, tecnologia, educacao, financas, agro, etc.
- Nao repetir TEMA das semanas anteriores, mesmo que a noticia seja de empresa diferente. Ex: se "energia solar + ESG" foi coberto na semana passada, rejeitar qualquer outra noticia de energia solar esta semana.
{exclusao_hint}

Para cada noticia, forneca:
1) titulo: Max 10 palavras, framing positivo
2) resumo: Paragrafo (3-4 frases) O QUE, QUEM, IMPACTO, POR QUE importa
3) texto_card: Resumo ultra-curto (max 2 frases, 25 palavras)
4) highlight_words: Lista de 2-4 palavras INDIVIDUAIS do titulo para destacar em amarelo
5) fonte: nome do veiculo
6) url: URL da materia
7) categoria: uma das categorias validas
8) cena_foto: Descricao em ingles [angulo] + [local/objeto com nome exato] + [elementos visuais concretos] + [condicao de luz]

Responda SOMENTE com um JSON array valido, sem texto adicional.
```

**Parametros Serper /news:** sem filtro de data rigido — o Serper retorna resultados recentes por padrao. Coletar volume suficiente (20+) para garantir 7 validas apos filtragem de URLs.

> **Por que Serper e nao Perplexity:** O Perplexity fabricava URLs — 12 de 14 retornavam 404. Com Serper, as URLs vem do Google News e sao verificadas com HEAD request antes de entregar ao Claude.

---

### Fase 3: Revisao Editorial por IA (auto, bloqueante)

Após receber as notícias do Perplexity, a IA revisa CADA notícia antes de avançar. Nao chamar Leonardo sem passar aqui. Corrigir automaticamente o que for possivel (categoria errada, highlight_word inventada); se a noticia for vaga ou inventada, substituir via Perplexity com `--tematica`.

**Checklist por notícia:**
- [ ] **Categoria coerente com o conteúdo** — a categoria deve refletir o tema real da notícia, não palavras soltas do texto. Ex: notícia sobre habitação NÃO pode ser "RECURSOS HÍDRICOS"
- [ ] **Título tem no máximo 10 palavras**
- [ ] **highlight_words são palavras individuais do título** (não frases, não números inventados)
- [ ] **cena_foto é específica** — tem local/objeto concreto, não genérico ("a professional working" não serve)
- [ ] **fonte é um veículo real** (não "Relatório interno" ou similar)

**Categorias válidas e seus temas:**

| Categoria | Temas que pertencem |
|---|---|
| ESTRATEGIA CORPORATIVA | ESG corporativo, governança, relatórios, políticas empresariais |
| INFRAESTRUTURA | Construção, logística, mobilidade, habitação, portos, rodovias |
| ENERGIA | Solar, eólica, biomassa, biocombustível, transmissão elétrica |
| TECNOLOGIA | Automação, IA, precision farming, captura de carbono, inovação |
| FINANCAS VERDES | Investimentos ESG, green bonds, fundos sustentáveis, seguros climáticos |
| BIODIVERSIDADE | Florestas, fauna, certificação agropecuária, agricultura sustentável |
| RECURSOS HIDRICOS | Água, saneamento, rios, chuvas, gestão hídrica |
| COOPERACAO GLOBAL | Acordos internacionais, ONU, COP, protocolos multilaterais |
| EDUCACAO | Programas educacionais, capacitação, escolas, formação profissional |

**Ação para cada erro encontrado:**
1. Corrigir o campo diretamente no JSON (categoria, highlight_words, cena_foto)
2. Se a notícia for vaga ou inventada, **substituir por outra** (rodar Perplexity novamente com `--tematica`)
3. Atualizar `noticias_raw.json` com os dados corrigidos antes de avançar

---

### Fase 4: Busca de Imagens (Serper, Leonardo)

Para cada noticia, tentar em ordem:

**Camada 0 — Serper.dev / Google Images**
- Busca por titulo da noticia via `fetch_images_google.py`
- Aceitar se: imagem >= 600x350 e fonte valida
- Requer `SERPER_API_KEY` no `.env`

**Camada 1 — Leonardo AI** (se Serper falhar ou sem chave)
- Gerar foto do zero usando `cena_foto` como descricao
- Usar o template rico de fotojornalismo (ver prompt `gerar_card_leonardo` no script)
- Sem fallback para Unsplash — imagem generica sem contexto e pior que gerar do zero

**Apos buscar todas as fotos:**
Copiar cada foto final para `output/.../fotos/{N:02d}-{categoria}.jpg`.
Esta pasta e a fonte de imagens para o artigo do site — usa as fotos originais (sem overlay de card).
Registrar os caminhos no `manifest.json` sob a chave `fotos_artigo`.

---

### Fase 5: Geracao dos Cards (Leonardo AI)

**Arquitetura:** Leonardo gera o card completo (foto + layout). Pillow so e usado para o logo no CTA.

**Endpoint:** `POST https://cloud.leonardo.ai/api/rest/v2/generations`

**Configuracao padrao:**
```json
{
  "model": "nano-banana-2",
  "parameters": {
    "width": 1856,
    "height": 2304,
    "quantity": 1,
    "prompt_enhance": "OFF"
  },
  "public": false
}
```

**Buscar resultado:** `GET https://cloud.leonardo.ai/api/rest/v1/generations/{generationId}`
- Cards de noticia: aguardar 70s antes do primeiro poll, 10 retries de 20s
- Capa e CTA: aguardar 90s antes do primeiro poll, 10 retries de 20s

---

#### Regras criticas de prompt (evitar erros recorrentes)

**1. Nunca incluir sinal de $ no prompt**
O sinal `$` causa `VALIDATION_ERROR` na API do Leonardo. Sanitizar antes de montar o prompt:
- `R$30 mi` → `R 30 mi`
- `US$2 bi` → `USD 2 bi`

**2. Nunca usar percentuais como descritores de layout**
Frases como "top 55%" ou "from 55 to 72 percent" fazem o Leonardo renderizar os numeros como texto na imagem. Usar descritores qualitativos:
- **Errado:** "from 55 to 72 percent a gradient transitions..."
- **Certo:** "UPPER HALF of the card: photo. LOWER HALF: teal background. SMOOTH GRADIENT TRANSITION between upper and lower halves."

**3. Nunca incluir hex codes na descricao da barra gradiente**
O Leonardo renderiza hex codes como texto. Usar nomes de cores:
- **Errado:** "gradient stripe from #3DAA35 to #00A5B8 to #D41A6A to #E86428"
- **Certo:** "gradient stripe flowing from bright green to teal to magenta pink to orange"

**4. Iniciar imagem editorial com crop 4:5 antes do upload**
Ao usar `init_image` (foto editorial como referencia), a imagem DEVE ser cortada para a proporcao 1856:2304 (ratio 0.8055) antes do upload. Imagens landscape causam letterbox branco nas bordas.

**5. Highlight words: normalizar para matching, renderizar com acentos**
Para identificar quais palavras do titulo ficar em amarelo, normalizar com `unicodedata.normalize("NFKD").encode("ascii", "ignore")` apenas no matching. O texto enviado ao Leonardo DEVE manter os acentos originais — Leonardo renderiza UTF-8 corretamente. Nunca fazer strip de acentos no texto que vai para o prompt.

---

#### Card 01 — Capa

**Prompt template:**
```
Social media carousel cover card, Instagram portrait format, no white borders, fills entire frame.
IMPORTANT: Do NOT render any percentage signs, numbers, rulers or layout markers.
UPPER HALF of the card: full-bleed hyperrealistic photojournalistic photograph of {melhor cena_foto das noticias}.
Natural light, candid moment, film grain, looks exactly like a real photograph, NOT AI looking.
LOWER HALF: solid dark teal background color 005F73.
SMOOTH GRADIENT TRANSITION between photo and background.
CENTERED near top of lower half: small rounded green pill badge with white bold uppercase text 'SUSTENTABILIDADE E RESPONSABILIDADE SOCIAL'.
LARGE BOLD HEADLINE below badge: white centered uppercase sans-serif: {titulo da capa}.
BOTTOM EDGE flush: thick horizontal gradient stripe spanning full width, colors flow smoothly from bright green to teal to magenta pink to orange.
Professional editorial cover design. No borders, no padding.
```

**Escolher a melhor cena para a capa:** Pontuar `cena_foto` das noticias por especificidade visual (termos como "aerial", "port", "factory", "solar", "terminal" pontuam mais). Usar a mais especifica.

**Variacoes de titulo da capa:**
- `"{N} boas noticias sobre sustentabilidade e responsabilidade social desta semana"`
- `"O lado positivo do ESG que voce precisa conhecer"`
- `"{N} avancos em sustentabilidade que marcaram esta semana"`

---

#### Cards 02-08 — Noticias

**Dois modos conforme disponibilidade de foto editorial:**

**Modo A — Com foto editorial (Serper encontrou imagem):**
Usar `init_image_id` + `init_strength: 0.55` — Leonardo mantem a foto e aplica o layout por cima.

**Modo B — Sem foto editorial (gera do zero via cena_foto):**
Usar o template rico abaixo, sem `init_image_id`.

**Prompt template (Modo B — sem foto de referencia):**
```
Social media card, Instagram portrait format, no white borders, fills entire frame edge to edge.
IMPORTANT: Do NOT render any percentage signs, numbers, rulers or layout markers anywhere on the card.
UPPER HALF of the card: full-bleed photorealistic photograph, edge to edge.
UPPER HALF PHOTO: hyperrealistic editorial photograph of {cena_foto}.
Photojournalistic documentary style, natural imperfect lighting, Canon EOS R5 50mm lens, visible film grain ISO 400, sharp details, looks exactly like a real professional news photograph published in a major news outlet - NOT stock photo, NOT CGI, NOT illustration. Full bleed edge to edge, no text, no watermarks.
LOWER HALF of the card: solid dark teal background, color 005F73.
SMOOTH GRADIENT TRANSITION between upper and lower halves, blending photo into teal.
POSITIONED near the top of the lower half: small rounded pill badge with white bold uppercase text '{CATEGORIA}'.
LARGE BOLD HEADLINE below the badge: white uppercase sans-serif, words marked [YELLOW]...[/YELLOW] render in bright yellow color F5B800, others in white: {headline com marcacoes}.
BODY TEXT below headline: smaller regular white sans-serif: '{texto_card}'.
ATTRIBUTION below body text: tiny italic light gray text 'Fonte: {fonte}'.
TOP RIGHT CORNER: small dark rounded counter badge with white text '{N}/{total}'.
BOTTOM EDGE flush: thick horizontal gradient stripe spanning full width, colors flow smoothly from bright green to teal to magenta pink to orange.
Professional editorial design, clean, no borders, no padding, no layout markers visible.
```

**Como marcar as highlight words no headline:**
1. Pegar o array `highlight_words` da noticia
2. Normalizar para matching (strip acentos, pontuacao) — NAO alterar o texto renderizado
3. Para cada palavra do titulo que casar com highlight_words, envolver em `[YELLOW]palavra[/YELLOW]`
4. Exemplo: titulo `"Petrobras investe em biorrefino"` com highlights `["biorrefino"]` → `"PETROBRAS INVESTE EM [YELLOW]BIORREFINO[/YELLOW]"`

---

#### Card 09 — CTA

**Prompt template:**
```
Social media carousel final CTA card, Instagram portrait format. Clean solid dark teal 005F73 background covering the entire card. Empty space at the top 15 percent for logo. Centered vertically: large bold white sans-serif text 'Siga para mais boas noticias toda semana'. Below: smaller white text '@nticsprojetos'. Below: smaller elegant white italic text 'Inovacao, Impacto e Regeneracao'. BOTTOM EDGE flush: thick horizontal gradient stripe spanning full width, colors flow smoothly from bright green to teal to magenta pink to orange. Minimalist professional design, just elegant typography centered on solid dark teal background.
```

**Pos-processamento Pillow (UNICO uso de Pillow em todo o pipeline):**
```python
from PIL import Image

cta = Image.open('09-cta-base.jpg').convert('RGBA')
logo = Image.open('brand-book/site/assets/LOGO NTICS - BRANCA.png').convert('RGBA')

W, H = cta.size
logo_max_h = int(H * 0.14)
ratio = logo_max_h / logo.height
logo_w = int(logo.width * ratio)
logo_resized = logo.resize((logo_w, logo_max_h), Image.LANCZOS)

logo_x = (W - logo_w) // 2
logo_y = int(H * 0.06)

cta.paste(logo_resized, (logo_x, logo_y), logo_resized)
cta.convert('RGB').save('09-cta.jpg', quality=95)
```

---

### Fase 6: Revisao Visual dos Cards (IA, auto, bloqueante)

**Esta fase e obrigatoria e bloqueante.** Ler cada card com a ferramenta Read (imagem) e aplicar o checklist completo. Reprovar e regenerar internamente antes de avancar para a Fase 5. So apresentar ao usuario apos passar em todos os criterios.

**Checklist visual (todos os cards 01-09):**
- [ ] **Degradê de transicao presente** — zona foto→teal suave e visivel (nao abrupta, nao ausente)
- [ ] **Barra gradiente no rodape** colada na borda inferior, cores corretas (verde → teal → rosa → laranja)
- [ ] **Sem hex codes visiveis** (ex: "005F73", "3DAA35") renderizados como texto na imagem
- [ ] **Sem percentuais ou marcadores de layout** (ex: "55%", "8%") visiveis na imagem
- [ ] **Sem borda branca** em volta da imagem (letterbox = init_image com proporcao errada)

**Checklist ortografia e texto (cards 02-08):**
- [ ] **Badge com acento correto** — ESTRATÉGIA, COOPERAÇÃO, RECURSOS HÍDRICOS, EDUCAÇÃO, FINANÇAS VERDES, AGRONEGÓCIO (nunca sem acento)
- [ ] **Headline legivel** sem palavras duplicadas (ex: "NO NO", "COM A COM A")
- [ ] **Highlight words em amarelo** — pelo menos 1-2 palavras em destaque (nao tudo branco)
- [ ] **Fonte da noticia citada** no rodape do card
- [ ] **Numero de pagina** (ex: "2/9") no canto superior direito

**Checklist foto (cards 01-08):**
- [ ] **Sem pessoas** — imagem deve ser paisagem, infraestrutura, natureza ou ambiente (nao pessoas, rostos ou grupos)
- [ ] **Sem telas** — nenhum monitor, laptop, TV ou projetor visivel na foto
- [ ] **Sem reunioes** — nao pode parecer stock photo corporativa (pessoas sentadas em mesa)
- [ ] **Imagem hiper-realista** — nao parece IA, nao e ilustracao, nao e render
- [ ] **Foto coerente** com o tema da noticia

**Checklist card 01 (capa):**
- [ ] Foto de ambiente natural relacionada ao tema ESG da semana
- [ ] Titulo "7 AVANCOS EM SUSTENTABILIDADE QUE MARCARAM ESTA SEMANA" legivel

**Checklist card 09 (CTA):**
- [ ] Logo NTICS branca visivel no topo
- [ ] "@nticsprojetos" e tagline presentes
- [ ] Fundo teal solido (sem foto)

**Criterios de reprovacao automatica — regenerar com `--cards N` imediatamente:**

| Problema | Acao |
|----------|------|
| Degradê ausente ou abrupto | Regenerar card |
| Hex code visivel | Regenerar card |
| Badge sem acento | Regenerar card |
| Pessoas/rostos na foto | Regenerar card |
| Tela/laptop na foto | Regenerar card |
| Headline duplicado | Regenerar com headline mais curto |
| Logo CTA ausente | Re-aplicar Pillow |

**Loop ate aprovacao:** Regenerar ate todos os cards passarem. Usar `--skip-perplexity --skip-images --cards N` para nao gastar creditos desnecessarios.

---

### Fase 7: Artigo de Aprofundamento + Publicacao no WordPress (auto)

Gerar o artigo e publicar no WordPress automaticamente apos os cards aprovados na Fase 4. Nao aguardar aprovacao humana — o artigo publicado (com URL real) faz parte do pacote final que sera revisado junto com os cards na Fase 6.

**Input:** As mesmas 7 noticias da Fase 1 (ja estao no `manifest.json`).

#### Etapa 5a: Gerar artigo HTML

**Script:** `python tools/content-gen/gerar_artigo_site.py --tipo noticias --semana YYYY-MM-DD`

**Processo:**
1. Agrupar as 7 noticias em 2-3 blocos tematicos por afinidade
2. Identificar o fio narrativo da semana (tendencia, tema recorrente)
3. **Recortar o topo dos cards Leonardo para usar como imagens do artigo** (sem gerar novas imagens):
   - Crop seguro: descartar os 10% superiores (onde fica a numeração `X/9` no canto) e parar em 45% da altura (antes do gradiente teal e do badge). NUNCA usar 60% (pega badge/texto), nem 0%-50% (pega numeração).
   - Para o card capa (01), começar em 0% (não tem numeração) e ir até 43% (antes do início do título grande).
   - Pillow:
     ```python
     img = Image.open(card_path).convert("RGB")
     w, h = img.size
     # Card capa: top=0, bottom=43%
     # Cards de noticia: top=10%, bottom=45%
     top_pct, bottom_pct = (0.0, 0.43) if eh_capa else (0.10, 0.45)
     crop = img.crop((0, int(h*top_pct), w, int(h*bottom_pct)))
     # Resize para web
     if crop.size[0] > 1200:
         ratio = 1200 / crop.size[0]
         crop = crop.resize((1200, int(crop.size[1]*ratio)), Image.LANCZOS)
     crop.save(dest_path, "JPEG", quality=88, optimize=True)
     ```
   - **Por quê:** o tema do blog NTICS faz crop automático da featured image em listings/banners. Se o crop original do artigo deixar passar a numeração (`7/9`), badge (ex: `BIODIVERSIDADE`) ou início do gradiente teal, esses elementos aparecem nas thumbnails da home/listing — visual ruim de "sobra de carrossel Instagram". Margens 10%-45% garantem que NUNCA aparece texto/número/badge.
   - Salvar em `output/marketing/artigos/Artigo-noticias/semana-YYYY-MM-DD/fotos/{nome-semantico}.jpg` (ex: `hero-semana.jpg`, `inline-tecnologia.jpg`).
   - Upload: usar nome único com prefixo de semana (ex: `esg-2026-04-14-hero-semana.jpg`) para evitar dedup `-1`/`-2` do WordPress.
   - Referenciar no HTML com caminho relativo: `fotos/{nome-semantico}.jpg`
4. Escrever artigo com a estrutura abaixo
5. **Montar HTML no formato WP-ready** (ver regras de formato abaixo)
6. Salvar em `output/marketing/artigos/Artigo-noticias/artigo-noticias-esg-semana-{YYYY-MM-DD}.html`

> **Regra de imagens:** Nunca gerar imagens novas para o artigo. Usar o topo cropado dos cards Leonardo (60% superior = area da foto sem texto). As fotos na pasta `fotos/` sao apenas o insumo bruto do Serper — NAO usar no artigo. Os cards cropados sao visualmente superiores e garantem coerencia entre carrossel e artigo.

#### Formato HTML WP-ready (OBRIGATORIO)

O artigo sera publicado automaticamente no WordPress. Para funcionar corretamente, o HTML deve seguir estas regras:

**NAO incluir (o WordPress ja fornece):**
- `<html>`, `<head>`, `<body>` — gerar apenas o conteudo do artigo
- `<article>` wrapper externo — o tema WP ja envolve o conteudo
- `<h1>` com o titulo — o WP renderiza o titulo do post separadamente
- Linha de data/subtitulo abaixo do titulo (ex: `<p>Semana 07/04/2026 · NTICS Projetos</p>`) — o WP mostra a data do post automaticamente
- `</output>` ou tags espurias no final

**INCLUIR:**
- CSS inline nos elementos (o WP nao carrega CSS externo do artigo)
- `<h2>` para secoes, `<h3>` para subsecoes (nunca `<h1>`)
- `<figure>` + `<img>` + `<figcaption>` para imagens com legenda
- `<blockquote>` para citacoes de destaque
- Estrutura semantica limpa que funcione dentro do tema WP

**Imagens — caminhos relativos (upload automatico na Etapa 5b):**
- Referenciar com caminho relativo a pasta do artigo: `fotos/semana-YYYY-MM-DD/hero-{tema}.jpg`
- O script `publicar_wordpress.py` fara upload automatico e substituira os caminhos pelas URLs do WP
- A primeira imagem do artigo sera usada como **featured image** (thumbnail nos listings)

#### Etapa 5b: Publicar no WordPress

Imediatamente apos gerar o HTML, publicar no WordPress:

```bash
python tools/publishing/publicar_wordpress.py \
    --html output/marketing/artigos/Artigo-noticias/artigo-noticias-esg-semana-{YYYY-MM-DD}.html \
    --titulo "{titulo do artigo}" \
    --categoria artigos \
    --slug semana-esg-{YYYY-MM-DD}-{tema} \
    --excerpt "{1-2 frases resumindo o artigo}" \
    --status publish
```

**O que o script faz automaticamente:**
1. Le o HTML do artigo
2. Remove wrappers desnecessarios (`<article>`, `<h1>` duplicado)
3. Faz upload de todas as imagens locais para a biblioteca de midia do WP
4. Substitui caminhos locais (`fotos/...`) pelas URLs do WordPress
5. Cria o post como **publicado** com featured image (primeira imagem do artigo)
6. Retorna JSON: `{"post_id": 12345, "url": "https://ntics.com.br/artigos/...", "images_uploaded": 3}`

**Verificacao pos-publicacao (OBRIGATORIA):**
```bash
python tools/publishing/publicar_wordpress.py --verify {post_id}
```
Confirmar que title, status=publish e categorias estao corretos.

> **Se algo der errado:** `--delete {post_id}` para remover sem afetar outros posts, corrigir o HTML e republicar.

#### Etapa 5c: Incluir URL real na descricao.txt do carrossel

Apos publicar, atualizar a `descricao.txt` do carrossel com a **URL real** do artigo publicado. A descricao que chega ao usuario na Fase 6 ja deve conter o link funcional — nunca placeholder.

**Estrutura do artigo (segue o padrão aprovado da semana 2026-04-07 em `output/marketing/artigos/Artigo-noticias/semana-2026-04-07/` — use como template de referencia):**
```
<article> wrapper com max-width: 800px

H1 — Titulo curto (frase-gancho, sem ":" e sem subtitulo anexado)
Data + "NTICS Projetos" em linha menor (cor #666, font 0.9rem)

LEAD — Paragrafo grande (font 1.15rem, weight 500) sintetizando o que as 7 noticias revelam

HERO IMAGE — Imagem do card capa (max-height 420px, object-fit cover)

RESUMO EXECUTIVO — Box destacada (background #f0f9fa, border-left 4px #005F73):
  4 bullets curtos no formato "<strong>Tema:</strong> dado + impacto"
  Cobre os principais insights agregados, não repete cada noticia

TEMA 1 — H2 com NOME DO TEMA apenas (NUNCA "Bloco 1 -", "Bloco 2 -" literalmente)
  2-3 paragrafos substanciais conectando 2-3 noticias relacionadas
  Cada noticia tem contexto + dado numerico + implicacao de negocio
  Citar fonte inline como texto ("segundo o Olhar Digital", "conforme reportou o Valor")

IMAGEM INLINE 1 (entre blocos, max-height 360px)

TEMA 2 — mesma estrutura

BLOCKQUOTE — dado mais impressionante do bloco (border-left 3px #3DAA35, italic)

TEMA 3 — mesma estrutura

IMAGEM INLINE 2

TEMA 4 — 1-2 noticias restantes

CONCLUSAO — H2 "O Que Isso Significa Para Empresas que Investem em Responsabilidade Social"
  2-3 paragrafos com movimentos praticos (frameworks GRI/SBTN/CDP, linhas de financiamento verde, relatorios auditaveis)

FONTES DESTA SEMANA — Box cinza (background #f8f8f8):
  Lista numerada <ol> com 7 itens no formato:
  <a href="URL">Titulo da noticia</a> — Nome da fonte

HR com gradient colorido (verde → teal → rosa → laranja)
BOILERPLATE NTICS — 1 paragrafo curto sobre a empresa
```

**Regras:**
- **Data do artigo:** Usar a data da semana atual (quando o artigo sera publicado), nao a data do carrossel (que e semana seguinte). Ex: carrossel semana-2026-04-14 publicado em 08/04/2026 → artigo data "Semana 07/04/2026"
- **Links no corpo do texto:** NAO colocar links inline no corpo do artigo (ex: `<a href="...">Reuters</a>`). Fontes ficam somente na secao **"Fontes desta semana"** no final, como lista numerada com os 7 links verificados do manifest.json. No corpo, citar a fonte apenas como texto simples (ex: "segundo a Reuters")
- Nao colar 7 resumos — integrar em narrativa analitica
- **Densidade:** cada noticia deve ter AO MENOS 2 paragrafos substanciais (~100-150 palavras cada) no corpo, nao um paragrafo curto de resumo. Expandir contexto, implicacoes de negocio e dados.
- **H2 dos blocos:** usar o NOME DO TEMA diretamente (ex: "Economia Circular Sai do Conceito e Vira Produto"). NUNCA iniciar com "Bloco 1 -", "Bloco 2 -" — isso e estrutura interna, nao texto publicado.
- Tom editorial/jornalistico (55% formal, 70% inspiracao)
- Usar pelo menos 2 blockquotes no artigo inteiro (dado mais impressionante de cada bloco relevante)
- **Resumo Executivo obrigatorio:** box destacada com 4 bullets B2B antes do primeiro H2 de bloco
- **Wrapper <article> obrigatorio:** com `max-width: 800px` — o post sem wrapper fica largo demais no tema do blog
- **Titulo do artigo (WP):** curto, sem subtitulo anexado, baseado no gancho mais forte da semana. Formato: `"{Frase-gancho}"` (ex: `"Do Pantanal ao Tênis Reciclado"`). NAO usar estrutura `titulo: subtitulo` nem ":" no title field do WordPress.
- **H1 dentro do HTML:** padrao fixo `"7 boas noticias da {ordinal} semana de {mes}"` (ex: `"7 boas noticias da segunda semana de abril"`). Esse H1 vem logo apos abertura do `<article>`.
- **Autor do post no WP:** `author=1` (Ntics Projetos, slug `oliinternet`). Nunca publicar como `arte3` (id 15) — passar `--author 1` no `publicar_wordpress.py` ou atualizar via PATCH apos publish.

**Output — pasta autocontida por semana:**
```
output/marketing/artigos/Artigo-noticias/
└── semana-{YYYY-MM-DD}/              ← data da semana de publicacao (nao do carrossel)
    ├── artigo-noticias-esg-semana-{YYYY-MM-DD}.html  (WP-ready, CSS inline, sem wrapper)
    ├── fotos/
    │   ├── hero-{tema}.jpg           ← crop 60% do card escolhido
    │   ├── inline1-{tema}.jpg
    │   └── inline2-{tema}.jpg
    └── descricao.txt                 ← titulo, blocos, fontes, carrossel associado, campos WP
```
> **Regra:** A pasta do artigo deve ser autocontida — HTML + fotos + descricao tudo junto. O HTML referencia as fotos com caminho relativo `fotos/{arquivo}`. O tool `publicar_wordpress.py` resolve os caminhos e faz upload automaticamente.

---

### Fase 8: Organizacao e Entrega (gate humano)

Apresentar ao usuario o pacote completo para revisao e aprovacao final:
- Todos os cards (01 a 09) — revisão visual pelo usuário
- Artigo ja publicado no WordPress — apresentar URL real para revisao
- descricao.txt com captions Instagram + LinkedIn + URL real do artigo

O usuario aprova ou solicita correcoes pontuais nos cards. O artigo ja esta publicado no site.

> **Se o usuario pedir correcao no artigo:** editar o HTML, deletar o post antigo (`--delete {id}`), republicar com `publicar_wordpress.py` e atualizar a URL na descricao.txt.

**Estrutura da pasta:**
```
output/marketing/carrosseis/noticias/
└── semana-{YYYY-MM-DD}/
    ├── 01-capa.jpg
    ├── 02-{categoria}.jpg       ← cards Leonardo (com overlay de texto)
    ├── ...
    ├── 08-{categoria}.jpg
    ├── 09-cta.jpg
    ├── fotos/                   ← fotos originais sem overlay (para artigo do site)
    │   ├── 01-{categoria}.jpg
    │   ├── 02-{categoria}.jpg
    │   └── ...
    ├── descricao.txt
    └── manifest.json            ← campo "fotos_artigo" mapeia indice → path da foto
```

**Conteudo do descricao.txt:**
```
========================================
CARROSSEL: BOAS NOTICIAS ESG
Semana {data}
========================================

--- CAPTION INSTAGRAM ---
{hook inspiracional + bullets com emoji + CTA engajador}
{tom: 40% formal, 85% inspiracional}
Quer aprofundar? Artigo completo no link da bio.
{4-6 hashtags relevantes}

--- CAPTION LINKEDIN ---
{paragrafo analitico + lista numerada titulo+1frase + pergunta final}
Analise completa: {URL REAL do artigo publicado no WP — ex: https://ntics.com.br/artigos/semana-esg-2026-04-14-energia-transparencia/}
{tom: 70% formal, 65% tecnico}
{max 5 hashtags}

--- WORDPRESS ---
post_id: {ID retornado pelo publicar_wordpress.py}
url: {URL real do artigo publicado}
status: publish

--- COMENTARIO COM LINKS (fixar como primeiro comentario) ---
{lista numerada: "N. Nome da Fonte — URL completa"}

--- ORDEM DOS CARDS ---
{lista dos arquivos com descricao de cada um}
```

---

## Especificacoes Tecnicas

| Elemento | Especificacao |
|----------|---------------|
| Proporcao | 4:5 (Instagram) |
| Dimensao | 1856 x 2304 px |
| Formato | JPG, quality 95 |
| Modelo IA | Nano Banana 2 (Leonardo AI v2 API) |
| Total de cards | 9 (capa + 7 noticias + CTA) |
| Pillow | APENAS para colar logo NTICS no CTA |
| Composicao | 100% Leonardo AI — zero Pillow para layout |
| init_image | Crop obrigatorio para ratio 1856:2304 (0.8055) antes do upload |
| Espera | Capa/CTA: 90s inicial; Noticias: 70s inicial; Retries: 10x de 20s |
| Busca noticias | Serper /news + verificacao HEAD de cada URL — zero URLs fabricadas |
| Selecao/redacao | Claude Haiku — seleciona 7 de 20+ candidatos e redige todos os campos |
| Escopo geografico | Brasil + mundo — fontes internacionais aceitas |
| Sinal $ | PROIBIDO no prompt Leonardo — sanitizar: R$ → R, US$ → USD |
| Layout % | PROIBIDO no prompt Leonardo — usar UPPER HALF / LOWER HALF |
| Hex codes | PROIBIDOS na barra gradiente — usar nomes de cores |
| Acentos no prompt | MANTER — Leonardo renderiza UTF-8 corretamente |
| Highlight matching | Normalizar (strip acento) SÓ para comparar — nao alterar texto do prompt |
| Fonte de imagem | Serper.dev (Google Images) → Leonardo cena_foto |
| Unsplash | REMOVIDO — imagens sem contexto editorial nao sao aceitaveis |

---

## Identidade Visual NTICS

| Cor | Hex | Uso |
|-----|-----|-----|
| Verde Regeneracao | #3DAA35 | Badges, barra gradiente |
| Azul Petroleo | #005F73 | Fundo de texto, area teal |
| Rosa Transformacao | #D41A6A | Barra gradiente |
| Laranja Acao | #E86428 | Barra gradiente |
| Teal Futuro | #00A5B8 | Barra gradiente, badges |
| Amarelo Destaque | #F5B800 | Highlight words no headline |
| Branco | #FFFFFF | Texto, logo |

---

## Conexao com Outras Skills

- **Artigo de aprofundamento:** Antes de publicar o carrossel, gerar artigo para o site com `artigo_noticias_site.md`. O artigo aprofunda as 7 noticias. Publicar o artigo PRIMEIRO, depois o carrossel com link para o artigo na descricao.
- Conteudo pode alimentar: `/email-marketing` (secao "Boas Noticias do Mundo")
- Frequencia: 1x por semana (semanas pares no calendario editorial)
- Independente do tema semanal do video — e curadoria livre
- Apos aprovacao: `/revisao-carrossel pasta=output/.../ tipo=noticias`

### Cadeia de publicacao

```
Serper /news coleta candidatos → Claude Haiku seleciona 7 (Fase 1)
  │
  ├→ Fases 1-4: Pesquisa, imagens, cards, revisao visual
  │
  ├→ Fase 5a: Gerar artigo HTML (WP-ready, CSS inline, sem wrapper)
  ├→ Fase 5b: publicar_wordpress.py → Upload imagens + publicar no WP
  │   (retorna URL real do artigo — ex: https://ntics.com.br/artigos/semana-esg-2026-04-14/)
  ├→ Fase 5c: Inserir URL real na descricao.txt do carrossel
  │
  └→ Fase 6: Aprovacao humana (cards + artigo ja publicado + descricao com URL real)
      → Usuario publica carrossel no Instagram/LinkedIn com link do artigo
```

Na `descricao.txt`, o link do artigo ja esta preenchido com a URL real:
- **Instagram:** "Quer aprofundar? Artigo completo no link da bio."
- **LinkedIn:** "Analise completa: {URL real do artigo publicado}"

### Tool de publicacao

| Tool | Comando | Uso |
|------|---------|-----|
| `publicar_wordpress.py` | `--html ... --titulo ... --status draft` | Criar rascunho com upload de imagens |
| `publicar_wordpress.py` | `--publish {id}` | Publicar rascunho aprovado |
| `publicar_wordpress.py` | `--verify {id}` | Verificar post (titulo, status, URL) |
| `publicar_wordpress.py` | `--delete {id}` | Remover post com problema |

> **Credenciais:** WP_URL, WP_USER, WP_APP_PASSWORD no `.env`. Categoria `artigos` = ID 73 no WP.
