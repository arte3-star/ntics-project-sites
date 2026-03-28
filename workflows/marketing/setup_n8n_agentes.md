# Setup n8n — Agentes de Conteúdo NTICS

> Guia completo para configurar os 3 agentes autônomos de conteúdo no n8n.

---

## Pré-requisitos

### Credenciais necessárias

| Serviço | Variável | Status |
|---------|----------|--------|
| Anthropic API | `ANTHROPIC_API_KEY` | ✅ Disponível no `.env` |
| GitHub Token | `GITHUB_TOKEN` | ✅ Disponível no `.env` |
| ClickUp API | `CLICKUP_API_KEY` | ⚠️ Vazio — preencher em Settings → Apps → API Token |
| Leonardo AI | `LEONARDO_API_KEY` | ✅ Disponível no `.env` |
| Perplexity | `PERPLEXITY_API_KEY` | ✅ Disponível no `.env` |

### Trigger IDs (Claude Code)

Antes de importar o workflow, é preciso criar 3 scheduled triggers no Claude Code CLI:

```bash
# 1. Agente Criador
claude trigger create \
  --name "agente-criador-semanal" \
  --schedule "0 23 * * 0" \
  --prompt "Leia e execute o workflow em workflows/marketing/agente_criador_semanal.md"

# 2. Agente Revisor
claude trigger create \
  --name "agente-revisor-semanal" \
  --schedule "0 11 * * 1" \
  --prompt "Leia e execute o workflow em workflows/marketing/agente_revisor_semanal.md"

# 3. Agente de Ajustes
claude trigger create \
  --name "agente-ajustes-tempo-real" \
  --prompt "Leia o arquivo mais recente em pending-ajustes/. Identifique a tarefa e o ajuste pedido. Leia e siga o workflow em workflows/marketing/agente_ajustes_tempo_real.md para processar o pedido."
```

Após criar, copie os trigger IDs e substitua no workflow n8n:
- `TRIGGER_CRIADOR_ID` → ID do trigger 1
- `TRIGGER_REVISOR_ID` → ID do trigger 2
- `TRIGGER_AJUSTES_ID` → ID do trigger 3

---

## Importar Workflow

1. Abrir n8n no navegador
2. Menu → Workflows → Import from File
3. Selecionar: `tools/n8n_workflow_agentes_conteudo.json`
4. O workflow aparece com 3 fluxos:

```
Fluxo 1: ⏰ Domingo 20h BRT → 🤖 Agente Criador
Fluxo 2: ⏰ Segunda 8h BRT  → 🔍 Agente Revisor
Fluxo 3: 💬 Comentário ClickUp → 🧑 É o Lucas? → 📝 Preparar → 📁 GitHub → 🔧 Ajustes
```

---

## Configurar Credenciais no n8n

### 1. Variáveis de ambiente

Em n8n → Settings → Variables, adicionar:

| Variable | Value |
|----------|-------|
| `ANTHROPIC_API_KEY` | `sk-ant-api03-XiNQ...` (copiar do .env) |
| `GITHUB_TOKEN` | `ghp_owlm...` (copiar do .env) |

### 2. Credencial ClickUp

Em n8n → Credentials → New → ClickUp API:
- **API Token:** Pegar em ClickUp → Settings → Apps → Generate API Token
- Salvar e vincular ao nó "💬 Novo Comentário ClickUp"

---

## Substituir Placeholders

No workflow importado, substituir:

| Placeholder | Onde | Substituir por |
|-------------|------|----------------|
| `TRIGGER_CRIADOR_ID` | Nó "🤖 Agente Criador" → URL | ID retornado pelo `claude trigger create` |
| `TRIGGER_REVISOR_ID` | Nó "🔍 Agente Revisor" → URL | ID retornado pelo `claude trigger create` |
| `TRIGGER_AJUSTES_ID` | Nó "🔧 Agente Ajustes" → URL | ID retornado pelo `claude trigger create` |
| `CLICKUP_CREDENTIAL_ID` | Nó "💬 Novo Comentário ClickUp" | Selecionar a credencial criada |

---

## Testar

### Teste Fluxo 3 (Ajustes — mais fácil de testar)

1. Ativar o workflow no n8n
2. Ir ao ClickUp → abrir uma tarefa do cronograma
3. Adicionar um comentário: "Teste — ajusta o texto da abertura"
4. Verificar no n8n → Executions se o fluxo rodou
5. Verificar no GitHub se o arquivo apareceu em `pending-ajustes/`
6. Verificar se o agente Claude respondeu na tarefa

### Teste Fluxo 1 (Criador)

1. No nó "⏰ Domingo 20h BRT", clicar "Execute Node" manualmente
2. Verificar se o trigger Anthropic foi chamado
3. Verificar no ClickUp se as tarefas foram atualizadas

### Teste Fluxo 2 (Revisor)

1. Mesmo processo — executar manualmente o cron
2. Verificar se o agente revisou e mudou status

---

## Horários (fuso horário)

Os crons estão em **UTC**. BRT = UTC-3.

| Agente | Horário BRT | Cron UTC |
|--------|-------------|----------|
| Criador | Domingo 20:00 | `0 23 * * 0` |
| Revisor | Segunda 08:00 | `0 11 * * 1` |
| Ajustes | Tempo real | Trigger por webhook |

---

## Arquivos Relacionados

| Arquivo | Descrição |
|---------|-----------|
| `workflows/marketing/agente_criador_semanal.md` | SOP do agente criador |
| `workflows/marketing/agente_revisor_semanal.md` | SOP do agente revisor |
| `workflows/marketing/agente_ajustes_tempo_real.md` | SOP do agente de ajustes |
| `tools/n8n_workflow_agentes_conteudo.json` | Workflow n8n para importar |
| `brand-book/data/brand-data.yaml` | Dados NTICS (referência dos agentes) |
| `brand-book/02-identidade-verbal/tom-de-voz.md` | Tom de voz (referência dos agentes) |

---

## Fluxo Completo de Conteúdo Semanal

```
Domingo 20h    → Agente Criador gera 4 peças
                   ↓ status: "em produção"
Segunda 8h     → Agente Revisor checa tudo
                   ↓ status: "revisão" + comentário @Lucas
Lucas revisa   → Aprova ou comenta ajustes
                   ↓ comentário na tarefa
Tempo real     → Agente Ajustes lê, corrige, responde
                   ↓ loop até aprovação
Lucas aprova   → Status: "concluído"
                   ↓ conteúdo pronto para agendar
```
