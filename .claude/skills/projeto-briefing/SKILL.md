---
name: projeto-briefing
description: "Gera briefing detalhado para um deliverable do projeto e delega à skill de produção correspondente do plugin ntics-brain (carrossel-cliente, briefing-video, kv-derivar, etc.)"
user-invocable: true
---

# /projeto-briefing — Gerar briefing e disparar produção

Quando o usuário invocar `/projeto-briefing <slug> <deliverable-id>`, orquestre a produção do deliverable usando dados do projeto + skill correspondente do plugin `ntics-brain`.

## Entrada

- `<slug>` — ex: `132-estacao-samarco`
- `<deliverable-id>` — ex: `A1`, `B2`, `C1`, `VIDEO-PRE-MG`

## Passos

1. **Carregar contexto (ordem obrigatória):**
   - `brand/NTICS-cheatsheet.md` — regras genéricas de voz, cores, vocabulário (sempre primeiro)
   - `SecondBrain/projetos/{slug-canonico}/brand-aplicacao-{patrocinador}.md` — SUBSTITUI regras NTICS quando aplicável (logo do cliente soberana, tom editorial específico, territórios sensíveis). Se este arquivo existir, **as regras dele têm precedência sobre o cheatsheet NTICS**.
   - `SecondBrain/projetos/{slug}/CLAUDE.md` — contexto operacional
   - `SecondBrain/projetos/{slug}/state.yaml` — encontrar o deliverable por id, extrair: `tipo`, `skill`, `formato_final`, `formato_entrega`, `dependencia`, `nome`
   - `SecondBrain/projetos/{slug}/stakeholders.yaml` — fluxo de aprovação, canais, cadência
   - `SecondBrain/projetos/{slug}/decisoes.md` — restrições recentes capturadas pelo sync
   - `SecondBrain/projetos/{slug}/brief/tap.md` e fontes apontadas — referências complementares

2. **Validar:**
   - Se `dependencia` contiver algum deliverable com status ≠ `concluido`, alertar o usuário: "A1 precisa estar concluído antes de B2. Continuar mesmo assim?" e só prosseguir com confirmação.
   - Se algum `blocker` do state.yaml impactar este deliverable, alertar explicitamente.

3. **Montar briefing consolidado:**
   - Ler o briefing detalhado correspondente em `AUTOMAÇÕES/output/marketing/132-briefings-propostos.md` (ou equivalente do projeto) buscando pelo id (A1, A2, B1, etc.).
   - Injetar no briefing:
     - Patrocinador + regras de marca de `stakeholders.yaml`
     - Tom editorial de `CLAUDE.md` do projeto
     - Referências de fotos (ex: `SecondBrain/projetos/{slug}/assets/`, se existir)
     - Formato final e de entrega do `state.yaml`

4. **Delegar para skill de produção do plugin `ntics-brain`:**

   | deliverable.skill | ação |
   |---|---|
   | `/kv-derivar` | Invocar `/kv-derivar` com briefing + manual Samarco |
   | `/carrossel-cliente` | Invocar `/carrossel-cliente` com 8 cards do briefing |
   | `/carrossel-educativo` | Invocar `/carrossel-educativo` |
   | `/briefing-video` | Invocar `/briefing-video` com roteiro sugerido |
   | `/post-instagram` | Invocar `/post-instagram` |
   | `/arte-impressao-cmyk` | Invocar com dimensões, sangria e conteúdo |
   | `/estampa-textil` | Invocar com área de estampa + tecido |
   | `/google-slides-template` | Invocar com placeholders nomeados |
   | `null` | Entregar o briefing em markdown para execução manual (ex: mockup Figma) |

5. **Salvar output do deliverable** em `SecondBrain/projetos/{slug}/content/{deliverable-id}/` com subpasta por tipo de arquivo.

6. **Ao final**, sugira: "Após revisão visual, use `/projeto-avanca {slug} {deliverable-id}` para marcar concluído e comentar no ClickUp."

## Regras

- **Leia feedback_* relevantes antes de gerar:** `feedback_leonardo_prompts.md`, `feedback_carrossel_case_padrao.md`, `feedback_assets_projetos.md`, etc.
- **Logo Samarco soberana** em peças do 132. NTICS só como "realização".
- **Nunca usar travessão `—`** em textos (regra global NTICS).
- **Respeitar territórios sensíveis** (Bento Rodrigues, Paracatu de Baixo, Santa Rita Durão) — tom positivo, sem referência ao rompimento.
- Se o deliverable já tem `output` preenchido no state.yaml, perguntar antes de sobrescrever.
