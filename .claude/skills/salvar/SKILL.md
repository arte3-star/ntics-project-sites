---
name: salvar
description: "Salva momento da conversa no vault Obsidian (segundo cérebro) com contexto, decisões e palavras exatas"
user-invocable: true
---

# /salvar — Salvar no Segundo Cérebro

Quando o usuário invocar `/salvar`, grave o momento atual da conversa no vault Obsidian.

## Vault

- **Caminho:** `G:\O meu disco\AUTOMAÇÕES\SecondBrain`
- **Fallback:** Se o MCP Obsidian não estiver disponível, escreva o arquivo `.md` diretamente no filesystem

## Como executar

1. **Identifique o conteúdo a salvar:**
   - Se o usuário disse `/salvar` sem contexto adicional, salve os últimos trechos relevantes da conversa
   - Se o usuário disse `/salvar [tema]`, foque nesse tema específico

2. **Determine o tipo de nota:**
   - **Conversa** → `conversas/YYYY-MM/YYYY-MM-DD-<topic-slug>.md`
   - **Decisão** → `decisoes/YYYY-MM-DD-<topic-slug>.md`
   - **Ideia** → `ideias/YYYY-MM-DD-<topic-slug>.md`
   - Na dúvida, use conversa

3. **Crie a nota com este formato:**

```markdown
---
date: YYYY-MM-DD
projeto: <nome do projeto se aplicável>
tags: [<tags relevantes>]
resumo: <uma linha descrevendo o conteúdo>
---

# <Título descritivo>

## Contexto
<O que motivou essa conversa / por que estávamos falando disso>

## Pontos Principais
<Trechos importantes — PRESERVAR AS PALAVRAS EXATAS DO LUCAS quando possível>
<Usar aspas para citações diretas>

## Decisões Tomadas
<O que foi decidido, se aplicável>

## Próximos Passos
<O que ficou pendente, se aplicável>
```

4. **Crie a subpasta do mês** se não existir (ex: `conversas/2026-03/`)

5. **Confirme ao usuário** com:
   - Caminho do arquivo criado
   - Resumo do que foi salvo
   - Tags aplicadas

## Regras

- **SEMPRE preserve as palavras exatas do Lucas** — o valor principal é poder buscar "como eu falei"
- Use slugs em português sem acentos para nomes de arquivo (ex: `decisao-obsidian-vault`)
- Tags devem ser lowercase, sem acento, separadas por vírgula
- Vincule decisões à conversa original com `[[conversas/...]]` quando aplicável
- Não salve informações sensíveis (senhas, tokens, chaves de API)
