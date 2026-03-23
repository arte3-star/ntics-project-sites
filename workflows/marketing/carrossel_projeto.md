# Carrossel de Projeto — NTICS Projetos

> Recebe um relatorio de projeto NTICS, extrai textos para 5 cards, usa fotos reais do usuario como referencia no Leonardo AI Nano Banana 2, gera os cards visuais, revisa, corrige erros e salva tudo organizado com descricao.txt.

---

## APIs Utilizadas

| API | Uso | Modelo/Config |
|-----|-----|---------------|
| Leonardo AI | Gerar cards visuais com foto de referencia + texto | model: nano-banana-2, 1856x2304 (4:5), guidances.image_reference |

### Chave
- `LEONARDO_API_KEY`

---

## Contexto da Marca

Antes de comecar, leia:

1. `brand-book/02-identidade-verbal/tom-de-voz.md` — secoes 3.1 (LinkedIn) e 3.4 (Instagram)
2. `brand-book/data/brand-data.yaml` — credenciais e metricas gerais
3. `brand-book/02-identidade-verbal/mensagens-chave.md` — taglines

### Personas-alvo

**Marina Costa** — Coordenadora/Diretora RSC que pesquisa projetos para patrocinar. Quer ver metodologia, dados e conexao ESG/ODS.

**Carlos Ferreira** — Diretor/CEO que aprova. Quer ver resultado claro e valor institucional.

---

## Inputs do Usuario

| Campo | Tipo | Obrigatorio | Descricao |
|-------|------|-------------|-----------|
| `relatorio` | PDF ou texto | Sim | Relatorio final do projeto NTICS |
| `fotos` | Arquivos na pasta | Sim | Fotos reais do projeto, nomeadas foto-01 a foto-05 |

---

## Execucao

### Fase 1: Extracao do Relatorio

Ler o documento completo e extrair:

1. **Nome do projeto** (titulo oficial)
2. **Descricao curta** — o que e, em uma frase
3. **Patrocinador** — empresa que patrocinou
4. **Lei de incentivo** — Rouanet, Esporte, FIA, etc.
5. **Valor para a empresa patrocinadora** — por que apoiar este projeto
6. **Alcance** — cidades, escolas, publico, formato
7. **Metodologia** — como foi executado
8. **Resultados de impacto** — numeros concretos
9. **ODS priorizados**

**IMPORTANTE:** Conferir TODOS os numeros extraidos contra o relatorio original. Listar cada numero com sua fonte no relatorio.

### Fase 2: Redacao dos 5 Cards

Estrutura fixa de 5 cards + 1 NTICS (que o usuario ja tem no Canva):

---

**Card 1 — Nome + Subtitulo**
- Badge: PROJETO DE IMPACTO (verde)
- Titulo: Nome do projeto com palavra-chave em amarelo #F5B800
- Subtitulo: Frase descritiva com 2-3 palavras em amarelo #F5B800
- Formato: "{Nome}" + "Um {tipo} que {transformacao} — com {elementos}."

**Card 2 — Valor para a Empresa**
- Badge: VALOR PARA A EMPRESA (verde)
- Degrade: verde #3DAA35
- Texto: por que patrocinar, conexao ESG, lei de incentivo
- Palavras destaque em amarelo: nome da lei, Agenda 2030

**Card 3 — Alcance**
- Badge: ALCANCE (teal)
- Degrade: roxo #6B2D7B
- Texto: numeros de escala em destaque (cidades, alunos, pessoas)
- Formato lista com bullets

**Card 4 — Metodologia**
- Badge: METODOLOGIA (amarelo)
- Degrade: teal #005F73
- Texto: como foi executado, atividades, abordagem
- Palavras destaque: nome das metodologias

**Card 5 — Impacto**
- Badge: IMPACTO (rosa)
- Degrade: rosa #D41A6A
- Texto: resultados concretos, numeros grandes
- Destaque em amarelo nos numeros principais

**Card 6 — NTICS (fixo, usuario ja tem no Canva)**

---

### Fase 3: Usuario Coloca Fotos

Pedir ao usuario para colocar 5 fotos na pasta:
```
carrosseis/projeto-{nome}/fotos/
```

Sugerir qual foto usar para cada card baseado no conteudo do relatorio.

### Fase 4: Upload e Geracao (Leonardo AI)

