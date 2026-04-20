# Workflow: Process Meeting Transcript (NTICS)

## Objective
Every 30 minutes, poll Google Calendar for meetings that have ended, check for attached transcripts ("Anotacoes do Gemini"), and autonomously:
1. Read the transcript content from the attached Google Doc
2. Classify the meeting type
3. Extract all tasks and decisions
4. Create tasks in ClickUp in the correct lists and phases
5. If SALES -> create a note in Pipedrive
6. Update the Learning Registry in ClickUp if new organizational knowledge is detected

---

## Trigger: Google Calendar Polling

**Scheduled task** runs every 30 minutes. Each run:

### Step 0 — Discover new transcripts from Calendar

1. Call `gcal_list_events` with:
   - `calendarId`: `primary`
   - `timeMin`: 24 hours ago (ISO 8601)
   - `timeMax`: now (ISO 8601)
   - `timeZone`: `America/Sao_Paulo`
   - `condenseEventDetails`: `false`
2. For each event returned, check if it has `attachments[]`
3. **IMPORTANT**: `gcal_list_events` does NOT always return attachments for events where the Gemini doc was added after the list was fetched (race condition). For any work meeting that has NO attachments in the list result, call `gcal_get_event` individually to confirm. Skip only personal/all-day/working-location events.
4. Filter attachments where `title` contains "Anotacoes do Gemini" or "Anotações do Gemini"
5. For each matching attachment, extract `fileId`
6. Read `.tmp/processed_atas.txt` and check if `fileId` is already listed (deduplication)
7. For each NEW transcript (not in processed list):
   - Store: `event_summary` (meeting title), `fileId`, `fileUrl`, `attendees[]`, `start/end` times, `organizer`
   - Proceed to Step 1

**Why 24h window instead of 30min:** Meetings can run longer than scheduled. A 24h window catches everything, and `processed_atas.txt` prevents reprocessing. This is simpler and more robust than trying to calculate exact end times.

---

## Required Inputs (per transcript)

| Input | Source | Required |
|-------|--------|----------|
| `fileId` | Calendar event attachment | Yes |
| `fileUrl` | Calendar event attachment | Yes |
| `event_summary` | Calendar event title | Yes |
| `attendees` | Calendar event attendees | No |

---

## Tools to Use (in order)

1. `gcal_list_events` + `gcal_get_event` (MCP) -> discover transcripts
2. `tools/integrations/read_google_doc.py` -> read transcript content from Google Doc
3. `tools/meetings/classify_meeting.py` -> classify type and extract tasks
4. `tools/integrations/create_clickup_tasks.py` -> create tasks in ClickUp
5. `tools/integrations/create_pipedrive_note.py` -> only if SALES classification
6. `tools/integrations/update_learning_registry.py` -> only if new knowledge detected

---

## Step-by-Step Execution

### Step 1 — Read transcript content
Run:
```
tools/integrations/read_google_doc.py --url {fileUrl}
```
Expected output: full text of the document saved to `.tmp/transcript.txt`

**NOTE**: `read_google_doc.py` requires `credentials.json` (service account) which is not available in the scheduled task environment. Use the Google Drive MCP tool instead:
```
google_drive_fetch(document_ids=["{fileId}"])
```
This returns the full text directly. Save the `.text` field to `.tmp/transcript.txt`.

### Step 2 — Classify and extract tasks
**NOTE**: `classify_meeting.py` has a path bug — it computes root as `tools/` instead of project root (uses `parent.parent` but should be `parent.parent.parent`). Workaround: write transcript to **both** `.tmp/transcript.txt` AND `tools/.tmp/transcript.txt`, then run the script. Output will be in `tools/.tmp/meeting_result.json` — copy it to `.tmp/meeting_result.json` after.

