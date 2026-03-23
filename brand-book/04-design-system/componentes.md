# Componentes — NTICS Projetos

> Brand Book v2.0 | Atualizado: Março 2026
> Framework: Atomic Design (Brad Frost)

---

## Atoms (Elementos Mínimos)

### Botões

| Variante | Background | Texto | Border-radius | Uso |
|----------|-----------|-------|---------------|-----|
| **Primary** | Verde Regeneração `#3DAA35` | Branco | 8px | CTAs principais: "Fale com nosso time", "Invista com propósito" |
| **Secondary** | Transparente | Azul Petróleo `#005F73` | 8px | Ações secundárias: "Saiba mais", "Ver projetos" |
| **Accent** | Rosa Transformação `#D41A6A` | Branco | 8px | Destaques de campanha, urgência positiva |
| **Ghost** | Transparente + borda 1px | Cor da borda | 8px | Ações terciárias, filtros |

**Estados:** hover (darken 10%), active (darken 15%), disabled (opacity 50%)
**Padding:** 12px 24px (md) | 16px 32px (lg)

### Tags / Badges

| Variante | Uso | Exemplo |
|----------|-----|---------|
| **ODS** | Identificar ODS relacionado | `ODS 4` em badge colorido |
| **Status** | Estado de projeto/processo | `Em andamento`, `Concluído` |
| **Categoria** | Tipo de conteúdo | `Educação`, `ESG`, `Cultura` |

**Estilo:** background com 15% opacity da cor + texto na cor sólida. Border-radius: full (pill).

### Ícones

| Estilo | Uso |
|--------|-----|
| **Line icons** (1.5px stroke) | Navegação, sustentabilidade, educação |
| **ODS icons** (oficiais ONU) | Referência a ODS específicos |
| **Engrenagens** (custom) | Elementos decorativos da marca |

---

## Molecules (Combinações)

### Card de Projeto

```
┌────────────────────────────┐
│  ┌──────────────────────┐  │
│  │     FOTO             │  │
│  │     (ratio 16:9)     │  │
│  └──────────────────────┘  │
│                            │
│  [ODS 4] [ODS 17]         │
│                            │
│  Título do Projeto         │
│  Descrição curta em até    │
│  2 linhas de texto...      │
│                            │
│  📍 15 cidades             │
│  👥 10.000 pessoas         │
│                            │
│  [Ver projeto →]           │
└────────────────────────────┘
```

**Specs:**
- Border-radius: 16px
- Sombra: `md`
- Padding interno: 24px
- Foto: 100% width, ratio 16:9, border-radius top 16px
- Tags ODS: posicionadas acima do título

### Card de Indicador

```
┌──────────────────────┐
│                      │
│  11.4M+              │  ← H2, cor primária (bold)
│  Pessoas impactadas  │  ← body-small, grafite
│  desde 2012          │  ← caption, cinza médio
│                      │
└──────────────────────┘
```

**Specs:**
- Background: branco ou cinza-claro
- Border-radius: 16px
- Padding: 32px
- Número: H2 em cor primária ou secundária

### Bloco de Citação / Destaque

```
┌──────────────────────────────────────┐
│  ▌                                   │
│  ▌ "Transformamos o propósito da     │
│  ▌  sua empresa em projetos de       │
│  ▌  impacto social."                 │
│  ▌                                   │
│  ▌  — NTICS Projetos                 │
└──────────────────────────────────────┘
```

**Specs:**
- Borda esquerda: 4px sólida na cor primária
- Background: cinza-claro `#F4F4F4`
- Padding: 24px 32px
- Texto: H4 italic, grafite

---

## Organisms (Seções Completas)

### Hero Section

Composição:
- Background: bloco geométrico em cor primária (70% da área)
- Bloco secundário sobreposto (30%)
- Engrenagem decorativa no canto
- H1 + subtítulo + CTA button
- Opcional: foto com overlay de bloco

### Seção de Números / Impacto

Grid de 3-4 Cards de Indicador, com:
- Overline: categoria (ex: "IMPACTO SOCIAL")
- H2: título da seção
- Grid: 3 colunas desktop, 2 tablet, 1 mobile

### Seção de Cases / Projetos

Grid de Cards de Projeto:
- Overline + H2
- Filtros por ODS (tags interativas)
- Grid: 3 colunas desktop
- Link "Ver todos os projetos"

### Seção de Valores / Pilares

```
┌─────────────────────────────────────────────────┐
│                                                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐      │
│  │ VERDE    │  │ AZUL     │  │ ROSA     │      │
│  │          │  │          │  │          │      │
│  │ ⚙ Ícone │  │ ⚙ Ícone │  │ ⚙ Ícone │      │
│  │          │  │          │  │          │      │
│  │ Título   │  │ Título   │  │ Título   │      │
│  │ Texto    │  │ Texto    │  │ Texto    │      │
│  └──────────┘  └──────────┘  └──────────┘      │
│                                                  │
└─────────────────────────────────────────────────┘
```

Cards com background colorido (cor primária), texto branco, ícone de engrenagem.

### Footer

- Background: Grafite `#2D2D2D`
- Logo branca
- Links de navegação em branco
- Contato, endereços, redes sociais
- Selo Pacto Global ONU + ODS
- Copyright

---

## Paleta de Componentes por Contexto

| Contexto | Cores Predominantes | Componentes Chave |
|----------|--------------------|--------------------|
| **Institucional** | Azul Petróleo + Verde + Branco | Hero, cards formais, footer |
| **Projetos/Cases** | Verde + Laranja + Teal | Cards de projeto, indicadores, galeria |
| **Campanhas** | Rosa + Amarelo + Laranja | Banners, CTAs, social media |
| **ESG/Relatórios** | Azul Petróleo + Teal + Verde | Gráficos, tabelas, indicadores |
| **Inovação/IA** | Roxo + Teal + Azul Petróleo | Cards tech, badges, seções especiais |
