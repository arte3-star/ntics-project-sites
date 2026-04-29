# Nome do Workflow

> TL;DR em uma linha: o que faz, para quem, qual entrega.

---

## Quando usar

Uma ou duas linhas. Condição de entrada. Quando NÃO usar (se houver confusão comum com workflow vizinho).

---

## Inputs

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| `campo_a` | string | Sim | Explicação curta |
| `campo_b` | string | Não | Default documentado |

---

## APIs e chaves

| API | Uso | Variável de ambiente |
|-----|-----|----------------------|
| ... | ... | `API_KEY` |

Se não usa API externa, omitir a seção.

---

## Tool(s)

```bash
python tools/<area>/<script>.py --<flag> <valor>
```

Flags úteis, flags de dry-run, flags de reuso de cache (se houver). Uma linha por flag.

---

## Execução

### Fase 1: Nome da fase (auto)

Descrição curta do que a fase faz. Sub-passos em bullets ou blocos de código quando necessário.

### Fase 2: Nome da fase (auto, bloqueante)

`(auto, bloqueante)` = automação não avança se a checagem falhar, mas não pede aprovação humana.

### Fase 3: Nome da fase (gate humano)

`(gate humano)` = precisa de validação explícita do Lucas antes de prosseguir.

Numeração sempre começa em 1, crescente, sem ramos `1.5` ou `0`. Se aparecer patch no meio, renumerar o arquivo inteiro.

---

## Output esperado

Lista curta e concreta:
- `output/<area>/<slug>/arquivo1.ext`
- Campo X atualizado em Y
- Task criada em lista `<id>`

---

## Checklist de qualidade

- [ ] Item 1
- [ ] Item 2
- [ ] Item 3

Cada item deve ser verificável sem julgamento subjetivo.

---

## Dependências

**Upstream (precisa rodar antes):**
- `outro_workflow.md` quando ...

**Downstream (roda depois):**
- `outro_workflow.md` consome o output
- Skill `/comando` continua o pipeline
