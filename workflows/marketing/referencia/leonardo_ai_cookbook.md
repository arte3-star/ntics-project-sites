# Leonardo AI, Cookbook NTICS

Detalhes completos, aprendizados, exemplos práticos e FAQ. Para referência rápida (payload mínimo, dimensões, checklist), ver [leonardo_ai_core.md](leonardo_ai_core.md).

Este documento é consulta sob demanda quando surgir erro de API, dúvida sobre estrutura de prompts, ou novo caso de uso.

---

## 1. Quando usar cada modo

Leonardo suporta 3 modos de geração na NTICS. Escolha pelo objetivo:

| Modo | Quando usar | Exemplo prático |
|---|---|---|
| **Pure prompt** (sem referência) | Cenário genérico, sem pessoa ou logo específicos | Artigo site, carrossel de notícias ESG, cenas ilustrativas |
| **Image Reference** (com referência) | Preservar rosto real, logo, ou foto de projeto | Carrossel cliente, capas de pílula, cards de case |
| **Pipeline híbrido** (Leonardo + Pillow) | Controle total de texto + fundo fotorrealista | Carrosséis educativos NTICS |

**Regra de ouro:** se precisa do rosto exato de alguém ou logo específico, **sempre use image_reference**. Pure prompt gera rostos genéricos mesmo com descrições detalhadas.

---

## 2. Endpoints

| Operação | URL | Versão |
|---|---|---|
| Upload init_image | `https://cloud.leonardo.ai/api/rest/v1/init-image` | v1 |
| Gerar (nano-banana-2) | `https://cloud.leonardo.ai/api/rest/v2/generations` | v2 |
| Gerar (Phoenix/Kino/Flux/etc) | `https://cloud.leonardo.ai/api/rest/v1/generations` | v1 |
| Poll status | `https://cloud.leonardo.ai/api/rest/v1/generations/{id}` | v1 |

`LEONARDO_API_KEY` fica no `.env`. Header: `Authorization: Bearer {key}`, `Content-Type: application/json`.

---

## 3. Modelos disponíveis

| Modelo | ID / string | API | Uso principal |
|---|---|---|---|
| **Nano Banana 2** (default) | `nano-banana-2` | v2 | Carrosséis, cards, capas — suporte a image_reference |
| Phoenix 1.0 | `de7d3faf-762f-48e0-b3b7-9d0ac3a3fcf3` | v1 | Fotorrealismo flagship |
| Lucid Realism | `05ce0082-2d80-4a2d-8653-4d1c85e2418e` | v1 | Fotografia editorial |
| Flux Dev | `b2614463-296c-462a-9586-aafdb8f00e36` | v1 | Estado-da-arte realismo |
| Kino XL | `aa77f04e-3eec-4034-9c07-d0f619684628` | v1 | Cinematográfico |
| Lightning XL | `b24e16ff-06e3-43eb-8d33-4416c2d75876` | v1 | Rápido (teste) |
| Absolute Reality v1.6 | `e316348f-7773-490e-adcd-46757c738eb7` | v1 | Fotografia documental |

**Default NTICS:** `nano-banana-2`. É o único modelo que suporta `guidances.image_reference` no payload v2. Use os outros só quando não precisa de referência.

---

## 4. Dimensões por formato

⚠️ **Correção importante (abr/2026):** `nano-banana-2` NÃO aceita qualquer dimensão. Dimensões fora da lista abaixo retornam `VALIDATION_ERROR` (resposta como `list`, não `dict`). Leonardo v1 limita `height` ≤ 1536.

### Dimensões válidas testadas para nano-banana-2 (v2)

| Formato | Dimensões | Uso |
|---|---|---|
| **Quadrado 1:1** | `2048 × 2048` | Default seguro, posts genéricos |
| **Portrait 4:5** | `1856 × 2304` | Carrosséis IG feed, posts |
| **Portrait 5:4** | `1856 × 2304` (mesma) | Carrosséis |
| **Landscape ~16:9** | `2048 × 1152` ou `1792 × 1024` | Hero artigo, banner widescreen |
| **Landscape 3:2** | `1536 × 1024` | Inline artigo, foto editorial |
| **Landscape 5:4** | `2304 × 1856` | Artigo grande, capa horizontal |

