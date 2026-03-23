# Workflow: Termo de Abertura (TA)

## Objetivo
Preencher o Termo de Abertura NTICS passo a passo, seção por seção, a partir de uma apresentação/briefing do projeto.

## Quando Executar
Novo projeto vendido que precisa de estruturação formal antes da execução.

## Inputs Necessários
| Input | Fonte | Obrigatório |
|-------|-------|-------------|
| Apresentação/briefing do projeto | Cliente ou comercial (PPTX, PDF, doc, texto) | Sim |
| Informações complementares | Reuniões, e-mails, alinhamentos | Quando disponível |

## Documentos de Referência
- `workflows/knowledge/tap_template.md` — Modelo oficial do TA (estrutura e campos)
- `workflows/knowledge/termo_abertura/anexo1_licoes_aprendidas.md` — Lições aprendidas por tipo de projeto
- `workflows/knowledge/termo_abertura/anexo2_mapa_stakeholders.md` — Mapa padrão de stakeholders
- `workflows/knowledge/termo_abertura/anexo4_indicadores_camada.md` — KPIs gerais (18 indicadores)
- `workflows/knowledge/termo_abertura/anexo4.1_regras_indicadores.md` — Regras de indicadores (3 camadas)
- `workflows/knowledge/termo_abertura/anexo5_riscos_mitigacao.md` — Matriz de riscos por tipologia
- `workflows/knowledge/termo_abertura/anexo6_fornecedores_equipe.md` — Fornecedores, funções e prazos

## Regras Críticas
- O modelo do TA é a ÚNICA fonte de estrutura, numeração, títulos e ordem
- Nunca inventar dados críticos (nomes, cargos, datas, valores, compromissos legais)
- Quando faltar informação: manter [Inserir] e registrar pendência
- Sugestões marcadas como "Sugestão (precisa validação)"
- Fontes externas marcadas como "Referência externa (precisa validação)"
- Proibido gerar o TA completo de uma vez — construir seção por seção

## Passo a Passo

### Passo 1 — Leitura e confirmação de entendimento
1. Ler integralmente o material enviado
2. Apresentar resumo estruturado: tipo, objetivos, eixos, territórios, público, natureza
3. Perguntar: "Este entendimento está correto antes de avançarmos?"
4. NÃO preencher nada nesta fase

### Passo 2 — Criação do documento (espelho do modelo)
1. Após confirmação, criar documento seguindo exatamente o modelo do TA
2. Mesmas seções, mesma numeração, mesma ordem
3. Campos inicialmente vazios ou com [Inserir]

### Passo 3 — Preenchimento guiado (seção por seção)
1. Preencher UMA seção por vez, na ordem do Termo
2. Para cada seção:
   - Preencher com base na apresentação e nos anexos
   - Marcar: [FONTE: APRESENTAÇÃO], [FONTE: ANEXO], ou "Sugestão (precisa validação)"
   - **Seção 2.4 (Premissas):** cruzar com Anexo 1 (lições aprendidas da tipologia)
   - **Seção 6 (Indicadores):** aplicar Anexo 4/4.1 — Camada 1 (gerais, obrigatórios), Camada 2 (específicos do escopo), Camada 3 (por ODS)
   - **Seção 7 (Stakeholders):** usar Anexo 2 como base, adaptar ao projeto
   - **Riscos:** usar Anexo 5 conforme tipologia (Caminhão, Robótica, Educacional, PEC, Culinária)
   - **Time/Fornecedores:** usar Anexo 6 para estrutura e prazos de confirmação
3. Após cada seção: "Podemos validar esta seção e seguir para a próxima?"
4. Só avançar após validação

### Passo 4 — Consolidação
1. Listar todas as pendências
2. Gerar perguntas objetivas para cada lacuna

## Seções do TA (ordem obrigatória)
0. Identificação do Projeto
1. Links Oficiais e Repositórios
2. Cliente, Patrocinador e Arranjo Institucional (contexto, metas, premissas)
3. Escopo (o que está dentro + devolutivas governamentais)
4. Engajamento (local, atividades, voluntariado, território sensível)
5. Comunicação (materiais gráficos + vídeos)
6. Indicadores (gerais + quantitativos + específicos + ODS)
7. Stakeholders (time + mapa)
8. Fases e Cronograma Macro (marcos críticos)

## Edge Cases
| Situação | Ação |
|----------|------|
| Apresentação incompleta | Preencher o máximo, [Inserir] nas lacunas, listar pendências |
| Múltiplas cidades | Criar tabela de metas por cidade na seção 2.3 |
| ODS não definidos | Perguntar quais ODS antes de preencher Camada 3 |
| Tipologia sem cobertura no Anexo 5 | Usar riscos mais próximos, marcar como sugestão |

## Output Esperado
Termo de Abertura completo em markdown, preenchido seção por seção, com fontes rastreáveis e pendências listadas.

## Checklist de Qualidade
- [ ] Todas as 9 seções (0-8) preenchidas ou com [Inserir] justificado
- [ ] Indicadores das 3 camadas contemplados
- [ ] Riscos identificados conforme tipologia
- [ ] Stakeholders com estratégia e cadência
- [ ] Marcos críticos com datas-alvo
- [ ] Premissas cruzadas com lições aprendidas (Anexo 1)
- [ ] Pendências listadas com perguntas objetivas
