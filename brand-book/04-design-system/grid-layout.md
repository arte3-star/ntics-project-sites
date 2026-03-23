# Grid & Layout — NTICS Projetos

> Brand Book v2.0 | Atualizado: Março 2026

---

## Sistema de Grid

### Grid Base: 12 Colunas

| Propriedade | Mobile | Tablet | Desktop | Wide |
|-------------|--------|--------|---------|------|
| **Breakpoint** | 0 – 639px | 640 – 1023px | 1024 – 1279px | 1280px+ |
| **Colunas** | 4 | 8 | 12 | 12 |
| **Gutter** | 16px | 24px | 24px | 24px |
| **Margem lateral** | 16px | 32px | 48px | auto (centralizado) |
| **Max-width** | 100% | 100% | 100% | 1280px |

---

## Espaçamento (Spacing Scale)

Base: **4px**

| Token | Valor | Uso |
|-------|-------|-----|
| `xs` | 4px | Espaço mínimo entre ícones e labels |
| `sm` | 8px | Padding interno de badges e tags |
| `md` | 16px | Espaçamento entre elementos inline |
| `lg` | 24px | Espaçamento entre componentes |
| `xl` | 32px | Separação de seções menores |
| `2xl` | 48px | Separação entre seções de página |
| `3xl` | 64px | Padding de hero sections |
| `4xl` | 96px | Separação entre capítulos/módulos |

---

## Composição de Blocos Geométricos

Os blocos geométricos são o **elemento visual central** da NTICS v2.0. Regras de composição:

### Princípios

1. **Assimetria intencional** — blocos nunca devem estar perfeitamente simétricos ou centralizados
2. **Sobreposição controlada** — blocos podem se sobrepor em até 30% da área
3. **Hierarquia por tamanho** — o bloco maior carrega a informação principal
4. **Cores da paleta** — cada bloco usa uma cor da paleta NTICS (nunca cores fora da paleta)
5. **Border-radius consistente** — usar `lg` (16px) ou `xl` (24px) em todos os blocos

### Regras de Composição

| Regra | Especificação |
|-------|---------------|
| **Mínimo de blocos** | 2 por composição |
| **Máximo de blocos** | 5 por composição (evitar poluição) |
| **Máximo de cores** | 3 cores diferentes por composição |
| **Sobreposição** | Até 30% da área do bloco menor |
| **Espaçamento entre blocos** | 0 (sobrepostos) ou `md` (16px) quando separados |
| **Opacidade** | Blocos sólidos (100%) — não usar opacidade/transparência |
| **Blocos sobre fotos** | Permitido como overlay parcial (máximo 40% da foto) |

### Tamanhos Recomendados

| Contexto | Bloco Principal | Bloco Secundário | Bloco Acento |
|----------|----------------|------------------|--------------|
| **Hero section** | 60-80% da largura | 30-40% | 15-20% |
| **Card** | 100% da largura | 50-60% | 20-30% |
| **Sidebar** | 80% da largura | 40-50% | — |
| **Background** | 100% | 60-70% | 30-40% |

---

## Engrenagens Decorativas

As engrenagens expandem o símbolo da lâmpada como elemento decorativo.

### Regras

| Propriedade | Especificação |
|-------------|---------------|
| **Cor** | Branco (#FFFFFF) sobre fundos coloridos, ou cor da paleta sobre fundos claros |
| **Opacidade** | 10-20% quando em background, 100% quando decorativas |
| **Tamanho** | Variado (3 tamanhos: pequena, média, grande) |
| **Posição** | Cantos, laterais ou dispersas — nunca centralizadas |
| **Máximo** | 3 engrenagens por composição |
| **Interação com texto** | Engrenagens sempre atrás do texto (z-index inferior) |

---

## Layouts de Página

### Hero Section
```
┌─────────────────────────────────────────────────┐
│ ┌──────────────────────┐                        │
│ │  BLOCO COLORIDO      │     ⚙ (engrenagem)    │
│ │  Título H1           │                        │
│ │  Subtítulo           │  ┌─────────────┐       │
│ │  CTA Button          │  │ BLOCO ACENTO│       │
│ └──────────────────────┘  └─────────────┘       │
└─────────────────────────────────────────────────┘
```

### Seção de Conteúdo
```
┌─────────────────────────────────────────────────┐
│  OVERLINE (categoria)                           │
│  Título H2                                      │
│                                                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐      │
│  │  Card 1  │  │  Card 2  │  │  Card 3  │      │
│  │          │  │          │  │          │      │
│  └──────────┘  └──────────┘  └──────────┘      │
└─────────────────────────────────────────────────┘
```

### Seção com Foto + Bloco
```
┌─────────────────────────────────────────────────┐
│  ┌──────────────────┐  ┌──────────────────────┐ │
│  │                  │  │  BLOCO COLORIDO      │ │
│  │   FOTO           │  │                      │ │
│  │   (com overlay   │  │  Texto descritivo    │ │
│  │    de bloco)     │  │  sobre o projeto     │ │
│  │                  │  │                      │ │
│  └──────────────────┘  └──────────────────────┘ │
└─────────────────────────────────────────────────┘
```

---

## Responsividade

### Comportamento dos Blocos

| Breakpoint | Comportamento |
|------------|---------------|
| **Desktop** | Composições laterais com sobreposição |
| **Tablet** | Blocos empilham parcialmente, mantêm sobreposição reduzida |
| **Mobile** | Blocos empilham verticalmente, sem sobreposição |

### Cards

| Breakpoint | Layout |
|------------|--------|
| **Desktop** | 3 ou 4 por linha |
| **Tablet** | 2 por linha |
| **Mobile** | 1 por linha (full width) |
