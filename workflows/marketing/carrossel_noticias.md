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

### Fase 0: Verificar Noticias Anteriores (Anti-Repeticao)

Antes de pesquisar, ler os arquivos `descricao.txt` de TODOS os carrosseis anteriores em `.tmp/marketing/carrosseis/semana-*/` para coletar:
- URLs ja utilizadas
- Titulos ja utilizados
- Empresas/organizacoes ja destacadas

Montar uma lista de exclusao para passar ao Perplexity no prompt.

### Fase 1: Pesquisa de Noticias (Perplexity)

**Endpoint:** `POST https://api.perplexity.ai/chat/completions`

**Prompt para o Perplexity:**
```
Quais sao as 6 noticias positivas mais recentes (ultimos 7 dias) sobre ESG, sustentabilidade e responsabilidade social corporativa no Brasil e no mundo? {Se tematica: "Foque especificamente em [tematica]."}
Foque em resultados concretos, novos investimentos, metas alcancadas e iniciativas lancadas.

IMPORTANTE: NAO inclua noticias das seguintes fontes/URLs que ja foram usadas em edicoes anteriores:
{lista de URLs anteriores}

Tambem evite repetir noticias sobre as mesmas empresas/organizacoes:
{lista de empresas ja destacadas}

Para cada noticia, forneca:
1) Titulo curto (maximo 10 palavras) — sem siglas nao explicadas
2) Paragrafo resumo (3-4 frases) que explique claramente o que aconteceu, quem fez e por que importa
3) Fonte (nome do veiculo)
4) URL da materia original
5) Uma palavra-chave em ingles para busca de imagem (ex: solar energy, reforestation)
6) Categoria (ESTRATEGIA CORPORATIVA, INFRAESTRUTURA, RECURSOS HIDRICOS, EDUCACAO, COOPERACAO GLOBAL, FINANCAS VERDES, ENERGIA, BIODIVERSIDADE ou TECNOLOGIA)
Responda em portugues brasileiro. Formate como JSON array.
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

#### Cards 02-07 — Noticias (Estilo C2 — icone circular + texto informativo)

**Prompt template para cada noticia:**
```
A social media carousel card Instagram 4:5 format. The top 55 percent is a full-bleed hyperrealistic photograph of {descricao da cena baseada na noticia — ser especifico ao conteudo}, candid unposed moment, Canon 50mm f1.4 natural bokeh warm tones, visible film grain ISO 800, natural imperfect lighting, NOT AI generated. In the upper right corner overlapping the photo a circular bubble icon approximately 12 percent width showing {elemento visual simbolico da noticia — ex: globo terrestre, folha verde, painel solar, gota d'agua}, surrounded by a glowing golden ring with soft amber light. From 55 to 72 percent a smooth dark gradient overlay transitions from transparent to solid dark teal 005F73. From 72 to 75 percent a small rounded {cor do badge} badge with white text {CATEGORIA}. From 75 to 88 percent large bold white uppercase sans-serif headline with key words in yellow F5B800: {titulo da noticia — palavras-chave em caps}. From 88 to 96 percent smaller white sans-serif body text: {paragrafo resumo da noticia}. At 97 percent tiny white text: Fonte: {fonte}. At the very bottom edge flush a thick gradient stripe bar from green 3DAA35 to teal 00A5B8 to pink D41A6A to orange E86428. Professional editorial card.
```

**Elementos novos do estilo C2:**
- **Icone circular** (canto superior direito): bolha com elemento visual tematico + anel dourado brilhante
- **Headline com destaques**: palavras-chave em amarelo #F5B800, restante em branco
- **Sem divisor decorativo**: logo NTICS entra via pos-processamento Pillow (nao no prompt)

**IMPORTANTE sobre a descricao da cena:**
- A cena deve representar EXATAMENTE o que a noticia fala
- Nao usar cenas genericas (ex: "paineis solares" se a noticia nao fala de energia solar)
- Descrever a cena como se fosse uma foto real sendo tirada por um jornalista
- Incluir detalhes de camera: Canon, lente, bokeh, luz natural
- Descrever imperfeicoes reais: mesa bagunçada, cabos visiveis, iluminacao imperfecta, alguem mexendo no celular
- SEMPRE incluir o bloco de realismo no prompt para evitar imagens com cara de IA

**IMPORTANTE sobre o icone circular:**
- Deve ser um simbolo/objeto concreto relacionado a noticia (nao abstrato)
- Exemplos: globo terrestre (cooperacao global), folha verde (biodiversidade), painel solar (energia), gota d'agua (recursos hidricos), engrenagem (tecnologia), graficos (financas)
- O anel dourado ao redor e obrigatorio — gera o efeito visual marcante

**Bloco de realismo (incluir em TODOS os prompts de foto):**
```
candid unposed moment, Nikon D850 85mm f1.8, visible film grain ISO 800, natural imperfect lighting with real shadows, shallow depth of field, skin pores visible, NOT AI generated NOT illustration
```

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

### Fase 4: Revisao Visual dos Cards (OBRIGATORIA — usar agente de revisao)

Apos gerar, lançar um **agente de revisao visual** que abre CADA card e verifica contra o checklist abaixo. O agente deve reprovar cards com defeitos e listar quais precisam ser regenerados. NAO pular esta fase.

**Checklist de revisao visual (verificar CADA card individualmente):**
- [ ] Texto correto — sem erros de ortografia ou numeros trocados
- [ ] Badge com categoria visivel e legivel
- [ ] Barra gradiente no rodape colada na borda inferior (sem espaco)
- [ ] Barra gradiente com cores corretas (verde → teal → rosa → laranja), SEM hex codes visiveis
- [ ] Foto hiper-realista e coerente com o conteudo da noticia
- [ ] Degradê suave da foto para o teal — SEM artefatos, SEM padrao xadrez, SEM banding
- [ ] Sem hex codes, percentuais ou codigos visiveis na imagem
- [ ] Fonte citada corretamente
- [ ] Icone circular com anel dourado presente e tematico (cards 02-07)
- [ ] Body text presente e legivel (cards 02-07)
- [ ] Pessoas (se houver): maximo 1-2, aspecto natural, sem rostos plastificados ou poses artificiais
- [ ] Sem texto gerado pelo Leonardo que nao foi solicitado (hashtags, watermarks)

**Criterios de reprovacao automatica (regenerar imediatamente):**
1. Degradê com artefatos (xadrez, banding, transparencia quebrada)
2. Hex codes ou percentuais visiveis na imagem
3. Body text ausente quando deveria estar presente
4. Grupo de 3+ pessoas com aspecto artificial/posado
5. Texto ilegivel ou cortado

**Se algum card falhar na revisao:** regenerar APENAS esse card com prompt ajustado, corrigindo o defeito especifico. Depois revisar novamente o card regenerado.

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
| Modelo IA | Nano Banana 2 (Leonardo AI v2 API) — **OBRIGATÓRIO usar 1856x2304** (outras dimensões retornam VALIDATION_ERROR) |
| Foto | Topo 55%, hiper-realista, estilo fotojornalistico |
| Icone circular | Canto superior direito, ~12% largura, elemento tematico + anel dourado |
| Degrade | 55-72% transicao, transparente → teal #005F73 |
| Texto headline | Branco bold uppercase, palavras-chave em amarelo #F5B800 |
| Texto corpo | Branco regular, sans-serif |
| Badge | Arredondado, cor por categoria, texto branco (72-75%) |
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
