---
name: projeto-avanca
description: "Marca deliverable como concluído: atualiza state.yaml, comenta evidência na task ClickUp correspondente, identifica próximo deliverable, salva decisão no SecondBrain"
user-invocable: true
---

# /projeto-avanca — Fechar deliverable e avançar estado

Quando o usuário invocar `/projeto-avanca <slug> <deliverable-id>`, encerre o deliverable e avance o estado do projeto.

## Entrada

- `<slug>` — ex: `132-samarco`
- `<deliverable-id>` — id do deliverable a marcar concluído (ex: `A1`, `B2`, `VIDEO-PRE-MG`)

## Passos

1. **Validar:**
   - Ler `projects/{slug}/state.yaml` e localizar o deliverable.
   - Se `status` já for `concluido`, perguntar: "já estava concluído, atualizar mesmo assim?"
   - Se `output` estiver vazio, pedir ao usuário o caminho do arquivo/link final antes de continuar.

2. **Atualizar `state.yaml`:**
   - `status: concluido`
   - `output: <caminho ou link>`
   - `concluido_em: <data ISO>`
   - Recalcular `proxima_acao`: primeiro deliverable com status `pendente` e sem dependência bloqueada, ordenado por prioridade.

3. **Comentar no ClickUp:**
   - Ler `projects/{slug}/tasks.yaml` e localizar a subtask correspondente ao deliverable.
   - Se a subtask ainda não existir (ids vazios em `subtasks_design_a_criar`), sugerir ao usuário criar antes — não criar automaticamente sem autorização.
   - Usar `mcp__claude_ai_ClickUp__clickup_create_task_comment` com:
     ```
     ✅ {deliverable.nome} — concluído em {data}
     Output: {caminho ou link}
     Próxima ação do projeto: {proxima_acao atualizada}
     ```
   - Após comentar, verificar com `clickup_get_task_comments` que o comentário existe.

4. **Salvar no SecondBrain LOCAL (projects-os/SecondBrain/):**
   - Caminho: `SecondBrain/projetos/{slug-canonico}/execucao.md` (append no final).
     - Normalizar slug: `132-samarco` → `132-estacao-samarco`.
   - Formato: `[{timestamp ISO UTC}] [deliverable_concluido] {deliverable.id} {deliverable.nome} concluído. Output: {link}`.
   - Para decisões formais detectadas no processo, também append em `decisoes.md` com tag `[MANUAL]`.
   - Não escrever em `AUTOMAÇÕES/SecondBrain/` — aquele vault é canônico e recebe só atas institucionais e contexto estratégico, não log operacional.

5. **Reportar ao usuário:**
   ```
   ✅ {deliverable.id} — concluído
   📋 ClickUp: comentário em {subtask.id}
   🧠 SecondBrain: entrada em execucao.md
   ➡️ Próxima ação: {nova proxima_acao}
   ```

## Regras

- **Nunca deletar tasks ClickUp** — só comentar/mover (`feedback_clickup_tasks.md`).
- **Nunca sobrescrever output** sem confirmação do usuário se já houver algo.
- Se qualquer um dos 4 passos (state.yaml, ClickUp, SecondBrain, reporte) falhar, **interromper e relatar o que passou + o que falhou**. Não declarar sucesso parcial.
- Após avançar, se o projeto entrou em nova fase (ex: último deliverable pré concluído → próxima fase é "em execução"), atualizar `state.fase` e pedir confirmação.
