# Carrossel de Boas Noticias ESG/CSR — NTICS Projetos

> Pesquisa noticias positivas da semana, gera 8 cards visuais (capa + 6 noticias + CTA) via Leonardo AI Nano Banana 2, revisa qualidade, adiciona logo NTICS no CTA, cria descricao com links e salva tudo organizado numa pasta da semana.

---

## APIs Utilizadas

| API | Uso | Modelo/Config |
|-----|-----|---------------|
| Perplexity | Pesquisar 6 noticias positivas ESG/CSR da semana | model: sonar, search_recency_filter: week |
| Leonardo AI | Gerar cards visuais hiper-realistas com texto | model: nano-banana-2, 1856x2304 (4:5) |
| Unsplash | Fallback se nao encontrar imagem da materia | orientation: landscape |

### Chaves (variaveis de ambiente)
- `PERPLEXITY_API_KEY`
- `LEONARDO_API_KEY`
- `UNSPLASH_API_KEY`

---

## Inputs do Usuario

| Campo | Tipo | Obrigatorio | Descricao |
|-------|------|-------------|-----------|
| `semana` | string | Sim | Data da semana (ex: "2026-03-22") |
| `tematica` | string | Nao | Tema especifico para filtrar noticias (ex: "economia circular"). Se vazio, busca noticias gerais ESG/CSR |

---

## Execucao

### Fase 1: Pesquisa de Noticias (Perplexity)

**Endpoint:** `POST https://api.perplexity.ai/chat/completions`

**Prompt para o Perplexity:**
```
Quais sao as 6 noticias positivas mais recentes (ultimos 7 dias) sobre ESG, sustentabilidade e responsabilidade social corporativa no Brasil e no mundo? {Se tematica: "Foque especificamente em [tematica]."}
Foque em resultados concretos, novos investimentos, metas alcancadas e iniciativas lancadas.
Para cada noticia, forneca:
1) Titulo curto (maximo 10 palavras) — sem siglas nao explicadas
2) Paragrafo resumo (3-4 frases) que explique claramente o que aconteceu, quem fez e por que importa
3) Fonte (nome do veiculo)
4) URL da materia original
5) Uma palavra-chave em ingles para busca de imagem (ex: solar energy, reforestation)
Responda em portugues brasileiro.
```

**Parametros:** `search_recency_filter: "week"`

### Fase 2: Revisao dos Textos

Antes de gerar os cards, revisar TODOS os textos:

**Checklist de revisao de texto:**
- [ ] Titulos sem siglas cruas — se usar sigla, explicar (ex: "CEBDS" → "Conselho das maiores empresas do Brasil")
- [ ] Paragrafos explicam O QUE aconteceu, QUEM fez e POR QUE importa
- [ ] Tom positivo — celebra avancos, nao denuncia problemas
- [ ] Marcas mencionadas com contexto (ex: "Kimberly-Clark, dona de Neve e Huggies")
- [ ] Numeros concretos e especificos
- [ ] Quem le consegue entender sem conhecimento previo do assunto
- [ ] Sensacao de positividade ao ler

### Fase 3: Geracao dos Cards (Leonardo AI Nano Banana 2)

**Endpoint:** `POST https://cloud.leonardo.ai/api/rest/v2/generations`

**Configuracao padrao para TODOS os cards:**
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
- Aguardar ~50 segundos antes de verificar
- Se status PENDING, aguardar mais 20 segundos e verificar novamente

---

#### Card 01 — Capa

**Prompt template:**
```
A social media carousel cover card for Instagram 4:5 format. The top 60 percent is a full-bleed hyperrealistic photograph of {cena realista relacionada ao tema da semana}, shot with a Canon EOS R5 35mm lens, natural warm sunlight, photojournalistic documentary style, looks exactly like a real photograph, no fantasy or futuristic elements. From 60 to 80 percent a smooth dark gradient overlay transitions from transparent to solid dark teal #005F73. From 80 to 98 percent, over the solid dark teal background, centered large bold white sans-serif text reads: {titulo da capa — ex: 6 boas noticias sobre sustentabilidade e responsabilidade social desta semana}. At the very bottom edge flush with zero margin, a thick prominent horizontal gradient stripe bar spanning full width approximately 2 percent of total height with smooth color flow from bright green to teal to magenta to orange. No logo, no branding text. Professional editorial cover design.
```

**Variacoes de titulo da capa** (alternar para nao repetir):
- "6 boas noticias sobre sustentabilidade e responsabilidade social desta semana"
- "O lado positivo do ESG que voce precisa conhecer"
- "6 avancos em sustentabilidade que marcaram esta semana"
- Se tematica especifica: "6 boas noticias sobre {tematica} desta semana"

---

#### Cards 02-07 — Noticias

**Prompt template para cada noticia:**
```
A social media carousel card for Instagram 4:5 format. The top 55 percent is a full-bleed hyperrealistic {descricao da cena baseada na noticia — ser especifico ao conteudo}, photojournalistic style shot with Canon 50mm f1.4 natural bokeh warm tones. From 55 to 75 percent a smooth dark gradient overlay transitions from transparent to solid dark teal #005F73. From 75 to 78 percent a small rounded {cor do badge} badge with white text {CATEGORIA}. From 78 to 92 percent large bold white sans-serif headline text: {titulo da noticia}. From 92 to 98 percent smaller white sans-serif body text: {paragrafo resumo da noticia}. Tiny text Fonte: {fonte} at the bottom. At the very bottom edge flush with zero margin, a thick prominent horizontal gradient stripe bar spanning full width approximately 2 percent of total height with smooth color flow from bright green to teal to magenta to orange. No hex codes visible. No logo. Professional editorial card design.
```

