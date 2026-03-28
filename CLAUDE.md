# Agent Instructions

You're working inside the **WAT framework** (Workflows, Agents, Tools). This architecture separates concerns so that probabilistic AI handles reasoning while deterministic code handles execution. That separation is what makes this system reliable.

## The WAT Architecture

**Layer 1: Workflows (The Instructions)**
- Markdown SOPs stored in `workflows/`, organizadas por área
- Each workflow defines the objective, required inputs, which tools to use, expected outputs, and how to handle edge cases
- Written in plain language, the same way you'd brief someone on your team

**Layer 2: Agents (The Decision-Maker)**
- This is your role. You're responsible for intelligent coordination.
- Read the relevant workflow, run tools in the correct sequence, handle failures gracefully, and ask clarifying questions when needed
- You connect intent to execution without trying to do everything yourself
- Example: If you need to pull data from a website, don't attempt it directly. Read the relevant workflow, figure out the required inputs, then execute the appropriate tool

**Layer 3: Tools (The Execution)**
- Python scripts in `tools/` that do the actual work
- API calls, data transformations, file operations, database queries
- Credentials and API keys are stored in `.env`
- These scripts are consistent, testable, and fast

**Why this matters:** When AI tries to handle every step directly, accuracy drops fast. If each step is 90% accurate, you're down to 59% success after just five steps. By offloading execution to deterministic scripts, you stay focused on orchestration and decision-making where you excel.

## How to Operate

**1. Look for existing workflows and tools first**
Before building anything new, check `workflows/` for the relevant SOP and `tools/` for existing scripts. Only create new ones when nothing exists for that task.

**2. Learn and adapt when things fail**
When you hit an error:
- Read the full error message and trace
- Fix the script and retest (if it uses paid API calls or credits, check with me before running again)
- Document what you learned in the workflow (rate limits, timing quirks, unexpected behavior)
- Example: You get rate-limited on an API, so you dig into the docs, discover a batch endpoint, refactor the tool to use it, verify it works, then update the workflow so this never happens again

**3. Keep workflows current**
Workflows should evolve as you learn. When you find better methods, discover constraints, or encounter recurring issues, update the workflow. That said, don't create or overwrite workflows without asking unless I explicitly tell you to. These are your instructions and need to be preserved and refined, not tossed after one use.

## The Self-Improvement Loop

Every failure is a chance to make the system stronger:
1. Identify what broke
2. Fix the tool
3. Verify the fix works
4. Update the workflow with the new approach
5. Move on with a more robust system

This loop is how the framework improves over time.

## File Structure

**Directory layout:**
```
workflows/                  # SOPs organizadas por área
  ├── escritorio-projetos/  # PMO: planejamento, execução, comunicação
  ├── inscricao-projetos/   # Estruturação e submissão a leis de incentivo
  ├── marketing/            # Produção de conteúdo, newsletters, carrosséis
  └── knowledge/            # Referência compartilhada (templates, anexos, manuais)
tools/                      # Python scripts for deterministic execution
squads/                     # Times de agentes especialistas por área
  └── marketing/            # 10 squads: brand, copy, traffic, storytelling, etc.
brand-book/                 # Identidade visual e verbal NTICS (referência compartilhada)
.claude/skills/             # Atalhos /comando que apontam para workflows
.tmp/                       # Temporary files. Regenerated as needed.
.env                        # API keys (NEVER store secrets anywhere else)
credentials.json, token.json  # Google OAuth (gitignored)
```

**Core principle:** Local files are just for processing. Anything I need to see or use lives in cloud services. Everything in `.tmp/` is disposable.

**Skills vs Workflows:** Skills (`.claude/skills/`) são atalhos leves que invocam workflows via `/comando`. A SOP real (com fases, inputs, checklists) sempre vive em `workflows/`. Quando alguém digita `/newsletter`, o skill diz "leia e execute `workflows/marketing/newsletter.md`".

## Workflows por Área

### Escritório de Projetos (`workflows/escritorio-projetos/`)

SOPs de planejamento, estruturação e gestão de projetos NTICS.

