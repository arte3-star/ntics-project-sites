# Workflow: Revisão de Arte para Impressão

## Objetivo
Auditoria técnica de arte antes do envio à gráfica. Valida CMYK, DPI, sangria, fontes em outline, logos vetoriais, hierarquia de marcas e regras específicas do projeto. Retorna checklist pass/fail com instruções de correção.

## Quando Executar
- Antes de enviar qualquer arte impressa para gráfica
- Após execução de `/arte-impressao-cmyk` (validação automática)
- Ao receber arte finalizada da designer externa
- Como diagnóstico de arte que saiu errada da gráfica

## Inputs Necessários

| Input | Fonte | Obrigatório |
|---|---|---|
| Arquivo | .PDF · .AI · .EPS · .PNG preview | Sim |
| Tipo de peça | rollup, pantojet, wind banner, camiseta, placa, etc. | Sim |
| Dimensões esperadas (cm) | Brief ou TAP | Sim |
| Código do projeto | Para cruzar com TAP no SecondBrain | Não (recomendado) |

## Passo a Passo

### Fase 1 — Identificação do projeto
Se tem código: ler `SecondBrain/projetos/{codigo}/tap.md` para extrair:
- Se é Lei de Incentivo (define se precisa régua MinC)
- Qual logo é soberana
- Qual logo é patrocinadora / apresenta
- Qual logo é realização
- Se tem hashtags, slogans, restrições

### Fase 2 — Análise técnica
Rodar o tool:
```bash
python tools/adobe/revisao_arte_pdf.py --file arte.pdf --project 132
# ou
python tools/adobe/revisao_arte_ai.py --file arte.ai --project 132
```

O tool valida:

#### Bloco 1 — Cor
- 🟢 Espaço de cor do documento é CMYK
- 🔴 Se RGB: listar quais elementos estão em RGB
- 🟡 Se mix CMYK+spot Pantone: aceitável, verificar se é intencional

#### Bloco 2 — Resolução
- 🟢 Todas as imagens raster ≥ 300 dpi no tamanho final
- 🔴 Se alguma imagem < 300 dpi: listar qual e qual resolução
- 🟡 Logos vetoriais: 🟢 ok
- 🔴 Logos em PNG/JPG: logo precisa ser vetor

#### Bloco 3 — Sangria e bleed
- 🟢 Sangria ≥ mínimo do tipo de peça (3 mm universal, 3 cm rollup, 5 cm pantojet)
- 🔴 Se menor: bloqueia
- 🟢 Trim marks (marcas de corte) presentes
- 🟡 Se só sangria sem marca: aceitável

#### Bloco 4 — Fontes
- 🟢 Fontes convertidas em outline (no PDF final)
- 🟡 Fontes vivas (não outline) — risco de a gráfica não ter a fonte → converter
- 🔴 Fonte missing: bloqueia

#### Bloco 5 — Hierarquia de marca (project-specific)
Cruzar com TAP:
- 🟢 Logo soberana em destaque (tamanho, posição top/center)
- 🔴 Se patrocinadora não é soberana quando TAP diz que deveria
- 🟢 Logo realização NTICS presente rodapé
- 🔴 Se NTICS ausente ou maior que soberana
- 🟢 Régua MinC presente (se Lei de Incentivo) / ausente (se corporativo)
- 🔴 Régua MinC em projeto corporativo (como Estação Samarco) ou ausente em Lei de Incentivo

#### Bloco 6 — Regras editoriais NTICS
- 🟢 Sem travessão `—` em textos (regra NTICS)
- 🟢 Números com ponto decimal (12.3 não 12,3)
- 🟢 Acentuação PT-BR correta
- 🟡 Sigla "IA" — recomendar trocar para "inteligência artificial" por extenso

### Fase 3 — Relatório
Gerar markdown estruturado:

```markdown
# Revisão de arte — {nome_arquivo}
**Projeto:** 132 Estação Samarco
**Tipo:** Rollup Sabores

## Resultado: 🔴 BLOQUEADO / 🟡 COM RESSALVAS / 🟢 APROVADO

## Checklist
| Item | Status | Observação |
|---|---|---|
| CMYK | 🟢 Pass | — |
| DPI ≥ 300 | 🔴 Fail | Imagem logo_samarco.png em 150 dpi |
| Sangria 3 cm | 🟢 Pass | — |
| Fontes em outline | 🟡 Warning | Montserrat Bold não convertida |
| Logo soberana | 🟢 Pass | Estação Samarco em hierarquia 1 |
| Sem régua MinC | 🟢 Pass | Ausente (corporativo) |

## Correções necessárias
1. Trocar `logo_samarco.png` por vetor `.AI` ou gerar PNG em 300 dpi mínimo no tamanho final
2. Converter fonte Montserrat Bold em outline antes de exportar PDF

## Liberação
🔴 NÃO LIBERAR para gráfica até corrigir itens acima.
```

### Fase 4 — Decisão
- **🔴 Bloqueado**: retornar erro, bloquear envio, listar correções
- **🟡 Com ressalvas**: alertar + permitir envio com confirmação do usuário
- **🟢 Aprovado**: liberar envio à gráfica

Se integrado com task ClickUp: postar resultado como comentário.

## Output Esperado
- Relatório markdown com checklist detalhado
- Decisão: 🔴 / 🟡 / 🟢
- Lista de correções específicas

## Tools
- `tools/adobe/revisao_arte_pdf.py` — usa PyMuPDF (fitz) para inspeção
- `tools/adobe/revisao_arte_ai.py` — Illustrator COM para inspeção de camadas

## Regras por tipo de projeto

| Tipo projeto | Régua MinC | Logo patrocinador | Observação |
|---|---|---|---|
| Lei de Incentivo (Rouanet, PROAC) | Obrigatória | Soberana | Régua inferior com PRONAC, MinC, Lei |
| Lei da Reciclagem | Obrigatória própria | Soberana | Régua específica reciclagem |
| Corporativo (Samarco, Whirlpool) | Ausente | Soberana | Realização NTICS rodapé |
| NTICS próprio | Ausente | Logo NTICS soberana | — |

## Integração
- Chamado automaticamente por `/arte-impressao-cmyk` antes de entregar
- Pode ser invocado avulso para validar artes externas
- Complementa `/revisao-carrossel` (que foca digital)
