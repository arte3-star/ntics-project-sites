---
name: projeto-abrir
description: "Bootstrap completo de um projeto NTICS novo dentro do SecondBrain a partir de inputs externos (apresentação vendida no Drive, pasta Drive do projeto, lista ClickUp, KV e logos do patrocinador). Cria toda a estrutura canônica (state.yaml, PLAYBOOK.md, tasks.yaml, brand/, brief/, content/, atas/...) e atualiza INDEX + MEMORY."
user-invocable: true
---

# /projeto-abrir — Bootstrap automatizado de projeto novo

Quando o usuário invocar `/projeto-abrir <codigo> <slug-curto>`, faça o bootstrap completo do projeto no SecondBrain NTICS espelhando o padrão de [SecondBrain/projetos/132-estacao-samarco/](../../../SecondBrain/projetos/132-estacao-samarco/) (ou [128-cnh-festival-agricultura/](../../../SecondBrain/projetos/128-cnh-festival-agricultura/) como referência mais enxuta).

## Entrada

- `<codigo>` — código NTICS do projeto. Ex: `128`, `134`.
- `<slug-curto>` — nome curto descritivo. Ex: `cnh-festival-agricultura`, `samarco-estacao`. Sem prefixo numérico (a skill adiciona).
- O slug final canônico será `{codigo}-{slug-curto}`.

## Passos

### 1. Perguntar interativamente (use AskUserQuestion)

Para cada item abaixo, peça ao usuário. Aceite "não tenho ainda" como resposta válida (segue sem aquele input).

- `apresentacao_drive_file_id` — ID Drive do PDF/Slides com a apresentação vendida ou TAP rascunho.
- `pasta_drive_id` — ID da pasta raiz do projeto no Drive.
- `clickup_list_id` — ID da lista no ClickUp ("Escritório de Projetos").
- `clickup_legacy_task_id` — ID da task legacy pré-lista (opcional).
- `kv_drive_file_id` — ID do KV oficial no Drive (opcional, pode chegar depois).
- `logos_patrocinador_drive_folder_id` — pasta com manuais/logos do patrocinador (opcional).
- `patrocinador_nome` — nome curto do patrocinador (e sub-marca, se houver).
- `lei` — Rouanet, ProAC, direto, etc.
- `gp_ntics` — nome do GP responsável.

### 2. Carregar MCPs sob demanda via ToolSearch

```
ToolSearch query="select:mcp__adf0e2d7-e075-41de-884b-58c6642b02d8__read_file_content,mcp__adf0e2d7-e075-41de-884b-58c6642b02d8__get_file_metadata,mcp__adf0e2d7-e075-41de-884b-58c6642b02d8__search_files,mcp__5cef576d-bc98-4847-9b33-9ca9928ad708__clickup_get_list,mcp__5cef576d-bc98-4847-9b33-9ca9928ad708__clickup_filter_tasks,mcp__5cef576d-bc98-4847-9b33-9ca9928ad708__clickup_get_task"
```

### 3. Ingerir inputs externos

- **Apresentação vendida** → ler texto via `read_file_content`. Salvar em `brief/apresentacao-extraida.md`.
- **Pasta Drive** → listar subpastas nível 1 via `search_files` `parentId = '{id}'`. Salvar mapa em `brief/drive-map.md`.
- **ClickUp list** → puxar tasks via `clickup_filter_tasks(list_ids=[id], subtasks=true, include_closed=true)`. Salvar JSON enxuto em `_cache/clickup-snapshot.json` e selecionar 10-25 tasks prioritárias para `tasks.yaml`.
- **ClickUp legacy task** → puxar via `clickup_get_task(task_id, detail_level='summary')` se ID fornecido. Salvar `brief/clickup-legacy-task.md`.
- **KV/Logos** → registrar metadata em `brand/kv/README.md` e `assets/LOGOS/PATROCINADOR/README.md`.

### 4. Criar estrutura de pastas

