# Workflow: Carrossel de Projeto para Cliente

## Objetivo
Gerar carrossel pronto para Instagram (8 cards: capa + 6 conteudo + CTA) a partir de release, TAP ou briefing do projeto, usando a identidade visual do cliente/patrocinador.

## Quando Executar
Quando precisar de carrossel de divulgacao para um projeto de cliente (pre-projeto, durante, pos-projeto). Equivalente visual do Roteiro de Edicao de Video — mesmo input, formato diferente.

## Inputs Necessarios

| Input | Fonte | Obrigatorio |
|-------|-------|-------------|
| Release, TAP ou briefing do projeto | Area de comunicacao ou workflows anteriores | Sim (pelo menos 1) |
| Foco do carrossel | Usuario define | Recomendado |
| Nome da empresa cliente/patrocinadora | Usuario | Sim |
| Site da empresa | Usuario (URL) | Sim |
| Instagram da empresa | Usuario (@ ou URL) | Nao |
| Manual de marca / KV / guia visual | Cliente | Nao |
| Logo da empresa | Cliente (PNG/SVG transparente) | Nao |
| Cores da marca | Usuario (hex ou descricao) | Nao |
| Fotos do projeto | Usuario (6 fotos) | Sim |

## Regras Criticas
- O release manda nos fatos (nomes, cidades, numeros, datas, patrocinador, publicos)
- A identidade visual do cliente manda na forma (cores, tom, estilo)
- Nunca inventar fatos. Dado ausente → [PREENCHER]
- Nunca citar: Ministerio da Cultura, Lei Rouanet, Lei de Incentivo
- Cartela final (CTA): **[PATROCINADOR] + NTICS Projetos**
- Formato padrao: 4:5 Instagram, 1856x2304 px
- Gerar apenas 1 carrossel por execucao (salvo pedido explicito de mais versoes)

---

## Passo a Passo

### Passo 1 — Identificacao (extrair do material)

Extrair do release/TAP/briefing:

| Campo | Exemplo |
|-------|---------|
| Nome do projeto | Projeto Crescer |
| N° do projeto | PRONAC 123456 |
| Cidade/UF | Recife/PE, Olinda/PE |
| Patrocinador | Empresa X |
| Realizacao | NTICS Projetos |
| Publico-alvo | Jovens de 14 a 18 anos |
| Tema/solucao | Educacao ambiental + oficinas praticas |
| CSR/impacto social | Conexao ESG, ODS relacionados |
| Atividades | Oficinas, palestras, vivencias |
| Datas | Marco a Junho 2026 |
| Locais | Escola Municipal Y, Centro Cultural Z |
| Redes sociais | @empresax / @nticsprojetos |

**IMPORTANTE:** Conferir TODOS os numeros e nomes contra o material original. Listar cada dado com sua fonte.

### Passo 2 — Definir Foco do Carrossel

Identificar a prioridade de comunicacao (perguntar ao usuario se nao estiver claro):

| Foco | Quando usar | Tom |
|------|-------------|-----|
| Convite para abertura/palestra | Evento especifico proximo | Urgencia + acolhimento. "Vem participar", "Dia X, as Yh" |
| Projeto chegando na cidade | Pre-projeto, anuncio geral | Expectativa + empolgacao. "Esta chegando", "[Cidade] vai receber" |
| Atividade especifica | Divulgar 1 frente do projeto | Foco + profundidade. Detalhar a atividade, publico, resultado esperado |
| Projeto completo (todas as atividades) | Visao geral do projeto | Amplitude + impacto. Panorama de tudo que vai/esta acontecendo |
| Institucional do patrocinador | Valorizar a marca do cliente | Credibilidade + proposito. Por que a empresa apoia, valores ESG |
| Resultados/encerramento | Pos-projeto | Celebracao + numeros. O que foi alcancado, impacto real |

O foco define quais cards ganham mais peso e como o texto e construido.

### Passo 3 — Pesquisa da Identidade Visual do Cliente

**Objetivo:** Construir perfil visual completo para guiar a geracao.

