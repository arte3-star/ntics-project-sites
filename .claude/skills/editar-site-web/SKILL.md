---
name: editar-site-web
description: "Quando precisar editar, preencher, clicar ou automatizar qualquer coisa dentro de um site (autenticado ou não), usa Playwright + Chrome CDP para controlar o browser real do usuário."
user-invocable: true
---

Quando o usuário pedir para editar, preencher ou interagir com qualquer site, use **Playwright via CDP** para controlar o Chrome real dele. Isso permite operar dentro de sessões já autenticadas (LinkedIn, ClickUp, Google, etc.) sem precisar de credenciais.

## Quando usar esta skill

- "Edita o perfil da empresa no LinkedIn"
- "Preenche esse formulário pra mim"
- "Clica em tal botão no site X"
- "Extrai dados dessa página que precisa de login"
- Qualquer site que exige autenticação ou interação manual

## Ferramentas

- **Python + Playwright** — já instalado na máquina
- **Chrome DevTools Protocol (CDP)** — protocolo nativo do Chrome para controle externo
- **Chrome do usuário** — com sessão e cookies reais

## Passo 1 — Abrir Chrome com porta de controle

Execute no terminal. **Não fecha as abas existentes** — abre uma janela separada:

```bash
"/c/Program Files/Google/Chrome/Application/chrome.exe" \
  --remote-debugging-port=9222 \
  --user-data-dir="C:\\Users\\lucas\\AppData\\Local\\Temp\\browser-session" \
  --no-first-run \
  "https://SITE_DESEJADO" &
```

> Se a porta 9222 já estiver em uso (de sessão anterior), use 9223, 9224 etc.

## Passo 2 — Conectar ao Chrome via Playwright

```python
import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp("http://localhost:9222")
        context = browser.contexts[0]
        page = context.pages[0]
        
        # Confirma conexão
        url = await page.evaluate('window.location.href')
        print(f"Conectado: {url}")
        
        # Seu código de automação aqui...

asyncio.run(main())
```

## Passo 3 — Padrões de automação

### Navegar para uma página
```python
await page.goto("https://exemplo.com/pagina")
await page.wait_for_load_state("domcontentloaded")
await asyncio.sleep(3)  # aguarda JS carregar
```

### Ver o que está na tela (screenshot)
```python
await page.screenshot(path=r"C:\Users\lucas\AppData\Local\Temp\tela.png")
# Leia com Read tool para "ver" e decidir o próximo passo
```

### Encontrar e clicar em elementos
```python
# Por texto visível
await page.get_by_text("Salvar", exact=False).click()

# Por papel/função
await page.get_by_role("button", name="Confirmar").click()

# Por coordenadas (último recurso, quando seletores falham)
await page.mouse.click(x, y)
```

### Preencher campos de texto
```python
await page.fill('input[name="email"]', "valor")
await page.fill('textarea#descricao', "texto longo aqui")
```

### Executar JavaScript na página (poderoso para APIs internas)
```python
result = await page.evaluate('''
    async () => {
        const res = await fetch('/api/endpoint', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({campo: 'valor'})
        });
        return {status: res.status, data: await res.json()};
    }
''')
print(result)
```

### Listar todos os elementos clicáveis (para entender a página)
```python
elements = await page.evaluate('''
    () => Array.from(document.querySelectorAll("a, button"))
        .map(el => {
            const r = el.getBoundingClientRect();
            return {
                tag: el.tagName,
                text: el.textContent.trim().substring(0, 60),
                href: el.href || "",
                x: Math.round(r.x), y: Math.round(r.y),
                visible: r.width > 0 && r.top >= 0 && r.top < window.innerHeight
            };
        })
        .filter(e => e.visible && e.text.length > 0)
''')
for e in elements:
    print(e)
```

### Extrair cookies e tokens de sessão
```python
cookies = await context.cookies()
cookie_dict = {c['name']: c['value'] for c in cookies}
# Ex: token CSRF do LinkedIn está em cookie 'JSESSIONID'
```

## Passo 4 — Verificar resultado

Sempre tire um screenshot após a ação e leia para confirmar que funcionou. Nunca declare "feito" sem verificar.

```python
await page.screenshot(path=r"C:\Users\lucas\AppData\Local\Temp\resultado.png")
```

## Fluxo de diagnóstico quando algo não funciona

1. **Seletor não encontra o elemento** → tire screenshot, veja o que está na tela, ajuste o seletor ou use coordenadas
2. **Timeout** → aumentar `timeout=60000` no método, ou usar `wait_for_load_state("domcontentloaded")` em vez de `"networkidle"`
3. **Site bloqueia automação** → usar `connect_over_cdp` com Chrome real (não Chromium limpo do Playwright)
4. **Precisa de login** → usuário faz login manualmente na janela aberta, depois o script assume
5. **Login bloqueado no Chromium** → usar Chrome real com `--user-data-dir` do perfil do usuário (sessão já salva)

## Sites já mapeados

| Site | Skill específica | Observação |
|------|-----------------|------------|
| LinkedIn (empresa) | `/editar-linkedin` | Requer Super Admin; usa Voyager API |
| Negócio Cultural | `/editar-negocio-cultural` | WordPress + Tutor LMS |
| Qualquer outro | Esta skill | Adaptar conforme o site |

## Instalação (se necessário)

```bash
pip install playwright
python -m playwright install chromium
```
