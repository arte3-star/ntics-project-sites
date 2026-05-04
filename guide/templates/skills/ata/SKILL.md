---
name: ata
description: Converte notas brutas de reunião em ata estruturada com decisões, responsáveis, prazos e tasks. Gera versão para registrar em SecondBrain e versão resumida para enviar por e-mail. Salva automaticamente no histórico do projeto.
---

# /ata

Transforme notas de reunião em ata estruturada.

## Como usar
1. Cole as notas brutas (pode ser bagunçado, áudio transcrito, bullets soltos)
2. Informe: data da reunião, quem participou, projeto relacionado

## Formato da ata

```
ATA DE REUNIÃO
Data: [data]
Projeto: [nome do projeto]
Participantes: [lista]
Duração: [se souber]

CONTEXTO
[1-2 frases: por que a reunião aconteceu]

PONTOS DISCUTIDOS
1. [Tema] — [resumo da discussão em 2-3 linhas]
2. [Tema] — [resumo]
3. [Tema] — [resumo]

DECISÕES TOMADAS
- [Decisão clara e objetiva] — decidido por: [nome]
- [Decisão] — decidido por: [nome]

PRÓXIMOS PASSOS
| O que | Quem | Até quando |
|-------|------|-----------|
| [ação] | [nome] | [data] |
| [ação] | [nome] | [data] |

PRÓXIMA REUNIÃO
[data/horário, ou "A definir"]
```

## Após gerar a ata
Pergunte ao usuário:
1. "Deseja salvar essa ata no SecondBrain do projeto?" (append em `memory/atas/`)
2. "Deseja criar as tasks de próximos passos no ClickUp?" (só se MCP do ClickUp estiver configurado)
3. "Deseja gerar um resumo de 3 linhas para enviar por WhatsApp aos participantes?"

## Regras
- Não invente informações que não estão nas notas
- Se algo não ficou claro, marque como "[verificar]" em vez de assumir
- Não use travessão (—). Use vírgula ou ponto.
- Não use frases genéricas ("Foi uma reunião muito produtiva")
