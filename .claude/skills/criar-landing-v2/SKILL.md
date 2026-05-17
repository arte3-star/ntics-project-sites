---
name: criar-landing-v2
description: "Cria landing page de projeto NTICS em ntics.com.br/{slug}/ sem Renderforest. Claude escreve o HTML diretamente guiado por /frontend-design e /ui-ux-pro-max. Fonte: ClickUp (briefing) + assets locais (logo, regua, fotos). Fallback: /criar-landing-preprojeto."
user-invocable: true
---

Você é o construtor de landing pages v2 do `ntics.com.br`. Escreve o HTML diretamente com
qualidade de produção, guiado pelas skills `/frontend-design` e `/ui-ux-pro-max`.

**Fallback disponível:** se este fluxo falhar, usar `/criar-landing-preprojeto` (pipeline Python + Lovable).

Leia e execute o workflow completo em `workflows/marketing/producao/landing_v2_ntics.md`.

## Quando usar

- Projeto novo sem site no Renderforest
- RF não está mais disponível
- Quer visual acima do padrão RF-origin
- Projeto pre-execução OU pós-execução

## Inputs

**Mínimos (obrigatórios):**
1. Nome ou ID do projeto no ClickUp
2. Slug da URL desejada (ex: `teatro-bons-habitos-ferroporte`)

**Opcionais (melhoram o resultado):**
- Cores da marca do patrocinador (hex)
- Fotos próprias do projeto
- Linha de ativação / hero subtitle

## Fluxo resumido

```
[1] Coletar conteudo (ClickUp)
[2] Coletar assets (logo, regua, fotos)
[3] Design thinking (/frontend-design + /ui-ux-pro-max)
[4] Claude escreve index.html completo
[5] Upload via REST API
[6] Verificacao obrigatoria
```

## Skills ativas neste fluxo

| Skill | Quando entra |
|---|---|
| `/frontend-design` | Passo 3: define direcao estetica antes de codar |
| `/ui-ux-pro-max` | Passo 3: checklist de acessibilidade, spacing, responsividade |

## Diferenca dos outros fluxos

| Fluxo | Fonte HTML | RF necessario |
|---|---|---|
| `criar-landing-ntics` | Script Python (template RF-origin) | Sim (obsoleto) |
| `criar-landing-preprojeto` | Script Python (template RF-origin) | Nao (usa Lovable) |
| `criar-landing-v2` (este) | Claude escreve direto | Nao |
