# Workflow — Projeto: abrir (bootstrap)

> **Skill associada:** `/projeto-abrir <codigo> <slug-curto>` — ver [.claude/skills/projeto-abrir/SKILL.md](../../.claude/skills/projeto-abrir/SKILL.md).

## Quando usar

Sempre que um novo projeto NTICS for confirmado (apresentação vendida + ClickUp list criada + pasta Drive criada pela GP). Esta é a primeira coisa a fazer antes de qualquer briefing ou produção.

## Inputs obrigatórios

- Código NTICS (ex: 128).
- Slug curto descritivo (ex: `cnh-festival-agricultura`).

## Inputs opcionais (mas recomendados — quanto mais, melhor o bootstrap)

- ID Drive da apresentação vendida.
- ID da pasta raiz Drive do projeto.
- ID da lista ClickUp.
- ID da task legacy pré-lista (se houver).
- ID Drive do KV oficial.
- ID Drive da pasta de logos/manual do patrocinador.

## Saída

Em `SecondBrain/projetos/{codigo}-{slug-curto}/`:

| Arquivo | Conteúdo |
|---------|----------|
| `README.md` | Landing do projeto, links rápidos |
| `CLAUDE.md` | Contexto carregado em toda sessão |
| `state.yaml` | Fase, deliverables A/B/C/D, blockers, próxima ação |
| `tasks.yaml` | list_id, task_mae, subtasks priorizadas, drive folders |
| `stakeholders.yaml` | Equipe NTICS + patrocinador |
| `budget.yaml` | Frentes de custo |
| `PLAYBOOK.md` | Constituição narrativa (14 seções) |
| `tap.md` | TAP rascunho com pontos abertos |
| `calendar.md` | Sugestões de marcos |
| `execucao.md` | Log do dia-a-dia (primeira entrada = bootstrap) |
| `decisoes.md` | Decisões consolidadas (primeira entrada = abertura) |
| `brand/README.md` | Aplicação da sub-marca neste projeto |
| `brand/kv/README.md` | KV oficial + a derivar |
| `atas/README.md` | Convenção de atas |
| `assets/INDEX.md` | Estrutura do acervo |
| `brief/apresentacao-extraida.md` | Texto extraído da apresentação vendida |
| `brief/drive-map.md` | Mapa da pasta Drive (nível 1-2) |
| `_cache/clickup-snapshot.json` | Snapshot da lista ClickUp |

Além disso:
- Atualiza `SecondBrain/projetos/INDEX.md` com linha do projeto novo.
- Atualiza ou cria `SecondBrain/clientes/{slug-cliente}.md`.
- Adiciona entrada em `MEMORY.md` apontando para `projeto_{codigo}_{slug-curto}.md`.
- Se já existir `SecondBrain/clientes/brand-aplicacao-{cliente}.md`, referencia em `brand/README.md`; senão, sugere criar.

## Princípios

1. **Read-only** no Drive e ClickUp. A skill nunca cria ou edita externamente.
2. **Não duplica** conteúdo. `brand-aplicacao` fica a nível de cliente quando aplicável.
3. **Pré-popula** o máximo possível a partir da apresentação vendida — deliverables, oficinas, cidades, ODS, plataformas mencionadas, etc.
4. **Marca tudo o que está pendente** explicitamente em state.yaml (`status: pendente`, blockers com `revisar_em`) e tap.md (lista "pontos em aberto").
5. **Sugere primeira ação concreta** ao final (`/projeto-status` + `/projeto-briefing A1`).

## Quando NÃO usar

- Para projetos já abertos (use `/projeto-status` ou `/projeto-tasks-sync`).
- Para entender escopo de projeto existente (use `/projeto-status`).

## Casos piloto

- **128. Festival Agricultura Sustentável (CNH/New Holland)** — aberto manualmente nesta sessão (2026-05-16) seguindo o passo-a-passo que virou esta skill.
- **129. Agrofuturo Cultural nas Escolas (CNH/Case IH)** — idem.

## Padrão de execução

Ver [.claude/skills/projeto-abrir/SKILL.md](../../.claude/skills/projeto-abrir/SKILL.md).
