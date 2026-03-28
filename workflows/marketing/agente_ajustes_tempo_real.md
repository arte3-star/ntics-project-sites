# Agente de Ajustes em Tempo Real — Resposta a Comentários

> Agente reativo que é disparado **automaticamente** quando Lucas comenta numa tarefa do cronograma de redes sociais. Lê o pedido de ajuste, executa a correção e responde no comentário da tarefa.

---

## Objetivo

Permitir que o Lucas peça ajustes direto no chat da tarefa no ClickUp e receba a correção em minutos, sem precisar esperar o próximo ciclo semanal.

---

## Trigger

```
Gatilho: Novo comentário na lista "Cronograma de redes sociais NTICS" (901109494072)
Via: Make.com webhook → HTTP POST para agente Claude remoto
Tempo de resposta: 2-5 minutos
```

### Fluxo Make.com

```
[1] ClickUp → Watch Task Comments (lista 901109494072)
         ↓
[2] Filter → Só comentários do Lucas (user_id: 87343005)
         ↓
[3] HTTP POST → GitHub API (salva contexto em pending-ajustes/)
         ↓
[4] HTTP POST → Anthropic Trigger (dispara agente Claude remoto)
         ↓
Claude remoto:
  → Lê o comentário e a descrição da tarefa
  → Identifica o tipo de ajuste
  → Executa a correção
  → Responde com comentário na tarefa
  → Atualiza status se necessário
```

---

## Tipos de Ajuste que o Agente Processa

### 1. Ajuste de Texto
**Exemplos de comentário:**
- "Muda a abertura para algo mais direto"
- "Troca 'empresas' por 'organizações'"
- "O fechamento está muito longo, encurta"

**Ação:** Reescreve o trecho, atualiza a descrição da tarefa e responde com o antes/depois.

### 2. Ajuste de Imagem
**Exemplos:**
- "Card 3 está sem degradê"
- "A foto do card 5 parece muito artificial"
- "Precisa de mais contraste no texto"

**Ação:** Regenera a imagem via Leonardo AI com prompt ajustado, salva na pasta e responde com link.

### 3. Ajuste de Estrutura
**Exemplos:**
- "Inverte a ordem dos cards 3 e 4"
- "Adiciona mais um card sobre indicadores"
- "Remove o card 6, está repetitivo"

**Ação:** Reestrutura o conteúdo, regenera se necessário e atualiza.

### 4. Aprovação
**Exemplos:**
- "Aprovado"
- "OK, pode agendar"
- "Tá ótimo"

**Ação:** Muda status para "concluído" e responde confirmando.

### 5. Pedido de Informação
**Exemplos:**
- "Qual foi a fonte dessa notícia?"
- "Por que escolheu essa foto?"
- "Quanto tempo tem o vídeo?"

**Ação:** Responde com a informação solicitada (fonte, justificativa, metadados).

---

## Regras de Resposta

1. **Sempre responder como comentário na tarefa** (não por email ou outro canal)
2. **Tom:** Direto, conciso, profissional. Sem emojis excessivos.
3. **Se o ajuste envolve custo de API** (Leonardo AI, Perplexity): executar sem perguntar, a menos que seja uma regeneração massiva (5+ imagens)
4. **Se o ajuste é ambíguo:** Perguntar para clarificar antes de executar
5. **Sempre mostrar o resultado:** Incluir o texto novo, link da imagem, ou confirmação do que mudou
6. **Atualizar a descrição da tarefa** quando o ajuste alterar o conteúdo final

---

## Exemplo de Interação

**Lucas comenta:**
> "O card 3 do carrossel de notícias tá sem o degradê embaixo. E o texto da abertura do educativo podia ser mais curto."

**Agente responde:**
> Feito! Dois ajustes:
>
> 1. **Card 3 Notícias:** Regenerei com degradê teal. Nova imagem salva em `.tmp/marketing/carrosseis/noticias-S02/card_03.png`
>
> 2. **Abertura Educativo:**
>    - Antes: "Os territórios mais prósperos têm algo em comum: empresas que investem em educação."
>    - Depois: "Empresas que investem em educação transformam territórios inteiros."
>
> Descrição da tarefa atualizada. Algo mais?

---

## Configuração Necessária

### No Make.com
1. Módulo: ClickUp → Watch Task Comments
   - Lista: 901109494072
   - Polling: a cada 5 minutos
2. Filtro: `comment.user.id = 87343005` (Lucas)
3. HTTP Module → GitHub API (commit contexto)
4. HTTP Module → Anthropic Trigger

### No Claude Code
- Trigger remoto configurado com acesso a:
  - ClickUp API (ler/escrever tarefas e comentários)
  - Leonardo AI (regenerar imagens)
  - Google Drive (salvar assets)
  - Repositório local (ler workflows e brand book)