❌ **Falham com VALIDATION_ERROR:** `1024×1024`, `1024×512`, `1472×832`, `1456×816`, `1664×928`, `1408×792`, `1024×576`, `1920×1080`, `2240×1280`. Em geral: a API rejeita combinações que não casam com seus presets internos.

⚠️ **Comportamento observado:** mesmo passando dim landscape válida (ex: `2048×1152`), a imagem final pode vir `2048×2048` quadrada. Confiar no `object-fit: cover` do CSS para crop. Se precisar exato 16:9, pode ser necessário pós-processar.

### Dimensões para v1 (Phoenix, Kino, Flux, Lucid)

| Formato | Dimensões | Uso |
|---|---|---|
| **Instagram feed 4:5** | `1152 × 1440` | Carrosséis (height ≤ 1536) |
| **Instagram Reels 9:16** | `768 × 1376` | Capas de Reels |
| **Artigo site / hero** | `1152 × 896` | Hero ntics.com.br |
| **Landscape banner** | `1536 × 640` ou `1280 × 720` | Free aspect (v1 mais flexível) |

---

## 5. Modo 1 — Pure prompt (sem referência)

Usado quando você só quer uma cena gerada por IA sem preservar nada específico.

### Payload mínimo (v2 / nano-banana-2)

```python
payload = {
    "model": "nano-banana-2",
    "parameters": {
        "prompt": "<prompt detalhado>",
        "width": 1856,
        "height": 2304,
        "quantity": 1,
        "prompt_enhance": "OFF",
    },
    "public": False
}
requests.post("https://cloud.leonardo.ai/api/rest/v2/generations", headers=HEADERS, json=payload)
```

### Payload v1 (Phoenix, Kino, etc)

```python
payload = {
    "prompt": "<prompt>",
    "negative_prompt": "<negative>",
    "modelId": "aa77f04e-3eec-4034-9c07-d0f619684628",  # Kino XL
    "width": 1152,
    "height": 1440,
    "num_images": 1,
    "public": False,
}
requests.post("https://cloud.leonardo.ai/api/rest/v1/generations", headers=HEADERS, json=payload)
```

### Quando vale a pena

- Imagens de cenário para artigos (campo de soja, sala de reunião, cidade sustentável)
- Ícones temáticos abstratos
- Cards com fundo colorido sólido + elementos decorativos

### Quando NÃO vale

- Quando precisa do rosto real do palestrante
- Quando precisa do logo exato de uma marca
- Quando precisa preservar uma foto específica do projeto

---

## 6. Modo 2 — Image Reference (com referência)

Preserva rosto, logo, ou foto real mantendo fidelidade visual. **Este é o modo mais usado na NTICS.**

### Fluxo em 2 passos

**Passo 1 — Upload da referência** (retorna `init_id`):

```python
import json, requests

# Requisitar URL pre-signed
r = requests.post(
    "https://cloud.leonardo.ai/api/rest/v1/init-image",
    headers=HEADERS,
    json={"extension": "jpg"}  # ou "png", "jpeg"
)
upload = r.json()["uploadInitImage"]
init_id = upload["id"]
fields = json.loads(upload["fields"])  # ← vem como STRING, precisa json.loads

# Upload do arquivo para S3
with open(photo_path, "rb") as f:
    requests.post(upload["url"], data=fields, files={"file": f})
```

⚠️ **Pegadinha 1:** `upload["fields"]` vem como **string JSON**, não dict. Sempre `json.loads()`.
⚠️ **Pegadinha 2:** upload para S3 usa `data=fields, files={"file": f}` — NÃO é multipart `files={k: (None, v), ...}`. Se usar multipart com form_data, quebra.

**Passo 2 — Geração com image_reference:**

```python
payload = {
    "model": "nano-banana-2",
    "parameters": {
        "prompt": "<prompt com 'uses the uploaded reference image'>",
        "width": 1856,
        "height": 2304,
        "quantity": 1,
        "prompt_enhance": "OFF",
        "guidances": {
            "image_reference": [
                {
                    "image": {"id": init_id, "type": "UPLOADED"},
                    "strength": "HIGH"
                }
            ]
        }
    },
    "public": False
}
```

