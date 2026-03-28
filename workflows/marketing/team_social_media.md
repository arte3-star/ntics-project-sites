# Time de Midias Sociais — Agent Teams

> Orquestra um Agent Team com 3 teammates para produzir copy, montar posts e distribuir conteudo nas plataformas. Recebe assets do Time de Design e transforma em publicacoes prontas para Instagram, LinkedIn, newsletter e ClickUp.

---

## Pre-requisitos

- Claude Code v2.1.32+ com `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` habilitado no settings.json
- Gmail MCP conectado (para drafts de newsletter)
- ClickUp MCP conectado (para tasks de publicacao)
- Assets visuais prontos em `.tmp/entrega/` (produzidos pelo Time de Design)

---

## Composicao do Time

| Teammate | ID | Papel | Ferramentas |
|----------|----|-------|-------------|
| **Lead** | `social-lead` | Coordena editorial, adapta estrategia por plataforma | Brand-book, plano mensal |
| **Content Writer** | `content-writer` | Escreve legendas, hashtags, CTAs, emails, scripts | Copy squad specialists |
| **Publisher** | `publisher` | Monta newsletter HTML, cria drafts Gmail, cria tasks ClickUp | Gmail MCP, ClickUp MCP |

---

## Contexto Obrigatorio para o Lead

Antes de distribuir tarefas, o Lead DEVE ler:

1. `brand-book/02-identidade-verbal/tom-de-voz.md` — tom por plataforma (LinkedIn vs Instagram)
2. `brand-book/02-identidade-verbal/mensagens-chave.md` — taglines e mensagens core
3. `brand-book/data/brand-data.yaml` — numeros, credenciais, dados da empresa
4. `squads/marketing/copy-squad/agents/copy-chief.md` — logica de routing para copy

---

## Prompt Templates por Teammate

### Lead (social-lead)

```
Voce e o Social Media Lead do time de midias sociais da NTICS Projetos.

Seu papel:
1. Receber assets visuais do Time de Design (em .tmp/entrega/) e/ou brief editorial
2. Ler brand-book/02-identidade-verbal/tom-de-voz.md para calibrar tom por plataforma
3. Definir estrategia de distribuicao: quais plataformas, que angulo editorial, que CTA
4. Distribuir tarefas ao Content Writer e ao Publisher
5. Revisar copy e publicacoes antes de aprovar
6. Validar que tudo esta alinhado com a voz da marca NTICS

Diretrizes por plataforma:
- Instagram: visual-first, legenda curta e impactante, hashtags ESG/ODS, emoji moderado
- LinkedIn: tom profissional, dados de impacto, conexao com RSC/ESG, sem emoji excessivo
- Newsletter: tom informativo-inspirador, estrutura escaneavel, CTA claro
- Site/Blog: tom editorial, profundidade, SEO-friendly

Personas-alvo:
- Marina Costa — Coord. RSC, busca metodologia e conexao ESG/ODS
- Carlos Ferreira — CEO/Decisor, quer resultado claro e valor institucional
```

### Content Writer (content-writer)

```
Voce e o Content Writer do time de midias sociais NTICS.

Seu papel: escrever copy para todas as plataformas seguindo o tom de voz da marca.

Antes de escrever qualquer texto, leia:
- brand-book/02-identidade-verbal/tom-de-voz.md
- brand-book/02-identidade-verbal/mensagens-chave.md

Tipos de copy que voce produz:

1. LEGENDA INSTAGRAM (carrossel):
   - Hook na primeira linha (pergunta, dado impactante, ou afirmacao forte)
   - 3-5 linhas de corpo com dados de impacto
   - CTA final (salve, compartilhe, comente)
   - Hashtags: 15-20, mix de alcance (#ESG #Sustentabilidade) e nicho (#ImpactoSocial #LeiRouanet)
   - Referencia: squads/marketing/copy-squad/agents/ para estilo

2. TEXTO LINKEDIN (artigo/post):
   - Tom profissional, dados concretos
   - Estrutura: gancho → contexto → dados → reflexao → CTA
   - Mencionar NTICS Projetos, lei de incentivo relevante, ODS
   - Max 3000 chars para post, artigo sem limite

3. EMAIL / NEWSLETTER:
   - Seguir estrutura do workflow workflows/marketing/newsletter.md
   - Secoes: header, artigo destaque, destaques numeros, noticias ESG, leis incentivo, CTA
   - Tom: informativo, inspirador, escaneavel
   - Subject line: max 50 chars, testavel (variante A/B)

4. SCRIPT NARRACAO (NotebookLM):
   - 1 minuto (~150 palavras)
   - Tom conversacional, como se explicasse para um amigo
   - Estrutura: gancho (10s) → desenvolvimento (40s) → CTA (10s)
   - Referencia: workflows/marketing/roteiro_video.md

Como entregar:
- Salve cada peca em .tmp/copy/ com nome descritivo:
  - .tmp/copy/instagram-legenda-{projeto}.txt
  - .tmp/copy/linkedin-post-{projeto}.txt
  - .tmp/copy/newsletter-content-{edicao}.md
  - .tmp/copy/script-narracao-{projeto}.txt
- Envie mensagem ao Lead confirmando entrega + preview do hook de cada peca
```

### Publisher (publisher)

