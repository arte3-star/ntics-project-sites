# Workflow: Publicar output final no Drive

Sobe pastas de `output/marketing/` pra `Marketing/2026/` no Google Drive após aprovação visual do Lucas.

## Quando disparar

- Após o Lucas sinalizar "aprovado", "pode subir", "publica"
- Nunca antes da revisão visual (a skill não substitui validação)

## Estrutura alvo no Drive

```
Marketing/2026/
├── 1. REDES SOCIAIS/{CARROSSEIS,POSTS,STORIES,REELS}/
├── 2. WEBSITE/{ARTIGOS BLOG,LANDING PAGES}/
├── 3. EMAIL/NEWSLETTERS/
├── 4. VIDEOS/{CASES,PRE-PROJETO,INSTITUCIONAL}/
├── 5. IMPRESSOS/
├── 6. APRESENTACOES/
├── 7. DESIGN ASSETS/{ASSINATURAS,FRAMES,ICONES,REGUAS}/
└── _ARQUIVO/
```

Folder ID raiz: `1mOX2HbTfM30WV1umXOu4gfrYV5WZdJEU`.

## Passos

### 1. Confirmar que o material está aprovado
Pergunte ao Lucas explicitamente se não estiver claro. Não publique rascunhos.

### 2. Conferir que a pasta local segue convenção
```
output/marketing/{categoria}/{subcategoria}/{nome-peca}/
```

Ex válidos:
- `output/marketing/carrosseis/cases/2026-04-23_samarco-estacao/`
- `output/marketing/artigos/2026-04-23_gamification-csr/`
- `output/marketing/newsletters/2026-04_abril/`

### 3. Rodar a skill/tool
```bash
python tools/integrations/publicar_drive.py \
  --source output/marketing/carrosseis/cases/samarco-estacao/
```

A saída traz:
- Path resolvido no Drive
- Quantidade de arquivos enviados
- Link webViewLink da pasta criada

### 4. Verificar (obrigatório)
- Abrir `webViewLink` e confirmar visualmente
- Se falhar, ver `.tmp/drive_publish_log.jsonl` pro último registro

### 5. Anexar link no ClickUp (se aplicável)
Se a peça tem task no ClickUp, atualizar a descrição com o link Drive. Para fluxos existentes, usar [`update_clickup_drive_links.py`](../../tools/integrations/update_clickup_drive_links.py).

## Quando o mapeamento automático não serve

Use `--dest` com caminho manual:
```bash
python tools/integrations/publicar_drive.py \
  --source output/marketing/especial/projeto-X/ \
  --dest "1. REDES SOCIAIS/CARROSSEIS/CLIENTES/projeto-X-custom"
```

## Recuperação de erros

- **Auth falhou** → apagar `tools/gws/token_drive.json` e rodar de novo pra reautenticar
- **Pasta existe no Drive com mesmo nome** → o script é idempotente; re-upload pula arquivos duplicados
- **Path não resolve** → adicionar novo mapeamento em `MAPPING` em [publicar_drive.py](../../tools/integrations/publicar_drive.py) ou usar `--dest`

## Setup inicial (one-shot, já executado em 2026-04-23)

Estes são os scripts que montaram a estrutura atual. Não precisa rodar de novo:

1. `drive_2026_discover.py` — inventário read-only → `.tmp/drive_2026_inventory.json`
2. `drive_2026_scaffold.py` — cria pastas 1-7 + `_ARQUIVO` → `.tmp/drive_2026_folder_map.json`
3. `drive_2026_reorg.py --dry-run` → preview de movimentos
4. `drive_2026_reorg.py` → executa movimentos → `.tmp/drive_2026_reorg_log.json`

Se precisar recriar do zero em outra pasta (ex: `Marketing/2027/`), rodar na ordem acima com `--root-id <novo_id>`.
