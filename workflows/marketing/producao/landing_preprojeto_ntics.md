# Landing Page Pré-Projeto NTICS

Workflow para criar landing page de projeto que **ainda vai acontecer** (sem fotos próprias do projeto), publicada em `ntics.com.br/{slug}/`. Diferente do [criar_landing_ntics.md](../referencia/criar_landing_ntics.md) (pós-projeto / Renderforest), aqui a fonte é o Lovable.

## Quando usar

- Projeto pré-execução ainda sem fotos próprias
- Cliente pediu landing page antecipada (mobilização, divulgação)
- Site já existe no Lovable mas precisa subir em `ntics.com.br`
- Usa fotos genéricas do banco `SecondBrain/banco-fotos/{categoria}/`

## Pipeline

```
URL Lovable do projeto
   │ (SPA — precisa renderizar JS para extrair texto)
   ▼
[1] Playwright headless renderiza e extrai:
     - hero_title + hero_subtitle
     - sobre_paragraphs (2-3 parágrafos)
     - atividades (títulos H3 + descrições)
     - cidades (se houver seção "Por onde passamos")
   → output/_lovable_{id}_content.json
   │
   ▼
[2] Selecionar categoria de fotos do banco:
     116/117 robótica    → SecondBrain/banco-fotos/5. ROBÓTICA NAS ESCOLAS/
     119 PEC             → SecondBrain/banco-fotos/2. PEC   PIE   PED/PEC/
     127 PIE             → SecondBrain/banco-fotos/2. PEC   PIE   PED/PIE/
     124/125 culinária   → SecondBrain/banco-fotos/7. CULINÁRIA SUSTENTÁVEL/
     oficina de foto     → SecondBrain/banco-fotos/OFICINA DE FOTOGRAFIA/
   │
   ▼
[3] Ranking estético + semântico das fotos:
     - tools/media/rank_aesthetic_laion.py (LAION score 1-10, CPU local)
     - Subagent Sonnet classifica cada foto: scene, activity_match[], hero_score, galeria_score, quality_issues
   → output/rankings/sonnet/{pool}.json
   │
   ▼
[4] tools/migration/build_all_models.py
     - Para cada atividade do Lovable, mapeia activity_match → tags → picks melhor foto
     - Filtra marcas de outros patrocinadores (BRAND_BLACKLIST)
     - Monta HTML fiel ao padrão RF-origin (header sólido + hero foto + sobre 2col + atividades zigue-zague + galeria masonry + régua + footer)
     - Gera site.html em assets/projetos/{N}/site.html
   │
   ▼
[5] tools/migration/upload_new_sites.py --only {id}
     - Sobe site.html como index.html
     - Sobe FOTOS/, LOGOS/, REGUAS/ via Code Snippet REST API (endpoint /nticsfiles/v1/write)
   │
   ▼
[6] curl -I https://ntics.com.br/{slug}/
     - Verifica 200 OK
```

## Regras obrigatórias (aprendidas em produção)

### Conteúdo editorial

1. **Atividades vêm do Lovable**, não do TAP nem do site.html local — user exige fidelidade ao que já foi publicado
2. **Textos SEM travessão** `—` (regra geral NTICS)
3. **"Ministério da Cultura apresenta"** — remover da seção sobre (redundante)

### Fotos

4. **Hero bg = foto real do projeto**, nunca o manual/KV do brand book
5. **Logo do projeto** aparece em 3 lugares: header pequeno (h-12), hero grande centralizado sobre card branco, footer (h-14)
6. **Nunca usar** o manual de aplicação da marca como logo — use `LOGOS/{num}_{nome}.png`
7. **Pool de fotos por tipo de atividade**, não por número do projeto (projeto novo não tem fotos próprias)
8. **BRAND_BLACKLIST**: filtrar fotos com marcas de outros patrocinadores visíveis (SADA, Pague Menos, Wilson Sons, Statkraft, Whirlpool, Áster, Sylvamo, Compagás, Nereu Ramos, Semec, Tecnoarte, Circuiteira, Revolucionários Verdes, Engrenagens da Imaginação)
9. **Oficina de Fotografia pool** só incluir quando projeto tem atividade "Oficina/Workshop de Fotografia" — caso contrário as 4 fotos do pool contaminam a galeria
10. **Se usuário fornecer fotos próprias** (ex: Taynan Rodrigues para 117), dropar o banco e usar só as fornecidas. Classificar via Sonnet subagent, atribuir aos slots, resize 1800px max