#### 3.1 — Analisar o Site

Usar WebFetch para acessar o site da empresa. Extrair:

- **Paleta de cores** — cores dominantes do header, botoes, fundos, destaques
- **Tipografia** — fontes usadas (inspecionar CSS se possivel)
- **Tom visual** — corporativo, jovem, sustentavel, premium, popular
- **Elementos graficos** — usa degrade? texturas? flat design? fotografias?
- **Slogan/tagline** — se visivel no site

#### 3.2 — Analisar o Instagram (se fornecido)

Usar WebFetch para acessar o perfil publico. Observar:

- **Estilo dos posts** — cores dominantes, filtros, estilo fotografico
- **Tom de comunicacao** — formal, descontraido, inspirador, tecnico
- **Padrao de carrossel** — se ja faz carrosseis, como sao estruturados
- **Elementos recorrentes** — badges, icones, bordas, molduras

#### 3.3 — Analisar Manual de Marca / KV (se fornecido)

- **Cores oficiais** — primaria, secundaria, complementar (hex e/ou CMYK)
- **Fontes oficiais** — titulos e corpo
- **Regras de uso** — espacamento minimo do logo, cores proibidas
- **Estilo fotografico** — se definido no manual

#### 3.4 — Montar Perfil Visual do Cliente

Compilar resumo estruturado:

```
PERFIL VISUAL — {Nome da Empresa}
================================================
Cores principais: {hex 1}, {hex 2}, {hex 3}
Cor de destaque: {hex}
Cor de fundo/degrade: {hex escuro}
Tom visual: {descricao}
Tom de comunicacao: {descricao}
Tipografia: {fonte titulos} / {fonte corpo}
Elementos graficos: {descricao}
Logo: {disponivel/nao disponivel}
Slogan: {texto ou N/A}
================================================
```

**→ PARADA 1: Apresentar perfil visual ao usuario para validacao.**

---

### Passo 4 — Redacao dos 8 Cards

#### Estrutura fixa

| Card | Funcao | Badge |
|------|--------|-------|
| 01 — Capa | Atrair atencao: nome do projeto + frase de impacto | — |
| 02 — O Projeto | Apresentar: o que e, objetivo, publico-alvo | O PROJETO |
| 03 — A Empresa | Valorizar patrocinador: quem e, por que apoia, valores ESG | [NOME DA EMPRESA] |
| 04 — Alcance | Dimensionar: numeros, cidades, beneficiarios | ALCANCE |
| 05 — Como Funciona | Explicar: metodologia, atividades, formato | COMO FUNCIONA |
| 06 — Resultados | Provar valor: resultados (pos) ou expectativas (pre) | RESULTADOS / EXPECTATIVA |
| 07 — Impacto | Inspirar: visao de longo prazo, ODS, transformacao | IMPACTO |
| 08 — CTA | Converter: chamada para acao + logos | — |

#### Adaptacao por foco

O foco definido no Passo 2 ajusta o peso dos cards:

| Foco | Cards que ganham mais espaco | Cards que podem ser mais leves |
|------|------------------------------|-------------------------------|
| Convite abertura | 01 (data/hora/local na capa), 04 (detalhes do evento), 08 (CTA com inscricao) | 07 |
| Chegando na cidade | 01 (nome cidade em destaque), 02, 04 (escala) | 06 |
| Atividade especifica | 02 (detalhar a atividade), 05 (como funciona em profundidade) | 04 |
| Projeto completo | Todos equilibrados | — |
| Institucional patrocinador | 03 (empresa como protagonista), 07 (impacto ESG) | 05 |
| Resultados/encerramento | 04 (numeros), 06 (resultados concretos), 07 (impacto) | 02, 05 |

#### Adaptacao por fase do projeto

- **Pre-projeto:** Tom de expectativa, futuro. "Vai acontecer", "esta chegando", "em breve", "[Cidade] vai receber"
- **Durante:** Tom de acontecimento, presente. "Esta acontecendo", "em andamento", "neste momento"
- **Pos-projeto:** Tom de resultado, passado. "Aconteceu", "transformou", "impactou", "alcancamos"

