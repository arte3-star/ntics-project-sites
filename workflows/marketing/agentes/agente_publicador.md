# Agente Publicador — Aprovação e Publicação em Redes Sociais

> Agente que detecta a aprovação do Lucas no ClickUp e publica automaticamente
> no LinkedIn (via n8n) e notifica para postagem manual no Instagram.

---

## Visão Geral do Fluxo Completo

```
[Claude Code — Agente Criador Semanal]
  domingo 20h: gera carrosséis (JPGs + PDF LinkedIn) + captions
       ↓
  upload para Google Drive (retorna links públicos)
       ↓
  atualiza task ClickUp:
    - campo customizado: drive_folder (link pasta Drive)
    - campo customizado: caption_ig (caption pronta para Instagram)
    - campo customizado: caption_li (caption pronta para LinkedIn)
    - descrição: checklist de aprovação
       ↓
  status → "revisao"

[Lucas — Revisão Manual no ClickUp]
  abre a task, confere checklist
       ↓
  muda status → "aprovado"

[n8n — Agente Publicador]  ← este documento
  webhook detecta status "aprovado"
       ↓
  lê campos customizados da task (drive_folder, caption_li)
       ↓
  baixa PDF do Drive (carrossel-linkedin.pdf)
       ↓
  publica no LinkedIn (página da empresa NTICS)
       ↓
  status → "publicado"
       ↓
  adiciona comentário na task com link do post + instruções Instagram

[Lucas — Instagram Manual]
  abre comentário na task ClickUp
       ↓
  copia caption_ig + baixa fotos do link drive_folder
       ↓
  posta no Instagram pelo app
```

---

## Fluxo de Status no ClickUp

```
nao iniciado → revisao → aprovado → publicado
     ↑             ↑          ↑           ↑
  (plano       (agente    (Lucas      (agente
  mensal)      criador)   aprova)    publicador)
```

| Status | Quem muda | Quando |
|--------|-----------|--------|
| `nao iniciado` | `/plano-mensal` | Criação das tasks mensais |
| `revisao` | Agente Criador (Claude Code) | Conteúdo gerado e pronto |
| `aprovado` | Lucas (manual) | Revisão concluída |
| `publicado` | Agente Publicador (n8n) | Após publicação LinkedIn bem-sucedida |

---

## Campos Customizados no ClickUp

Criar na lista `901109494072` (Cronograma de redes sociais NTICS):

| Campo | Tipo | Preenchido por | Usado por |
|-------|------|----------------|-----------|
| `drive_folder` | URL | Agente Criador | n8n + Lucas (Instagram) |
| `caption_ig` | Text (Long) | Agente Criador | Lucas (Instagram manual) |
| `caption_li` | Text (Long) | Agente Criador | n8n (LinkedIn auto) |

**IDs dos campos** (hardcodados em `tools/integrations/create_social_media_tasks.py`):
```
FIELD_DRIVE_FOLDER = "1d64bc13-8d71-43b1-a1d0-58ee7dc77c9f"
FIELD_CAPTION_IG   = "5a040812-38d9-45a9-a911-4fcc17396d10"
FIELD_CAPTION_LI   = "f1fd09a5-7dc8-48bd-959d-3724baf21edd"
```

---

## Como Lucas Aprova (Passo a Passo)

1. Abrir ClickUp → lista **Cronograma de redes sociais NTICS**
2. Filtrar por status **"revisao"**
3. Abrir a task da peça a revisar
4. Clicar no link `drive_folder` → conferir as imagens no Drive
5. Ler `caption_ig` e `caption_li` — conferir tom, dados, CTA
6. Marcar os checkboxes do checklist na descrição
7. Se OK: **mudar status para "aprovado"** — a publicação LinkedIn dispara automaticamente
8. Se precisar de ajuste: comentar na task (o Agente de Ajustes responde)

---

## Como Lucas Posta no Instagram (Passo a Passo)

Após receber o comentário de confirmação do LinkedIn na task:

1. Abrir a task no ClickUp
2. Copiar o texto do campo `caption_ig`
3. Clicar no link `drive_folder` → baixar as imagens (JPGs numerados)
4. Abrir o Instagram no celular
5. Criar novo post → selecionar múltiplas imagens (na ordem numerada) → carrossel
6. Colar a caption copiada
7. Publicar ou agendar

---

## Estrutura do Workflow n8n (5 Nós)

```
[1] Webhook — recebe taskStatusUpdated do ClickUp
    ↓
[2] IF — status == "aprovado"?
    ↓ (sim)
[3] HTTP Request — GET task do ClickUp (ler campos customizados)
    ↓
[4] LinkedIn Node — posta PDF carrossel + caption_li na página da empresa
    ↓
[5a] ClickUp Update Task — status → "publicado"
[5b] ClickUp Comment — link do post LinkedIn + instruções Instagram
```

### Nó 1 — Webhook ClickUp

- **Tipo:** Webhook (HTTP POST)
- **Evento:** `taskStatusUpdated`
- **Configurar em:** ClickUp → Settings → Integrations → Webhooks → Add Webhook
  - Events: `taskStatusUpdated`
  - Lista: `901109494072`
  - Endpoint: URL gerada pelo n8n

### Nó 2 — IF: Filtrar "aprovado"

