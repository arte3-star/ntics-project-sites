# Workflow — Capa de Post Instagram NTICS

Gera uma capa 4:5 para post único do feed Instagram da NTICS, seguindo o padrão visual dos carrosseis case (foto UPPER HALF, bloco de texto sobre teal LOWER HALF, badge colorido, destaques amarelos, barra gradiente no rodape).

> Usar quando o usuario pedir "crie uma capa pra esse post", "faz uma imagem pro Instagram", "gera o post da entrega/evento X". Se for carrossel (multiplos cards), usar `/carrossel-cliente` ou `/carrossel-caso`.

## Pre-requisitos
- `LEONARDO_API_KEY` no `.env`
- Foto de referencia do evento/entrega (foto real com pessoas da NTICS)
- Descricao/caption do post que o usuario quer publicar (pra extrair headline + corpo)

## Fluxo

### Fase 0 — Gate de Design (OBRIGATORIO)

Invocar `/design-briefing` antes de qualquer chamada Leonardo. Propor ao usuario:

| Parametro | Default |
|-----------|---------|
| Modelo | `nano-banana-2` |
| Modo | `guidances.image_reference` strength `HIGH` (preserva rostos exatos) |
| Dimensao | `1856 × 2304` (4:5 Instagram feed, dimensao valida nano-banana-2) |
| Proporcao foto | UPPER HALF (50% superior — padrao case) |
| Paleta | teal `005F73` (fundo), verde `3DAA35` (badge default), amarelo `FFCC00` (destaques [YELLOW]) |
| Tom | celebratorio + institucional |

Aguardar aprovacao do usuario antes de prosseguir. Se pedir badge em outra cor, perguntar qual (verde/amarelo/rosa/laranja da paleta).

### Fase 1 — Coleta da foto de referencia

1. Se o usuario anexou a foto na conversa, procurar em `C:/Users/lucas/Downloads/` pelos arquivos de imagem mais recentes (`ls -lt *.{jpg,jpeg,png}`). Pegar o mais recente que bate com a descricao.
2. Abrir com `Read` para confirmar visualmente que e a foto correta.
3. Copiar para `output/marketing/posts-avulsos/{slug}/foto-referencia.jpg`.

### Fase 2 — Briefing de copy (conversa com usuario)

A partir da caption/descricao do post, propor:
- **Badge** (4-5 palavras, caixa alta): ex. `PARCERIAS QUE TRANSFORMAM`, `RECONHECIMENTO INSTITUCIONAL`, `PROJETO DE IMPACTO`
- **Headline** (2 linhas, caixa alta): foco no reconhecimento/evento — ex. `RECONHECIMENTO / À EDUCAÇÃO DE RIO CLARO`
- **Corpo** (2-4 linhas, caixa baixa): texto da caption reescrito em ate ~50 palavras, com destaques `[YELLOW]...[/YELLOW]` em 3-4 palavras-chave (patrocinador, projeto, ODS etc.)

Aguardar aprovacao explicita do copy antes de gerar.

### Fase 3 — Montar o prompt

Template validado (abr/2026, `output/marketing/posts-avulsos/rio-claro-reconhecimento/capa-v8.jpg`):

```
Social media carousel card, Instagram 4:5 format, no white borders, fills entire frame edge to edge. Uses the uploaded reference image. Preserve the exact faces, clothing and pose of the {N pessoas} holding the {objeto}. Do not alter their identities.
UPPER HALF of the card: full-bleed photograph of the uploaded reference image, edge to edge, no text.
SMOOTH GRADIENT TRANSITION between upper and lower halves, blending the photo into solid dark teal background below.
LOWER HALF of the card: solid dark teal 005F73 background.
Near top of lower half: small rounded pill badge with white bold uppercase text {BADGE} on {COR_BADGE} background.
Below the badge: large bold white uppercase sans-serif headline, two lines: {LINHA1} / {LINHA2}.
Below headline: smaller regular white sans-serif body text, words marked [YELLOW]...[/YELLOW] render in bright yellow color: {CORPO_COM_TAGS_YELLOW}.
Bottom edge flush: thick horizontal gradient stripe, from LEFT to RIGHT green 3DAA35 to teal 00A5B8 to pink D41A6A to orange E86428.
Clean editorial design with preserved Portuguese accents. No percent signs, no layout markers.
```

**Limite:** prompt < 1000 chars. Acima disso, Leonardo retorna `VALIDATION_ERROR` como lista (nao dict).

