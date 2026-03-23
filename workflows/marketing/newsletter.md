# /newsletter — ESG em Foco | NTICS Projetos

Gera a newsletter completa da NTICS e cria um rascunho HTML no Gmail pronto para enviar.

---

## Antes de Comecar

Leia estes arquivos para calibrar tom e dados:

1. `brand-book/02-identidade-verbal/tom-de-voz.md`
2. `brand-book/02-identidade-verbal/mensagens-chave.md`
3. `brand-book/03-identidade-visual/cores.md`

---

## Inputs

Pergunte ao usuario (use AskUserQuestion):

| Campo | Obrigatorio | Descricao |
|-------|-------------|-----------|
| `artigo` | Sim | Titulo + resumo + link do artigo postado no site |
| `destaques` | Sim | Metricas, conquistas ou dados relevantes do periodo |
| `noticias` | Sim | Tema ou 3 boas noticias ESG/CSR (ou pedir para pesquisar) |
| `leis_incentivo` | Nao | Atualizacoes sobre leis de incentivo fiscal |
| `numero_edicao` | Sim | Numero da edicao |
| `periodicidade` | Sim | "semanal" ou "mensal" |

Se o usuario nao fornecer noticias, pesquise usando WebSearch por "boas noticias ESG sustentabilidade Brasil {mes} {ano}".

---

## Estrutura do Email (Template v4 Aprovado)

### HEADER
- Fundo: Azul Petroleo `#005F73`, border-radius topo `12px`
- **Esquerda:** Logo NTICS branca SVG `https://ntics.com.br/wp-content/uploads/2023/05/logo-ntics-branco-01.svg` (width 140px)
- **Direita:** Titulo "ESG em Foco" (26px bold branco) + subtitulo "Noticias que transformam" (13px branco 60%)
- **Barra inferior:** 6 blocos quadriculados de cor solida (6px altura), cada um com 16.66% de largura:
  - `#3DAA35` | `#00A5B8` | `#005F73` | `#D41A6A` | `#E86428` | `#F5B800`
- **SEM links de navegacao** no header

### EDITION BADGE
- "NEWSLETTER SEMANAL" (ou MENSAL) + "Edicao #{numero} — {data}"

### ARTIGO DESTAQUE
- Badge verde "Artigo da Semana" (ou "do Mes")
- **Imagem:** Buscar no Unsplash uma imagem relacionada ao tema do artigo (URL formato: `https://images.unsplash.com/photo-{ID}?w=1200&h=480&fit=crop&q=80`). Usar width 536, border-radius 12px
- **Overline:** Categoria em `#00A5B8` (ex: "ESG • INOVACAO")
- **Titulo:** Max 80 chars, font-size 22px bold `#2D2D2D`
- **Resumo:** 2-3 frases, 15px, line-height 24px
- **Meta:** "X min de leitura • Por {autor}"
- **CTA:** Botao verde `#3DAA35`, border-radius 8px, texto "Ler artigo completo →"
- Link do CTA aponta para o artigo no site

### DESTAQUES DA SEMANA/MES
- Overline teal `#00A5B8` + titulo "Impacto Social em Numeros" (20px bold)
- **Grafico ISD:** Card cinza `#F4F4F4` com barras horizontais coloridas (Verde, Teal, Rosa, Laranja, Amarelo) + labels + valores em R$. Total com border-top `#E4E2E1`
- **3 Stats Cards:** Lado a lado, cada um com:
  - Border-top 3px (Verde, Teal, Rosa)
  - Numero grande 28px font-weight 300 na cor do border
  - Label 10px uppercase cinza

### BOAS NOTICIAS DO MUNDO
- Overline amarelo `#F5B800` + titulo "Noticias que inspiram" (20px bold)
- **Noticia 1 (principal):** Card com IMAGEM GRANDE no topo (Unsplash, width 536, border-radius 10px 10px 0 0) + texto abaixo com fundo claro, border-left 3px na cor do ODS, link "Ler mais →"
- **Noticia 2:** Card HORIZONTAL — thumbnail esquerda (160x120px, border-radius 10px 0 0 10px) + texto direita com fundo claro e border-left 2px teal
- **Noticia 3:** Card HORIZONTAL — mesmo layout da noticia 2, border-left 2px rosa
- **IMPORTANTE:** Sempre usar imagens reais (Unsplash) em vez de icones emoji. Buscar imagens relacionadas ao tema de cada noticia

### LEIS DE INCENTIVO (se houver)
- Overline roxo `#6B2D7B` + titulo "Atualizacoes Regulatorias" (20px bold)
- Cards com border-left 3px colorido + fundo claro:
  - Roxo `#F9F5FC` para Rouanet (com badge "NOVO" se aplicavel)
  - Verde `#EBF8F2` para Lei do Esporte
  - Teal `#E0F4F7` para FIA
