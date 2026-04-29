# Workflow: Capa de Video de Projeto

> Referencia Leonardo AI: estrutura validada (PIE Guarulhos + Gastronomia Sustentavel, abr/2026). Se surgir erro de API, dúvida sobre payload ou resultado visual inesperado, consultar `workflows/marketing/referencia/leonardo_ai_core.md`.

## Objetivo
Gerar capa estática (JPG 4:5, 1856×2304 px) para o vídeo de um projeto com identidade visual do patrocinador, foto real do projeto, logo do projeto e logo do patrocinador. Companion do roteiro de vídeo (mesmo input, formato diferente).

## Quando Executar
Sempre que entregar um vídeo de projeto (Pré, Durante ou Pós) precisamos de uma capa que:
1. Funcione como thumbnail no Reels e no feed
2. Comunique nome do projeto + patrocinador imediatamente
3. Mantenha a identidade visual do projeto

## Inputs Necessários

| Input | Origem | Obrigatório |
|-------|--------|-------------|
| Foto principal (1) | `assets/melhores-fotos/{programa}/` ou `assets/projetos/{slug}/FOTOS/` | Sim |
| Logo do projeto (1) | `assets/projetos/{slug}/LOGOS/` ou `PECAS_COMUNICACAO/` | Sim |
| Logo do patrocinador (1) | `assets/projetos/{slug}/LOGOS/` ou `brand-book/site/assets/` | Sim |
| Nome oficial do projeto | TAP / release | Sim |
| Subtítulo / edição | TAP / release | Sim (ex: "Culinária Sustentável - 2ª Edição") |
| Tagline ou copy curta | Briefing | Não |
| Cidade/UF | TAP | Não (entra na tagline) |

## Regras Críticas

- **3 image_references é o limite duro do nano-banana-2.** Quarta referência = `VALIDATION_ERROR`. Padrão: foto + logo projeto + logo patrocinador.
- **Prompt sub-1500 chars.** Prompts longos retornam `VALIDATION_ERROR` sem mensagem clara. Encurtar removendo redundância.
- **Headline em painel branco arredondado.** Texto solto sobre blocos de cor é ilegível. Painel branco com headline na cor primária da marca.
- **NO BLACK em texto** se o cliente pedir variação sem preto. Brand logos mantêm cores originais.
- **Proibir régua tricolor explicitamente** no prompt: `DO NOT add any tricolor stripe ruler or sponsor-logo bar at the bottom edge`.
- **Apenas "PATROCINADOR APRESENTA" no topo**, nunca duplicar com outra label de "GRU AIRPORT" ou similar no meio.
- **Nome do projeto SEMPRE escrito como texto** no painel branco, não confiar só no logo do projeto (pequeno demais para ler em mobile).

## Passo a Passo

### Passo 1 — Identificação
Extrair do briefing/release:
- Nome oficial completo
- Subtítulo/Edição (ex: "2ª Edição")
- Tagline curta (ex: "está chegando em Guarulhos")
- Patrocinador
- Cidade/UF

### Passo 2 — Selecionar a foto
Ideal: foto que:
- Tem o público em atividade (não posada)
- Tem cor coerente com a paleta do projeto
- Não tem watermark, data ou logo sobreposto
- Tem ≥ 800 px no menor lado

Se houver múltiplas opções, rodar pipeline de ranking (`tools/media/rankear_fotos.py`) ou perguntar ao usuário.

### Passo 3 — Coletar logos
Conferir que existem em `assets/projetos/{slug}/`:
- `LOGOS/{projeto}_logo.png` (logo do projeto, com transparência)
- `LOGOS/grulogo_*.png` ou logo do patrocinador

Se faltar, buscar em `brand-book/site/assets/` (logo NTICS) ou pedir ao usuário.

### Passo 4 — Definir paleta
Usar a paleta da identidade do projeto:
- Cor primária (geralmente do logo do projeto)
- 1-2 cores de destaque
- Branco como fundo neutro

Documentar como dict em Python:
```python
PALETTE = {
    "primary": "#1BA9B7",   # teal Gastronomia
    "magenta": "#D6116D",
    "lime": "#C7D435",
    "orange": "#E68427",
}
```

### Passo 5 — Gerar 3 versões em paralelo

Sempre gerar **3 variações de layout** na primeira rodada, deixando o usuário escolher:

| Versão | Layout |
|--------|--------|
| **v1** | Foto topo (45%) + curva onda + área cor com círculo branco do logo + painel branco bottom com headline |
| **v2** | Bloco cor topo com logo do projeto grande + curva onda + foto bottom + painel branco bottom com headline |
| **v3** | Foto fullbleed com logo flutuando no canto + painel branco bottom dominante (45%) com headline + créditos |

