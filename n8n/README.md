# n8n Workflows

Automações da NTICS construídas na plataforma n8n.

## Como importar

1. Abrir n8n (`http://localhost:5678` ou instância cloud)
2. Menu → Workflows → Import
3. Selecionar o arquivo `.json` desta pasta

## Convenção de nomes

```
n8n_workflow_{area}_{descricao}.json
```

## Workflows

| Arquivo | Descrição | Status |
|---|---|---|
| [n8n_workflow_agentes_conteudo.json](n8n_workflow_agentes_conteudo.json) | Agentes semanais de criação de conteúdo (domingo 20h + segunda 8h) | Ativo |
| [n8n_workflow_fluxo3_ajustes.json](n8n_workflow_fluxo3_ajustes.json) | Fluxo 3 — ajustes em tempo real via ClickUp | Ativo |
| [n8n_workflow_publicador.json](n8n_workflow_publicador.json) | Publicação LinkedIn automática ao aprovar no ClickUp | Novo |

## Relação com Skills e Agentes

Os workflows n8n orquestram as skills e tools Claude:
- `agentes_conteudo` → invoca `/agente-criador-semanal` e `/agente-revisor-semanal`
- `fluxo3_ajustes` → invoca `/agente-ajustes-tempo-real`
- `publicador` → webhook ClickUp (status "aprovado") → posta no LinkedIn → atualiza status para "publicado"

Ver SOP: [workflows/marketing/agentes/agente_publicador.md](../workflows/marketing/agentes/agente_publicador.md)
