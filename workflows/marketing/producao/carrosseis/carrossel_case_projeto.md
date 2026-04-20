# Carrossel de Case — NTICS Projetos

> Carrossel pos-projeto (case) com identidade NTICS. **9 cards** (7 de conteúdo + 1 trilha NTICS + 1 CTA). Usa SecondBrain como fonte de texto e `assets/projetos/` como primeira fonte de fotos. Gera cards via Leonardo AI Nano Banana 2, revisa, corrige e exporta textos + PDF LinkedIn.

> 📚 **Referência Leonardo AI:** Este workflow tem estrutura validada — siga-o como fonte primária. Se surgir erro de API, dúvida sobre payload ou resultado visual inesperado, consulte `workflows/marketing/referencia/leonardo_ai_core.md` como base de conhecimento complementar.

---

## APIs Utilizadas

| API | Uso | Modelo/Config |
|-----|-----|---------------|
| Leonardo AI | Gerar cards visuais com foto de referencia + texto | model: nano-banana-2, 1856x2304 (4:5), guidances.image_reference strength HIGH |

**Chave:** `LEONARDO_API_KEY`

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

## Inputs

| Campo | Tipo | Obrigatorio | Descricao |
|-------|------|-------------|-----------|
| `nome_projeto` | string | Sim | Nome ou parte do nome do projeto (ex: "cinegastroarte", "statkraft pec") |

---

## Fluxo de dados (nova ordem)

**1ª fonte:** `SecondBrain/` (texto) + `assets/projetos/` (fotos).
**Fallback de fotos:** baixar PDF pelo link público do Drive (sem API) e extrair.
**Nunca:** Drive API, ClickUp pra foto/texto — só usar se SB e assets não tiverem o necessário.

---

## Execucao

### Fase 1: Localizar na base de conhecimento

Ler `brand-book/data/projetos-carrossel.yaml` e localizar pelo `nome_projeto`:

1. Encontrar a entrada (busca parcial no `nome`, `slug`, `patrocinador`)
2. Confirmar com o usuario: "Encontrei **{nome}** ({ano}, {patrocinador}). Posso prosseguir?"
3. Salvar: `slug`, `relatorio_pdf`, `fotos_drive`, `numeros`, `patrocinador`, `ano`, `lei`

**Se não encontrar:** Perguntar. Adicionar entrada no YAML antes de continuar.

---

### Fase 2: Ler texto do relatorio do SecondBrain

```
Arquivo: SecondBrain/projetos-anteriores/{num}-{slug}.md
```

O perfil já tem:
- Nome, patrocinador, ano, lei, categoria
- Tabela de indicadores (pessoas diretas/indiretas, alunos, professores, cidades, nota, empregos)
- Metodologia, resultados, aprendizados
- Linha do tempo de execução (kick-off → pré-produção → execução → pós-produção)
- Texto integral do relatório extraído via PDF

**Extrair e confirmar:**
1. Nome oficial do projeto
2. Descrição curta (1 frase)
3. Patrocinador + lei de incentivo
4. Alcance (cidades, público, formato)
5. Metodologia (etapas)
6. **Pessoas impactadas DIRETAMENTE** (nunca usar indiretos)
7. ODS priorizados
8. Período de execução (mês/ano início → mês/ano fim, ou só o ano)
9. Nota média + indicadores qualitativos (ex: "98% querem participar de novo")

**IMPORTANTE:** Conferir TODOS os números contra o perfil do SB. Se o SB não tem o dado, ler o PDF original em `.tmp/` (próxima fase).

---

### Fase 3: Checar fotos em assets/projetos

**Pasta local:** `assets/projetos/{num}. {NOME} ({SPONSOR})/FOTOS/`

Listar arquivos e contar fotos úteis (exceto `desktop.ini` e thumbs). Se houver **≥7 fotos curadas reais**, seguir direto para Fase 5 (selecao).

