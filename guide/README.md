# Guia: Assessor Pessoal IA com Claude Code

> Como usar Claude Code como um copiloto executivo que entende projetos, clientes e executa tarefas — para quem está começando do zero.

---

## O que é isso

Esse guia foi construído a partir de uma pesquisa das melhores práticas globais de uso de Claude Code para gestão de projetos e empresas (Chase H · Nate Herk · Garry Tan/YC · Simon Willison · Shrivu Shankar, março–maio 2026).

O objetivo: você sair daqui com um **assessor pessoal IA** funcionando em 4 passos, sem precisar de toda a infraestrutura avançada da NTICS.

**Relatório visual completo:** [relatorio-assessor-ia.html](relatorio-assessor-ia.html) — abra no navegador.

---

## A estrutura de quem está começando do zero

```
meu-projeto/
├── CLAUDE.md              # regras e contexto do projeto (o cérebro)
├── memory/
│   ├── MEMORY.md          # índice da memória persistente
│   ├── sobre-mim.md       # seu perfil, papel, prioridades
│   ├── sobre-o-projeto.md # contexto do projeto/empresa
│   └── feedback.md        # o que funcionou e o que não funcionou
├── stakeholders.yaml      # quem é quem, tom de comunicação
├── state.yaml             # fase atual, próximas ações, blockers
├── voice.md               # tom de voz para comunicação
└── .claude/
    └── skills/            # comandos personalizados (atalhos)
```

Copie os templates da pasta [`templates/`](templates/) e adapte para o seu contexto.

---

## Os 4 passos para montar seu assessor

### Passo 1 — Context (conhece o negócio)

> **Teste:** sessão fresca do Claude responde "quem é o cliente, qual fase, qual o tom" sem precisar buscar nada.

1. Copie [`templates/CLAUDE.md`](templates/CLAUDE.md) para a raiz do seu projeto
2. Preencha as seções: missão, papel, projetos ativos, regras de comunicação
3. Copie [`templates/sobre-o-projeto.md`](templates/sobre-o-projeto.md) para `memory/`
4. Copie [`templates/stakeholders.yaml`](templates/stakeholders.yaml) e liste as pessoas-chave

Abra o Claude Code e teste: `"Quem são os stakeholders do projeto X e qual o tom ideal pra comunicação com eles?"`

---

### Passo 2 — Connections (alcança os sistemas)

> **Teste:** dados do ClickUp/Notion/Gmail chegam sem você precisar copiar e colar.

Configure os MCPs (integrações) que você usa. Edite o arquivo `.mcp.json` na raiz:

```json
{
  "mcpServers": {
    "clickup": {
      "command": "npx",
      "args": ["-y", "@composio-core/mcp@latest", "--toolkits", "clickup"],
      "env": { "COMPOSIO_API_KEY": "SUA_CHAVE_AQUI" }
    },
    "gmail": {
      "command": "npx",
      "args": ["-y", "@composio-core/mcp@latest", "--toolkits", "gmail"],
      "env": { "COMPOSIO_API_KEY": "SUA_CHAVE_AQUI" }
    }
  }
}
```

Opções: ClickUp, Notion, Linear, Jira, Gmail, Google Calendar, Google Drive, Slack.

---

### Passo 3 — Capabilities (executa workflows)

> **Teste:** uma frase curta dispara um processo de várias etapas e devolve artefato pronto.

Crie suas primeiras skills em `.claude/skills/`. Comece com as 3 mais úteis:

| Skill | O que faz |
|-------|-----------|
| `/status` | Lê o estado atual do projeto e reporta fase, próximos passos, blockers |
| `/email` | Gera rascunho de e-mail para stakeholder no tom certo |
| `/ata` | Converte notas de reunião em ata estruturada + decisões + tasks |

Copie os templates em [`templates/skills/`](templates/skills/) para `.claude/skills/`.

---

### Passo 4 — Cadence (roda sozinho)

> **Teste:** um workflow dispara no horário ou por evento, com laptop fechado.

Só configure automação depois que os passos 1-3 estiverem funcionando manualmente.

Exemplo de rotina matinal (configure via `/schedule` no Claude Code):