Also: run with `-X utf8` flag on Windows to avoid emoji encoding errors:
```
python -X utf8 tools/meetings/classify_meeting.py --url {fileUrl} --name {event_summary}
```
(transcript is read from `tools/.tmp/transcript.txt` automatically)
Expected output: `.tmp/meeting_result.json` with structure:
```json
{
  "meeting_type": "INTERNAL|SALES|STRATEGIC",
  "confidence": 0-100,
  "title": "string",
  "project_number": "115-127 or null",
  "list_id": "ClickUp list ID or 901113425673",
  "external_participants": [],
  "tasks": [
    {
      "title": "Action in infinitive",
      "assignee_id": "numeric ID or null",
      "due_date": "YYYY-MM-DD or null",
      "priority": "urgent|high|normal|low",
      "city": "string or null",
      "phase": "string or null",
      "context": "excerpt from transcript"
    }
  ],
  "pipedrive_summary": "string or null",
  "learning": "string or null"
}
```

### Step 3 — Create ClickUp tasks
Run:
```
python -X utf8 tools/integrations/create_clickup_tasks.py --input .tmp/meeting_result.json
```
- Creates each task in the identified list
- If `city` or `phase` is set -> search for parent task and create as subtask
- **TODAS as tasks vão sempre para a lista `901113425673`** (lista única para pós-reuniões), independente do projeto identificado. `list_id` é fixo no código.
- Confidence < 80% -> criar review task com title "Revisar ata — {title}", assign to Lucas (81513300)
- Always include in description: meeting title, type, date, transcript URL, context excerpt
- **OBRIGATÓRIO**: todas as tasks devem ter `tags` com o título da reunião (event_summary) no momento da criação. Nunca criar task sem tag.

**BUG CONHECIDO**: `create_clickup_tasks.py` usa `"status": "to do"` mas a lista `901113425673` não tem esse status. O script lança HTTPError 400. **Fix confirmado (2026-04-19)**: usar o MCP `clickup_create_task` **sem passar o campo `status`** (omitir completamente) — o ClickUp usa o status padrão da lista. Nem "to do" nem "backlog" funcionam nessa lista; omitir é o correto.

### Step 3.5 — Create ClickUp Doc "ATA Reuniao"

After creating tasks, create a ClickUp Doc to centralize the meeting record:

Use `clickup_create_document` MCP tool:
- **name**: `ATA Reuniao - {event_summary} ({DD/MM/YYYY})`
- **parent**: `{"id": "{list_id}", "type": "6"}` (same list as the tasks)
- **visibility**: `PUBLIC`
- **create_page**: `true`

Then use `clickup_update_document_page` to fill the page with:
```markdown
# ATA Reuniao - {event_summary}

**Data:** {start_date} {start_time} - {end_time} (BRT)
**Organizador:** {organizer_name} ({organizer_email})
**Tipo:** {meeting_type} ({confidence}% confianca)
**Projeto:** {project_number} — {project_name}

**Participantes:**
- {attendee_1_name} ({attendee_1_email})
- ...

---

## Transcricao / Anotacoes do Gemini

[Anotacoes do Gemini - Google Docs]({fileUrl})

---

## Resumo

{summary from classify_meeting.py - meeting_result.json title + pipedrive_summary or first 300 chars of transcript}

---

## Tarefas Criadas

- {task_1_title} -> {assignee_name}
- {task_2_title} -> {assignee_name}
- ...

---

## Evento no Google Calendar

[Abrir evento no Calendar]({event_htmlLink})
```

Include the doc URL in the final report.

### Step 4 — Create Pipedrive note (SALES only)
If `meeting_type == "SALES"` AND `confidence >= 80`:
```
tools/integrations/create_pipedrive_note.py --input .tmp/meeting_result.json --url {fileUrl}
```
- Search deal by external participant name
- Create note linked to deal (or unlinked if not found)

### Step 5 — Update Learning Registry (if applicable)
If `learning` field is not null:
```
tools/integrations/update_learning_registry.py --learning "{learning_text}" --meeting "{title}"
```
- Appends new row to the learning table in ClickUp doc `8cje8p1-65331`, page `8cje8p1-39691`

### Step 6 — Mark as processed
Append `fileId` to `.tmp/processed_atas.txt` (one ID per line) to prevent reprocessing.

---

## Edge Cases

