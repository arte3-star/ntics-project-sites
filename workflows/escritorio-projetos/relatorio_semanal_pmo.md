# Relatório Semanal PMO de Projetos

> Pipeline retrospectivo + prospectivo. Lê ClickUp com janela de 14 dias, agrega o que foi entregue na semana passada e o que está planejado para a próxima, agrupado por coordenador. Roda sexta 16h.

---

## Quando usar

- **Automático**: roda sexta 16h via scheduled task `relatorio-pmo-semanal`
- **Manual**: para retrospectiva fora do horário, alimentar planning de segunda, ou validar formato após mudança no template
- **NÃO usar** para snapshot diário operacional (esse é o relatório diário, com saúde, alertas e bloqueios)

---

## Inputs

| Campo | Tipo | Default | Descrição |
|-------|------|---------|-----------|
| `--mode` | enum | `dry-run` | `dry-run`, `draft`, `send` |
| `--date` | YYYY-MM-DD | hoje BRT | Data referência. Janelas seg-dom calculadas a partir dela |
| `--no-llm` | flag | off | Pula Haiku, usa template determinístico |
| `--limit N` | int | nenhum | Limita N listas (debug) |

---

## Janelas

- **Semana passada**: segunda da semana corrente − 7 dias até domingo − 1 dia
- **Próxima semana**: próxima segunda até próximo domingo
- Quando rodado na sexta 26/04: passada = 13–19/04, próxima = 27/04–03/05

---

## Tool

```bash
python tools/reports/run_pmo_weekly.py --mode draft     # cria rascunho Gmail
python tools/reports/run_pmo_weekly.py --mode send      # envia para destinatários
python tools/reports/run_pmo_weekly.py --mode dry-run   # HTML local
```

Reusa configuração de `tools/reports/config/pmo_diario.yaml`:
- `recipients` — destinatários
- `coordinator_overrides` — mapa list_id → coordenador real
- `team.designers / video_makers` — separa equipe criativa
- `status_done` — status considerados concluídos
- `ai` — modelo Haiku para resumo

---

## Execução

### Fase 1: Pull projetos com janela 14 dias (auto)

`tools/integrations/clickup_pull_projetos_ntics.py --cutoff-hours 336`. Inclui tasks abertas + fechadas nos últimos 14 dias (cobre semana passada inteira). Output: `.tmp/pmo_raw_tasks.json`.

### Fase 2: Agregar métricas semanais (auto)

`tools/reports/aggregate_pmo_weekly.py`:
- Para cada task com `date_done` na janela passada: marca como entregue
- Para cada task aberta com `due_date` na janela próxima: marca como planejada
- Agrupa por coordenador (com overrides)
- Separa equipe criativa (designers + video makers)

Output: `.tmp/pmo_weekly_metrics.json`.

### Fase 3: Resumo executivo Haiku (auto)

`tools/reports/generate_weekly_summary.py` chama Claude Haiku 4.5. Devolve JSON com `bom`/`foco`/`recomendacao`. Em falha, fallback determinístico.

### Fase 4: Render HTML + auto-review (auto, bloqueante)

`tools/reports/render_pmo_weekly.py` aplica Jinja2 + premailer. Auto-review valida 6 seções, sem em-dash, sem placeholder não resolvido, HTML > 3 KB.

Output: `output/relatorios/pmo-semanal/YYYY-MM-DD.html`.

### Fase 5: Envio Gmail (auto)

`tools/reports/send_pmo_email.py --subject-kind weekly` envia com subject `PMO Semanal - DD/MM - N entregues / M próxima`.

---

## Estrutura do email

1. **Header** — Data + janelas (passada e próxima)
2. **Resumo da semana** — 3 cards (Entregue / Foco / Atenção PMO)
3. **Visão geral** — KPIs (entregues, próxima, design feito, design vir)
4. **Por coordenador** — Cada PM com seus projetos:
   - Pill verde "Entregue" + lista das tasks fechadas na semana passada
   - Pill azul "Próxima semana" + lista das planejadas
5. **Design e vídeo** — Marina, Marcos, Luísa, Alisson
6. **Footer** — Instrução curta

---

## Output esperado

- `output/relatorios/pmo-semanal/YYYY-MM-DD.html` (≈ 100 KB com 16 projetos, 6 coordenadores)
- `output/relatorios/pmo-semanal/YYYY-MM-DD.sent.json` (modo send)
- `.tmp/pmo_weekly_metrics.json`, `pmo_weekly_summary.json`

---

## Checklist

- [ ] `.env` com `CLICKUP_API_KEY` e `ANTHROPIC_API_KEY`
- [ ] `tools/gws/credentials.json` + `token.json` para Gmail
- [ ] `tools/reports/config/pmo_diario.yaml` com destinatários corretos
- [ ] Scheduled task `relatorio-pmo-semanal` ativa com cron `0 16 * * 5`
- [ ] Logs `output/relatorios/pmo-semanal/*.sent.json` confirmando entrega

---

## Skill associada

Slash `/relatorio-pmo-semanal` em [.claude/skills/relatorio-pmo-semanal/SKILL.md](../../.claude/skills/relatorio-pmo-semanal/SKILL.md).

---

## Dependências

- Reusa `clickup_pull_projetos_ntics.py` parametrizando `--cutoff-hours`
- Reusa `_common.py`, `aggregate_pmo_metrics.py` (helpers `is_done`, `_is_creative`, `task_view`)
- Reusa `render_pmo_html.py` (helpers `render`, `inline_css`)
- Reusa `send_pmo_email.py` (com `--subject-kind weekly`)
- Template separado: `tools/reports/templates/pmo_semanal.html.j2`
