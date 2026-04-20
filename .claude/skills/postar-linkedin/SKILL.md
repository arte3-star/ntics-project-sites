---
name: postar-linkedin
description: "Publica posts na página da NTICS Projetos no LinkedIn (texto, imagem, vídeo, PDF/carrossel documento) via Playwright + Chrome CDP. Aceita comentário fixo opcional com link do artigo/fontes."
user-invocable: true
---

Publica posts na página da empresa NTICS Projetos no LinkedIn usando automação do browser. Requer Super Admin na página e arquivos já prontos (PDF, imagem, vídeo).

## Pré-requisitos

- Chrome aberto com `--remote-debugging-port=9222` (ver skill `/editar-site-web`)
- Usuário logado como Super Admin da página NTICS (Company ID: **35558673**)
- Assets já prontos (PDF, JPG, MP4) — esta skill **não gera conteúdo**, só publica

## Entrada esperada

O usuário deve fornecer:
1. **Caption** (texto do post) — obrigatório
2. **Tipo de mídia** — `documento` (PDF), `imagem` (JPG/PNG), `video` (MP4), ou `texto` (sem anexo)
3. **Caminho do arquivo** — se for mídia
4. **Título do documento** — se for PDF, máximo 56 caracteres
5. **Comentário fixado** — opcional, geralmente link do artigo + fontes

Se faltar algo, pergunte antes de executar.

## Passo 1 — Conectar ao Chrome e abrir modal de post

```python
import asyncio
from playwright.async_api import async_playwright

async def open_post_modal():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp("http://localhost:9222", timeout=15000)
        context = browser.contexts[0]
        page = context.pages[-1]

        # URL que abre direto o modal "Iniciar publicação" como organização
        await page.goto(
            "https://www.linkedin.com/company/35558673/admin/page-posts/published"
            "?share=true&shareActorType=ORGANIZATION"
            "&shareOrganizationActor=urn%3Ali%3Afsd_company%3A35558673",
            timeout=30000
        )
        await page.wait_for_load_state("domcontentloaded")
        await asyncio.sleep(5)
        return page
```

## Passo 2 — Preencher caption

```python
editor = page.locator('[role="textbox"]').first
await editor.click()
await editor.fill(CAPTION)
await asyncio.sleep(2)
```

## Passo 3 — Anexar mídia (conforme tipo)

Barra de ícones na parte inferior do modal. Seletores por `aria-label`:

| Tipo | aria-label do botão | Aceita |
|------|-------------------|--------|
| Imagem/Vídeo | `"Adicionar mídia"` | JPG, PNG, MP4 |
| Documento | `"Adicione um documento"` | PDF, DOC, DOCX, PPT, PPTX |
| Enquete | `"Crie uma enquete"` | — |
| Evento | `"Crie um evento"` | — |

### Documento (PDF/carrossel)

```python
doc_btn = page.locator('button[aria-label="Adicione um documento"]').first
await doc_btn.click()
await asyncio.sleep(3)

# Upload via input file (oculto pelo LinkedIn)
file_input = page.locator('input[type="file"]').last
await file_input.set_input_files(PDF_PATH)
await asyncio.sleep(5)

# Preencher título (MÁX 56 chars!)
title_input = page.locator('input[id*="title-input"]').first
await title_input.fill(DOC_TITLE)  # <= 56 chars

# Clicar "Concluído"
done_btn = page.get_by_text("Concluído", exact=True).first
await done_btn.click()
await asyncio.sleep(5)
```

### Imagem/Vídeo

```python
media_btn = page.locator('button[aria-label="Adicionar mídia"]').first
await media_btn.click()
await asyncio.sleep(2)

# Upload
file_input = page.locator('input[type="file"]').last
await file_input.set_input_files(IMAGE_PATH)
await asyncio.sleep(5)

# Avançar
next_btn = page.get_by_text("Avançar", exact=True).first
await next_btn.click()
await asyncio.sleep(3)
```

