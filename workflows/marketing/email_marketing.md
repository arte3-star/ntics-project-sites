# Email Marketing / Newsletter Mensal — NTICS Projetos

> Gera o conteudo completo da newsletter mensal da NTICS, seguindo o template HTML existente em `brand-book/05-aplicacoes/email-newsletter-template.html`.

---

## Contexto da Marca

Antes de comecar, leia:

1. `brand-book/02-identidade-verbal/tom-de-voz.md` — calibracao para email (60% formal, 55% tecnico, 65% inspiracao)
2. `brand-book/05-aplicacoes/email-newsletter-template.html` — template HTML com estrutura das secoes
3. `brand-book/data/brand-data.yaml` — metricas, projetos, credenciais
4. `brand-book/02-identidade-verbal/mensagens-chave.md` — taglines e proof points

---

## Inputs do Usuario

| Campo | Tipo | Obrigatorio | Descricao |
|-------|------|-------------|-----------|
| `artigo_mensal` | string | Sim | Titulo + resumo do artigo do mes (vem de /artigo-mensal) |
| `destaques` | string | Sim | Metricas ou realizacoes do mes (projetos, numeros, conquistas) |
| `noticias_esg` | string | Sim | 3 boas noticias ESG/CSR para a secao "Boas Noticias do Mundo" |
| `leis_incentivo` | string | Nao | Atualizacoes sobre leis de incentivo (Rouanet, Esporte, FIA, etc.) |
| `numero_edicao` | number | Sim | Numero da edicao da newsletter |
| `data_edicao` | string | Sim | Data da edicao (ex: "22 Mar 2026") |

---

## Secoes do Template

O template HTML ja tem as seguintes secoes. Gere conteudo para cada uma:

### 1. Preheader
- Texto invisivel que aparece na preview do inbox
- Maximo 100 caracteres
- Deve conter: titulo do artigo + 1 destaque + "Boas noticias"

### 2. Edition Badge
- Formato: "NEWSLETTER MENSAL" + "Edicao #{numero} — {data}"

### 3. Artigo Destaque
- **Overline:** Categoria (ex: "ESG • INOVACAO" ou "IMPACTO SOCIAL • EDUCACAO")
- **Titulo:** Titulo do artigo (maximo 80 caracteres, impactante)
- **Resumo:** 2-3 frases que geram curiosidade para ler o artigo completo
- **Meta:** Tempo de leitura + autor
- **CTA:** "Ler artigo completo →"

### 4. Destaques do Mes
- **Header:** "Destaques de {Mes}" com subtitulo contextual
- **Grafico ISD:** Se aplicavel, dados de Investimento Social Direto (5 barras com labels e valores)
- **Stats Cards:** 3 cards com:
  - Numero grande (ex: "1.060+")
  - Label (ex: "projetos executados")
  - Variacao/contexto (ex: "+12 este mes")

### 5. Boas Noticias do Mundo
- 3 noticias positivas sobre ESG/CSR
- Para cada noticia:
  - **Badge:** Categoria com cor (ex: "ENERGIA LIMPA" verde, "BIODIVERSIDADE" azul)
  - **Titulo:** Headline da noticia (maximo 60 chars)
  - **Resumo:** 2 frases de contexto
  - **Fonte:** Nome da fonte + "Leia mais →"

### 6. Leis de Incentivo
- 3 leis de incentivo em destaque
- Para cada lei:
  - **Badge de status:** "ABERTO" (verde), "ENCERRANDO" (laranja), ou "EM BREVE" (azul)
  - **Nome da lei:** Ex: "Lei Rouanet — Mecanismo de Incentivo"
  - **Descricao:** 1 frase sobre oportunidade
  - **Prazo:** Data limite ou status
- **CTA:** "Descubra como investir com incentivo fiscal →"

### 7. CTA Final
- **Titulo:** Frase inspiradora conectada ao tema do mes
- **Subtitulo:** Complemento com dados
- **Botao:** CTA principal (ex: "Fale com nosso time")

---

## Execucao

### Fase 1: Subject Line + Preheader

