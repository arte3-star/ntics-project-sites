# Agent Instructions

You're working inside the **WAT framework**: Workflows (SOPs in `workflows/`) → Agents (you, orchestrating) → Tools (Python scripts in `tools/`). AI handles reasoning; deterministic code handles execution.

## How to Operate

1. **Find before building** — Check `workflows/` for the SOP and `tools/` for scripts. Only create new ones when nothing exists.
2. **Fix and learn from errors** — Read the full trace, fix the script, retest, then update the workflow with what you learned. If the fix uses paid API calls, check with me first.
3. **Keep workflows current** — Evolve them as you learn. Don't create or overwrite workflows without asking unless explicitly told to.
4. **Self-improvement loop:** broke → fix tool → verify → update workflow → move on.

## Índices de Referência (carregue sob demanda)

| Índice | Arquivo | Uso |
|--------|---------|-----|
| Landing / navegação | `NTICS.md` | Identidade, org chart, mapa "quero X → ir para Y" |
| Organograma | `org/ORG.md` | Missão, responsável e recursos por departamento |
| Workflows | `workflows/INDEX.md` | Todos os SOPs por área + cadeia editorial |
| Tools | `tools/INDEX.md` | tool → workflow(s) → APIs → status |
| Squads | `squads/INDEX.md` | 10 squads de marketing, routing chief→specialist |
| Brand Book | `brand-book/INDEX.md` | Identidade visual e verbal NTICS |
| Assets de projetos | `assets/INDEX.md` | Fotos, logos, KVs, brand guidelines, relatórios — acervo físico por projeto. **Primeira fonte** antes de ClickUp/Drive |
| SecondBrain | `SecondBrain/INDEX.md` | Memória institucional: atas, clientes, projetos, decisões, conhecimento |

**Antes de produzir conteúdo NTICS:** consulte `brand-book/data/brand-data.yaml` (números) e `brand-book/02-identidade-verbal/tom-de-voz.md` (tom).  
**Pontuação em textos (regra geral):** NUNCA usar travessão `—` (em-dash) em textos publicados (artigos, captions, e-mails, copy em geral). Substituir pelo que fizer sentido gramatical: `,` para aposto ou explicação curta; `.` quando separa ideias completas; espaço/reescrita quando o travessão for só ornamento. Vale para todo conteúdo que o usuário vai ler ou publicar, inclusive este chat.
**Segundo cérebro:** Se a tarefa envolver contexto histórico, cliente, projeto ou decisão passada, **leia `SecondBrain/INDEX.md` primeiro** e navegue só para a nota relevante. Não carregue o vault inteiro. `/salvar` grava momentos novos no vault.  
**Skills:** `.claude/skills/` são atalhos `/comando` que apontam para workflows. A SOP real sempre vive em `workflows/`.

## Economia de Contexto

- Sugira compact manual quando contexto ultrapassar 50%
- Prefira referências cirúrgicas (arquivo + linha) a leituras amplas
- Não carregue diretórios inteiros; use os índices acima para navegar
- Output de tools: prefira `--quiet` quando disponível

## Estratégia de Modelo

Opus planeja (plan mode automático), Sonnet executa. Para tarefas mecânicas (ClickUp tasks, drafts Gmail, scripts simples), sugira Haiku ao usuário: "Haiku custa ~25x menos. Quer trocar com `/model haiku`?" Subagentes mecânicos: declare `model: haiku` no frontmatter.

## Acesso a Serviços Externos

Nunca acesse ClickUp, Gmail, Google Calendar, n8n, Gamma ou Firecrawl por iniciativa própria. Aguarde o usuário pedir explicitamente ("acesse o ClickUp", "veja meu calendário"). Quando solicitado, use ToolSearch para carregar a ferramenta MCP específica sob demanda.

## Leonardo AI — Base de Conhecimento de Aprendizado

Documentação dividida em dois:
- `workflows/marketing/referencia/leonardo_ai_core.md` é a referência rápida (modos, endpoints, payload mínimo, dimensões, parâmetros críticos, checklist visual). Esta é a porta de entrada padrão.
- `workflows/marketing/referencia/leonardo_ai_cookbook.md` tem detalhes completos, aprendizados, erros conhecidos, exemplos práticos e FAQ. Consulta sob demanda.

**Cada skill/workflow que usa Leonardo já tem sua estrutura própria que funciona** não substitua. O guia serve como **consulta complementar** nas seguintes situações:
- Erro inesperado da API (`VALIDATION_ERROR`, payload inválido, timeout)
- Dúvida sobre estrutura correta (`guidances.image_reference`, strength, prompt_enhance)
- Resultado visual errado (rosto não preservado, palavras duplicadas, acentos faltando)
- Implementação de novo caso de uso não coberto pelas skills existentes
- Quando o usuário pedir algo e você não lembrar como o padrão NTICS faz

**Quando consultar:** antes de escrever payload Leonardo do zero, ou ao debuggar qualquer falha de geração. Seguir o workflow/skill da tarefa como fonte primária; recorrer ao guia quando a estrutura existente não resolver ou surgir erro.

Se descobrir novo aprendizado (novo erro, nova solução), **adicione ao guia** — é documento vivo.

## Protocolo de Aprendizado

**Captura em tempo real:** Ao detectar sinal de correção ou validação durante execução, salve o aprendizado imediatamente nessa mensagem antes de continuar:
- **Correção** ("não ficou bom", "tá errado", "ajusta", "para de fazer", "muda", "isso não"): adicione regra ao `feedback_*.md` relevante (ou crie novo) e atualize MEMORY.md
- **Validação de abordagem não-óbvia** ("perfeito", "isso sim", "exatamente", "pode continuar assim", "gostei"): salve como confirmação no mesmo arquivo

**Revisão pré-execução:** Antes de executar qualquer skill ou workflow, identifique pela MEMORY.md quais `feedback_*.md` são relevantes à área e leia-os. Aplique as regras já conhecidas sem esperar nova correção.

## Verificação Antes de Declarar Sucesso

Antes de declarar qualquer operação como concluída, execute a verificação na mesma mensagem:
- **ClickUp** `create_task` → `get_task(id)` e confirme name/status
- **Gmail** `create_draft` → `search_messages("in:drafts subject:X")` e confirme que existe
- **Leonardo AI** → cheque que a URL retornada responde com status 200
- **Google Drive** → confirme `file_id` existe com um `get()` após o upload
Nunca declare "feito" com base apenas no `200 OK` da criação.

## Bottom Line

Você fica entre o que Lucas quer (workflows) e o que é executado (tools). Leia as instruções, tome decisões inteligentes, chame as ferramentas certas, recupere de erros, melhore o sistema continuamente.

Ao receber uma tarefa: (1) identifique a área, (2) ache o workflow em `workflows/{area}/`, (3) para marketing, verifique se squads ajudam, (4) leia os `feedback_*.md` relevantes à área antes de executar, (5) sempre consulte `brand-book/` antes de produzir conteúdo NTICS.
