# Relatório Diário PMO de Projetos

> Pipeline automatizado que lê ClickUp (pasta Projetos Ativos + Sprint da semana), agrega saúde por coordenador, busca comentários das tasks atrasadas, gera resumo executivo via Claude Haiku e envia HTML por email todo dia útil às 8h.

---

## Quando usar

- **Automático**: roda 8h BRT em dias úteis via scheduled task
- **Manual**: quando precisa de snapshot antes de reunião com diretoria, ou para validar formato após mudança no template/regras
- **NÃO usar** para relatórios mensais/trimestrais (esse é diário, janela de 24h)

---

## Inputs

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| `--mode` | enum | Não | `dry-run` (default), `draft`, `send` |
| `--date` | YYYY-MM-DD | Não | Data referência (default hoje BRT) |
| `--no-llm` | flag | Não | Pula Haiku, usa template determinístico |
| `--skip-business-day-check` | flag | Não | Força execução em fim de semana ou feriado |
| `--limit N` | int | Não | Limita N listas (debug) |

---

## APIs e chaves

| API | Uso | Variável de ambiente |
|-----|-----|----------------------|
| ClickUp | Pull tasks de projetos + sprint + comentários | `CLICKUP_API_KEY` |
| Anthropic Claude | Resumo executivo (Haiku) | `ANTHROPIC_API_KEY` |
| Gmail | Envio do relatório | OAuth via `credentials.json` + `token.json` |

---

## Tool

```bash
# Manual (modo padrão dry-run abre HTML local)
python tools/reports/run_pmo_daily.py --mode dry-run

# Cria rascunho no Gmail para revisão
python tools/reports/run_pmo_daily.py --mode draft

# Envia direto para destinatários do YAML
python tools/reports/run_pmo_daily.py --mode send

# Forçar dia útil (quando rodando manualmente em final de semana)
python tools/reports/run_pmo_daily.py --mode draft --skip-business-day-check
```

Configuração editável em `tools/reports/config/pmo_diario.yaml`:
- `recipients.to/cc` — destinatários
- `coordinator_overrides` — mapa list_id → coordenador real (quando assignee dominante não bate)
- `team.designers / video_makers` — separa quem entra na seção "Design e vídeo"
- `health` — thresholds VERDE/AMARELO/VERMELHO
- `blockers` — keywords para detectar bloqueios e decisões pendentes

---

## Execução

### Fase 1: Pull projetos (auto)

`tools/integrations/clickup_pull_projetos_ntics.py` lê todas as listas da pasta `90115187061` (exceto triagem `901113425673` e gestão `901108780010`). Resolve custom fields `Fase`, `Áreas/Setores`, `Trimestre`, `Completion Rate`. Inclui tasks abertas + fechadas nas últimas 24h. Output: `.tmp/pmo_raw_tasks.json`.

### Fase 2: Pull sprint da semana (auto)

`tools/integrations/clickup_pull_sprint.py` identifica a sprint ativa pela janela no nome (`Sprint NN (DD/M/YY - DD/M/YY)`) na pasta `90115190074` e puxa todas as tasks. Output: `.tmp/pmo_raw_sprint.json`.

### Fase 3: Agregar métricas (auto)

`tools/reports/aggregate_pmo_metrics.py` calcula:
- Saúde por projeto (VERDE/AMARELO/VERMELHO baseado em overdue_pct e bloqueios)
- Atrasos, marcos próximos 7 dias, decisões pendentes, mudanças 24h
- Aderência da Sprint por dia da semana
- Agrupamento por coordenador (com overrides do YAML)
- Tasks de design/vídeo por pessoa (Luísa, Marina, Alisson, Marcos)

Output: `.tmp/pmo_metrics.json`.

### Fase 4: Comentários das tasks atrasadas (auto, não-bloqueante)

`tools/integrations/clickup_pull_overdue_comments.py` busca o último comentário (≤30 dias) das top 5 atrasadas por projeto via `GET /task/{id}/comment`. Enriquece `pmo_metrics.json` com `last_comment` por task.

