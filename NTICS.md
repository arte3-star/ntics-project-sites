# NTICS Projetos — Hub de Automação

> Empresa de impacto social especializada em projetos de educação, sustentabilidade e cultura, financiados por leis de incentivo. Esta pasta é a **plataforma de IA e automação** que multiplica a capacidade da equipe.

---

## Organograma

```
NTICS Projetos
│
├── Hub de IA & Comunicação ............. Lucas Rotta
├── Escritório de Projetos (PMO) ........ [responsável]
├── Inscrição de Projetos ............... [responsável]
├── Marketing & Comunicação ............. [responsável]
├── Financeiro .......................... [futuro]
└── Vendas & Captação ................... [futuro]
```

→ Detalhes: [org/ORG.md](org/ORG.md)

---

## Mapa de Navegação

| Quero... | Ir para |
|---|---|
| Entender como este sistema funciona | [CLAUDE.md](CLAUDE.md) |
| Ver a estrutura organizacional | [org/ORG.md](org/ORG.md) |
| Encontrar um workflow / SOP | [workflows/INDEX.md](workflows/INDEX.md) |
| Encontrar um script / tool | [tools/INDEX.md](tools/INDEX.md) |
| Usar um squad especialista | [squads/](squads/) |
| Consultar identidade visual | [brand-book/INDEX.md](brand-book/INDEX.md) |
| Acessar acervo de assets dos projetos (fotos, logos, KVs) | [assets/INDEX.md](assets/INDEX.md) |
| Ver outputs gerados | [output/](output/) |
| Ver filas de processamento | [queue/](queue/) |
| Ver automações n8n | [n8n/](n8n/) |
| Acessar o Segundo Cérebro | [SecondBrain/](SecondBrain/) |

---

## Arquitetura WAT

Esta plataforma usa o **WAT Framework** (Workflows, Agents, Tools):

- **Workflows** (`workflows/`) — SOPs em Markdown. Dizem o QUE fazer e em que ordem.
- **Agents** (este Claude) — Lê workflows, toma decisões, orquestra tools e squads.
- **Tools** (`tools/`) — Scripts Python determinísticos. Fazem o trabalho pesado.

> "AI handles reasoning. Code handles execution. That's what makes the system reliable."

---

## Departamentos

| Departamento | Missão | DEPT |
|---|---|---|
| Hub de IA | Construir e manter a plataforma de automação | [org/hub-ia/](org/hub-ia/DEPT.md) |
| PMO | Estruturar, abrir e comunicar projetos de impacto | [org/escritorio-projetos/](org/escritorio-projetos/DEPT.md) |
| Inscrição | Submeter projetos a leis de incentivo com excelência | [org/inscricao-projetos/](org/inscricao-projetos/DEPT.md) |
| Marketing | Posicionar NTICS e projetos como referência de impacto | [org/marketing/](org/marketing/DEPT.md) |
| Financeiro | Orçamento, compliance e prestação de contas | [org/financeiro/](org/financeiro/DEPT.md) |
| Vendas | Captar patrocinadores e converter propostas | [org/vendas/](org/vendas/DEPT.md) |

---

## Identidade da Empresa

- **Propósito:** Gerar impacto em educação, sustentabilidade e cultura via leis de incentivo
- **Visão 2030:** Hub de referência em projetos ESG no Brasil
- **Brand Book:** [brand-book/](brand-book/INDEX.md)
- **Dados de marca:** [brand-book/data/brand-data.yaml](brand-book/data/brand-data.yaml)
