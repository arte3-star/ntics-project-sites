# Template de Prompt — Capa de Vídeo 9:16 NTICS

> Padrão consolidado a partir de dois casos validados: Global Goals Educa (Áster) e Negócio Cultural Itapoá (Porto Itapoá). Usar como base para qualquer capa de Reels/TikTok.

---

## Regra de Zona Segura (obrigatória)

Em uma imagem 9:16, o Instagram faz um recorte 4:5 para exibição no feed.  
**Os 12% superiores e 12% inferiores são cortados.**  
**Toda informação relevante deve estar nos 76% centrais.**

```
┌─────────────────────────┐  0%
│   ZONA CORTADA (topo)   │  12%   ← só fundo/blur, sem texto
├─────────────────────────┤
│                         │
│   ZONA SEGURA           │  76%   ← ÚNICO lugar onde texto e logos podem aparecer
│   (todo o conteúdo      │
│    fica aqui)           │
│                         │
├─────────────────────────┤  88%
│   ZONA CORTADA (base)   │  12%   ← só fundo/blur, sem texto
└─────────────────────────┘  100%
```

---

## Estrutura interna da Zona Segura (76%)

Dentro dos 76%, dividir em três sub-zonas:

```
┌─────────────────────────┐  12%   ← início da zona segura
│                         │
│   FOTO (com blur suave) │  ~40%  ← foto visível com atmosfera, sem texto
│                         │
├ ─ ─ ─ gradiente ─ ─ ─ ─┤  ~52%  ← transição suave foto → bloco de cor
│                         │
│   BLOCO DE COR          │  ~30%  ← headline + subtítulo + body text
│   (headline + texto)    │
│                         │
│   ESPAÇO VAZIO          │  ~6%   ← margem de respiro antes da zona cortada
└─────────────────────────┘  88%   ← fim da zona segura
```

---

## Template de Prompt (copiar e preencher)

```
Vertical 9:16 social media video cover, full bleed, no borders.

SAFE ZONE RULE: The top 12% and bottom 12% of the image are cut off when displayed
in Instagram feed (4:5 crop). All text and important elements MUST be placed ONLY
in the MIDDLE 76% of the image. The top and bottom strips contain only the background
with no text or important elements.

BACKGROUND (full bleed, 0% to 100%): [FOTO DE REFERÊNCIA] extends edge to edge.
In the top and bottom cut zones, apply a soft gaussian blur overlay with slightly
desaturated colors and a dreamy atmosphere. No text anywhere outside the safe zone.

UPPER SAFE ZONE (12% to 52%): the reference photo visible through a soft blur overlay,
colors slightly desaturated. No text, no logos in this area.

SMOOTH GRADIENT TRANSITION at ~52%: seamless blend from the photo blur above into the
solid [COR PRINCIPAL] block below.

TEXT ZONE (52% to 82%): solid [COR PRINCIPAL HEX] background.
All text centered, strictly inside this zone:

  Line 1 — LARGE BOLD UPPERCASE white sans-serif: [HEADLINE LINHA 1]
  Line 2 — LARGE BOLD UPPERCASE white sans-serif: [HEADLINE LINHA 2]
  
  Below: medium weight white text: [SUBTÍTULO]
  
  Below: smaller regular white text: [BODY TEXT]
  Highlight words in bright yellow: [PALAVRAS EM DESTAQUE]

  Leave ~6% empty space at the bottom of this zone before the cut area.
  [OPCIONAL: thin horizontal gradient stripe — green → teal → pink — at ~83%, full width]

BOTTOM SAFE MARGIN (82% to 88%): [COR PRINCIPAL] background, completely empty.
BOTTOM CUT ZONE (88% to 100%): background only, no elements.

No tricolor stripe at the edge. No institutional logos unless specified.
Portuguese accents must be preserved (Ã, Ç, É, Á, Ô).
```

---

## Preenchimento para Cultura Robótica / Áster

| Campo | Valor |
|-------|-------|
| Foto de referência | `082_robotica-escolas...instrutor.jpg` |
| Cor principal | `#367C2B` (verde escuro Áster) |
| Headline linha 1 | `CULTURA` |
| Headline linha 2 | `ROBÓTICA` |
| Subtítulo | `Teatro, arte e robótica na escola pública` |
| Body text | `Sidrolândia, Maracaju e São Gabriel — MS` |
| Destaques em amarelo | `teatro, arte e robótica`, `São Gabriel` |
| Stripe gradiente | Não |

---

## Regras fixas (nunca quebrar)

1. **Nunca colocar texto fora da zona segura** (12-88%)
2. **Nunca incluir a régua institucional** (Lei Rouanet, logos, Ministério) em posts de redes sociais
3. **Deixar espaço vazio na base da zona segura** — ~6% de margem antes de 88%
4. **Foto como fundo nos cortes** — o blur da foto preenche os 12% de cima e de baixo
5. **Prompt sub-1500 chars** para evitar VALIDATION_ERROR no nano-banana-2
6. **prompt_enhance: OFF** sempre — ON reescreve o prompt e destrói as zonas
7. **Máximo 3 image_references** por geração no nano-banana-2

---

## Dimensões válidas (nano-banana-2, 9:16)

| Tamanho | Dimensões |
|---------|-----------|
| Small | 768 × 1376 |
| Medium | 1536 × 2752 (recomendado) |
| Large | 3072 × 5504 |

---

## Conexão com outros workflows

| Arquivo | Relação |
|---------|---------|
| `capa_video.md` | SOP completo de geração de capa de vídeo |
| `leonardo_ai_core.md` | Referência de endpoints, modelos e parâmetros |
| `leonardo_ai_cookbook.md` | Erros conhecidos e exemplos completos |