**Step 1 — Upload de cada foto:**
```python
# Para cada foto
r = requests.post('https://cloud.leonardo.ai/api/rest/v1/init-image',
    headers=headers, json={'extension': 'jpg'})
upload = r.json()['uploadInitImage']
fields = json.loads(upload['fields'])
init_id = upload['id']

with open(foto_path, 'rb') as f:
    r2 = requests.post(upload['url'], data=fields, files={'file': f})
# init_id sera usado como referencia
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

---

### Prompt Template para cada Card

```
Social media carousel card Instagram 4:5. Top 55 percent uses the uploaded reference image as the main photograph. Bottom 45 percent smooth gradient transition to solid {cor do degrade}. Small {cor do badge} badge {NOME DO BADGE}. Large bold white sans-serif headline with key words in yellow F5B800: {titulo com destaques}. Below medium white text: {corpo com palavras destaque em amarelo F5B800}. Bottom edge flush thick gradient bar green to teal to pink to orange. Clean editorial card.
```

**IMPORTANTE no prompt:**
- NAO descrever o conteudo da foto — dizer apenas "uses the uploaded reference image"
- Indicar palavras em amarelo F5B800 para quebrar o branco
- Variar a cor do degrade entre os cards
- Sempre incluir a barra gradiente no rodape

### Cores de Degrade por Card

| Card | Degrade | Hex |
|------|---------|-----|
| 01 - Nome | Teal | #005F73 |
| 02 - Valor | Verde | #3DAA35 |
| 03 - Alcance | Roxo | #6B2D7B |
| 04 - Metodologia | Teal | #005F73 |
| 05 - Impacto | Rosa | #D41A6A |

### Cores dos Badges

| Badge | Cor fundo | Cor texto |
|-------|-----------|-----------|
| PROJETO DE IMPACTO | Verde #3DAA35 | Branco |
| VALOR PARA A EMPRESA | Verde #3DAA35 | Branco |
| ALCANCE | Teal #00A5B8 | Branco |
| METODOLOGIA | Amarelo #F5B800 | Escuro |
| IMPACTO | Rosa #D41A6A | Branco |

---

### Fase 5: Revisao Visual

Apos gerar, verificar CADA card:

**Checklist:**
- [ ] Texto correto — sem erros de ortografia (especialmente acentos: caminhao vs caminhão)
- [ ] Numeros batem com o relatorio
- [ ] Foto de referencia foi usada (nao uma foto generica)
- [ ] Badge visivel com categoria correta
- [ ] Barra gradiente no rodape colada na borda inferior
- [ ] Degrade com cor correta para o card
- [ ] Palavras destaque em amarelo visiveis
- [ ] Sem hex codes ou codigos visiveis na imagem

**Se algum card falhar:** regenerar APENAS esse card. Fazer novo upload da foto e gerar novamente.

### Fase 6: Descricao e Organizacao

**Estrutura da pasta:**
```
carrosseis/
└── projeto-{nome}/
    ├── fotos/
    │   ├── (fotos originais do usuario)
    ├── 01-nome.jpg
    ├── 02-valor.jpg
    ├── 03-alcance.jpg
    ├── 04-metodologia.jpg
    ├── 05-impacto.jpg
    └── descricao.txt
```

**Conteudo do descricao.txt:**
```
========================================
CARROSSEL: {NOME DO PROJETO}
{Patrocinador} | NTICS Projetos
========================================

--- CAPTION INSTAGRAM ---
{caption — tom inspirador, numeros de destaque, hashtags}

--- CAPTION LINKEDIN ---
{caption — tom profissional, lista de resultados, CTA consultivo, hashtags}

--- ORDEM DOS CARDS ---
{lista dos arquivos com descricao e foto usada}

--- DADOS DO PROJETO (verificados) ---
{todos os numeros usados com fonte no relatorio}
```

---

## Especificacoes Tecnicas

| Elemento | Especificacao |
|----------|---------------|
| Proporcao | 4:5 (Instagram) |
| Dimensao | 1856 x 2304 px |
| Formato | JPG |
| Modelo IA | Nano Banana 2 (Leonardo AI v2 API) |
| Referencia foto | guidances.image_reference, type: UPLOADED, strength: HIGH |
| Foto | Topo 55%, foto real do usuario via referencia |
| Degrade | 45% inferior, cor variada por card |
| Texto | Branco + destaque amarelo #F5B800 em palavras-chave |
| Barra gradiente | 2% da altura, colada no rodape, sem espaco |
| Cores da barra | #3DAA35 → #00A5B8 → #D41A6A → #E86428 |
| Sem logo | Usuario adiciona depois |

---

## Identidade Visual NTICS

| Cor | Hex | Uso nos cards |
|-----|-----|---------------|
| Verde Regeneracao | #3DAA35 | Badge, degrade, barra |
| Azul Petroleo | #005F73 | Degrade principal |
| Rosa Transformacao | #D41A6A | Badge impacto, degrade, barra |
| Laranja Acao | #E86428 | Barra |
| Teal Futuro | #00A5B8 | Badge alcance, barra |
| Amarelo Consciencia | #F5B800 | Destaque de palavras-chave |
| Roxo Inovacao | #6B2D7B | Degrade alcance |
| Branco | #FFFFFF | Texto principal |
