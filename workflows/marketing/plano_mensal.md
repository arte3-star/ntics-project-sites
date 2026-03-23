# Plano Editorial Mensal — NTICS Projetos

> Gera o plano editorial completo do mes para a NTICS Projetos, com arco narrativo, sub-temas semanais, hooks e calendario.

---

## Contexto da Marca

Antes de comecar, leia os seguintes arquivos para alinhar voz e dados:

1. `brand-book/02-identidade-verbal/tom-de-voz.md` — pilares de voz e calibracao por canal
2. `brand-book/02-identidade-verbal/mensagens-chave.md` — taglines, manifesto, proof points
3. `brand-book/data/brand-data.yaml` — metricas, projetos, credenciais NTICS

---

## Inputs do Usuario

| Campo | Tipo | Obrigatorio | Descricao |
|-------|------|-------------|-----------|
| `tema_mensal` | string | Sim | Tema central do mes (ex: "Responsabilidade Social Corporativa") |
| `projetos_relevantes` | string | Nao | Projetos NTICS relacionados ao tema (para b-rolls e cases) |
| `mes_ano` | string | Sim | Mes e ano alvo (ex: "Abril 2026") |
| `patrocinador_foco` | string | Nao | Persona do patrocinador: Renata (ESG), Ricardo (Marketing) ou Carla (Financeiro) |

---

## Execucao

### Fase 1: Arco Narrativo do Mes

Use o framework **ABT (And-But-Therefore)** do storytelling squad (`storytelling/tasks/build-narrative.md`) para criar uma progressao logica ao longo das 4 semanas:

- **Semana 1 (AND):** Contexto — apresentar o tema, por que importa agora
- **Semana 2 (BUT):** Problema — os desafios e equivocos comuns
- **Semana 3 (THEREFORE):** Solucao — como resolver, cases NTICS, boas praticas
- **Semana 4 (SINTESE):** Visao — futuro, compilacao, artigo mensal

### Fase 2: Hooks Semanais

Para cada semana, gere 1 hook principal usando a metodologia do hormozi squad (`hormozi-squad/tasks/create-hooks.md`):

- Aplique a **regra da especificidade**: numeros, nomes, detalhes concretos
- Categorias recomendadas por semana:
  - Semana 1: **Curiosity Gap** ou **Bold Claim** (gerar interesse)
  - Semana 2: **Contrarian** ou **Question** (desafiar crencas)
  - Semana 3: **Result/Proof** (mostrar resultados NTICS)
  - Semana 4: **Story** (fechar com narrativa)
- Teste: "Eu pararia de rolar o feed por isso?"

### Fase 3: Distribuicao de Conteudo

Para cada semana, defina:
- **1 video** (1 min) — sub-tema + estilo sugerido (animacao ou b-roll)
- **1 carrossel** — alternando entre projeto de sucesso e boas noticias ESG
- **1-2 posts** complementares (LinkedIn + Instagram)
- **B-rolls sugeridos** — cenas dos projetos NTICS que combinam com o sub-tema

### Fase 4: Estrutura do Artigo

Crie o outline do artigo mensal que sera o compilado:
- Titulo provisorio
- 4 secoes (uma por semana/video)
- Tom: Blog/Conteudo Educativo (55% formal, 60% tecnico, 70% inspiracao)

---

## Formato de Saida

```markdown
# Plano Editorial: {Tema} | {Mes/Ano}

## Tema Central
{Descricao do tema, relevancia para patrocinadores, conexao com ESG/ODS}

## Arco Narrativo do Mes
{Progressao ABT das 4 semanas}

---

### Semana 1: {Sub-tema}
**Angulo:** {AND — contexto}
**Hook:** {hook com categoria entre parenteses}

| Conteudo | Formato | Estilo/Tipo |
|----------|---------|-------------|
| Video | 1 min | animacao / b-roll |
| Carrossel | 5-8 slides | projeto / noticias |
| Post LinkedIn | caption | thought leadership |
| Post Instagram | caption | inspiracional |

**B-rolls sugeridos:** {cenas dos projetos NTICS}

### Semana 2: {Sub-tema}
{mesma estrutura}

### Semana 3: {Sub-tema}
{mesma estrutura}

### Semana 4: {Sub-tema}
{mesma estrutura}

---

## Artigo Mensal (Outline)
**Titulo:** {titulo provisorio}
**Secoes:**
1. {secao 1 — baseada na semana 1}
2. {secao 2 — baseada na semana 2}
3. {secao 3 — baseada na semana 3}
4. {secao 4 — baseada na semana 4}

## Email Marketing (Preview)
**Subject line:** {sugestao}
**Preheader:** {sugestao}

## Calendario Visual

| Semana | Seg | Ter | Qua | Qui | Sex |
|--------|-----|-----|-----|-----|-----|
| 1 | | Video | | Post LI | Carrossel |
| 2 | | Video | | Post LI | Carrossel |
| 3 | | Video | | Post LI | Carrossel |
| 4 | | Video | | Post LI | Artigo + Email |
```

---

## Checklist de Qualidade

- [ ] 4 sub-temas distintos que constroem um arco narrativo coerente (nao aleatorios)
- [ ] Hooks seguem regra da especificidade (numeros, nomes, detalhes)
- [ ] Voz alinhada aos 4 pilares NTICS: Informativa, Confiante, Inspiradora, Acessivel
- [ ] Pelo menos 2 proof points do brand-data.yaml citados
- [ ] B-rolls sugeridos sao realistas para empresa de impacto social/ESG
- [ ] Calendario pratico e executavel
- [ ] Artigo outline conecta os 4 temas de forma integrada (nao justaposta)

---

## Conexao com Outras Skills

Apos gerar este plano, use:
- `/roteiro-video` para cada video semanal (input: sub-tema + b-rolls)
- `/carrossel-projeto` para carrosseis de projetos de sucesso
- `/carrossel-noticias` para carrosseis de boas noticias ESG/CSR
- `/artigo-mensal` no final do mes (input: os 4 roteiros)
- `/email-marketing` para a newsletter mensal
