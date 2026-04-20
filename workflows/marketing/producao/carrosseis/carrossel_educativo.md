# Carrossel Educativo — NTICS Projetos

> Cadencia semanal. O conteudo (tema, cards, cenas) ja esta definido no ClickUp. O agente busca a task da semana, adiciona ao dict SEMANAS do script e executa o pipeline hibrido completo: Leonardo AI gera fotos de fundo → Pillow aplica pelicula teal → Leonardo AI renderiza texto por cima. Card 08 CTA reconstruido 100% via Pillow com fundo solido uniforme.

> 📚 **Referência Leonardo AI:** Este workflow tem estrutura validada — siga-o como fonte primária. Se surgir erro de API, dúvida sobre payload ou resultado visual inesperado, consulte `workflows/marketing/referencia/leonardo_ai_core.md` como base de conhecimento complementar (erros conhecidos, modos, exemplos).

---

## APIs Utilizadas

| API | Uso | Modelo/Config |
|-----|-----|---------------|
| Leonardo AI | Passo 1: foto de fundo limpa (sem texto) | nano-banana-2, 1856x2304, prompt_enhance OFF |
| Leonardo AI | Passo 2: card final com texto (via init_image) | nano-banana-2, init_strength 0.70 (capa: 0.65) |

### Chaves
- `LEONARDO_API_KEY`

---

## Contexto da Marca

Antes de comecar, leia:

1. `brand-book/02-identidade-verbal/tom-de-voz.md` — tom de voz Instagram e LinkedIn
2. `brand-book/data/brand-data.yaml` — metricas e credenciais NTICS
3. `brand-book/02-identidade-verbal/mensagens-chave.md` — taglines

### Persona-alvo

**Marina Costa** — Coordenadora/Diretora RSC que busca conhecimento pratico sobre ESG e responsabilidade social. Quer conteudo claro, com dados e aplicavel.

---

## Input: adicionar semana ao script

Editar o dict `SEMANAS` em `tools/content-gen/gerar_educativos_3semanas.py` com:

| Campo | Descricao |
|-------|-----------|
| `tema` | Titulo do carrossel em caixa alta |
| `capa_subtitulo` | Subtitulo da capa |
| `capa_cena` | Descricao da cena para foto de fundo da capa — **sem mencionar telas, monitores, projetores** |
| `cta_pergunta` | Pergunta do card 08 CTA |
| `metodo_frase` | Frase do Metodo NTICS (ex: "24 ANOS DE METODO QUE ENTREGA") |
| `cards` | Lista com 5 cards (slug, titulo, texto, frase, cena) |

### Regras obrigatorias ao escrever o conteudo

- **Travessao (—)** → substituir por virgula ou "mas"
- **Palavras inglesas isoladas** ("performance", "feedback") → substituir por portugues
- **Ponto final** em `texto` e `frase` → remover
- **Decimais** → usar ponto ("11.4M", "9.32"), nunca virgula
- **capa_cena** → no maximo 1-2 pessoas, ou cena sem pessoas; nunca grupo celebrando

---

## Execucao

### Fase 1: Buscar task da semana no ClickUp

1. Acessar a lista de carrosseis educativos no ClickUp
2. Localizar a task da semana atual (status "a fazer" ou equivalente)
3. Extrair o briefing da task: tema, subtitulo, cena da capa, cards 02-06, frase do metodo, pergunta CTA
4. Consultar `brand-book/data/brand-data.yaml` — metricas oficiais para o card de metodo
5. Verificar memorias `feedback_leonardo_prompts.md` e `feedback_editorial_tone.md`

### Fase 2: Estruturar os 8 Cards

| Card | Pipeline | Conteudo |
|------|----------|----------|
| 01 — Capa | Hibrido | Foto full-bleed com pelicula teal, badge "RESPONSABILIDADE SOCIAL QUE RESOLVE", titulo, subtitulo |
| 02-06 — Conteudo | Hibrido | Foto de fundo + pelicula teal, titulo bold, texto regular, frase destaque amarela |
| 07 — Metodo NTICS | Hibrido | Foto de fundo + pelicula teal, grid 2x2 metricas (numeros amarelos), selos |
| 08 — CTA | Pillow puro | Fundo teal solido uniforme, logo NTICS, pergunta, ntics.com.br, @nticsprojetos |

### Fase 3: Geracao dos Cards (pipeline hibrido)

Executar `tools/content-gen/gerar_educativos_3semanas.py`:

```bash
python tools/content-gen/gerar_educativos_3semanas.py
```

O script executa o pipeline hibrido completo para cada semana configurada no dict `SEMANAS`:
- Passo 1: Leonardo gera foto limpa (sem texto) para cada card
- Pillow aplica pelicula teal ~62% de opacidade
- Passo 2: Leonardo gera card final com texto por cima (init_image)
- Card 08 CTA: reconstruido 100% Pillow (fundo solido uniforme)
- Copia automatica para `.tmp/marketing/carrosseis/educativo/{SEMANA}/`

