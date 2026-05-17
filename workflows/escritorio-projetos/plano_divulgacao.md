# Workflow: Plano de Divulgação

## Objetivo
Gerar o Plano de Divulgação completo (estratégia de comunicação + releases pré/durante/pós) a partir do TAP e do PEP.

## Quando Executar
Após aprovação do Termo de Abertura e do Perfil Estratégico do Patrocinador.

## Inputs Necessários
| Input | Fonte | Obrigatório |
|-------|-------|-------------|
| TAP (Termo de Abertura do Projeto) | Workflow `termo_abertura.md` | Sim |
| PEP (Perfil Estratégico do Patrocinador) | Workflow `perfil_estrategico.md` | Sim |
| Banco de imagens do projeto | `SecondBrain/projetos/{slug}/assets/` ou `SecondBrain/projetos-anteriores/{slug}/assets/` | Quando disponível |
| Materiais complementares (sinopses, apostilas, vídeos) | Drive / ClickUp Docs | Quando disponível |

## Regras Críticas
- Não inventar nomes, cargos, datas, metas, números, cidades, claims ou contatos
- Dado ausente → **XX** (no documento) e perguntar no chat
- Não se aplica → **N/A**
- Releases são para divulgação de impacto (linguagem jornalística), nunca "prestação de contas"
- Respeitar PEP: tom de voz, termos/claims permitidos/proibidos, prioridades ESG
- Cada mensagem-chave deve combinar 1 elemento TAP + 1 elemento PEP
- **Cada atividade do projeto deve ser listada individualmente** — nunca agrupar atividades distintas (ex: "oficinas maker + artes plásticas" deve virar 2 entradas separadas)
- Itens que são **entrega obrigatória ao MINC** devem ser marcados com `[ENTREGA MINC]` na frente

## Passo a Passo

### Passo 1 — Leitura, extração e dados institucionais
Ler TAP + PEP. Extrair e preencher imediatamente:

**1.1 — Dados do Projeto**
- Nome oficial do projeto
- Patrocinador(es)
- Proponente / realizador
- Cidades/UF de execução
- Período de execução (início — fim)
- Lei de incentivo / mecanismo de captação
- Número PRONAC / SALIC (se Rouanet)

**1.2 — Dados Institucionais** (preencher tudo que já existir, XX para o resto)
| Campo | Valor |
|-------|-------|
| Porta-voz institucional NTICS | Nome + cargo |
| Porta-voz do patrocinador | Nome + cargo |
| Porta-voz técnico/artístico | Nome + cargo |
| Assessoria de imprensa responsável | Nome + contato |
| E-mail oficial para imprensa | — |
| Telefone/WhatsApp de plantão | — |
| Site oficial do projeto | URL |
| Redes sociais do projeto | URLs |
| Hashtags oficiais | — |
| Data limite para validação do plano | — |

### Passo 2 — Inventário de atividades (uma por uma)
Listar TODAS as atividades do projeto extraídas do TAP, **cada uma em linha separada**. Montar 3 elementos:

**2.1 — Tabela-resumo de atividades** (visão geral em uma única tabela):

| # | Atividade | Formato | Público-alvo | Meta Cidade A | Meta Cidade B | Período | Classificação |
|---|-----------|---------|-------------|---------------|---------------|---------|---------------|
| 1 | [nome] | [presencial/virtual/digital] | [público] | [meta] | [meta] | [período] | Execução prática / `[ENTREGA MINC]` |

**2.2 — Descrição por atividade** (texto corrido, 2-3 frases cada):
Para cada linha da tabela, um parágrafo com: o que acontece, como funciona, qual o diferencial, materiais de apoio. Marcar `[ENTREGA MINC]` nas que são obrigação contratual.

**2.3 — Tabela de acessibilidade por atividade:**

| # | Atividade | Gratuito | LIBRAS | Audiodescrição | Monitores | Acess. Física | Outro |
|---|-----------|----------|--------|----------------|-----------|---------------|-------|
| 1 | [nome] | Sim/Não | Sim/XX/N/A | Sim/XX/N/A | Sim/— | Sim/N/A | [detalhe] |

> **Regra:** se o TAP agrupa atividades (ex: "oficinas maker e artes plásticas"), desmembrar em linhas individuais e confirmar com o usuário.

### Passo 3 — Criar estrutura do plano
Criar documento com 5 seções principais:
1. **Estratégia** (objetivo, insights, porta-vozes, guia linguagem, mensagens-chave)
2. **Atividades** (tabela-resumo + descrições + tabela de acessibilidade do Passo 2)
3. **Assessoria de Imprensa** (mídias por cidade, kit imprensa, canais extras)
4. **Releases Resumo** (tabela pré/durante/pós)
5. **Banco de Evidências e Imagens**