#### Regras de redacao

- Usar o tom de comunicacao identificado no Passo 3
- Titulo: maximo 8 palavras
- Corpo: maximo 3 linhas curtas
- Destacar palavras-chave (serao coloridas com cor de destaque do cliente)
- Numeros sempre em destaque
- Sem jargao tecnico a menos que a empresa use
- Texto fluido, claro — quem le entende sem contexto previo

**→ PARADA 2: Apresentar ficha do projeto + textos dos 8 cards ao usuario para aprovacao.**

Formato de entrega (inspirado no Roteiro de Edicao de Video):

```
========================================
FICHA DO PROJETO
========================================
Nome: {nome}
Patrocinador: {empresa}
Cidade/UF: {lista}
Publico: {descricao}
Foco do carrossel: {foco escolhido}
Fase: {pre/durante/pos}
========================================

RESUMO (1 paragrafo)
{Paragrafo descritivo do que o carrossel comunica}

========================================
TEXTOS DOS CARDS
========================================

CARD 01 — CAPA
Titulo: {texto}
Subtitulo: {texto}

CARD 02 — O PROJETO
Badge: O PROJETO
Titulo: {texto} (palavras destaque: X, Y)
Corpo: {texto}

[... cards 03-07 ...]

CARD 08 — CTA
Texto principal: {chamada para acao}
Texto secundario: {contato/redes}
Texto terciario: {slogan empresa se houver}
Logos: {patrocinador} + NTICS Projetos
```

---

### Passo 5 — Fotos do Projeto

Pedir ao usuario para colocar 6 fotos na pasta:
```
.tmp/carrosseis-cliente/{nome-empresa}/{nome-projeto}/fotos/
```

Sugerir qual foto usar para cada card baseado no conteudo:

| Card | Tipo de foto ideal |
|------|-------------------|
| 02 - O Projeto | Panoramica do espaco/atividade |
| 03 - A Empresa | Fachada/logo visivel ou evento com banner |
| 04 - Alcance | Grupo grande, plateia, multidao |
| 05 - Como Funciona | Atividade em andamento, oficina, interacao |
| 06 - Resultados | Momento de conquista, entrega, apresentacao |
| 07 - Impacto | Retrato emotivo, expressao de transformacao |

Card 01 (capa) e Card 08 (CTA) nao usam foto de referencia — capa usa descricao de cena, CTA usa fundo solido.

---

### Passo 6 — Paleta Visual dos Cards

Montar paleta baseada no perfil visual do cliente:

| Elemento | Como definir |
|----------|--------------|
| Cor de degrade principal | Cor escura da marca (ou primaria escurecida) |
| Cor de degrade alternativa | Segunda cor da marca |
| Cor dos badges | Cor primaria da marca |
| Cor de destaque (palavras-chave) | Cor vibrante/complementar da marca |
| Cor do texto | Branco (sobre fundo escuro) ou escuro (sobre fundo claro) |
| Barra gradiente no rodape | Gradiente com as 3-4 cores da marca |

**Regra:** A paleta deve ser reconhecivel como a identidade da empresa.

Cores de degrade por card (variar para ritmo visual):

| Card | Sugestao |
|------|----------|
| 01 - Capa | Cor primaria escura |
| 02 - O Projeto | Cor primaria escura |
| 03 - A Empresa | Cor secundaria |
| 04 - Alcance | Cor terciaria ou complementar |
| 05 - Como Funciona | Cor primaria escura |
| 06 - Resultados | Cor primaria escura |
| 07 - Impacto | Cor de destaque (vibrante) |
| 08 - CTA | Cor primaria escura (solido) |

---

### Passo 7 — Geracao dos Cards (Leonardo AI)

**Step 1 — Upload de cada foto:**
```python
r = requests.post('https://cloud.leonardo.ai/api/rest/v1/init-image',
    headers=headers, json={'extension': 'jpg'})
upload = r.json()['uploadInitImage']
fields = json.loads(upload['fields'])
init_id = upload['id']

with open(foto_path, 'rb') as f:
    r2 = requests.post(upload['url'], data=fields, files={'file': f})
```

