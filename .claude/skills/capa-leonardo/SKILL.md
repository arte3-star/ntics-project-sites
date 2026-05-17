---
name: capa-leonardo
description: "Gera prompt Leonardo AI para capa de post (4:5) ou capa de video (9:16) com a gramatica visual NTICS unificada. Escolhe sozinho o melhor esqueleto de layout para o texto/foto recebidos. Em 9:16 aplica safe zone para nao cortar texto na UI do Reels/Stories."
user-invocable: true
---

> Referencia Leonardo AI: `workflows/marketing/referencia/leonardo_ai_core.md` (erros, payload, dimensoes).
> Gramatica visual completa: `workflows/marketing/referencia/capa_instagram_versoes.md`.

## Quando usar

Usuario pede capa de post ou capa de video NTICS. Pode passar foto + briefing completo, ou apenas texto.

- "Cria capa de post" → 4:5 (1856x2304)
- "Cria capa de video" / "video 9:16" / "Reels" / "Story" → 9:16 (1440x2560) com safe zone
- Para carrossel multi-card → use `/carrossel-cliente` ou `/carrossel-educativo`

## Inputs aceitos

- Foto de referencia (anexo, path local ou link Drive)
- Briefing/release/caption com nome do projeto, patrocinador, categoria, dado de impacto
- Formato desejado (post ou video). Se nao informado, perguntar antes de gerar

## Regra de formato

| Formato | Dimensoes | Safe zone |
|---|---|---|
| Post 4:5 | 1856 x 2304 | usar a area inteira |
| Video 9:16 | 1440 x 2560 | bandas solidas estruturais (ver abaixo) |

### Safe zone 9:16 — regra obrigatoria

Leonardo IGNORA coordenadas em pixel ("y=280", "top 280px reserved"). A unica forma que funciona e transformar a safe zone em **bandas solidas que a IA precisa pintar**, nao em area vazia. A foto fica **estritamente dentro de uma banda do meio**, e os textos sentam em bandas teal/verde no topo e rodape.

**Padrao canonico validado** (4 bandas verticais):

```
- TOP BAND 14 percent: solid dark teal 005F73 flat, holds {logo + badge}.
- SECOND BAND 50 percent: full-bleed photograph from image 1, edge to edge.
- THIRD BAND 28 percent: solid bright green 3DAA35 (ou teal) flat, holds {headline + body}.
- FOURTH BAND 8 percent: solid dark teal 005F73 flat, holds {creditos + reguazinha gradiente no rodape}.
```

Sempre usar `Strictly four horizontal bands stacked top to bottom` e fechar com `photo strictly inside the second band`. Esse "strictly" e o que faz a IA respeitar.

## Prompt-base (gramatica unificada)

Use sempre este esqueleto, escolhendo o `{ESQUELETO}` que melhor servir ao texto:

```
Social media card, Instagram {FORMATO} format, edge to edge, no white borders. Uses the uploaded reference image, preserving exact faces and composition with natural vibrant colors.

IDENTIDADE NTICS (sempre):
- Paleta: dark teal 005F73, bright green 3DAA35, pink D41A6A, orange E86428, yellow F5B800, teal medio 00A5B8.
- Reguazinha gradiente fina na borda inferior, LEFT to RIGHT: green 3DAA35 to teal 00A5B8 to pink D41A6A to orange E86428.
- Badge pill arredondada bright green 3DAA35 com {CATEGORIA} em uppercase branca.
- Headline UPPERCASE bold sans-serif branca, 2 a 3 linhas curtas, sempre sobre area solida ou overlay.
- Body menor branca com dados em [YELLOW]numero[/YELLOW].
- Acentos PT-BR preservados.

COMPOSICAO (escolha o esqueleto pelo conteudo):
- Foto cinematografica vendendo sozinha → fullbleed com overlay teal nos 40% inferiores e headline monumental.
- Texto protagonista, abertura de serie → invertido: top 45% teal solido com headline gigante 3 linhas, bottom 55% foto fullbleed.
- Numero/estatistica como estrela → grid 3 colunas (foto / bloco verde com numero gigante / bloco teal com headline).
- 3 unidades de info separaveis → foto a esquerda 60% + 3 blocos solidos empilhados a direita.
- Variacao ritmica em serie → diagonal 30 graus (foto em um triangulo, teal solido no outro), engrenagens brancas 10-15% no lado teal.
- Tema tecnologico/educacional → fundo teal, foto em moldura circular, engrenagens orbitando 10-25%.

{REGRA_SAFE_ZONE_SE_9_16}

CONTEUDO:
- CATEGORIA: {categoria}
- HEADLINE: {2 a 3 linhas curtas}
- BODY: {frase com [YELLOW]numero[/YELLOW]}
- PATROCINADOR (rodape pequeno): {nome}

Estilo final: editorial, alto contraste, impacto institucional NTICS.
```

Quando `{FORMATO}` = `9:16`, injetar:
```
SAFE ZONE 9:16: nao posicionar texto, badge, headline ou logo nos 280px superiores nem nos 420px inferiores do frame (areas cobertas pela UI do Reels/Stories e pela legenda). Concentrar todo o conteudo grafico entre y=280 e y=2140.
```

## Fluxo

1. Identifica formato (post 4:5 vs video 9:16). Se ambiguo, pergunta uma vez.
2. Le briefing/foto. Extrai categoria, headline (2-3 linhas curtas), dado, patrocinador.
3. Escolhe o esqueleto que melhor serve ao texto (ver tabela do prompt).
4. Monta o prompt final substituindo as variaveis.
5. Entrega ao usuario o prompt pronto pra colar no Leonardo (e, se solicitado, dispara via API com `nano-banana-2`, `image_reference HIGH`, `prompt_enhance OFF`).

## Saida

- Prompt final (texto pronto pra colar no Leonardo)
- Caso o usuario peca pra gerar, output em `output/marketing/posts-avulsos/{slug}/` ou `SecondBrain/projetos/{slug}/assets/capa-video/`