| Workflow | Arquivo | Quando usar |
|----------|---------|-------------|
| Termo de Abertura | `termo_abertura.md` | Novo projeto precisa de estruturação formal (TA) |
| Perfil Estratégico | `perfil_estrategico.md` | Analisar empresa antes de proposta/TA |
| Plano de Divulgação | `plano_divulgacao.md` | Criar comunicação + releases (requer TA + PEP) |
| Roteiro Edição Vídeo | `roteiro_edicao_video.md` | Criar script de vídeo pré-projeto |
| Briefing Website | `briefing_website.md` | Montar conteúdo para site do projeto |
| Engenhoca Prestação Contas | `engenhoca_prestacao_contas.md` | Automação de prestação de contas Rouanet |
| Processamento de Reuniões | `process_meeting_transcript.md` | Transcrição → classificação → tasks no ClickUp |
| Carrossel Projeto Cliente | `carrossel_projeto_cliente.md` | Carrossel com identidade visual do patrocinador (pesquisa marca + Leonardo AI) |
| Criar Site do Projeto | `criar_site_projeto.md` | Site institucional no Lovable (briefing ClickUp + assets Drive + GitHub + Jinja2/Tailwind) |

**Cadeia de dependências típica:**
```
Perfil Patrocinador ──┐
                      ├──> Termo de Abertura ──> Plano Divulgação ──> Roteiro Vídeo
                      │                                              └──> Briefing Website ──> Criar Site (Lovable)
```

### Inscrição de Projetos (`workflows/inscricao-projetos/`)

SOPs para estruturação e submissão de projetos a leis de incentivo.

| Workflow | Arquivo | Quando usar |
|----------|---------|-------------|
| Estruturador Lei Rouanet | `estruturador_rouanet.md` | Estruturar projeto para inscrição MinC |
| Conselheiro SALIC | `conselheiro_salic.md` | Preencher campos SALIC campo-a-campo |
| Conselheiro Lei Reciclagem | `conselheiro_reciclagem.md` | Execução/diligências/PC Lei Reciclagem |

### Marketing (`workflows/marketing/`)

SOPs de produção de conteúdo, editorial e comunicação. Invocáveis via `/comando`.

| Workflow | Arquivo | Comando | Quando usar |
|----------|---------|---------|-------------|
| Plano Mensal | `plano_mensal.md` | `/plano-mensal` | Planejamento editorial do mês (arco ABT + hooks) |
| Roteiro Vídeo | `roteiro_video.md` | `/roteiro-video` | Script de 1 min para NotebookLM |
| Carrossel Projeto | `carrossel_projeto.md` | `/carrossel-projeto` | 5 cards Instagram via Leonardo AI |
| Carrossel Notícias | `carrossel_noticias.md` | `/carrossel-noticias` | 8 cards ESG news (Perplexity + Leonardo AI) |
| Artigo Mensal | `artigo_mensal.md` | `/artigo-mensal` | Compila 4 roteiros em artigo integrado |
| Email Marketing | `email_marketing.md` | `/email-marketing` | Conteúdo newsletter mensal (7 seções) |
| Newsletter | `newsletter.md` | `/newsletter` | HTML completo + draft Gmail |
| Artigo Site | `artigo_site.md` | `/artigo-site` | Página HTML para ntics.com.br |
| Newsletter Semanal | `weekly_csr_newsletter.md` | — | Newsletter semanal ESG (pipeline Python) |
| Newsletter Mensal (artigo) | `monthly_article_newsletter.md` | — | Newsletter mensal com artigo hero |
| Uso de Squads | `uso_squads_marketing.md` | — | Como invocar squads de marketing |

**Cadeia editorial típica:**
```
/plano-mensal
  ├→ /roteiro-video × 4
  ├→ /carrossel-projeto
  ├→ /carrossel-noticias
  └→ /artigo-mensal
       └→ /email-marketing
            └→ /newsletter
/artigo-site (independente)
```

**Knowledge files** (referência compartilhada): `workflows/knowledge/`

## Squads de Agentes Especialistas

Times de agentes com hierarquia Chief → Specialists. Cada squad tem um orquestrador (chief) que roteia para o especialista certo. Organizados por área em `squads/`.

### Como usar um squad

1. Identifique o squad pelo tipo de problema (tabela abaixo)
2. Leia o `squad.yaml` do squad para entender a estrutura
3. Leia o agente chief (orquestrador) para entender o routing
4. O chief indica qual especialista usar — leia o agente especialista
5. Execute a task seguindo as instruções do especialista
6. Valide contra o `checklists/output-quality.md` do squad

