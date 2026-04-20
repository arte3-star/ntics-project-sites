# Workflows de Marketing

Estrutura organizada em 4 areas: producao de conteudo, carrosseis, agentes autonomos e referencia.

---

## Producao (`producao/`)

Workflows executaveis que geram conteudo. Invocaveis via `/comando`.

| Workflow | Arquivo | Comando | Output | Cadencia |
|----------|---------|---------|--------|----------|
| Plano Mensal | `plano_mensal.md` | `/plano-mensal` | Calendario editorial + tasks ClickUp | Mensal |
| Roteiro Video | `roteiro_video.md` | `/roteiro-video` | Script 1min (~150 palavras) | Semanal (4x/mes) |
| Artigo Mensal | `artigo_mensal.md` | `/artigo-mensal` | Artigo B2B + versao LinkedIn | Mensal |
| Newsletter | `newsletter.md` | `/newsletter` | HTML responsivo + Gmail draft | Semanal ou mensal |
| Artigo Site | `artigo_site.md` | `/artigo-site` | Pagina HTML + 5 imagens Leonardo AI | Por artigo |
| Vetorizar | `vetorizar_imagem.md` | — | SVG/AI/EPS/PDF vetorial | Sob demanda |

---

## 4 Tipos de Carrossel (`producao/carrosseis/`)

| Tipo | Arquivo | Comando | Identidade | APIs | Cadencia |
|------|---------|---------|------------|------|----------|
| **Noticias ESG** | `carrossel_noticias.md` | `/carrossel-noticias` | NTICS | Perplexity + Leonardo AI | Semanal |
| **Educativo ESG** | `carrossel_educativo.md` | `/carrossel-educativo` | NTICS | Leonardo AI (capa) + Pillow | Semanal |
| **Case Projeto** | `carrossel_case_projeto.md` | `/carrossel-case` | NTICS | Leonardo AI + image_reference | Por projeto finalizado |
| **Projeto Ativo Cliente** | `carrossel_projeto_ativo_cliente.md` | `/carrossel-cliente` | **DO CLIENTE** | WebFetch + Leonardo AI | Por projeto (3 fases) |
| Briefing Companion | `briefing_carrossel_video.md` | `/briefing-video` | DO CLIENTE | — | Por projeto |

### Projeto Ativo Cliente — 3 sub-tipos

| Fase | Tom | Quando |
|------|-----|--------|
| **Pre-projeto** | Futuro ("vai acontecer") | Antes da execucao |
| **Durante** | Presente ("esta acontecendo") | Durante execucao |
| **Pos-projeto** | Passado ("aconteceu") | Apos execucao (case + reels de venda) |

---

## Agentes Autonomos (`agentes/`)

| Agente | Arquivo | Trigger | O que faz |
|--------|---------|---------|-----------|
| Criador Semanal | `agente_criador_semanal.md` | Domingo 20h | Produz educativo (seg) + noticias (ter) + video (qua) + case (qui) |
| Revisor Semanal | `agente_revisor_semanal.md` | Segunda 8h | Revisa qualidade contra brand book |
| Ajustes Tempo Real | `agente_ajustes_tempo_real.md` | Comentario ClickUp | Corrige conteudo quando Lucas comenta |
| Publicador | `agente_publicador.md` | Status "aprovado" (webhook n8n) | Publica LinkedIn (auto) + notifica Instagram manual, status → "publicado" |

---

## Referencia (`referencia/`)

| Doc | Arquivo | Proposito |
|-----|---------|-----------|
| LinkedIn Strategy | `linkedin_strategy.md` | Pilares, formatos, tom e cadencia |
| Uso de Squads | `uso_squads_marketing.md` | Como rotear para os 10 squads |
| Time Midias Sociais | `team_midias_sociais.md` | Agent Team: lead + writer + publisher |
| Time Design Conteudo | `team_design_conteudo.md` | Agent Team de design visual |

---

## Diretorios de Output

```
output/marketing/                     # Entregas finais
  carrosseis/
    noticias/semana-{data}/            # 8 JPGs + descricao.txt
    educativos/semana-{data}/          # 8 JPGs + descricao.txt + manifest.json
    cases/{nome}/                      # 8 JPGs + descricao.txt + PDF LinkedIn
    clientes/{numero-projeto}/{fase}/  # 8 JPGs + perfil-visual.md + descricao.txt
  artigos/
    artigo-{slug}.html + imagens
  newsletters/
    newsletter-{YYYY-MM-DD}.html
  videos/
    roteiro-{slug}.md
  planos/
    plano-{YYYY-MM}.md

.tmp/marketing/                        # So intermediarios (gitignored)
  raw_search_*.json, stories_*.json, images/, build/
```

---

## Cadeia de Dependencias

```
/plano-mensal (gera plano + cria tasks ClickUp)
  |
  +-> Agente criador semanal (domingo 20h)
  |   +-> /carrossel-educativo (segunda)
  |   +-> /carrossel-noticias (terca)
  |   +-> /roteiro-video (quarta)
  |   +-> /carrossel-case (quinta)
  |
  +-> Lucas aprova via ClickUp
  |   +-> Agente ajustes tempo real (se necessario)
  |
  +-> /artigo-mensal (fim do mes)
       +-> /newsletter (consolida tudo + Gmail draft)

/artigo-site (independente)
/carrossel-cliente (por projeto ativo — pre/durante/pos)
```