**IMPORTANTE sobre a descricao da cena:**
- A cena deve representar EXATAMENTE o que a noticia fala
- Nao usar cenas genericas (ex: "paineis solares" se a noticia nao fala de energia solar)
- Descrever a cena como se fosse uma foto real sendo tirada por um jornalista
- Incluir detalhes de camera: Canon, lente, bokeh, luz natural

**Categorias e cores dos badges:**
- ESTRATEGIA CORPORATIVA → verde
- INFRAESTRUTURA → verde
- RECURSOS HIDRICOS → azul
- EDUCACAO → amarelo
- COOPERACAO GLOBAL → roxo
- FINANCAS VERDES → verde
- ENERGIA → laranja
- BIODIVERSIDADE → verde
- TECNOLOGIA → teal

---

#### Card 08 — CTA

**Prompt template:**
```
A social media carousel final CTA card for Instagram 4:5 format. Clean solid dark teal #005F73 background covering the entire card. The top 15 percent is empty dark teal space reserved for a logo. In the center of the card vertically, large bold white sans-serif text reads: Siga para mais boas noticias toda semana. Below in smaller white text: @nticsprojetos. Below that in even smaller elegant white italic text: Inovacao, Impacto e Regeneracao. At the very bottom edge flush with zero margin, a thick prominent horizontal gradient stripe bar spanning full width approximately 2 percent of total height with smooth color flow from bright green to teal to magenta to orange. Minimalist professional design, no images, just elegant typography centered on solid dark teal background with generous empty space at the top.
```

**Pos-processamento do CTA (Python):**
Adicionar logo NTICS branca real no topo via Pillow:
```python
from PIL import Image

cta = Image.open('08-cta-base.jpg').convert('RGBA')
logo = Image.open('brand-book/site/assets/LOGO NTICS - BRANCA.png').convert('RGBA')

W, H = cta.size
logo_max_h = int(H * 0.14)  # 14% da altura = dobro do padrao
ratio = logo_max_h / logo.height
logo_w = int(logo.width * ratio)
logo_resized = logo.resize((logo_w, logo_max_h), Image.LANCZOS)

logo_x = (W - logo_w) // 2
logo_y = int(H * 0.06)  # 6% do topo

cta.paste(logo_resized, (logo_x, logo_y), logo_resized)
cta.convert('RGB').save('08-cta.jpg', quality=95)
```

---

### Fase 4: Revisao Visual dos Cards

Apos gerar, verificar CADA card:

**Checklist de revisao visual:**
- [ ] Texto correto — sem erros de ortografia ou numeros trocados
- [ ] Badge com categoria visivel
- [ ] Barra gradiente no rodape colada na borda inferior (sem espaco)
- [ ] Barra gradiente visivel e com cores corretas (verde → teal → rosa → laranja)
- [ ] Foto hiper-realista e coerente com o conteudo da noticia
- [ ] Degradê suave da foto para o teal
- [ ] Sem hex codes ou codigos visiveis na imagem
- [ ] Fonte citada corretamente

**Se algum card falhar na revisao:** regenerar apenas esse card com prompt ajustado.

### Fase 5: Organizacao e Entrega

**Estrutura da pasta:**
```
carrosseis/
└── semana-{YYYY-MM-DD}/
    ├── 01-capa.jpg
    ├── 02-{categoria}.jpg
    ├── 03-{categoria}.jpg
    ├── 04-{categoria}.jpg
    ├── 05-{categoria}.jpg
    ├── 06-{categoria}.jpg
    ├── 07-{categoria}.jpg
    ├── 08-cta.jpg
    └── descricao.txt
```

**Conteudo do descricao.txt:**
```
========================================
CARROSSEL: BOAS NOTICIAS ESG/CSR
Semana {data}
========================================

--- CAPTION INSTAGRAM ---
{texto da caption — tom esperancoso, lista das noticias, convite para salvar/compartilhar, hashtags}

--- CAPTION LINKEDIN ---
{texto da caption — tom profissional, lista numerada das noticias, pergunta engajadora, hashtags}

--- COMENTARIO COM LINKS (fixar como primeiro comentario) ---
{lista numerada com nome da fonte + URL completa de cada materia}

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
| Foto | Topo 55-60%, hiper-realista, estilo fotojornalistico |
| Degrade | 15-20% de transicao, transparente → teal #005F73 |
| Texto | Branco, sans-serif, bold para titulo, regular para corpo |
| Badge | Arredondado, cor por categoria, texto branco |
| Barra gradiente | 2% da altura, colada no rodape, sem espaco abaixo |
| Cores da barra | #3DAA35 → #00A5B8 → #D41A6A → #E86428 |
| Logo CTA | NTICS branca, 14% da altura, centralizada, topo 6% |
| Logo arquivo | `brand-book/site/assets/LOGO NTICS - BRANCA.png` |

---

## Identidade Visual NTICS

| Cor | Hex | Uso |
|-----|-----|-----|
| Verde Regeneracao | #3DAA35 | Badges, barra |
| Azul Petroleo | #005F73 | Fundo degrade, area de texto |
| Rosa Transformacao | #D41A6A | Barra |
| Laranja Acao | #E86428 | Barra |
| Teal Futuro | #00A5B8 | Barra, badges |
| Branco | #FFFFFF | Texto, logo |

---

## Conexao com Outras Skills

- Conteudo pode alimentar: `/email-marketing` (secao "Boas Noticias do Mundo")
- Frequencia: 1x por semana (semanas pares no calendario editorial)
- Independente do tema semanal do video — e curadoria livre
