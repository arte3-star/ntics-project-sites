# Workflow: Revisão de Carrossel NTICS

## Objetivo

Garantir qualidade visual e editorial de qualquer carrossel NTICS antes de publicar:
educativo, case ou notícias. Detecta problemas bloqueantes e sinaliza com gravidade.

## Inputs obrigatórios

- `pasta` — caminho da pasta com os cards (JPG/PNG)
- `tipo` — `educativo`, `case` ou `noticias`
- `regenerar` (opcional, default `false`) — se `true`, dispara correção automática dos problemas 🔴

---

## Fase 1 — Carregar referências de marca

1. Ler `brand-book/data/brand-data.yaml` — para conferir números: projetos, pessoas impactadas, NPS, etc.
2. Ler `brand-book/02-identidade-verbal/tom-de-voz.md` — para calibrar avaliação de tom
3. Consultar feedback memories em MEMORY.md — especialmente `feedback_editorial_tone.md` e `feedback_leonardo_prompts.md`

---

## Fase 2 — Inspecionar visualmente cada card

Usar `Read` para carregar cada imagem da pasta e registrar observações por card:

```
Para cada arquivo JPG/PNG na pasta:
  - Número do card e conteúdo textual visível
  - Cores predominantes e presença da barra de gradiente
  - Presença/ausência de elementos obrigatórios
  - Problemas visuais observados
```

---

## Fase 3 — Checklist universal (todos os tipos)

Aplicar a TODOS os cards:

- [ ] **Sem erros ortográficos** — portugês correto, acentuação, concordância verbal/nominal
- [ ] **Dados numéricos corretos** — conferir com `brand-data.yaml` (ex: "1.060+" projetos, "11,4M" pessoas, NPS 88)
- [ ] **Tom positivo** — framing de oportunidade, não de problema ou alarmismo
- [ ] **Sem "CSR"** — sempre "Responsabilidade Social" por extenso
- [ ] **Barra de gradiente presente** (verde → teal → rosa → laranja) em todos os cards, sem hex codes visíveis como texto
- [ ] **Frase destaque presente** em cada card de conteúdo (cards 02-06)
- [ ] **Card 01 (capa)** — foto sem telas, monitores, TVs, projetores; não parece IA gerada; ambiente natural/pessoas
- [ ] **Card 08 (CTA)** — logo NTICS visível no topo, "ntics.com.br" correto, "@nticsprojetos" presente

---

## Fase 4 — Checklist por tipo

### Educativo

- [ ] **Capa** — badge "RESPONSABILIDADE SOCIAL QUE RESOLVE" presente e legível
- [ ] **Card 07 (Método)** — sem anotações de layout visíveis (ex: "8%", "10-22%"); grid 2×2 com dados NTICS corretos (1.060+, 11,4M, 9,32, 88)
- [ ] **Consistência visual** — todos os cards com mesmo padrão de fundo (teal ou foto+overlay)

### Case

- [ ] **Badge de categoria** correto (Educação / Cultura / Sustentabilidade / etc.)
- [ ] **Nome do patrocinador** presente se aplicável (ex: Sylvamo, CNH)
- [ ] **Logo do patrocinador** no card de capa se for carrossel de cliente
- [ ] **Foto de referência** usada (não foto genérica do banco de imagens)
- [ ] **Sem duplicação de palavras** (erro clássico do Leonardo: "NO NO MATO GROSSO")

### Notícias

- [ ] **Fonte da notícia** indicada em algum card
- [ ] **Sem repetição de tema** das semanas anteriores (verificar output recente)
- [ ] **3-4 notícias distintas** por semana

---

## Fase 5 — Relatório e ação

### Formato do relatório

```
## Revisão: {tipo} — {pasta}
Data: {data}

### Card 01 — Capa
🟢 Foto sem monitor
🟢 Badge presente
🔴 Hex code "3DAA35" visível na barra de gradiente

### Card 07 — Método NTICS
🔴 Anotações de layout visíveis: "8%", "10-22%"
🟡 NPS correto (88) mas "9,32" aparece como "9.32" (ponto em vez de vírgula)

### Card 08 — CTA
🔴 Logo NTICS ausente
🟢 ntics.com.br correto
🟢 @nticsprojetos correto

---
### Resumo
- 🔴 Bloqueantes: 3
- 🟡 Recomendados: 1
- 🟢 OK: 12
```

### Gravidades

| Ícone | Gravidade | Ação |
|-------|-----------|------|
| 🔴 | Bloqueante | Corrigir antes de publicar |
| 🟡 | Recomendado | Corrigir se possível |
| 🟢 | OK | Nenhuma ação necessária |

### Ação automática (se `regenerar=true`)

Para achados 🔴 em carrossel educativo:
- Hex codes na barra → corrigir em `gerar_educativos_3semanas.py` (já corrigido nas versões atuais)
- Logo ausente no CTA → rodar `python tools/content-gen/regen_educativo_bg_test.py --semana {S} --cards 08 --skip-leonardo`
- Anotações no Card 07 → regenerar via Leonardo com prompt corrigido

### Salvar relatório

Salvar em `{pasta}/revisao-{YYYY-MM-DD}.md` com o relatório completo.

---

## Scripts de correção disponíveis

| Problema | Script |
|----------|--------|
| Logo NTICS ausente no CTA | `regen_educativo_bg_test.py --cards 08 --skip-leonardo` |
| Card 07 com anotações de layout | Regenerar via `gerar_educativos_3semanas.py` (prompt corrigido) |
| Capa com tela/monitor | Corrigir `capa_cena` e regenerar card 01 |
| Fundo foto test | `regen_educativo_bg_test.py --cards 03,05 [--skip-leonardo]` |
