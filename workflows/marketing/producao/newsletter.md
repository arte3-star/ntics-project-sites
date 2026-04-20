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
| `noticias` | Sim | 3 boas noticias ESG/CSR (ou pedir para pesquisar) |
| `numero_edicao` | Sim | Numero da edicao |
| `periodicidade` | Nao | Padrao "mensal" (pode usar "semanal" para edicoes especiais) |
| `projetos_ativos` | Nao | Auto-detectado de `assets/projetos/_metadata-sites-2026.json`. Passe `--mes-referencia` para override, `--no-projetos` para desligar a secao. |

Se o usuario nao fornecer noticias, pesquise usando WebSearch por "boas noticias ESG sustentabilidade Brasil {mes} {ano}".

---

## Estrutura do Email (Template v5 Mensal, Abril/2026)

Ordem definitiva (de cima para baixo):

1. HEADER
2. EDITION BADGE
3. ARTIGO DESTAQUE
4. PROJETOS EM EXECUCAO
5. CTA DE VENDAS (fundo petroleo + botao laranja)
6. DESTAQUES (Stats/ISD)
7. BOAS NOTICIAS (compactas, sem hero)
8. FOOTER

Sem secao de Leis de Incentivo. Periodicidade padrao: mensal.

### HEADER
- Fundo: Azul Petroleo `#005F73`, border-radius topo `12px`
- **Esquerda:** Logo NTICS branca SVG `https://ntics.com.br/wp-content/uploads/2023/05/logo-ntics-branco-01.svg` (width 140px)
- **Direita:** Titulo "ESG em Foco" (26px bold branco) + subtitulo "Noticias que transformam" (13px branco 60%)
- **Barra inferior:** 6 blocos quadriculados de cor solida (6px altura), cada um com 16.66% de largura:
  - `#3DAA35` | `#00A5B8` | `#005F73` | `#D41A6A` | `#E86428` | `#F5B800`
- **SEM links de navegacao** no header

### EDITION BADGE
- "NEWSLETTER MENSAL" (ou SEMANAL em edicoes especiais) + "Edicao #{numero} — {data}"

### ARTIGO DESTAQUE
- Badge verde "Artigo da Semana" (ou "do Mes")
- **Imagem:** Buscar no Unsplash uma imagem relacionada ao tema do artigo (URL formato: `https://images.unsplash.com/photo-{ID}?w=1200&h=480&fit=crop&q=80`). Usar width 536, border-radius 12px
- **Overline:** Categoria em `#00A5B8` (ex: "ESG • INOVACAO")
- **Titulo:** Max 80 chars, font-size 22px bold `#2D2D2D`
- **Resumo:** 2-3 frases, 15px, line-height 24px
- **Meta:** "X min de leitura • Por {autor}"
- **CTA:** Botao verde `#3DAA35`, border-radius 8px, texto "Ler artigo completo →"
- Link do CTA aponta para o artigo no site

### PROJETOS EM EXECUCAO
- **Overline** Azul Petroleo `#005F73`: "EM CAMPO AGORA"
- **Titulo:** "Projetos em execucao em {Mes}/{Ano}" (20px bold)
- **Cards horizontais** (mesmo padrao das noticias 2/3): thumb 160x120 (KV do projeto) + texto com `border-left: 3px solid {accent_color do projeto}`
- **Campos por card:** nome do projeto (15px bold), "Patrocinio: {sponsors}", cidades separadas por " · ", "Inicio: DD/MM/AAAA" em `#005F73` bold
- **Limite:** 4 cards visiveis, ordenados por data de inicio mais recente. Se houver mais, linha "+N outros em execucao" centralizada abaixo
- **Fonte de dados:** `assets/projetos/_metadata-sites-2026.json` (campos `status`, `start_date`, `end_date` populados via `tools/publishing/enrich_projects_metadata.py`)
- **Filtro de mes:** `--mes-referencia "Abril/2026"` ou "2026-04" (padrao: mes atual)
- **Desligar:** `--no-projetos` ou `projetos_ctx: {}` no `--data` JSON
- **Expansoes obrigatorias:** PEC isolado vira "Empreendedorismo e Cultura"
- Secao se auto-oculta quando nao ha projetos ativos no mes

