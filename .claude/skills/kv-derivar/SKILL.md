---
name: kv-derivar
description: "Deriva KV do projeto (subbrand) a partir do manual oficial do cliente. Pega logos, paleta e tipografia do manual, aplica ao nome do projeto específico e gera uma biblioteca de ícones temáticos via Leonardo AI com style reference bloqueada. Entrega .AI + .PDF manual + .PNG/.SVG ícones pronto para uso em todas as peças do projeto."
user-invocable: true
---

Leia e execute o workflow completo em `workflows/escritorio-projetos/kv_derivar_projeto.md`.

> 📚 **Referência Leonardo AI:** Esta skill usa Leonardo AI com style reference para gerar biblioteca de ícones coerente com o KV do cliente. Se surgir erro da API ou resultado visual inesperado, consulte `workflows/marketing/referencia/leonardo_ai_core.md` como base de conhecimento complementar.

## Quando usar

- Projeto corporativo em que o cliente fornece manual de marca e NTICS precisa derivar um KV próprio para o sub-programa
- Exemplo: Estação Samarco (sub da Samarco), PIE (sub do patrocinador), Teatro ODS (sub do patrocinador)
- Qualquer vez que o cliente pede "use nossa identidade mas adapte para este projeto específico"

## Inputs

- **Manual de marca do cliente** (.PDF) — paleta CMYK, tipografia, regras de aplicação
- **Nome do projeto** (ex: "Estação Samarco", "Negócio Cultural 3ª Edição")
- **Temas para ícones** — lista de áreas temáticas do projeto (ex: empreendedorismo, culinária sustentável, beleza, inteligência artificial, capacitação profissionalizante)
- **Hierarquia de marcas** (qual logo soberana, qual realização)
- **Quantidade de ícones** (padrão: 12)
- **Estilo visual dos ícones** (flat, linear, geométrico, preenchido) — deriva do manual cliente

## Output

- **`.AI` vetorial do logo projeto** com versões: positiva, negativa, colorida, horizontal, vertical, monocromática
- **`.PDF do manual** de aplicação visual (A4 horizontal, 300 dpi) com paleta, tipografia, aplicações, restrições e biblioteca de ícones
- **`.PNG 512×512 px + .SVG vetorial`** da biblioteca de ícones — mínimo 12 ícones
- **Folder do Drive do projeto** com estrutura: `KV/logos/` + `KV/icones/` + `KV/manual.pdf`

## Ferramentas

| Ferramenta | Arquivo | Função |
|---|---|---|
| Gerador KV | `tools/adobe/kv_derivar.py` | Orquestra: lê manual cliente → gera logo projeto → chama Leonardo AI para ícones → monta manual PDF |
| Leonardo AI | `workflows/marketing/referencia/leonardo_ai_core.md` | Style reference + payloads para ícones |
| Illustrator base | `tools/adobe/adapt_artwork_illustrator.py` | Manipulação vetorial |

## Fluxo

1. **Gate de design**: Invocar `/design-briefing` — confirmar estilo dos ícones (flat/linear/gradient), paleta derivada e tipografia com o usuário
2. Extrair do manual cliente: paleta CMYK, tipografia, regras
3. Gerar logo projeto (variações) via Illustrator
4. Gerar biblioteca de ícones via Leonardo AI com style reference bloqueada (cor única do KV)
5. Vetorizar ícones PNG→SVG (usar skill `/vetorizar` se necessário)
6. Montar manual PDF de aplicação visual
7. **OBRIGATORIO**: Revisão visual antes de entregar
8. Subir pacote na pasta Drive do projeto

## Regras críticas

- **Logo cliente soberana** — nunca inventar cores/tipografia se o manual existe
- **Ícones coerentes** — usar mesma cor-assinatura e mesmo peso visual em todos
- **Biblioteca reutilizável** — entregar como modelo para o tipo de programa (reuso futuro)
- **Sem régua MinC quando projeto não é Lei de Incentivo**