Estrutura de prompt comum (sub-1500 chars):

```
Vertical 4:5 Instagram video cover, project '{NOME}' sponsored by {PATROCINADOR}.
Palette: primary {hex}, accents {hexes}, white. NO BLACK for any text.

TOP {X} percent: clean white area. Centered, small {primary} uppercase: '{PATROCINADOR} APRESENTA'.
This is the ONLY label at the top, do not repeat it anywhere else.

[Layout específico v1/v2/v3 com posições e referências]

BOTTOM panel: bold {primary} headline centered, this is the project name: '{NOME}'.
Below in smaller magenta uppercase: '{SUBTITLE}'. Below in small magenta italic: '{TAGLINE}'.
Centered small magenta uppercase 'PATROCÍNIO' and below it the THIRD reference image
(GRU AIRPORT logo) preserved pixel-for-pixel with original colors.

No tricolor stripe at the bottom edge. Clean editorial design.
```

### Passo 6 — Revisão visual obrigatória

Por versão, conferir:
- [ ] Acentos PT-BR íntegros (Á, É, Ã, Ç)
- [ ] Nome do projeto sem palavra duplicada
- [ ] Logo do patrocinador renderizado (não retângulo preto, não distorcido)
- [ ] Logo do projeto preservado
- [ ] Tagline correta, sem acréscimo de palavra
- [ ] Sem régua tricolor no rodapé
- [ ] Headline em painel branco (não texto solto sobre cor)
- [ ] Sem repetição de "{PATROCINADOR} APRESENTA"

Se algum item falhar:
1. Salvar gen_id em log antes de apagar
2. Renomear arquivo defeituoso para `{nome}-defeito.jpg`
3. Ajustar prompt e regerar

### Passo 7 — Apresentar ao usuário
3 versões lado a lado. Usuário escolhe e pode pedir variações pontuais (mudar tagline, mudar cor, trocar foto). Regerar só a versão escolhida com o ajuste.

### Passo 8 — Entrega
```
output/marketing/carrosseis/projetos/{slug}/capa-video/
├── capa-video-v1.jpg
├── capa-video-v2.jpg
├── capa-video-v3.jpg
└── geracao.log    # gen_ids para recuperação
```

## Recuperar versão apagada (CDN do Leonardo)

Se um arquivo for apagado por engano, recupera com o `gen_id`:

```python
gid = "1f13ff1a-c288-6180-8159-e3906880fa9e"
r = requests.get(f"https://cloud.leonardo.ai/api/rest/v1/generations/{gid}", headers=HEADERS)
url = r.json()["generations_by_pk"]["generated_images"][0]["url"]
open("recuperada.jpg", "wb").write(requests.get(url, timeout=60).content)
```

Por isso `geracao.log` é obrigatório antes de qualquer `rm`.

## Erros Conhecidos

| Sintoma | Causa | Fix |
|---------|-------|-----|
| `VALIDATION_ERROR` no `/v2/generations` | Prompt > 1500 chars OU > 3 image_references | Encurtar prompt; reduzir refs |
| Logo do patrocinador vira retângulo preto | Leonardo falhou em renderizar essa ref nessa geração | Regenerar (não deterministico) |
| Headline ilegível sobre blocos coloridos | Não usou painel branco | Adicionar `clean white rounded panel with bold headline` no prompt |
| Régua tricolor aparece | Não proibiu explicitamente | Adicionar `DO NOT add any tricolor stripe ruler` |
| "GRU AIRPORT APRESENTA" duplicado | Prompt menciona em mais de um lugar | Restringir: `This is the ONLY label at the top, do not repeat it anywhere else` |
| Nome do projeto cortado/errado | Headline muito longa | Quebrar em 2 linhas no prompt: `'GASTRONOMIA' / 'TAMBÉM É ARTE'` |

## Conexão com Outros Workflows

| Workflow | Relação |
|----------|---------|
| `roteiro_video.md` | Fonte do conteúdo do vídeo que esta capa representa |
| `briefing_carrossel_video.md` | Mesmo input, formatos diferentes |
| `carrossel_projeto_ativo_cliente.md` | Compartilha padrões visuais (template + foto + logo, painel branco) |
| `referencia/leonardo_ai_core.md` | Detalhes de payload, dimensões, erros conhecidos |

## Especificações Técnicas

| Elemento | Especificação |
|----------|---------------|
| Proporção | 4:5 (Instagram, funciona como Reels cover e feed) |
| Dimensão | 1856 × 2304 px |
| Formato | JPG quality 95 |
| Modelo | nano-banana-2 (v2 API) |
| image_references | máx 3, strength HIGH |
| prompt_enhance | OFF |
| Custo por versão | ~US$ 0,058 → 3 versões ≈ US$ 0,18 |
