# Engenhoca 2.0 - Prestação de Contas Rouanet

## Objetivo
Automatizar a transferência de dados orçamentários do SALIC para o sistema de prestação de contas, substituindo o processo manual da planilha Engenhoca.

## Fluxo Atual (Manual)
1. Mayara exporta planilha orçamentária do SALIC (Excel)
2. Abre a Engenhoca (Google Sheets)
3. Duplica a aba modelo
4. Digita/copia rubricas uma a uma, ajustando cidade, valores, formatação (MAIÚSCULAS)
5. Vera registra pagamentos manualmente na planilha
6. Fórmulas do Igor calculam saldos e verificam limites

## Fluxo Novo (Engenhoca 2.0)
1. Mayara exporta planilha orçamentária do SALIC (Excel)
2. Faz upload no app Engenhoca 2.0
3. Parser automático extrai todas as rubricas
4. Mayara revisa preview e confirma import
5. Vera registra pagamentos direto no app
6. Dashboard calcula saldos e verifica limites automaticamente

## Ferramentas

### Parser SALIC (`tools/research/parse_salic_excel.py`)
- **Input:** Arquivo Excel do SALIC (grid_PlanilhaOrcamentaria_Homologada.xlsx)
- **Output:** JSON com rubricas estruturadas
- **Uso:** `python tools/research/parse_salic_excel.py --input arquivo.xlsx`
- **O que faz:**
  - Lê a hierarquia: Fonte Recurso → Produto → Etapa → UF → Município → Itens
  - Extrai: nome, unidade, quantidade, ocorrência, valor unitário, valor aprovado
  - Formata nome no padrão Engenhoca: `RUBRICA - CIDADE/UF` (MAIÚSCULAS)
  - Numera sequencialmente

### App Web (Lovable + Supabase)
- **URL:** (a definir após deploy)
- **Stack:** React + TypeScript + Tailwind + Supabase
- **Funcionalidades:**
  - Import SALIC com preview
  - Gestão de projetos
  - Registro de pagamentos
  - Dashboard de verificação de limites

## Regras de Negócio (Lei Rouanet)

| Regra | Limite | Observação |
|-------|--------|------------|
| Custos de captação | 10% do projeto | Até R$100.000 |
| Custos de divulgação | 20% do projeto | 30% para projetos até R$300k |
| Custos administrativos | 15% do projeto | |
| Fornecedor por rubrica | 50% do valor | Nenhum fornecedor pode ter mais |
| Realocação | 20% entre rubricas | Pode resultar em saldo negativo |

## Formato do SALIC (Export Excel)

Estrutura hierárquica com linhas de contexto:
```
Fonte Recurso : Incentivo Fiscal Federal
Produto : Espetáculo de Artes Cênicas
Etapa : 2 - Produção / Execução
UF : SP
Municipio : Campinas
Item | Unidade | Dias | Qtde | Ocorrência | Vl. Unitário | ... | Vl. Aprovado
Monitores | Serviço | 0 | 2 | 10 | 500 | ... | 10000
Total por município - Soma | ... | 10000
```

## Formato Engenhoca (Aba de Projeto)

```
Nº  | RUBRICA (MAIÚSCULAS)              | BENEFICIÁRIO | PAGO EM | REF | NF  | QTD | OCORR | VL.UNIT | TOTAL
1.0 | MONITORES - CAMPINAS/SP           |              |         | SVC |     | 2   | 10    | 500     | 10000
    | [beneficiário]                    | [data]       | PEDIDO  | NF  |     |     |       |         | -valor
    |                                   |              |         |     |     |     | SALDO |         | saldo
```

## Edge Cases
- Projetos com muitas cidades: rubricas duplicadas para cada cidade (normal)
- São Paulo tem mais rubricas que outras cidades (normal)
- Saldo negativo: OK quando há realocação 20%
- Produtos com nomes longos: truncar se necessário no display
- Etapa 9 (Assessoria Contábil/Jurídica): só aparece em São Paulo geralmente

## Equipe
- **Mayara Ferreira** — opera o import e preenche dados
- **Vera** — registra pagamentos e monitora saldos
- **Igor** — criou fórmulas originais (consultar para dúvidas sobre cálculos)
- **Lucas Rotta** — desenvolvedor da automação