### Estrutura correta de `guidances` (crítico)

```python
# ✅ CERTO — guidances é OBJETO com chave image_reference
"guidances": {
    "image_reference": [
        {"image": {"id": "...", "type": "UPLOADED"}, "strength": "HIGH"}
    ]
}

# ❌ ERRADO — array no topo (causa VALIDATION_ERROR)
"guidances": [
    {"type": "IMAGE_REFERENCE", "imageId": "...", "strength": 0.7}
]
```

### Múltiplas referências (pessoa + logo)

Suportado. Passa duas entradas no array:

```python
"guidances": {
    "image_reference": [
        {"image": {"id": person_id, "type": "UPLOADED"}, "strength": "HIGH"},
        {"image": {"id": logo_id,   "type": "UPLOADED"}, "strength": "HIGH"},
    ]
}
```

### Valores de `strength`

`nano-banana-2` usa strings: `"LOW"`, `"MEDIUM"`, `"HIGH"`.

| Valor | Fidelidade à referência | Uso |
|---|---|---|
| `"LOW"` | Baixa — modelo interpreta livremente | Inspiração solta |
| `"MEDIUM"` | Média — estilo preservado | Variações da mesma cena |
| `"HIGH"` | Alta — rosto/logo idênticos | Padrão NTICS (carrossel cliente, pílulas) |

Em alguns scripts antigos (pipeline híbrido) usa-se `0.70` (float) como init_strength — isso é o modo image-to-image, diferente do image_reference.

### Script de referência

`tools/media/generate_pilula_cover.py` — implementação canônica: upload de pessoa + logo, geração com 2 referências, prompt de zonas, 768×1376.

---

## 7. Modo 3 — Pipeline híbrido (Leonardo + Pillow)

Usado em carrosséis educativos para ter **controle total do texto** renderizado. Leonardo gera o fundo, Pillow desenha o texto por cima.

### Fluxo em 3 passos

1. **Leonardo gera fundo sem texto** — prompt inclui `NO_TEXT_SUFFIX` (ver seção 9)
2. **Pillow aplica película colorida** — gradiente, barra, overlay teal
3. **Pillow desenha texto** — fontes NTICS, cores da paleta, posicionamento por zona

### Quando usar híbrido em vez de Image Reference

- Quando o **texto precisa estar 100% correto** (Leonardo às vezes duplica palavras, omite acentos, erra formatação)
- Quando a **paleta e fontes precisam ser exatas** (brand compliance)
- Quando o **layout precisa ser pixel-perfect** (grid 2x2, dividers, etc)

### Scripts de referência

- `tools/content-gen/gerar_carrossel_educativo.py`
- `tools/content-gen/gerar_educativos_3semanas.py`
- `tools/content-gen/gerar_carrossel_noticias_v2.py`

---

## 8. Estrutura de prompts — padrões que funcionam

### 8.1 Zonas verticais (`From X to Y percent`)

Controle preciso de posicionamento. Formato testado em 100+ cards:

```
A social media card Instagram 4:5 format 1856x2304px.
From 0 to 55 percent: uses the uploaded reference image as the main photograph.
From 55 to 75 percent: smooth dark gradient overlay transitions from transparent to solid dark teal 005F73.
From 75 to 78 percent: small rounded green badge with white text 'PROJETO DE IMPACTO'.
From 78 to 92 percent: large bold white sans-serif headline: CINEMA GASTRONOMIA E ARTE EM UMA SÓ EXPERIÊNCIA.
From 92 to 98 percent: medium white body text: Festival itinerante que une cinema, culinária e arte.
At the very bottom edge flush with zero margin: thick horizontal gradient stripe bar from green 3DAA35 to teal 00A5B8 to pink D41A6A to orange E86428.
```

**Por que funciona:** modelo interpreta literalmente as porcentagens. Descrições vagas como "at the top" ou "below" dão resultados imprevisíveis.

