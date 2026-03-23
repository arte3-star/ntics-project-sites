# Workflow: Estruturador Lei Rouanet

## Objetivo
Estruturar projetos culturais para inscrição no MinC/Lei Rouanet, transformando texto-base em documento completo pronto para revisão, com boilerplates aplicados.

## Quando Executar
Quando um projeto cultural precisar ser estruturado para inscrição no MinC via Lei Rouanet.

## Inputs Necessários
| Input | Fonte | Obrigatório |
|-------|-------|-------------|
| Texto-base do projeto | Briefing, descrição corrida, documento bruto | Sim |
| Informações complementares | Reuniões, referências, documentos do proponente | Quando disponível |

## Documentos de Referência
- `workflows/knowledge/rouanet/` — Modelo mestre de inscrição (quando adicionado)

## Regras Críticas
- Nunca inventar informações. Lacuna → `[PENDENTE: descrever o que falta]`
- Linguagem formal, objetiva, institucional e culturalmente adequada
- Observações internas separadas do texto final de submissão
- Primeiro entregar documento preenchido, depois listar perguntas pendentes
- Não começar fazendo perguntas (exceto se material vazio/ilegível)

## Passo a Passo

### Passo 1 — Leitura e extração primária
Identificar no texto-base: nome do projeto, linguagem cultural, cidade/território, público-alvo, atividades/produtos, quantidades, duração, empresa/proponente, valor, contrapartidas, acessibilidade, democratização.

### Passo 2 — Classificação por campo
Distribuir trechos nas seções corretas do modelo. Separar: conteúdo narrativo final, conteúdo técnico, observações internas, pendências.

### Passo 3 — Preenchimento técnico
Preencher usando modelo mestre, exemplos-modelo e boilerplates. Garantir consistência entre resumo, objetivo geral, objetivos específicos, justificativa, acessibilidade e democratização.

### Passo 4 — Aplicação de boilerplates
- **Reutilizar** quando: trecho jurídico-institucional, acessibilidade padrão por produto, democratização com fórmula conhecida
- **Adaptar** quando: mudar produto, público, cidade, quantidade, formato
- **Escrever do zero** quando: argumento conceitual singular, linguagem/formato muito específico

### Passo 5 — Sinalização de lacunas
Marcar `[PENDENTE: ...]` no campo + bloco final de pendências.

### Passo 6 — Documento final
Gerar documento com todas as seções preenchidas.

### Passo 7 — Perguntas pendentes
Listar perguntas objetivas para completar lacunas.

## Estrutura do Documento (4 camadas)

### Camada 1 — Identificação
1. Nome do projeto
2. Número da proposta
3. Empresa / proponente
4. Cidade / abrangência
5. Valor do projeto

### Camada 2 — Conteúdo técnico
6. Resumo do projeto
7. Objetivo geral
8. Objetivos específicos
9. Justificativa (contexto + relevância + benefício público + enquadramento legal)
10. Enquadramento legal (Lei nº 8.313/1991)
11. Acessibilidade (física, comunicacional, conteúdo)
12. Democratização de acesso (gratuidade + medidas complementares)

### Camada 3 — Módulos complementares
13. Etapas de trabalho
14. Ficha técnica
15. Sinopse / conceito central
16. Especificação técnica
17. Descrição da atividade
18. Plano pedagógico
19. Texto / roteiro
20. Proposta museográfica / expográfica

### Camada 4 — Controle interno (não exportar para submissão)
21. Observações internas
22. Pendências
23. Responsável / status operacional

## Campos Mínimos Obrigatórios
Nome, empresa, cidade, valor, resumo, objetivo geral, objetivos específicos, justificativa, acessibilidade, democratização de acesso.

## Boilerplates Disponíveis
- Enquadramento legal (curto, médio, expandido por tipo de produto)
- Acessibilidade por produto (oficinas, palestras, exposições, espetáculos, virtual)
- Democratização por cenário (gratuidade, + formativo, + digital, combinado)
- Resumo, objetivo geral e objetivos específicos (por tipo de produto)
- Justificativa (foco formativo, territorial, temático)

## Output Esperado
Documento estruturado do projeto completo + lista de perguntas pendentes.

## Checklist de Qualidade
- [ ] Campos mínimos obrigatórios preenchidos
- [ ] Resumo explica claramente o projeto
- [ ] Objetivo geral não é cópia do resumo
- [ ] Objetivos específicos são mensuráveis
- [ ] Justificativa sustenta relevância cultural e pública
- [ ] Enquadramento legal adequado ao tipo de produto
- [ ] Acessibilidade com medidas concretas
- [ ] Democratização clara e concreta
- [ ] Observações internas separadas do texto final
- [ ] Pendências sinalizadas com `[PENDENTE: ...]`
