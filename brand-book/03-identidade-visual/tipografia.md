# Tipografia — NTICS Projetos
> Brand Book v2.0 | Atualizado: Marco 2026

---

## Visao Geral

A tipografia da NTICS Projetos prioriza legibilidade, hierarquia clara e tom profissional. O sistema tipografico utiliza duas familias que se complementam em contextos impressos e digitais.

---

## Familias Tipograficas

### Helvetica Neue (Primaria)

Familia principal para materiais impressos, apresentacoes e documentos institucionais.

| Peso | Uso Principal |
|------|--------------|
| **Light (300)** | Textos decorativos, numeros grandes, citacoes em destaque |
| **Regular (400)** | Corpo de texto, paragrafos, descricoes |
| **Medium (500)** | Subtitulos, labels, enfase moderada |
| **Bold (700)** | Titulos, headlines, CTAs, destaques importantes |

### Inter (Alternativa Web)

Alternativa gratuita via Google Fonts para web, aplicativos e contextos digitais onde Helvetica Neue nao esta disponivel.

| Peso Helvetica Neue | Peso Inter Equivalente |
|---------------------|----------------------|
| Light (300) | Light (300) |
| Regular (400) | Regular (400) |
| Medium (500) | Medium (500) |
| Bold (700) | Bold (700) |

**Fonte Google Fonts:**
```
https://fonts.google.com/specimen/Inter
```

**Importacao CSS:**
```css
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;700&display=swap');
```

**Fallback stack:**
```css
font-family: 'Inter', 'Helvetica Neue', Helvetica, Arial, sans-serif;
```

---

## Hierarquia Tipografica

### Escala Completa

| Nivel | Tamanho | Peso | Line-Height | Letter-Spacing | Uso |
|-------|---------|------|-------------|---------------|-----|
| **H1** | 48px / 3rem | Bold (700) | 1.15 (56px) | -0.02em | Titulo principal da pagina |
| **H2** | 36px / 2.25rem | Bold (700) | 1.2 (44px) | -0.015em | Secoes principais |
| **H3** | 28px / 1.75rem | Medium (500) | 1.25 (36px) | -0.01em | Subsecoes |
| **H4** | 22px / 1.375rem | Medium (500) | 1.3 (28px) | 0 | Titulos de cards, blocos |
| **H5** | 18px / 1.125rem | Bold (700) | 1.35 (24px) | 0.01em | Labels de secao, categorias |
| **H6** | 16px / 1rem | Bold (700) | 1.4 (22px) | 0.02em | Subtitulos menores, tags |
| **Body** | 16px / 1rem | Regular (400) | 1.6 (26px) | 0 | Texto principal, paragrafos |
| **Body Small** | 14px / 0.875rem | Regular (400) | 1.5 (21px) | 0.005em | Texto secundario, notas |
| **Caption** | 12px / 0.75rem | Regular (400) | 1.4 (17px) | 0.02em | Legendas, footnotes, metadata |
| **Overline** | 12px / 0.75rem | Bold (700) | 1.4 (17px) | 0.1em | Labels acima de titulos, categorias |

### Overline (Detalhe)

O estilo **overline** e usado acima de titulos para contextualizar a secao:

```
SUSTENTABILIDADE              ← Overline: 12px, Bold, uppercase, letter-spacing 0.1em
Nosso Compromisso             ← H2: 36px, Bold
com o Futuro
```