**Step 2 — Gerar card com Nano Banana 2 + referencia:**
```json
{
  "model": "nano-banana-2",
  "parameters": {
    "width": 1856,
    "height": 2304,
    "prompt": "{prompt do card}",
    "quantity": 1,
    "prompt_enhance": "OFF",
    "guidances": {
      "image_reference": [
        {
          "image": {
            "id": "{init_id da foto}",
            "type": "UPLOADED"
          },
          "strength": "HIGH"
        }
      ]
    }
  },
  "public": false
}
```

**Step 3 — Buscar resultado:**
```
GET https://cloud.leonardo.ai/api/rest/v1/generations/{generationId}
```
Aguardar ~55 segundos. Se PENDING, aguardar mais 25s.

#### Prompt Template — Card 01 (Capa, sem foto de referencia)

```
A social media carousel cover card for Instagram 4:5 format. The top 60 percent is a full-bleed hyperrealistic photograph of {cena representativa do projeto — ser especifico ao conteudo do release}, shot with a Canon EOS R5 35mm lens, natural warm sunlight, photojournalistic documentary style, looks exactly like a real photograph, candid unposed moment, visible film grain ISO 800, natural imperfect lighting with real shadows, NOT AI generated NOT illustration. From 60 to 80 percent a smooth dark gradient overlay transitions from transparent to solid {cor_degrade_hex}. From 80 to 98 percent, over the solid background, centered large bold white sans-serif text reads: {titulo da capa}. Below in smaller text: {subtitulo}. Key words highlighted in {cor_destaque_hex}. At the very bottom edge flush with zero margin, a thick prominent horizontal gradient stripe bar spanning full width approximately 2 percent of total height with smooth color flow from {cor1_marca} to {cor2_marca} to {cor3_marca}. No logo. Professional editorial cover design.
```

#### Prompt Template — Cards 02-07 (com foto de referencia)

```
Social media carousel card Instagram 4:5. The top 55 percent uses the uploaded reference image as the main photograph. From 55 to 75 percent a smooth dark gradient overlay transitions from transparent to solid {cor_degrade_hex}. From 75 to 78 percent a small rounded {cor_badge_hex} badge with white text {NOME DO BADGE}. From 78 to 92 percent large bold white sans-serif headline with key words in {cor_destaque_hex}: {titulo com destaques}. From 92 to 98 percent medium white text: {corpo com palavras destaque}. At the very bottom edge flush with zero margin, a thick gradient stripe bar from {cor1_marca} to {cor2_marca} to {cor3_marca}. Clean editorial card.
```

**IMPORTANTE no prompt:**
- NAO descrever o conteudo da foto nos cards 02-07 — dizer apenas "uses the uploaded reference image"
- Indicar palavras em {cor_destaque_hex} para quebrar o branco
- Variar a cor do degrade entre os cards conforme paleta
- Sempre incluir a barra gradiente no rodape
- USAR a estrutura "From X to Y percent" para garantir posicionamento
- Badge e texto SEMPRE abaixo de 75% (area de cor solida)

#### Prompt Template — Card 08 (CTA)

```
A social media carousel final CTA card for Instagram 4:5 format. Clean solid {cor_degrade_principal_hex} background covering the entire card. The top 15 percent is empty space reserved for a logo. In the center of the card vertically, large bold white sans-serif text reads: {chamada para acao}. Below in smaller white text: {contato/perfil}. Below that in even smaller elegant white italic text: {slogan empresa}. At the very bottom edge flush with zero margin, a thick prominent horizontal gradient stripe bar spanning full width approximately 2 percent of total height with smooth color flow from {cor1_marca} to {cor2_marca} to {cor3_marca}. Minimalist professional design, no images, just elegant typography centered on solid background.
```

