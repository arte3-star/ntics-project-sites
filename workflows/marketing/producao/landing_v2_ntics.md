# Landing Page v2 — NTICS (sem Renderforest)

Workflow para criar landing pages de projeto NTICS publicadas em `ntics.com.br/{slug}/`,
sem dependência do Renderforest. Claude escreve o HTML diretamente, guiado pelas skills
`/frontend-design` e `/ui-ux-pro-max`.

**Fallback:** se algo falhar, usar `/criar-landing-preprojeto` (pipeline Python + Lovable).

## Quando usar

- Projeto novo sem site no Renderforest
- RF não está mais disponível como fonte
- Quer resultado visual acima do padrão RF-origin
- Projeto pre-execução OU pós-execução (com ou sem fotos próprias)

## Pré-requisitos

1. `.env` com `WP_URL`, `WP_USER`, `WP_APP_PASSWORD`
2. Code Snippet id=6 ativo em ntics.com.br/wp-admin
3. `assets/projetos/{N}/LOGOS/` com logo do projeto (PNG transparente)
4. `assets/projetos/{N}/REGUAS/` com régua de patrocinadores

## Pipeline

```
ClickUp (briefing + atividades + titulo)
   +
SecondBrain/projetos/{slug}/assets/ (logo, regua, fotos se existirem)
   +
SecondBrain/banco-fotos/{categoria}/ (banco generico se sem fotos proprias)
   │
   ▼
[1] Coletar conteudo (ClickUp)
   │
   ▼
[2] Coletar assets (Drive / pasta local)
   │
   ▼
[3] Design thinking (/frontend-design + /ui-ux-pro-max)
   │
   ▼
[4] Claude escreve index.html completo
   │
   ▼
[5] Upload via REST API (mesmo endpoint dos outros fluxos)
   │
   ▼
[6] Verificacao obrigatoria
```

---

## Passo 1 — Coletar conteudo do ClickUp

Buscar na task do projeto:
- `hero_title`: nome do projeto (ex: "Teatro dos Bons Hábitos")
- `hero_subtitle`: linha de ativacao (ex: "Teatro, leitura e cidadania nas escolas públicas")
- `sobre_paragraphs`: 2-3 paragrafos descritivos (sem travessao `—`)
- `atividades`: lista com titulo + descricao curta de cada atividade
- `cidades`: cidades de realizacao (se houver)
- `patrocinador`: nome + cores da marca (buscar site via WebFetch se necessario)

```python
# Buscar task principal do projeto
task = clickup_get_task(task_id)
comments = clickup_get_task_comments(task_id)
# Extrair TAP ou briefing do projeto nos comentarios
```

**Regras editoriais:**
- NUNCA usar travessao `—` em textos publicados — substituir por `,` ou `.`
- Remover "Ministério da Cultura apresenta" do sobre
- Atividades vêm do briefing aprovado, nao de rascunhos

---

## Passo 2 — Coletar assets

```
SecondBrain/projetos/{slug}/assets/
  LOGOS/    → logo PNG transparente do projeto
  REGUAS/   → régua de patrocinadores JPG/PNG
  FOTOS/    → fotos do projeto (se pos-execucao)
```

Se sem fotos proprias, usar banco:
```
SecondBrain/banco-fotos/{categoria}/
  Ex: 5. ROBÓTICA NAS ESCOLAS/
      2. PEC   PIE   PED/PEC/
      7. CULINÁRIA SUSTENTÁVEL/
```

**BRAND_BLACKLIST** — filtrar fotos com marcas visiveis de outros patrocinadores:
SADA, Pague Menos, Wilson Sons, Statkraft, Whirlpool, Áster, Sylvamo, Compagás,
Nereu Ramos, Semec, Tecnoarte, Circuiteira, Revolucionários Verdes, Engrenagens da Imaginação.

**Cores do projeto:** extrair do site do patrocinador via WebFetch, ou do ClickUp,
ou pedir ao usuario. Definir `color_main` (principal) + `color_dark` (escuro) como hex.

Referencia de paletas existentes:
- Azul: `#2196F3` / `#1565C0`
- Cyan: `#0891B2` / `#155E75`
- Verde: `#16A34A` / `#14532D`
- Laranja: `#EA580C` / `#9A3412`
- Rosa: `#DB2777` / `#9D174D`

---

## Passo 3 — Design thinking

Antes de escrever qualquer codigo, definir:

### Direcao estetica (guiada por /frontend-design)

Avaliar contexto do projeto:
- **Publico:** estudantes, comunidade, patrocinador corporate?
- **Tema:** robotica, gastronomia, teatro, sustentabilidade?
- **Tom:** inspirador, educativo, social, cultural?

Escolher direcao e documentar antes de codar:
```
Direcao: [ex: "editorial social com energia juvenil"]
Tipografia: [par de fontes — evitar Inter/Roboto/Arial]
Estetica: [ex: "cor principal do patrocinador dominante, fotos grandes, texto bold"]
Animacoes: [ex: "fade-in suave nas secoes, hover nos cards de atividade"]
```

### Decisoes de UI (guiada por /ui-ux-pro-max)