```
Toda manhã às 8h:
- Leia as tasks do ClickUp que vencem essa semana
- Leia os e-mails não lidos das últimas 12h
- Leia o state.yaml do projeto ativo
- Gere um briefing de 5 bullets: decisões do dia, riscos, follow-ups pendentes
- Envie como rascunho para meu Gmail
```

> **Regra de ouro (Nate Herk):** não automatize (Cadence) um workflow manual que ainda está quebrado.

---

## Os 7 níveis de maturidade

Scale criada por Chase H para saber onde você está:

| Nível | O que você tem | Próximo passo |
|-------|---------------|---------------|
| 1 | Prompting básico no terminal | Criar CLAUDE.md |
| 2 | CLAUDE.md + slash commands | Criar skills |
| **3** | **Skills versionadas** | **Memória persistente** |
| 4 | Memória + hooks automáticos | Automation local |
| 5 | Agent teams (chief + specialists) | Dashboard de acesso |
| 6 | Agentic OS multi-domínio | Iteração contínua |

**Comece pelo nível 1 e suba um nível por semana.** Tentar chegar ao nível 5 sem passar pelos anteriores é o erro mais comum.

---

## Regras que todo mundo aprende na raça

Coletadas de Chase H, Nate Herk, Garry Tan e Simon Willison:

- **CLAUDE.md menor que 200 linhas** funciona melhor. Arquivo enorme que ninguém lê não é contexto, é ruído.
- **Human-in-the-loop sempre antes de publicar.** Nada vai para cliente, rede social ou e-mail sem aprovação humana.
- **Boring is beautiful. Workflows beat agents.** Processo determinístico antes de agente autônomo.
- **Não confie no 200 OK.** Após criar uma task no ClickUp, confirme que existe. Após enviar draft, confirme no Gmail.
- **Modelo certo para cada tarefa:** modelo mais barato (Haiku) para coleta e triagem; modelo intermediário (Sonnet) para criação; modelo mais poderoso (Opus) só para planejamento estratégico.
- **Memória é o problema #1.** Sem persistência, você ensina o mesmo contexto toda sessão. Mantenha MEMORY.md atualizado.
- **Voice-lock por cliente/plataforma.** LinkedIn tem tom diferente do WhatsApp. Documente em `voice.md`.

---

## O que NÃO fazer (anti-patterns)

- Dar ao agente acesso a produção sem aprovação humana nas ações críticas
- Automatizar tudo de uma vez antes de testar manualmente
- Usar o mesmo tom de escrita em todas as plataformas
- Criar subagentes para tarefas simples que uma skill resolve
- Publicar sem revisão humana (nenhum dos três frameworks recomenda isso)

---

## Ferramentas e recursos para aprofundar

| Recurso | O que tem | Link |
|---------|-----------|------|
| Chase H | Agentic OS, 7 Levels of Marketing, Content System | chaseai.io/blog |
| Nate Herk | AIOS framework, Four Cs, Three Ms | nateherk.com |
| Garry Tan | gstack — 23 personas open-source (MIT) | github.com/garrytan/gstack |
| Simon Willison | Skills vs MCP, usos práticos | simonwillison.net |
| Shrivu Shankar | Setup pessoal completo, project structure | blog.sshh.io |
| Sid Saladi | Templates de projeto prontos | sidsaladi.substack.com |
| awesome-claude-code | Curadoria de skills e subagents | github.com/hesreallyhim/awesome-claude-code |
| Docs oficiais | Skills, hooks, subagents, scheduling | code.claude.com/docs |

---

## Estrutura avançada (quando você tiver tudo funcionando)

Depois que os 4 passos estiverem rodando, a evolução natural é:

1. **Skills por área** (PMO, Marketing, Comunicação, Financeiro)
2. **Subagents especializados** (Chief delega para Specialist)
3. **Dashboard de acesso** para pessoas não-técnicas rodarem skills sem terminal
4. **Audit trail automático** de todas as ações (JSONL append-only)
5. **Relatórios automáticos** para cliente toda semana

---

## Contribuindo

Se você criar uma skill útil, template ou aprendizado novo, adicione à pasta `templates/skills/` e abra um PR. Esse guia cresce com o uso.

---

*Pesquisa: Lucas Rotta · NTICS Projetos · Maio 2026*  
*Referências: Chase H, Nate Herk, Garry Tan, Simon Willison, Shrivu Shankar, Anthropic docs*