Espelhando 132-samarco e 128-cnh-festival-agricultura, criar dentro de `SecondBrain/projetos/{slug-canonico}/`:

**Subpastas:**
- `assets/{LOGOS/PROJETO, LOGOS/PATROCINADOR, FOTOS, REGUAS, ELEMENTOS, DOCUMENTOS, COMUNICACAO_VISUAL}/`
- `brief/`, `brand/{kv, logo, paleta, fontes, elementos}/`, `comms/`, `content/`, `atas/`, `_cache/`, `evidencias/`, `operacional/`, `site/`

### 5. Criar arquivos seed

**Arquivos raiz:**
- `README.md` — visão geral + links Drive/ClickUp.
- `CLAUDE.md` — contexto operacional resumido.
- `state.yaml` — fase: `kickoff-pendente`, deliverables A/B/C/D extraídos da apresentação, blockers conhecidos.
- `tasks.yaml` — list_id, task_mae, subtasks_prioritarias, drive_folder_oficial, gmail_query.
- `stakeholders.yaml` — equipe NTICS padrão + placeholders patrocinador.
- `budget.yaml` — frentes de custo extraídas da apresentação.
- `PLAYBOOK.md` — esqueleto 14 seções, seções 1-6 pré-preenchidas a partir da apresentação.
- `tap.md` — TAP rascunho com pontos abertos listados.
- `calendar.md` — sugestões de marcos.
- `execucao.md` — primeira entrada datada de hoje com o que foi feito no bootstrap.
- `decisoes.md` — primeira entrada com a decisão de abertura.
- `brand/README.md` — aplicação específica da sub-marca; ou linkar `brand-aplicacao-{cliente}.md` se já existir em `SecondBrain/clientes/`.

**READMEs leves:**
- `brand/kv/README.md`, `atas/README.md`, `assets/INDEX.md`.

### 6. Atualizar índices e memória

- Adicionar linha em [SecondBrain/projetos/INDEX.md](../../../SecondBrain/projetos/INDEX.md).
- Atualizar perfil do cliente em `SecondBrain/clientes/{slug-cliente}.md` (criar se não existe).
- Adicionar entrada em `MEMORY.md` apontando para um novo `projeto_{codigo}_{slug-curto}.md` no diretório de memory.

### 7. Reportar

Ao final, apresente:

```markdown
# Projeto {codigo}-{slug-curto} aberto ✅

**Patrocinador:** ... · **Lei:** ... · **GP:** ...

## Inputs ingeridos
- ✅ Apresentação vendida: brief/apresentacao-extraida.md
- ✅ Pasta Drive: brief/drive-map.md (X subpastas)
- ✅ ClickUp list: tasks.yaml + _cache/clickup-snapshot.json (N tasks)
- ⏳ KV oficial: ... (se faltou)

## Arquivos criados
{lista}

## Próximas ações sugeridas
1. /projeto-status {slug-canonico} — conferir tudo coerente.
2. /projeto-briefing {slug-canonico} A1 — começar primeiro deliverable (provavelmente KV).
```

## Regras

- **Read-only no Drive e ClickUp.** Esta skill nunca cria ou edita tasks no ClickUp, nem arquivos no Drive. Só lê.
- **Não duplicar conteúdo.** Se já existe `SecondBrain/clientes/brand-aplicacao-{cliente}.md`, referenciar via `brand/README.md` em vez de duplicar.
- **Datas atuais.** Use `date` ou a data corrente nas entradas de execucao.md, decisoes.md, `atualizado:` em state.yaml.
- **Sem travessão `—`** em qualquer arquivo gerado.
- **TodoWrite obrigatório** para tasks de mais de 3 passos.
- **Confirmar antes de sobrescrever.** Se a pasta `SecondBrain/projetos/{slug-canonico}/` já existe, pergunte se deve sobrescrever, mesclar ou abortar.

## Workflow espelho

`workflows/escritorio-projetos/projeto-abrir.md` — documentação completa do SOP.
