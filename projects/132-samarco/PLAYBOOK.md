# Playbook — Projeto 132 (Estação Samarco / Territórios do Futuro)

> **O que é este documento.** Fonte única narrativa do projeto. Consolida visão, regras, decisões e estado atual em prosa legível. Complementa (não substitui) `state.yaml` (dado estruturado), `stakeholders.yaml`, `tasks.yaml`, e o histórico em `SecondBrain/projetos/132-samarco/`.
>
> **Como usar.** Antes de qualquer entrega ou decisão, releia as seções relevantes. Ao tomar uma decisão nova, registre na seção 12 e atualize a seção afetada. Ao fechar fase, anote no changelog (seção 13).
>
> **Última atualização:** _(preencher na primeira edição)_
> **Versão:** 0.1 (esqueleto)

---

## Parte I — Constituição (muda pouco)

### 1. Sumário executivo

> _Uma página. Quem lê isso entende o projeto em 2 minutos._
>
> Preencher: o que é, pra quem, valor contratado, fase atual, próxima decisão crítica, top 3 riscos.

_(a preencher)_

---

### 2. Visão, propósito e métricas de sucesso

> _Por que esse projeto existe pra Samarco e pra NTICS. Como saberemos que deu certo._

**Propósito Samarco:**
_(a preencher — ler TAP em `brief/tap.md` e perfil cliente em `AUTOMAÇÕES/SecondBrain/clientes/samarco.md`)_

**Propósito NTICS:**
_(a preencher)_

**Métricas de sucesso:**
- Quantitativas: _(nº inscritos, nº certificados, nº cidades cobertas, ...)_
- Qualitativas: _(satisfação, recolocação, recompra cliente, ...)_

**Gatilho de atualização:** revisitar se Samarco mudar diretriz estratégica ou se métricas contratuais forem ajustadas.

---

### 3. Escopo — territórios, trilhas, números

**12 cidades** (ver `CLAUDE.md` linhas 9-13 para lista canônica).
- MG (7): Camargos, Antônio Pereira, Bento Rodrigues†, Paracatu de Baixo†, Santa Rita Durão†, Brumal, Catas Altas
- ES (5): Meaípe, Mãe-Bá, Parati, Ubu, Recanto do Sol
- † = território sensível (rompimento Fundão 2015)

**3 trilhas formativas:**
1. Trilha Inicial — Empreendedorismo & IA (4h presenciais)
2. Estação Sabores — Culinária Sustentável (24h pres + 22h digital)
3. Estação Beleza & Estética (24h pres + 22h digital, nova 2026)

**Regra:** 1 trilha por CPF (decisão 22/04). Quórum mínimo por turma: _(preencher)_. Tamanho turma prática: **decisão pendente** — 40 ou 2×20.

**O que NÃO é escopo:**
- Não é Lei de Incentivo (sem PRONAC/MinC).
- NTICS não faz captação/inscrição (responsabilidade equipe sensibilização Samarco).
- Sem impulsionamento pago.
- Assessoria de imprensa: _(pendente decisão — NTICS envolvida?)_

**Gatilho de atualização:** mudança de cidade, trilha, ou regra de elegibilidade.

---

### 4. Stakeholders & matriz RACI

> _Quem decide o quê. Resumo aqui; detalhe em `stakeholders.yaml`._

| Decisão / Entrega | Responsável | Aprova | Consultado | Informado |
|---|---|---|---|---|
| Peça de comunicação corporativa MG+ES | NTICS (Lucas) | Amanda + Rayane | Bruna | Cíntia |
| Peça específica ES | NTICS (Lucas) | Rayane | Amanda | — |
| Cronograma / contrato | Bruna | Cíntia | Amanda | — |
| Tom editorial em cidade atingida | Lucas | Amanda + Rayane | Cíntia | — |
| Acesso SharePoint / Teams | — | Cíntia | — | Bruna |
| Voluntariado corporativo | — | _(pendente)_ | — | — |

**Aprovação interna NTICS antes de qualquer envio:** Bruna + Lucas obrigatórios.

**Stakeholders extras citados em reuniões** (nem todos no `stakeholders.yaml`): ver `~/.claude/projects/.../memory/projeto_132_stakeholders_extras.md`.

**Gatilho de atualização:** entrada/saída de pessoa-chave, mudança de papel.

---

### 5. Governança — fluxo de aprovação, canais, prazos, ritos

**Canal único oficial:** Teams / SharePoint Samarco. **NUNCA WhatsApp Web** para envio de peças.

**Prazos:**
- Aprovação ideal: 48h.
- Aprovação mínima: 24h.
- Resposta cliente em férias / ausência: usar substituto declarado (ex: Rayane substitui Amanda — registrar em `decisoes.md`).

**Ritos recorrentes:**
- _(preencher: reuniões semanais? quinzenais? quem participa? ata onde?)_

**Fluxo padrão de uma peça:**
1. Briefing (`/projeto-briefing`)
2. Produção (skill ntics-brain correspondente)
3. Aprovação interna NTICS (Bruna + Lucas)
4. Envio Samarco via SharePoint
5. Ciclo aprovação (48h)
6. Ajustes / aprovação final
7. Registro em `historico.md` via `/projeto-registrar`

