# Workflow: Criar Site do Projeto

## Objetivo
Gerar site institucional do projeto no Lovable a partir da documentacao existente (briefing, TAP, KV), usando GitHub como ponte de assets entre o agente e o Lovable.

## Quando Executar
Quando o usuario pedir para criar o site de um projeto. Pre-requisito: tarefa "Criar Briefing do site" deve estar completa no ClickUp (ou o briefing pode ser gerado neste workflow usando `briefing_website.md`).

## Inputs Necessarios

| Input | Fonte | Obrigatorio |
|-------|-------|-------------|
| Nome ou ID do projeto | Usuario | Sim |
| Briefing do site | ClickUp (comentarios da task "Criar Briefing do site") | Sim |
| KV do projeto (imagem principal) | Google Drive (pasta Planejamento do projeto) | Sim |
| Logo do projeto | Google Drive (pasta Planejamento do projeto) | Recomendado |
| Regua de logos (patrocinadores) | Google Drive (pasta Planejamento do projeto) | Recomendado |
| Cores da marca do patrocinador | Briefing ou pesquisa (site do patrocinador) | Sim |
| Fotos do projeto | Google Drive (galeria) | Nao |

## Regras Criticas
- Nunca inventar dados. Se nao esta no briefing → marcar **PENDENTE** e perguntar ao usuario
- Prioridade: briefing do ClickUp para conteudo; Google Drive para assets visuais
- Todo texto deve ser linguagem externa (sem termos internos/operacionais)
- O HTML gerado e intermediario — o produto final e o site no Lovable
- GitHub e usado como repositorio de assets para o Lovable acessar
- Antes de gerar, validar com usuario todos os itens PENDENTE

## Documentos de Referencia

| Documento | Localizacao |
|-----------|-------------|
| Template HTML Jinja2 | `tools/templates/project_site.html` |
| Script de geracao | `tools/publishing/generate_project_site.py` |
| Dados dos projetos | `.tmp/sites/projects_data.json` |
| Briefing Website (SOP) | `workflows/escritorio-projetos/briefing_website.md` |
| Brand Book NTICS | `brand-book/` |
| Sites de referencia | Ver lista no Passo 6 |

---

## Passo a Passo

### Passo 1 — Localizar o Projeto no ClickUp

1. Buscar no ClickUp a pasta do projeto dentro de "Projetos Ativos"
2. Localizar as tarefas:
   - **"Criar Briefing do site"** — ler comentarios para extrair o briefing completo
   - **"Criar Site do projeto no Lovable"** — esta e a task que sera atualizada ao final
3. Extrair do briefing (comentarios da task):
   - Nome do projeto, periodo, cidades
   - Descricao geral (linguagem externa)
   - Atividades (nome + descricao de cada)
   - Democratizacao do acesso
   - Links de midia, galeria, KV, regua
   - Patrocinadores

**Se o briefing nao existir:** executar `workflows/escritorio-projetos/briefing_website.md` primeiro.

### Passo 2 — Coletar Assets Visuais no Google Drive

1. Acessar a pasta compartilhada dos projetos no Google Drive
2. Navegar ate a pasta do projeto → subpasta Planejamento
3. Localizar e registrar os IDs dos seguintes arquivos:

| Asset | Onde procurar | Formato esperado |
|-------|---------------|------------------|
| KV (Key Visual) | `{projeto}/Planejamento/KV*.pdf` ou `KV*.png` | PDF ou imagem |
| Logo do projeto | `{projeto}/Planejamento/Logo*.png` | PNG com transparencia |
| Regua de logos | `{projeto}/Planejamento/Regua*.png` ou `Barra*.png` | PNG |
| Fotos do projeto | `{projeto}/Fotos/` ou `{projeto}/Galeria/` | JPG/PNG |

4. Para cada arquivo encontrado, montar a URL de acesso:
   - Thumbnail: `https://lh3.googleusercontent.com/d/{FILE_ID}=w800`
   - Download: `https://drive.google.com/uc?export=download&id={FILE_ID}`

### Passo 3 — Verificar Completude dos Assets

Montar checklist e validar:

```
========================================
CHECKLIST DE ASSETS — {Nome do Projeto}
========================================
[x] Briefing do site (ClickUp)
[ ] KV do projeto (Google Drive) → {status: encontrado / PENDENTE}
[ ] Logo do projeto (Google Drive) → {status: encontrado / PENDENTE}
[ ] Regua de logos (Google Drive) → {status: encontrado / PENDENTE}
[ ] Cores do patrocinador (hex) → {status: definidas / PENDENTE}
[ ] Fotos do projeto → {status: X fotos encontradas / PENDENTE}
========================================
```

**→ PARADA 1: Se houver itens PENDENTE, apresentar a lista ao usuario e pedir os arquivos faltantes.**

