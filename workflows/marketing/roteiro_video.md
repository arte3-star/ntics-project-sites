# Roteiro de Video — NTICS Projetos

> Gera roteiro completo de video (1 minuto) para producao via NotebookLM + Opus Clip/Agent. Suporta 2 estilos: animacao e b-roll.

---

## Contexto da Marca

Antes de comecar, leia:

1. `brand-book/02-identidade-verbal/tom-de-voz.md` — secao 3.3 (Blog/Conteudo Educativo: 55% formal, 60% tecnico, 70% inspiracao)
2. `brand-book/data/brand-data.yaml` — metricas e projetos para citar
3. `brand-book/02-identidade-verbal/mensagens-chave.md` — taglines e proof points

---

## Inputs do Usuario

| Campo | Tipo | Obrigatorio | Descricao |
|-------|------|-------------|-----------|
| `subtopico` | string | Sim | Sub-tema semanal (vem do /plano-mensal) |
| `estilo` | enum | Sim | `animacao` ou `broll` |
| `brolls_disponiveis` | string | Se estilo=broll | Descricao dos b-rolls que o usuario tem |
| `tema_mensal` | string | Nao | Tema geral do mes para contexto |
| `dados_relevantes` | string | Nao | Metricas ou projetos NTICS especificos para usar |

---

## Pipeline do Usuario (para referencia)

1. **Texto gerado aqui** → usuario cola no NotebookLM → gera audio
2. Audio → **Opus Clip** → gera video com frames
3. Se estilo `broll`: usuario substitui frames por seus b-rolls reais no **Opus Agent**
4. Opus Agent adiciona motions/transicoes entre b-rolls

---

## Execucao

### Fase 1: Hook (primeiros 3 segundos)

Use a metodologia do hormozi squad (`hormozi-squad/tasks/create-hooks.md`):

- Em 1 min de video, o hook e TUDO. Se nao prende em 3 segundos, perdeu.
- Categorias que funcionam para video curto:
  - **Curiosity Gap:** "Voce sabia que [dado surpreendente]?"
  - **Bold Claim:** "[Numero impactante] em [periodo curto]"
  - **Contrarian:** "Tudo que voce ouviu sobre [tema] esta errado"
  - **Result/Proof:** "Com [abordagem X], conseguimos [resultado Y]"
- Aplique a regra da especificidade: trocar palavras vagas por numeros e detalhes
- Maximo 12 palavras no hook

### Fase 2: Estrutura Compacta (1 minuto total)

Estrutura fixa para video de 1 min (~150 palavras):

| Secao | Tempo | Palavras | O que acontece |
|-------|-------|----------|----------------|
| **HOOK** | 0:00-0:03 | ~12 | Frase que para o scroll |
| **CONTEXTO** | 0:03-0:18 | ~35 | Situar o tema, por que importa |
| **INSIGHT** | 0:18-0:43 | ~60 | O ponto central, a revelacao, o ensinamento |
| **PROVA** | 0:43-0:55 | ~30 | Dado NTICS, resultado, case real |
| **CTA** | 0:55-1:00 | ~13 | Chamada para acao |

### Fase 3: Escrita por Estilo

**Se estilo = `animacao`:**
- Inserir marcacoes `[ANIMACAO: descricao da cena]` em cada transicao
- Sugerir motion graphics, icones animados, textos cinematicos
- Sugerir paleta de cores NTICS (consultar `brand-book/03-identidade-visual/cores.md`)

**Se estilo = `broll`:**
- Inserir marcacoes `[B-ROLL: descricao]` mapeadas ao footage real do usuario
- Cada b-roll deve ter 3-5 segundos
- Indicar momentos de transicao onde Opus Agent adicionara motions

**Para ambos os estilos:**
- Inserir `[TEXTO NA TELA: texto]` nos momentos-chave (hook, dado principal, CTA)
- Maximo 3 textos na tela por video de 1 min

### Fase 4: Texto Limpo para NotebookLM

Gerar uma secao separada com APENAS o texto falado:
- Sem marcacoes de b-roll, animacao ou texto na tela
- Texto corrido em paragrafos naturais
- Pronto para copiar e colar no NotebookLM
- Tom conversacional mas informado (Blog/Conteudo Educativo)

---

## Formato de Saida

```markdown
# Roteiro de Video: {Titulo}

**Tema Mensal:** {tema}
**Sub-topico:** {subtopico}
**Estilo:** {animacao / broll}
**Duracao:** ~1 min (~150 palavras)
**Tom:** Informativo + Inspirador (Blog scale)

---

## Roteiro Completo

### HOOK (0:00 - 0:03)
{texto do hook}
[TEXTO NA TELA: {frase-chave}]
[ANIMACAO: {cena}] ou [B-ROLL: {descricao do footage}]

### CONTEXTO (0:03 - 0:18)
{texto falado}
[ANIMACAO: {cena}] ou [B-ROLL: {descricao}]

### INSIGHT (0:18 - 0:43)
{texto falado — ponto central}
[TEXTO NA TELA: {dado ou frase-chave}]
[ANIMACAO: {cena}] ou [B-ROLL: {descricao}]

### PROVA (0:43 - 0:55)
{texto com dado NTICS}
[ANIMACAO: {cena}] ou [B-ROLL: {descricao}]

### CTA (0:55 - 1:00)
{chamada para acao}
[TEXTO NA TELA: {CTA visual}]

---

## Texto para NotebookLM

{Texto completo sem nenhuma marcacao. Apenas o que sera falado. Paragrafos naturais, tom conversacional. Pronto para copiar e colar.}

---

## Mapa Visual

| Timestamp | Visual | Duracao |
|-----------|--------|---------|
| 0:00-0:03 | {animacao/broll} | 3s |
| 0:03-0:18 | {animacao/broll} | 15s |
| 0:18-0:43 | {animacao/broll} | 25s |
| 0:43-0:55 | {animacao/broll} | 12s |
| 0:55-1:00 | {animacao/broll} | 5s |

## Textos para Tela
| Timestamp | Texto | Posicao Sugerida |
|-----------|-------|-----------------|
| 0:00 | {hook} | Centro |
| 0:25 | {dado principal} | Inferior |
| 0:55 | {CTA} | Centro |
```

---

## Checklist de Qualidade

- [ ] Hook prende atencao em 3 segundos (maximo 12 palavras)
- [ ] Texto total tem ~150 palavras (±20)
- [ ] Voz alinhada: Informativa, Confiante, Inspiradora, Acessivel
- [ ] Pelo menos 1 dado especifico NTICS citado (do brand-data.yaml)
- [ ] Marcacoes visuais corretas para o estilo escolhido (animacao OU broll)
- [ ] Secao "Texto para NotebookLM" esta 100% limpa (sem marcacoes)
- [ ] CTA e especifico e nao-agressivo (tom consultivo)
- [ ] Maximo 3 textos na tela

---

## Conexao com Outras Skills

- Input vem de: `/plano-mensal` (sub-tema semanal)
- Guarde este roteiro: sera input para `/artigo-mensal` no final do mes
