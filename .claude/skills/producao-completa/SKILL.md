---
name: producao-completa
description: "Pipeline completo: Time de Design produz assets visuais, depois Time de Midias Sociais produz copy e distribui"
user-invocable: true
---

Este skill orquestra dois Agent Teams em sequencia:

## Etapa 1: Time de Design
Leia `workflows/marketing/team_design_content.md` e monte o Agent Team de design.
Aguarde a entrega dos assets em `.tmp/entrega/`.

## Etapa 2: Time de Midias Sociais
Apos a entrega dos assets, leia `workflows/marketing/team_social_media.md` e monte o Agent Team de midias sociais.
Os assets do Time de Design em `.tmp/entrega/` sao o input do Time de Midias Sociais.

## Pipeline
```
/time-design (assets visuais)
  └──> .tmp/entrega/
        └──> /time-social (copy + distribuicao)
              ├──> Gmail draft (newsletter)
              ├──> ClickUp tasks (publicacoes)
              └──> .tmp/publicacao/ (pacotes por plataforma)
```

Pergunte ao usuario:
1. Qual projeto/tema?
2. Quais tipos de assets visuais precisa? (carrossel, apresentacao, motion)
3. Quais plataformas de distribuicao? (Instagram, LinkedIn, newsletter)
4. Quais inputs tem disponiveis? (relatorio, fotos, template .aep)
