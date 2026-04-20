# Leonardo AI, Guia Essencial NTICS

Referência rápida para payloads, dimensões e checklist visual. Detalhes, erros conhecidos, FAQ e exemplos completos em [leonardo_ai_cookbook.md](leonardo_ai_cookbook.md).

---

## 1. Modos de geração

| Modo | Quando usar | Exemplo |
|---|---|---|
| **Pure prompt** (sem referência) | Cenário genérico, sem rosto/logo específicos | Artigo site, carrossel notícias |
| **Image Reference** (v2, `guidances`) | Preservar rosto real, logo, foto de projeto | Carrossel cliente, pílulas, case |
| **Pipeline híbrido** (Leonardo + Pillow) | Texto 100% correto, brand compliance | Carrossel educativo NTICS |

Regra: rosto ou logo específicos → sempre image_reference. Pure prompt gera rostos genéricos mesmo com descrição detalhada.

---

## 2. Endpoints

| Operação | URL | Versão |
|---|---|---|
| Upload init_image | `https://cloud.leonardo.ai/api/rest/v1/init-image` | v1 |
| Gerar (nano-banana-2) | `https://cloud.leonardo.ai/api/rest/v2/generations` | v2 |
| Gerar (Phoenix/Kino/Flux) | `https://cloud.leonardo.ai/api/rest/v1/generations` | v1 |
| Poll status | `https://cloud.leonardo.ai/api/rest/v1/generations/{id}` | v1 |

Header: `Authorization: Bearer {LEONARDO_API_KEY}`, `Content-Type: application/json`.

---

## 3. Modelos

| Modelo | ID | API | Uso |
|---|---|---|---|
| **Nano Banana 2** (default) | `nano-banana-2` | v2 | Carrosséis, capas, único com image_reference |
| Phoenix 1.0 | `de7d3faf-762f-48e0-b3b7-9d0ac3a3fcf3` | v1 | Fotorrealismo flagship |
| Lucid Realism | `05ce0082-2d80-4a2d-8653-4d1c85e2418e` | v1 | Fotografia editorial |
| Flux Dev | `b2614463-296c-462a-9586-aafdb8f00e36` | v1 | Estado-da-arte |
| Kino XL | `aa77f04e-3eec-4034-9c07-d0f619684628` | v1 | Cinematográfico |

Default NTICS: `nano-banana-2`.

---

## 4. Dimensões válidas

### nano-banana-2 (v2), dimensões fora dessa lista retornam `VALIDATION_ERROR`

| Formato | Dimensões | Uso |
|---|---|---|
| Quadrado 1:1 | `2048 × 2048` | Default seguro |
| Portrait 4:5 | `1856 × 2304` | Carrosséis IG feed |
| Landscape ~16:9 | `2048 × 1152` ou `1792 × 1024` | Hero, banner |
| Landscape 3:2 | `1536 × 1024` | Inline artigo |
| Landscape 5:4 | `2304 × 1856` | Capa horizontal |

### v1 (Phoenix, Kino, Flux, Lucid), height ≤ 1536

| Formato | Dimensões | Uso |
|---|---|---|
| IG feed 4:5 | `1152 × 1440` | Carrosséis |
| IG Reels 9:16 | `768 × 1376` | Capas Reels |
| Artigo hero | `1152 × 896` | ntics.com.br |

Falhas conhecidas e detalhes: [cookbook §4](leonardo_ai_cookbook.md#4-dimensões-por-formato).

---

## 5. Payload mínimo por modo

### Pure prompt (v2)

```python
payload = {
    "model": "nano-banana-2",
    "parameters": {
        "prompt": "<prompt>",
        "width": 1856, "height": 2304,
        "quantity": 1,
        "prompt_enhance": "OFF",
    },
    "public": False,
}
requests.post("https://cloud.leonardo.ai/api/rest/v2/generations", headers=HEADERS, json=payload)
```

### Image Reference (v2)

```python
# 1. Upload
r = requests.post("https://cloud.leonardo.ai/api/rest/v1/init-image", headers=HEADERS,
                  json={"extension": "jpg"})
upload = r.json()["uploadInitImage"]
init_id = upload["id"]
fields = json.loads(upload["fields"])  # fields vem como string JSON, sempre json.loads
with open(photo_path, "rb") as f:
    requests.post(upload["url"], data=fields, files={"file": f})

# 2. Gerar
payload = {
    "model": "nano-banana-2",
    "parameters": {
        "prompt": "<prompt com 'uses the uploaded reference image'>",
        "width": 1856, "height": 2304,
        "quantity": 1, "prompt_enhance": "OFF",
        "guidances": {
            "image_reference": [
                {"image": {"id": init_id, "type": "UPLOADED"}, "strength": "HIGH"}
            ]
        },
    },
    "public": False,
}
```

Estrutura correta de `guidances`: objeto com chave `image_reference`, não array no topo. Valores de `strength`: `"LOW"`, `"MEDIUM"`, `"HIGH"`. Default NTICS: `"HIGH"`.

Pegadinhas, múltiplas referências, polling, extração de `generationId`: [cookbook §6-10](leonardo_ai_cookbook.md#6-modo-2--image-reference-com-referência).

---

## 6. Parâmetros críticos

| Parâmetro | Valor NTICS | Impacto |
|---|---|---|
| `prompt_enhance` | `"OFF"` sempre | `ON` reescreve o prompt e destrói estrutura de zonas |
| `strength` (image_reference) | `"HIGH"` | Preserva rosto/logo fielmente |
| `quantity` | `1` | 1 imagem por geração, mais previsível |
| `public` | `False` | Evita indexação pública |
| `negative_prompt` (só v1) | `"cartoon, illustration, painting, drawing, animation, CGI, render, unrealistic, blurry, low quality, watermark, text, logo, banner, distorted faces, extra limbs, bad anatomy"` | |

---

## 7. Checklist de revisão visual (bloqueante)

Antes de entregar qualquer imagem, percorrer. Item falhou → regenerar.

**Texto:**
- [ ] Palavras corretas (sem duplicação, sem corte)
- [ ] Acentos PT-BR presentes (`Ã`, `Ç`, `É`, `Á`)
- [ ] Números com ponto decimal, `%` em vez de "porcento"
- [ ] Sem ponto final em headline
- [ ] Sem palavras inglesas onde deveria ser PT

**Composição:**
- [ ] Rosto não distorcido
- [ ] Logo legível
- [ ] Zonas respeitadas
- [ ] Sem bordas/padding indesejados
- [ ] Sem elementos fantasmas (% signs, réguas)

**Consistência (carrossel):**
- [ ] Mesmo gradiente em todos os cards
- [ ] Mesma paleta de badges
- [ ] Barra gradiente no rodapé em todos
- [ ] Fotos do mesmo projeto

**Identidade visual:**
- [ ] Paleta correta (hex conferido com brand book)
- [ ] Logo no lugar padrão (inferior esquerdo para Sylvamo, etc)
- [ ] Fonte adequada ao brand

---

## 8. Quando consultar o cookbook

Abra [leonardo_ai_cookbook.md](leonardo_ai_cookbook.md) quando:

- Surgir erro de API (`VALIDATION_ERROR`, payload rejeitado, timeout)
- Dúvida sobre estrutura de zonas, `[YELLOW]` tags, `NO_TEXT_SUFFIX`
- Resultado visual errado (rosto genérico, palavras duplicadas, acentos faltando)
- Implementar caso de uso novo (usar um exemplo do §14 como base)
- Debug de polling ou extração de `generationId`

Se descobrir novo erro ou padrão que funciona, registrar no cookbook §11.
