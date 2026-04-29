---
name: criar-landing-ntics
description: "Cria landing page de projeto NTICS em ntics.com.br/{slug}/ a partir de site Renderforest (ou de assets+scrape existentes). Pipeline completo: scrape RF → organiza assets → gera HTML fiel → upload via Code Snippets API."
user-invocable: true
---

Você é o construtor de landing pages do **ntics.com.br**. Usa o fluxo abaixo para toda criação/manutenção de landing page de projeto ativo.

## Quando usar

- Migrar site Renderforest (`*.renderforestsites.com`) para `ntics.com.br/{slug}/`
- Republicar landing page de projeto ativo com cores + fotos + vídeo + régua
- Atualizar landing existente (rodar o pipeline de novo sobrescreve)

## Stack & Arquitetura

| Parte | Tecnologia |
|---|---|
| Infra | Apache + WordPress (tema Uncode) em hostserver.com.br (OLI) |
| Bypass WP | Arquivos `index.html` físicos no filesystem servem direto via Apache |
| Upload | REST API custom via Code Snippet id=6 (`/wp-json/nticsfiles/v1/write`) |
| Tema | Tailwind CDN + Poppins (inline), sem dependência do tema WP |
| Autenticação | `WP_USER` + `WP_APP_PASSWORD` no `.env` (Basic Auth) |

## Pré-requisitos

1. `.env` tem `WP_URL`, `WP_USER`, `WP_APP_PASSWORD` configurados
2. Code Snippet id=6 "NTICS File Operations REST API" ativo em ntics.com.br/wp-admin (endpoints `/nticsfiles/v1/write`, `/mkdir`, `/ls`)
3. Chrome aberto com porta 9222 debug E logado no Renderforest (se for scrape novo)

## Pipeline completo

```
URL Renderforest
   │
   ▼
[1] tools/migration/organize_all_assets.py (ou scrape_rf_v2.py se for novo)
   │  → assets/projetos/{N}. NOME/
   │    ├── FOTOS/ (todas as fotos do RF, nomes rf-{site_id}-{hash}.ext)
   │    ├── LOGOS/ (logo do projeto)
   │    ├── REGUAS/ (régua de patrocinadores, nome regua_{hash}.jpg)
   │    ├── cores.json (extraídas do CSS do RF)
   │    └── section_map.json (mapeamento seção → fotos do RF)
   │
   ▼
[2] tools/migration/generate_all_final.py
   │  → assets/projetos/{N}. NOME/index.html (HTML fiel ao RF)
   │
   ▼
[3] tools/migration/upload_ntics.py --only {N}
   │  → ntics.com.br/{slug}/index.html + FOTOS/ + LOGOS/ + REGUAS/
   │
   ▼
[4] tools/migration/_review_live.py
   │  → verifica fotos quebradas, tamanho logo hero, tamanho régua
```

## Regras obrigatórias (aprendidas em produção)

### Layout de fotos

1. **Galeria** ≠ **grids temáticos**: no RF algumas páginas têm 4 grids de 8 fotos quadradas (exposição) + 1 galeria com 7 fotos em masonry. Não misturar os dois.
2. **Logo fora da galeria**: logo só em header + Sobre, NUNCA em galeria.
3. **Régua fora da galeria**: régua só no footer (hash identificada em `REGUAS/regua_*`), filtrar por hash no gerador.
4. **Fotos únicas**: cada foto aparece 1x apenas na página inteira (o gerador faz merge de seções sem título e marca `used_in_sections`).

### Cores

5. Cada projeto tem cores próprias extraídas do CSS do RF (headings + buttons). Nunca hardcode.
6. `cores.json` traz `primary`, `secondary`, `dark`, `light`, `source: renderforest_css`.

### Vídeo

7. Quase todos os RF têm YouTube embed — extraído do **editor RF logado** (URL `https://www.renderforest.com/website-maker/{rf_id}/lang/edit`), não do site público (que usa componente dinâmico).
8. IDs salvos em `section_map.json['youtube_ids']` e renderizados na seção Democratização.

### Estrutura visual

