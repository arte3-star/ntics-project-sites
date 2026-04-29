# Padrão `projects/{slug}/`

Cada projeto NTICS tem um workspace próprio. Estrutura obrigatória:

```
projects/{slug}/
├── CLAUDE.md           # contexto operacional resumido (< 200 linhas)
├── state.yaml          # estado atual: fase, deliverables, próxima ação, blockers
├── stakeholders.yaml   # quem é quem no projeto (cliente, produtor, time NTICS)
├── budget.yaml         # rubricas aprovadas vs realizadas
├── tasks.yaml          # índice de tasks ClickUp relevantes (ID + status conhecido)
├── calendar.md         # cadência de comunicação e publicação
├── brief/              # TAP, releases e briefings recebidos
├── comms/              # histórico de e-mails trocados
└── content/            # outputs gerados (carrosseis, posts, videos)
```

## Convenções

### slug
- Formato: `{numero-projeto}-{patrocinador-kebab}` (ex: `132-samarco`, `087-engie`)
- Match com número no ClickUp/SecondBrain

### CLAUDE.md do projeto
- Até ~150 linhas
- Cobre: resumo do TAP (objetivo, escopo, trilhas, cidades, período), stakeholders-chave, regras específicas do patrocinador (cores, logo, restrições), particularidades de execução
- NÃO cola o TAP inteiro — referencia `brief/tap.md` para detalhes

### state.yaml
Estrutura mínima:
```yaml
slug: 132-samarco
fase: pre-kickoff   # ou: em-execucao, fechamento, concluido
atualizado: 2026-04-22
proxima_acao: "Aprovar KV A1 com Samarco"
blockers: []
deliverables:
  - id: A1-KV
    tipo: kv
    status: pendente    # ou: em-andamento, concluido
    skill: /kv-derivar
    output: null
  # ... demais
```

### stakeholders.yaml
```yaml
cliente:
  - nome: Amanda Sobrinho
    cargo: Gerente CSR Samarco
    email: amanda.sobrinho@samarco.com   # placeholder — confirmar
    canal_preferido: email
produtor_local: null   # TBD
time_ntics:
  - lucas@sbsustainablebusiness.com
  - ...
```

### tasks.yaml
```yaml
task_mae: "868j96x17"
subtasks:
  - id: "868xxxxxx"
    nome: "Aprovar KV"
    status: "to do"
    deliverable: A1-KV
```

## Ciclo de vida

1. `/projeto-status {slug}` — reporta fase, blockers, próxima ação
2. `/projeto-briefing {slug} {deliverable-id}` — gera briefing e invoca skill de produção do plugin
3. Revisão humana do output
4. `/projeto-avanca {slug} {deliverable-id}` — atualiza state, comenta ClickUp, salva no SecondBrain
5. `/projeto-email {slug} {tipo}` — quando o projeto demanda comunicação (calendário, relatório, aviso)

## Privacidade

`projects/*/` está gitignored. Apenas `INDEX.md` e este `README.md` são versionados. Stakeholders, orçamentos, contatos e outputs ficam locais.
