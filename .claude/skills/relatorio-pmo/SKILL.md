---
name: relatorio-pmo
description: Gera o relatorio diario PMO de Projetos NTICS lendo ClickUp (pasta Projetos Ativos + Sprint da semana), agregando saude por coordenador, atrasos, mudancas 24h, marcos, bloqueios, decisoes pendentes e tasks de design/video. Resumo executivo via Claude Haiku. Entrega HTML por email para Lucas/Bruna/Abilio. Usar quando o usuario pedir o relatorio diario, status PMO, dashboard de projetos, ou quiser rodar sob demanda fora do agendamento das 8h.
---

# Relatório Diário PMO

Pipeline automatizado que lê ClickUp e entrega um relatório executivo da área de Projetos por email (HTML). Roda automaticamente 8h em dias úteis. Pode ser chamado manualmente.

## Quando usar

- "Gera o relatório diário PMO" / "manda o relatório de hoje"
- "Como tá a área de Projetos hoje?" / "status do PMO"
- Antes de uma reunião com diretoria, para ter snapshot atual
- Para revisar e aprovar o template antes de enviar

## Como chamar

```bash
# Dry-run: gera HTML local e abre no navegador (não envia email)
python tools/reports/run_pmo_daily.py --mode dry-run

# Draft: cria rascunho no Gmail (não envia)
python tools/reports/run_pmo_daily.py --mode draft

# Send: envia email para destinatários do YAML
python tools/reports/run_pmo_daily.py --mode send

# Forçar execução em fim de semana / feriado:
python tools/reports/run_pmo_daily.py --mode dry-run --skip-business-day-check

# Data específica (debug histórico):
python tools/reports/run_pmo_daily.py --mode dry-run --date 2026-04-25
```

## Configuração

`tools/reports/config/pmo_diario.yaml` controla:
- Folder ClickUp (Projetos Ativos `90115187061`, Sprint `90115190074`)
- Listas excluídas (triagem `901113425673`, gestão `901108780010`)
- Destinatários do email
- Lista de designers/video makers (Luísa, Marina, Alisson, Marcos)
- Status considerados "concluído"
- Detecção de bloqueios e decisões pendentes
- Modelo IA para resumo executivo (default: Haiku)

## Estrutura do relatório

1. **Resumo executivo (Haiku)**: 3 cartões (O que foi bom / O que preocupa / Decidir hoje)
2. **KPIs gerais**: Projetos, tasks abertas, atrasadas, bloqueios, % aderência sprint
3. **Aderência da Sprint**: tabela por dia da semana (previstas, no prazo, atrasadas, pendentes)
4. **Por coordenador**: cada PM com seus projetos, saúde agregada e tabela detalhada
5. **Design e vídeo**: tasks por designer/videomaker com atrasadas + próximos 7 dias
6. **Mudanças últimas 24h**: agrupadas por projeto (criadas, fechadas, alteradas)
7. **Marcos próximos 7 dias**: tasks de Kick-off/Fechamento/entrega/aprovação
8. **Decisões e bloqueios**: tasks com tag/status indicando travamento ou aguardando decisão

## Pipeline interno

```
ClickUp pasta Projetos Ativos  ─┐
                                ├─▶ aggregate_pmo_metrics.py ─▶ pmo_metrics.json ─┐
ClickUp pasta Sprint (semana)  ─┘                                                  │
                                                                                   ├─▶ render_pmo_html.py ─▶ HTML ─▶ Gmail
                                                Claude Haiku ─▶ pmo_summary.json ─┘
```

Scripts (`tools/`):
- `integrations/clickup_pull_projetos_ntics.py` — pull do folder `90115187061`
- `integrations/clickup_pull_sprint.py` — identifica sprint ativa por data e puxa
- `reports/aggregate_pmo_metrics.py` — saúde, atrasos, bloqueios, agrupamento
- `reports/generate_pmo_summary.py` — resumo executivo (Haiku, fallback determinístico)
- `reports/render_pmo_html.py` — Jinja2 + premailer + auto-review bloqueante
- `reports/send_pmo_email.py` — Gmail API + verificação de SENT
- `reports/run_pmo_daily.py` — orquestrador end-to-end

## Saída

- `output/relatorios/pmo-diario/YYYY-MM-DD.html` — relatório renderizado
- `output/relatorios/pmo-diario/YYYY-MM-DD.sent.json` — log do envio (modo send)
- `.tmp/pmo_*.json` — artefatos intermediários

## Workflow detalhado

Ver [workflows/escritorio-projetos/relatorio_diario_pmo.md](../../../workflows/escritorio-projetos/relatorio_diario_pmo.md).