**Pos-processamento do CTA (logos patrocinador + NTICS):**
```python
from PIL import Image

cta = Image.open('08-cta-base.jpg').convert('RGBA')
W, H = cta.size

# Logo do patrocinador (topo)
if logo_cliente_path:
    logo_cliente = Image.open(logo_cliente_path).convert('RGBA')
    logo_max_h = int(H * 0.10)
    ratio = logo_max_h / logo_cliente.height
    logo_w = int(logo_cliente.width * ratio)
    logo_resized = logo_cliente.resize((logo_w, logo_max_h), Image.LANCZOS)
    logo_x = (W - logo_w) // 2
    logo_y = int(H * 0.04)
    cta.paste(logo_resized, (logo_x, logo_y), logo_resized)

# Logo NTICS (rodape, acima da barra gradiente)
logo_ntics = Image.open('brand-book/site/assets/LOGO NTICS - BRANCA.png').convert('RGBA')
ntics_max_h = int(H * 0.06)
ratio_n = ntics_max_h / logo_ntics.height
ntics_w = int(logo_ntics.width * ratio_n)
ntics_resized = logo_ntics.resize((ntics_w, ntics_max_h), Image.LANCZOS)
ntics_x = (W - ntics_w) // 2
ntics_y = int(H * 0.88)
cta.paste(ntics_resized, (ntics_x, ntics_y), ntics_resized)

cta.convert('RGB').save('08-cta.jpg', quality=95)
```

---

### Passo 8 — Revisao Visual

Verificar CADA card:

**Checklist:**
- [ ] Texto correto — sem erros de ortografia
- [ ] Numeros batem com o release/TAP/briefing
- [ ] Cores da marca do cliente aplicadas corretamente
- [ ] Foto de referencia usada (nao generica) nos cards 02-07
- [ ] Badge visivel com categoria correta
- [ ] Barra gradiente no rodape colada na borda inferior
- [ ] Degrade com cor correta para o card
- [ ] Palavras destaque na cor do cliente visiveis
- [ ] Sem hex codes ou codigos visiveis na imagem
- [ ] O carrossel "parece ser" da empresa cliente (identidade reconhecivel)
- [ ] Sem mencao a Ministerio da Cultura / Lei Rouanet / Lei de Incentivo
- [ ] Cartela CTA tem logos do patrocinador + NTICS Projetos

**Se algum card falhar:** regenerar APENAS esse card.

---

### Passo 9 — Organizacao e Entrega

**Estrutura da pasta:**
```
.tmp/carrosseis-cliente/{nome-empresa}/{nome-projeto}/
├── fotos/
│   ├── foto-01.jpg ... foto-06.jpg
├── 01-capa.jpg
├── 02-o-projeto.jpg
├── 03-a-empresa.jpg
├── 04-alcance.jpg
├── 05-como-funciona.jpg
├── 06-resultados.jpg
├── 07-impacto.jpg
├── 08-cta.jpg
├── perfil-visual.md
└── descricao.txt
```

**Conteudo do descricao.txt:**
```
========================================
CARROSSEL PROJETO CLIENTE
{Nome do Projeto}
{Nome da Empresa} | NTICS Projetos
Foco: {foco escolhido}
Fase: {pre-projeto / durante / pos-projeto}
========================================

--- FICHA DO PROJETO ---
Nome: {nome}
N°: {numero ou N/A}
Patrocinador: {empresa}
Cidade/UF: {lista}
Publico: {descricao}
Atividades: {lista}
Periodo: {datas}

--- PERFIL VISUAL DO CLIENTE ---
Cores: {lista hex}
Tom: {descricao}
Fonte referencia: {site / Instagram / manual}

--- CAPTION INSTAGRAM ---
{caption — tom alinhado com a comunicacao da empresa, numeros de destaque, hashtags}

--- CAPTION LINKEDIN ---
{caption — tom profissional, lista de resultados/expectativas, CTA, hashtags}

--- ORDEM DOS CARDS ---
01-capa.jpg — Capa: {titulo}
02-o-projeto.jpg — O que e o projeto (foto: foto-01)
03-a-empresa.jpg — A empresa patrocinadora (foto: foto-02)
04-alcance.jpg — Alcance e numeros (foto: foto-03)
05-como-funciona.jpg — Metodologia (foto: foto-04)
06-resultados.jpg — Resultados/expectativas (foto: foto-05)
07-impacto.jpg — Impacto e visao (foto: foto-06)
08-cta.jpg — CTA com logos patrocinador + NTICS

--- DADOS UTILIZADOS (verificados) ---
{todos os numeros e dados usados, com fonte no release/TAP}
```