- CTA ghost: "Fale sobre incentivos fiscais" com border `#005F73`

### CTA FINAL
- Fundo Azul Petroleo `#005F73`, texto centralizado
- Titulo 20px bold branco + subtitulo 13px branco 70%
- Botao laranja `#E86428`, border-radius 8px, link para `https://ntics.com.br/fale-com-a-ntics/`

### FOOTER (compacto, 3 linhas)
- **Linha 1:** Logo NTICS branca (100px) a esquerda + icones sociais a direita (28x28px cada):
  - Instagram: `https://www.instagram.com/nticsprojetos`
  - LinkedIn: `https://www.linkedin.com/company/nticsprojetos`
  - YouTube: `https://www.youtube.com/@nticsprojetos/featured`
  - Facebook: `https://www.facebook.com/nticsprojetoss`
  - Icones via CDN iconfinder (128px versions)
- **Linha 2:** Links (Projetos, Equipe, Notes, Relatorio) a esquerda + `contato@ntics.com.br` a direita
- **Linha 3:** Copyright + telefone (11) 3042-4023 + Descadastrar + Privacidade
- Fundo: `#2D2D2D`, border-radius inferior 12px

---

## Links Reais do Site NTICS

| Destino | URL |
|---------|-----|
| Site | `https://ntics.com.br` |
| Projetos | `https://ntics.com.br/pilar-desenvolvimento-sustentavel/` |
| Equipe | `https://ntics.com.br/equipe-ntics/` |
| Notes/Blog | `https://ntics.com.br/notes` |
| Relatorio | `https://ntics.com.br/relatorio` |
| Contato | `https://ntics.com.br/fale-com-a-ntics/` |
| Privacidade | `https://ntics.com.br/politica-de-privacidade-e-seguranca-de-dados/` |
| Logo branca SVG | `https://ntics.com.br/wp-content/uploads/2023/05/logo-ntics-branco-01.svg` |
| Logo colorida SVG | `https://ntics.com.br/wp-content/uploads/2023/05/ntics-colorido-01.svg` |
| Instagram | `https://www.instagram.com/nticsprojetos` |
| LinkedIn | `https://www.linkedin.com/company/nticsprojetos` |
| YouTube | `https://www.youtube.com/@nticsprojetos/featured` |
| Facebook | `https://www.facebook.com/nticsprojetoss` |
| Email | `contato@ntics.com.br` |
| Telefone | `+55 (11) 3042-4023` |

---

## Regras de Email HTML

| Regra | Especificacao |
|-------|---------------|
| Largura maxima | 600px |
| Fontes | Arial, Helvetica (webmail safe) |
| Botoes | Min 44px altura, border-radius 8px |
| Imagens | Alt text obrigatorio, max 200KB, usar URLs externas (Unsplash) |
| Layout | Tables para estrutura (nao divs), inline styles |
| Dark mode | Classes `.dark-bg`, `.dark-card`, `.dark-text` |
| Responsive | Media query max-width 620px, classes `.mobile-stack`, `.mobile-hide` |

---

## Execucao

### Fase 1: Coleta
1. Receber inputs do usuario
2. Se faltar noticias, pesquisar via WebSearch
3. Buscar imagens no Unsplash para artigo + cada noticia

### Fase 2: Subject Line
Gerar 3 opcoes (max 50 chars cada):
- **Curiosity Gap:** Cria lacuna de informacao
- **Result/Proof:** Lidera com resultado
- **Question:** Pergunta que forca reflexao

### Fase 3: Montar HTML
Construir o HTML completo seguindo a estrutura acima, preenchendo com o conteudo real.

### Fase 4: Criar Rascunho no Gmail
Usar `mcp__claude_ai_Gmail__gmail_create_draft` com:
- `subject`: Subject line escolhida
- `contentType`: "text/html"
- `body`: HTML completo
- Retornar o link do rascunho ao usuario

### Fase 5: Mostrar Resumo
Apresentar ao usuario:
- Link do rascunho no Gmail
- Subject line escolhida
- Preview das secoes

---

## Checklist de Qualidade

- [ ] Subject line < 50 chars, sem spam words
- [ ] Preheader complementa o subject (nao repete)
- [ ] Header: logo + titulo, SEM links de nav, barra quadriculada
- [ ] Artigo com imagem real (Unsplash), nao placeholder
- [ ] Noticias com imagens reais, nao icones emoji
- [ ] Stats com numeros concretos e verificaveis
- [ ] Leis com status atualizado e prazos
- [ ] Tom: 60% formal, 55% tecnico, 65% inspiracao
- [ ] Todos os links apontando para URLs reais do site
- [ ] Footer compacto (3 linhas) com icones sociais reais
- [ ] Rascunho criado no Gmail com sucesso
