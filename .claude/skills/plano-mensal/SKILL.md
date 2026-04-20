---
name: plano-mensal
description: "Gera plano editorial mensal (arco ABT + hooks + calendario) e cria tasks no ClickUp para as 4 semanas"
user-invocable: true
---

Leia e execute o workflow completo em `workflows/marketing/producao/plano_mensal.md`.

## Inputs

**Minimos (obrigatorios):**
1. **Tema central** do mes (ex: "Responsabilidade Social Corporativa")
2. **Mes/Ano** (ex: "Abril 2026")

**Opcionais:**
- Projetos NTICS relevantes para cases
- Persona do patrocinador (Renata, Ricardo ou Carla)

## Fluxo

1. Gerar plano editorial completo (arco ABT, hooks, distribuicao, outline artigo)
2. Apresentar plano para aprovacao do Lucas
3. Apos aprovacao, criar tasks no ClickUp via `tools/integrations/create_social_media_tasks.py`:
   - 4 tarefas de carrossel educativo (segundas)
   - 4 tarefas de carrossel noticias (tercas)
   - 4 tarefas de carrossel case (quintas, se houver dados)
4. Retornar resumo do mes com links das tasks

## Ferramentas

| Ferramenta | Arquivo | Funcao |
|-----------|---------|--------|
| Plano editorial | `workflows/marketing/producao/plano_mensal.md` | SOP completo |
| Tasks ClickUp | `tools/integrations/create_social_media_tasks.py` | Criacao de tasks na lista 901109494072 |