Gere 3 opcoes de subject line seguindo a metodologia do copy squad (`copy-squad/tasks/write-email-sequence.md`):

- **Opcao Curiosity Gap:** Cria lacuna de informacao (ex: "O dado que mudou nossa estrategia ESG em marco")
- **Opcao Result/Proof:** Lidera com resultado (ex: "11,4M de pessoas impactadas — e o que vem agora")
- **Opcao Question:** Pergunta que forca reflexao (ex: "Sua empresa esta aproveitando 100% dos incentivos fiscais?")

Regras:
- Maximo 50 caracteres no subject
- Sem spam words (gratis, urgente, etc.)
- Preheader complementa o subject (nao repete)

### Fase 2: Conteudo por Secao

Escreva o conteudo de cada secao seguindo:
- Tom de email NTICS: 60% formal, 55% tecnico, 65% inspiracao
- Frases curtas e escaneaveis
- Dados sempre com contexto
- Voz do Sage que ensina e do Caregiver que cuida

### Fase 3: Revisao de Coerencia

- Verificar que todas as secoes se conectam ao tema do mes
- Verificar que o tom e consistente (nao misturar super-formal com casual)
- Verificar que nenhuma secao esta vazia ou com placeholder

---

## Formato de Saida

```markdown
# Newsletter NTICS — Edicao #{numero}

**Data:** {data}
**Tema do Mes:** {tema}

---

## Subject Lines (3 opcoes)

1. {opcao curiosity gap}
2. {opcao result/proof}
3. {opcao question}

**Recomendada:** #{numero da melhor opcao} — {justificativa}

## Preheader

{texto do preheader — max 100 chars}

---

## Secao: Artigo Destaque

- **Overline:** {categoria}
- **Titulo:** {titulo do artigo}
- **Resumo:** {2-3 frases}
- **Meta:** {X min de leitura | Por {autor}}
- **CTA:** Ler artigo completo →

## Secao: Destaques de {Mes}

**Subtitulo:** {frase de contexto}

**Stats Cards:**
| Numero | Label | Contexto |
|--------|-------|----------|
| {dado 1} | {label 1} | {variacao} |
| {dado 2} | {label 2} | {variacao} |
| {dado 3} | {label 3} | {variacao} |

## Secao: Boas Noticias do Mundo

### Noticia 1
- **Badge:** {categoria} ({cor})
- **Titulo:** {headline}
- **Resumo:** {2 frases}
- **Fonte:** {fonte} | Leia mais →

### Noticia 2
{mesma estrutura}

### Noticia 3
{mesma estrutura}

## Secao: Leis de Incentivo

### Lei 1
- **Status:** {ABERTO / ENCERRANDO / EM BREVE}
- **Nome:** {nome da lei}
- **Descricao:** {1 frase sobre oportunidade}
- **Prazo:** {data ou status}

### Lei 2-3
{mesma estrutura}

**CTA:** Descubra como investir com incentivo fiscal →

## Secao: CTA Final

- **Titulo:** {frase inspiradora}
- **Subtitulo:** {complemento com dados}
- **Botao:** {texto do CTA}
```

---

## Checklist de Qualidade

- [ ] Subject line tem menos de 50 caracteres
- [ ] Preheader complementa (nao repete) o subject
- [ ] Artigo destaque gera curiosidade para clicar
- [ ] Stats cards tem numeros concretos e verificaveis
- [ ] 3 noticias ESG positivas com fontes
- [ ] Leis de incentivo com status atualizado
- [ ] Tom consistente: 60% formal, 55% tecnico, 65% inspiracao
- [ ] Voz NTICS em todas as secoes
- [ ] CTA final claro e conectado ao tema
- [ ] Todas as secoes preenchidas (sem placeholders)

---

## Conexao com Outras Skills

- Input vem de:
  - `/artigo-mensal` (secao Artigo Destaque)
  - `/carrossel-noticias` (secao Boas Noticias do Mundo)
  - `/plano-mensal` (tema e dados do mes)
- Este e o ultimo skill do pipeline mensal — distribui todo o conteudo produzido
