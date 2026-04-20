# Agente de Conteudo Semanal — Producao + Revisao Autonoma

> Agente autonomo que roda todo **domingo as 20h** via Claude Code scheduled task.
> Produz as pecas da semana, revisa cada uma contra o brand book, corrige problemas e entrega conteudo com qualidade publicavel no ClickUp.

---

## Objetivo

Produzir E revisar autonomamente as pecas semanais de conteudo. As tasks JA EXISTEM no ClickUp — o agente apenas busca, produz e atualiza. O Lucas so precisa aprovar ou pedir ajustes via comentarios no ClickUp.

---

## Modelo de Operacao

**Tasks JA EXISTEM** na lista `Cronograma de redes sociais NTICS` (ID: `901109494072`).
O agente **NAO cria tasks** — busca por due_date e atualiza as existentes.

**Description NUNCA e modificada** — preserva o briefing original criado pelo plano mensal.
O output vai nos **campos customizados** + **comentario** na task.

---

## Pecas Semanais

| Dia | Tipo | Task no ClickUp | Observacao |
|-----|------|-----------------|------------|
| Segunda | Carrossel Educativo | `Carrossel Educativo SXX — {tema}` | `/carrossel-educativo` |
| Terca | Artigo Noticias ESG | `Artigo Noticias SXX — Noticias ESG semana XX` | Gerado primeiro; task e entregue ao Lucas para postar no site |
| Terca | Carrossel Noticias ESG | `Carrossel Noticias SXX — Noticias ESG semana XX` | `/carrossel-noticias`; gerado apos o artigo, caption inclui link do artigo |
| Quinta | Carrossel Projeto | `Carrossel Projeto SXX — #{num} {projeto} ({patrocinador})` | `/carrossel-case` |

**Importante — terca tem 2 tasks:**
- O artigo e gerado primeiro (Perplexity → HTML → Drive → atualiza task `Artigo Noticias SXX`)
- Depois o carrossel e gerado usando o link do artigo na caption (atualiza task `Carrossel Noticias SXX`)
- Ambas as tasks existem no ClickUp e sao atualizadas separadamente com seus respectivos assets

**Video:** Producao de video ainda nao esta estruturada — tasks de Video existem no ClickUp mas NAO sao produzidas por este agente. Pular tasks do tipo `Video SXX`.

---

## Execucao

### Fase 1: Identificar tarefas da semana

1. Buscar tarefas da proxima semana:
   ```bash
   python tools/integrations/create_social_media_tasks.py get-week --start {YYYY-MM-DD da segunda}
   ```
2. Filtrar tarefas com status "nao iniciado"
3. Ler a descricao de cada tarefa para entender o briefing
4. Identificar o tipo pelo nome: `Carrossel Educativo`, `Carrossel Noticias`, `Carrossel Projeto`
5. **Ignorar** tasks do tipo `Video SXX` — producao de video nao esta estruturada ainda

### Fase 2: Carregar referencias da marca

1. Consultar `brand-book/data/brand-data.yaml` — dados oficiais
2. Consultar `brand-book/02-identidade-verbal/tom-de-voz.md` — tom de voz
3. Consultar memorias `feedback_leonardo_prompts.md` e `feedback_editorial_tone.md`

### Fase 3: Loop por tarefa (CRIAR → REVISAR → CORRIGIR → ENTREGAR)

Para CADA tarefa da semana, executar o ciclo completo:

#### 3a. CRIAR

Identificar o tipo e executar o workflow correspondente:

| Tipo | Workflow | Tool |
|------|----------|------|
| Carrossel Educativo | `workflows/marketing/producao/carrosseis/carrossel_educativo.md` | `tools/content-gen/gerar_carrossel_educativo.py` |
| Carrossel Noticias ESG | `workflows/marketing/producao/carrosseis/carrossel_noticias.md` | `tools/content-gen/gerar_carrossel_noticias_v2.py` |
| Carrossel Projeto | `workflows/marketing/producao/carrosseis/carrossel_case_projeto.md` | Leonardo AI + fotos do relatorio |

**Ordem de producao na terca (Carrossel Noticias):**
O workflow `/carrossel-noticias` ja cobre tudo em sequencia:
1. Serper /news busca noticias reais com URLs verificadas → Claude seleciona 7 e redige campos
2. Leonardo AI gera os 9 cards (sem init_image — paisagens sem pessoas via cena_foto + negative_prompt)
3. **Revisao visual obrigatoria** (Fase 4 do workflow) — reprovar e regenerar internamente antes de avancar
4. Gera artigo HTML com fotos cropadas dos cards → `output/marketing/artigos/Artigo-noticias/`
5. Caption inclui link do artigo → `output/marketing/carrosseis/noticias/`
Tudo isso sai de uma unica task do ClickUp (`Carrossel Noticias SXX`).

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
- [ ] Proporcao 1856x2304 (4:5) — OBRIGATORIO com Nano Banana 2
- [ ] Logo NTICS no CTA com posicao e tamanho corretos
- [ ] Consistencia visual entre cards da mesma serie
- [ ] Legibilidade — texto com contraste suficiente