### 8.2 Zonas nomeadas (alternativa com Zone 1/2/3...)

Usada nas capas de pílulas 9:16 (ESG no Agro). Mais legível:

```
--- COMPOSITION LAYOUT (vertical zones) ---

Zone 1 (top 15%): Background only — sky and field. No content. Safe zone for Instagram crop.
Zone 2 (15% to 28%): Logo placement area. Center the event logo with subtitle below.
Zone 3 (28% to 65%): Portrait zone. Person centered, surrounded by glowing neon light trails.
Zone 4 (65% to 85%): Typography zone. Bold uppercase text: "HEADLINE AQUI"
Zone 5 (bottom 15%): Background only — field ground.
```

### 8.3 Frase-chave para image_reference

**Sempre incluir** no prompt quando usar `image_reference`:

> `uses the uploaded reference image as the person` (pessoa)
> `uses the uploaded reference image as the main photograph` (cena)
> `use the person and logo exactly as shown — do not alter face, clothing, or logo design` (dupla referência)

Sem essa frase, modelo ignora a referência mesmo com `strength: HIGH`.

### 8.4 Tags de cor `[YELLOW]...[/YELLOW]`

Sintaxe proprietária testada no carrossel CineGastroArte. Leonardo renderiza as palavras marcadas em cor destacada:

```
LARGE BOLD HEADLINE: white uppercase sans-serif, words marked [YELLOW]...[/YELLOW] render in bright yellow color:
[YELLOW]CINEMA[/YELLOW] GASTRONOMIA E ARTE EM UMA SÓ EXPERIÊNCIA.
```

Funciona bem para destacar números, marcas ou palavras-chave.

### 8.5 NO_TEXT_SUFFIX (para fundos sem texto)

Quando quer que Leonardo gere apenas a foto (pipeline híbrido):

```
<prompt da cena> Important: absolutely NO text, NO words, NO letters, NO numbers, NO watermarks anywhere on the image.
```

### 8.6 Hex codes no prompt

**Usar hex literal** em vez de nomes de cor. Testado:

```
✅ "solid dark teal 005F73 background"
✅ "yellow-gold F5B800 tones"
❌ "dark teal background"  ← Leonardo interpreta aproximadamente
```

### 8.7 Blacklist explícita

Quando Leonardo insiste em adicionar elementos indesejados:

```
Do NOT render any percentage signs, numbers, rulers or layout markers anywhere on the card.
No white borders, no padding, no layout markers visible.
Pure photograph, no graphics.
```

---

## 9. Parâmetros críticos

| Parâmetro | Valor NTICS | Impacto |
|---|---|---|
| `prompt_enhance` | **`"OFF"`** sempre | ON reescreve o prompt e destrói estrutura de zonas |
| `strength` (image_reference) | `"HIGH"` | Preserva rosto/logo fielmente |
| `quantity` | `1` | 1 imagem por geração (mais previsível) |
| `public` | `False` | Evita indexação pública |
| `negative_prompt` | (só v1) | `"cartoon, illustration, painting, drawing, animation, CGI, render, unrealistic, blurry, low quality, watermark, text, logo, banner, distorted faces, extra limbs, bad anatomy"` |

---

## 10. Polling e extração de `generationId`

Leonardo responde com estruturas **diferentes** dependendo do modelo/versão:

```python
def extract_gen_id(response_json):
    # 1. v1 clássico (Kino, Phoenix, etc)
    if "sdGenerationJob" in response_json:
        return response_json["sdGenerationJob"]["generationId"]

    # 2. v2 nano-banana-2 (chave "generate")
    if "generate" in response_json:
        return response_json["generate"]["generationId"]

    # 3. Direto
    if "generationId" in response_json:
        return response_json["generationId"]

    # 4. Fallback: iterar sobre values
    for v in response_json.values():
        if isinstance(v, dict):
            if v.get("generationId"):
                return v["generationId"]
            if v.get("id"):
                return v["id"]

    raise RuntimeError(f"generationId não encontrado: {response_json}")
```

### Polling

