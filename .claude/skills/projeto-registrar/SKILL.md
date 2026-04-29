---
name: projeto-registrar
description: "Registra artefato finalizado/aprovado no histórico do projeto (documento, e-mail enviado, post publicado, arte aprovada, atualização passada ao cliente). Append em SecondBrain/projetos/{slug}/historico.md — fonte única auditável de tudo que saiu do projeto."
user-invocable: true
---

# /projeto-registrar — Histórico de artefatos do projeto

Catálogo cronológico de **tudo que foi finalizado e saiu** do projeto: documento aprovado, e-mail enviado, post publicado, arte aprovada pelo cliente, atualização repassada à equipe. Não é narrativa (`execucao.md`) nem decisão (`decisoes.md`) — é o **registro de artefato** linkável e auditável.

## Quando registrar

Toda vez que um artefato é dado como **concluído/aprovado/enviado**. O gatilho típico é o usuário aprovar no chat ("ok", "aprovado", "pode mandar", "finalizado", "perfeito, manda", "envia", "fechou"). Ver regra de auto-trigger em `CLAUDE.md` do repo.

Não registrar:
- Rascunhos, versões intermediárias, propostas que ainda vão ser ajustadas
- Coisas que entram em `decisoes.md` (decisão estratégica, não artefato)
- Atas de reunião — vão em `atas/` via `/projeto-salvar ata`

## Entrada

- `<slug>` — obrigatório. Ex: `132-samarco`. Normalizar para canônico (`132-estacao-samarco`) antes de gravar.
- `<tipo>` — obrigatório. Um de:
  - `documento` — TAP, briefing, plano, relatório, ata formal entregue
  - `email` — draft Gmail criado E o usuário deu ok pra enviar (ou já foi enviado)
  - `post` — post Instagram/LinkedIn publicado
  - `arte` — KV, carrossel, card, arte impressa aprovada pelo cliente
  - `video` — vídeo finalizado e entregue
  - `update` — atualização verbal/escrita passada ao cliente, produtor ou equipe (status, aviso, alinhamento)
  - `outro` — qualquer outro artefato que saiu do projeto
- `<referência>` — caminho do arquivo, link Drive/Lovable, draft_id Gmail, thread_id, URL do post, ou descrição curta se não houver link.
- `<descrição>` — 1 linha do que é + para quem foi (cliente, produtor, equipe interna).

Se faltar info, perguntar antes de gravar — nunca inventar.

## Passos

1. **Normalizar slug** para forma canônica do SecondBrain.

2. **Garantir pasta:** se `SecondBrain/projetos/{slug-canonico}/` não existir, criar (já com `atas/` e `evidencias/`).

3. **Append em `historico.md`** no formato:

   ```
   [YYYY-MM-DDTHH:MMZ] [tipo] descrição
     ref: caminho-ou-link
     destinatario: cliente|produtor|equipe-interna|publico
   ```

   Se o arquivo não existir, criar com cabeçalho:
   ```
   # Histórico — {slug}

   Catálogo cronológico de artefatos finalizados/aprovados/enviados do projeto.
   Cada entrada: timestamp UTC, tipo, descrição, referência, destinatário.

   ---
   ```

4. **Reportar ao usuário** em 1 linha:
   ```
   📒 registrado: [tipo] {descrição} → historico.md
   ```

   Não dar relatório longo. O ponto é registrar sem atrito.

## Regras

- **Timestamp ISO UTC sempre** (`2026-04-28T14:30Z`).
- **Append-only.** Nunca editar entrada antiga. Se o usuário quiser corrigir, append nova entrada com `[correcao]` no início da descrição apontando a anterior.
- **Nunca travessão `—`** no texto gravado (regra global NTICS).
- Se o usuário aprovou um artefato mas você não tem a referência (caminho/link/id), **pergunte antes de registrar**. Histórico sem ref serve pra pouco.
- Se houver dúvida se algo é "finalizado" ou ainda rascunho, perguntar: "registrar como finalizado no histórico?"
- Esta skill é chamada **automaticamente** pelas skills `projeto-email` (após draft criado e usuário ok), `projeto-avanca` (após deliverable concluído) e por instrução de auto-trigger no `CLAUDE.md`. Não duplicar registro: se `projeto-avanca` já registrou, não registrar de novo no mesmo turno.
