---
name: criar-landing-preprojeto
description: "Cria landing page de projeto NTICS pré-execução (sem fotos próprias) em ntics.com.br/{slug}/ a partir de site Lovable + banco de fotos genéricas por categoria. Pipeline: Playwright renderiza Lovable → LAION+Sonnet rankeia fotos → injeta no template RF-origin → upload via Code Snippets API."
user-invocable: true
---

Você é o construtor de landing pages **pré-projeto** do `ntics.com.br`. Para projetos que já aconteceram (com fotos próprias), use `/criar-landing-ntics` (Renderforest). Aqui é só para **projetos futuros** ainda sem fotos.

## Quando usar

- Projeto ainda vai acontecer (mobilização, divulgação antecipada)
- Existe site correspondente no **Lovable** mas precisa subir em `ntics.com.br`
- Não tem pasta de fotos próprias — usa banco genérico em `assets/melhores-fotos/{categoria}/`
- Quando user fornecer fotos próprias (ex: ensaio Taynan Rodrigues), usar as dele no lugar do banco

## Fluxo completo

Ver [workflows/marketing/producao/landing_preprojeto_ntics.md](../../../workflows/marketing/producao/landing_preprojeto_ntics.md) para detalhes.

```
1. Extrair Lovable (Playwright headless, porque é SPA)
   → output/_lovable_{id}_content.json

2. Rankear fotos do banco:
   - LAION (local, grátis): tools/media/rank_aesthetic_laion.py
   - Sonnet vision (subagents paralelos, classifica scene/activity_match/hero_score/galeria_score)

3. tools/migration/build_all_models.py
   → assets/projetos/{N}/site.html

4. tools/migration/upload_new_sites.py --only {id}
   → https://ntics.com.br/{slug}/
```

## Pré-requisitos

1. `.env` com `WP_URL`, `WP_USER`, `WP_APP_PASSWORD`
2. Code Snippet id=6 ativo em ntics.com.br/wp-admin
3. `LOGOS/` e `REGUAS/` presentes em `assets/projetos/{N}/`
4. URL do Lovable do projeto
5. Python com playwright + PIL + beautifulsoup4 + torch (LAION)

## Regras obrigatórias

### Conteúdo
1. **Atividades vêm do Lovable**, não do TAP — fidelidade ao que está publicado
2. Textos sem travessão `—` (regra NTICS)
3. Remover "Ministério da Cultura apresenta" do sobre

### Fotos
4. **Hero = foto real do projeto** (nunca manual/KV)
5. **Logo** em 3 lugares: header h-12, hero grande em card branco, footer h-14 — nunca usar manual da marca
6. **BRAND_BLACKLIST**: filtrar fotos com outras marcas (SADA, Pague Menos, Wilson Sons, Statkraft, Whirlpool, Áster, Sylvamo, Compagás, etc.)
7. **include_oficina_foto=True apenas** se projeto tem "Oficina/Workshop de Fotografia" — caso contrário contamina galeria
8. **Fotos próprias fornecidas** sobrescrevem o banco genérico. Classificar via 1 subagent Sonnet, atribuir aos slots (hero_bg, sobre, atividade_N, galeria_N), resize 1800px.

### Layout
9. Header sticky **colorido sólido** (nunca transparente)
10. Hero com SVG wave divider no fim
11. Atividades zigue-zague (foto alterna lado)
12. Galeria masonry: item 1 (span-2×2) + item 5 (span-2 largo)
13. Paleta por projeto em `SITES dict` de `build_all_models.py`

### Upload
14. Paths relativos `FOTOS/`, `LOGOS/`, `REGUAS/` (nunca GitHub raw)
15. Re-upload sobrescreve idempotente

## Verificação obrigatória antes de declarar "feito"

- [ ] `curl -I https://ntics.com.br/{slug}/` retorna 200 OK
- [ ] Abrir URL no navegador e checar: hero com foto real, logo correto, atividades com fotos semânticas, galeria sem fotos marcadas de outros patrocinadores
- [ ] Régua carrega (inspecionar network: sem 404 em REGUAS/)

## 6 sites publicados (referência 2026-04-21)

| # | Projeto | URL ntics.com.br |
|---|---|---|
| 116 | Cultura Robótica (Áster) | cultura-robotica-aster |
| 117 | Teatro Robótica (Whirlpool) | teatro-oficina-robotica-4ed-whirlpool |
| 119 | PEC (Sylvamo) | pec-eu-faco-parte-2ed-sylvamo |
| 125 | Gastronomia 2ed (GRU) | gastronomia-tambem-e-arte-2ed-gru |
| 127G | PIE (GRU) | pie-empreendedorismo-e-arte-2ed-gru |
| 127S | PIE (Sotreq) | pie-empreendedorismo-e-arte-2ed-sotreq |