### Fase 4: Revisao Visual (OBRIGATORIA — antes de copiar para final/)

**Executar o workflow de revisao completo em `workflows/marketing/producao/carrosseis/revisao-carrossel.md` com:**
- `pasta` = `.tmp/marketing/carrosseis/educativo/{SEMANA}/`
- `tipo` = `educativo`

**Ler visualmente todos os 8 cards via `Read` (imagem) e aplicar os checklists do workflow de revisao.**

**Regra de entrega:**
- Se houver qualquer achado 🔴 → corrigir antes de copiar para `final/`. NAO entregar ao usuario.
- Se houver apenas 🟡 → pode entregar mas mencionar ao usuario.
- Se tudo 🟢 → copiar para `output/marketing/carrosseis/educacional/{SEMANA}-{slug}/final/` e entregar.

**Corrецoes comuns:**
- Gradiente invertido → corrigir prompt (adicionar "from LEFT to RIGHT") e regenerar com Leonardo. NUNCA corrigir via Pillow.
- Card 08 com barra grossa → ajustar `BAR_START` em `apply_logo_cta` (valor atual: 0.988)
- Hex codes visiveis → remover hex do prompt de gradiente, usar apenas nomes de cor
- Foto com tela/monitor → corrigir `capa_cena` e regenerar card 01
- Numeros com espaco ("11, 4M") → usar ponto decimal ("11.4M") em `fmt_num()`

### Fase 5: Organizacao e Entrega

**Estrutura da pasta:**
```
output/marketing/carrosseis/educativos/
└── semana-{semana}/
    ├── 01-capa.jpg
    ├── 02-{slug}.jpg
    ├── 03-{slug}.jpg
    ├── 04-{slug}.jpg
    ├── 05-{slug}.jpg
    ├── 06-{slug}.jpg
    ├── 07-metodo.jpg
    ├── 08-cta.jpg
    ├── descricao.txt
    └── manifest.json
```

**Conteudo do descricao.txt:**
```
========================================
CARROSSEL EDUCATIVO
Tema: {tema}
Semana {data}
========================================

--- CAPTION INSTAGRAM ---
{caption — tom inspirador, pergunta engajadora, hashtags}

--- CAPTION LINKEDIN ---
{caption — tom profissional, lista dos conceitos, CTA consultivo, hashtags}

--- COMENTARIO COM LINKS ---
{se houver fontes/referencias, listar aqui}

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
| Modelo IA | nano-banana-2 — todos os cards 01-07 (passo 1 foto + passo 2 texto) |
| Card 08 CTA | 100% Pillow — fundo teal solido uniforme |
| Fundo cards 01-07 | Foto Leonardo + pelicula teal RGBA(0,95,115,158) ~62% opacidade |
| Texto titulo | Branco bold uppercase, Segoe UI Bold |
| Texto corpo | Branco regular, Segoe UI |
| Frase destaque | Amarelo #F5B800 italic com borda esquerda |
| Grid metricas | Numeros amarelo #F5B800 bold, descritores branco |
| Barra gradiente | 2.5% da altura, colada no rodape |
| Cores da barra | #3DAA35 → #00A5B8 → #D41A6A → #E86428 |
| Logo CTA | NTICS branca, 14% altura, centralizada, topo 6% |
| Logo arquivo | `brand-book/site/assets/LOGO NTICS - BRANCA.png` |

---

## Identidade Visual NTICS

| Cor | Hex | Uso nos cards |
|-----|-----|---------------|
| Verde Regeneracao | #3DAA35 | Barra, faixa topo |
| Azul Petroleo | #005F73 | Fundo principal |
| Rosa Transformacao | #D41A6A | Barra |
| Laranja Acao | #E86428 | Barra |
| Teal Futuro | #00A5B8 | Barra, faixa topo |
| Amarelo Consciencia | #F5B800 | Numeros, frases destaque |
| Branco | #FFFFFF | Texto, logo |

---

## Adaptacao LinkedIn

Gerar versao para LinkedIn como **documento PDF**:

1. Usar os mesmos 8 cards JPG
2. Combinar em PDF unico via Pillow
3. Caption LinkedIn:
   - **Gancho:** Dado ou pergunta provocadora sobre o tema
   - **Lista:** 5 conceitos numerados (titulo + 1 frase de contexto cada)
   - **Reflexao:** "O que isso significa para empresas brasileiras" (2-3 linhas)
   - **CTA consultivo:** "Quer saber como aplicar isso na sua empresa? Fale com nosso time."
   - **Hashtags:** maximo 5
4. Tom: 70% formal, 65% tecnico, 60% inspiracional (conforme `linkedin_strategy.md`)

---

## Conexao com Outras Skills

- Tema definido no `/plano-mensal` (arco ABT — semana 1 contexto, 2 problema, 3 solucao, 4 sintese)
- Frequencia: 1x por semana (segundas no calendario editorial)
- Pode alimentar o artigo mensal (`/artigo-mensal`)
- Independente do carrossel de noticias — complementar tematicamente
