# Workflow — Projeto: retrospectiva por tarefa

> **Skill associada:** `/projeto-retrospectiva <slug> <deliverable-id>` — ver [.claude/skills/projeto-retrospectiva/SKILL.md](../../.claude/skills/projeto-retrospectiva/SKILL.md).

## Quando usar

**Imediatamente após `/projeto-avanca`** para um deliverable concluído. Esta skill fecha o ciclo de auto-melhoria: cada tarefa vira aprendizado capturado.

## Inputs

- `<slug>` — projeto.
- `<deliverable-id>` — deliverable concluído.

## As 4 perguntas (script)

1. **(a) Algo na execução te incomodou?**
2. **(b) Algo que valeu a pena anotar pra próxima vez?**
3. **(c) Essa execução merece virar skill própria / workflow novo?**
4. **(d) Ajustar alguma skill existente?**

Mantenha curtas. Se o user quiser detalhar, segue follow-up única.

## Saída

- Append em `SecondBrain/projetos/{slug}/execucao.md` com bloco datado.
- Se (c) = sim: stub em `workflows/escritorio-projetos/_propostas/{nome}.md`.
- Se (d) = sim: append/criação em `memory/feedback_{skill}.md` + entrada em `MEMORY.md` se novo.
- Sugestão proativa quando o **detector rule-of-3** detectar padrão repetido em 3 retrospectivas.

## Detector rule-of-3

Antes de gravar, busca em `execucao.md` por entradas `## YYYY-MM-DD — Retrospectiva` recentes. Se o tema da resposta atual aparecer em 2 entradas anteriores, sugere virar skill nova.

Heurística para "tema":
- Substantivos-chave em (b) e (c).
- Skill mencionada em (d) — se a mesma skill aparecer 3x sendo "ajustar", proponha refactor dessa skill.

## Princípios

1. **Nunca pula a captura.** Mesmo respostas "tudo OK" geram uma entrada curta — assim mantemos auditável que toda tarefa passou por retrospectiva.
2. **Não muda state.yaml.** A skill é puramente de captura. Mudança de estado é responsabilidade de `/projeto-avanca`.
3. **Aprendizado é cumulativo.** Quanto mais retrospectivas, mais o sistema acerta no rule-of-3.

## Integração com outras skills

- **Vem DEPOIS de `/projeto-avanca`** sempre.
- **Pode chamar `/skill-creator`** indiretamente (sugestão ao user) quando rule-of-3 disparar.
- **Alimenta `/dream`** indiretamente — o `/dream` lê o memory/feedback_*.md e consolida.

## Casos piloto

Quando o primeiro deliverable real dos projetos 128 ou 129 for entregue, esta skill será exercitada. Os aprendizados das primeiras 3 execuções vão definir se ela precisa de ajuste.
