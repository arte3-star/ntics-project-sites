---
name: projeto-salvar
description: "Salva nota/decisão/ata no SecondBrain do projeto (execucao.md, decisoes.md, atas/) — não no vault canônico NTICS em AUTOMAÇÕES"
user-invocable: true
---

# /projeto-salvar — Gravar no SecondBrain local do projeto

Diferente de `/salvar` (skill do plugin ntics-brain, que escreve no vault canônico NTICS em `AUTOMAÇÕES/SecondBrain/`), esta skill grava na memória de **execução** de um projeto específico em `SecondBrain/projetos/{slug}/`.

## Quando usar qual

| Skill | Quando usar | Destino |
|---|---|---|
| `/salvar` (plugin) | Decisão estratégica NTICS, conhecimento transversal, ata institucional | `AUTOMAÇÕES/SecondBrain/` |
| `/projeto-salvar` (esta) | Ação/decisão/evidência específica de um projeto em execução | `SecondBrain/projetos/{slug}/` |

## Entrada

- `<slug>` — obrigatório. Ex: `132-samarco` (ou `132-estacao-samarco` — aceita ambos; normaliza).
- `<tipo>` — opcional. Um de: `execucao` (default), `decisao`, `ata`, `evidencia`.
- Conteúdo — o que salvar. Pode ser passado explicitamente pelo usuário ou inferido da conversa recente.

## Passos

1. **Normalizar slug** para o formato canônico do SecondBrain: `132-samarco` → `132-estacao-samarco`. Se já estiver no formato canônico, usar como está.

2. **Identificar conteúdo a salvar:**
   - Se o usuário forneceu texto explícito, usar exatamente.
   - Se o usuário disse só `/projeto-salvar 132-samarco decisao`, pegar a última decisão/conclusão da conversa atual e perguntar: "Salvar isto? [conteúdo]" antes de gravar.

3. **Roteamento por tipo:**

   | tipo | arquivo destino | formato append |
   |---|---|---|
   | `execucao` (default) | `SecondBrain/projetos/{slug}/execucao.md` | `[YYYY-MM-DDTHH:MMZ] [nota] {conteúdo}` |
   | `decisao` | `SecondBrain/projetos/{slug}/decisoes.md` | `[YYYY-MM-DDTHH:MMZ] [MANUAL] {conteúdo}` |
   | `ata` | `SecondBrain/projetos/{slug}/atas/YYYY-MM-DD-{slug-do-titulo}.md` | criar novo arquivo com frontmatter |
   | `evidencia` | `SecondBrain/projetos/{slug}/evidencias/` | o usuário envia link/caminho; criar arquivo apontando para ele |

4. **Gravar** com encoding UTF-8. Confirmar ao usuário: "salvei em `{caminho_relativo}`".

5. **Nunca sobrescrever** — sempre append para execucao.md e decisoes.md. Para atas, se já existe arquivo na data, perguntar antes.

## Regras

- **Formato de data:** ISO 8601 com timezone UTC (`2026-04-23T14:30Z`).
- **Nunca travessão `—`** no texto gravado (regra global NTICS).
- Se o projeto `{slug}` não existir em `SecondBrain/projetos/`, criar a pasta + subpastas `atas/` e `evidencias/` na hora.
- Se o usuário esquecer o tipo, assumir `execucao` (append em execucao.md).
