# Elementos Visuais — NTICS Projetos
> Brand Book v2.0 | Atualizado: Marco 2026

---

## Visao Geral

A linguagem visual da NTICS Projetos e construida sobre **blocos geometricos coloridos** e **engrenagens decorativas** — elementos ja presentes no Relatorio de Sustentabilidade 2023/2024 e agora formalizados e sistematizados neste Brand Book.

Esses elementos traduzem visualmente os valores da marca: impacto social (blocos que constroem), inovacao (engrenagens que movem) e diversidade (cores vibrantes que coexistem).

---

## Blocos Geometricos

### Forma Base
- **Retangulos arredondados** com border-radius entre 8px e 24px
- Cantos arredondados transmitem acolhimento e acessibilidade
- Evitar retangulos com cantos vivos (transmitem rigidez)

### Composicoes Assimetricas
Os blocos devem ser posicionados de forma **assimetrica** para criar dinamismo:

```
+------------------+
|  Bloco Grande    |      +----------+
|  (Verde)         |      | Bloco    |
|                  |      | (Azul)   |
+------------------+      +----------+
         +----------+
         | Bloco    |
         | (Rosa)   |
         +----------+
```

#### Regras de Composicao
- Usar **2 a 4 blocos** por composicao
- Tamanhos variados: 1 bloco dominante + blocos menores de apoio
- Permitir **sobreposicao parcial** entre blocos (10% a 30% de area)
- Manter pelo menos **1 bloco com respiro** (sem sobreposicao)
- Alinhar pelo menos uma borda de cada bloco a outro elemento ou ao grid

### Sobreposicao e Camadas (Overlay)
- Blocos sobrepostos devem usar **opacidade entre 80% e 95%**
- Na sobreposicao, o bloco da frente deve ter cor diferente do de tras
- A sobreposicao cria uma terceira cor — verificar se o resultado e harmonico
- Blocos sobre fotos: usar opacidade de **70% a 85%** para manter a foto visivel

### Espacamento entre Blocos
- **Sem sobreposicao:** gap minimo de 16px (1rem)
- **Com sobreposicao:** sobreposicao maxima de 30% da area do bloco menor
- **Blocos flutuantes:** manter pelo menos 24px de distancia das bordas da composicao

### Cores dos Blocos
- Usar cores da paleta primaria e secundaria
- Cada composicao deve ter **no maximo 3 cores** de blocos
- O bloco dominante deve usar uma cor primaria
- Blocos menores podem usar cores secundarias

---

## Engrenagens Decorativas

As engrenagens derivam do logo (lampada + engrenagens) e funcionam como assinatura visual dispersa.

### Estilos de Engrenagem

#### Engrenagem Branca (principal)
- Cor: Branco #FFFFFF
- Uso: sobre fundos coloridos (Verde, Azul Petroleo, Rosa, etc.)
- Opacidade: 100% ou sutil a 60-80%

#### Engrenagem em Cor com Baixa Opacidade
- Cor: qualquer primaria ou secundaria
- Opacidade: 10% a 20%
- Uso: sobre fundos brancos ou Cinza Claro como textura sutil

#### Engrenagem Outline (contorno)
- Apenas o contorno, sem preenchimento
- Espessura: 2px a 4px
- Uso: composicoes mais leves, backgrounds de secoes

### Tamanhos
| Tamanho | Dimensao Aproximada | Uso |
|---------|-------------------|-----|
| Grande | 120px — 200px | Cantos de pagina, elemento decorativo principal |
| Medio | 60px — 100px | Complemento, agrupamento |
| Pequeno | 24px — 48px | Detalhes, padrao repetido |

### Regras de Posicionamento
- Posicionar nas **bordas e cantos** da composicao
- Permitir que engrenagens sejam **cortadas pela borda** (parcialmente visiveis)
- Agrupar 2-3 engrenagens de tamanhos diferentes para criar conjuntos
- **Nunca** centralizar engrenagens na composicao (devem ser perifericas)
- **Nunca** posicionar sobre texto ou conteudo principal
- Maximo de **5 engrenagens** por composicao

### Rotacao
- Engrenagens decorativas podem ser rotacionadas livremente
- Variar angulos entre engrenagens do mesmo conjunto para naturalidade
- Engrenagens adjacentes devem ter rotacoes diferentes

---

## Icones

