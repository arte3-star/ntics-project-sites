# Workflow: Email de Calendário de Postagens (Redes Sociais)

## Objetivo
Gerar email para o cliente/patrocinador com calendário de postagens do projeto (carrosséis, reels, vídeo case) + descrição curta de cada peça + regras de entrega/aprovação, a partir de TAP, Plano de Divulgação, Releases e tasks ClickUp.

## Quando Executar
- Antes do início da fase Pré do projeto, quando a comunicação estiver pronta para alinhar o calendário com o cliente.
- Reenviar quando houver mudança relevante (novas datas, nova fase, reestruturação de peças).
- Adaptar para envio periódico (ex.: atualização semanal/mensal).

## Inputs Necessários

| Input | Fonte | Obrigatório |
|-------|-------|-------------|
| Código(s) do projeto | Usuário | Sim |
| TAP (Termo de Abertura) | `SecondBrain/projetos/{slug}/tap.md` ou ClickUp Doc | Sim |
| Plano de Divulgação | ClickUp Doc, dentro do escopo do projeto | Sim |
| Releases Pré/Durante/Pós | ClickUp Doc, sub-página do Plano de Divulgação | Recomendado |
| Datas das postagens | ClickUp list do projeto (tasks `Postar ...`) | Opcional (deixar `{{data}}` se vazio) |
| Regras específicas do patrocinador | Plano de Divulgação + atas de comunicação externa | Sim |

## Decisões de Formato

### 1 email ou N emails?
- **1 cliente, N projetos** (ex.: GRU Airport com 125 + 127): **1 email unificado com N tabelas separadas** (uma por projeto).
- **N clientes, 1 projeto com cotas independentes** (ex.: 120 Statkraft + Porto Itapoá): **N emails, 1 por patrocinador**.
- **1 cliente, 1 projeto:** 1 email simples.

### Tabela de Calendário
- Colunas: `Data | Formato` (para projetos padrão).
- Colunas: `Data | Projeto | Formato` (apenas quando cliente pediu consolidação, senão tabelas separadas).
- Colunas: `Data | Formato | Quantidade` (projetos com muitas peças por cidade, ex.: Samarco 132).
- Se cliente pediu tabelas separadas por projeto, usar headers H3 (`### Nome do Projeto`).

### Datas
- Formato padrão: `D/mês.` (ex.: `27/abr.`, `4/mai.`, `18/ago.`).
- Ordenar cronologicamente dentro de cada tabela.
- Se tasks ClickUp duplicadas (ex.: cota GRU + cota SOTREQ no mesmo projeto), pegar as tasks com sufixo explícito (`GRU`, `SOTREQ`) quando existir, ou escolher pelo cronograma de execução (próxima ao Durante do patrocinador específico).
- Vazio → `{{data}}` como placeholder.

## Estrutura do Email (base)

```
Assunto: Calendário de Postagens, <Nome do Projeto> (<Patrocinador>)

Bom dia,

Obrigado pelo alinhamento de marca, as diretrizes já serão aplicadas em todos os materiais.

Segue o calendário de postagens e as propostas de estrutura para carrosséis e vídeos
do projeto <nome> em <cidade/território>, com <meta> <beneficiários/visitantes>.

## Calendário de Postagens
Datas flexíveis, todas em collab entre NTICS e <Patrocinador>. Nos avisem se houver restrições.

<tabela(s) de datas>

## Reels (60s, vertical)
- Pré-projeto: <descrição curta, 1 linha>
- Durante #1, <tema>: <descrição curta>
- Durante #2, <tema>: <descrição curta>
- Durante #3, <tema>: <descrição curta>
(adicionar mais Durante se o projeto tiver)

## Vídeo Case (2 a 3 min, horizontal)
Fechamento institucional com <foco específico do projeto>.

## Carrosséis
Três carrosséis, 7 páginas cada.
- Pré-projeto, "O que vem aí": <descrição curta>
- Durante, "Acontecendo agora": <descrição curta>
- Pós, "O que fica": <descrição curta>

## Entrega dos Materiais
Como as peças da fase Durante são produzidas com material captado em campo, conseguimos
entregar para aprovação com <prazo> de antecedência.

<Seções condicionais conforme regras do patrocinador>

Seguimos à disposição para ajustes.

Att,
```

## Seções Condicionais por Patrocinador

### Identidade visual (quando aplicável)
Usar quando houver regra crítica de marca diferente do padrão. Exemplos:
- **Statkraft:** usar lettering "Complexo Santa Eugênia" no lugar da logo.
- **Samarco:** logo Samarco soberana em todas as peças, identidade do projeto como acessório.

### Nota sobre outro proponente
Quando nas mesmas cidades houver projeto com proponente diferente (ex.: 116 Cultura Robótica + Hábitos Saudáveis), incluir nota no fim:

> Nas mesmas cidades acontece também a **<nome peça>**, com **outro proponente (<razão social>)** e PRONAC separado (<número>). A divulgação dessa peça será feita em peças independentes, sem mistura.

### Diretrizes de Comunicação (projetos corporativos/sensíveis)
Quando projeto tem território sensível (Samarco rompimento, GRU Malvinas), adicionar bloco:

> ## Diretrizes de Comunicação
> - Tom editorial positivo, voltado à <foco>, sem menções a <temas sensíveis>.
> - Depoimentos sempre com termo de consentimento (imagem e som).
> - Aprovação dupla obrigatória (<fluxo>).

### Anexos (vídeos prontos)
Quando vídeo pré-projeto já estiver editado, anexar no final:

> Também coloco abaixo o Vídeo <tipo> que já editamos, caso precisem de algum ajuste estamos à disposição.
>
> 📎 Vídeo <tipo>, <Nome do Projeto> (<Patrocinador>).mp4

## Regras Críticas

### Pontuação (regra NTICS global)
- **NUNCA usar travessão em-dash `—`** em nada que vai para o cliente. Trocar por `,`, `.`, ou reescrever.
- Vale para todo o email, inclusive sub-títulos e listas.

### Descrições dos Reels/Carrosséis
- **Simples e diretas**, 1 linha por peça. Evitar adjetivos excessivos.
- Puxar do **Release** (não do TAP) sempre que possível, porque Release já é linguagem externa.
- Se projeto não tem Release pronto, usar seção "Atividades" do Plano de Divulgação ou "Descrição por Atividade".

### Quantidade de Durantes
- Projetos padrão (escolares, oficinas únicas): 3 Durantes.
- Projetos com múltiplas frentes paralelas (ex.: Gastronomia = exposição + oficinas + workshops): 4 a 6 Durantes, um por frente.
- Projetos corporativos multi-cidade (ex.: Samarco): 1 Durante por cidade (pode ser 12+).

### Prazo de Entrega Padrão
- 3 dias antes da postagem (padrão NTICS).
- Samarco: 48h ideal (a cliente define).
- GRU Airport: 5-7 dias (incluindo aspas) — mencionado se for edição inicial.

## Passo a Passo

### Passo 1, Identificar escopo
- Ler README + TAP do(s) projeto(s) em `SecondBrain/projetos/{slug}/`.
- Decidir formato (1 email vs N emails).
- Listar patrocinador(es), território(s), meta(s), fases Pré/Durante/Pós.

### Passo 2, Puxar Plano de Divulgação + Releases do ClickUp
- `clickup_list_document_pages` no doc principal do projeto.
- Identificar páginas: `PLANO DE DIVULGAÇÃO`, `RELEASES`, `CARROSSEIS` (quando existir).
- `clickup_get_document_pages` nas páginas relevantes.
- Ler com foco em: mensagens-chave, descrição por atividade, termos recomendados/proibidos, regras de governança.

### Passo 3, Puxar datas do ClickUp (opcional)
- Se user mandou screenshots: extrair dados direto das imagens.
- Se não: `clickup_search` por `Postar` na list do projeto + examinar tasks.
- Se duplicados (projeto com 2 cotas), filtrar pelo sufixo (`GRU`/`SOTREQ`) ou pela proximidade com execução.
- Se não houver datas: usar `{{data}}` em todas as linhas da tabela.

### Passo 4, Montar o email
- Seguir estrutura base.
- Gerar descrições simples dos Reels a partir dos Releases + Plano.
- Gerar descrições simples dos 3 Carrosséis a partir do Plano de Divulgação.
- Adicionar seções condicionais conforme regras do patrocinador.
- Validar: nenhum travessão `—`, descrições de 1 linha, datas ordenadas cronologicamente.

### Passo 5, Confirmar com Lucas pontos em aberto
Sempre listar no final do email (em bloco separado) as dúvidas de:
- Ambiguidade de datas (duplicatas no ClickUp).
- Gaps suspeitos entre postagens.
- Particularidades do patrocinador que precisam confirmação.

## Exemplos de Projetos Processados (referência)

| Projeto | Cliente | Nota |
|---------|---------|------|
| 119 | Sylvamo | Template base original (Mogi Guaçu + Guatapará) |
| 125 + 127 | GRU Airport | Email unificado, 2 tabelas separadas |
| 120 (cota Porto Itapoá) | Porto Itapoá | Email independente |
| 120 (cota Statkraft) | Statkraft | Lettering "Complexo Santa Eugênia" |
| 124 | Compagas | Exposição como legado (doação município) |
| 132 | Samarco | Corporativo (não Rouanet), 12 cidades, marca soberana |
| 116 | Áster | Nota de outro proponente (Hábitos Saudáveis) |

## Output Esperado
Email pronto para copiar e enviar, com:
- Assunto
- Tabela(s) de calendário (com datas ou `{{data}}`)
- Descrições curtas de Reels e Carrosséis
- Seções condicionais do patrocinador
- Bloco de dúvidas pendentes (se houver)

## Checklist de Qualidade
- [ ] Nenhum travessão em-dash `—` no texto
- [ ] Descrições de reels/carrosséis em 1 linha
- [ ] Tabela(s) ordenada(s) cronologicamente
- [ ] Sufixo da cota correto quando patrocinador tem múltiplas (GRU/SOTREQ/etc)
- [ ] Seção condicional incluída quando aplicável (marca Statkraft, Samarco, etc)
- [ ] Nota de outro proponente quando existir (ex.: 116 Hábitos Saudáveis)
- [ ] Vídeo pré anexado quando já editado
- [ ] Assunto claro com nome do projeto + patrocinador
- [ ] Bloco de dúvidas pendentes ao final quando houver ambiguidade