```python
def poll_generation(gen_id, timeout=180):
    time.sleep(10)  # dar tempo para modelo inicializar
    elapsed = 10
    while elapsed < timeout:
        r = requests.get(
            f"https://cloud.leonardo.ai/api/rest/v1/generations/{gen_id}",
            headers=HEADERS
        )
        job = r.json().get("generations_by_pk", {})
        status = job.get("status", "PENDING")  # PENDING | COMPLETE | FAILED

        if status == "COMPLETE":
            return job["generated_images"][0]["url"]
        if status == "FAILED":
            raise RuntimeError(f"Geração falhou: {gen_id}")

        time.sleep(10)
        elapsed += 10
    raise TimeoutError(f"Timeout após {timeout}s")
```

**Tempos observados:** 20–60 segundos por imagem com nano-banana-2. Se passar de 120s, provavelmente há problema (fila ou erro silencioso).

---

## 11. Aprendizados — erros conhecidos e mitigações

Esta seção é a mais importante. **Sempre consultar antes de gerar.**

### 11.1 Falhas na API

| Sintoma | Causa | Solução |
|---|---|---|
| `Validation failed` no v2 | `guidances` como array em vez de objeto `{"image_reference": [...]}` | Usar estrutura objeto aninhado |
| `Unexpected variable guidanceScale` | `guidanceScale` não aceito em nano-banana-2 | Remover do payload v2 |
| `height must be between 32 and 1536` | Modelo v1 não aceita altura > 1536 | Usar v2 (nano-banana-2) ou reduzir dimensões |
| `'str' object has no attribute 'items'` | `upload["fields"]` é string JSON | `json.loads(upload["fields"])` |
| `'list' object has no attribute 'get'` | Resposta v2 vem como lista de erro | Imprimir `resp.text` e tratar |

### 11.2 `init_image` vs `image_reference` (erro comum)

| | `init_image_id` (v1) | `image_reference` (v2) |
|---|---|---|
| O que faz | Image-to-image: começa da foto + adiciona ruído | Guia visual: preserva rosto/estilo |
| Resultado | **Copia o estilo da foto** (se foto é P&B, gera P&B) | Mantém o rosto mas segue prompt |
| Quando usar | Híbrido (fundo Leonardo → adicionar texto) | Rosto exato de palestrante |
| Strength | Float 0.0–1.0 | String "LOW"/"MEDIUM"/"HIGH" |

**Erro que cometi uma vez:** usei `init_image_id` com `init_strength: 0.38` tentando preservar rosto — resultado: Leonardo replicou a foto original em preto-e-branco, ignorou o prompt de composição. Para rosto exato, **sempre** use `guidances.image_reference`.

### 11.3 Problemas de texto renderizado

| Erro | Exemplo | Causa | Mitigação |
|---|---|---|---|
| Palavra duplicada | `"NO NO MATO GROSSO"` | Prompt longo + tokens repetidos | Encurtar headline, remover redundâncias |
| Acento faltando | `"EDUCACAO"` virou `"EDUCAÇÃO"` mal-renderizado | Modelo processa mal acentos em uppercase | Forçar acentos no prompt com UTF-8 explícito |
| Formato numérico | `"20 porcento"` virou texto estranho | Modelo confunde extenso | Usar `%` ou `"20 percent"` em inglês |
| Palavra cortada | `"COLHEITADEIR"` | Headline muito longa na zona | Reduzir fonte ou quebrar em 2 linhas |
| Trecho duplicado | `"COM A AGENDA COM A AGENDA 2030"` | Headline com highlight ambíguo | Reformular sintaxe |

**Regra:** acentos PT-BR devem estar no prompt. Se passar `"EDUCACAO"` sem cedilha, modelo não vai adicionar sozinho.

### 11.4 Elementos visuais indesejados

| Erro | Mitigação |
|---|---|
| Bordas brancas/padding na imagem | `"edge to edge, no borders, no padding, fills entire frame"` |
| % signs aparecendo como decoração | `"Do NOT render any percentage signs or numbers"` |
| Layout markers (réguas, gridlines) | `"no layout markers visible"` |
| Texto em inglês quando pediu PT | Incluir texto PT literal no prompt com aspas |
| Rosto distorcido / extra limbs | `negative_prompt: "distorted faces, extra limbs, bad anatomy"` |

