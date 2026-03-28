# Agente de Conteudo Semanal — Producao + Revisao Autonoma

> Agente autonomo que roda todo **domingo as 20h**. Produz as 4 pecas da semana, revisa cada uma contra o brand book, corrige problemas automaticamente e entrega conteudo com qualidade publicavel no ClickUp.

---

## Objetivo

Produzir E revisar autonomamente as 4 pecas semanais de conteudo, entregando ao Lucas apenas a aprovacao final:

1. **Carrossel Educativo** (segunda) — cards sobre o tema da semana
2. **Carrossel Noticias ESG** (terca) — curadoria via Perplexity + imagens Leonardo AI
3. **Video** (quarta) — roteiro + audio narracao
4. **Carrossel Projeto** (quinta) — se houver relatorio/fotos disponiveis

---

## Execucao

### Fase 1: Identificar tarefas da semana

1. Ler tarefas da proxima semana no ClickUp (lista `901109494072`)
2. Filtrar por `due_date` da semana seguinte (segunda a sexta)
3. Identificar quais tarefas estao com status "nao iniciado"
4. Ler a descricao de cada tarefa para entender o briefing

### Fase 2: Carregar referencias da marca

1. Consultar `brand-book/data/brand-data.yaml` — dados oficiais
2. Consultar `brand-book/02-identidade-verbal/tom-de-voz.md` — tom de voz
3. Consultar memorias `feedback_leonardo_prompts.md` e `feedback_editorial_tone.md`

### Fase 3: Loop por tarefa (CRIAR → REVISAR → CORRIGIR → ENTREGAR)

Para CADA tarefa da semana, executar o ciclo completo:

#### 3a. CRIAR

Identificar o tipo de peca e executar o workflow correspondente:

| Tipo | Workflow | Tool |
|------|----------|------|
| Carrossel Noticias ESG | `workflows/marketing/carrossel_noticias.md` | `tools/gerar_carrossel_noticias.py` |
| Roteiro Video | `workflows/marketing/roteiro_video.md` | Edge-TTS (pt-BR-AntonioNeural) |
| Carrossel Educativo | (briefing na tarefa) | `tools/generate_images_leonardo.py` |
| Carrossel Projeto | `workflows/marketing/carrossel_projeto.md` | `tools/generate_images_leonardo.py` |

Salvar em `.tmp/marketing/` nas subpastas correspondentes.

#### 3b. REVISAR (imediatamente apos criar)

**Checklist de Texto:**
- [ ] Sem sigla CSR — sempre "Responsabilidade Social" por extenso
- [ ] Tom positivo — framing de oportunidade, nao de problema
- [ ] Tom de voz NTICS — informativo, confiante, inspirador, acessivel
- [ ] Dados conferidos com `brand-data.yaml`
- [ ] Sem erros gramaticais (ortografia, concordancia, pontuacao)
- [ ] CTA presente no card final
- [ ] Coerencia tematica entre as pecas da semana

**Checklist Visual (carrosseis):**
- [ ] Degrade teal #005F73 na parte inferior de todos os cards
- [ ] Texto sobre area solida do degrade (nunca sobre zona de transicao)
- [ ] Fotos realistas e espontaneas (sem aparencia artificial/stock)
- [ ] Proporcao 1080x1350 (4:5) para carrosseis
- [ ] Logo NTICS no CTA com posicao e tamanho corretos
- [ ] Consistencia visual entre cards da mesma serie
- [ ] Legibilidade — texto com contraste suficiente

**Checklist Audio/Video:**
- [ ] Roteiro cabe em 60-90 segundos
- [ ] Fluxo narrativo: abertura -> desenvolvimento -> metodo NTICS -> fechamento
- [ ] Audio sem cortes ou artefatos
- [ ] Alinhamento com briefing editorial da semana

#### 3c. CORRIGIR (se necessario)

- Corrigir automaticamente tudo que for possivel (texto, tom, dados, CTA)
- Regenerar imagens se tiverem problemas visuais
- Escalar para o Lucas APENAS problemas que exigem decisao humana:
  - Ambiguidade de tom
  - Dados nao confirmados
  - Fotos/relatorios indisponiveis

#### 3d. ENTREGAR

Quando a peca passar na revisao:

1. Atualizar tarefa no ClickUp:
   - Adicionar secao "Conteudo Gerado" na descricao com link da pasta
   - Mudar status para **"revisao"** (pronto para aprovacao do Lucas)

2. Adicionar comentario na tarefa:
   - Resumo do que foi produzido
   - Resultado da revisao (todos checks OK ou lista de ressalvas)
   - "@Lucas Rotta — Conteudo produzido e revisado. Pronto para sua aprovacao."

### Fase 4: Resumo semanal

Adicionar comentario na PRIMEIRA tarefa da semana com visao geral:
- Quantas pecas produzidas e revisadas
- Quantas aprovadas automaticamente vs com ressalvas
- Observacoes gerais sobre qualidade
- Proximos passos

---

## Outputs

| Peca | Pasta | Arquivos |
|------|-------|----------|
| Carrossel Noticias | `.tmp/marketing/carrosseis/noticias-SXX/` | 8 cards + CTA (.png) + textos (.md) |
| Video | `.tmp/marketing/videos/semana-XX/` | roteiro.md + audio.mp3 |
| Carrossel Educativo | `.tmp/marketing/carrosseis/educativo-SXX/` | 7-8 cards (.png) + textos (.md) |
| Carrossel Projeto | `.tmp/marketing/carrosseis/projeto-SXX/` | 7 cards + CTA (.png) + textos (.md) |

---

## Regras

- **Tom:** Positivo, construtivo, inspiracional. Nunca usar sigla CSR.
- **Imagens:** Realistas, espontaneas. Degrade teal #005F73 na parte inferior. Texto sempre sobre area solida.
- **Dados NTICS:** Sempre conferir com `brand-book/data/brand-data.yaml`
- **Noticias:** Nao repetir noticias ja usadas em semanas anteriores
- **Se API falhar:** Documentar erro no comentario da tarefa e seguir com as demais pecas
- **Autonomia:** Voce cria, revisa, corrige e entrega. O Lucas so precisa aprovar ou pedir ajustes pontuais via comentarios no ClickUp.

---

## Criterios de Aprovacao Automatica

Pode marcar como "revisao" (pronto para Lucas) quando:
- Todos os checklists passam
- Nenhum erro critico encontrado
- Conteudo alinhado com briefing editorial

Deve escalar para o Lucas quando:
- Dados da NTICS precisam de confirmacao
- Tom do texto ambiguo ou potencialmente negativo
- Imagens com problemas que nao podem ser corrigidos automaticamente
- Projeto do carrossel sem dados/fotos disponiveis

---

## Referencias

| Recurso | Caminho |
|---------|---------|
| Tom de voz | `brand-book/02-identidade-verbal/tom-de-voz.md` |
| Dados NTICS | `brand-book/data/brand-data.yaml` |
| Mensagens-chave | `brand-book/02-identidade-verbal/mensagens-chave.md` |
| Calendario editorial | ClickUp Doc `8cje8p1-62051` pagina `8cje8p1-37991` |
| Regras Leonardo AI | Memoria `feedback_leonardo_prompts.md` |
| Tom editorial | Memoria `feedback_editorial_tone.md` |

---

## Trigger

```
Frequencia: Semanal (domingo 20:00 BRT)
Tipo: Scheduled Task (Claude Code)
```
