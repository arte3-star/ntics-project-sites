---
name: projeto-tasks-sync
description: "Sincronização bidirecional informativa entre ClickUp e tasks.yaml de um projeto NTICS. Puxa estado atual da lista ClickUp, faz diff com snapshot anterior (em _cache/clickup-snapshot.json), e apresenta 3 grupos: novo no ClickUp (importar?), fechado no ClickUp (avançar deliverable?), mudou status. Sempre pergunta antes de mudar tasks.yaml. Nunca escreve no ClickUp."
user-invocable: true
---

# /projeto-tasks-sync — Espelhamento ClickUp ↔ tasks.yaml

Quando o usuário invocar `/projeto-tasks-sync <slug>`, sincronize o estado das tasks ClickUp do projeto com o `tasks.yaml` local, com **diff explícito** e confirmação antes de modificar.

## Entrada

- `<slug>` — pasta em `SecondBrain/projetos/`. Ex: `128-cnh-festival-agricultura`.

## Passos

### 1. Carregar MCP ClickUp via ToolSearch

```
ToolSearch query="select:mcp__5cef576d-bc98-4847-9b33-9ca9928ad708__clickup_filter_tasks,mcp__5cef576d-bc98-4847-9b33-9ca9928ad708__clickup_get_task"
```

### 2. Ler estado local

- `SecondBrain/projetos/{slug}/tasks.yaml` — pegar `list_id`, `task_mae.id`, `subtasks_prioritarias`.
- `SecondBrain/projetos/{slug}/_cache/clickup-snapshot.json` — snapshot anterior.

### 3. Puxar estado atual do ClickUp

- `clickup_filter_tasks(list_ids=[list_id], subtasks=true, include_closed=true)` → tasks atuais.
- Para a `task_mae`, opcionalmente puxar comentários com `clickup_get_task_comments` (só se a task tem reply_count > 0 e usuário pediu detalhado).

### 4. Calcular diff vs snapshot anterior

Comparar a lista atual de tasks (id → status) com o snapshot. Categorizar:

- **Tasks novas** (estão no ClickUp atual, NÃO estavam no snapshot): podem ser importadas para `subtasks_prioritarias` em tasks.yaml.
- **Tasks fechadas** (estavam pendentes/in_progress no snapshot, agora `complete`/`closed`): podem avançar deliverable correspondente no state.yaml se mapeadas.
- **Status alterados** (estão em ambos, mas status mudou — ex: `backlog` → `in_progress`): apenas reportar.
- **Tasks removidas** (estavam no snapshot, sumiram): provavelmente arquivadas; reportar.

### 5. Apresentar diff ao usuário

```markdown
# Diff ClickUp para {slug}

## Novas no ClickUp ({N})
- [{id}] {nome} — status: {status} — assignee: {assignee}
- ...

## Fechadas no ClickUp ({M})
- [{id}] {nome} — mapeia para deliverable: {deliverable-id se conhecido}
- ...

## Status alterados ({P})
- [{id}] {nome}: {antes} → {agora}
- ...

## Tasks sumidas ({Q})
- [{id}] {nome} (último status conhecido: {x})
```

### 6. Perguntar via AskUserQuestion

Uma pergunta para cada grupo não-vazio (max 4):

- **Importar tasks novas para tasks.yaml?** "Sim, todas" / "Selecionar" / "Não, só atualizar snapshot".
- **Avançar deliverables das tasks fechadas?** "Sim, listar deliverables a marcar concluído" / "Não, só registrar status".
- **Aplicar mudanças de status no tasks.yaml?** "Sim" / "Não".

### 7. Aplicar mudanças confirmadas

- Atualizar `subtasks_prioritarias` em `tasks.yaml`.
- Sugerir comandos `/projeto-avanca {slug} {deliverable-id}` para os deliverables que o usuário marcou avançar (não rodar automaticamente — sugerir).

### 8. Atualizar snapshot

Sobrescrever `_cache/clickup-snapshot.json` com o estado atual. Bumpar `last_sync` para data corrente.

### 9. Reportar

```markdown
# Sync {slug} concluído ✅

- Snapshot atualizado: {data}
- Tasks no snapshot: {N total}
- tasks.yaml modificado: {sim/não}
- Próxima ação sugerida: {ex: rodar /projeto-avanca para A1}.
```

## Regras

- **Nunca escreve no ClickUp.** Esta skill é puramente leitura no ClickUp + escrita local.
- **Sempre confirmar antes de mudar tasks.yaml.** Use AskUserQuestion.
- **Snapshot deve ser sempre atualizado**, mesmo que tasks.yaml não mude — assim o próximo diff é correto.
- Se a lista tiver > 100 tasks (limite de página da API), paginação será necessária — alertar o usuário e processar em lotes.
- **Mapear deliverable** quando possível: olhar campo `mapeia_para_deliverable` em `subtasks_prioritarias`. Se não houver mapping registrado, listar a task como "fechada (sem mapping)".

## Workflow espelho

`workflows/escritorio-projetos/projeto-tasks-sync.md` (estende `projeto-sync` existente).
