# Artigo para o Site NTICS — Pagina HTML Completa

> Recebe conteudo de artigo (markdown ou texto), gera imagens fotorrealistas via Leonardo AI Nano Banana 2, monta pagina HTML completa com design system NTICS Brand Book v2.0, header/footer oficial do site ntics.com.br, e salva tudo pronto para publicacao.

> 📚 **Referência Leonardo AI:** Este workflow tem estrutura validada — siga-o como fonte primária. Se surgir erro de API, dúvida sobre payload ou resultado visual inesperado, consulte `workflows/marketing/referencia/leonardo_ai_core.md` como base de conhecimento complementar (erros conhecidos, modos, exemplos).

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
   - **1 hero** (capa do artigo) — cena que represente o tema geral (banner WordPress)
   - **2 imagens inline** — entre secoes, representando temas especificos
   - ~~3 imagens related posts~~ (o site WordPress/Uncode cuida dos related posts)
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

#### Download das imagens:
- Baixar todas para a mesma pasta do HTML
- Nomes padrao: `hero-{slug}.jpg`, `img-{descricao-curta}.jpg`

### Fase 3: Montagem do HTML

**IMPORTANTE:** O site ntics.com.br (WordPress 6.9 + Uncode + WPBakery) ja cuida do header, navbar, banner/hero image, titulo, metadata, related posts, CTA e footer. Nos produzimos **apenas o corpo do artigo**.

**Script:** `tools/content-gen/gerar_artigo_site.py` — gera HTML body + imagens.

#### Output: HTML self-contained para preview

O HTML e um arquivo completo para abrir no navegador (preview), mas o conteudo e apenas o `<article>`:

```html
<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <style>/* CSS minimo: tipografia Inter, cores Brand Book, componentes */</style>
</head>
<body>
  <article class="article-body">
    <!-- APENAS o corpo do texto — do lead ao boilerplate NTICS -->
  </article>
</body>
</html>
```

**Nao inclui:** top bar, navbar, hero section, CTA box, author box, related posts, footer.

#### Estrutura do corpo do artigo

```
ARTICLE BODY (<article class="article-body">, max 760px)
  - Lead (20px, azul petroleo, border-bottom)
  - Resumo Executivo (box com border-top azul petroleo, fundo cinza)
  - Secoes H2 com numero colorido verde (01, 02, 03...)
  - H3 subsecoes
  - Paragrafos (16px, line-height 1.75)
  - Tabelas (header azul petroleo, hover sutil)
  - Blockquotes (borda esquerda verde, fundo cinza claro)
  - Listas (marker verde)
  - Imagens inline (border-radius 16px, figcaption)
  - Componentes especiais (quando aplicavel):
    - Stats row (4 colunas de metricas)
    - Signs grid (cards com borda colorida)
    - Elements grid (cards para pilares/elementos)
    - Model layers (barras laterais coloridas)
  - Referencias (numeradas, links teal)
  - Ultimo paragrafo: boilerplate NTICS (fundacao, numeros, metodo)
```

#### Componentes especiais por tipo de conteudo

**Se o artigo tem lista de elementos/pilares** (3-5 itens com titulo + descricao):
- Usar `.elements-grid` com cards com borda superior colorida alternante

**Se o artigo tem modelo em camadas/etapas** (sequencia numerada):
- Usar `.model-layers` com barras laterais nas cores: azul petroleo, teal, verde, rosa

**Se o artigo tem dados estatisticos** (numeros de destaque):
- Usar `.stats-row` com 4 colunas de metricas (numero grande + label)

### Fase 4: Salvar e Abrir

1. Salvar HTML em: `output/marketing/artigos/artigo-{slug}.html`
2. Imagens na mesma pasta (`output/marketing/artigos/`)
3. Abrir no navegador com `start "" "caminho/do/arquivo.html"`

---

## Checklist Final

- [ ] Hero com imagem fotorrealista Nano Banana 2 (para banner WordPress)
- [ ] 2 imagens inline nas secoes relevantes
- [ ] HTML contem APENAS corpo do artigo (sem header, navbar, CTA, footer)
- [ ] Lead paragraph em azul petroleo com border-bottom
- [ ] Resumo executivo com box destacado (border-top azul petroleo)
- [ ] Tipografia Inter via Google Fonts
- [ ] Cores do Brand Book v2.0
- [ ] H2 com numeros coloridos verdes (01, 02, 03...)
- [ ] Tabelas com header azul petroleo
- [ ] Blockquotes com borda verde + fundo cinza
- [ ] Ultimo paragrafo: boilerplate NTICS (fundacao, numeros, metodo)
- [ ] Responsivo (breakpoints 1023px e 639px)
- [ ] Aberto no navegador para revisao visual
- [ ] HTML pronto para colar no WordPress/WPBakery
