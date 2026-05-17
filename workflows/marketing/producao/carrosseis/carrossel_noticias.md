# Boletim de Boas Noticias ESG — Documento Semanal (v3)

> Pesquisa noticias positivas da semana via Perplexity, cura 8-10 historias ranqueadas por fonte, e gera um documento de briefing para o designer com titulo, resumo, texto do card e legenda do post. O documento e postado na task ClickUp de noticias da semana.

---

## APIs Utilizadas

| API | Uso | Modelo/Config |
|-----|-----|---------------|
| Perplexity sonar-pro | 3 queries de busca em tempo real (clientes NTICS, ESG Brasil, sustentabilidade global) | base_url: api.perplexity.ai, model: sonar-pro |
| Claude Haiku | Seleciona 8-10 melhores noticias e redige todos os campos (resumo, card, legenda) | claude-haiku-4-5-20251001 |
| ClickUp MCP | Posta o documento na descricao da task de noticias da semana | clickup_search + clickup_update_task |

> **Aprendizado (v2):** Perplexity pode retornar URLs fabricadas. Este workflow mitiga com HEAD requests de verificacao antes de passar os dados ao Haiku. URLs com status [OK] tem prioridade na curadoria.

### Chaves necessarias
- `PERPLEXITY_API_KEY`
- `ANTHROPIC_API_KEY` (Claude Haiku para curadoria e redacao)

---

## Script

```bash
python tools/content-gen/gerar_noticias_semana.py --semana YYYY-MM-DD
```

**Flags uteis:**
- `--skip-perplexity` — reutiliza `raw_perplexity.json` do cache (economiza tokens Perplexity)
- `--n 8` — seleciona 8 noticias em vez do padrao 9

---

## Filtros de selecao de noticias

O Haiku aplica os seguintes criterios em ordem de prioridade:

1. **Somente positivo** — conquistas, metas atingidas, lancamento de programas. Rejeitar: crises, multas, quedas, controversias.
2. **Clientes NTICS prioritarios** — Boticario, Whirlpool, CNH Industrial, Rabobank, Samarco, Statkraft, Repsol, Bayer, ISA CTEEP, Sylvamo, Novelis, Moove, CTG Brasil (lista completa em `brand-book/data/clientes-newsroom.yaml`)
3. **Diversidade tematica** — nunca dois sobre o mesmo assunto (agua, energia, educacao, cooperativa, biodiversidade, governanca...)
4. **Diversidade de fontes** — maximo 2 noticias do mesmo veiculo
5. **Fontes reconhecidas** — Reuters, BBC, G1, Valor Economico, Exame, Agencia Brasil, Folha, Estadao, El Pais
6. **URLs verificadas** — prefere [OK] sobre [FAIL]
7. **Anti-repeticao** — nao repete URLs, temas ou empresas das semanas anteriores

---

## Execucao

### Fase 0 — Anti-Repeticao

Le `manifest.json` de todas as semanas em `output/marketing/carrosseis/noticias/semana-*/` e monta lista de:
- URLs ja usadas
- Titulos/temas ja cobertos
- Empresas ja destacadas recentemente

Tambem le `descricao.txt` de semanas v2 (retrocompativel).

---

### Fase 1 — Pesquisa Perplexity (3 queries)

**Query 1 — Clientes NTICS:**
```
positive ESG sustainability news this week {nomes dos clientes} achievement award 2026
```

**Query 2 — ESG Brasil:**
```
boas noticias responsabilidade social ESG empresas Brasil semana sustentabilidade conquista resultado
```

**Query 3 — Sustentabilidade global:**
```
positive sustainability ESG corporate social responsibility good news world week 2026 milestone impact
```

Cada query retorna: texto estruturado + lista de URLs (citations). Cache salvo em `raw_perplexity.json`.

---

### Fase 1b — Verificacao de URLs

Para cada URL retornada pelo Perplexity, faz HEAD request com timeout 5s:
- Status < 400 → `[OK]` (URL acessivel)
- Outros / timeout → `[FAIL]` (URL possivelmente fabricada ou fora do ar)

---

### Fase 2 — Curadoria e Redacao (Claude Haiku)

Recebe: conteudo Perplexity (ate 7.000 chars) + lista de URLs com status + lista de exclusao.

Para cada noticia selecionada, Haiku redige:

| Campo | Descricao |
|-------|-----------|
| `titulo_noticia` | Titulo completo como publicado na midia |
| `fonte` | Nome do veiculo (ex: "Valor Economico") |
| `url` | URL exata sem modificacao |
| `url_ok` | true/false conforme verificacao |
| `area` | Tema livre em portugues (ex: "Energia Renovavel") |
| `resumo` | 3-4 frases: o que/quem/impacto/por que importa. Somente dados reais do snippet. |
| `card_titulo` | Max 8 palavras, framing positivo, sem ponto final |
| `card_texto` | Array de 3 strings (max 25 palavras no total) |
| `legenda_post` | Caption Instagram/LinkedIn com 2-3 paragrafos + hashtags |
| `empresa_cliente_ntics` | Nome se for cliente NTICS, ou null |

---

### Fase 3 — Geracao do Documento

**Output:** `output/marketing/carrosseis/noticias/semana-YYYY-MM-DD/`

```
semana-YYYY-MM-DD/
├── noticias.md       ← briefing do designer (formato legivel)
├── manifest.json     ← dados estruturados + historico anti-repeticao
└── raw_perplexity.json  ← cache das buscas (para reprocessamento)
```

**Formato noticias.md — por noticia:**

```
## N. Titulo completo da noticia

**Fonte:** Nome da Midia | [Ver noticia](URL)  [URL verificada]
**Area:** Tema

**Resumo:**
3-4 frases com dados reais.

**Card — Titulo:** Max 8 palavras aqui
**Card — Texto:**
Linha 1 do card.
Linha 2 do card.
Linha 3 do card.

**Legenda do post:**
Caption para Instagram e LinkedIn.
#ESG #Sustentabilidade #ResponsabilidadeSocial #NTICS

---
```

---

### Fase 4 — Postagem no ClickUp (feita pelo agente)

Apos o script gerar o documento, o agente Claude:

1. Usa `clickup_search` para localizar a task de noticias da semana
2. Le o `noticias.md` gerado
3. Usa `clickup_update_task` para atualizar a descricao com o conteudo
4. Confirma com `clickup_get_task` que foi salvo corretamente

---

## Historico de versoes

| Versao | Script | Diferenca |
|--------|--------|-----------|
| v1 | — | Perplexity + Pillow (cards manuais) |
| v2 | `gerar_carrossel_noticias_v2.py` | Serper + Claude Haiku + Leonardo AI (9 cards JPG) |
| v3 | `gerar_noticias_semana.py` | Perplexity + Claude Haiku → documento markdown para designer |

> **v2 mantido** em `tools/content-gen/gerar_carrossel_noticias_v2.py` como referencia historica — nao modificar.
