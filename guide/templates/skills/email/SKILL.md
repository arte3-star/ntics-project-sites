---
name: email
description: Gera rascunho de e-mail para um stakeholder do projeto. Lê stakeholders.yaml para usar o tom certo e voice.md para respeitar o estilo de comunicação. NUNCA envia — sempre gera rascunho para aprovação.
---

# /email

Gere um rascunho de e-mail para o stakeholder indicado.

## Inputs esperados
O usuário vai indicar:
- Para quem é o e-mail (nome ou papel)
- Qual o assunto / contexto
- O que precisa comunicar (tópicos ou texto bruto)

## O que ler antes de escrever
1. `stakeholders.yaml` — encontre o destinatário, leia o tom e o canal preferido
2. `voice.md` — aplique o tom e evite as frases proibidas
3. `state.yaml` — use dados atuais do projeto se relevante

## Como escrever

### Para tom formal
- Abertura: "Prezado(a) [Nome],"
- Corpo: contexto em 1 frase, depois bullets claros
- Fechamento: próximo passo + "Fico à disposição"
- Assinatura: [Nome] | [Cargo] | [Empresa]

### Para tom semiformal
- Abertura: "Olá [Nome],"
- Direto ao ponto, linguagem mais fluida
- Fechamento: "Qualquer dúvida, é só chamar."

### Para tom informal (WhatsApp/chat)
- Máximo 3-5 linhas
- Direto. Sem "Prezado", sem "Fico à disposição"

## Regras
- NUNCA envie. Sempre apresente o rascunho com "Rascunho — aguardando sua aprovação:"
- Não use travessão (—). Use vírgula ou ponto.
- Não use frases proibidas do voice.md
- Se faltar contexto (o que comunicar), pergunte antes de escrever