### Passo 4 — Preencher Seção 1 (Estratégia)
- Identificação do Projeto + Resumo
- Objetivo do plano de comunicação
- Insights (território + públicos + patrocinador + riscos + oportunidades)
- Porta-vozes autorizados (da tabela do Passo 1.2)
- Guia de linguagem (tom, termos permitidos/proibidos, claims, compliance PEP)
- Mensagens-chave:
  - Institucionais (patrocinador + proponente)
  - Por público-alvo
  - Provas / evidências numéricas
- Listar dúvidas para resolver os XX

### Passo 5 — Preencher Seções 3 e 4
- **Assessoria de Imprensa:** pesquisar veículos por cidade (Tier 1/2/3), canais extras (podcasts, universidades)
- **Releases Resumo:** tabela com momento, atividade vinculada, metodologia
  - Indicar quais atividades são `[ENTREGA MINC]` na coluna de observações
- Perguntar: "Posso seguir para a construção dos releases?"

### Passo 6 — Banco de Evidências e Imagens
**6.1 — Evidências documentais**
| Tipo | Descrição | Link |
|------|-----------|------|
| Sinopse (peça teatral) | Sinopse de "Nome da Peça" | [link] |
| Apostila | Material didático oficina X | [link] |
| Relatório anterior | Resultados edição 2024 | [link] |
| Vídeo institucional | Teaser do projeto | [link] |
| Pesquisa de impacto | Dados quali/quanti | [link] |

**6.2 — Banco de imagens**
- Buscar em `assets/projetos/{slug}/` as melhores imagens da última realização
- Organizar por atividade:
  | Atividade | Qtd fotos | Pasta/Link | Observações |
  |-----------|-----------|------------|-------------|
  | Oficina Maker | 5 | `assets/projetos/slug/oficina-maker/` | Fotos com menores: checar autorização |
  | Espetáculo X | 8 | `assets/projetos/slug/espetaculo/` | Alta resolução disponível |
- Se não existir banco organizado, criar pasta `assets/projetos/{slug}/banco-imagens/` e curar as melhores (máx 10-15 por atividade)

### Passo 7 — Gate de Validação Pré-Comunicação
**Antes de liberar qualquer peça para divulgação**, validar:

| # | Verificação | Status | Responsável |
|---|-------------|--------|-------------|
| 1 | Dados institucionais completos (sem XX remanescente) | ☐ | PMO |
| 2 | Porta-vozes confirmados e autorizados | ☐ | Coordenação |
| 3 | Claims e números verificados contra fonte oficial | ☐ | PMO |
| 4 | Compliance PEP: termos proibidos ausentes | ☐ | Comunicação |
| 5 | Acessibilidade descrita por atividade | ☐ | Produção |
| 6 | Entregas MINC sinalizadas e corretas | ☐ | PMO |
| 7 | Imagens com autorização de uso (menores → termo assinado) | ☐ | Jurídico |
| 8 | Logos do patrocinador na versão correta (manual de marca) | ☐ | Design |
| 9 | Links de evidências testados e acessíveis | ☐ | Comunicação |
| 10 | Aprovação final do patrocinador para divulgação | ☐ | Coordenação |

> Só avançar para Passo 8 (releases) após todos os itens marcados ☐→✓ ou justificados como N/A.

### Passo 8 — Construção dos Releases (após autorização + gate aprovado)
3 releases em texto final:
- **Release 01 (Pré):** anúncio + informação institucional + serviço + acessibilidade
- **Release 02 (Durante):** cobertura + personagem + 1 depoimento obrigatório + menção a recursos de acessibilidade
- **Release 03 (Pós):** dados de impacto/resultados + legado + conexão PEP + links para evidências

Cada release deve:
- Marcar atividades que são `[ENTREGA MINC]` quando mencionadas
- Incluir bloco "Serviço" com dados institucionais completos (do Passo 1.2)
- Mencionar recursos de acessibilidade disponíveis

## Output Esperado
1. Plano de Divulgação completo (estratégia + atividades detalhadas + assessoria + releases resumo)
2. Banco de evidências com links diretos
3. Banco de imagens curado por atividade
4. Gate de validação preenchido
5. 3 Releases em texto final (pré/durante/pós)

## Checklist de Qualidade
- [ ] Todas as atividades listadas individualmente (sem agrupamentos)
- [ ] Cada atividade tem descrição, metas por cidade e acessibilidade preenchidos
- [ ] Entregas MINC sinalizadas com tag `[ENTREGA MINC]`
- [ ] Dados institucionais preenchidos (porta-vozes, contatos, datas) — ou XX justificado
- [ ] Mensagens-chave combinam TAP + PEP
- [ ] Mídias pesquisadas por cidade (Tier 1/2/3)
- [ ] Claims respeitam PEP (permitidos/proibidos)
- [ ] Release 02 tem depoimento de participante
- [ ] Release 03 tem 2-4 números de impacto
- [ ] Compliance de imagem de menores verificado
- [ ] Evidências documentais com links diretos e testados
- [ ] Banco de imagens organizado por atividade em `assets/projetos/{slug}/`
- [ ] Gate de validação pré-comunicação aprovado antes dos releases