**Gatilho de atualização:** mudança de canal, prazo, ou rito.

---

### 6. Identidade & comunicação

**Marca (precedência sobre cheatsheet NTICS — ver `SecondBrain/projetos/132-samarco/brand-aplicacao-samarco.md` quando criado):**
- Logo **Estação Samarco soberana** em toda peça.
- Logo NTICS apenas como "realização", proporção menor.
- Sem slogan/subtítulo extra (decisão Rayane).
- Sem régua MinC (projeto não-incentivado).
- KV oficial: _(aguardando Amanda — bloqueante)_.

**Tom editorial:**
- Positivo, futuro, reconstrução.
- Foco em "o que você está construindo agora".
- **Nunca** citar rompimento de Fundão.
- **Nunca** revitimizar. **Nunca** linguagem assistencialista ou triunfalista.

**Cidades atingidas (Bento Rodrigues, Paracatu de Baixo, Santa Rita Durão):**
- Cuidado editorial máximo.
- Qualquer dúvida → escalar Amanda + Cíntia antes de publicar.

**Do / Don't específicos:**
_(preencher conforme aprendizados)_

**Gatilho de atualização:** quando KV oficial chegar, quando Samarco enviar manual de marca, quando houver feedback editorial relevante.

---

## Parte II — Execução (atualiza constantemente)

### 7. Cronograma macro & marcos firmes

> _Datas firmadas vs. datas sugeridas. Sempre marcar a fonte (reunião X, e-mail Y)._

**Marcos firmes** (decisão Cíntia 24/04 — ver memória `projeto_132_cronograma.md`):
- _(preencher datas conforme memória)_

**Marcos sugeridos / em discussão:**
- Divulgação MG: maio _(sugestão deck, não confirmado)_
- Execução MG: fim maio / junho
- Execução ES: após MG

**Bloqueantes de cronograma:**
- KV Samarco
- Acessos SharePoint
- Plataforma Lovable
- Contratação fornecedores (4 produtores, culinarista ES, educadoras Beleza, dev Lovable)

**Gatilho de atualização:** toda vez que `state.yaml` mudar campo `fase` ou `cronograma_*`.

---

### 8. Catálogo de entregas

> _19 briefings de design + grade redes sociais. Status resumido aqui; detalhe em `state.yaml`._

**Bloco A — Pré-projeto digital (6):**
| ID | Entrega | Status | Bloqueio |
|---|---|---|---|
| A1 | KV + biblioteca ícones | _aguardando KV Samarco_ | KV oficial |
| A2 | Carrossel informativo | — | — |
| A3 | Convite post cidade | — | KV |
| A4 | Convite WhatsApp | — | KV |
| A5 | Card inscrição QR | — | KV + LP Lovable |
| A6 | Mockup LP Lovable | — | dev Lovable |

**Bloco B — Estrutura de campo (11):** pantojet, rollups (6), wind banner, avental culinária, saia bancada, moldura espelho, dolma, uniforme beleza, avental corte cabelo, placa fotos (4), camisetas equipe.
_(expandir tabela quando entrar em produção)_

**Bloco C — Certificados (2):** profissionalizante, trilha inicial.

**Grade redes sociais:**
- Pré: 2 vídeos (1/estado) + 1 carrossel.
- Durante: 12 vídeos cobertura (1/cidade) + 1 carrossel editorial/cidade.
- Pós: 1 vídeo case (2-3 min) + 1 carrossel encerramento.

**Gatilho de atualização:** toda vez que `/projeto-avanca` rodar ou status mudar no ClickUp.

---

### 9. Operação de campo

> _Como o projeto acontece no chão. Captação, turmas, certificação, plataforma._

**Captação:** Samarco (equipe sensibilização). NTICS produz peças apenas.

**Turmas:** _(tamanho a definir — 40 ou 2×20)_. Quórum mínimo: _(preencher)_.

**Certificação:** e-certificado.com (código público + LinkedIn). Bloqueante: plataforma Lovable concluída.

**Plataforma digital (Lovable):** _(status, dev contratado?, cronograma)_.

**Pâmela** (culinarista MG, continua de 2025); culinarista ES e educadoras Beleza pendentes.

**Marina** contratada por R$ 1k _(papel: preencher — ver memória `projeto_132_status_emails_27-28abr.md`)_.

**Gatilho de atualização:** entrada de fornecedor, mudança de regra operacional.

---

### 10. Orçamento, contratos & fornecedores

> _Resumo aqui; detalhe em `budget.yaml` e na planilha Drive aba FORNECEDORES._

**Valor contratado:** _(pendente — registrar quando confirmado por Cíntia)_

**Frentes de custo:**
- Produção visual (skills ntics-brain, sem custo direto além de créditos APIs)
- Produtores de campo (4)
- Culinaristas + educadoras
- Dev Lovable
- Material gráfico (rollups, pantojet, têxtil)
- Logística cidade (deslocamento, alimentação)