### Marketing (`squads/marketing/`)

| Squad | Pasta | Chief | Quando usar |
|-------|-------|-------|-------------|
| Advisory Board | `squads/marketing/advisory-board/` | `board-chair` | Decisões estratégicas, investimento, liderança, cultura |
| Brand Squad | `squads/marketing/brand-squad/` | `brand-chief` | Posicionamento, identidade, naming, arquétipos, messaging |
| C-Level Squad | `squads/marketing/c-level-squad/` | `vision-chief` | Planejamento estratégico, operações, GTM, tecnologia |
| Copy Squad | `squads/marketing/copy-squad/` | `copy-chief` | Copywriting, emails, VSL, sales letters, headlines, landing pages |
| Data Squad | `squads/marketing/data-squad/` | `data-chief` | Analytics, métricas, CLV, growth, retenção, comunidade |
| Design Squad | `squads/marketing/design-squad/` | `design-chief` | Design systems, UX/UI, atomic design, componentes |
| Hormozi Squad | `squads/marketing/hormozi-squad/` | `hormozi-chief` | Ofertas, lead gen, pricing, vendas, hooks, lançamentos |
| Movement | `squads/marketing/movement/` | `movement-chief` | Construção de movimentos, manifestos, identidade coletiva |
| Storytelling | `squads/marketing/storytelling/` | `story-chief` | Narrativas, roteiros, brand storytelling, pitches |
| Traffic Masters | `squads/marketing/traffic-masters/` | `traffic-chief` | Tráfego pago, Facebook/YouTube/Google Ads, media buying |

### Estrutura de cada squad

```
squads/{area}/{squad-name}/
├── squad.yaml           # Manifesto: agentes, tasks, workflows, routing
├── config/config.yaml   # Tiers, handoffs, ativação
├── agents/              # Agentes MD (chief + especialistas)
├── tasks/               # Definições de tarefas com input/output
├── workflows/           # Orquestrações multi-fase (YAML)
├── checklists/          # Quality gates
└── data/                # Catálogos de frameworks e routing
```

## Brand Book NTICS

Identidade completa da NTICS em `brand-book/`. Recurso compartilhado por todos os workflows e squads.

| Seção | Pasta | Conteúdo |
|-------|-------|----------|
| Fundação | `brand-book/01-fundacao/` | Propósito, posicionamento, arquétipo, prisma de identidade |
| Identidade Verbal | `brand-book/02-identidade-verbal/` | Tom de voz, mensagens-chave, brand story, dos & don'ts |
| Identidade Visual | `brand-book/03-identidade-visual/` | Logo, cores, tipografia, fotografia, elementos gráficos |
| Design System | `brand-book/04-design-system/` | Grid, componentes, tokens |
| Aplicações | `brand-book/05-aplicacoes/` | Papelaria, digital, materiais, apresentações |
| Governança | `brand-book/06-governance/` | Regras de uso, aprovação, versionamento |
| Dados | `brand-book/data/brand-data.yaml` | Números, credenciais, clientes, taglines (fonte única de verdade) |

**Regra:** Sempre consulte `brand-book/data/brand-data.yaml` para números da NTICS e `brand-book/02-identidade-verbal/tom-de-voz.md` para calibrar o tom antes de produzir qualquer conteúdo.

## APIs de Conteúdo

APIs usadas pelos workflows de marketing (chaves em `.env`):

| API | Uso | Variável |
|-----|-----|----------|
| Leonardo AI | Geração de imagens (nano-banana-2, 4:5 Instagram) | `LEONARDO_API_KEY` |
| Perplexity | Busca de notícias ESG/CSR (sonar, filtro semanal) | `PERPLEXITY_API_KEY` |
| Unsplash | Imagens stock (fallback) | `UNSPLASH_API_KEY` |
| Gmail | Criação de drafts de newsletter (via MCP) | Google OAuth |

## Bottom Line

You sit between what I want (workflows) and what actually gets done (tools). Your job is to read instructions, make smart decisions, call the right tools, recover from errors, and keep improving the system as you go.

When you receive a request:
1. Identify the area (marketing, projetos, inscrição, etc.)
2. Find the relevant workflow in `workflows/{area}/`
3. For marketing, check if squads can help with specialized expertise
4. Always consult `brand-book/` before producing any NTICS content

Stay pragmatic. Stay reliable. Keep learning.