### CTA DE VENDAS
- Posicao: logo apos PROJETOS EM EXECUCAO (enquanto o interesse esta alto)
- Fundo Azul Petroleo `#005F73`, texto centralizado branco
- Titulo "Quer transformar o impacto da sua empresa?" (20px bold) + subtitulo "22 anos de experiencia em projetos com resultados mensuraveis." (13px branco 70%)
- Botao laranja `#E86428`, border-radius 8px, "Agendar conversa →" para `https://ntics.com.br/fale-com-a-ntics/`

### DESTAQUES DA SEMANA/MES
- Overline teal `#00A5B8` + titulo "Impacto Social em Numeros" (20px bold)
- **Grafico ISD:** Card cinza `#F4F4F4` com barras horizontais coloridas (Verde, Teal, Rosa, Laranja, Amarelo) + labels + valores em R$. Total com border-top `#E4E2E1`
- **3 Stats Cards:** Lado a lado, cada um com:
  - Border-top 3px (Verde, Teal, Rosa)
  - Numero grande 28px font-weight 300 na cor do border
  - Label 10px uppercase cinza

### BOAS NOTICIAS DO MUNDO (reduzida)
- Overline amarelo `#F5B800` + titulo "Rapidas para voce se inspirar" (18px bold)
- **3 cards compactos em lista vertical**, cada um com:
  - Fundo `#FAFAFA`, border-radius 6px
  - `border-left: 3px` alternando cores (verde `#3DAA35`, teal `#00A5B8`, rosa `#D41A6A`)
  - Padding 10px 14px (compacto)
  - Source em 10px bold na cor do border + titulo clicavel 13px bold + summary curta 12px cinza
  - **Sem imagens** — a secao e curta e textual, apenas para "noticias inspiram" sem competir com artigo/projetos
- Posicao no email: apos CTA e Destaques, antes do footer (fechamento leve)

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
2. Se faltar noticias, buscar dos **carrosseis de noticias ja gerados** no mes (pasta `output/marketing/carrosseis/noticias/`). Selecionar as 3 mais relevantes. Apenas se nao houver carrosseis, pesquisar via WebSearch
3. **CTAs:** Todos os links devem apontar para URLs reais publicadas no blog NTICS. Nunca usar placeholders

### Fase 1b: Busca de Imagens (Serper)

Para cada noticia e para o artigo destaque, buscar imagens reais via Serper (Google Images):

1. **Buscar com nome especifico** — usar nome da empresa/projeto + contexto:
   - Exemplo: "Porto Itapoa terminal containers", "B3 bolsa valores predio", "Petrobras biorrefino laboratorio"
   - NAO usar termos genericos como "sustainability" ou "green energy"
2. **Buscar 3-5 resultados** por noticia (`num: 5` no Serper, `gl: br`, `hl: pt-br`)
3. **Validar coerencia:** Para cada imagem selecionada, verificar:
   - A imagem mostra o que a noticia descreve? (ex: se fala de B3, a foto deve ser da B3)
   - A imagem e em contexto brasileiro? (evitar fotos em ingles para noticias BR)
   - A resolucao e suficiente? (min 400px largura para cards, 800px para hero)
   - Se a primeira opcao nao for adequada, usar a segunda/terceira
4. **Artigo destaque:** Usar imagem real do artigo no blog NTICS (se publicado). Senao, buscar via Serper
5. **Fallback:** Unsplash somente como ultimo recurso, com termos em portugues

```python
# Exemplo de busca Serper para imagens da newsletter
import requests
r = requests.post('https://google.serper.dev/images', json={
    'q': 'Porto Itapoa Santa Catarina terminal',
    'gl': 'br', 'hl': 'pt-br', 'num': 5
}, headers={'X-API-KEY': SERPER_API_KEY})
```

**Regra de ouro:** a imagem deve ser reconhecivel por quem conhece o assunto. Se alguem que trabalha na B3 vir a foto, deve reconhecer que e a B3.

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