Se houver **<7 fotos reais** (frequente em projetos que só têm `site.html` scrapado ou oficina isolada), ir para Fase 4.

---

### Fase 4 (fallback): Baixar PDF + extrair fotos

```
Destino: .tmp/marketing/carrosseis/{slug}/
├── relatorio.pdf
├── paginas-revisao/
├── fotos-hires/
└── fotos-selecionadas/
```

**3.1 — Download via link público (sem API):**

Se `relatorio_pdf` no YAML for `/file/d/ID/view`, extrair ID e baixar:
```python
import urllib.request
url = f'https://drive.google.com/uc?export=download&id={FILE_ID}'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req, timeout=60) as r:
    data = r.read()
with open('relatorio.pdf','wb') as f:
    f.write(data)
```

Se for pasta Drive, pedir o PDF principal ao usuário.

**3.2 — Renderizar páginas do PDF:**
```python
import fitz
doc = fitz.open('relatorio.pdf')
for i in range(len(doc)):
    pix = doc[i].get_pixmap(matrix=fitz.Matrix(1.5,1.5), alpha=False)
    pix.save(f'paginas-revisao/pagina_{i+1:02d}.jpg', output='jpeg', jpg_quality=80)
```

**3.3 — Inventário visual obrigatório:**

Abrir cada `pagina_XX.jpg` e classificar:

| Pagina | Classificacao |
|--------|--------------|
| XX | ✓ foto-real (pessoas/atividades do projeto) |
| XX | ✗ slide-texto (capa, infográfico, sumário) |
| XX | ✗ mockup (tela de celular, arte gráfica) |
| XX | ✗ inutilizável (tremida, escura, só logo) |

Criteérios de foto aprovada:
- Pessoas reais em atividade do projeto
- Não é mockup nem arte gráfica
- Não está tremida/escura/cortada

**3.4 — Extrair imagens hires das páginas aprovadas:**
```python
import fitz
doc = fitz.open('relatorio.pdf')
paginas_aprovadas = [0, 2, 4, ...]  # 0-indexed
seen = set()
for pi in paginas_aprovadas:
    for img in doc[pi].get_images(full=True):
        xref, w, h = img[0], img[2], img[3]
        if xref in seen or min(w,h) < 600:
            continue
        aspect = max(w,h)/max(min(w,h),1)
        if aspect > 3.5:  # descartar banners horizontais
            continue
        pix = fitz.Pixmap(doc, xref)
        if pix.n > 4:
            pix = fitz.Pixmap(fitz.csRGB, pix)
        pix.save(f'fotos-hires/p{pi+1:02d}_xref{xref}_{w}x{h}.jpeg')
        seen.add(xref)
```

**ATENÇÃO:** Fotos <100KB são miniaturas — descartar. Fotos reais hires têm tipicamente >400KB e >1600px no lado maior.

---

### Fase 5: Selecao das fotos

Abrir cada candidata em `fotos-hires/` (ou direto em `assets/projetos/{num}/FOTOS/`) e mapear:

| Card | O que procurar |
|------|----------------|
| 01 Capa | Grupo de pessoas, evento principal, fotografia icônica do projeto |
| 02 O Projeto | Abertura, banner do projeto visível, plateia |
| 03 Metodologia | Oficina em ação, atividade pedagógica em andamento |
| 04 Alcance | Panorâmica, espaço do evento com escala visível |
| 05 A Empresa | Representante do patrocinador, equipe, momento institucional |
| 06 Resultados | Feira de Ideias, alunos mostrando protótipo, apresentação |
| 07 Impacto | Foto emotiva de aluno/jovem em destaque |

Copiar com nomes padronizados:
```bash
cp fotos-hires/p{XX}_*.jpeg fotos-selecionadas/card01-capa.jpeg
# ... card02, card03, card04, card05, card06, card07
```

A pasta `fotos-selecionadas/` deve conter **7 arquivos** antes de gerar.

---

