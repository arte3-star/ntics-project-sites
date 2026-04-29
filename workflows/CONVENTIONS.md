# Convenções de Workflows

Regras curtas para todo SOP em `workflows/`. Quando criar ou refatorar, copie `_TEMPLATE.md`.

## Estrutura fixa

Ordem das seções, sem variação:

1. Título `# Nome`
2. TL;DR em blockquote
3. `## Quando usar`
4. `## Inputs`
5. `## APIs e chaves` (omitir se não houver)
6. `## Tool(s)` (comando e flags)
7. `## Execução` (com fases numeradas a partir de 1)
8. `## Output esperado`
9. `## Checklist de qualidade`
10. `## Dependências` (upstream/downstream)

## Numeração de fases

Sempre `### Fase N: Título`, começando em 1. Sem `Fase 0`. Sem `Fase 1.5`. Se precisar inserir uma fase entre duas existentes, renumerar o arquivo inteiro.

Cada título traz marker de gate entre parênteses:
- `(auto)` roda sozinho, sem checagem crítica
- `(auto, bloqueante)` roda sozinho mas falha dura se checagem quebra
- `(gate humano)` pausa para Lucas validar antes de avançar

## Pontuação

Nunca usar travessão `—` (em-dash) em conteúdo novo. Trocar por vírgula, ponto ou espaço conforme a gramática. Vale para títulos, body, tabelas. Vale para todo conteúdo que o usuário lê ou publica.

## Referências a outros docs

Usar caminho relativo do root do projeto: `brand-book/data/brand-data.yaml`, `tools/content-gen/script.py`. Evitar URLs absolutas. Markdown link quando o leitor precisa clicar.

## Extração para knowledge

Se duas seções idênticas aparecem em workflows diferentes (identidade visual, regras de prompt, checklist Leonardo), extrair para `workflows/knowledge/` e linkar. Não duplicar regra em dois SOPs.

## Tamanho

Meta: 150 a 350 linhas por workflow. Acima disso, extrair knowledge ou dividir em fluxos menores. Acima de 500 linhas, justificar no TL;DR.

## Economia de tokens

- Referencie; não inclua. Se um checklist grande já existe em `referencia/`, linke em vez de copiar.
- Não abrir sempre com bloco de "contexto da marca" listando 3 arquivos do brand-book. O agente já sabe consultar `brand-book/INDEX.md` quando precisa.
- Exemplos são úteis, mas um exemplo representativo basta. Três são redundantes.

## Auditoria

Ao ler um workflow e encontrar desvio destas regras, corrija no mesmo commit em que for editar o arquivo por outro motivo. Não criar PR só para formatar.
