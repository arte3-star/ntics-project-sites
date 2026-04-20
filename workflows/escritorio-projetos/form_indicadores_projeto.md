# Workflow: Formulário de Indicadores de Projeto

## Objetivo
Gerar um Google Form de coleta de indicadores para qualquer projeto NTICS, a partir da seção **6) Indicadores** do Termo de Abertura (TAP) do projeto. O form consolida KPIs Gerais NTICS, Quantitativos, Específicos e ODS em um único link preenchível por GP / Produtor de Campo / Escritório de Projetos.

## Quando Executar
- Projeto tem TAP preenchido (seção 6) e está entrando em execução
- Precisa distribuir link de coleta de indicadores para GP e Produtor de Campo
- Consolidação final do projeto (relatório / prestação de contas)

## Inputs Necessários
| Input | Fonte | Obrigatório |
|-------|-------|-------------|
| Código do projeto (ex: 124) | Usuário | Sim |
| TAP do projeto (seção 6) | ClickUp Docs | Sim |
| Metas quantitativas do projeto | TAP seções 2.3 e 6.2 | Sim |

## Ferramentas
- **ClickUp MCP** (`clickup_search` + `clickup_get_document_pages`) — ler TAP
- **Tool Python:** `tools/gws/forms_create.py` — cria Google Form de YAML
- **Auth:** `tools/gws/gws_auth.py` (scope `forms.body` já incluso)

## Referências
- `workflows/knowledge/termo_abertura/anexo4_indicadores_camada.md` — KPIs gerais NTICS
- `workflows/knowledge/termo_abertura/anexo4.1_regras_indicadores.md` — Regras de coleta (participação única, multiplicador 3, N/A vs 0, escalas 0–10)
- `memory/reference_clickup_tap_docs.md` — Como achar TAP no ClickUp
- `memory/reference_google_forms_tool.md` — Tool forms_create.py
- **Exemplo de saída:** `output/projetos/124-compagas/form_indicadores_124.yaml`

## Passo a Passo

### Passo 1 — Localizar e ler o TAP do projeto
```python
clickup_search(
    keywords=f"Termo de Abertura {codigo}",
    filters={"asset_types": ["doc"]},
    count=5
)
# Pegar result com pageName == "TERMO DE ABERTURA - {codigo}"
# Usar doc_id + pageId

clickup_get_document_pages(
    document_id="<doc_id>",
    page_ids=["<pageId>"],
    content_format="text/md"
)
```

Ler com foco em:
- **0) Identificação** → nome do projeto, patrocinador, cidade
- **2.3 Meta geral** → metas quantitativas macro
- **6.1 Indicadores Gerais NTICS** → KPIs obrigatórios
- **6.2 Quantitativos** → metas específicas do projeto
- **6.3 Específicos** → perguntas customizadas
- **6.4 ODS** → ODS trabalhados

### Passo 2 — Mapear atividades do projeto
Ler seção **3.1 Escopo** e listar as atividades distintas (oficinas, workshops, palestras, exposições, etc). Essas entram como opções do campo "Atividade referente a este preenchimento" (checkbox).

### Passo 3 — Montar o YAML de config
Criar `output/projetos/{codigo}-{slug}/form_indicadores_{codigo}.yaml` seguindo a estrutura abaixo.

**Seções obrigatórias (todas):**

1. **Identificação do preenchimento** — nome, papel, atividade (checkbox), data, local
2. **Alcance** — beneficiários diretos, indiretos (×3)
3. **Perfil do público** — acessibilidade (nº + tipos), escolaridade, faixa etária, gênero
4. **Economia local** — fornecedores locais, empregos gerados
5. **Execução** — carga horária
6. **Percepção/aprendizagem** — temática, patrocinador, ODS (escalas 0–10) + ODS trabalhados (checkbox)
7. **Satisfação** — alunos + stakeholders (escalas + depoimentos em paragraph)
8. **Qualidade** — atendimento às expectativas
9. **Cliente** — NPS do patrocinador
10. **Impacto** — % nota ≥ 8 na pergunta de transformação + depoimentos
11. **Quantitativos do projeto** — um campo por linha da tabela 6.2, cada um com `description` mostrando a META
12. **Específicos do projeto** — um campo por linha da tabela 6.3
13. **ODS** — um campo por ODS da tabela 6.4
14. **Evidências e observações** — links + texto livre

