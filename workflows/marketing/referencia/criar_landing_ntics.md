# Criar Landing Page no site NTICS — Guia de Aprendizados

Documento vivo com os erros cometidos na criação das 9 landing pages de projetos RF→NTICS (abril 2026) e como evitá-los. Use junto com `/criar-landing-ntics`.

## Contexto

Em abril/2026 migramos 9 landing pages de Renderforest (`*.renderforestsites.com`) para `ntics.com.br/{slug}/`. Fizemos três tentativas antes de acertar:

1. **Tentativa 1 — Lovable**: Construímos via IA no Lovable. Ficou com visual idêntico em todos (hardcoded), galeria com logo/régua sobreposta, fotos duplicadas.
2. **Tentativa 2 — WordPress page**: Publicamos como `wp/v2/pages` no ntics.com.br. Apareceu com header/footer do tema em volta. Não dá para mudar template via REST API.
3. **Tentativa 3 — HTML estático via Code Snippets** (✅ funcionou): Criei um endpoint REST customizado no WP via Code Snippets que escreve arquivos físicos. Apache serve `index.html` direto, bypass do WordPress.

---

## Erros cometidos e como evitar

### 1. Assumir estrutura de fotos sem ler o DOM do original

**O que aconteceu**: Joguei 32 fotos da "Exposição Culinária" (4 grids de 8) na galeria final, que no RF só tem 7 fotos. Layout ficou irreconhecível.

**Por que**: Template genérico que tratava todas as fotos como "galeria", sem entender que o RF tem grids temáticos separados.

**Como evitar**:
- Sempre rodar `organize_all_assets.py` que mapeia **seção → fotos** via DOM do RF
- Respeitar a distinção: grids temáticos (quadrados, 4xN) ≠ galeria final (masonry, poucas fotos)
- `section_map.json` é fonte da verdade, não hardcode

### 2. Mesmas cores em todos os sites

**O que aconteceu**: Todos os 9 sites saíram com `#1E3A8A` azul + `#E91E63` magenta hardcoded.

**Por que**: Gerador HTML tinha cores no `<style>` em vez de ler de `cores.json`.

**Como evitar**:
- `extract_rf_colors.py` extrai cores reais dos headings do RF
- Cada projeto tem `cores.json` com `primary`, `secondary`, `dark`, `light`
- Gerador lê `colors` e injeta como inline style

### 3. Digitar nomes de arquivo manualmente no HTML

**O que aconteceu**: Digitei hashes como `rf-1316311-78f905eba4d700e077ed64ecd66e4a83.jpg` no HTML manualmente. Alguns não existiam no GitHub → imagens quebradas.

**Por que**: Hashes longos de 32 chars são impossíveis de digitar sem erro.

**Como evitar**:
- **Nunca** digitar filenames no HTML
- Sempre ler do filesystem via `os.listdir()` ou `Path.iterdir()`
- `_review_live.py` reporta `broken imgs` para detectar essa classe de bug

### 4. Logo e régua na galeria de fotos

**O que aconteceu**: O hash da régua (`regua_XXXXX.jpg`) aparecia também como foto na galeria, resultando em uma imagem 2200x700 gigante no meio da galeria.

**Por que**: Filtro ingênuo `if 'logo' in filename` não pegava réguas cujo filename só tinha hash.

**Como evitar**:
- Função `is_regua(filename, regua_hashes)` checa: `'regua' in filename.lower()` OR hash da pasta REGUAS está contido no filename
- `get_regua_hashes(project_num)` lê a pasta `REGUAS/` e retorna set de hashes para filtro

### 5. Ignorar seção "Democratização de Acesso" e vídeos

**O que aconteceu**: Omiti a seção de vídeo em todos os projetos. Lucas corrigiu: "quase todos têm vídeo embutido".

**Por que**: O site público do RF não mostra o iframe YouTube (é carregado dinamicamente), só mostra o placeholder SVG decorativo. Meu scraper não detectava vídeo.

**Como evitar**:
- **Vídeos do RF só aparecem no editor logado** (URL `https://www.renderforest.com/website-maker/{rf_id}/lang/edit`)
- `organize_all_assets.py` navega para o editor e extrai `youtube.com/embed/{id}` do HTML
- Salva em `section_map.json['youtube_ids']`
- Gerador renderiza iframe na seção Democratização

### 6. Título "O MINISTÉRIO DA CULTURA APRESENTA:" como hero title

