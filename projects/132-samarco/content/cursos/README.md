# Cursos de Qualificação Profissional NTICS, Programa Estação Samarco

**Versão 1.0 da documentação completa, abril de 2026**

Esta pasta consolida toda a documentação pedagógica, operacional e tecnológica dos cursos de qualificação profissional da NTICS Projetos, com aplicação inicial no Programa Estação Samarco, Territórios do Futuro.

A versão 1.0 está completa e pronta para revisão. Cada documento é independente e pode ser aprovado, ajustado ou substituído isoladamente sem afetar os demais.

---

## Estrutura

```
cursos/
├── README.md                           # este arquivo
├── 00-projeto-pedagogico-v1.md         # documento-mãe (PPP)
├── anexos/                             # 10 anexos institucionais
│   ├── anexo-i-matriz-curricular.md
│   ├── anexo-ii-ementa-formacao-inicial.md
│   ├── anexo-iii-ementa-culinaria.md
│   ├── anexo-iv-ementa-beleza.md
│   ├── anexo-v-planos-aula-presencial.md
│   ├── anexo-vi-conteudos-digitais.md
│   ├── anexo-vii-avaliacao-pratica.md
│   ├── anexo-viii-regulamento.md
│   ├── anexo-ix-modelo-certificado.md
│   └── anexo-x-relatorio-execucao-turma.md
├── aulas/                              # planos de aula presencial detalhados
│   ├── inicial/
│   │   └── encontro-00-empreendedorismo-ia.md
│   ├── culinaria/
│   │   ├── modulo-1-fundamentos.md
│   │   ├── modulo-2-organizacao-cardapio.md
│   │   ├── modulo-3-identidade-aproveitamento.md
│   │   ├── modulo-4-padronizacao-inclusivos.md
│   │   └── modulo-5-precificacao-venda.md
│   └── beleza/
│       ├── modulo-1-fundamentos-higiene.md
│       ├── modulo-2-manicure-pedicure.md
│       ├── modulo-3-escova-penteado.md
│       ├── modulo-4-maquiagem.md
│       └── modulo-5-atendimento-divulgacao.md
├── digital/                            # roteiros dos módulos digitais
│   ├── d1-boas-vindas-plataforma.md
│   ├── d2-postura-atendimento.md
│   ├── d3-empreendedorismo-precificacao.md
│   ├── d4-ia-vendas-divulgacao.md
│   ├── d5-whatsapp-redes-sociais.md
│   ├── d6-aprofundamento-culinaria.md
│   ├── d6-aprofundamento-beleza.md
│   ├── d7-renda-territorio.md
│   └── d8-projeto-aplicacao.md
├── plataforma-prototipo/               # protótipo HTML da plataforma + brief Lovable
│   ├── index.html
│   ├── login.html
│   ├── dashboard.html
│   ├── modulo.html
│   ├── certificado-validar.html
│   └── lovable-brief.md
└── apoio/                              # documentos operacionais
    ├── formulario-inscricao.md
    ├── termo-participacao-lgpd.md
    ├── termo-uso-imagem.md
    └── checklist-execucao-turma.md
```

---

## Como navegar

### Para entender a proposta
Leia primeiro **[00-projeto-pedagogico-v1.md](00-projeto-pedagogico-v1.md)**. É o documento-mãe.

### Para conferir a estrutura curricular
**[Anexo I, Matriz Curricular](anexos/anexo-i-matriz-curricular.md)**.

### Para ver o conteúdo de cada curso
- Trilha Inicial: **[Anexo II](anexos/anexo-ii-ementa-formacao-inicial.md)**.
- Culinária: **[Anexo III](anexos/anexo-iii-ementa-culinaria.md)**.
- Beleza: **[Anexo IV](anexos/anexo-iv-ementa-beleza.md)**.

### Para usar como facilitador em sala
Os planos de aula em **[aulas/](aulas/)** são auto-suficientes. Cada um traz materiais, insumos, roteiro de fala, atividade prática e critérios de observação.

### Para entender e produzir os conteúdos digitais
Os roteiros em **[digital/](digital/)** detalham vídeos, atividades e materiais a serem produzidos para a plataforma.

### Para construir a plataforma
- Protótipo visual: **[plataforma-prototipo/index.html](plataforma-prototipo/index.html)** (abra em qualquer navegador).
- Brief técnico: **[plataforma-prototipo/lovable-brief.md](plataforma-prototipo/lovable-brief.md)**.

### Para operação em campo
- **[Anexo VIII, Regulamento](anexos/anexo-viii-regulamento.md)** define as regras.
- **[apoio/formulario-inscricao.md](apoio/formulario-inscricao.md)** é o formulário padrão.
- **[apoio/checklist-execucao-turma.md](apoio/checklist-execucao-turma.md)** é o passo a passo operacional.