### Fase 6: Redacao dos 9 cards

**Estrutura fixa de 7 cards de conteúdo + 1 trilha NTICS + 1 CTA:**

---

#### Card 01 — Capa
- Badge: **PROJETO DE IMPACTO** (verde #3DAA35)
- Degradê: **teal #005F73** (CONSTANTE em todos os cards, não alternar!)
- Linha pequena acima do título: **"PROGRAMA DE EMPREENDEDORISMO E CULTURA"** (sigla expandida — ex: CODS → "Conhecendo os ODS", MHS → "Meus Hábitos Saudáveis", PEC → "Empreendedorismo e Cultura")
- Título grande: "PEC **[YELLOW]EU FAÇO PARTE[/YELLOW]**" (sigla + nome oficial)
- Linha abaixo: "EDIÇÃO [YELLOW]2025[/YELLOW]" (ano em destaque)
- Corpo: "Realizado pela NTICS em **{cidade1}, {cidade2} e {cidade3}** com patrocínio **[YELLOW]{Patrocinador}[/YELLOW]** via Lei {lei}"

**Regras ortográficas obrigatórias na capa:**
- Cidades separadas por vírgula + "e" antes da última
- Usar sigla expandida ANTES do nome com sigla

#### Card 02 — O Projeto
- Badge: **O PROJETO** (teal #00A5B8)
- Degradê: teal
- Corpo: o que é + público + formato. Destaque em amarelo: tipo de atividade principal

#### Card 03 — Metodologia
- Badge: **METODOLOGIA** (amarelo #F5B800, texto escuro)
- Degradê: teal
- Corpo: etapas + diferenciais. Número de etapas em amarelo

#### Card 04 — Alcance
- Badge: **ALCANCE** (teal)
- Degradê: teal
- Lista em bullets, números em amarelo:
  - [YELLOW]N CIDADES[/YELLOW]
  - **CIDADE1, CIDADE2 E CIDADE3** (linha própria, vírgulas obrigatórias)
  - [YELLOW]N.NNN[/YELLOW] ALUNOS
  - [YELLOW]NNN[/YELLOW] PROFESSORES
  - [YELLOW]N[/YELLOW] EMPREGOS LOCAIS

#### Card 05 — A Empresa
- Badge: **A EMPRESA** (verde #3DAA35)
- Degradê: teal (não verde! manter teal)
- Título: "[YELLOW]{PATROCINADOR}[/YELLOW] APOIA {tema da empresa}"
- Corpo: "Patrocínio via [YELLOW]Lei {lei}[/YELLOW] reafirma compromisso com os [YELLOW]ODS N, N, N e N[/YELLOW]" (ODS separados por vírgula + "e")
- **Regra:** Mencionar o patrocinador apenas no card 01 (capa) e aqui (05). Nos demais cards usar "empresa patrocinadora"

#### Card 06 — Resultados
- Badge: **RESULTADOS** (laranja #E86428)
- Degradê: teal
- Título: "NOTA [YELLOW]N,N[/YELLOW] NA AVALIAÇÃO FINAL" ou similar com indicador principal
- Corpo: indicadores de satisfação/aprovação. Números como dígitos, sem spell out.
- **ATENÇÃO Leonardo:** reforçar no prompt "render digits as digits, NOT as words" para evitar "NOVE VÍRGULA QUATRO"

#### Card 07 — Impacto
- Badge: **IMPACTO** (rosa #D41A6A)
- Degradê: teal
- Título: "[YELLOW]N.NNN PESSOAS[/YELLOW] IMPACTADAS DIRETAMENTE"
- Corpo: narrativa de transformação — protagonismo, premiação, mudança de olhar
- **REGRA OBRIGATÓRIA:** usar apenas pessoas impactadas DIRETAMENTE. Nunca citar indiretos aqui.

#### Card 08 — Trilha NTICS do programa (novo!)
- Badge: **METODOLOGIA NTICS** (amarelo, texto escuro)
- Degradê: teal
- Título: "[YELLOW]+{N} MIL PESSOAS[/YELLOW] IMPACTADAS DIRETAMENTE"
- Corpo: "Desde {ano primeiro} o {SIGLA} já teve [YELLOW]{N} edições[/YELLOW] com [YELLOW]{N} patrocinadores[/YELLOW]: {Lista de patrocinadores separados por vírgula + 'e' antes do último}"
- **Fonte dos números:** consolidar os perfis em `SecondBrain/projetos-anteriores/` que pertencem à mesma família (`SecondBrain/conhecimento/programa-{slug}.md` lista as edições). Somar apenas pessoas diretas.
- **Função:** mostrar maturidade do programa (PEC/CODS/MHS/etc) como prova social

#### Card 09 — CTA
- Fundo sólido teal #005F73
- Logo NTICS branca (42% largura, topo 6%)
- Texto: "Siga para mais projetos de impacto" + @nticsprojetos + "Inovação, Impacto e Regeneração"
- Barra gradiente no rodapé
- **NÃO gerar via Leonardo** — reutilizar CTA de carrossel anterior (ex: `output/marketing/carrosseis/cases/cinegastroarte/08-cta.jpg`), ou gerar uma vez via Pillow e reusar

---

### REGRA DE POSICIONAMENTO DO DEGRADE

```
0-55%   → Foto (referência real do projeto)
55-75%  → Zona de degradê (transparente → teal sólido)
75-78%  → Badge
78-92%  → Título
92-98%  → Corpo
98-100% → Barra gradiente (verde → teal → rosa → laranja)
```

Nenhum texto pode ficar sobre a zona de transição (55-75%).

---

### Fase 7: Geracao via Leonardo AI

**Template base de prompt** (cada card substitui variáveis):

```
Social media carousel card, Instagram portrait format, no white borders, fills entire frame edge to edge.
IMPORTANT: Do NOT render percentage signs, numbers as words, rulers or layout markers. Keep all commas and spaces between words exactly as shown.
UPPER HALF of the card: full-bleed photograph, uses the uploaded reference image as the main visual. Edge to edge, no text, no watermarks.
SMOOTH GRADIENT TRANSITION between upper and lower halves, blending the photo into the solid dark teal background below.
LOWER HALF of the card: solid dark teal background.
POSITIONED near the top of the lower half: small rounded pill badge with {cor texto} bold uppercase text '{NOME DO BADGE}' on {cor badge} background.
LARGE BOLD HEADLINE below the badge: white uppercase sans-serif, words marked [YELLOW]...[/YELLOW] render in bright yellow color: {título com marcações}.
BODY TEXT below headline: smaller regular white sans-serif: '{corpo}'.
BOTTOM EDGE flush: thick horizontal gradient stripe spanning full width, colors flow smoothly from bright green to teal to magenta pink to orange.
Professional editorial design, clean, no borders, no padding.
```

**Regras críticas do prompt:**
- **NUNCA usar percentuais** ("top 55%") — usar `UPPER HALF / LOWER HALF / SMOOTH GRADIENT TRANSITION`
- **NUNCA incluir hex codes** — usar nomes de cor ("dark teal", "bright green")
- **NÃO descrever o conteúdo da foto** — "uses the uploaded reference image"
- **Highlight words:** envolver em `[YELLOW]palavra[/YELLOW]`
- **Acentos:** manter no prompt (Leonardo renderiza UTF-8 corretamente)
- **Headlines:** máximo 8-10 palavras
- **Números:** sempre pedir "render as digits, NOT as words" — Leonardo tende a soletrar decimais ("nove vírgula quatro")
- **Vírgulas:** reforçar "Keep all commas and spaces between words exactly as shown" em listas
- **Decimais:** pedir explicitamente "render decimal number with comma and no space" (evita "9, 4")
- **CTA:** NÃO gerar via Leonardo — reutilizar CTA existente

**Código Leonardo (referência):**
Ver `.tmp/marketing/carrosseis/{slug-anterior}/gerar_cards.py` para padrão validado. Sempre usa:
- `model: nano-banana-2`
- `width: 1856, height: 2304` (4:5)
- `prompt_enhance: OFF`
- `guidances.image_reference: [{image: {id, type: UPLOADED}, strength: HIGH}]`
- Polling a cada 10s, timeout 420s

---

### Fase 8: Revisao Visual (auto, bloqueante)

Nenhum card pode ser apresentado ao usuário sem passar por esta revisão.

**Checklist por card:**
- [ ] Sem palavras duplicadas ("COM COM", "NO NO MATO GROSSO")
- [ ] Sem trechos duplicados
- [ ] Acentos corretos (Educação, Inovação, Osório — não EDUCACAO)
- [ ] **Vírgulas presentes em listas** (cidades, ODS, patrocinadores)
- [ ] Números idênticos ao relatório, como dígitos (9,4 não "NOVE VÍRGULA QUATRO")
- [ ] Decimais sem espaço ("9,4" não "9, 4")
- [ ] Siglas expandidas na capa (PEC → Programa de Empreendedorismo e Cultura)
- [ ] Ano/período visível na capa
- [ ] Badge com categoria correta
- [ ] Foto de referência usada (não genérica)
- [ ] **Degradê teal #005F73 em TODOS os cards** (não alternar com roxo/verde/rosa)
- [ ] Barra gradiente colada na borda inferior
- [ ] Apenas pessoas impactadas DIRETAMENTE nos cards 07 e 08
- [ ] Card 08 tem lista completa de patrocinadores do programa com vírgulas

**Erros frequentes do Leonardo AI:**

| Tipo | Exemplo | Solução |
|------|---------|---------|
| Palavra duplicada | "NO NO MATO GROSSO" | Encurtar headline |
| Acento faltando | "EDUCACAO" | Manter acento no prompt |
| Percentual visível | "55%" na imagem | Nunca usar % no prompt |
| Hex code visível | "#005F73" | Nunca usar hex — usar nomes |
| Decimais por extenso | "NOVE VÍRGULA QUATRO" | Pedir "render as digits, NOT as words" |
| Decimais com espaço | "9, 4" | Pedir "decimal number with comma and no space" |
| Vírgulas faltando | "OSÓRIO UIBAÍ IBIPEBA" | Pedir "Keep all commas exactly as shown" |
| Siglas coladas | "PECEU FAÇO PARTE" | Separar em linhas ou pedir espaçamento visível |
| Degradê errado | roxo em card 04 | Forçar "solid dark teal background" em TODOS |

**Ação para cada card com erro:** ajustar prompt → upload foto + nova geração → repetir revisão → loop até passar.

---

### Fase 9: Textos e PDF LinkedIn

Editar `tools/content-gen/gerar_textos_pdf_carrossel.py`:

1. Adicionar entrada em `TEXTOS` com slug do projeto (instagram + linkedin)
2. Adicionar entrada em `PROJETOS_PDF` com lista de 9 cards:
   ```python
   "01-capa.jpg", "02-o-projeto.jpg", "03-metodologia.jpg", "04-alcance.jpg",
   "05-a-empresa.jpg", "06-resultados.jpg", "07-impacto.jpg",
   "08-trilha-pec.jpg", "09-cta.jpg",
   ```
3. Executar:
   ```bash
   python tools/content-gen/gerar_textos_pdf_carrossel.py
   ```

**Saídas em `output/marketing/carrosseis/cases/{slug}/`:**
- `texto_instagram.txt` — legenda casual com emojis e hashtags
- `texto_linkedin.txt` — post formal com bullets de métricas ESG
- `linkedin-carrossel.pdf` — 9 páginas 4:5 completo (210x262.5mm)

**Tom Instagram:** casual, inspiracional, 2-3 emojis, gancho emocional, hashtags no final.
**Tom LinkedIn:** formal, dado de impacto no gancho, bullets com métricas ESG, CTA consultivo, max 5 hashtags.
**Ambos:** usar apenas pessoas diretas (não citar indiretos).

---

### Fase 10: Organizacao final e atualizacao de status (gate humano)

**Estrutura da pasta de output:**
```
output/marketing/carrosseis/cases/{slug}/
├── 01-capa.jpg
├── 02-o-projeto.jpg
├── 03-metodologia.jpg
├── 04-alcance.jpg
├── 05-a-empresa.jpg
├── 06-resultados.jpg
├── 07-impacto.jpg
├── 08-trilha-{programa}.jpg
├── 09-cta.jpg
├── texto_instagram.txt
├── texto_linkedin.txt
└── linkedin-carrossel.pdf
```

**Após concluir:**
1. Atualizar `brand-book/data/projetos-carrossel.yaml` — mudar `status_carrossel` do projeto de `pendente` para `feito`
2. Apresentar os 9 cards ao usuário para validação final

---

## Especificações Técnicas

| Elemento | Especificação |
|----------|---------------|
| Proporção | 4:5 (Instagram) |
| Dimensão | 1856 x 2304 px |
| Formato cards | JPG |
| Formato PDF | 210 x 262.5mm (4:5, sem crop) |
| Modelo IA | Nano Banana 2 (Leonardo AI v2 API) |
| Referência foto | guidances.image_reference, type: UPLOADED, strength: HIGH |
| Foto | Topo 55%, foto real via referência |
| Degradê | 55-75%, **teal #005F73 em TODOS os cards** |
| Texto | Branco + destaque amarelo #F5B800 |
| Barra gradiente | 98-100%, colada no rodapé |
| Logo CTA | brand-book/site/assets/LOGO NTICS - BRANCA.png, 42% largura, Pillow pós-processamento |
| Total de cards | 9 (7 conteúdo + trilha NTICS + CTA) |

## Identidade Visual NTICS

| Cor | Hex | Uso nos cards |
|-----|-----|---------------|
| Azul Petróleo | #005F73 | **Degradê principal em TODOS os cards** (constante) |
| Verde Regeneração | #3DAA35 | Badge capa/empresa |
| Rosa Transformação | #D41A6A | Badge impacto |
| Laranja Ação | #E86428 | Badge resultados, barra gradiente |
| Teal Futuro | #00A5B8 | Badge alcance/projeto, barra gradiente |
| Amarelo Consciência | #F5B800 | Destaque palavras-chave, badge metodologia |
| Branco | #FFFFFF | Texto principal |

**IMPORTANTE:** Cores roxo e verde não entram mais como degradê principal (regra antiga). Só aparecem como cor de badge ou como parte da barra gradiente do rodapé.

---

## Aprendizados da sessão PEC/Statkraft (2026-04-14 a 2026-04-16)

1. **Leonardo apaga vírgulas** em listas — sempre reforçar no prompt "Keep all commas exactly as shown"
2. **Leonardo soletra decimais** — pedir "digits as digits, NOT as words"
3. **Leonardo gruda palavras** quando termina uma linha com sigla curta — separar em linhas distintas ou "line1 = ... line2 = ..." no prompt
4. **Degradê teal único** é o padrão NTICS — não alternar por categoria
5. **Siglas sempre expandidas** na primeira menção (capa) — leitor novo não sabe o que é PEC/CODS/MHS
6. **Ano/período obrigatório** na capa
7. **Só impacto direto** em comunicação pública — indiretos são estimativas
8. **Card de trilha do programa** antes do CTA posiciona NTICS como dona de metodologia madura (prova social)
9. **SecondBrain > PDF > Drive API** — texto já está extraído; fotos estão em `assets/projetos/` ou extraíveis do PDF via link público
