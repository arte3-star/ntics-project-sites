---
name: arte-impressao-cmyk
description: "Gera arte vetorial pronta para gráfica (.AI + .PDF CMYK 300 dpi com sangria + .PNG preview) para rollups, pantojet, wind banner, saia de bancada, moldura espelho, placa de fotos e qualquer impresso físico. Recebe dimensões finais, sangria, logos, paleta e conteúdo; devolve os 3 formatos prontos para envio direto à gráfica."
user-invocable: true
---

Leia e execute o workflow completo em `workflows/escritorio-projetos/arte_impressao_cmyk.md`.

## Quando usar

- Rollups (85×200 cm padrão)
- Pantojet / backdrop (2×2 m padrão)
- Wind banner (80×300 cm)
- Saia de bancada (90×200 cm)
- Placa de fotos (50×30 cm)
- Moldura espelho (vinil recortado)
- Qualquer impresso físico

## Inputs

- **Tipo de peça** e **dimensões finais** (cm)
- **Sangria** (padrão: 3 cm para rollup/banner · 5 cm para pantojet · 2 cm para placa pequena)
- **Paleta KV** (CMYK obrigatório — nunca RGB para impressão)
- **Logos** vetoriais (.AI/.EPS/.SVG) — patrocinador + realização
- **Hierarquia** (qual logo soberana, qual rodapé)
- **Conteúdo textual** (headlines, corpo, tagline)
- **Ícones** do enxoval do KV (opcional)

## Output

- `.AI` vetorial com camadas nomeadas (LOGO_SAMARCO, LOGO_NTICS, KV_PADRONAGEM, TEXTO, SANGRIA)
- `.PDF/X-4` CMYK 300 dpi com marcas de corte + sangria preservada
- `.PNG` preview RGB 1200 px (lado maior) para validação e task ClickUp

## Ferramentas

| Ferramenta | Arquivo | Função |
|---|---|---|
| Gerador arte impressão | `tools/adobe/arte_impressao.py` | Pipeline Illustrator COM: monta artboard + aplica camadas + exporta CMYK PDF/X-4 |
| Script JSX base | `tools/adobe/jsx/arte_impressao.jsx` | Ações Illustrator automatizadas |
| Adaptador existente | `tools/adobe/adapt_artwork_illustrator.py` | Reusa lógica de troca de cores/logos |

## Regras críticas

- **CMYK obrigatório** — converter quaisquer cores RGB antes de enviar
- **Sangria nunca menos de 3 mm** (3 cm para pantojet, 5 cm para backdrop inflável)
- **DPI ≥ 300** nas imagens embedadas
- **Fontes em outline** no PDF final (evita problema na gráfica)
- **Logos vetoriais sempre** — nunca PNG/JPG
- **Validar com `revisao-arte-impressao`** antes de entregar
