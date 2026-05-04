---
name: status
description: Reporta o status executivo do projeto ativo. Lê state.yaml e stakeholders.yaml e gera um resumo: fase atual, próxima ação, deliverables pendentes, blockers e o que precisa de decisão hoje.
---

# /status

Leia os arquivos de contexto do projeto e reporte o status executivo.

## O que ler
1. `state.yaml` — fase, deliverables, blockers, próxima ação
2. `stakeholders.yaml` — quem precisa saber de alguma coisa
3. `memory/sobre-o-projeto.md` — contexto geral

## Formato do relatório

```
PROJETO: [nome]
FASE: [fase atual]

PRÓXIMA AÇÃO:
- [O que] até [quando] — responsável: [quem]

DELIVERABLES EM ANDAMENTO:
- [nome] | prazo: [data] | status: [status]
- [nome] | prazo: [data] | status: [status]

BLOCKERS:
- [descrição] → responsável: [quem] até [quando]
(ou "Nenhum blocker no momento")

DECISÕES PENDENTES:
- [O que precisa de decisão] — quem decide: [nome]
(ou "Nenhuma decisão pendente")

PRÓXIMO MARCO:
[O próximo evento ou entrega importante e quando]
```

## Regras
- Seja objetivo. Máximo 15 linhas.
- Se não houver blockers ou decisões, diga explicitamente "Nenhum".
- Se state.yaml não existir, peça para o usuário criar usando o template.