## Passo 4 — Publicar

O botão "Publicar" aparece duas vezes na DOM (span e button). Use o primeiro button visível:

```python
pub_btns = await page.evaluate("""() => {
    return Array.from(document.querySelectorAll('button')).filter(el =>
        el.textContent.trim() === 'Publicar'
    ).map(el => {
        const r = el.getBoundingClientRect();
        return {x: Math.round(r.x), y: Math.round(r.y), w: Math.round(r.width), visible: r.width > 0};
    }).filter(e => e.visible);
}""")
if pub_btns:
    await page.mouse.click(pub_btns[0]['x'] + pub_btns[0]['w']//2, pub_btns[0]['y'] + 15)
    await asyncio.sleep(8)
```

Confirmação de sucesso: toast verde "Publicação bem-sucedida" no canto inferior esquerdo.

## Passo 5 — Comentário fixado (opcional)

Quando houver artigo do blog NTICS + fontes para linkar.

```python
# Volta para lista de posts
await page.goto("https://www.linkedin.com/company/35558673/admin/page-posts/published", timeout=30000)
await page.wait_for_load_state("domcontentloaded")
await asyncio.sleep(5)

# Clica "Comentar" no primeiro post (o mais recente)
comment_btn = page.locator('button[aria-label="Comentar"]').first
await comment_btn.scroll_into_view_if_needed()
await comment_btn.click()
await asyncio.sleep(3)

# Preenche o campo de comentário
comment_box = page.locator('.comments-comment-box__form [role="textbox"]').first
await comment_box.click()
await comment_box.fill(COMMENT_TEXT)
await asyncio.sleep(2)

# Verifica que o submit ficou habilitado (não scroll antes disso!)
submit = page.locator('button.comments-comment-box__submit-button--cr').first
if not await submit.is_disabled():
    await submit.click()
    await asyncio.sleep(5)
```

**Cuidado:** se scrollar ou clicar fora do campo antes de enviar, o texto **é perdido** e o botão volta a ficar desabilitado. Digite e envie sem interrupções.

## Passo 6 — Verificação

Sempre confirmar publicação com screenshot:

```python
await page.screenshot(path=r"C:\Users\lucas\AppData\Local\Temp\li-posted.png", timeout=60000)
```

Leia o screenshot para confirmar:
- Toast "Publicação bem-sucedida" apareceu
- Post aparece na lista com imagem/preview correto
- Comentário aparece abaixo do post com preview do link

## Limites do LinkedIn

| Campo | Limite |
|-------|--------|
| Caption | 3.000 chars |
| Título do documento | **56 chars** (trunca visualmente) |
| Comentário | 1.250 chars (mas aceita até ~3.000) |
| PDF | Máx ~100 MB, recomendado <10 MB |
| Imagem | JPG/PNG até 5 MB |
| Vídeo | MP4 até 5 GB, 10 min máx |

## Contexto NTICS

- **Company ID:** 35558673
- **Slug:** nticsprojetos
- **Blog:** https://ntics.com.br/artigos/
- **Hashtags recorrentes:** #ESG #Sustentabilidade #ResponsabilidadeSocial #ImpactoSocial #NTICSProjetos #ODS
- **Cadência editorial:** 1 vídeo + 3 carrosseis por semana (ver `feedback_editorial_tone.md`)

## Observações aprendidas

- O LinkedIn bloqueia `PATCH`/`PUT` direto na Voyager API para updates — só a UI funciona
- Título do documento >56 chars trunca e gera warning visual — sempre validar comprimento
- Scroll antes de enviar comentário apaga o texto — preencher e enviar sem interrupções
- O botão "Publicar" aparece duplicado na DOM; use coordenadas e clique no primeiro visível
- PDF gerado com Pillow a partir de JPGs funciona perfeitamente como carrossel-documento
- Após publicar, o LinkedIn gera automaticamente preview de qualquer URL no comentário
