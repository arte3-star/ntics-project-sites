---
name: editar-linkedin
description: "Edita o perfil de páginas de empresa no LinkedIn (tagline, descrição, especialidades, website) via Playwright + Voyager API interna. Requer Super Admin na página."
user-invocable: true
---

Você é o editor de páginas de empresa no LinkedIn. Siga o fluxo abaixo para qualquer edição solicitada.

## Pré-requisito Crítico

O usuário deve ser **Super Admin** da página LinkedIn — não apenas Administrador de Conteúdo.

| Função | Pode editar perfil? |
|--------|-------------------|
| Super Admin | ✅ Sim |
| Administrador de Conteúdo | ❌ Não |

Para promover: **Configurações → Gerenciar administradores → alterar função**.

## Ferramentas

- **Playwright** (já instalado: `pip install playwright` + `playwright install chromium`)
- **Chrome com CDP** (porta 9222) — conecta ao Chrome real do usuário (sessão autenticada)
- **LinkedIn Voyager API** — API interna do LinkedIn usada pelo próprio frontend

## Passo 1 — Abrir Chrome com sessão real

Lance um Chrome separado com remote debugging (não interfere nas abas abertas):

```bash
"/c/Program Files/Google/Chrome/Application/chrome.exe" \
  --remote-debugging-port=9222 \
  --user-data-dir="C:\\Users\\lucas\\AppData\\Local\\Temp\\linkedin-session" \
  --no-first-run \
  --no-default-browser-check \
  "https://www.linkedin.com/login" &
```

Aguarde o usuário fazer login com **email/senha** (não Google — bloqueado no Chromium limpo).

## Passo 2 — Conectar via CDP e verificar sessão

```python
import asyncio
from playwright.async_api import async_playwright

async def connect():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp("http://localhost:9222")
        context = browser.contexts[0]
        page = context.pages[0]
        await page.goto("https://www.linkedin.com/feed/")
        await page.wait_for_load_state("domcontentloaded")
        url = await page.evaluate('window.location.href')
        print(f"Sessão ativa: {url}")
        return page, context
```

## Passo 3 — Verificar permissão de Super Admin

Navegue para `https://www.linkedin.com/company/<ID>/admin/dashboard/` e verifique se há botão "Editar página" ou ícone de lápis na sidebar. Se não aparecer → usuário é Content Admin apenas.

**Identificar company ID:**
```python
await page.goto("https://www.linkedin.com/company/<slug>/")
# O redirect revela o ID numérico na URL: /company/35558673/admin/dashboard/
```

## Passo 4 — Ler dados atuais via Voyager API

```python
result = await page.evaluate('''
    async () => {
        const res = await fetch('/voyager/api/organization/companies/COMPANY_ID', {
            headers: {
                'csrf-token': document.cookie.match(/JSESSIONID="?([^";]+)/)?.[1] || '',
                'x-restli-protocol-version': '2.0.0',
                'accept': 'application/vnd.linkedin.normalized+json+2.1'
            }
        });
        const data = await res.json();
        const c = data?.data || data;
        return {
            tagline: c.tagline,
            description: c.description,
            specialties: c.specialties,
            websiteUrl: c.websiteUrl,
            headquarter: c.headquarter
        };
    }
''')
```

## Passo 5 — Atualizar via Voyager API (requer Super Admin)

```python
update_payload = {
    "tagline": "NOVO TAGLINE",
    "description": "NOVA DESCRIÇÃO",
    "specialties": ["Especialidade 1", "Especialidade 2"],
    "websiteUrl": "https://www.exemplo.com.br"
}

result = await page.evaluate('''
    async (payload) => {
        const csrf = document.cookie.match(/JSESSIONID="?([^";]+)/)?.[1] || '';
        const res = await fetch('/voyager/api/organization/companies/COMPANY_ID', {
            method: 'POST',
            headers: {
                'csrf-token': csrf,
                'x-restli-protocol-version': '2.0.0',
                'content-type': 'application/json',
                'x-http-method-override': 'PATCH'
            },
            body: JSON.stringify(payload)
        });
        return {status: res.status, ok: res.ok};
    }
''', update_payload)
```

## Passo 6 — Verificar alteração

Releia via API (Passo 4) e confirme que os campos foram salvos. Nunca declare "feito" sem verificar.

---

## Campos editáveis no LinkedIn

| Campo | API key | Limite |
|-------|---------|--------|
| Slogan/Tagline | `tagline` | 120 chars |
| Sobre (descrição) | `description` | 2.000 chars |
| Especialidades | `specialties` | lista de strings |
| Website | `websiteUrl` | URL completa |
| Sede | `headquarter` | objeto de endereço |

## Dados NTICS (referência)

**Company ID:** 35558673  
**Slug:** nticsprojetos

**Tagline proposta:**
> Transformamos o propósito da sua empresa em projetos de impacto social — com leis de incentivo fiscal.

**Descrição proposta:**
> A NTICS Projetos desenha, executa e mensura programas de impacto social para empresas que investem via leis de incentivo fiscal — Rouanet, Lei do Esporte e FIA/FUMCAD.
>
> Em 24 anos de operação, desenvolvemos mais de 1.060 projetos em 165+ cidades, impactando 11,4 milhões de pessoas em educação, cultura, sustentabilidade e responsabilidade social corporativa.
>
> Nossos programas transformam o incentivo fiscal da sua empresa em indicadores ESG mensuráveis, alinhados aos ODS da ONU e reportados segundo os GRI Standards.
>
> Por que escolher a NTICS:
> — ISO 9001 | GRI Standards | Signatária do Pacto Global da ONU desde 2018
> — NPS 88 | Nota média 9,32 entre clientes e beneficiários
> — 100% emissões neutralizadas | 75% liderança feminina
> — Clientes: Whirlpool, Nubank, Bayer, Eneva, CNH Industrial, Engie
>
> Somos parte do Grupo NEST, ecossistema com soluções em ESG, consultoria e capacitação.
>
> Nossas frentes:
> — LAB NTICS: laboratório de inovação e criatividade
> — HUB ESG: hubs regionais de impacto (Cuiabá, Manaus, BH, Campinas)
> — NTICS Educa: escola de líderes e jovens do futuro
> — NTICS Recicla: economia circular via Lei de Reciclagem
>
> Transformamos o propósito da sua empresa em projetos de impacto real — com dados para provar.

**Especialidades propostas:**
Leis de Incentivo Fiscal, Lei Rouanet, Lei do Esporte, ESG, Responsabilidade Social Corporativa, Impacto Social Mensurável, Relatórios GRI, ODS, Sustentabilidade, Educação, Cultura, Projetos Sociais, Pacto Global ONU, Incentivo Fiscal

**Website:** https://www.ntics.com.br

## Observações Aprendidas

- LinkedIn bloqueia login via Chromium "limpo" → usar Chrome real do usuário com `--remote-debugging-port`
- Não usar login com Google no Chromium separado → bloqueado por segurança
- A URL `/company/<slug>/` redireciona admins para `/admin/dashboard/` — usar ID numérico direto
- O botão "Editar página" só aparece para Super Admin — Content Admin não vê a opção
- A Voyager API funciona via `fetch()` no contexto do browser autenticado (sem necessidade de credenciais externas)
- CSRF token está no cookie `JSESSIONID` (remover as aspas ao usar)