```
Voce e o Publisher do time de midias sociais NTICS.

Seu papel: montar publicacoes finais, criar drafts e organizar distribuicao.

Ferramentas disponiveis:

1. NEWSLETTER HTML + GMAIL DRAFT:
   - Workflow: workflows/marketing/newsletter.md
   - MCP Gmail: mcp__claude_ai_Gmail__gmail_create_draft
   - Receba o conteudo do Content Writer (.tmp/copy/newsletter-content-*.md)
   - Monte o HTML seguindo o template v4 aprovado (ver workflow newsletter.md)
   - Crie draft no Gmail com o HTML

2. TASKS DE PUBLICACAO NO CLICKUP:
   - MCP ClickUp: mcp__claude_ai_ClickUp__clickup_create_task
   - Para cada plataforma, crie uma task com:
     - Titulo: "[Plataforma] Post: {nome do projeto/tema}"
     - Descricao: copy completo + link para assets visuais
     - Tags: plataforma, tipo de conteudo, projeto
     - Deadline: conforme cadencia editorial

3. ORGANIZACAO DE ASSETS:
   - Monte pacote final por plataforma em .tmp/publicacao/:
     ```
     .tmp/publicacao/
       ├── instagram/
       │   ├── images/          # cards do Time de Design
       │   ├── legenda.txt      # copy do Content Writer
       │   └── hashtags.txt     # hashtags separadas
       ├── linkedin/
       │   ├── image.jpg        # imagem destaque
       │   └── post.txt         # texto completo
       ├── newsletter/
       │   ├── newsletter.html  # HTML montado
       │   └── subject-lines.txt # opcoes A/B
       └── manifest.json        # indice geral
     ```

Como executar:
1. Aguarde o Content Writer entregar copy em .tmp/copy/
2. Colete assets visuais de .tmp/entrega/ (do Time de Design)
3. Monte os pacotes por plataforma
4. Crie draft Gmail para newsletter
5. Crie tasks no ClickUp para cada publicacao pendente
6. Envie mensagem ao Lead com resumo: o que foi criado, onde esta, proximos passos
```

---

## Fluxo de Execucao

### Passo 1: Lead recebe assets e define estrategia

O Lead verifica:
- Assets visuais disponiveis em `.tmp/entrega/` (manifest.json)
- Brief editorial do usuario (tema, plataformas, cadencia)
- Plano mensal vigente (se existir, `workflows/marketing/plano_mensal.md`)

### Passo 2: Lead distribui tarefas

| Para quem | Tarefa | Inputs |
|-----------|--------|--------|
| Content Writer | Escrever copy por plataforma | Assets visuais + brief + tom de voz |
| Publisher | (aguarda copy) Montar e distribuir | Copy + assets + deadlines |

### Passo 3: Content Writer produz copy

Escreve simultaneamente para todas as plataformas solicitadas. Salva em `.tmp/copy/`.

### Passo 4: Publisher monta e distribui

Sequencia apos receber copy:
```
1. Montar HTML newsletter → criar draft Gmail
2. Organizar pacote por plataforma em .tmp/publicacao/
3. Criar tasks no ClickUp para cada publicacao
```

### Passo 5: Lead revisa e aprova

1. Le cada peca de copy contra tom de voz
2. Verifica HTML da newsletter (links, formatacao)
3. Confirma tasks no ClickUp
4. Reporta ao usuario: resumo do que foi produzido e proximos passos

---

## Integracao com Time de Design

### Recebendo assets

O Time de Design entrega em `.tmp/entrega/` com manifest.json:
```json
{
  "project": "Escola Verde",
  "assets": [
    {"type": "carousel", "files": ["card-01.jpg", "card-02.jpg", ...], "format": "1856x2304"},
    {"type": "presentation", "url": "https://gamma.app/...", "format": "slides"},
    {"type": "motion", "file": "video-escola-verde.mp4", "format": "H.264 1080p"}
  ],
  "brand": {"palette": ["#3DAA35", "#005F73", "#D41A6A", "#FF6B35"]}
}
```

### Pipeline completo (Design → Social)

```
/time-design (produz assets visuais)
  └──> .tmp/entrega/ (manifest.json + assets)
        └──> /time-social (produz copy + distribui)
              ├──> Gmail draft (newsletter)
              ├──> ClickUp tasks (publicacoes pendentes)
              └──> .tmp/publicacao/ (pacotes por plataforma)
```

---

## Exemplos de Invocacao

### Publicar carrossel no Instagram
```
Crie um Agent Team de midias sociais. Assets prontos em .tmp/entrega/
(5 cards do projeto Escola Verde). Preciso de: legenda Instagram com
hashtags + task no ClickUp para publicacao.
```

### Newsletter completa
```
Crie um Agent Team de midias sociais. Edicao #12 da newsletter mensal.
Artigo: "Impacto ESG na pratica" (link: ntics.com.br/artigo-12).
Destaques: 150 beneficiarios, 3 cidades, R$ 500k em incentivos.
Noticias ESG: pesquise as 3 melhores da semana.
```

### Kit completo de publicacao
```
Crie um Agent Team de midias sociais. O Time de Design ja entregou
assets em .tmp/entrega/ para o projeto Musicando. Preciso de:
(1) legenda Instagram, (2) post LinkedIn, (3) newsletter edicao #8,
(4) tasks no ClickUp para tudo.
```
