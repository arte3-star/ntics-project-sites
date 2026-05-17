# Workflow — Projeto: tasks-sync (espelhamento ClickUp ↔ tasks.yaml)

> **Skill associada:** `/projeto-tasks-sync <slug>` — ver [.claude/skills/projeto-tasks-sync/SKILL.md](../../.claude/skills/projeto-tasks-sync/SKILL.md).

## Quando usar

- Periodicamente (semanal ou após reunião com cliente) para refletir mudanças do ClickUp no SecondBrain.
- Antes de `/projeto-status` se quiser que o relatório use estado fresco.
- Sempre que o GP comentar que mexeu nas tasks no ClickUp.

## Relação com `/projeto-sync` existente

`/projeto-sync` (skill já existente) faz sync rápido sem diff explícito. `/projeto-tasks-sync` é a **versão informativa**: mostra ao user 3 grupos de mudanças e pede confirmação antes de aplicar no `tasks.yaml`.

Use `/projeto-sync` para sync mecânico (cron, abertura de sessão); use `/projeto-tasks-sync` quando quiser revisar mudanças antes.

## Diff em 4 categorias

1. **Tasks novas** (ClickUp tem, tasks.yaml não) → propõe importar para `subtasks_prioritarias`.
2. **Tasks fechadas** (status closed/complete agora, antes pendentes) → propõe avançar deliverables que mapeiam para essas tasks.
3. **Status alterados** (em ambos, status diferente) → reporta + opção de aplicar.
4. **Tasks sumidas** (estavam, agora não) → reporta + opção de remover de subtasks_prioritarias.

## Saída

- `tasks.yaml` atualizado (apenas com confirmação do user).
- `_cache/clickup-snapshot.json` sempre atualizado (mesmo sem confirmação para tasks.yaml).
- Sugestões de comandos `/projeto-avanca` para deliverables que podem ser concluídos.

## Princípios

1. **Read-only no ClickUp.** Nunca escreve lá.
2. **Confirmação obrigatória** antes de mudar tasks.yaml.
3. **Snapshot sempre atualizado** — caso contrário, próximo diff fica corrompido.
4. **Mapping `task_id → deliverable_id`** vive em `tasks.yaml.subtasks_prioritarias[*].mapeia_para_deliverable`. Manter atualizado para o diff entregar valor.

## Paginação

ClickUp API limita ~100 tasks por página. Se a lista exceder, paginar com `page` parameter no `clickup_filter_tasks` e processar em lotes.

## Casos piloto

- **128 e 129** — listas tem ~100 tasks. Primeiro `/projeto-tasks-sync` rodará sem diff (snapshot inicial igual ao atual). A partir do segundo, começa a entregar valor.
