---
name: projeto-retrospectiva
description: "Captura de aprendizado por tarefa. Roda DEPOIS de /projeto-avanca para um deliverable concluído. Faz 4 perguntas curtas (incomodou? valeu anotar? vira skill? ajustar skill existente?), grava o aprendizado em execucao.md, e — quando aplicável — gera stub de skill nova em workflows/escritorio-projetos/_propostas/ ou append em memory/feedback_{skill}.md. Inclui detector rule-of-3: se um padrão similar aparece em 3 retrospectivas, sugere proativamente virar skill."
user-invocable: true
---

# /projeto-retrospectiva — Captura de aprendizado por tarefa

Quando o usuário invocar `/projeto-retrospectiva <slug> <deliverable-id>`, faça uma retrospectiva curta da execução do deliverable e capture o aprendizado para alimentar o ciclo de auto-melhoria.

## Entrada

- `<slug>` — pasta em `SecondBrain/projetos/`. Ex: `128-cnh-festival-agricultura`.
- `<deliverable-id>` — id do deliverable concluído. Ex: `A1`, `B2`, `VIDEO-PRE`.
- **Pré-requisito:** `/projeto-avanca {slug} {deliverable-id}` já rodou (status `concluido` em state.yaml).

## Passos

### 1. Carregar contexto

- `SecondBrain/projetos/{slug}/state.yaml` — confirmar deliverable existe e está `concluido`. Se não, alertar usuário e parar.
- `SecondBrain/projetos/{slug}/execucao.md` — ler últimas 5-10 entradas para detectar repetições (rule-of-3).
- `SecondBrain/projetos/{slug}/historico.md` (se existir) — entrada do `/projeto-registrar`.

### 2. Fazer as 4 perguntas

Use AskUserQuestion (4 perguntas em UMA chamada — `multiSelect: false` em cada):

1. **Algo na execução te incomodou?** Opções: "Sim, principal: ..." / "Tudo correu bem" / "Pequenos atritos, não vale anotar". Se "Sim", coletar texto livre depois.

2. **Algo que valeu a pena anotar pra próxima vez?** Opções: "Sim, aprendizado novo" / "Confirmação de algo já sabido" / "Não".

3. **Essa execução merece virar skill própria / workflow novo?** Opções: "Sim, padrão novo claro" / "Talvez, observar próximas vezes" / "Não, é caso isolado".

4. **Ajustar alguma skill existente?** Opções: "Sim, skill: ..." / "Não".

Se a opção "Outro" for usada, o usuário pode descrever em texto livre.

### 3. Detectar rule-of-3

Antes de gravar a entrada, faça uma busca rápida em `execucao.md` (e opcionalmente `decisoes.md`) por padrões similares ao aprendizado capturado. Heurística simples:

- Se a resposta de (b) ou (c) menciona um tema que aparece em 2 entradas anteriores de retrospectiva (procurar pelo padrão `## YYYY-MM-DD` seguido de `### Retrospectiva`), gere uma sugestão proativa no final:
  > **🔔 Rule of 3 detectado:** o padrão "X" apareceu em 3 retrospectivas. Considere promover para skill via `/skill-creator`.

### 4. Gravar entrada em execucao.md

Append em `SecondBrain/projetos/{slug}/execucao.md`:

```markdown
## YYYY-MM-DD — Retrospectiva {deliverable-id}: {nome curto}

- **Artefato:** {link/path do output}
- **ClickUp:** {id da task se aplicável}

### Retrospectiva
- **(a) O que incomodou:** {resposta 1}
- **(b) O que valeu anotar pra próxima:** {resposta 2}
- **(c) Vira skill nova?** {sim/não} — {detalhe}
- **(d) Ajustar skill existente?** {sim/não} — {qual skill, qual ajuste}
{🔔 sugestão rule-of-3 se aplicável}
```

### 5. Se (c) for "Sim, padrão novo claro"

Criar stub em `workflows/escritorio-projetos/_propostas/{nome-sugerido}.md`:

```markdown
# Proposta de skill: {nome}

**Origem:** retrospectiva de {slug} / {deliverable-id} em {data}.

**Problema observado:** {resposta b/c}

**Proposta de skill:** {nome sugerido começando com /}

**Inputs:** ...
**Outputs:** ...
**Workflow base:** ...

**Próximo passo:** rodar `/skill-creator` para promover este stub a skill formal.
```

### 6. Se (d) for "Sim, skill: ..."

Append/atualizar `C:\Users\lucas\.claude\projects\G--O-meu-disco-Claude-NTICS-Projetos\memory\feedback_{nome_da_skill}.md` (criar se não existe) com frontmatter `type: feedback` e regra clara + Why + How to apply.

Adicionar linha em `MEMORY.md` se for memory novo.

### 7. Reportar

Resumo curto:

```markdown
# Retrospectiva registrada ✅

- Entrada em execucao.md: linha {N}.
- Skill nova proposta: {sim/não}.
- Feedback de skill existente: {sim/não — qual}.
- Rule-of-3 detectado: {sim/não}.

Próximo deliverable sugerido: {ler state.yaml e sugerir o próximo `status: pendente` sem blocker}.
```

## Regras

- **Mantenha as 4 perguntas curtas.** Cada uma deve caber em uma linha. Não faça mais perguntas — se quiser detalhe, peça uma única follow-up por pergunta.
- **Nunca pule a captura.** Mesmo se todas as respostas forem "não/tudo bem", grave a entrada (curta) em execucao.md — assim mantemos o cadastro de "passou pela retrospectiva".
- **Sem travessão `—`** nas entradas.
- **Não mexa em state.yaml** — esta skill é puramente de captura, não de mudança de estado.

## Workflow espelho

`workflows/escritorio-projetos/projeto-retrospectiva.md`.
