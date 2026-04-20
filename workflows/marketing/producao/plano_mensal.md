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

Para cada semana, defina **3 carrosseis + 1 video**:

- **Segunda:** Carrossel Educativo — conceito/framework sobre o sub-tema da semana
- **Terca:** Carrossel Noticias ESG — curadoria de 6 boas noticias (Perplexity)
- **Quarta:** Video (1 min) — sub-tema + estilo sugerido (animacao ou b-roll)
- **Quinta:** Carrossel Case — projeto NTICS de sucesso (se houver dados disponiveis)
- **1-2 posts** complementares (LinkedIn + Instagram)
- **B-rolls sugeridos** — cenas dos projetos NTICS que combinam com o sub-tema

Para cada carrossel educativo, incluir no plano:
- Titulo do tema
- 5 sub-temas dos cards de conteudo
- Frase destaque de cada card
- Cena sugerida para foto de capa (Leonardo AI)

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
| 1 | Educativo | Noticias ESG | Video | Case | Post LI |
| 2 | Educativo | Noticias ESG | Video | Case | Post LI |
| 3 | Educativo | Noticias ESG | Video | Case | Post LI |
| 4 | Educativo | Noticias ESG | Video | Case | Artigo + Email |
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

## Fase 5: Criar Tasks no ClickUp

Apos aprovacao do plano pelo Lucas, criar tasks automaticamente:

1. Gerar JSON do plano no formato esperado por `tools/integrations/create_social_media_tasks.py`
2. Executar: `python tools/integrations/create_social_media_tasks.py create-plan --plan .tmp/marketing/plano_{mes}.json`
3. Verificar tasks criadas na lista `901109494072`

**Formato do JSON:**
```json
{
  "mes": "Abril 2026",
  "tema": "Responsabilidade Social Corporativa",
  "semanas": [
    {
      "numero": 1,
      "tema": "Por que RS importa agora",
      "hook": "88% dos consumidores preferem marcas com impacto social real",
      "inicio": "2026-04-06",
      "conteudos": [
        {
          "tipo": "educativo",
          "titulo": "5 sinais de maturidade em RS",
          "briefing": "Conceitos essenciais sobre maturidade em responsabilidade social...",
          "dia_semana": 0
        },
        {
          "tipo": "noticias",
          "titulo": "Boas noticias ESG da semana",
          "briefing": "Curadoria automatica — noticias positivas ESG/CSR da semana",
          "dia_semana": 1
        },
        {
          "tipo": "case",
          "titulo": "Conhecendo os ODS — Wilson Sons",
          "briefing": "Case do projeto Conhecendo os ODS com foco em resultados...",
          "dia_semana": 3
        }
      ]
    }
  ]
}
```

**Output:** Lista de task IDs criados, salva em `.tmp/clickup_plan_result.json`

---

## Conexao com Outras Skills

Apos gerar este plano e criar tasks, use:
- `/carrossel-educativo` para cada carrossel educativo semanal
- `/carrossel-noticias` para carrosseis de boas noticias ESG/CSR (automatico)
- `/carrossel-projeto` para carrosseis de projetos de sucesso
- `/roteiro-video` para cada video semanal (input: sub-tema + b-rolls)
- `/artigo-mensal` no final do mes (input: os 4 roteiros)
- `/email-marketing` para a newsletter mensal

O agente criador semanal (`agente_criador_semanal.md`) le as tasks do ClickUp e executa automaticamente.