### Fase 4b: Publicar via Brevo (alternativa ao Gmail)

Quando o usuario pedir envio via Brevo (envio em massa para subscribers):

1. **Salvar HTML** gerado na Fase 3 em `.tmp/newsletter_YYYY-MM-DD.html`
2. **Ajustar unsubscribe:** ao montar o HTML, passar `unsubscribe_url="{{ unsubscribe }}"` como string literal para que o Brevo processe o link de descadastramento automaticamente
3. **Executar:**
   ```bash
   python tools/publishing/publish_to_brevo.py \
     --html-file .tmp/newsletter_YYYY-MM-DD.html \
     --subject "Subject line escolhida" \
     --mode draft
   ```
4. Retornar o Campaign ID ao usuario para revisao no painel do Brevo

**Env vars necessarias:**
- `BREVO_API_KEY` — chave da API Brevo (obrigatoria)
- `BREVO_LIST_ID` — ID da lista de contatos no Brevo

**Quando usar cada canal:**
| Canal | Uso |
|-------|-----|
| Gmail | Testes rapidos, envios internos, revisao individual |
| Brevo | Envio em massa para subscribers, campanhas de marketing |

### Fase 5: Mostrar Resumo
Apresentar ao usuario:
- Link do rascunho no Gmail
- Subject line escolhida
- Preview das secoes

---

## Pipeline — Conexao com Outros Workflows

Este workflow e o ultimo da cadeia editorial mensal. Inputs vem de:

| Input | Fonte | Secao que alimenta |
|-------|-------|--------------------|
| Artigo do mes | `/artigo-mensal` | Artigo Destaque |
| Noticias ESG | `/carrossel-noticias` ou pesquisa propria | Boas Noticias do Mundo |
| Tema e metricas | `/plano-mensal` | Destaques + CTA Final |
| Leis de incentivo | Manual ou pesquisa | Leis de Incentivo |

### Modo Semanal vs Mensal

| Aspecto | Semanal | Mensal |
|---------|---------|--------|
| Badge | "NEWSLETTER SEMANAL" | "NEWSLETTER MENSAL" |
| Artigo | "Artigo da Semana" | "Artigo do Mes" |
| Destaques | "Destaques da Semana" | "Destaques de {Mes}" |
| Artigo hero | Opcional | Obrigatorio (vem de /artigo-mensal) |

Quando `periodicidade == "mensal"` e `artigo` inclui URL do site, o bloco Artigo Destaque deve ter:
- Imagem hero do artigo (se disponivel, usar imagem do site; senao, Unsplash)
- Excerpt editorial de 2-3 frases (tom narrativo, nao bullet points)
- Badge de categoria (ex: "Legislacao & Incentivos")
- Preheader usa o excerpt do artigo (nao o tema geral)

---

## Checklist de Qualidade

- [ ] Subject line < 50 chars, sem spam words
- [ ] Preheader complementa o subject (nao repete)
- [ ] Header: logo + titulo, SEM links de nav, barra quadriculada
- [ ] Artigo com imagem real do blog ou buscada via Serper (nome especifico)
- [ ] Secao "Projetos em execucao" presente (ou `--no-projetos` justificado)
- [ ] Cada card de projeto com KV, patrocinio, cidade(s) e data de inicio em DD/MM/AAAA
- [ ] PEC isolado expandido para "Empreendedorismo e Cultura"
- [ ] Nenhum travessao `—` em nomes/textos (regra global)
- [ ] Cada noticia com imagem buscada via Serper (nome da empresa/projeto)
- [ ] Auto-review: cada imagem faz sentido visual com sua noticia
- [ ] Nenhuma imagem generica ou em ingles para conteudo brasileiro
- [ ] Se primeira opcao de imagem nao for boa, segunda/terceira foi testada
- [ ] Stats com numeros concretos e verificaveis
- [ ] Leis com status atualizado e prazos
- [ ] Tom: 60% formal, 55% tecnico, 65% inspiracao
- [ ] Todos os links apontando para URLs reais do site
- [ ] Footer compacto (3 linhas) com icones sociais reais
- [ ] Rascunho criado no Gmail com sucesso