---

## Decisões consolidadas que sustentam toda a versão 1.0

1. **Cursos independentes**, não trilhas de um único curso. Nomenclatura formal: *Curso de Qualificação Profissional em Culinária* e *Curso de Qualificação Profissional em Beleza*.
2. **50 horas cada**, modalidade híbrida: 28h presencial + 22h digital.
3. **Estrutura presencial:** 4h Formação Inicial Comum (Trilha Inicial em Empreendedorismo & IA) + 24h prática específica (5 módulos de 5h, 5h, 5h, 5h, 4h).
4. **Estrutura digital:** 8 módulos. 7 comuns + 1 específico do curso (D6).
5. **Trilha Inicial autônoma:** ofertável também como componente independente, com certificado próprio de 4h.
6. **Avaliação:** por aptidão (Apto, Apto com orientação, Não apto), sem nota numérica.
7. **Certificação:** própria NTICS, com validação digital. Caráter de qualificação profissional livre, não MEC.
8. **Plataforma:** Lovable (canônico do projeto), com protótipo HTML neste repositório como referência visual.
9. **Cuidado editorial em comunidades atingidas** (Bento Rodrigues, Paracatu, Santa Rita): tom positivo, voltado ao futuro, sem revitimização.
10. **Logo Samarco soberana**, NTICS como realização, sem régua MinC.
11. **Vocabulário institucional NTICS** aplicado em todos os documentos (comunidades, programa, transformação, construímos, investimento social).
12. **Sem travessão (em-dash)** em todo o conteúdo publicado, conforme regra hard do brand book NTICS.

---

## O que ainda depende de decisão externa para finalização visual

| Item | Status | Dependência |
|---|---|---|
| Arte final dos certificados | Texto institucional aprovado nesta versão; arte visual prevista nos deliverables C1 e C2 | Envio do KV oficial Samarco e manual de marca pela patrocinadora |
| Plataforma real | Protótipo HTML pronto + brief Lovable detalhado | Decisão final de stack (Lovable confirmado em PLAYBOOK do projeto) e início da construção |
| Vídeos da plataforma | Roteiros completos disponíveis | Produção audiovisual a contratar |
| Listas de fornecedores e preços de mercado | Referências citadas em cada plano de aula | Pesquisa de mercado por cidade no momento da execução |
| Nome do responsável técnico-pedagógico no PPP | Placeholder em vigor | Definição interna NTICS |

---

## Fluxo de aprovação sugerido

1. Leitura interna NTICS (Bruna, Lucas, Abilio).
2. Revisão pedagógica (consultora Pâmela Cardinalli para Culinária; consultora a definir para Beleza).
3. Aprovação institucional NTICS.
4. Apresentação à Samarco para alinhamento institucional.
5. Aprovação final.
6. Construção da plataforma (Lovable).
7. Produção dos vídeos.
8. Início da primeira turma (Brumal, 25 de maio de 2026, conforme cronograma do projeto).

---

## Como atualizar essa documentação

Esta é uma documentação viva. Quando houver ajuste:

1. Identifique o documento específico a alterar (PPP, anexo ou plano de aula).
2. Atualize o documento, mantendo a versão atual ou criando v1.1, v1.2, etc.
3. Registre a mudança em commit do repositório.
4. Comunique à coordenação NTICS para que a base operacional seja atualizada em conjunto.

A versão da plataforma e dos vídeos segue o ciclo próprio de produção, com versionamento independente.

---

## Aplicação além do Programa Estação Samarco

O Projeto Pedagógico foi escrito com flexibilidade para que possa ser usado também por outros programas e patrocinadores da NTICS. Para cada nova aplicação:

- Substitua referências específicas a "Programa Estação Samarco" pelo novo programa.
- Ajuste a regra de logo (manter Samarco soberano apenas onde for o caso).
- Mantenha integralmente a estrutura curricular, regulamentação e modelos de avaliação.
- Adapte a tabela de preços de referência conforme a região.

---

## Créditos

**Construção da documentação:** equipe NTICS Projetos com apoio de IA generativa.
**Base pedagógica:** equipe pedagógica do Programa Estação Samarco e proposta detalhada da consultora Pâmela Cardinalli (Estação Sabores, módulos de Culinária).
**Revisão visual:** equipe de design NTICS (deliverables A, B e C do projeto).
**Coordenação institucional:** Bruna Seibel (gestão de projeto), Abilio Martins (atendimento e operação), Lucas Rotta (comunicação).

---

*Versão 1.0, finalizada em abril de 2026. Pronta para revisão e aprovação.*