**Checklist Audio/Video:**
- [ ] Roteiro cabe em 60-90 segundos
- [ ] Fluxo narrativo: abertura → desenvolvimento → metodo NTICS → fechamento
- [ ] Audio sem cortes ou artefatos
- [ ] Alinhamento com briefing editorial da semana

#### 3c. CORRIGIR (se necessario)

- Corrigir automaticamente tudo que for possivel (texto, tom, dados, CTA)
- Regenerar imagens se tiverem problemas visuais
- Escalar para o Lucas APENAS problemas que exigem decisao humana

#### 3d. ENTREGAR

Quando a peca passar na revisao:

1. **Upload para Google Drive** via API (link imediato, sem delay de sync):
   ```bash
   python tools/integrations/upload_to_drive.py \
     --source output/marketing/carrosseis/{tipo}/semana-{data}/ \
     --dest "Carrosseis/{Tipo}/semana-{data}"
   ```
   Retorna URL publica da pasta.

2. **Atualizar task no ClickUp** — apenas campos customizados (description NAO e tocada):
   ```bash
   python tools/integrations/create_social_media_tasks.py update-assets \
     --task-id {TASK_ID} \
     --assets .tmp/marketing/assets_update.json
   ```

   O JSON de assets:
   ```json
   {
     "drive_folder_url": "https://drive.google.com/...",
     "caption_ig": "Caption pronta para Instagram...",
     "caption_li": "Caption pronta para LinkedIn...",
     "content_summary": "Carrossel Educativo | 8 cards | Tema: Impacto genuino"
   }
   ```

   Isso automaticamente:
   - Grava `drive_folder`, `caption_ig`, `caption_li` nos campos customizados
   - Adiciona comentario com resumo + checklist de aprovacao
   - Muda status para "revisao"

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
| Carrossel Educativo | `output/marketing/carrosseis/educativos/semana-{data}/` | 8 cards (.jpg) + descricao.txt |
| Artigo Noticias | `output/marketing/artigos/` | artigo-noticias-esg-semana-{data}.html + 3 imagens |
| Carrossel Noticias | `output/marketing/carrosseis/noticias/semana-{data}/` | 9 cards (.jpg) + descricao.txt + manifest.json |
| Video | `output/marketing/videos/` | roteiro.md + audio.mp3 |
| Carrossel Projeto | `output/marketing/carrosseis/cases/{slug}/` | 8 cards (.jpg) + textos + linkedin-carrossel.pdf |

---

## Regras

- **Tom:** Positivo, construtivo, inspiracional. Nunca usar sigla CSR.
- **Imagens:** Realistas, espontaneas. Degrade teal #005F73 na parte inferior. Texto sempre sobre area solida.
- **Dados NTICS:** Sempre conferir com `brand-book/data/brand-data.yaml`
- **Noticias:** Nao repetir noticias ja usadas em semanas anteriores (checar manifest.json)
- **Description:** NUNCA modificar. Output vai nos campos customizados + comentario.
- **Se API falhar:** Documentar erro no comentario da tarefa e seguir com as demais pecas
- **Autonomia:** Voce cria, revisa, corrige e entrega. O Lucas so precisa aprovar ou pedir ajustes via comentarios no ClickUp.

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

## Campos Customizados (IDs hardcoded)

| Campo | ID | Tipo |
|-------|-----|------|
| `drive_folder` | `1d64bc13-8d71-43b1-a1d0-58ee7dc77c9f` | URL |
| `caption_ig` | `5a040812-38d9-45a9-a911-4fcc17396d10` | Text |
| `caption_li` | `f1fd09a5-7dc8-48bd-959d-3724baf21edd` | Text |

---

## O Que NAO Faz Parte Deste Agente

- **Newsletter** — roda mensalmente, trigger manual (`/newsletter`)
- **Artigo Mensal** — roda mensalmente, trigger manual (`/artigo-site`)
- **Carrossel Projeto Ativo Cliente** — roda sob demanda (`/carrossel-cliente`)
- **Publicacao LinkedIn** — feita pelo n8n Agente Publicador (webhook ClickUp)

---

## Referencias

| Recurso | Caminho |
|---------|---------|
| Tom de voz | `brand-book/02-identidade-verbal/tom-de-voz.md` |
| Dados NTICS | `brand-book/data/brand-data.yaml` |
| Mensagens-chave | `brand-book/02-identidade-verbal/mensagens-chave.md` |
| Calendario editorial | ClickUp Doc `8cje8p1-62051` pagina `8cje8p1-40051` |
| Regras Leonardo AI | Memoria `feedback_leonardo_prompts.md` |
| Tom editorial | Memoria `feedback_editorial_tone.md` |
| Script ClickUp | `tools/integrations/create_social_media_tasks.py` |
| Upload Drive | `tools/integrations/upload_to_drive.py` |

---

## Trigger

```
Frequencia: Semanal (domingo 20:00 BRT)
Tipo: Claude Code Scheduled Task
ID: agente-criador-semanal
```
