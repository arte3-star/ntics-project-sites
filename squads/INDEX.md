# Squads Index

Times de agentes com hierarquia Chief → Specialists. Cada squad tem um orquestrador (chief) que roteia para o especialista certo.

## Como usar um squad

1. Identifique o squad pelo tipo de problema (tabela abaixo)
2. Leia o `squad.yaml` do squad para entender a estrutura
3. Leia o agente chief (orquestrador) para entender o routing
4. O chief indica qual especialista usar — leia o agente especialista
5. Execute a task seguindo as instruções do especialista
6. Valide contra o `checklists/output-quality.md` do squad

## Marketing (`squads/marketing/`)

| Squad | Pasta | Chief | Quando usar |
|-------|-------|-------|-------------|
| Advisory Board | `squads/marketing/advisory-board/` | `board-chair` | Decisões estratégicas, investimento, liderança, cultura |
| Brand Squad | `squads/marketing/brand-squad/` | `brand-chief` | Posicionamento, identidade, naming, arquétipos, messaging |
| C-Level Squad | `squads/marketing/c-level-squad/` | `vision-chief` | Planejamento estratégico, operações, GTM, tecnologia |
| Copy Squad | `squads/marketing/copy-squad/` | `copy-chief` | Copywriting, emails, VSL, sales letters, headlines, landing pages |
| Data Squad | `squads/marketing/data-squad/` | `data-chief` | Analytics, métricas, CLV, growth, retenção, comunidade |
| Design Squad | `squads/marketing/design-squad/` | `design-chief` | Design systems, UX/UI, atomic design, componentes |
| Hormozi Squad | `squads/marketing/hormozi-squad/` | `hormozi-chief` | Ofertas, lead gen, pricing, vendas, hooks, lançamentos |
| Movement | `squads/marketing/movement/` | `movement-chief` | Construção de movimentos, manifestos, identidade coletiva |
| Storytelling | `squads/marketing/storytelling/` | `story-chief` | Narrativas, roteiros, brand storytelling, pitches |
| Traffic Masters | `squads/marketing/traffic-masters/` | `traffic-chief` | Tráfego pago, Facebook/YouTube/Google Ads, media buying |

## Estrutura de cada squad

```
squads/{area}/{squad-name}/
├── squad.yaml           # Manifesto: agentes, tasks, workflows, routing
├── config/config.yaml   # Tiers, handoffs, ativação
├── agents/              # Agentes MD (chief + especialistas)
├── tasks/               # Definições de tarefas com input/output
├── workflows/           # Orquestrações multi-fase (YAML)
├── checklists/          # Quality gates
└── data/                # Catálogos de frameworks e routing
```
