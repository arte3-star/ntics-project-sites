# Auto-sync por projeto (Opção D)

Roda automaticamente no SessionStart do Claude Code em projects-os. Puxa estado do ClickUp, diffa contra cache, só invoca LLM (Haiku) quando há delta real.

## O que faz

1. Lê `projects/{slug}/tasks.yaml` → pega `task_mae.id` (ex: 868j96x17 para 132)
2. Puxa via ClickUp API: task-mãe + subtasks + comentários
3. Compara contra `projects/{slug}/.cache/clickup-snapshot.json`
4. **Se nada mudou:** atualiza timestamp no cache e sai. **Custo LLM = 0.**
5. **Se mudou:** manda o delta + contexto resumido do state.yaml para Haiku classificar (relevância, deliverable afetado, ação sugerida, decisão capturada)
6. Escreve eventos em `projects/{slug}/comms/events.log`

## Uso manual

```bash
# Sync padrão
python tools/sync/projeto_sync.py 132-samarco

# Dry-run (não grava cache nem log)
python tools/sync/projeto_sync.py 132-samarco --dry-run

# Output JSON (para integrar com outros scripts)
python tools/sync/projeto_sync.py 132-samarco --json --quiet
```

## Requisitos

- `.env` em `../AUTOMAÇÕES/.env` com `CLICKUP_API_KEY` e `ANTHROPIC_API_KEY` (já existe)
- Python 3.10+
- Pacotes: `requests`, `python-dotenv`, `pyyaml` (já vêm no venv de AUTOMAÇÕES)

## Custo real esperado (132-samarco)

- **Check sem delta** (95% dos dias enquanto o projeto está pré-kickoff): 2 chamadas HTTP ClickUp, 0 tokens LLM. **$0.**
- **Check com delta típico** (1-3 mudanças): ~2k tokens input Haiku + ~500 tokens output. **~$0.002/invocação.**
- **Dia ativo** (10 mudanças): ~5k input + 1.5k output. **~$0.007.**

Com SessionStart (abrindo projects-os ~5 vezes/dia): **<$1/mês** na fase atual do projeto.

Quando o projeto entrar em execução em 12 cidades com chat ativo diário, custo deve subir para **$3-8/mês**. Se virar problema, a Opção C (cron 2h com diff incremental) fica como upgrade natural.

## Quando NÃO rodar

- Hook falha silenciosamente (`|| echo ...`) para não bloquear session start.
- Se `.env` não tiver as keys, o script sai com erro mas a sessão Claude Code continua normal.
- `--dry-run` útil para debugar sem poluir o log.

## Gmail integration (ativa)

O script puxa threads Gmail cuja query está definida em `projects/{slug}/tasks.yaml` no campo `gmail_query`. Usa o auth OAuth já configurado em `AUTOMAÇÕES/tools/gws/token.json` (via `gws_auth.get_credentials()`).

Query atual do 132:
```
(from:samarco.com OR to:samarco.com OR subject:"Estação Samarco" OR subject:"132") newer_than:7d
```

Ajuste essa query se quiser capturar outros domínios/assuntos.

## Cron 2h (Windows Scheduled Task)

Para ativar a sincronização periódica além do SessionStart, rode **uma vez** no PowerShell:

```powershell
cd "g:\O meu disco\projects-os"
.\tools\sync\register_cron_windows.ps1
```

Isso registra uma task Windows que roda a cada 120 min. Logs em `projects/132-samarco/.cache/cron.log`.

Para remover:
```powershell
schtasks /Delete /TN "NTICS-projeto-sync-132-samarco" /F
```

## Próximas evoluções (TODO)

- **ClickUp chat da lista 132:** endpoint `clickup_get_chat_channel_messages` via MCP já existe mas não via API REST direta — migrar quando precisar.
- **Decisões capturadas vão para SecondBrain:** hoje só ficam em `events.log`. Próximo passo: append em `AUTOMAÇÕES/SecondBrain/projetos/132-estacao-samarco/execucao.md`.
- **Telemetria de custo:** logar tokens consumidos Haiku em `.cache/cost.log` para monitorar se o custo estimado ($3-8/mês) bate com a realidade.
