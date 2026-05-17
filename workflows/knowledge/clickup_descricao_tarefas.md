# ClickUp — Formatacao de Descricao de Tarefas

> Referencia rapida para escrever descricoes de tasks ClickUp que renderizam corretamente.

---

## Regra principal

Sempre usar o parametro `markdown_description` (e nao `description`) ao chamar o MCP `clickup_update_task` ou `clickup_create_task`. O campo `description` aceita somente texto plano e ignora toda formatacao. O `markdown_description` renderiza markdown no ClickUp.

```python
# ERRADO — nao formata
clickup_update_task(task_id="...", description="## Titulo\n| col | col |")

# CORRETO — renderiza tabela, negrito, cabecalhos
clickup_update_task(task_id="...", markdown_description="## Titulo\n| col | col |")
```

---

## Estrutura padrao de descricao

```markdown
## NOME DA SECAO
**Campo-chave:** valor | **Outro campo:** valor

---

## OUTRA SECAO
Texto corrido.

---

## TABELA

| Coluna 1 | Coluna 2 | Coluna 3 |
|---|---|---|
| valor | valor | valor |

---

**LINK OU CAMPO DESTACADO:**
https://...
```

### Elementos que funcionam

| Elemento | Sintaxe | Observacao |
|---|---|---|
| Cabecalho de secao | `## NOME` | Usa `##`, nao `#` |
| Negrito em campo | `**Nome:** valor` | Para rotulos inline |
| Divisor | `---` | Separa secoes visuais |
| Tabela | `\| col \| col \|` seguido de `\|---|---|` | Linha de separador obrigatorio |
| Lista | `- item` ou `1. item` | Funciona normalmente |
| Bloco de codigo | triple backtick | Para scripts/comandos |

### Elementos que NAO funcionam no ClickUp

- Tabelas sem a linha `|---|---|` de separador (renderiza como texto)
- Cabecalho `#` nivel 1 (some ou fica igual ao `##`)
- HTML inline (`<b>`, `<br>`, `<table>`) — ignorado ou renderiza como texto

---

## Exemplo real: briefing de video

```markdown
## CONTEXTO DO VIDEO
**Projeto:** 117 — Teatro e Oficina Robotica 4a Edicao
**Captacao:** 04 a 08/05/2026
**Formato:** Reel viral 9:16 vertical ate 60s

---

## PERSONAGEM CENTRAL
Crianca participante. Ela fala diretamente para a camera.

---

## SCRIPT SUGERIDO

| Tempo | Texto na tela | Narracao |
|---|---|---|
| 0:00-0:05 | "Rio Claro" | "Ela nao sabia o que ia encontrar." |
| 0:20-0:50 | sem texto | DEPOIMENTO da crianca |

---

**PASTA DO DRIVE:**
https://drive.google.com/drive/folders/...
```

---

## Checklist rapido antes de salvar

- [ ] Usando `markdown_description`, nao `description`
- [ ] Toda tabela tem linha `|---|---|` apos o cabecalho
- [ ] Secoes separadas por `---`
- [ ] Campos-chave em negrito (`**Campo:**`)