Aguardar usuario fornecer ou confirmar que nao tem. Para itens que o usuario nao pode fornecer agora:
- KV ausente: usar placeholder com cores da marca
- Logo ausente: usar nome do projeto estilizado
- Regua ausente: listar nomes dos patrocinadores em texto
- Fotos ausentes: usar placeholders tematicos

### Passo 4 — Definir Identidade Visual do Site

Extrair ou pesquisar as cores da marca do patrocinador:

1. Se o briefing tem cores definidas → usar
2. Se nao, acessar o site do patrocinador (WebFetch) e extrair:
   - Cor primaria (accent)
   - Cor secundaria (accent dark)
   - Cores de fundo (gradiente hero)

Montar perfil visual:

```
PERFIL VISUAL — {Nome do Projeto}
================================================
Cor primaria (accent): {hex}
Cor secundaria (dark): {hex}
Fundo hero (start): {hex}
Fundo hero (end): {hex}
Patrocinador: {nome}
Lei Rouanet: {sim/nao}
================================================
```

### Passo 5 — Montar JSON do Projeto

Criar ou atualizar o arquivo `.tmp/sites/projects_data.json` com os dados extraidos.

Estrutura do objeto:

```json
{
  "id": "{numero}_{slug}",
  "project_name": "{nome completo}",
  "project_short_name": "{nome curto}",
  "hero_title": "{titulo do hero}",
  "tagline": "{frase de impacto}",
  "description": "{descricao geral — linguagem externa}",
  "sobre": "{dados de impacto, publico, metodologia}",
  "period": "{periodo de execucao}",
  "accent_color": "{hex primaria}",
  "accent_secondary": "{hex secundaria}",
  "hero_bg_start": "{hex fundo claro}",
  "hero_bg_end": "{hex fundo medio}",
  "kv_url": "https://lh3.googleusercontent.com/d/{KV_FILE_ID}=w800",
  "logo_url": "{URL do logo ou null}",
  "cities": [{"name": "Cidade/UF"}],
  "activities": [{"name": "...", "description": "..."}],
  "democratizacao": "{texto}",
  "sponsors": [{"name": "..."}],
  "has_lei_rouanet": true,
  "clickup_site_task_id": "{task_id}"
}
```

### Passo 6 — Gerar o HTML

Executar o script de geracao:

```bash
python tools/publishing/generate_project_site.py --data .tmp/sites/projects_data.json --project {id_do_projeto}
```

O HTML e gerado em `.tmp/sites/{id}.html`.

**Verificar o resultado:**
1. Servir localmente (HTTP server ou Preview)
2. Tirar screenshot e verificar:
   - Hero com KV como background
   - Cores da marca corretas
   - Todas as secoes preenchidas
   - Tipografia legivel
   - Mobile responsive

### Passo 7 — Subir Assets no GitHub

**Objetivo:** Criar um repositorio (ou branch) no GitHub com os assets do projeto para que o Lovable possa acessar diretamente.

#### 7.1 — Estrutura do repositorio

```
ntics-sites/
├── {slug-projeto}/
│   ├── index.html          ← HTML gerado no Passo 6
│   ├── assets/
│   │   ├── kv.jpg          ← Key Visual do projeto
│   │   ├── logo.png        ← Logo do projeto (se disponivel)
│   │   ├── regua.png       ← Regua de logos (se disponivel)
│   │   └── fotos/          ← Fotos do projeto (se disponiveis)
│   └── data.json           ← Dados do projeto (subset do JSON)
```

#### 7.2 — Comandos

```bash
# Clonar/atualizar repo
git clone https://github.com/{org}/ntics-sites.git .tmp/ntics-sites 2>/dev/null || cd .tmp/ntics-sites && git pull

# Criar pasta do projeto
mkdir -p .tmp/ntics-sites/{slug}/assets/fotos

# Copiar HTML
cp .tmp/sites/{id}.html .tmp/ntics-sites/{slug}/index.html

# Baixar e copiar assets do Google Drive
# (KV, logo, regua — usando URLs do Passo 2)

# Commit e push
cd .tmp/ntics-sites
git add {slug}/
git commit -m "site: {nome do projeto}"
git push
```

#### 7.3 — Verificar que os arquivos estao acessiveis

Testar URL raw do GitHub:
```
https://raw.githubusercontent.com/{org}/ntics-sites/main/{slug}/index.html
```

### Passo 8 — Criar Prompt para o Lovable

Montar prompt otimizado para o Lovable replicar o HTML:

```
Crie um site identico ao HTML que vou fornecer. O site e institucional
para o projeto "{nome do projeto}" da NTICS Projetos.

INSTRUCOES:
1. Replique EXATAMENTE o layout, cores, tipografia e estrutura do HTML
2. Use as mesmas fontes (Playfair Display + Inter via Google Fonts)
3. Use Tailwind CSS
4. Mantenha todas as animacoes de scroll (Intersection Observer)
5. Mantenha o header fixo com transparencia que muda ao scroll
6. Mantenha o menu mobile hamburger
7. As imagens estao hospedadas no Google Drive — mantenha as URLs

ASSETS NO GITHUB:
- Repositorio: https://github.com/{org}/ntics-sites/tree/main/{slug}
- HTML completo: {url_raw_html}
- KV: {url_kv}
- Logo: {url_logo}
- Regua: {url_regua}

CORES DA MARCA:
- Primaria: {accent_color}
- Secundaria: {accent_secondary}
- Fundo hero: gradiente de {hero_bg_start} a {hero_bg_end}

O HTML abaixo e o modelo completo. Replique fielmente:

[COLAR HTML AQUI]
```