**Contratos firmados:**
- Marina — R$ 1.000 _(detalhar escopo)_
- _(adicionar conforme fechamento)_

**Gatilho de atualização:** todo novo contrato ou alteração de valor.

---

### 11. Riscos ativos & contingências

| # | Risco | Prob | Impacto | Mitigação | Owner |
|---|---|---|---|---|---|
| R1 | Plataforma Lovable atrasa → certificado não sai | A | Alto | Acompanhar dev semanal; plano B = certificação manual provisória | Bruna |
| R2 | Atraso acesso SharePoint comprime aprovação | M | Médio | Escalar Cíntia; usar e-mail como fallback temporário | Lucas |
| R3 | KV Samarco atrasa → peças paradas | A | Alto | Cobrar Amanda/Rayane semanal; pré-produzir o que não depende de marca | Lucas |
| R4 | Slippage editorial em cidade atingida | B | Crítico | Aprovação dupla obrigatória + revisão Cíntia em qualquer dúvida | Lucas |
| R5 | _(adicionar)_ | | | | |

**Gatilho de atualização:** novo risco identificado, mitigação executada, risco fechado.

---

## Parte III — Memória (acumula)

### 12. Log de decisões consolidadas

> _Decisões que mudam o projeto. Cada linha: data, decisão, contexto, fonte (reunião/e-mail/ata). Apêndice do `decisoes.md`, mas só as que valem pra todo o projeto (não decisão operacional do dia)._

| Data | Decisão | Contexto | Fonte |
|---|---|---|---|
| 2026-04-22 | Consolidar Mariana + quórum mínimo + 1 trilha/CPF + módulo Turismo | Reunião pós-22/04 | memória `projeto_132_decisoes_recentes.md` |
| 2026-04-24 | Cronograma firmado com Cíntia | Reunião 24/04 | memória `projeto_132_cronograma.md` |
| 2026-04-2X | Plano de comunicação aprovado; Rayane substitui Amanda em férias | E-mails 27-28/04 | memória `projeto_132_status_emails_27-28abr.md` |
| | | | |

**Gatilho de atualização:** toda decisão estratégica (não operacional). Decisão operacional vai em `SecondBrain/projetos/132-samarco/decisoes.md`.

---

### 13. Changelog do playbook

| Data | Versão | Mudança | Por |
|---|---|---|---|
| 2026-04-28 | 0.1 | Criação do esqueleto | Lucas + Claude |
| | | | |

---

## Parte IV — Referências

### 14. Mapa de arquivos & links

**Estrutura local do projeto:**
- `CLAUDE.md` — contexto operacional resumido (carregado em toda sessão)
- `state.yaml` — fase, deliverables, próxima ação, blockers (estruturado)
- `stakeholders.yaml` — todas as pessoas e contatos
- `tasks.yaml` — índice ClickUp + gmail_query + planilhas monitoradas
- `budget.yaml` — orçamento e fornecedores
- `calendar.md` — cadência de reuniões e publicações
- `brief/tap.md` — Termo de Abertura do Projeto (TAP) resumido
- `comms/events.log` — log automático do sync (Gmail + ClickUp + Drive)
- `content/` — outputs gerados (carrosseis, posts, peças)
- `.cache/` — snapshot ClickUp + Gmail + planilhas (último sync)

**SecondBrain (memória de execução, gitignored):**
- `SecondBrain/projetos/132-samarco/execucao.md` — log operacional do dia-a-dia
- `SecondBrain/projetos/132-samarco/decisoes.md` — decisões automáticas + manuais
- `SecondBrain/projetos/132-samarco/atas/` — atas formais por data
- `SecondBrain/projetos/132-samarco/brand-aplicacao-samarco.md` — regras de marca Samarco (precedência sobre NTICS-cheatsheet)
- `SecondBrain/projetos/132-samarco/historico.md` — catálogo auditável de artefatos finalizados

**Fontes externas canônicas:**
- TAP completo: `AUTOMAÇÕES/SecondBrain/projetos/132-samarco/tap.md`
- Perfil cliente: `AUTOMAÇÕES/SecondBrain/clientes/samarco.md`
- Cheatsheet NTICS: `brand/NTICS-cheatsheet.md`
- Planilha operacional: ver `tasks.yaml:planilhas_monitoradas`
- ClickUp list: ver `tasks.yaml:list_id`

---

## Como manter este documento vivo

1. **Toda decisão estratégica** → adicionar linha na seção 12 + atualizar seção afetada.
2. **Toda mudança de fase** → revisar seções 7, 8, 11.
3. **Todo novo risco** → seção 11.
4. **Todo novo contrato/fornecedor** → seção 10.
5. **Toda mudança neste documento** → linha no changelog (seção 13) e bump de versão.
6. **Mensalmente** (ou início de fase) → ler do começo ao fim, marcar o que está estagnado, revisar riscos.

> Se uma seção fica obsoleta (ex: bloqueio resolvido), **não apague** — mova pro changelog dizendo "resolvido em DD/MM por Y". Memória do projeto importa.
