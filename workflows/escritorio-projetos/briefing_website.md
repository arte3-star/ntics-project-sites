# Workflow: Briefing para Website do Projeto

## Objetivo
Transformar TAP + Plano de Divulgação em briefing estruturado de conteúdo para o site do projeto.

## Quando Executar
Após aprovação do Termo de Abertura e do Plano de Divulgação, quando o projeto tiver site previsto.

## Inputs Necessários
| Input | Fonte | Obrigatório |
|-------|-------|-------------|
| TAP (Termo de Abertura) | Workflow `termo_abertura.md` | Sim |
| Plano de Divulgação | Workflow `plano_divulgacao.md` | Sim |

## Regras Críticas
- Não inventar. Se a informação não estiver nos inputs, escrever **PENDENTE**
- Prioridade: Plano para descrições e atividades; TAP para links e dados oficiais
- Descrição do projeto: 3-6 linhas, linguagem externa
- Atividades: 2-4 linhas por atividade, linguagem externa, sem termos internos
- Links: manter exatamente como nos inputs (não encurtar)

## Passo a Passo

### Passo 1 — Leitura e extração
Ler TAP + Plano de Divulgação. Extrair: nome do projeto, período, cidades, atividades, descrições, links (Drive, galeria, KV, régua).

### Passo 2 — Preencher o briefing
Seguindo a estrutura:

1. **Tabela inicial:** Nome do Projeto + Período de execução
2. **Cidades do projeto:** lista de Cidades/UF participantes
3. **O que é o projeto:** descrição geral (3-6 linhas, linguagem externa)
4. **Atividades:** tabela com Nome, Descrição (2-4 linhas), Link de evidência
5. **Democratização do acesso:** como o projeto garante acesso (3-8 bullets) + links
6. **Links de mídia:** galeria de fotos, KV, régua do projeto
7. **Vídeos extras:** links de palestras/apresentações/depoimentos/making of
8. **Itens extras:** campo livre para conteúdo adicional

### Passo 3 — Validar e perguntar
Listar perguntas objetivas apenas para campos PENDENTE.

## Output Esperado
Briefing Website preenchido seguindo o modelo de 7 seções, pronto para o desenvolvedor do site.

## Checklist de Qualidade
- [ ] Nome e período corretos
- [ ] Cidades listadas
- [ ] Descrição geral em linguagem externa (3-6 linhas)
- [ ] Cada atividade descrita (2-4 linhas)
- [ ] Links de mídia preenchidos ou marcados PENDENTE
- [ ] Democratização do acesso descrita
- [ ] Sem termos internos/operacionais no texto
