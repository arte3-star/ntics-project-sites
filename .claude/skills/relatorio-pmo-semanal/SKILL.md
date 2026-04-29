---
name: relatorio-pmo-semanal
description: Gera o relatorio semanal PMO de Projetos NTICS lendo ClickUp (pasta Projetos Ativos) com janela semana corrida (segunda a domingo). Mostra o que foi entregue na semana passada e o que esta planejado para a proxima semana, agrupado por coordenador. Resumo executivo via Claude Haiku. Roda automaticamente sexta 16h via scheduled task. Usar quando pedirem o relatorio semanal, balanco da semana, retrospectiva ou planejamento da proxima sprint.
---

# Relatório PMO Semanal

Pipeline complementar ao diário, com foco retrospectivo e prospectivo. Roda automaticamente sexta 16h, mostra o que foi entregue na semana corrente e o que vem na próxima.

## Quando usar

- "Gera o relatório semanal" / "balanço da semana"
- "O que cada um vai entregar na próxima semana?"
- Antes da revisão de sprint sexta 16h
- Para alimentar planning da segunda

## Como chamar

```bash
# Dry-run: gera HTML local e abre no navegador
python tools/reports/run_pmo_weekly.py --mode dry-run

# Draft no Gmail
python tools/reports/run_pmo_weekly.py --mode draft

# Envia para destinatários
python tools/reports/run_pmo_weekly.py --mode send

# Data específica (debug histórico):
python tools/reports/run_pmo_weekly.py --mode dry-run --date 2026-04-25
```

## Janelas

- **Semana passada**: segunda anterior à atual até domingo passado
- **Próxima semana**: próxima segunda até próximo domingo
- Calculado a partir da data de referência (default hoje BRT)

## Estrutura do relatório

1. **Resumo da semana** (Haiku): O que foi entregue / Foco da próxima / Atenção PMO
2. **Visão geral**: Entregues, Próxima semana, Design feito, Design vir
3. **Por coordenador**: cada coord com seus projetos:
   - Tasks entregues na semana (data de fechamento + responsável)
   - Tasks planejadas para próxima semana (due_date + responsável)
4. **Design e vídeo**: Marina, Marcos, Luísa, Alisson com entregas e próximas

## Diferença para o diário

| Aspecto | Diário | Semanal |
|---------|--------|---------|
| Cadência | 8h dias úteis | Sexta 16h |
| Janela | Últimas 24h | Semana corrida (seg-dom) |
| Foco | Operacional, alertas | Retrospectivo + planejamento |
| Saúde por projeto | Sim, com bloqueios | Não (sem semáforo) |
| Comentários inline | Sim, em atrasadas | Não |
| Marcos | Próximos 7 dias | Embutido em "próxima semana" |

## Pipeline interno

```
ClickUp (cutoff 14d) ─▶ aggregate_pmo_weekly.py ─▶ pmo_weekly_metrics.json ─┐
                                                                            ├─▶ render_pmo_weekly.py ─▶ HTML ─▶ Gmail
                                Claude Haiku ─▶ pmo_weekly_summary.json ───┘
```

Scripts em `tools/reports/`:
- `aggregate_pmo_weekly.py` — separa entregue vs próxima por coordenador
- `generate_weekly_summary.py` — Haiku para resumo retrospectivo
- `render_pmo_weekly.py` — Jinja2 + premailer
- `run_pmo_weekly.py` — orquestrador

Reusa `clickup_pull_projetos_ntics.py` com `--cutoff-hours 336` (14 dias).

## Saída

- `output/relatorios/pmo-semanal/YYYY-MM-DD.html` (≈ 100 KB)
- `output/relatorios/pmo-semanal/YYYY-MM-DD.sent.json` (modo send)

## Workflow detalhado

Ver [workflows/escritorio-projetos/relatorio_semanal_pmo.md](../../../workflows/escritorio-projetos/relatorio_semanal_pmo.md).