**O que aconteceu**: Projetos 89, 98, 110 tinham `h1` começando com "O MINISTÉRIO DA CULTURA APRESENTA:\nCaminhão da Cultura..." e meu split pegava só a primeira linha, resultando em título errado.

**Como evitar**:
```python
parts = [p.strip() for p in hero_title_raw.split('\n') if p.strip()]
if parts and 'MINISTÉRIO DA CULTURA' in parts[0].upper():
    hero_title = parts[1] if len(parts) > 1 else nome
else:
    hero_title = parts[0] if parts else nome
```

### 7. Sections sem título ficando órfãs no HTML

**O que aconteceu**: Projeto 87 tem seções 5-8 no RF onde só a 5 tem título ("EXPOSIÇÃO CULINÁRIA SUSTENTÁVEL") e 6, 7, 8 são continuação sem título. Meu gerador as tratava como sections separadas, gerando 4 áreas vazias com fotos.

**Como evitar**:
```python
merged_sections = []
for s in sections:
    if not s['title'].strip() and (s['imgs'] or s['bgs']) and merged_sections and merged_sections[-1]['title'].strip():
        merged_sections[-1]['imgs'].extend(s['imgs'])
        merged_sections[-1]['bgs'].extend(s['bgs'])
    else:
        merged_sections.append({**s})
```

### 8. Tema WordPress "vazava" em volta do HTML

**O que aconteceu**: Criei `wp/v2/pages` com HTML completo. O tema Uncode NTICS adicionou header + footer próprio em volta.

**Por que**: Template de página requer `page-template-elementor_header_footer` mas o REST API bloqueia mudança de template (`rest_invalid_param`).

**Como evitar**: Publicar como **arquivo físico** no filesystem:
- Endpoint PHP customizado via Code Snippets
- `file_put_contents($full_path, $content)` escreve em `ABSPATH/{slug}/index.html`
- Apache serve o arquivo direto, WordPress nem é chamado
- **Não usa** `wp/v2/pages`

### 9. Logo pequena no hero e régua pequena no footer

**O que aconteceu**: Versão inicial tinha `h-28 md:h-36` (112-144px) para logo hero e `max-w-4xl` (896px) para régua — parecia apertado em telas >= 1440px.

**Como evitar**: Valores finais validados:
- Hero logo: `h-40 md:h-56 lg:h-64` (160-256px)
- Footer régua: `max-w-6xl` (1152px)

### 10. Upload SSL timeout no meio

**O que aconteceu**: Upload de muitos arquivos em sequência causou timeout SSL, crashou no projeto 98/110.

**Como evitar**:
- `--only N` permite re-rodar só o que falhou
- API aceita sobrescrever arquivo existente (idempotente)
- Não interromper: deixar rodar, depois checar o que falta via `_review_live.py`

### 11. Scrapear fotos do RF público só por `<img>` tags

**O que aconteceu**: RF usa lazy-load + bg-images. `<img>` iniciais têm `src=""` até aparecerem no viewport.

**Como evitar**:
- Scroll completo com `page.mouse.wheel(0, 300)` em loops
- Aguardar `networkidle` após scroll
- Capturar também `background-image` via `getComputedStyle`
- Enviar `Referer` header no download (senão RF bloqueia com 403)

---

## Verificação obrigatória antes de declarar "feito"

Rode `tools/migration/_review_live.py` e confirme:

- [ ] `broken imgs: 0` para todos os projetos
- [ ] `hero logo: >= 200px altura`
- [ ] `footer regua: >= 1100px largura`
- [ ] URL retorna HTTP 200
- [ ] Curl do HTML não mostra `<header class="site-header">` ou `<footer id="colophon">` (tema WP)

Se algum falhar, volte ao erro correspondente acima.

---

## Ferramentas de referência

| Script | Função |
|---|---|
| `tools/migration/organize_all_assets.py` | Scrape RF + download fotos + mapeia seções |
| `tools/migration/extract_rf_colors.py` | Extrai cores CSS reais do RF |
| `tools/migration/find_reguas.py` | Detecta régua por aspect ratio >= 2.5 |
| `tools/migration/generate_all_final.py` | Gera HTML fiel ao RF usando section_map |
| `tools/migration/upload_ntics.py` | Upload via REST API custom |
| `tools/migration/_review_live.py` | Verificação visual pós-deploy |

## Skill relacionada

`/criar-landing-ntics` — ponto de entrada para qualquer criação/atualização nova.
