---
name: publicar-drive
description: Publica output final aprovado de marketing no Google Drive em Marketing/2026, com estrutura organizada por categoria (REDES SOCIAIS, WEBSITE, EMAIL, VIDEOS, IMPRESSOS, APRESENTACOES, DESIGN ASSETS). Usar somente depois que o material foi validado visualmente pelo Lucas. Aceita --source apontando para pasta em output/marketing/ e resolve destino automaticamente.
---

# Publicar Drive

Sobe output final aprovado para `Marketing/2026/` no Drive compartilhado (ID `1mOX2HbTfM30WV1umXOu4gfrYV5WZdJEU`).

## Quando usar

- Lucas disse "aprovado", "pode subir", "publica" ou equivalente
- Peça foi revisada visualmente (carrossel/post/vídeo/etc.)
- Artefato está em `output/marketing/<categoria>/<projeto-ou-data>/`

**NÃO usar** se o material ainda está em rascunho ou aguardando revisão.

## Como chamar

```bash
python tools/integrations/publicar_drive.py --source output/marketing/<path>/
```

Exemplo real:
```bash
python tools/integrations/publicar_drive.py --source output/marketing/carrosseis/cases/samarco-estacao/
```

O script resolve o destino automaticamente via `MAPPING` em [publicar_drive.py](../../../tools/integrations/publicar_drive.py).

## Mapeamento local → Drive

| Local (`output/marketing/...`)  | Drive (`2026/...`)                          |
|---------------------------------|---------------------------------------------|
| `carrosseis/cases/`             | `1. REDES SOCIAIS/CARROSSEIS/CASES/`        |
| `carrosseis/noticias/`          | `1. REDES SOCIAIS/CARROSSEIS/NOTICIAS/`     |
| `carrosseis/educacional/`       | `1. REDES SOCIAIS/CARROSSEIS/EDUCATIVOS/`   |
| `carrosseis/clientes/`          | `1. REDES SOCIAIS/CARROSSEIS/CLIENTES/`     |
| `posts-avulsos/` ou `posts/`    | `1. REDES SOCIAIS/POSTS/`                   |
| `stories/`                      | `1. REDES SOCIAIS/STORIES/`                 |
| `reels/`                        | `1. REDES SOCIAIS/REELS/`                   |
| `artigos/`                      | `2. WEBSITE/ARTIGOS BLOG/`                  |
| `sites/`                        | `2. WEBSITE/LANDING PAGES/`                 |
| `newsletters/`                  | `3. EMAIL/NEWSLETTERS/`                     |
| `videos/cases/`                 | `4. VIDEOS/CASES/`                          |
| `videos/pre-projeto/`           | `4. VIDEOS/PRE-PROJETO/`                    |
| `videos/institucional/`         | `4. VIDEOS/INSTITUCIONAL/`                  |
| `impressos/`                    | `5. IMPRESSOS/`                             |
| `apresentacoes/`                | `6. APRESENTACOES/`                         |

## Convenção de nome da subpasta final

- Com projeto: `{YYYY-MM-DD}_{projeto-slug}_{peca}/` — ex: `2026-04-23_samarco-estacao_carrossel-case/`
- Notícias semanais: `semana-S{NN}/` — ex: `semana-S17/`
- Post único: `{slug-do-post}/`

Se a pasta local já segue o padrão, o script replica o nome como está.

## Verificação pós-publicação

Depois de rodar o script:
1. O link retornado deve estar em `.tmp/drive_publish_log.jsonl` (última linha)
2. Abrir o `webViewLink` e confirmar que os arquivos subiram
3. Se a skill da peça (ex: `carrossel-case`) tiver integração com ClickUp, anexar o link na task

## Override manual

Se o mapeamento automático não funcionar ou você quiser caminho custom:
```bash
python tools/integrations/publicar_drive.py \
  --source output/marketing/algum-path/ \
  --dest "1. REDES SOCIAIS/CARROSSEIS/CASES/nome-custom"
```

## Scripts relacionados

- [drive_2026_discover.py](../../../tools/integrations/drive_2026_discover.py) - inventário read-only da pasta 2026
- [drive_2026_scaffold.py](../../../tools/integrations/drive_2026_scaffold.py) - cria/garante estrutura padrão
- [drive_2026_reorg.py](../../../tools/integrations/drive_2026_reorg.py) - reorganiza conteúdo existente (one-shot)
- [upload_to_drive.py](../../../tools/integrations/upload_to_drive.py) - helper base de upload (usado por publicar_drive)

## Workflow completo

Ver [workflows/marketing/publicar_drive.md](../../../workflows/marketing/publicar_drive.md)