9. **Hero logo** deve ser `h-40 md:h-56 lg:h-64` (160-256px) — não menor.
10. **Footer régua** deve ser `max-w-6xl` (1152px) — não `max-w-4xl`.
11. **Títulos MINISTÉRIO DA CULTURA APRESENTA:** ignorar, pegar próxima linha como título real.
12. **Sections sem título consecutivas** (ex: 87 tem 4 grids sem título) → merge no anterior.

### Upload

13. **Paths relativos no HTML publicado** (não GitHub raw) — o `upload_ntics.py` faz replace automático do `gh_base` antes de subir.
14. **Re-upload sobrescreve**: rodar `upload_ntics.py --only N` pode falhar no meio por timeout SSL, basta rerodar que pula os arquivos já uploadados (API aceita sobrescrever).
15. **Fotos quebradas**: se `_review_live.py` reportar imgs broken, baixar do RF via `hosting.renderforestsites.com/24321761/{rf_id}/media/{hash}.jpg` e re-upload.

## Fluxo típico

### Criar nova landing
```bash
# 1. Adicionar projeto em tools/migration/sites_pendentes.json com rf_url, subdomain, etc.

# 2. Scrape + organize
python tools/migration/organize_all_assets.py
python tools/migration/extract_rf_colors.py
python tools/migration/find_reguas.py

# 3. Extrair vídeos do editor RF (usuário precisa estar logado no Chrome CDP)
# Já coberto pelo organize_all_assets.py

# 4. Gerar HTML
python tools/migration/generate_all_final.py

# 5. Upload
python tools/migration/upload_ntics.py --only {N}

# 6. Verificar
python tools/migration/_review_live.py
```

### Atualizar landing existente
```bash
# Editar assets ou gerador, então:
python tools/migration/generate_all_final.py
python tools/migration/upload_ntics.py --only {N}
python tools/migration/_review_live.py
```

### Verificação obrigatória antes de declarar "feito"

- [ ] `_review_live.py` reporta `broken imgs: 0` para o projeto
- [ ] Hero logo `h >= 200px` (não pequeno)
- [ ] Footer régua `w >= 1100px` (não pequeno)
- [ ] Vídeo YouTube embed presente se RF tinha
- [ ] URL `https://ntics.com.br/{slug}/` retorna 200 OK sem conteúdo do tema WP

## 9 sites ativos

| # | Projeto | URL |
|---|---|---|
| 86 | Teatro dos Bons Hábitos | https://ntics.com.br/teatro-dos-bons-habitos-ferroporte/ |
| 87 | Exposição Culinária Sustentável | https://ntics.com.br/exposicao-culinaria-sustentavel-imetame/ |
| 82 | Robótica Cultural nas Escolas | https://ntics.com.br/robotica-cultural-nas-escolas/ |
| 89 | Oficina de Teatro Sustentável | https://ntics.com.br/oficina-teatro-sustentavel-ferroport/ |
| 91 | Teatro dos ODS | https://ntics.com.br/teatro-dos-ods/ |
| 98 | Conhecendo os ODS | https://ntics.com.br/conhecendo-os-ods/ |
| 104 | PEC 3ª Edição | https://ntics.com.br/pec-3aed-porto-itapoa/ |
| 106 | Teatro Robótica 2ªED | https://ntics.com.br/teatro-oficina-robotica-2aed-cnh/ |
| 110 | Caminhão da Cultura | https://ntics.com.br/caminhao-cultura-sustentabilidade-jaepel/ |

## Code Snippet PHP (referência)

O snippet id=6 está ativo em ntics.com.br. Se precisar recriar:
- Endpoint `POST /wp-json/nticsfiles/v1/write` — params: `path`, `content`, `base64` (boolean)
- Endpoint `POST /wp-json/nticsfiles/v1/mkdir` — param: `path`
- Endpoint `GET /wp-json/nticsfiles/v1/ls?path=` — lista diretório
- Permission: `current_user_can('manage_options')` — só admin
- Base: `ABSPATH` (raiz do WordPress, dentro de `/home/ntics/domains/ntics.com.br/public_html/`)

## Documento de aprendizados

Ver `workflows/marketing/referencia/criar_landing_ntics.md` para o registro completo dos erros cometidos e como evitá-los.