### 11.5 Regras editoriais NTICS (conteúdo dos prompts)

De `feedback_editorial_tone.md` e `feedback_carrossel_revisao_visual.md`:

- **Travessão (—)** → substituir por vírgula ou "mas" (modelo renderiza ruim)
- **Decimais** → usar ponto: `"11.4M"`, `"9.32"` (vírgula vira confuso)
- **Ponto final** em `texto` e `frase` → REMOVER (fica estranho visualmente)
- **Palavras inglesas isoladas** → traduzir: `"performance"` → `"desempenho"`, `"feedback"` → `"retorno"`
- **Capa sem celebração** → máximo 1-2 pessoas, sem grupo celebrando
- **Sem monitores/telas/TVs** nas cenas (fica artificial)
- **Sem sigla CSR** → usar "Responsabilidade Social"
- **Nome do projeto em destaque** na capa do carrossel cliente
- **CTA fonte ≥ 130px** para legibilidade mobile
- **Logo inferior esquerdo** (padrão cliente Sylvamo, etc)

### 11.6 Polling / performance

| Sintoma | Solução |
|---|---|
| Polling imediato retorna PENDING por muito tempo | Sleep inicial 10–15s antes do primeiro poll |
| Timeout 180s insuficiente | Aumentar para 240s em horário de pico |
| Várias gerações em paralelo falhando | Serializar — rodar uma por vez |
| Upload S3 intermitente | Retry com backoff |

---

## 12. Checklist de revisão visual (BLOQUEANTE)

Antes de entregar qualquer imagem Leonardo ao usuário, percorrer este checklist. Se qualquer item falhar → regenerar ou corrigir.

**Texto:**
- [ ] Todas as palavras corretas (sem duplicação, sem corte)
- [ ] Acentos PT-BR presentes (`Ã`, `Ç`, `É`, `Á`)
- [ ] Números em formato correto (ponto decimal, `%` não "porcento")
- [ ] Sem ponto final em headlines / títulos
- [ ] Sem palavras inglesas onde deveria ser português

**Composição:**
- [ ] Rosto não distorcido (olhos simétricos, sem extras)
- [ ] Logo legível e não distorcido
- [ ] Zonas respeitadas (logo em cima, texto no lugar certo)
- [ ] Sem bordas/padding indesejados
- [ ] Sem elementos decorativos fantasmas (% signs, rulers)

**Consistência (carrossel):**
- [ ] Mesma cor de gradiente em todos os cards
- [ ] Mesma paleta de badges/destaques
- [ ] Barra gradiente no rodapé em todos
- [ ] Fotos do mesmo projeto (não misturar eventos)

**Identidade visual (cliente/NTICS):**
- [ ] Paleta correta do cliente (hex conferido com brand book)
- [ ] Logo posicionamento padrão (inferior esquerdo para Sylvamo, etc)
- [ ] Fonte adequada ao brand

Qualquer item ❌ → regenerar o card específico com prompt ajustado.

---

## 13. Scripts de referência por caso de uso

| Caso de uso | Script | Modo |
|---|---|---|
| **Pílulas com rosto exato + logo** (capa de Reel 9:16) | `tools/media/generate_pilula_cover.py` | image_reference (2x) |
| **Carrossel de projeto ativo cliente** (8 cards) | `.tmp/generate_carousel_pec.py`, `.tmp/regenerate_cards_v3.py` | image_reference + Pillow (CTA) |
| **Carrossel educativo NTICS semanal** (8 cards) | `tools/content-gen/gerar_carrossel_educativo.py` | Pipeline híbrido |
| **Carrossel de notícias ESG** (8 cards) | `tools/content-gen/gerar_carrossel_noticias_v2.py` | Pure prompt + Pillow |
| **Imagem hero de artigo site** | `tools/content-gen/gerar_artigo_site.py` | Pure prompt |
| **Geração em batch (notícias)** | `tools/media/generate_images_leonardo.py` | Pure prompt |
| **Carrossel de case (exemplo)** | `.tmp/marketing/carrosseis/cinegastroarte/gerar_cards.py` | image_reference + [YELLOW] tags |

