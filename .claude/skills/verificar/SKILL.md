---
name: verificar
description: "Verifica se uma operação de criação realmente produziu o resultado esperado — checklist por serviço antes de declarar sucesso"
user-invocable: true
---

## Quando usar

Invoque `/verificar` imediatamente após qualquer operação que cria ou modifica um objeto externo (ClickUp, Gmail, Google Drive, Leonardo AI). Nunca declare "feito" sem executar a verificação correspondente nesta mesma mensagem.

---

## Checklist por Serviço

### ClickUp — Criar task / comentário / status
```
# Após create_task:
task = clickup_get_task(task_id=<id_retornado>)
assert task['name'] == <nome_esperado>
assert task['status'] não é None
# Reporte o task_id verificado, não apenas "criado"
```

### Gmail — Criar draft / enviar mensagem
```
# Após gmail_create_draft:
drafts = gmail_search_messages(query="in:drafts subject:<assunto>")
assert len(drafts) > 0
# Confirme subject e destinatário antes de reportar
```

### Leonardo AI — Geração de imagem
```
# Após chamada de geração:
# 1. Aguarde status "COMPLETE" no polling (não apenas "PENDING")
# 2. Acesse a URL retornada e confirme status HTTP 200
# 3. Só então reporte o caminho/URL da imagem
```

### Google Drive — Upload de arquivo
```
# Após files.create():
file = drive.files.get(fileId=<id_retornado>, fields="id,name,size")
assert file['name'] == <nome_esperado>
assert int(file['size']) > 0
```

### Google Calendar — Criar evento
```
# Após gcal_create_event:
event = gcal_get_event(event_id=<id_retornado>)
assert event['summary'] == <titulo_esperado>
assert event['start'] está correto
```

---

## O que reportar ao usuário

Após verificação bem-sucedida, inclua no relatório:
- **ID confirmado** (task_id, draft_id, file_id)
- **Status verificado** (não apenas "chamada retornou 200")
- **Link direto** quando disponível (URL do ClickUp, link do Drive)

Exemplo correto:
> "Task criada e verificada: **#86abc123** — 'Carrossel Educativo Semana 15' · Status: Open · [Ver no ClickUp](https://app.clickup.com/t/86abc123)"

Exemplo incorreto:
> "Task criada com sucesso." ← sem verificação, não aceitável