### Fase 5: Resumo executivo Haiku (auto)

`tools/reports/generate_pmo_summary.py` chama Claude Haiku 4.5 com agregados + top 5 atrasos + bloqueios + decisões. Devolve JSON com `good`/`concern`/`decide_today` (3 parágrafos, máx 80 palavras cada). Em falha, fallback determinístico baseado nos KPIs.

### Fase 6: Render HTML + auto-review (auto, bloqueante)

`tools/reports/render_pmo_html.py` aplica Jinja2 + premailer (CSS inline). Auto-review valida:
- HTML > 5 KB
- 9 seções presentes (header, resumo, kpis, sprint, saude, design, mudancas, marcos, decisoes, footer)
- Sem placeholder Jinja não resolvido
- **Sem em-dash (—)** — regra do CLAUDE.md
- 3 chaves do summary preenchidas com >= 50 chars

Output: `output/relatorios/pmo-diario/YYYY-MM-DD.html`.

### Fase 7: Envio Gmail (auto)

`tools/reports/send_pmo_email.py` cria mensagem MIME multipart, envia via Gmail API e verifica que `labelIds` contém `SENT`. Salva log em `output/relatorios/pmo-diario/YYYY-MM-DD.sent.json`.

Em falha, mantém HTML local e cria task review na lista de triagem `901113425673` com tag `pmo-relatorio-falha`.

---

## Estrutura do email

1. **Header** — Data por extenso, janela 24h
2. **Resumo executivo** — 3 cards (Bom / Preocupa / Decidir hoje) gerados pelo Haiku
3. **KPIs gerais** — Projetos, Tasks abertas, Atrasadas, Bloqueios, % Sprint
4. **Aderência da Sprint** — Tabela dia-a-dia (previstas, no prazo, atrasadas, pendentes, %)
5. **Por coordenador** — Cada PM com seus projetos, expandindo:
   - Cabeçalho do projeto (fase, abertas, atrasadas, saúde)
   - Lista de tasks atrasadas (top 8)
   - Último comentário (se ≤30 dias) inline em cada task
6. **Design e vídeo** — Marcos, Luisa, Marina, Alisson com atrasadas + próximos 7 dias
7. **Mudanças últimas 24h** — Por projeto, máx 8 itens
8. **Marcos próximos 7 dias** — Por projeto
9. **Decisões e bloqueios** — Borda vermelha, com motivo
10. **Footer** — Instrução curta para responder o email

---

## Output esperado

- `output/relatorios/pmo-diario/YYYY-MM-DD.html` (≈ 90 KB com 16 projetos, 3000+ tasks)
- `output/relatorios/pmo-diario/YYYY-MM-DD.sent.json` (modo send)
- `.tmp/pmo_raw_tasks.json`, `pmo_raw_sprint.json`, `pmo_metrics.json`, `pmo_summary.json`

---

## Checklist

- [ ] `.env` carrega `CLICKUP_API_KEY` e `ANTHROPIC_API_KEY`
- [ ] `credentials.json` + `token.json` presentes na raiz
- [ ] `requirements.txt` atualizado com `PyYAML` e `holidays`
- [ ] `tools/reports/config/pmo_diario.yaml` com destinatários corretos
- [ ] Scheduled task ativa com cron `0 8 * * 1-5` em `America/Sao_Paulo`
- [ ] Logs `output/relatorios/pmo-diario/*.sent.json` confirmando entrega

---

## Skill associada

Usuário pode chamar `/relatorio-pmo` (skill em `.claude/skills/relatorio-pmo/SKILL.md`) para rodar manualmente.

---

## Dependências

- `clickup_pull_projetos_ntics.py` reusa `_common.py` para headers, paginação, backoff
- `clickup_pull_sprint.py` importa `slim_task` e `fetch_tasks` de `clickup_pull_projetos_ntics.py`
- Template em `tools/reports/templates/pmo_diario.html.j2`
- Paleta brand NTICS: `#005F73` (azul petróleo), `#3DAA35` (verde), `#D41A6A` (rosa) — ver `brand-book/03-identidade-visual/cores.md`
