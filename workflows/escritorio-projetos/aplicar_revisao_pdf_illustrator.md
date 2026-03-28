# Aplicar Revisao de PDF no Illustrator

## Objetivo
Ler comentarios/anotacoes de revisao de um PDF e aplicar as correcoes de texto automaticamente no arquivo correspondente aberto no Adobe Illustrator.

## Quando usar
- Voce recebeu um PDF com marcacoes de revisao (highlights, riscos, notas adesivas, comentarios)
- O arquivo original (.ai) esta aberto no Illustrator
- Precisa aplicar dezenas de correcoes de texto sem fazer manualmente uma a uma

## Inputs necessarios
| Input | Obrigatorio | Descricao |
|-------|-------------|-----------|
| PDF revisado | Sim | Arquivo PDF com comentarios/anotacoes de revisao |
| Arquivo .ai aberto | Sim | Documento correspondente aberto no Illustrator |

## Pipeline

### Fase 1: Extracao de comentarios do PDF

```bash
python tools/extract_pdf_comments.py --pdf "CAMINHO_DO_PDF" --output .tmp/text_edits/pdf_edits.json
```

**Tipos de anotacao reconhecidos:**
- **Highlight + comentario**: texto destacado = original, comentario = instrucao de troca
- **StrikeOut (riscado)**: texto a remover. Se tiver comentario, usa como substituto
- **Caret (insercao)**: ponto de insercao com texto novo no comentario
- **Sticky note**: comentario posicional — tenta extrair instrucao de troca
- **FreeText**: anotacao de texto livre
- **Underline/Squiggly + comentario**: texto marcado com instrucao

**Padroes de comentario reconhecidos (PT/EN):**
- "trocar por: texto novo"
- "alterar para: texto novo"
- "substituir por texto novo"
- "deve ser: texto novo"
- "-> texto novo"
- Texto entre aspas = texto substituto
- Comentario curto sem interrogacao = provavel substituto (confianca media)

**Output:** JSON com edits classificados por tipo (replace/delete/insert) e nivel de confianca (high/medium/low).

### Fase 2: Revisao das edicoes

Antes de aplicar, o agente deve:
1. Ler o JSON extraido
2. Apresentar as edicoes ao usuario organizadas por confianca
3. Pedir confirmacao, especialmente para edicoes de confianca baixa/media
4. Permitir ajustes manuais no mapeamento

**Opcao automatica (sem revisao):** use `--auto` somente se o usuario confirmar que confia nos comentarios.

### Fase 3: Aplicacao no Illustrator

```bash
# Pipeline completo (com revisao interativa)
python tools/apply_text_edits_illustrator.py --pdf "CAMINHO_DO_PDF"

# Dry-run primeiro (recomendado)
python tools/apply_text_edits_illustrator.py --pdf "CAMINHO_DO_PDF" --dry-run

# Aplicar JSON ja revisado
python tools/apply_text_edits_illustrator.py --edits-json .tmp/text_edits/pdf_edits.json --auto

# Filtrar por confianca (so aplicar as certas)
python tools/apply_text_edits_illustrator.py --pdf "CAMINHO_DO_PDF" --min-confidence high --auto

# Match fuzzy (para textos com pequenas diferencas)
python tools/apply_text_edits_illustrator.py --pdf "CAMINHO_DO_PDF" --match-mode fuzzy
```

**Modos de match:**
- `exact`: texto tem que ser identico ao text frame inteiro
- `contains` (default): busca o trecho dentro de text frames maiores
- `fuzzy`: tolera diferencas de pontuacao, espacos, acentos

### Fase 4: Verificacao

Apos aplicar:
1. Conferir o relatorio em `.tmp/text_edits/apply_report.json`
2. Verificar edicoes "not_found" — podem indicar texto que difere entre PDF e .ai
3. Se houver edicoes nao encontradas, tentar com `--match-mode fuzzy`
4. Salvar o documento no Illustrator

## Flags uteis

| Flag | Descricao |
|------|-----------|
| `--extract-only` | So extrai comentarios, nao aplica |
| `--dry-run` | Simula aplicacao sem alterar documento |
| `--auto` | Aplica sem pedir confirmacao |
| `--min-confidence high` | So aplica edicoes de alta confianca |
| `--match-mode fuzzy` | Match tolerante a pequenas diferencas |
| `--page N` | Processar apenas pagina N do PDF |
| `--no-case-sensitive` | Busca sem distinguir maiusculas |

## Troubleshooting

| Problema | Solucao |
|----------|---------|
| "Nenhuma edicao encontrada" | PDF pode nao ter anotacoes nativas (ex: marcacoes feitas como desenho). Verificar com `--show` |
| "not_found" em varias edicoes | Texto no PDF difere do .ai (reflow, hifenizacao). Tentar `--match-mode fuzzy` |
| Erro COM/Illustrator | Verificar que o Illustrator esta aberto com o documento correto |
| Texto trocado errado | O match "contains" pode pegar o texto errado se for generico. Usar `--match-mode exact` |
| Comentarios em formato inesperado | Editar o JSON manualmente em `.tmp/text_edits/pdf_edits.json` e aplicar com `--edits-json` |

## Arquivos gerados
```
.tmp/text_edits/
  pdf_edits.json      # Edicoes extraidas do PDF
  edits_config.json   # Config enviada ao JSX
  edits_config_result.json  # Resultado do JSX
  apply_report.json   # Relatorio final
```
