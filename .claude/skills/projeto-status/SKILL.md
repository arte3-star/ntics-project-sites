---
name: projeto-status
description: "Reporta status executivo de um projeto NTICS: fase atual, próxima ação, deliverables pendentes e concluídos, blockers. Lê state.yaml + sincroniza com ClickUp."
user-invocable: true
---

# /projeto-status — Status executivo do projeto

Quando o usuário invocar `/projeto-status <slug>`, gere um resumo executivo do projeto.

## Entrada

- `<slug>` — obrigatório. Nome da pasta em `SecondBrain/projetos/`. Ex: `132-estacao-samarco`. Aceita aliases curtos (`132-samarco`) e normaliza para o canônico via prefixo numérico.
- Se slug não for fornecido, pergunte qual projeto ou liste opções de `SecondBrain/projetos/INDEX.md`.

## Passos

1. **Ler contexto do projeto:**
   - `SecondBrain/projetos/{slug}/CLAUDE.md` — contexto operacional
   - `SecondBrain/projetos/{slug}/state.yaml` — fase, deliverables, blockers, próxima ação
   - `SecondBrain/projetos/{slug}/tasks.yaml` — índice ClickUp

2. **Sincronizar status do ClickUp (se disponível):**
   - Usar MCP ClickUp para puxar status atual da `task_mae` em `tasks.yaml` via `get_task`.
   - Para subtasks listadas, puxar status se a sessão tiver quota.
   - Se ClickUp MCP não estiver carregado nesta sessão, pular a sincronização e usar apenas `tasks.yaml` local — sinalizar no relatório: "status ClickUp não sincronizado nesta sessão".

3. **Gerar relatório (formato Markdown):**
   ```markdown
   # {slug} — {nome do projeto}

   **Fase:** {state.fase} · **Atualizado:** {state.atualizado}

   ## Próxima ação
   {state.proxima_acao}

   ## Blockers ({contagem})
   - [{id}] {descricao} — responsável: {responsavel}

   ## Deliverables
   - ✅ {concluidos}/{total_design}  design
   - ✅ {concluidos}/{total_conteudo}  conteúdo
   - 🔴 Bloqueados por: {lista de blocker IDs}

   ## Top 3 próximos entregáveis
   {primeiros 3 `status: pendente` sem blocker, ordenados por prioridade P1 primeiro}

   ## ClickUp
   - Task-mãe: [{id}]({url}) — status: {status_fresh_ou_conhecido}
   ```

4. **Ao final**, sugira a próxima ação concreta: "Use `/projeto-briefing {slug} {id-do-próximo-deliverable}` para iniciar."

## Regras

- **Nunca invente status.** Se não conseguir ler state.yaml ou o projeto não existe, pergunte ao usuário.
- **Não modifique arquivos** — esta skill é read-only.
- Se o usuário pedir `/projeto-status` sem slug E só houver 1 projeto ativo em `SecondBrain/projetos/INDEX.md`, use esse automaticamente.
