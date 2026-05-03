---
name: projeto-sync
description: "Força sincronização imediata do estado do projeto com ClickUp + Gmail (em vez de esperar o próximo SessionStart ou o cron). Roda o script projeto_sync.py e reporta eventos novos."
user-invocable: true
---

# /projeto-sync — Sync manual sob demanda

Use quando quiser puxar mudanças recentes do ClickUp + Gmail sem abrir nova sessão nem esperar o cron de 2h.

## Entrada

- `<slug>` — opcional. Se omitido e houver 1 só projeto ativo em `SecondBrain/projetos/INDEX.md`, usa esse automaticamente. Ex: `132-estacao-samarco`.

## Passos

1. Rodar no terminal:
   ```bash
   python "g:/O meu disco/Claude-NTICS-Projetos/tools/sync/projeto_sync.py" {slug}
   ```

2. **Ler stdout** do script. Se retornar "Sem mudanças desde último sync", reportar ao usuário: "nada novo desde última sincronização ({timestamp do cache})".

3. Se houver eventos, ler as últimas linhas de `SecondBrain/projetos/{slug}/comms/events.log` (equivalente ao que o script imprimiu) e resumir de forma executiva:
   - Quantos eventos de alta/média/baixa relevância
   - Principais ações sugeridas
   - Se alguma decisão foi capturada
   - Se algum blocker foi impactado (comparar com `state.yaml`)

4. **Se houver evento de alta relevância com ação sugerida urgente** (ex: reunião nas próximas 24h, aprovação solicitada, deadline próximo), destacar no topo da resposta.

5. Sugerir próxima ação ao usuário: `/projeto-status {slug}` para ver panorama completo, ou `/projeto-avanca {slug} {id}` se algum deliverable foi concluído.

## Regras

- **Não edite `events.log` ou `state.yaml` diretamente** — o script já faz isso. Esta skill é só o disparador + interpretação humana do output.
- Se o script falhar (credenciais, rede), reportar o erro stderr mas não falhar a sessão.
- Se `--dry-run` for pedido pelo usuário ("testa sem escrever"), adicionar a flag no comando.
