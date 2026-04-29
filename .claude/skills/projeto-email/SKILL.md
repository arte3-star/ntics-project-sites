---
name: projeto-email
description: "Gera draft Gmail para comunicação do projeto (calendário social, relatório mensal, aviso de cidade, status para produtor, release de pauta) usando stakeholders.yaml do projeto"
user-invocable: true
---

# /projeto-email — Draft Gmail contextualizado

Quando o usuário invocar `/projeto-email <slug> <tipo>`, gere um draft Gmail apropriado usando dados do projeto.

## Entrada

- `<slug>` — ex: `132-samarco`
- `<tipo>` — um de: `calendario-social`, `relatorio-mensal`, `aviso-cidade`, `status-produtor`, `release-pauta`, `solicitacao` (livre)

## Passos

1. **Carregar contexto (ordem obrigatória):**
   - `brand/NTICS-cheatsheet.md` — tom de voz NTICS, regras de pontuação (nunca travessão `—`), vocabulário preferido
   - `SecondBrain/projetos/{slug-canonico}/brand-aplicacao-{patrocinador}.md` — tom específico do projeto (ex: Samarco = positivo, reconstrução, sem citar Fundão). Precedência sobre cheatsheet.
   - `projects/{slug}/stakeholders.yaml` — destinatários, canais, cadência
   - `projects/{slug}/CLAUDE.md` — contexto operacional
   - `projects/{slug}/calendar.md` — quando aplicável (calendário social, relatório mensal)
   - `projects/{slug}/state.yaml` — fase atual e deliverables recentes

2. **Montar e-mail conforme tipo:**

   - **`calendario-social`** — destinatário: Amanda (+ Rayane em cc). Assunto: `[Estação Samarco] Calendário de redes sociais — {mes}`. Corpo: tabela HTML com peças planejadas × datas × status, reutilizando padrão de `workflows/marketing/producao/email_calendario_social.md`.

   - **`relatorio-mensal`** — destinatário: Amanda + Cíntia (+ Rayane cc). Assunto: `[Estação Samarco] Relatório {mes/YYYY}`. Corpo: resumo de entregas do mês + próximos passos + números quando disponíveis.

   - **`aviso-cidade`** — destinatário a confirmar (equipe sensibilização Samarco). Assunto: `[Estação Samarco — {cidade}] Aviso de ativação {data}`. Corpo: dados da cidade + trilhas + CTA para sensibilização local.

   - **`status-produtor`** — destinatário: produtor local da cidade. Assunto: `[Estação Samarco — {cidade}] Status semanal`. Corpo: o que foi feito, próximos passos, pedidos de evidência.

   - **`release-pauta`** — destinatário: Amanda + Cíntia. Assunto: `[Estação Samarco] Release para aprovação — {tema}`. Corpo: texto de release em PT-BR com parágrafo de acessibilidade padrão NTICS (ver `SecondBrain/institucional/templates-acessibilidade.md` se existir).

3. **Criar draft via Gmail MCP:**
   - Usar `mcp__claude_ai_Gmail__create_draft` com `to`, `cc`, `subject`, `body` (HTML quando for calendário/relatório com tabela).
   - Se o e-mail do destinatário não estiver em `stakeholders.yaml` (muitos estão como `null` no 132), perguntar ao usuário antes de criar o draft — nunca inventar endereço.

4. **Verificar** (obrigatório antes de declarar sucesso):
   - Após `create_draft`, chamar `search_threads("in:drafts subject:...")` com parte do assunto para confirmar que o draft existe.
   - Reportar ao usuário: link aberto no Gmail + preview do primeiro parágrafo.

## Regras

- **Canal oficial com Samarco é Teams/SharePoint.** Gmail NTICS é usado só para trocas internas ou casos onde o compliance permite. Se o tipo exigir envio formal via SharePoint, gerar o **conteúdo** mas alertar o usuário que o envio oficial precisa ser feito manualmente no Teams.
- **Tom editorial do projeto** (positivo, sem citar rompimento em 132).
- **Nunca travessão `—`** em e-mails.
- **Aprovação interna NTICS** (Bruna + Lucas) antes de qualquer envio ao cliente. O draft fica em Gmail para revisão; nunca enviar automaticamente.
