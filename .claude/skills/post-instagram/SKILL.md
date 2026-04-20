---
name: post-instagram
description: "Cria capa 4:5 para post unico no feed Instagram NTICS via Leonardo AI (nano-banana-2 + image_reference). Padrao case UPPER/LOWER HALF, badge verde, destaques amarelos, barra gradiente."
user-invocable: true
---

> 📚 **Referencia Leonardo AI:** Siga o workflow normalmente. Se surgir erro da API, duvida sobre payload ou resultado visual inesperado, consulte `workflows/marketing/referencia/leonardo_ai_core.md` como base complementar (erros conhecidos, dimensoes validas, modos).

Leia e execute o workflow completo em `workflows/marketing/producao/posts/post-instagram.md`.

## Quando usar

Usuario pede capa/imagem para **um post unico** do Instagram NTICS (entrega de placa, evento, reconhecimento, anuncio). Para carrossel com multiplos cards, usar `/carrossel-cliente` ou `/carrossel-caso`.

## Inputs

- **Foto de referencia** do evento/entrega — geralmente anexada na conversa ou em `C:/Users/lucas/Downloads/`
- **Descricao/caption** do post (pra extrair headline + corpo)
- **Slug curto** do post (opcional — inferir da descricao, ex: `rio-claro-reconhecimento`)

## Ferramentas

| Ferramenta | Arquivo | Funcao |
|-----------|---------|--------|
| Gerador post unico | Template em `output/marketing/posts-avulsos/rio-claro-reconhecimento/gerar.py` | Pipeline Leonardo: upload foto → image_reference HIGH → poll → download |

## Estrutura da capa (padrao NTICS)

| Elemento | Detalhe |
|----------|---------|
| UPPER HALF (50%) | Foto de referencia preservada (rostos exatos) |
| Gradient transition | Suave entre foto e bloco inferior |
| LOWER HALF | Fundo teal solido `005F73` |
| Badge topo lower | Pill colorido (verde `3DAA35` default), texto branco caixa alta |
| Headline | 2 linhas, branco caixa alta sans-serif bold |
| Corpo | 2-4 linhas, branco sans-serif, 3-4 palavras em `[YELLOW]...[/YELLOW]` |
| Rodape | Barra gradiente LEFT→RIGHT: verde → teal → rosa → laranja |

## Fluxo

1. **Gate de design** — Invocar `/design-briefing` antes de qualquer chamada Leonardo (modelo, paleta, badge, dimensao)
2. **Coleta foto** — identificar e copiar para `output/marketing/posts-avulsos/{slug}/foto-referencia.jpg`
3. **Copy** — propor badge + headline + corpo com destaques `[YELLOW]`, aguardar aprovacao
4. **Gerar** — copiar o template `gerar.py`, ajustar PROMPT, rodar
5. **Revisao visual OBRIGATORIA** — checar rostos, acentos, destaques amarelos, concatenacoes (ex: "a inovação" → "ainovação")
6. **Iterar** se necessario (`capa-v2.jpg`, `capa-v3.jpg`) ate aprovacao

## Regras criticas

- Prompt **< 1000 chars** (acima: `VALIDATION_ERROR`)
- Artigo + palavra curta **concatena** — reformular sem artigo
- Dimensoes validas: `1856×2304` (4:5). `1024×1024` e `2048×2048` **falham**
- `[YELLOW]palavra[/YELLOW]` funciona pra destacar palavras-chave
- Sempre `strength: HIGH` no image_reference pra preservar rostos

## Custo tipico

`$0.058` por geracao nano-banana-2 a `1856×2304`. Orçar 2-3 iteracoes por post = ~$0.15-0.20.
