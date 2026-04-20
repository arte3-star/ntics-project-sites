# Gamma API: gerar decks via REST

Workflow para criar apresentação, documento ou post via Gamma sem abrir o navegador.

## Status atual (abr/2026)

- Endpoint vivo: `POST https://public-api.gamma.app/v1.0/generations`
- Endpoint v0.2 retorna **HTTP 410 Gone**, descontinuado
- Polling de status: `GET https://public-api.gamma.app/v1.0/generations/{id}`

## Pegadinhas de implementação

| Problema | Causa | Solução |
|---|---|---|
| HTTP 403 + `error code: 1010` no POST | Cloudflare bloqueia urllib (User-Agent default `Python-urllib/3.x`) | Adicionar header `User-Agent` de browser real |
| HTTP 410 Gone | Endpoint v0.2 descontinuado | Trocar para `/v1.0/generations` |
| Verificação por `curl` na URL final retorna 403 | Decks são privados, exigem login na conta Gamma | Não validar deck via curl. Confiar no response `status=completed` + `credits.deducted > 0` |

## Schema do POST /generations

| Campo | Tipo | Valores | Obrigatório |
|---|---|---|---|
| `inputText` | string | 1 a 400000 chars | Sim |
| `textMode` | string | `preserve` / `generate` / `condense` | Sim |
| `format` | string | `presentation` / `document` / `social` / `webpage` | Não |
| `cardSplit` | string | `inputTextBreaks` / `auto` | Não |
| `numCards` | number | >= 1 | Não |
| `additionalInstructions` | string | 0 a 5000 chars | Não |
| `themeId` | string | ID do tema | Não |
| `textOptions` | object | `amount` (`brief`/`medium`/`detailed`), `tone`, `audience`, `language` | Não |
| `imageOptions` | object | `model`, `style`, `source` (`aiGenerated`/`stock`/`unsplash`) | Não |
| `cardOptions` | object | `dimensions` (`16x9`/`4x3`/`fluid`), `headerFooter` | Não |
| `exportAs` | string | `pptx` / `pdf` / `png` | Não |

## Quando usar cada `textMode`

- **preserve**: você tem texto exato que precisa sair literal nos slides. Prompts, passo a passo numerado, citações. Use com `cardSplit: inputTextBreaks` e `---` separando os slides.
- **generate**: você tem só o esqueleto (bullets curtos) e quer a Gamma expandir em conteúdo rico. Bom para palestra institucional.
- **condense**: tem texto longo (artigo, transcrição) e quer resumir em deck. Bom para "transformar relatório em pitch".

## Resposta do POST

```json
{
  "generationId": "bTIWj8PsYbrnYVlHV1Siz",
  "warnings": null
}
```

Polling no GET retorna:
```json
{
  "generationId": "...",
  "status": "pending" | "completed" | "failed",
  "gammaUrl": "https://gamma.app/docs/...",
  "exportUrl": "...",
  "credits": {"deducted": 194, "remaining": 7576}
}
```

## Verificação de sucesso (regra NTICS)

Não declarar pronto só com `200 OK` do POST.

Aguardar `status: completed` no GET, conferir `credits.deducted > 0`, e copiar `gammaUrl`. **Não** validar a URL via curl externo (deck é privado, retorna 403).

## Tool no projeto

`tools/content-gen/gamma_create.py`

Uso:
```bash
GAMMA_API_KEY="sk-gamma-..." python tools/content-gen/gamma_create.py \
  output/workshops/professores-ia-input.md \
  --format presentation \
  --text-mode preserve \
  --card-split inputTextBreaks \
  --language pt-br \
  --tone "instructional, friendly" \
  --audience "professores ensino fundamental" \
  --amount detailed \
  --image-style "modern flat educational illustration" \
  --dimensions 16x9
```

## Custos observados

- Deck de 17 cards, format presentation, textMode preserve, com imagens AI: **194 créditos**
- Plano Pro tem ~10000 créditos mensais

## Casos de uso NTICS

| Caso | Format | textMode | Imagem |
|---|---|---|---|
| Workshop / vídeo aula | presentation | preserve | aiGenerated |
| Pitch institucional | presentation | generate | aiGenerated |
| Resumo executivo de relatório | document | condense | stock |
| Carrossel rápido | social | generate | aiGenerated |
