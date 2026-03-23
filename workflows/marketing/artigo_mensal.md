# Artigo Mensal — NTICS Projetos

> Compila os 4 roteiros/temas semanais em um artigo profissional para patrocinadores e publico B2B, posicionando a NTICS como guia estrategico em ESG.

---

## Contexto da Marca

Antes de comecar, leia:

1. `brand-book/02-identidade-verbal/tom-de-voz.md` — secoes 3.3 (Blog: 55% formal, 70% inspiracao) e 3.2 (Propostas B2B: 80% formal, 85% dados)
2. `brand-book/02-identidade-verbal/mensagens-chave.md` — elevator pitches, manifesto, proof points
3. `brand-book/data/brand-data.yaml` — metricas completas, credenciais, projetos
4. `brand-squad/tasks/create-brand-story.md` — framework StoryBrand SB7

---

## Inputs do Usuario

| Campo | Tipo | Obrigatorio | Descricao |
|-------|------|-------------|-----------|
| `roteiros_semanais` | string | Sim | Os 4 roteiros de video ou resumos dos temas semanais |
| `tema_mensal` | string | Sim | Tema central do mes |
| `patrocinador` | string | Nao | Nome do patrocinador (se aplicavel) |
| `links_videos` | string | Nao | URLs dos videos publicados para embedding |
| `dados_adicionais` | string | Nao | Metricas ou resultados extras para incluir |

---

## Execucao

### Fase 1: Extrair o Fio Narrativo

1. Analisar os 4 roteiros para encontrar a progressao logica
2. Usar o framework **ABT** do storytelling squad (`storytelling/tasks/build-narrative.md`):
   - **AND:** O contexto do tema (semana 1)
   - **BUT:** Os desafios e equivocos (semana 2)
   - **THEREFORE:** As solucoes e cases (semanas 3-4)
3. O artigo nao e 4 textos colados — e uma narrativa unica que INTEGRA os 4 temas

### Fase 2: Posicionamento StoryBrand

Usar o framework StoryBrand (`brand-squad/tasks/create-brand-story.md`):

- **Heroi:** O patrocinador / empresa leitora (nao a NTICS)
- **Problema:** A dificuldade do heroi com o tema ESG/CSR
- **Guia:** A NTICS (autoridade + empatia)
- **Plano:** O que a NTICS propoe / como o tema se resolve
- **Acao:** CTA consultivo
- **Sucesso:** O que muda quando o heroi age
- **Fracasso:** O custo de nao agir (sutil, nao ameacador)

### Fase 3: Escrita com Voz Dupla

O artigo tem 2 tons:

**Resumo Executivo (topo):**
- Tom de Proposta Comercial: 80% formal, 75% tecnico, 85% dados
- 2-3 paragrafos densos, orientados a resultado
- Para o decisor que le rapido

**Corpo do Artigo:**
- Tom de Blog/Conteudo Educativo: 55% formal, 60% tecnico, 70% inspiracao
- Tom de quem ensina com generosidade (arquetipo Sage)
- Aberturas com pergunta ou cenario
- Analogias do cotidiano
- Dados como suporte, nao protagonistas

### Fase 4: Integracao dos Videos

- Para cada secao, referenciar o video correspondente
- Se links disponiveis, incluir como CTA embedded
- Se nao, indicar placeholder para link

### Fase 5: SEO e Metadados

- Titulo SEO: maximo 60 caracteres
- Meta descricao: maximo 160 caracteres
- 5-8 palavras-chave relevantes (ESG, leis de incentivo, impacto social, etc.)

---

## Formato de Saida

```markdown
# {Titulo do Artigo}

**Tema:** {tema mensal}
**Mes/Ano:** {mes}
**Palavras:** {contagem}
**Publico-alvo:** Patrocinadores, diretores ESG, gestores de responsabilidade social

---

## Resumo Executivo

{2-3 paragrafos em tom B2B: dados, resultados, valor estrategico. Para o decisor que le rapido.}

---

## Introducao

{Por que este tema importa agora. Hook com dado ou cenario. Conexao com a realidade do leitor.}

## 1. {Titulo da Secao — baseado na Semana 1}

{Conteudo integrado do video/tema da semana 1}

> Assista ao video: [{titulo do video}]({link})

## 2. {Titulo da Secao — baseado na Semana 2}

{Conteudo integrado do video/tema da semana 2}

> Assista ao video: [{titulo do video}]({link})

## 3. {Titulo da Secao — baseado na Semana 3}

{Conteudo integrado}

> Assista ao video: [{titulo do video}]({link})

## 4. {Titulo da Secao — baseado na Semana 4}

{Conteudo integrado}

> Assista ao video: [{titulo do video}]({link})

## Conclusao: {Frase visionaria}

{Amarrar tudo. Visao de futuro. CTA consultivo e nao-agressivo.}

---

## Sobre a NTICS Projetos

{Boilerplate: 24 anos, 1.060+ projetos, 11,4M pessoas, NPS 88, ISO 9001, Pacto Global ONU. Extrair de brand-data.yaml.}

---

## Metadados SEO

- **Titulo SEO:** {max 60 chars}
- **Meta descricao:** {max 160 chars}
- **Palavras-chave:** {5-8 termos}
- **Tags:** {categorias}
```

---

## Checklist de Qualidade

- [ ] Os 4 temas semanais estao integrados (narrativa unica, nao 4 textos colados)
- [ ] Arco ABT coerente do inicio ao fim
- [ ] NTICS posicionada como guia (StoryBrand), nao como heroi
- [ ] Resumo executivo em tom B2B (80% formal, 85% dados)
- [ ] Corpo em tom Blog (55% formal, 70% inspiracao)
- [ ] Pelo menos 4 proof points do brand-data.yaml
- [ ] Links/referencias aos videos em cada secao
- [ ] CTA consultivo, nao vendedor
- [ ] Boilerplate NTICS atualizado
- [ ] Metadados SEO completos

---

## Conexao com Outras Skills

- Input vem de: `/roteiro-video` (os 4 roteiros semanais)
- Conteudo alimenta: `/email-marketing` (secao "Artigo Destaque")
