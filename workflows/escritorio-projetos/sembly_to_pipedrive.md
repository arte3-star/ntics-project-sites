# Workflow: Sembly → Pipedrive (notas em deals)

## Objective
A cada 4h, ler reuniões processadas no Sembly, classificar via Claude e, quando for **SALES**, criar uma nota no deal correspondente do Pipedrive (matching por email do participante externo). Reuniões sem participante externo ou que não forem classificadas como SALES são descartadas. Reuniões sem deal correspondente viram **nota órfã**, não-linkada.

Diferente do pipeline Gemini (`process_meeting_transcript.md`), este NÃO cria tasks no ClickUp e NÃO atualiza Learning Registry. É focado exclusivamente em CRM de vendas.

---

## Trigger

Scheduled task chamando `python tools/integrations/sembly_to_pipedrive.py`. Cron: `0 9,13,18,22 * * *` (BRT).

Idempotência: `.cache/sembly_processed.json` armazena `last_run` (ISO 8601) e `processed_ids` (últimas 500 meeting IDs). Cada run filtra IDs já vistas.

---

## Pipeline

```
sembly_to_pipedrive.py (orquestrador)
  │
  ├── sembly_pull_meetings.list_recent_meetings(since=last_run)
  │      └── filtra IDs já processadas
  │
  └── para cada meeting nova:
        ├── sembly.get_meeting_detail() + extract_participants()
        ├── has_external_participant()? não → SKIP_NO_EXTERNAL
        ├── sembly.get_meeting_transcript()
        ├── classify_meeting.py via subprocess (--text/--url/--name)
        ├── meeting_type != SALES? → SKIP_NOT_SALES
        ├── pipedrive_match_deal.find_deal_for_participants(emails)
        │      ├── 1º: persons/search?fields=email
        │      └── 2º (fallback): organizations/search por domínio
        └── create_pipedrive_note.py --deal-id (ou unlinked se None)
```

---

## Required Inputs

| Input | Source | Required |
|-------|--------|----------|
| Sembly meeting ID | `list_recent_meetings()` | Yes |
| Transcript completo | `get_meeting_transcript(id)` | Yes |
| Lista de attendees com email | `get_meeting_detail(id)` | Yes |

---

## Tools

| Order | Script | Função |
|-------|--------|--------|
| 1 | `tools/integrations/sembly_pull_meetings.py` | Cliente Sembly (list/detail/transcript) |
| 2 | `tools/meetings/classify_meeting.py` | Claude classifica e gera `pipedrive_summary` |
| 3 | `tools/integrations/pipedrive_match_deal.py` | Match deal por email → fallback domínio |
| 4 | `tools/integrations/create_pipedrive_note.py` | POST /v1/notes com `--deal-id` |

---

## Env Vars

```
SEMBLY_API_KEY=...      # Bearer; plano Sembly Professional ou superior
PIPEDRIVE_API_KEY=...   # Token API do Pipedrive
ANTHROPIC_API_KEY=...   # já existente
```

---

## Filtros e regras

**Domínios internos** (não são "cliente"): `ntics.com.br`, `sbsustainablebusiness.com`. Editar em `sembly_pull_meetings.INTERNAL_DOMAINS` se trocar de domínio.

**Confiança mínima**: respeita o que `classify_meeting.py` retorna. Confiança baixa marca `triage=true` mas a nota ainda é criada.

**Nota órfã**: quando nenhum deal bater, a nota vai para o feed do Pipedrive sem `deal_id`. Pode ser linkada manualmente depois.

---

## Troubleshooting

| Sintoma | Diagnóstico | Ação |
|---------|-------------|------|
| 401 do Sembly | Token expirado ou plano sem API | Regerar key em sembly.ai/api ou subir plano |
| 404 em `/v1/meetings` | Sembly mudou rota | Conferir `developer.sembly.ai/`, atualizar `LIST_PATH` no client |
| `SKIP_NO_EXTERNAL` em reunião com cliente | Email do cliente está num domínio interno por engano | Limpar lista de domínios em `INTERNAL_DOMAINS` |
| Nota linkada ao deal errado | Pessoa tem múltiplos deals abertos | Email match retorna deal mais recente; cuidar manualmente ou refinar `open_deal_for_person` |
| Nota duplicada | Cache corrompido / state file apagado | `.cache/sembly_processed.json` é fonte da verdade; restaurar de backup |
| Classifier falha JSON parse | Transcript muito longo / corrupto | `classify_meeting.py` corta em 12k chars; revisar transcript em `.tmp/transcript.txt` |

---

## Estado e logs

| Caminho | Conteúdo |
|---------|----------|
| `.cache/sembly_processed.json` | `last_run` + `processed_ids` (mantém últimas 500) |
| `.tmp/transcript.txt` | Última transcrição lida do Sembly |
| `.tmp/meeting_result.json` | Saída do classifier |
| `logs/sembly_pipedrive_YYYY-MM-DD.log` | Uma linha por meeting com outcome |

Outcomes possíveis: `PROCESSED`, `SKIP_NO_EXTERNAL`, `SKIP_NOT_SALES`, `FAILED`.

---

## Verificação manual (após qualquer mudança)

```bash
# 1. Sanity test do client Sembly
python tools/integrations/sembly_pull_meetings.py --limit 5

# 2. Lookup Pipedrive por email
python tools/integrations/pipedrive_match_deal.py --email cliente@empresa.com

# 3. Dry-run do orquestrador (não posta)
python tools/integrations/sembly_to_pipedrive.py --dry-run

# 4. Rodar de fato uma vez
python tools/integrations/sembly_to_pipedrive.py

# 5. Validar idempotência
python tools/integrations/sembly_to_pipedrive.py
# segundo run deve mostrar "0 new"
```

Confira no Pipedrive: deal correspondente, aba Notes, deve ter nota pinned com título, data, participantes externos, link Sembly e summary.
