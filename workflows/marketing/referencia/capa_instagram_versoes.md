# Capa Instagram NTICS — Diretriz das Versões (v1, v2, v3, v5, v6, v16, v21)

Documento de **gramática visual** das capas Instagram NTICS testadas em [output/marketing/posts-avulsos/instagram-redesign-experimentos/](../../../output/marketing/posts-avulsos/instagram-redesign-experimentos/). Permite regenerar qualquer estilo (ou criar derivados) trocando só o **bloco variável** dentro de um prompt-template comum.

## 1. Receita técnica fixa (sempre igual)

| Parâmetro | Valor |
|---|---|
| API | Leonardo AI · `nano-banana-2` (endpoint v2/generations) |
| Formato | Instagram 4:5 — `1856 × 2304 px` |
| Foto | upload via `/init-image`, usado como `image_reference` com `strength: HIGH` |
| `prompt_enhance` | `OFF` (para não distorcer paleta nem layout) |
| Quantity | `1` por variação, paralelizadas com `ThreadPoolExecutor` |
| Limite prompt | < 1500 chars (cap nano-banana-2); ideal < 1000 |

Scripts de referência: [gerar.py](../../../output/marketing/posts-avulsos/instagram-redesign-experimentos/gerar.py) (v1–v5), [gerar-v2.py](../../../output/marketing/posts-avulsos/instagram-redesign-experimentos/gerar-v2.py) (v6–v15), [gerar-v3.py](../../../output/marketing/posts-avulsos/instagram-redesign-experimentos/gerar-v3.py) (v16–v25).

## 2. Identidade visual (sempre presente, não muda)

- **Paleta NTICS 2.0**: teal `005F73`, verde `3DAA35`, pink `D41A6A`, laranja `E86428`, amarelo `F5B800`
- **Régua gradiente** colada na borda inferior, LEFT→RIGHT: verde → teal `00A5B8` → pink → laranja
- **Badge pill** verde `3DAA35` com label categoria em UPPERCASE branca (`EDUCACAO`, `CULTURA`, etc.)
- **Headline**: bold UPPERCASE sans-serif branca, 2–3 linhas
- **Body**: `[YELLOW]números[/YELLOW]` para destacar estatísticas
- **Acentos PT-BR preservados**, edge-to-edge sem bordas brancas
- **Foto**: `preserving exact face composition natural vibrant colors` (frase obrigatória contra deformação)

## 3. Bloco variável — a "alma" de cada versão

| Versão | Esqueleto | Quando usar |
|---|---|---|
| **v1-diagonal** | Split diagonal 30°: foto canto sup-direito, bloco teal sólido inf-esquerdo, engrenagem 12% atrás do texto | Postagem padrão com foto forte; permite copy longo no teal |
| **v2-blocos** | Foto à esquerda 60% com cantos arredondados; coluna direita = 3 blocos sólidos empilhados (verde / teal / pink) | Quando há 3 unidades de info (categoria + headline + stat) bem separáveis |
| **v3-editorial** | Foto fullbleed 100%; overlay teal só nos 40% inferiores; headline monumental 3 linhas em cima do overlay | Foto cinematográfica, conceito vende sozinho — máximo impacto |
| **v5-grid** | 3 colunas verticais 33% cada: foto / bloco verde com número gigante / bloco teal com texto | Quando o **número** é a estrela (ex.: "5.000 alunos") |
| **v6-orbital** | Fundo teal sólido; foto em moldura circular ao centro; engrenagens brancas orbitando em opacidades 10–25% | Tema tecnológico/educacional, identidade NTICS antiga (engrenagens) |
| **v16-diagonal-inverso** | v1 espelhado: teal sup-esquerdo, foto inf-direita | Variação rítmica do v1 dentro de uma série; quebra repetição |
| **v21-fullbleed-headline-topo** | **Invertido**: top 45% teal sólido com headline monumental 3 linhas; bottom 55% foto fullbleed; transição suave | **Capa de abertura de série** (formato vencedor — Global Goals); título lê antes da foto |

## 4. Prompt-template universal

Estrutura de **8 linhas fixas + 1 linha variável** que gera qualquer versão acima ou novos derivados:

```
Social media card, Instagram 4:5, edge to edge, no white borders. Uses uploaded reference image.
{ESQUELETO}                                                    ← linha variável (ver tabela §3)
Top: rounded pill badge bright green 3DAA35 white bold uppercase {CATEGORIA}.
Headline: large bold white uppercase sans-serif, two lines {HEADLINE_LINHA1} / {HEADLINE_LINHA2}.
Body: smaller white sans-serif, [YELLOW]{STAT_1}[/YELLOW] em [YELLOW]{STAT_2}[/YELLOW] {COMPLEMENTO}.
Photo: preserving exact face composition with natural vibrant colors.
Bottom edge flush: thin horizontal gradient stripe LEFT to RIGHT green 3DAA35 teal 00A5B8 pink D41A6A orange E86428.
{ESTILO_FINAL}, Portuguese accents preserved.
```

**Variáveis a preencher por peça:**
- `{ESQUELETO}` — copiar a 1 linha-âncora da versão escolhida na tabela §3
- `{CATEGORIA}` — `EDUCACAO`, `CULTURA`, `SUSTENTABILIDADE`, `ESPORTE`...
- `{HEADLINE_LINHA1}` / `{HEADLINE_LINHA2}` — gancho em 2–3 palavras por linha
- `{STAT_1}` / `{STAT_2}` — números com destaque amarelo
- `{COMPLEMENTO}` — texto que une os stats (`publicas`, `em 12 cidades`, etc.)
- `{ESTILO_FINAL}` — adjetivo de fechamento (`clean editorial design`, `bold geometric`, `magazine impact`)

## 5. Regras quando criar nova versão (vN)

1. **Manter** identidade fixa do §2 — nunca reinventar paleta, régua, badge ou headline style
2. **Variar só** o ESQUELETO (composição) e o `{ESTILO_FINAL}`
3. **Frase obrigatória** contra deformação de rosto: `preserving exact face composition natural vibrant colors`
4. **Régua gradiente sempre LEFT→RIGHT** na ordem `verde → teal → pink → laranja` (regra global NTICS — ver [feedback_leonardo_prompts.md](../../../../.claude/projects/g--O-meu-disco-AUTOMA--ES/memory/feedback_leonardo_prompts.md))
5. **Headline em painel/área sólida**, nunca solto sobre foto sem overlay (ver [feedback_leonardo_layout_carrossel.md](../../../../.claude/projects/g--O-meu-disco-AUTOMA--ES/memory/feedback_leonardo_layout_carrossel.md))
6. **Cap de prompt**: ≤ 1500 chars, ≤ 3 image_references (ver [feedback_leonardo_limites_payload.md](../../../../.claude/projects/g--O-meu-disco-AUTOMA--ES/memory/feedback_leonardo_limites_payload.md))
7. **Salvar `gen_id`** antes de qualquer rm — CDN Leonardo permite recuperar
8. **Testar 3–5 layouts em paralelo** no mesmo run; comparar visual e congelar o vencedor (foi assim que v21 nasceu)

## 6. Versões já validadas como padrão

- **v21-fullbleed-headline-topo** → padrão de **capa de abertura de série** (Global Goals Educa)
- **v21-invertida** → variação para itens internos de série
- **v3-editorial** → padrão para fotos com forte presença emocional
- **v5-grid** → padrão para posts orientados a número/dado

Nenhuma das outras (v1, v2, v6, v16) virou padrão — ficaram como **vocabulário disponível** para variação rítmica dentro de uma sequência editorial.