**→ PARADA 2: Apresentar o prompt ao usuario para revisao antes de usar no Lovable.**

### Passo 9 — Criar no Lovable e Atualizar ClickUp

1. **Lovable:** Usuario cria o projeto no Lovable usando o prompt do Passo 8
2. **ClickUp:** Atualizar a task "Criar Site do projeto no Lovable":
   - Status → Completa
   - Comentario com URL do site no Lovable
   - Comentario com link do GitHub

---

## Output Esperado

| Entrega | Formato | Localizacao |
|---------|---------|-------------|
| HTML do site | Arquivo .html | `.tmp/sites/{id}.html` |
| JSON do projeto | Arquivo .json | `.tmp/sites/projects_data.json` |
| Assets no GitHub | Repositorio | `github.com/{org}/ntics-sites/{slug}/` |
| Prompt para Lovable | Texto | Entregue ao usuario |
| Site no Lovable | URL | `{slug}.lovable.app` |
| Task ClickUp atualizada | Status + comentario | ClickUp |

---

## Fluxo Resumido

```
Usuario pede "criar site do projeto X"
  │
  ├→ Passo 1: Localizar projeto no ClickUp (briefing + task)
  ├→ Passo 2: Coletar assets no Google Drive (KV, logo, regua, fotos)
  │
  ├→ Passo 3: Verificar completude → PARADA 1 (pedir o que falta)
  ├→ Passo 4: Definir identidade visual (cores, perfil)
  │
  ├→ Passo 5: Montar JSON do projeto
  ├→ Passo 6: Gerar HTML (Jinja2 + Tailwind)
  │
  ├→ Passo 7: Subir assets no GitHub
  ├→ Passo 8: Criar prompt para Lovable → PARADA 2 (revisao)
  │
  └→ Passo 9: Criar no Lovable + atualizar ClickUp
```

**Pontos de validacao (2 paradas):**
1. Apos checklist de assets (Passo 3) — pedir o que falta
2. Apos prompt do Lovable (Passo 8) — revisar antes de usar

---

## Processamento em Lote

Para criar multiplos sites de uma vez:

1. Executar Passos 1-3 para TODOS os projetos (coleta paralela)
2. Apresentar checklist consolidado ao usuario (1 parada para todos)
3. Executar Passos 4-6 para todos (geracao paralela)
4. Subir todos no GitHub em um unico commit
5. Gerar prompts individuais para cada projeto

---

## Conexao com Outros Workflows

| Workflow | Relacao |
|----------|---------|
| `briefing_website.md` | Gera o briefing que alimenta este workflow |
| `termo_abertura.md` | TAP e fonte de dados oficiais do projeto |
| `plano_divulgacao.md` | Plano gera releases e descricoes |
| `carrossel_projeto_cliente.md` | Mesmo input (projeto), formato diferente |
| `perfil_estrategico.md` | PEP ajuda a definir identidade visual |

---

## Especificacoes Tecnicas

| Elemento | Especificacao |
|----------|---------------|
| Template | Jinja2 (`tools/templates/project_site.html`) |
| CSS Framework | Tailwind CSS v3 (CDN) |
| Fontes | Playfair Display (titulos) + Inter (corpo) |
| Animacoes | Intersection Observer (reveal, fade, scale) |
| Responsivo | Mobile-first, hamburger menu |
| Imagens | Google Drive URLs (`lh3.googleusercontent.com/d/{ID}=w800`) |
| Hosting intermediario | GitHub (raw files) |
| Hosting final | Lovable (`{slug}.lovable.app`) |
| Script | `python tools/publishing/generate_project_site.py --data {json} [--project {id}]` |

---

## Checklist de Qualidade Final

- [ ] Briefing completo extraido do ClickUp
- [ ] KV do projeto visivel como hero background
- [ ] Cores da marca do patrocinador aplicadas corretamente
- [ ] Todas as atividades listadas com descricoes
- [ ] Cidades corretas
- [ ] Periodo correto
- [ ] Democratizacao do acesso descrita
- [ ] Patrocinadores + realizacao listados
- [ ] Responsivo (testar mobile)
- [ ] Animacoes de scroll funcionando
- [ ] GitHub com todos os assets
- [ ] Prompt do Lovable revisado pelo usuario
- [ ] Task do ClickUp atualizada com URL final
- [ ] Sem termos internos/operacionais no texto do site
