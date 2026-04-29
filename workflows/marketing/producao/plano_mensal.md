# Plano Editorial Mensal

> Gera plano editorial completo do mês (arco ABT, hooks, distribuição semanal, outline de artigo) e cria tasks no ClickUp após aprovação.

---

## Quando usar

Início do mês, quando o tema central já foi definido. Um plano cobre 4 semanas de conteúdo.

Não usar para replanejamento de semana isolada (nesse caso, editar a task direto no ClickUp).

---

## Inputs

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| `tema_mensal` | string | Sim | Tema central do mês (ex: "Responsabilidade Social Corporativa") |
| `mes_ano` | string | Sim | Mês e ano alvo (ex: "Abril 2026") |
| `projetos_relevantes` | string | Não | Projetos NTICS relacionados ao tema (para b-rolls e cases) |
| `patrocinador_foco` | string | Não | Persona: Renata (ESG), Ricardo (Marketing) ou Carla (Financeiro) |

Antes de começar, consultar `brand-book/INDEX.md` para tom, proof points e paleta.

---

## APIs e chaves

| API | Uso | Variável |
|-----|-----|----------|
| ClickUp | Criar tasks das 4 semanas na lista `901109494072` | via script (token em `.env`) |

---

## Tool

```bash
python tools/integrations/create_social_media_tasks.py create-plan --plan .tmp/marketing/plano_{mes}.json
```

Tool é invocada só na Fase 6. As fases 1 a 4 são redação pelo agente.

---

## Execução

### Fase 1: Arco narrativo do mês (auto)

Framework **ABT** (And-But-Therefore) distribuído em 4 semanas:

- **Semana 1 (AND):** contexto, por que o tema importa agora
- **Semana 2 (BUT):** problemas, equívocos, desafios
- **Semana 3 (THEREFORE):** solução, cases NTICS, boas práticas
- **Semana 4 (SÍNTESE):** visão, futuro, compilação para o artigo

### Fase 2: Hooks semanais (auto)

Um hook principal por semana, aplicando regra da especificidade (números, nomes, detalhes concretos). Categorias sugeridas:

- Semana 1: Curiosity Gap ou Bold Claim
- Semana 2: Contrarian ou Question
- Semana 3: Result/Proof
- Semana 4: Story

Teste de corte: "eu pararia de rolar o feed por isso?"

### Fase 3: Distribuição de conteúdo (auto)

Cada semana tem 3 carrosseis + 1 vídeo:

- **Segunda:** Carrossel Educativo, conceito ou framework do sub-tema
- **Terça:** Carrossel Notícias ESG, 6 boas notícias da semana
- **Quarta:** Vídeo de 1 min, sub-tema com estilo sugerido (animação ou b-roll)
- **Quinta:** Carrossel Case, projeto NTICS que ilustra o sub-tema (se houver dado)

Para cada carrossel educativo, incluir: título, 5 sub-temas dos cards, frase-destaque por card, cena da capa para Leonardo.

### Fase 4: Outline do artigo (auto)

Compilado mensal, uma seção por semana:

- Título provisório
- 4 seções (uma por sub-tema semanal)
- Tom: Blog educativo (55% formal, 60% técnico, 70% inspiração)

### Fase 5: Apresentar plano ao Lucas (gate humano)

Renderizar o plano no formato de saída (ver abaixo) e pedir aprovação. Ajustar o que vier antes de seguir.

### Fase 6: Criar tasks no ClickUp (auto, após aprovação)

1. Gerar JSON do plano no formato esperado pelo tool (schema abaixo)
2. Rodar o script e verificar que tasks apareceram na lista `901109494072`
3. Salvar IDs retornados em `.tmp/clickup_plan_result.json`

Schema mínimo do JSON:

```json
{
  "mes": "Abril 2026",
  "tema": "Responsabilidade Social Corporativa",
  "semanas": [
    {
      "numero": 1,
      "tema": "Por que RS importa agora",
      "hook": "88% dos consumidores preferem marcas com impacto real",
      "inicio": "2026-04-06",
      "conteudos": [
        {"tipo": "educativo", "titulo": "...", "briefing": "...", "dia_semana": 0},
        {"tipo": "noticias",  "titulo": "...", "briefing": "...", "dia_semana": 1},
        {"tipo": "case",      "titulo": "...", "briefing": "...", "dia_semana": 3}
      ]
    }
  ]
}
```

---

## Output esperado

Plano em markdown apresentado na conversa, com:

```markdown
# Plano Editorial: {Tema} | {Mês/Ano}

## Tema Central
{relevância, conexão ESG/ODS}

## Arco Narrativo
{progressão ABT}

### Semana 1..4: {Sub-tema}
**Ângulo:** {AND/BUT/THEREFORE/SÍNTESE}
**Hook:** {hook + categoria}
| Conteúdo | Formato | Estilo |
| ... | ... | ... |
**B-rolls sugeridos:** ...

## Artigo Mensal (Outline)
## Email Marketing (Preview)
## Calendário Visual (tabela 4 linhas)
```

Após aprovação: tasks criadas em ClickUp `901109494072`, IDs salvos em `.tmp/clickup_plan_result.json`.

---

## Checklist de qualidade

- [ ] 4 sub-temas distintos que formam arco narrativo coerente (não justaposição)
- [ ] Hooks com especificidade (números, nomes, detalhes)
- [ ] Pelo menos 2 proof points do `brand-book/data/brand-data.yaml` citados
- [ ] B-rolls realistas para empresa de impacto social/ESG
- [ ] Calendário executável nas datas reais do mês
- [ ] Outline do artigo conecta as 4 semanas, não lista solta
- [ ] Nenhum travessão `—` no plano final

---

## Dependências

**Upstream:** nenhum (entrada do pipeline editorial).

**Downstream:**
- Agente criador semanal lê as tasks do ClickUp e dispara os workflows
- `/carrossel-educativo`, `/carrossel-noticias`, `/carrossel-case` executam os cards da semana
- `/roteiro-video` para cada vídeo semanal
- `/artigo-mensal` no fim do mês consome os 4 roteiros
- `/newsletter` consolida tudo em email
