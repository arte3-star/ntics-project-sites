# Workflow: Process Meeting Transcript (NTICS)

## Objective
Process a meeting transcript received from the Make webhook (Google Drive trigger) and autonomously:
1. Classify the meeting type
2. Extract all tasks and decisions
3. Create tasks in ClickUp in the correct lists and phases
4. If SALES → create a note in Pipedrive
5. Update the Learning Registry in ClickUp if new organizational knowledge is detected

---

## Required Inputs

| Input | Source | Required |
|-------|--------|----------|
| `transcript_text` | Webhook payload or URL content | Yes |
| `file_url` | Google Doc URL | Yes |
| `file_name` | Document name from Drive | Yes |

---

## Tools to Use (in order)

1. `tools/read_google_doc.py` → if only URL provided (no content in payload)
2. `tools/classify_meeting.py` → classify type and extract tasks
3. `tools/create_clickup_tasks.py` → create tasks in ClickUp
4. `tools/create_pipedrive_note.py` → only if SALES classification
5. `tools/update_learning_registry.py` → only if new knowledge detected

---

## Step-by-Step Execution

### Step 1 — Read content (if needed)
If `transcript_text` is empty or short (<100 chars), run:
```
tools/read_google_doc.py --url {file_url}
```
Expected output: full text of the document saved to `.tmp/transcript.txt`

### Step 2 — Classify and extract tasks
Run:
```
tools/classify_meeting.py --text {transcript_text} --url {file_url} --name {file_name}
```
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
tools/create_clickup_tasks.py --input .tmp/meeting_result.json
```
- Creates each task in the identified list
- If `city` or `phase` is set → search for parent task and create as subtask
- Confidence < 80% → create in list `901113425673` with title "⚠️ Revisar ata — {title}", assign to Lucas (81513300)
- Always include in description: meeting title, type, date, transcript URL, context excerpt

### Step 4 — Create Pipedrive note (SALES only)
If `meeting_type == "SALES"` AND `confidence >= 80`:
```
tools/create_pipedrive_note.py --input .tmp/meeting_result.json --url {file_url}
```
- Search deal by external participant name
- Create note linked to deal (or unlinked if not found)

### Step 5 — Update Learning Registry (if applicable)
If `learning` field is not null:
```
tools/update_learning_registry.py --learning "{learning_text}" --meeting "{title}"
```
- Appends new row to the learning table in ClickUp doc `8cje8p1-65331`, page `8cje8p1-39691`

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

---

## Expected Final Output

Report to user:
```
✅ Ata processada: {file_name}
Tipo: {meeting_type} ({confidence}% confiança)
Projeto: {project_number} — {project_name}
Tarefas criadas: {count}
  - {task_title} → {assignee_name} ({list_name})
  - ...
Pipedrive: {updated/skipped}
Aprendizado registrado: {yes/no}
```

---

## NTICS Organizational Context

### Team (Name → ClickUp ID)
- Ana Carolina Xavier (CEO): 81460584
- Abilio Martins (Dir. Operações e Vendas): 81470291
- Bruna Seibel (Coord. Projetos): 81461902
- Raíza Araújo (Produtora): 81460587
- Jessica Lora (Produtora): 81477520
- Mayara Ferreira (Inscrição/Auditoria): 81460588
- Lucas Rotta (AI/Comunicação): 81513300
- Vera Carvalho (Financeiro): 126152139
- Cristina Ygiro (CSR/Negócios): 81502630
- Fernando Clark (Novos Negócios): 81460585
- Luiz Felipe Deffune (Jurídico): 81460586
- Ariadne Canaver (Financeiro): 81545764
- Angelo Miguel (Assessoria): 81549824
- Luisa Moreira (Design): 87399549

### Assignment Rules by Keyword
- "produção / campo" → Raíza 81460587 or Jessica 81477520
- "financeiro / NF / pagamento" → Vera 126152139
- "jurídico / contrato" → Luiz Felipe 81460586
- "vendas / proposta / captação" → Abilio 81470291 or Cristina 81502630
- "comunicação / IA / site / post" → Lucas 81513300
- "inscrição / MINC" → Mayara 81460588
- "coordenação / prazo / PMO" → Bruna 81461902
- "assessoria / release / clipping" → Angelo 81549824
- "design / carrossel / visual" → Luisa 87399549

### Active Projects 2026 (Number → List ID)
- 116 → 901113068470 (Cultura Robótica / Éster)
- 117 → 901113013525 (Teatro Robótica / Whirlpool)
- 119 → 901113051700 (PEC Eu Faço Parte / Sylvamo)
- 124 → 901113142041 (Gastronomia é Arte / Compagas)
- Default (no project) → 901113425673

### Project Identification Keywords
- Whirlpool → 117 | Sylvamo/PEC → 119 | Wilson Sons → 118
- Repsol/Itinerante → 122 | TCP/Circo → 123 | Compagas/Gastronomia → 124
- TAG/Negócio Cultural → 121 | Sotreq/Empreendedorismo → 127
- Statkraft/Porto Itapoá → 120 | Éster → 116 | Peróxidos/Tupy/BTG → 115

### Project Phases (PMBOK Simplified)
1. Pré-Projeto / Engajamento
2. Planejamento da Execução
3. Execução em Campo (by city)
4. Pós-Execução / Comunicação
5. Relatórios Parciais
6. Fechamento MINC
7. Fechamento do Projeto
8. Logística de Materiais

### Meeting Classification Rules
- INTERNAL: Only NTICS team, operational agenda → ClickUp only, NO Pipedrive
- SALES: External client/sponsor present → ClickUp + Pipedrive
- STRATEGIC: Leadership + OKRs/direction → ClickUp only, NO Pipedrive

### ClickUp Context Documents
- Base de Conhecimento: `8cje8p1-65311`
- Inteligência de Reuniões: `8cje8p1-65331`
- Registro de Aprendizados (page): `8cje8p1-39691`
- Workspace ID: `9011929793`

---

## Make Trigger Configuration

The Make scenario sends this payload when a new Google Doc appears in the atas folder:
```json
{
  "evento": "nova_ata",
  "secret": "ntics-secret-2026",
  "arquivo": {
    "id": "google_doc_id",
    "nome": "file name",
    "url": "https://docs.google.com/document/d/...",
    "conteudo": "full text if available"
  }
}
```

File name prefix can hint at meeting type:
- Starts with "INT" → likely INTERNAL
- Starts with "SALES" → likely SALES
- Starts with "EST" → likely STRATEGIC
Use as a hint only, not a rule — always verify with content analysis.