Checklist obrigatorio antes de codar:
- [ ] Contraste minimo 4.5:1 para texto sobre fundo
- [ ] Touch targets >= 44x44px em botoes/links
- [ ] Mobile-first: breakpoints sm/md/lg definidos
- [ ] Imagens com `alt` descritivo
- [ ] `prefers-reduced-motion` respeitado nas animacoes
- [ ] Fonte base >= 16px, line-height >= 1.5

---

## Passo 4 — Escrever o HTML

Claude gera `index.html` completo. Stack obrigatoria:
- **Tailwind CDN** (sem build step)
- **Google Fonts** com o par tipografico escolhido
- **CSS variables** para cores do projeto
- **JavaScript inline** apenas se necessario (sem frameworks externos)

### Estrutura de secoes (obrigatoria)

```html
1. <header>  sticky, fundo color_main solido, logo pequeno + nav
2. <section#hero>  foto real full-height, overlay escuro, logo grande centralizado
                   SVG wave divider no bottom
3. <section#sobre>  2 colunas: texto esquerda, foto direita (ou inverso)
4. <section#atividades>  cards zigue-zague (foto alterna lado a cada item)
5. <section#galeria>  masonry: item-1 span-2col+2row, item-5 span-2col, resto quadrado
6. <section#cidades>  se houver dados de cidades
7. <footer>  regua de patrocinadores max-w-6xl centrada + info NTICS
```

### Regras de layout (inegociaveis — aprendidas em producao)

**Header:**
- Sticky com fundo `color_main` solido — NUNCA transparente
- Logo `h-10 md:h-12`

**Hero:**
- Foto background full-height (`min-h-screen`)
- Overlay `bg-black/50` para legibilidade
- Logo do projeto em card branco centralizado: `h-40 md:h-56 lg:h-64`
- SVG wave no bottom (branco, curvo, suaviza transicao)

**Atividades:**
- Zigue-zague obrigatorio: `flex-row` nos pares, `flex-row-reverse` nos impares
- Foto quadrada ou 4:3 a cada card

**Galeria masonry:**
- `grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4`
- Item 1: `col-span-2 row-span-2` (destaque)
- Item 5: `col-span-2` (banner largo)
- Demais: quadrado padrao
- N = 6 (padrao), 12 se pool de fotos for grande

**Regua / footer:**
- `<img>` regua com `max-w-6xl mx-auto` — NUNCA `max-w-4xl`
- Footer escuro com info basica NTICS

**Paths de imagens:**
- Sempre relativos: `FOTOS/nome.jpg`, `LOGOS/logo.png`, `REGUAS/regua.jpg`
- NUNCA paths absolutos ou GitHub raw

### CSS variables obrigatorias

```css
:root {
  --color-main: #HEXCODE;
  --color-dark: #HEXCODE;
  --color-text: #1a1a1a;
  --color-bg: #ffffff;
  --font-display: 'Nome da Fonte Display', sans-serif;
  --font-body: 'Nome da Fonte Body', sans-serif;
}
```

---

## Passo 5 — Upload

```bash
# Garantir que index.html esta em assets/projetos/{N}/
python tools/migration/upload_new_sites.py --only {N}
```

Se o script nao existir ou falhar, upload direto via REST API:

```python
import requests, base64, os
from dotenv import load_dotenv
load_dotenv()

WP_URL = os.getenv("WP_URL")
auth = (os.getenv("WP_USER"), os.getenv("WP_APP_PASSWORD"))
endpoint = f"{WP_URL}/wp-json/nticsfiles/v1/write"

# Upload index.html
with open("assets/projetos/{N}/index.html") as f:
    html = f.read()
requests.post(endpoint, auth=auth, json={
    "path": "{slug}/index.html",
    "content": html,
    "base64": False
})

# Upload cada imagem em FOTOS/, LOGOS/, REGUAS/
for folder in ["FOTOS", "LOGOS", "REGUAS"]:
    for fname in os.listdir(f"assets/projetos/{N}/{folder}"):
        with open(f"assets/projetos/{N}/{folder}/{fname}", "rb") as f:
            content = base64.b64encode(f.read()).decode()
        requests.post(endpoint, auth=auth, json={
            "path": f"{slug}/{folder}/{fname}",
            "content": content,
            "base64": True
        })
```

---

## Passo 6 — Verificacao obrigatoria

```bash
curl -I https://ntics.com.br/{slug}/
# Esperado: HTTP/2 200
```

Checklist visual (abrir no navegador):
- [ ] Hero: foto carrega, logo visivel, texto legivel sobre overlay
- [ ] Header sticky: aparece ao rolar, fundo solido (nao transparente)
- [ ] Atividades: fotos alternando lado (zigue-zague confirmado)
- [ ] Galeria: item 1 em destaque, sem fotos de outros patrocinadores
- [ ] Regua: carrega no footer, largura correta (nao pequena)
- [ ] Mobile: abrir em viewport 375px, sem scroll horizontal
- [ ] Nenhuma imagem quebrada (404 no network)

---

## Historico de projetos v2

| # | Projeto | URL | Data |
|---|---|---|---|
| — | — | — | — |

*(preencher apos primeiro projeto publicado)*
