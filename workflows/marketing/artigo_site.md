# Artigo para o Site NTICS — Pagina HTML Completa

> Recebe conteudo de artigo (markdown ou texto), gera imagens fotorrealistas via Leonardo AI Nano Banana 2, monta pagina HTML completa com design system NTICS Brand Book v2.0, header/footer oficial do site ntics.com.br, e salva tudo pronto para publicacao.

---

## APIs Utilizadas

| API | Uso | Modelo/Config |
|-----|-----|---------------|
| Leonardo AI | Gerar imagens fotorrealistas para hero + inline + related posts | model: nano-banana-2, 1152x896, prompt_enhance: OFF |

### Chaves (variaveis de ambiente)
- `LEONARDO_API_KEY`

---

## Inputs do Usuario

| Campo | Tipo | Obrigatorio | Descricao |
|-------|------|-------------|-----------|
| `conteudo` | markdown/texto | Sim | Artigo completo com titulo, secoes, tabelas, citacoes, referencias |
| `categoria` | string | Nao | Ex: "ESG & Governanca", "Artigos". Default: "Artigos" |
| `data` | string | Nao | Data de publicacao. Default: data atual |
| `tempo_leitura` | string | Nao | Ex: "8 min". Se vazio, calcular pelo tamanho do texto |
| `slug` | string | Nao | Nome do arquivo. Se vazio, gerar a partir do titulo |
| `related_posts` | array | Nao | Posts relacionados com titulo, URL e tag. Se vazio, buscar os 3 mais recentes em ntics.com.br/notes |

---

## Execucao

### Fase 1: Analise do Conteudo

1. Ler o conteudo do artigo fornecido
2. Identificar:
   - Titulo principal (H1)
   - Lead / paragrafo introdutorio
   - Secoes (H2) — numerar com 01, 02, 03...
   - Subsecoes (H3)
   - Tabelas
   - Citacoes / blockquotes
   - Listas
   - Referencias
3. Definir quais imagens sao necessarias:
   - **1 hero** (capa do artigo) — cena que represente o tema geral
   - **2 imagens inline** — entre secoes, representando temas especificos
   - **3 imagens related posts** — para cards de posts relacionados
4. Calcular tempo de leitura se nao fornecido (media 200 palavras/min)

### Fase 2: Geracao de Imagens (Leonardo AI Nano Banana 2)

**Endpoint:** `POST https://cloud.leonardo.ai/api/rest/v2/generations`

**Configuracao padrao para TODAS as imagens:**
```json
{
  "model": "nano-banana-2",
  "parameters": {
    "width": 1152,
    "height": 896,
    "quantity": 1,
    "prompt_enhance": "OFF"
  },
  "public": false
}
```

**Buscar resultado:** `GET https://cloud.leonardo.ai/api/rest/v1/generations/{generationId}`
- Aguardar ~50 segundos antes de verificar
- Se status PENDING, aguardar mais 20 segundos e verificar novamente

#### Regras dos prompts de imagem:
- Todas as imagens DEVEM ser fotorrealistas, estilo fotojornalistico/documental
- Incluir especificacoes de camera: Canon EOS R5, Nikon Z6, Sony A7III, lente, f-stop
- Luz natural sempre (golden hour, daylight, overcast)
- Expressoes genuinas, candidas, nao posadas
- NAO gerar cenarios fantasiosos ou futuristas — sempre realismo
- NAO incluir texto, watermarks ou logos nas imagens
- Contexto brasileiro/latino-americano quando aplicavel
- Diversidade de genero, etnia e idade
- Terminar TODOS os prompts com: "No text no watermarks no logos."

#### Prompt templates por tipo:

**Hero (tema geral do artigo):**
```
Candid documentary photograph of {cena principal do artigo}. {detalhes do ambiente}. Natural {tipo de luz} lighting. {detalhes de pessoas se aplicavel}. Shot with Canon EOS R5, 35mm f1.8, editorial documentary photography, ultra realistic, authentic expressions. No text no watermarks no logos.
```

**Imagem inline (tema de secao):**
```
{Estilo: Photojournalistic/Documentary/Authentic} photograph of {cena especifica da secao}. {detalhes de ambiente e pessoas}. Warm natural {light type}. {camera specs}, candid moment, editorial style. No text no watermarks no logos.
```

**Related post (thumbnail):**
```
{Estilo} photograph of {cena do post relacionado}. {detalhes curtos}. Natural lighting. {camera}, shallow depth of field, editorial photography. No text no watermarks no logos.
```

#### Download das imagens:
- Baixar todas para a mesma pasta do HTML
- Nomes padrao: `hero-{slug}.jpg`, `img-{descricao-curta}.jpg`, `related-{descricao}.jpg`

