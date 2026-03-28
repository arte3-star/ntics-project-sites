---
name: criar-site
description: "Cria site institucional do projeto no Lovable a partir do briefing do ClickUp, assets do Google Drive e template HTML (Tailwind + Jinja2)"
user-invocable: true
---

Leia e execute o workflow completo em `workflows/escritorio-projetos/criar_site_projeto.md`.

## Inputs

**Minimos (obrigatorios):**
1. **Nome ou ID do projeto** no ClickUp
2. **Briefing do site** (extraido dos comentarios da task "Criar Briefing do site" no ClickUp)

**Opcionais (melhoram o resultado):**
- KV do projeto (Google Drive)
- Logo do projeto (PNG transparente)
- Regua de logos dos patrocinadores
- Cores da marca do patrocinador (hex)
- Fotos do projeto

## Ferramentas Disponiveis

| Ferramenta | Arquivo | Funcao |
|-----------|---------|--------|
| Gerador de sites | `tools/generate_project_site.py` | Renderiza HTML via Jinja2 + Tailwind |
| Template HTML | `tools/templates/project_site.html` | Template Jinja2 com design avancado |
| Dados dos projetos | `.tmp/sites/projects_data.json` | JSON com dados de todos os projetos |

## Fontes de Dados

| Dado | Fonte | Como acessar |
|------|-------|--------------|
| Briefing | ClickUp | `clickup_get_task_comments` na task "Criar Briefing do site" |
| KV / Logo / Regua | Google Drive | `google_drive_search` na pasta do projeto |
| Cores da marca | Site do patrocinador | `WebFetch` no site da empresa |
| Task para atualizar | ClickUp | `clickup_search` por "Criar Site do projeto no Lovable" |

## Fluxo

Comece pelo Passo 1 (localizar projeto no ClickUp) e siga com as 2 paradas de validacao:
1. Apos checklist de assets (Passo 3) — pedir o que falta ao usuario
2. Apos prompt do Lovable (Passo 8) — revisar antes de usar

## Processamento em Lote

Para criar multiplos sites de uma vez, executar Passos 1-3 em paralelo para todos os projetos, consolidar checklist de pendencias, e depois gerar todos os HTMLs juntos.

## Sites de Referencia (Lovable)

- circo-no-brasil.lovable.app
- festival-de-circo.lovable.app
- museu-intinerante.lovable.app
- festivalcine.lovable.app
- programa-das-artes-literarias.lovable.app
- cultura-na-comunidade.lovable.app
- teatro-nas-escolas-objetivo-de-desenvol-sust.lovable.app