### Layout

11. **Header sticky com fundo colorido sólido** — nunca transparente (some sobre o hero)
12. **Hero bottom**: SVG wave divider suaviza transição
13. **Atividades zigue-zague** (alternando foto-esquerda / foto-direita) — nunca tudo na mesma coluna
14. **Galeria masonry**: item 1 span-2 col + span-2 row (destaque), item 5 span-2 (banner largo), demais quadrados
15. **Régua** max-w-6xl centrada, antes do footer
16. **Galeria N = 6 padrão**, 12 quando pool é grande (ex: culinária com 42 fotos sem marca)

### Paleta (por projeto)

17. Não usar cores hardcoded entre projetos; definir `color_main` + `color_dark` em SITES dict:
    - 116 Cultura Robótica Áster: `#2196F3` / `#1565C0` (azul)
    - 117 Teatro Robótica Whirlpool: `#0891B2` / `#155E75` (cyan)
    - 119 PEC Sylvamo: `#16A34A` / `#14532D` (verde)
    - 125 Gastronomia GRU: `#EA580C` / `#9A3412` (laranja)
    - 127 PIE: `#DB2777` / `#9D174D` (rosa)

### Upload

18. **Paths relativos** no HTML (FOTOS/, LOGOS/, REGUAS/) — nunca GitHub raw nem absoluto
19. **Code Snippet id=6 ativo** em ntics.com.br/wp-admin (endpoints `/nticsfiles/v1/write`, `/mkdir`, `/ls`)
20. **Re-upload sobrescreve** — rerodar é idempotente

## 6 sites publicados em 2026-04-21

| # | Projeto | URL | Lovable origem |
|---|---|---|---|
| 116 | Cultura Robótica (Áster) | https://ntics.com.br/cultura-robotica-aster/ | cultura-robotica-2026.lovable.app |
| 117 | Teatro Robótica (Whirlpool) | https://ntics.com.br/teatro-oficina-robotica-4ed-whirlpool/ | teatro-e-oficina-robotica-2026.lovable.app |
| 119 | PEC (Sylvamo) | https://ntics.com.br/pec-eu-faco-parte-2ed-sylvamo/ | pec-eu-faco-parte-2026.lovable.app |
| 125 | Gastronomia 2ed (GRU) | https://ntics.com.br/gastronomia-tambem-e-arte-2ed-gru/ | gastronomia-tambem-e-arte-2ed-2026.lovable.app |
| 127G | PIE (GRU) | https://ntics.com.br/pie-empreendedorismo-e-arte-2ed-gru/ | pie-empreendedorismo-gru.lovable.app |
| 127S | PIE (Sotreq) | https://ntics.com.br/pie-empreendedorismo-e-arte-2ed-sotreq/ | pie-empreendedorismo-serra.lovable.app |

**124 Compagás**: pendente (logo+régua ausentes, sem URL Lovable conhecida).

## Tools criadas

- `tools/migration/build_all_models.py` — gera site.html a partir de config + content Lovable + pool de fotos
- `tools/migration/upload_new_sites.py` — sobe site.html + FOTOS/ + LOGOS/ + REGUAS/ via REST API
- `tools/media/rank_aesthetic_laion.py` — LAION Aesthetic Predictor v2 (já existia)

## Config SITES dict em build_all_models.py

Cada entrada suporta:

```python
"117": {
    "dir": "117. TEATRO E OFICINA ROBÓTICA 4ED (WHIRLPOOL)",
    "logo": "117_teatro_robotica.png",
    "regua": "Régua - 117.png",
    "color_main": "#0891B2",
    "color_dark": "#155E75",
    "hero_subtitle": "Teatro, robótica e criatividade nas escolas públicas",
    "sonnet_pool": "robotica",            # 'robotica'|'pec'|'pie'|'culinaria'
    "include_oficina_foto": False,        # True só se tem Oficina de Fotografia
    "galeria_n": 6,                       # padrao 6, usa 12 se pool grande
    "force_atividade_photo": {1: "stem"}, # override manual (ex: Lucas disse "use foto 57")
    "force_sobre_photo": "stem",          # override manual da imagem sobre
}
```