### Fase 3: Montagem do HTML

Usar o template HTML completo com:

#### Design System (CSS Variables — Brand Book v2.0)
```css
:root {
  --verde-regeneracao: #3DAA35;
  --azul-petroleo: #005F73;
  --rosa-transformacao: #D41A6A;
  --laranja-acao: #E86428;
  --amarelo-consciencia: #F5B800;
  --teal-futuro: #00A5B8;
  --roxo-inovacao: #6B2D7B;
  --branco: #FFFFFF;
  --cinza-claro: #F4F4F4;
  --cinza-medio: #6B7280;
  --grafite: #2D2D2D;
  --font-primary: 'Inter', 'Helvetica Neue', Arial, sans-serif;
}
```

#### Estrutura da Pagina

```
TOP BAR (azul petroleo #19496b)
  - "NTICS Notes" → /notes
  - "Acesso a Plataforma" → ntics.evolutto.com.br
  - PT | EN

NAVBAR (sticky, branco, 80px altura)
  - Logo SVG oficial: ntics.com.br/wp-content/uploads/2023/05/ntics-green-preto.svg
  - Menu: NTICS Projetos | Pilares (dropdown) | Equipe | Diferenciais | Cases | Relatorio 2023|2024 | Contato
  - CTA verde: "Fale com a NTICS"

HERO (imagem fullbleed + overlay gradient azul petroleo)
  - Blocos geometricos decorativos (verde 12% opacity, rosa 8% opacity)
  - Badge categoria (pill verde)
  - Data + Tempo de leitura
  - H1 branco, max-width 800px

ARTICLE BODY (grid centralizado, max 760px)
  - Lead (20px, azul petroleo, border-bottom)
  - Secoes H2 com numero colorido verde (01, 02, 03...)
  - H3 subsecoes
  - Paragrafos (16px, line-height 1.75)
  - Tabelas (header azul petroleo, hover sutil)
  - Blockquotes (borda esquerda verde, fundo cinza claro)
  - Listas (marker verde)
  - Imagens inline (border-radius 16px, figcaption)
  - Cards grid para elementos/pilares (borda superior colorida)
  - Modelo em camadas (barras laterais coloridas: azul, teal, verde, rosa)
  - Referencias (numeradas, links teal)
  - Author box (avatar azul petroleo, nome + descricao)
  - CTA box (azul petroleo, blocos geometricos, botao verde)

RELATED POSTS (grid 3 colunas)
  - Cards com imagem + tag + titulo + data

FOOTER (4 colunas, fundo #19496b)
  - Col 1: Logo branca + endereco Brasil (Florianopolis)
  - Col 2: Contato BR + endereco EUA (Orlando)
  - Col 3: Links "Explore"
  - Col 4: Redes sociais (Facebook, Instagram, LinkedIn)
  - Footer bottom: copyright
```

#### Componentes especiais por tipo de conteudo

**Se o artigo tem lista de elementos/pilares** (3-5 itens com titulo + descricao):
- Usar `.elements-grid` com cards com borda superior colorida alternante

**Se o artigo tem modelo em camadas/etapas** (sequencia numerada):
- Usar `.model-layers` com barras laterais nas cores: azul petroleo, teal, verde, rosa

**Se o artigo tem dados estatisticos** (numeros de destaque):
- Destacar valores em `<strong>` com cor verde na tabela

#### Template de referencia
O arquivo `artigo-csr-conselho-leonardo.html` na pasta raiz do projeto e o template de referencia completo. Usar como base e substituir o conteudo.

### Fase 4: Salvar e Abrir

1. Salvar HTML em: `g:/O meu disco/Claude Code/marketing/artigo-{slug}.html`
2. Imagens na mesma pasta
3. Abrir no navegador com `start "" "caminho/do/arquivo.html"`

---

## Checklist Final

- [ ] Hero com imagem fotorrealista Nano Banana 2
- [ ] 2 imagens inline nas secoes relevantes
- [ ] 3 imagens nos related posts
- [ ] Header com top bar + navbar oficial NTICS (logo SVG, menu completo, dropdown Pilares, CTA)
- [ ] Footer 4 colunas com enderecos BR/EUA, redes sociais, links
- [ ] Tipografia Inter via Google Fonts
- [ ] Cores do Brand Book v2.0 (proporcao 70/25/5)
- [ ] H2 com numeros coloridos verdes (01, 02, 03...)
- [ ] Tabelas com header azul petroleo
- [ ] Blockquotes com borda verde + fundo cinza
- [ ] Blocos geometricos decorativos no hero e CTA
- [ ] Author box NTICS
- [ ] CTA "Fale com a NTICS"
- [ ] Responsivo (breakpoints 1023px e 639px)
- [ ] Aberto no navegador para revisao