### Estilo de Icone
- **Estilo:** line icons (contorno, nao preenchidos)
- **Espessura do traco:** 1.5px a 2px
- **Cantos:** arredondados, consistente com os blocos
- **Tamanho padrao:** 24px x 24px (interface), 48px x 48px (destaque)
- **Cor:** Grafite (#2D2D2D) em fundos claros, Branco (#FFFFFF) em fundos escuros

### Temas de Icones
Icones customizados para os temas de sustentabilidade da NTICS:
- Meio ambiente (folhas, agua, energia)
- Educacao (livros, lampada, graduacao)
- Tecnologia (circuitos, devices, cloud)
- Comunidade (pessoas, maos, coracoes)
- Governanca (balanca, escudo, graficos)

### Icones dos ODS
- Usar os **icones oficiais da ONU** para os Objetivos de Desenvolvimento Sustentavel
- Manter as cores originais dos ODS quando usados isoladamente
- Quando integrados a composicoes NTICS, podem receber tratamento monocromatico

---

## Padroes e Texturas

### Padrao de Engrenagens
- Grid de engrenagens pequenas (24px) em opacidade 5-10%
- Usar como textura de fundo em secoes inteiras
- Funciona melhor sobre Branco ou Cinza Claro

### Padrao de Pontos (Dots)
- Grid de circulos pequenos (4px) com spacing de 24px
- Opacidade: 10-15%
- Cor: Cinza Medio ou cor primaria da secao
- Uso: backgrounds de cards, secoes de dados

### Padrao de Linhas Diagonais
- Linhas finas (1px) a 45 graus
- Spacing: 16px entre linhas
- Opacidade: 5-8%
- Uso: areas de destaque sutil, backgrounds de citacoes

### Regras Gerais de Padroes
- Padroes sao **sempre sutis** — nunca devem competir com o conteudo
- Opacidade maxima de 15% para qualquer padrao
- Usar no maximo 1 padrao por secao
- Padroes nao substituem cor de fundo — sao sobrepostos a ela

---

## Grid para Composicoes Visuais

### Grid Base
- **Colunas:** 12 colunas com gutter de 24px (desktop)
- **Margem lateral:** 48px (desktop), 24px (tablet), 16px (mobile)
- **Modulo base:** 8px — todos os espacamentos sao multiplos de 8

### Grid de Composicao Visual
Para pecas graficas (posts, banners, capas):

```
+-------------------------------------------------+
|  M  |  1  |  2  |  3  |  4  |  5  |  6  |  M  |
|     |     |     |     |     |     |     |     |
|     |  Bloco Principal  |  Eng. |     |     |
|     |  (col 1-4)        |       |     |     |
|     |                   |  Bloco|     |     |
|     |                   |  (3-5)|     |     |
|     |     |     |     |     |     |     |     |
+-------------------------------------------------+
  M = margem
```

#### Regras do Grid
- Blocos geometricos devem ocupar **no minimo 2 colunas**
- Engrenagens podem ultrapassar colunas (sao decorativas)
- Texto deve estar contido dentro das colunas do grid
- Fotos devem alinhar-se ao grid (sangria permitida nas bordas)

---

## Elementos Descontinuados

Os seguintes elementos do manual anterior (v1.0) estao **descontinuados**:

### Filtros de Opacidade Monocromaticos
- **NAO usar** filtros que tornam fotos preto-e-branco ou monocromaticas
- **NAO usar** overlays opacos que escondem completamente a foto
- **Substituir por:** blocos semi-transparentes coloridos (70-85% opacidade) que preservam a foto

### Sombras Pesadas (Drop Shadows)
- **NAO usar** box-shadows com blur > 8px e opacidade > 15%
- **Substituir por:** bordas sutis ou elevacao leve (0-4px blur, 5-10% opacidade)

### Bordas Grossas e Contornos
- **NAO usar** contornos com mais de 2px em elementos da interface
- **Substituir por:** blocos de cor solida ou backgrounds coloridos

---

## Checklist de Aplicacao

- [ ] Blocos geometricos com cantos arredondados (8-24px radius)
- [ ] Composicao assimetrica com tamanhos variados
- [ ] Maximo 3 cores de blocos por composicao
- [ ] Engrenagens posicionadas nas bordas, nao sobre conteudo
- [ ] Maximo 5 engrenagens por composicao
- [ ] Icones em estilo line com espessura consistente
- [ ] Padroes com opacidade <= 15%
- [ ] Grid de 12 colunas respeitado
- [ ] Nenhum elemento descontinuado utilizado
- [ ] Espacamentos em multiplos de 8px
