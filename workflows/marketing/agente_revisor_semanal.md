# Agente Revisor Semanal — Quality Gate de Conteúdo

> Agente autônomo que roda toda **segunda às 8h**, após o agente criador. Revisa todo o conteúdo gerado, verifica qualidade, consistência e alinhamento com a marca, e entrega para aprovação final do Lucas.

---

## Objetivo

Atuar como **revisor editorial e de design** de todas as peças da semana, garantindo que o conteúdo chegue ao Lucas já com qualidade publicável. O Lucas só precisa aprovar ou pedir ajustes pontuais.

---

## Execução

### Fase 1: Identificar peças para revisão

1. Buscar tarefas da semana atual no ClickUp (lista `901109494072`)
2. Filtrar por status "em produção"
3. Para cada tarefa, ler a descrição e identificar a pasta de assets

### Fase 2: Revisão de Texto

Para cada peça, verificar:

- [ ] **Sem sigla CSR** — sempre "Responsabilidade Social" por extenso
- [ ] **Tom positivo** — nenhuma frase negativa/alarmista. Framing de oportunidade, não de problema
- [ ] **Tom de voz NTICS** — informativo, confiante, inspirador, acessível (consultar `brand-book/02-identidade-verbal/tom-de-voz.md`)
- [ ] **Dados corretos** — números da NTICS conferidos com `brand-book/data/brand-data.yaml`
- [ ] **Sem erros gramaticais** — ortografia, concordância, pontuação
- [ ] **CTA presente** — todo carrossel deve ter card final com call-to-action
- [ ] **Coerência temática** — o tema da semana é consistente entre vídeo, carrossel educativo e briefing editorial

### Fase 3: Revisão Visual (Carrosséis)

Para cada imagem gerada, verificar:

- [ ] **Degradê teal** (#005F73) presente na parte inferior de todos os cards
- [ ] **Texto sobre área sólida** — nunca sobre a zona de transição do degradê
- [ ] **Fotos realistas e espontâneas** — sem aparência artificial ou stock genérico
- [ ] **Proporção correta** — 1080×1350 (4:5) para carrosséis
- [ ] **Logo NTICS** no CTA — posição e tamanho corretos
- [ ] **Consistência visual** — todos os cards da mesma série com estilo uniforme
- [ ] **Legibilidade** — texto com contraste suficiente, tamanho adequado

### Fase 4: Revisão de Áudio/Vídeo

Para o roteiro e áudio:

- [ ] **Duração** — roteiro cabe em 60-90 segundos
- [ ] **Fluxo narrativo** — abertura → desenvolvimento → método NTICS → fechamento
- [ ] **Áudio gerado** — qualidade OK, sem cortes ou artefatos
- [ ] **Alinhamento com briefing** — tema do áudio bate com o editorial da semana

### Fase 5: Revisão de Consistência Semanal

Olhar as 4 peças como um todo:

- [ ] **Tema coerente** — todas as peças da semana falam do mesmo tema central
- [ ] **Sem repetição** — notícias ESG não repetem semanas anteriores
- [ ] **Progressão editorial** — o tema se encaixa na fase do arco narrativo (consciência/autoridade/confiança/etc.)
- [ ] **Completude** — todas as 4 peças foram produzidas (ou há justificativa para ausência)

### Fase 6: Relatório e Encaminhamento

Para cada tarefa revisada:

1. **Se aprovada:**
   - Mudar status para "revisão"
   - Adicionar comentário: "@Lucas Rotta — Conteúdo revisado e aprovado pelo agente. Pronto para sua aprovação final."
   - Incluir no comentário um resumo do que foi produzido

2. **Se com problemas:**
   - Manter status "em produção"
   - Adicionar comentário detalhando os problemas encontrados
   - Se possível, corrigir automaticamente (erros de texto, ajustes menores)
   - Se não for possível corrigir, listar o que precisa de atenção: "@Lucas Rotta — Encontrei [X] problemas que precisam de atenção antes da publicação: [lista]"

3. **Resumo semanal:**
   - Adicionar comentário na primeira tarefa da semana com visão geral:
     - Quantas peças revisadas
     - Quantas aprovadas vs com problemas
     - Observações gerais sobre qualidade

---

## Critérios de Aprovação Automática

O revisor pode aprovar automaticamente (status → "revisão") quando:
- Todos os checklists acima passam
- Nenhum erro crítico encontrado
- Conteúdo está alinhado com o briefing editorial

O revisor deve escalar para o Lucas quando:
- Dados da NTICS precisam de confirmação
- Tom do texto está ambíguo ou potencialmente negativo
- Imagens têm problemas visuais que não podem ser corrigidos automaticamente
- Projeto do carrossel ainda não foi definido

---

## Referências

| Recurso | Caminho |
|---------|---------|
| Tom de voz | `brand-book/02-identidade-verbal/tom-de-voz.md` |
| Dados NTICS | `brand-book/data/brand-data.yaml` |
| Mensagens-chave | `brand-book/02-identidade-verbal/mensagens-chave.md` |
| Calendário editorial | ClickUp Doc `8cje8p1-62051` página `8cje8p1-37991` |
| Regras Leonardo AI | Memória `feedback_leonardo_prompts.md` |
| Tom editorial | Memória `feedback_editorial_tone.md` |

---

## Trigger

```
Frequência: Semanal (segunda 08:00 BRT)
Tipo: Scheduled trigger (Claude Code)
Depende de: Agente Criador ter rodado (domingo 20:00)
```