| Situation | Action |
|-----------|--------|
| Confidence < 80% | Create review task in `901113425673`, assign to Lucas, skip Pipedrive |
| Project not identified | Use default list `901113425673` |
| Assignee not found | Leave unassigned, add note in description |
| Google Doc not readable | Log error, create manual review task |
| Pipedrive deal not found | Create note without deal_id |
| Transcript too short (<100 chars) | Skip processing, log warning |
| Event has no attachments | Skip (not a recorded meeting) |
| Attachment title != "Anotacoes do Gemini" | Skip (not a transcript) |
| fileId already in processed_atas.txt | Skip (already processed) |
| Meeting still ongoing | Will be caught in next 30min cycle |

---

## Expected Final Output

Report to user:
```
Ata processada: {event_summary}
Tipo: {meeting_type} ({confidence}% confianca)
Projeto: {project_number} — {project_name}
Tarefas criadas: {count}
  - {task_title} -> {assignee_name} ({list_name})
  - ...
Pipedrive: {updated/skipped}
Aprendizado registrado: {yes/no}
```

---

## NTICS Organizational Context

### Team (Name -> ClickUp ID)
- Ana Carolina Xavier (CEO): 81460584
- Abilio Martins (Dir. Operacoes e Vendas): 81470291
- Bruna Seibel (Coord. Projetos): 81461902
- Raiza Araujo (Produtora): 81460587
- Jessica Lora (Produtora): 81477520
- Mayara Ferreira (Inscricao/Auditoria): 81460588
- Lucas Rotta (AI/Comunicacao): 81513300
- Vera Carvalho (Financeiro): 126152139
- Cristina Ygiro (CSR/Negocios): 81502630
- Fernando Clark (Novos Negocios): 81460585
- Luiz Felipe Deffune (Juridico): 81460586
- Ariadne Canaver (Financeiro): 81545764
- Angelo Miguel (Assessoria): 81549824
- Luisa Moreira (Design): 87399549

### Assignment Rules by Keyword
- "producao / campo" -> Raiza 81460587 or Jessica 81477520
- "financeiro / NF / pagamento" -> Vera 126152139
- "juridico / contrato" -> Luiz Felipe 81460586
- "vendas / proposta / captacao" -> Abilio 81470291 or Cristina 81502630
- "comunicacao / IA / site / post" -> Lucas 81513300
- "inscricao / MINC" -> Mayara 81460588
- "coordenacao / prazo / PMO" -> Bruna 81461902
- "assessoria / release / clipping" -> Angelo 81549824
- "design / carrossel / visual" -> Luisa 87399549

### Active Projects 2026 (Number -> List ID)
- 116 -> 901113068470 (Cultura Robotica / Ester)
- 117 -> 901113013525 (Teatro Robotica / Whirlpool)
- 119 -> 901113051700 (PEC Eu Faco Parte / Sylvamo)
- 124 -> 901113142041 (Gastronomia e Arte / Compagas)
- Default (no project) -> 901113425673

### Project Identification Keywords
- Whirlpool -> 117 | Sylvamo/PEC -> 119 | Wilson Sons -> 118
- Repsol/Itinerante -> 122 | TCP/Circo -> 123 | Compagas/Gastronomia -> 124
- TAG/Negocio Cultural -> 121 | Sotreq/Empreendedorismo -> 127
- Statkraft/Porto Itapoa -> 120 | Ester -> 116 | Peroxidos/Tupy/BTG -> 115

### Project Phases (PMBOK Simplified)
1. Pre-Projeto / Engajamento
2. Planejamento da Execucao
3. Execucao em Campo (by city)
4. Pos-Execucao / Comunicacao
5. Relatorios Parciais
6. Fechamento MINC
7. Fechamento do Projeto
8. Logistica de Materiais

### Meeting Classification Rules
- INTERNAL: Only NTICS team, operational agenda -> ClickUp only, NO Pipedrive
- SALES: External client/sponsor present -> ClickUp + Pipedrive
- STRATEGIC: Leadership + OKRs/direction -> ClickUp only, NO Pipedrive

### ClickUp Context Documents
- Base de Conhecimento: `8cje8p1-65311`
- Inteligencia de Reunioes: `8cje8p1-65331`
- Registro de Aprendizados (page): `8cje8p1-39691`
- Workspace ID: `9011929793`