---

## Variacoes Permitidas
- Projeto de uma cidade ou multi-cidades
- Carrossel institucional do patrocinador (foco 100% na empresa)
- Carrossel de convite para evento especifico (data/hora/local em destaque)
- Carrossel reunindo dois projetos do mesmo patrocinador
- Carrossel pos-projeto com foco em resultados numericos

---

## Especificacoes Tecnicas

| Elemento | Especificacao |
|----------|---------------|
| Proporcao | 4:5 (Instagram) |
| Dimensao | 1856 x 2304 px |
| Formato | JPG, quality 95 |
| Modelo IA | Nano Banana 2 (Leonardo AI v2 API) |
| Referencia foto | guidances.image_reference, type: UPLOADED, strength: HIGH |
| Foto | Topo 55%, foto real do usuario via referencia (cards 02-07) |
| Degrade | 45% inferior, cores da marca do cliente |
| Texto | Branco + destaque na cor do cliente |
| Barra gradiente | 2% da altura, colada no rodape, cores da marca |
| Logo CTA | Patrocinador (topo, 10%) + NTICS (rodape, 6%) |

---

## Regra de Posicionamento do Degrade

```
0-55%   → Foto (referencia real do projeto)
55-75%  → Zona de degrade (transparente → cor solida)
75-78%  → Badge (ja sobre cor solida)
78-92%  → Titulo (sobre cor solida)
92-98%  → Corpo do texto (sobre cor solida)
98-100% → Barra gradiente (cores da marca do cliente)
```

Nenhum texto fica sobre a zona de transicao.

---

## Conexao com Outros Workflows

| Workflow | Relacao |
|----------|---------|
| `roteiro_edicao_video.md` | Mesmo input (release/TAP). Video = versao audiovisual, Carrossel = versao visual estatica |
| `plano_divulgacao.md` | Gera os releases que alimentam este workflow |
| `termo_abertura.md` | TAP pode ser usado como input direto |
| `perfil_estrategico.md` | PEP ajuda a entender o tom do patrocinador |
| `adaptar_arte_cliente.md` | Adapta artes existentes. Este workflow CRIA artes novas |

---

## Fluxo Resumido

```
Release / TAP / Briefing
  │
  ├→ Passo 1: Identificacao (extrair dados do material)
  ├→ Passo 2: Definir foco (convite, cidade, atividade, completo, institucional, resultados)
  │
  ├→ Passo 3: Pesquisa marca (site + Instagram + manual)
  ├→ Passo 3.4: Perfil visual → VALIDACAO COM USUARIO
  │
  ├→ Passo 4: Redacao 8 cards + ficha do projeto → VALIDACAO COM USUARIO
  │
  ├→ Passo 5: Usuario coloca fotos
  ├→ Passo 6: Define paleta visual
  │
  ├→ Passo 7: Gera cards (Leonardo AI)
  ├→ Passo 8: Revisao visual
  └→ Passo 9: Entrega organizada
```

**Pontos de validacao (2 paradas):**
1. Apos perfil visual (Passo 3.4)
2. Apos textos dos cards (Passo 4)

---

## Checklist de Qualidade Final
- [ ] Nome do projeto correto
- [ ] Patrocinador correto
- [ ] Cidades corretas
- [ ] Numeros corretos (do release/TAP)
- [ ] Sem Ministerio da Cultura / Lei Rouanet / Lei de Incentivo
- [ ] Tom coerente com identidade da empresa
- [ ] Identidade visual do cliente reconhecivel nos cards
- [ ] Cartela CTA: patrocinador + NTICS Projetos
- [ ] Captions Instagram e LinkedIn geradas
- [ ] Ficha do projeto completa no descricao.txt