### Fase 4 — Executar geracao

Usar script base em `output/marketing/posts-avulsos/rio-claro-reconhecimento/gerar.py` como template. Copiar para novo diretorio `output/marketing/posts-avulsos/{slug}/gerar.py`, ajustar `PROMPT` e rodar:

```bash
python output/marketing/posts-avulsos/{slug}/gerar.py
```

Pipeline:
1. Upload foto como `init-image` v1 (retorna `init_id`)
2. POST `/v2/generations` com `guidances.image_reference` + strength HIGH
3. Poll `/v1/generations/{gen_id}` ate COMPLETE (tipicamente 60-150s; timeout 360s)
4. Download da URL retornada para `capa.jpg` (ou `capa-vN.jpg` em iteracoes)

### Fase 5 — Revisao visual obrigatoria

Usar `Read` no arquivo gerado e checar:
- [ ] Rostos preservados (sem distorcao)
- [ ] Badge com a cor correta, texto em caixa alta
- [ ] Headline completa e centralizada
- [ ] Todos os destaques `[YELLOW]` amarelos e nas palavras corretas
- [ ] Acentos PT-BR (`Ó`, `Á`, `Ã`, `Ç`, `Í`, `Ú`) sem omissao
- [ ] **Concatenacao de artigo + palavra** (ex: "a inovação" → "ainovação"): regra conhecida, se aparecer reformular sem artigo
- [ ] Barra gradiente LEFT→RIGHT no rodape
- [ ] Sem artefatos tipo `%`, numeros de zona, bordas brancas

Se houver problema, iterar no prompt e regerar com sufixo `-vN`.

### Fase 6 — Entrega

Mostrar path final (`output/marketing/posts-avulsos/{slug}/capa-vN.jpg`), tamanho, dimensao e custo (`$0.058` por geracao nano-banana-2 4:5). Oferecer ajustes.

## Regras criticas aprendidas

1. **Prompt < 1000 chars** — prompt verboso causa `VALIDATION_ERROR` silencioso (response como list com `BadRequestException`).
2. **Artigo + palavra curta concatena** — "a inovação" vira "ainovação". Reformular: "com inovação" (sem artigo) ou trocar por "à inovação".
3. **Dimensoes validas nano-banana-2:** `1856×2304` (4:5), `1472×1840` (4:5), `2048×1152` (16:9), `1536×1024` (3:2), `768×1376` (9:16). `1024×1024` e `2048×2048` FALHAM.
4. **`[YELLOW]palavra[/YELLOW]`** — funciona pra destacar ate 4 palavras/frases no corpo em amarelo.
5. **Badge colorido funciona** — `on bright green 3DAA35 background` (ou amarelo FFCC00, rosa D41A6A, laranja E86428) rende badges vibrantes. Teal `00384A` fica escuro demais — evitar.
6. **Sanitize `$`** — remover "$" do prompt (quebra GraphQL da API).
7. **Frase-chave image_reference** — sempre "uses the uploaded reference image" + "preserve the exact faces" no prompt. Sem isso o modelo ignora a foto.
8. **Acentos PT-BR no prompt** — manter intactos. O modelo renderiza corretamente UTF-8.
9. **`À` inicio de linha** — renderiza bem em headlines ("À EDUCAÇÃO DE..."), nao omitir o acento.

## Estrutura de output

```
output/marketing/posts-avulsos/
└── {slug-do-post}/
    ├── foto-referencia.jpg   # copia da foto anexada
    ├── gerar.py              # script parametrizado
    ├── capa.jpg              # versao final aprovada
    └── capa-vN.jpg           # iteracoes descartadas (para debug)
```

`{slug}` = descricao curta do post em kebab-case. Ex: `rio-claro-reconhecimento`, `entrega-iso-nubank`, `abertura-festival-circo`.

## Referencia

- `workflows/marketing/referencia/leonardo_ai_core.md` — base de conhecimento Leonardo (payloads, dimensoes, erros).
- `tools/media/generate_pilula_cover.py` — script canonico com dupla image_reference (pessoa + logo).
- `output/marketing/posts-avulsos/rio-claro-reconhecimento/` — primeiro caso validado (abr/2026), usar como template de copy/paste.
- `.tmp/marketing/carrosseis/educacao-cultural-statkraft/gerar_cards.py` — padrao UPPER/LOWER HALF dos cases.