- **Condição:** `{{ $json.history_items[0].after.status }} == "aprovado"`
- Branch FALSE: Stop (sem ação — ignora mudanças para outros status)

### Nó 3 — HTTP Request: Get Task ClickUp

- **Método:** GET
- **URL:** `https://api.clickup.com/api/v2/task/{{ $json.task_id }}?custom_fields=true`
- **Header:** `Authorization: {{ $env.CLICKUP_API_KEY }}`
- Extrair dos campos customizados:
  - `caption_li` → texto para LinkedIn
  - `drive_folder` → link da pasta (para encontrar o PDF)

### Nó 4 — LinkedIn: Publicar Carrossel

- **Tipo:** LinkedIn node (nativo n8n)
- **Credencial:** LinkedIn OAuth2 com scope `w_organization_social`
- **Post type:** Document (PDF)
- **Author:** URN da página NTICS: `urn:li:organization:{ID}`
  - Como obter: abrir `linkedin.com/company/ntics` → URL contém o ID numérico
- **Document URL:** link do arquivo `carrossel-linkedin.pdf` na pasta Drive
  - Converter URL de visualização para download: `https://drive.google.com/uc?export=download&id={FILE_ID}`
- **Commentary:** `{{ campo caption_li da task }}`

> O Agente Criador já exporta o PDF e o sobe no Drive com nome `carrossel-linkedin.pdf`.
> O n8n baixa e envia direto — sem processamento de imagem.

### Nó 5a — ClickUp Update Task

- **Status:** `publicado`
- **Task ID:** `{{ $('Webhook').item.json.task_id }}`

### Nó 5b — ClickUp Comment

```
LinkedIn publicado com sucesso!
Link: {url_do_post_linkedin}
Publicado em: {data_hora_BRT}

---
Instagram: caption e imagens prontas no campo da task.
Baixe as fotos em: {drive_folder}
```

---

## Pré-requisitos e Credenciais

### ClickUp

| Item | Como obter |
|------|-----------|
| API Key | ClickUp → Settings → Apps → API Token |
| Webhook | ClickUp → Settings → Integrations → Webhooks |
| IDs dos campos customizados | URL ao editar cada campo |

### LinkedIn

| Item | Detalhes |
|------|---------|
| Onde criar app | [LinkedIn Developer Portal](https://developer.linkedin.com/) |
| Tipo | Company App (associado à página NTICS) |
| Permissão | `w_organization_social` |
| URN da empresa | `linkedin.com/company/ntics` → número na URL |
| No n8n | Criar credencial "LinkedIn OAuth2 API" → fazer OAuth uma vez |

> A permissão `w_organization_social` exige que o usuário autenticando seja admin da página NTICS no LinkedIn.

### Google Drive

As pastas de marketing são públicas (link "qualquer pessoa com o link pode ver").
Download direto sem autenticação: `https://drive.google.com/uc?export=download&id={FILE_ID}`

---

## Tratamento de Erros

| Situação | Comportamento |
|----------|--------------|
| PDF não encontrado no Drive | Comentário de erro na task + status volta "revisao" |
| LinkedIn API falha (token expirado) | Comentário de erro + status volta "revisao" |
| Task sem campo `caption_li` preenchido | Publicar com caption vazia + comentário de aviso |
| Webhook chega com status ≠ "aprovado" | Filtrado no Nó 2 — sem ação |

**Em qualquer falha:** o status volta para `"revisao"` e o comentário informa a etapa que falhou, para Lucas republicar manualmente se necessário.

---

## Checklist de Manutenção Mensal

- [ ] Token LinkedIn ainda válido (testar no n8n → Credentials)
- [ ] Webhook ClickUp ativo (ClickUp desativa após 30 dias sem uso — verificar em Settings → Integrations → Webhooks)
- [ ] Arquivo `carrossel-linkedin.pdf` presente nas pastas do Drive após geração

---

## Migração Futura: Instagram Automático

Quando o acesso à Meta Graph API for resolvido (vincular conta Facebook correta ao Instagram):

1. Criar app no Meta for Developers com permissões `instagram_content_publish`
2. Gerar System User Token (não expira)
3. Adicionar 4 nós HTTP Request ao workflow n8n (após o Nó 4):
   - Upload cada imagem → `creation_id`
   - Criar container CAROUSEL com `children[]` + `caption_ig`
   - Polling `status_code == FINISHED`
   - Publicar → `media_id`
4. Remover instruções de postagem manual do comentário ClickUp

---

## Referências

| Recurso | Caminho |
|---------|---------|
| Agente que gera o conteúdo | `workflows/marketing/agentes/agente_criador_semanal.md` |
| Agente que revisa | `workflows/marketing/agentes/agente_revisor_semanal.md` |
| Agente de ajustes | `workflows/marketing/agentes/agente_ajustes_tempo_real.md` |
| Estratégia LinkedIn | `workflows/marketing/referencia/linkedin_strategy.md` |
| Script ClickUp (gravar campos) | `tools/integrations/create_social_media_tasks.py` |
| Upload Drive | `tools/integrations/upload_to_drive.py` |

---

## Trigger

```
Tipo: Webhook (evento ClickUp taskStatusUpdated)
Plataforma: n8n
Depende de: Agente Criador ter rodado + Lucas ter aprovado no ClickUp
```
