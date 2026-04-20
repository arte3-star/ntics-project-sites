---
name: carrossel-cliente
description: "Cria carrossel de projeto ativo do cliente com identidade visual do patrocinador a partir de release, TAP ou briefing (8 cards via Leonardo AI)"
user-invocable: true
---

> 📚 **Referência Leonardo AI:** Esta skill tem sua estrutura de geração validada — siga o workflow normalmente. Se surgir erro da API, dúvida sobre payload ou resultado visual inesperado, consulte `workflows/marketing/referencia/leonardo_ai_core.md` como base de conhecimento complementar (erros conhecidos, modos, exemplos).

Leia e execute o workflow completo em `workflows/marketing/producao/carrosseis/carrossel_projeto_ativo_cliente.md`.

## Inputs

**Minimos (obrigatorios):**
1. **Release, TAP ou briefing** do projeto (pelo menos 1)
2. **Nome da empresa** cliente/patrocinadora
3. **Site da empresa** (URL)
4. **Fotos** do projeto (6 fotos na pasta `.tmp/marketing/carrosseis/projetos/{numero-projeto}/{fase}/fotos/`)

**Opcionais (melhoram o resultado):**
- Foco do carrossel (convite, cidade, atividade, completo, institucional, resultados)
- Instagram da empresa (@ ou URL)
- Manual de marca / KV / guia visual
- Logo da empresa (PNG/SVG transparente)
- Cores da marca (se ja conhecidas)

## Ferramentas Disponiveis

| Ferramenta | Arquivo | Funcao |
|-----------|---------|--------|
| Gerador de cards | `tools/gerar_carrossel_sylvamo.py` | Referencia: upload foto + geracao Leonardo AI (7 cards) |
| Gerador de CTA | `tools/gerar_cta_sylvamo.py` | Referencia: card CTA via Pillow (fundo solido + logos) |

**Nota:** Esses scripts sao implementacoes de referencia para o projeto Sylvamo/PEC. Para novos clientes, copiar e adaptar com as cores, textos e fotos do novo projeto.

## Estrutura dos 8 Cards

| Card | Nome | Funcao |
|------|------|--------|
| 01 | Capa | Atrair: nome do projeto + patrocinador + frase de impacto |
| 02 | O Projeto | Apresentar: o que e, objetivo, publico |
| 03 | Metodologia | Explicar: como funciona, atividades, formato |
| 04 | Alcance | Dimensionar: numeros, cidades, beneficiarios |
| 05 | A Empresa | Valorizar patrocinador: quem e, por que apoia |
| 06 | Expectativa/Resultado | Pre: o que se espera / Pos: o que foi alcancado |
| 07 | Impacto | Inspirar: visao de longo prazo, transformacao |
| 08 | CTA | Converter: logos patrocinador + NTICS + redes sociais |

## Regras de Consistencia Visual (aprendizados)

1. **Cor do degrade:** Manter a mesma cor primaria da marca em TODOS os cards (nao alternar entre cores diferentes de degrade — quebra o padrao visual)
2. **Highlights:** Usar UMA cor de destaque consistente para badges e palavras-chave
3. **Tom dos textos:** Adotar o mesmo tom do Roteiro de Edicao de Video do projeto. Os textos devem soar como a empresa fala, nao como marketing generico
4. **CTA:** Fundo na cor primaria da marca (nao branco se o logo do patrocinador for dessa cor). Logos com tamanho generoso (20% da altura para patrocinador, 12% para NTICS). Texto "Realizacao" acima do logo NTICS
5. **Barra gradiente:** Sempre presente no rodape de TODOS os cards, colada na borda inferior

## Fluxo

Comece pelo Passo 1 (identificacao dos dados do release) e siga o fluxo com as 2 paradas de validacao:
1. Apos perfil visual do cliente (Passo 3.4)
2. Apos textos dos 8 cards (Passo 4)