- Sempre em **uppercase**
- Cor: Cinza Medio (#6B7280) ou cor primaria da secao
- Espacamento inferior: 8px ate o titulo

---

## Regras de Line-Height

| Contexto | Line-Height | Motivo |
|----------|------------|--------|
| Headlines (H1-H3) | 1.15 — 1.25 | Compacto para impacto visual |
| Subtitulos (H4-H6) | 1.3 — 1.4 | Equilibrio entre compacto e legivel |
| Body text | 1.6 | Conforto de leitura em paragrafos longos |
| Captions | 1.4 | Compacto para informacao auxiliar |

---

## Regras de Letter-Spacing

| Contexto | Letter-Spacing | Motivo |
|----------|---------------|--------|
| Headlines grandes (H1-H2) | Negativo (-0.02em a -0.015em) | Compacta letras grandes para coesao |
| Body text | 0 (padrao) | Espacamento natural para leitura |
| Captions e overlines | Positivo (0.02em a 0.1em) | Abre texto pequeno para legibilidade |
| Uppercase text | +0.05em a +0.1em | Compensa o adensamento visual do uppercase |

---

## Regras de Uso por Peso

### Light (300)
- Numeros estatisticos grandes ("1060+ projetos")
- Citacoes em destaque (blockquotes)
- Textos decorativos em pecas visuais
- **NAO usar** para body text ou textos longos (legibilidade reduzida)

### Regular (400)
- Todo corpo de texto e paragrafos
- Listas e bullet points
- Descricoes e explicacoes
- Textos de interface (menus, navegacao)

### Medium (500)
- Subtitulos (H3, H4)
- Labels de formularios
- Nomes em cards
- Enfase moderada dentro de paragrafos

### Bold (700)
- Titulos principais (H1, H2)
- Headlines de campanhas
- CTAs e botoes
- Palavras-chave em destaque dentro de textos
- Overlines em uppercase

---

## Regras de Pareamento

### Headlines + Body
```
H1 Bold + Body Regular     → Contraste maximo, uso padrao
H2 Bold + Body Regular     → Secoes de conteudo
H3 Medium + Body Regular   → Subsecoes, contraste moderado
```

### Destaque dentro de texto
```
Body Regular com palavras em Bold → enfase pontual
Body Regular com palavras em Medium → enfase sutil
```

### Combinacoes a Evitar
- Light + Regular no mesmo bloco (contraste insuficiente entre pesos)
- Bold para paragrafos inteiros (cansa a leitura)
- Mais de 2 pesos diferentes no mesmo bloco de texto
- Italico nao faz parte do sistema — usar **Bold** ou **cor** para enfase

---

## Escala Responsiva

### Desktop (>= 1024px)
Usar a escala padrao conforme tabela de hierarquia.

### Tablet (768px — 1023px)
| Nivel | Tamanho Desktop | Tamanho Tablet |
|-------|----------------|---------------|
| H1 | 48px | 40px |
| H2 | 36px | 30px |
| H3 | 28px | 24px |
| Body | 16px | 16px |

### Mobile (<= 767px)
| Nivel | Tamanho Desktop | Tamanho Mobile |
|-------|----------------|---------------|
| H1 | 48px | 32px |
| H2 | 36px | 26px |
| H3 | 28px | 22px |
| H4 | 22px | 20px |
| Body | 16px | 16px |
| Caption | 12px | 12px |

**Regra:** body text e caption nunca diminuem abaixo do tamanho padrao em nenhum breakpoint.

---

## Cores Tipograficas

| Elemento | Cor | HEX |
|----------|-----|-----|
| Texto principal | Grafite | #2D2D2D |
| Texto secundario | Cinza Medio | #6B7280 |
| Texto sobre fundo escuro | Branco | #FFFFFF |
| Links | Teal Futuro | #00A5B8 |
| Links hover | Azul Petroleo | #005F73 |
| Overlines | Cinza Medio ou cor da secao | #6B7280 / variavel |

---

## Implementacao CSS

```css
:root {
  /* Font families */
  --font-primary: 'Inter', 'Helvetica Neue', Helvetica, Arial, sans-serif;

  /* Font sizes */
  --text-h1: 3rem;        /* 48px */
  --text-h2: 2.25rem;     /* 36px */
  --text-h3: 1.75rem;     /* 28px */
  --text-h4: 1.375rem;    /* 22px */
  --text-h5: 1.125rem;    /* 18px */
  --text-h6: 1rem;        /* 16px */
  --text-body: 1rem;      /* 16px */
  --text-body-sm: 0.875rem; /* 14px */
  --text-caption: 0.75rem;  /* 12px */

  /* Font weights */
  --font-light: 300;
  --font-regular: 400;
  --font-medium: 500;
  --font-bold: 700;

  /* Line heights */
  --lh-tight: 1.15;
  --lh-snug: 1.25;
  --lh-normal: 1.4;
  --lh-relaxed: 1.6;
}
```

---

## Checklist de Aplicacao

- [ ] Familia correta usada (Helvetica Neue impresso / Inter digital)
- [ ] Hierarquia respeitada (H1 > H2 > H3 > ... > Caption)
- [ ] Maximo 2 pesos por bloco de texto
- [ ] Line-height adequado ao contexto
- [ ] Escala responsiva aplicada para mobile/tablet
- [ ] Contraste de cor do texto verificado (WCAG AA)
- [ ] Overlines em uppercase com letter-spacing expandido
- [ ] Sem uso de italico (usar bold ou cor para enfase)