---

## 14. Exemplos práticos completos

### 14.1 Capa de Reel 9:16 com rosto + logo

```python
# Upload pessoa + logo
person_id = upload_init_image("foto_palestrante.jpg")
logo_id   = upload_init_image("logo_evento.png")

prompt = f"""\
Reference images provided: use the person and logo exactly as shown — do not alter face, clothing, or logo design.
Shallow depth of field soybean crops field background throughout.

Zone 1 (top 15%): Background only — sky and field.
Zone 2 (15% to 28%): Logo placement area. Center the event logo with subtitle below.
Zone 3 (28% to 65%): Portrait zone. Person centered, surrounded by dynamic glowing neon light trails forming circular motion around them — green and yellow energy streaks, luminous particles, futuristic energy branding style. Floating thematic icons: {icons_tema}.
Zone 4 (65% to 85%): Typography zone. Bold uppercase modern sans-serif text: "{headline}". Clean layout, centered.
Zone 5 (bottom 15%): Background only — field ground.

High-end corporate advertising look, cinematic lighting, sharp focus, vibrant colors, modern branding aesthetic."""

payload = {
    "model": "nano-banana-2",
    "parameters": {
        "prompt": prompt,
        "width": 768,
        "height": 1376,
        "quantity": 1,
        "prompt_enhance": "OFF",
        "guidances": {
            "image_reference": [
                {"image": {"id": person_id, "type": "UPLOADED"}, "strength": "HIGH"},
                {"image": {"id": logo_id,   "type": "UPLOADED"}, "strength": "HIGH"},
            ]
        }
    },
    "public": False
}
```

**Ícones temáticos por tipo de pílula** (mudar por cada geração):

| Tema | Ícones |
|---|---|
| Saúde mental | `brain, heartbeat, lightbulb, smiley face, meditation` |
| Agricultura precisão | `tractor, GPS map, satellite, gear, efficiency gauge` |
| IA / produtividade | `AI chip, satellite, combine harvester, rising bar chart` |
| Governança | `balance scale, contract, shield, family tree` |
| Sucessão / carreira | `ladder, handshake, growth arrow, wrench` |
| Segurança trabalho | `hard hat, warning sign, focused eye, medical cross` |

### 14.2 Card de carrossel cliente com foto do projeto

```python
photo_id = upload_init_image("projeto_cena.jpg")

prompt = """\
Social media carousel card Instagram 4:5.
UPPER HALF of the card: full-bleed photograph — uses the uploaded reference image as the main visual. Edge to edge, no text, no watermarks.
SMOOTH GRADIENT TRANSITION between upper and lower halves, blending the photo into solid dark teal 005F73 below.
LOWER HALF of the card: solid dark teal background.
POSITIONED near the top of the lower half: small rounded pill badge with white bold uppercase text 'PROJETO DE IMPACTO'.
LARGE BOLD HEADLINE below the badge: white uppercase sans-serif, words marked [YELLOW]...[/YELLOW] render in bright yellow:
[YELLOW]CINEMA[/YELLOW] GASTRONOMIA E ARTE EM UMA SÓ EXPERIÊNCIA.
BODY TEXT below: smaller regular white sans-serif: 'Festival itinerante que une cinema, culinária e arte em experiência sinestésica única'.
BOTTOM EDGE flush: thick horizontal gradient stripe from green 3DAA35 to teal 00A5B8 to pink D41A6A to orange E86428.
Professional editorial design, clean, no borders, no padding, no layout markers visible.
"""
```

### 14.3 Imagem hero de artigo (pure prompt)

```python
prompt = """\
Candid documentary photograph of a Brazilian corporate executive and a community leader in an informal meeting outdoors in a urban park in Brazil, reviewing a social impact project report together. Both engaged, genuine expressions. Natural golden hour lighting. Shot with Canon EOS R5, 35mm f1.8, editorial documentary photography, ultra realistic. No text no watermarks no logos.
"""

payload = {
    "model": "nano-banana-2",
    "parameters": {
        "prompt": prompt,
        "width": 1152,
        "height": 896,
        "quantity": 1,
        "prompt_enhance": "OFF",
    },
    "public": False
}
```

