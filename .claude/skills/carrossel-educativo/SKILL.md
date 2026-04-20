---
name: carrossel-educativo
description: "Cria carrossel educativo sobre ESG/Responsabilidade Social (8 cards via Pillow + capa Leonardo AI) a partir de briefing ou tema"
user-invocable: true
---

> 📚 **Referência Leonardo AI:** Esta skill tem sua estrutura de geração validada — siga o workflow normalmente. Se surgir erro da API, dúvida sobre payload ou resultado visual inesperado, consulte `workflows/marketing/referencia/leonardo_ai_core.md` como base de conhecimento complementar (erros conhecidos, modos, exemplos).

Leia e execute o workflow completo em `workflows/marketing/producao/carrosseis/carrossel_educativo.md`.

## Inputs

O conteudo ja esta definido no ClickUp — nao e necessario fornecer briefing.

**Necessario:**
- Semana alvo (ex: "2026-04-07") ou "semana atual"

O agente busca a task no ClickUp, extrai o briefing e executa o pipeline completo.

## Ferramentas

| Ferramenta | Arquivo | Funcao |
|-----------|---------|--------|
| Gerador educativo | `tools/content-gen/gerar_educativos_3semanas.py` | Pipeline hibrido: Leonardo foto + Pillow pelicula + Leonardo texto |

## Estrutura dos 8 Cards

| Card | Pipeline | Funcao |
|------|----------|--------|
| 01 | Hibrido (Leo foto → Pillow pelicula → Leo texto) | Capa — foto full-bleed + tema + subtitulo |
| 02-06 | Hibrido | Conteudo — titulo + texto + frase destaque |
| 07 | Hibrido | Metodo NTICS — grid 2x2 metricas |
| 08 | Pillow puro | CTA — fundo teal solido + logo NTICS + @nticsprojetos |

## Fluxo

1. **Gate de design**: Invocar `/design-briefing` — confirmar modelo Leonardo, estilo, paleta e formato com o usuário antes de gerar qualquer imagem
2. Buscar task da semana no ClickUp — extrair tema, cards, cenas, frase do método, pergunta CTA
3. Adicionar semana ao dict `SEMANAS` em `gerar_educativos_3semanas.py`
4. Executar: `python tools/content-gen/gerar_educativos_3semanas.py`
5. **OBRIGATORIO**: Revisar visualmente os 8 cards via `/revisao-carrossel` antes de entregar
6. Corrigir achados 🔴 antes de copiar para `final/`
7. Gerar captions Instagram e LinkedIn