**Regras de preenchimento do YAML:**
- `title` = "Indicadores do Projeto {codigo} — {nome do projeto} ({patrocinador})"
- `description` = contexto curto (cidade, período, quem preenche)
- `collect_email: true` (sempre — precisa identificar quem respondeu)
- Para cada item da tabela 6.2/6.3/6.4, incluir **a meta na `description`** do campo, para que o respondente tenha referência na hora de preencher
- Usar `type: scale` (low 0, high 10) para todas as médias 0–10 dos KPIs de percepção/satisfação
- Usar `type: text` para números absolutos (contagens, horas, %)
- Usar `type: paragraph` para depoimentos, distribuições (% por faixa) e observações
- Usar `type: checkbox` para opções múltiplas (atividades, tipos de acessibilidade, ODS)
- Campos de acessibilidade: deixar claro que "N/A" é diferente de "0" (anexo 4.1)

**Template mínimo de um campo:**
```yaml
- title: "Nome do indicador"
  type: text|paragraph|radio|checkbox|scale|date
  required: true|false       # opcional
  description: "Meta: X | Regra de coleta"  # contexto útil
  options: [...]             # só para radio/checkbox/dropdown
  low: 0                     # só para scale
  high: 10
  low_label: "..."
  high_label: "..."
```

### Passo 4 — Criar o form
```bash
cd tools/gws
python forms_create.py --config ../../output/projetos/{codigo}-{slug}/form_indicadores_{codigo}.yaml
```

Primeira execução de sessão pode pedir re-auth (abre browser). Depois imprime:
- Form ID
- URL de edição
- URL de resposta

### Passo 5 — Verificação pós-criação
Antes de declarar sucesso:
1. Abrir URL de edição e conferir: título, descrição, número total de perguntas
2. Confirmar que perguntas obrigatórias estão marcadas como required
3. Testar URL de resposta (abrir em aba anônima)

### Passo 6 — Entregáveis ao usuário
- URL de edição (para ajustes posteriores)
- URL de resposta (para distribuir ao time)
- Caminho do YAML (para regerar/alterar)
- Resumo: quantas perguntas no total, agrupadas por seção

## Decisões de Design

**Por que um único form e não um por atividade?**
O TAP já organiza indicadores de forma que a maioria aplica ao projeto inteiro (perfil público, satisfação, ODS). Um form único permite ao Produtor consolidar respostas por atividade via o campo "Atividade referente" (checkbox). Se o projeto tem atividades muito distintas (ex: exposição ≠ oficina), o GP pode preencher várias vezes — uma por atividade.

**Por que incluir a meta na description?**
Quem preenche geralmente não tem o TAP aberto do lado. Mostrar "Meta: 120 participantes" ao lado do campo elimina erros e acelera o preenchimento.

**Por que collect_email = true sempre?**
Auditoria e follow-up. Em prestação de contas (Rouanet/Lei Reciclagem) precisa identificar responsável pela evidência.

## Evoluções possíveis
- Vincular as respostas a uma Google Sheet (`service.forms().watches()`)
- Adicionar seção condicional por atividade (não suportado no tipo `scale`/`text`, mas em `sectionHeader` + `pageBreak`)
- Gerar task ClickUp "Preencher indicadores" com o link de resposta no campo
- Batch: criar forms de todos os projetos ativos de uma vez (loop pela list `90115187061`)

## Exemplo de execução (projeto 124 — Compagás, 2026-04-14)
- TAP: doc `8cje8p1-59571`, page `8cje8p1-34851`
- YAML: `output/projetos/124-compagas/form_indicadores_124.yaml` (47 perguntas)
- Form ID: `1fgDdqyUt0Vki56MZbGSU97pBO4E-IDOs0-dXj7af-5A`