---

## 15. FAQ / Troubleshooting

**P: O rosto saiu genérico mesmo com image_reference. O que fazer?**
R: Verificar se o prompt inclui literalmente `"uses the uploaded reference image as the person"`. Sem essa frase, modelo ignora a referência mesmo com `strength: HIGH`.

**P: A imagem saiu em preto-e-branco ou com o estilo errado.**
R: Você provavelmente usou `init_image_id` (v1, image-to-image) em vez de `guidances.image_reference` (v2). `init_image_id` herda o estilo da foto original. Para preservar **só o rosto**, use `image_reference`.

**P: O texto está com palavras duplicadas.**
R: Headline longa demais. Reduza para ≤ 8 palavras por linha. Reformule para eliminar repetições como "COM A AGENDA COM A AGENDA".

**P: Acentos PT-BR sumiram do texto.**
R: Garanta que o prompt passa os acentos literais (`"SAÚDE"`, não `"SAUDE"`). Se está chamando pelo terminal Windows, configure encoding UTF-8: `sys.stdout.reconfigure(encoding="utf-8", errors="replace")`.

**P: O Leonardo está ignorando minha estrutura de zonas.**
R: Confira se `prompt_enhance` está `"OFF"`. Se estiver `"ON"`, Leonardo reescreve o prompt e destrói a estrutura.

**P: `VALIDATION_ERROR` no v2.**
R: Provavelmente `guidances` está como array em vez de objeto. Formato correto: `"guidances": {"image_reference": [{...}]}`.

**P: Posso usar 2 referências (pessoa + logo)?**
R: Sim. Array `image_reference` aceita múltiplas entradas. Testado e funciona com 2. Mais que isso não testei.

**P: Qual dimensão para Reels / Stories?**
R: `768 × 1376` (aproximadamente 9:16). Testado e aprovado.

**P: Qual dimensão para feed 4:5?**
R: `1856 × 2304` com nano-banana-2 (v2). Com modelos v1 (Kino, Phoenix), máximo `1152 × 1440` por limite de altura 1536.

**P: Quanto custa uma geração?**
R: Nano-banana-2 ~ $0.013–0.018 por imagem (observado no response `cost.amount`). ~55–75 imagens por $1.

---

## 16. Atualização deste documento

**Sempre que descobrir um novo erro ou padrão que funciona, adicionar aqui.** Esta base cresce por aprendizado — não deixe conhecimento em comentários de código ou em memórias que ninguém vai ler.

**Última atualização:** 2026-04-14 — Nano-banana-2 aceita `R$` literal no prompt sem `VALIDATION_ERROR`. Sanitização agressiva (`R$` → `R`) era cautela antiga desnecessária. Render fiel inclusive com `R$ 25 milhões` em headline. Restrição antiga removida do `_sanitize_prompt` em `tools/content-gen/gerar_carrossel_noticias_v2.py`.

**2026-05-14 — ID do nano-banana-2 mudou. String `"nano-banana-2"` no campo `model` do payload v2 retorna `remote-schema-error` ("Missing data field"). Usar UUID: `7418e71f-4133-4e1b-9895-bee19f48f2ce`. Consultar `GET /v2/models` para IDs atuais dos modelos. Outros modelos v2 disponíveis: Nano Banana (1°) `4a008a65`, Nano Banana Pro `7c02ef35`, FLUX.1 Kontext `28aeddf8`, GPT Image 2 `135b2740`. A v2 gerou VALIDATION_ERROR em todas as gerações de teste — possível restrição de conta. Fallback validado: pipeline Pillow (foto + composição manual). Exemplo: `tmp/marketing/carrosseis/teatro-ods-repsol/gerar_cards_pillow.py`.**

**2026-04-10** — pílulas ESG no Agro SB (image_reference dupla pessoa+logo, 9:16 768×1376, zonas verticais com texto renderizado no prompt).
