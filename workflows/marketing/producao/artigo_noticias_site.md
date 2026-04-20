# Artigo de Noticias para o Site — NTICS Projetos

> Referencia: este workflow e uma **fase do carrossel de noticias**. A SOP completa esta em `producao/carrosseis/carrossel_noticias.md`, Fase 5.

## Resumo

Transforma as 7 noticias ESG da semana (pesquisadas via Perplexity) em artigo aprofundado para ntics.com.br. O artigo e publicado ANTES do carrossel, e o carrossel linka para ele na descricao.

## Cadeia de publicacao

```
Perplexity pesquisa 7 noticias (Fase 1 do carrossel)
  ├→ Artigo Noticias Site (Fase 5 — publica PRIMEIRO)
  └→ Carrossel Noticias (Fase 6 — publica DEPOIS, com link pro artigo)
```

## Script

```bash
python tools/content-gen/gerar_artigo_site.py --tipo noticias --semana YYYY-MM-DD
```

## Output

```
output/marketing/artigos/
├── artigo-noticias-esg-semana-{YYYY-MM-DD}.html  (body only, CSS inline)
├── hero-noticias-esg-semana-{YYYY-MM-DD}.jpg
├── img-{desc1}.jpg
└── img-{desc2}.jpg
```

## Checklist de Revisão (antes de entregar)

Executar antes de salvar o HTML final e passar para a Fase 6 do carrossel:

**Conteúdo**
- [ ] As 7 notícias do carrossel estão todas cobertas no artigo
- [ ] Nenhum dado inventado — todo número tem fonte no Perplexity/search
- [ ] Sem menção a Ministério da Cultura, Lei Rouanet ou Lei de Incentivo
- [ ] Tom alinhado com `brand-book/02-identidade-verbal/tom-de-voz.md`
- [ ] Título e lead paragraph capturam a narrativa da semana (não lista solta)

**Imagens**
- [ ] Hero com imagem fotorrealista (Nano Banana 2 ou foto real)
- [ ] Pelo menos 2 imagens inline coerentes com o contexto BR
- [ ] Nenhuma imagem genérica em inglês ou com texto estrangeiro visível
- [ ] Imagens reutilizadas dos cards do carrossel quando possível

**Estrutura HTML**
- [ ] Apenas body do artigo (sem `<html>`, `<head>` ou `<body>` wrapper)
- [ ] CSS inline no lead paragraph (cor azul-petróleo)
- [ ] Tipografia Inter + cores do Brand Book
- [ ] Link para o carrossel no Instagram incluído (ou placeholder `[LINK_CARROSSEL]`)

**Acao em caso de problema:** corrigir antes de mover para Fase 6. Nao publicar com pendencias 🔴.

---

## SOP Completa

Ver: [`carrossel_noticias.md` → Fase 5](carrosseis/carrossel_noticias.md)
