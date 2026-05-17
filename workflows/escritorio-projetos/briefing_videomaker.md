# Briefing Videomaker (HTML Interativo por Projeto)

> TL;DR: Gera dois artefatos por ciclo de captação — (A) um HTML interativo para o captador em campo e (B) tasks ClickUp estruturadas para a editora. São destinatários e documentos diferentes com informações diferentes.

---

## Quando usar

Sempre que um ciclo de captação estiver se aproximando (pré-projeto, durante ou case final) e houver fotógrafo/videomaker com datas em vista. Um documento por ciclo de captação (ex.: `2026-05-04`), cobrindo todos os projetos ativos do período. Não usar para briefings de design ou carrossel.

---

## Os dois destinatários — lógica central

| | Track A: Captação em campo | Track B: Criação do vídeo |
|--|---------------------------|--------------------------|
| **Quem recebe** | Fotógrafo, videomaker, captador no local | Editora (Aline), criador do conteúdo |
| **Onde fica** | HTML GitHub Pages (link compartilhado) | Task ClickUp do projeto |
| **Quando usa** | Dia da captação, antes e durante | Depois que o bruto chega do campo |
| **O que precisa saber** | O que captar, quem entrevistar, o que perguntar, onde guardar | O que montar, como narrar, o que publicar, quem aprova |
| **Formato** | Visual, escaneável, por personas | Estruturado, completo, sem ambiguidade |

---

## Inputs

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| Lista de projetos ativos | lista de IDs | Sim | Ex.: 116, 117, 119, 120, 124, 125, 127 |
| Datas de campo confirmadas | por projeto | Sim | Data + cidade + fotógrafo + telefone |
| IDs das tasks ClickUp (vídeos) | por projeto | Sim | Para criar/atualizar as tasks de edição |
| ID da lista ClickUp (Aline) | string | Sim | Lista onde as tasks de edição ficam |
| Drive IDs por projeto | string | Sim | Pasta raiz de evidências de cada projeto |
| CLAUDE.md de cada projeto | arquivo | Sim | Contexto, público, cidade, stakeholders, regras editoriais |
| Diretriz de captação audiovisual | arquivo | Sim | `SecondBrain/conhecimento/diretrizes/captacao-audio-visual.md` |

---

## APIs e chaves

| API | Uso | Variável |
|-----|-----|----------|
| ClickUp API v2 | Criar tasks, inserir descrição completa e comentários | `CLICKUP_TOKEN` |
| GitHub Pages | Publicação do HTML via `arte3-star/ntics-project-sites` | Git credentials |

---

## Fase 1: Levantamento de contexto (gate humano)

Para cada projeto na lista:

1. Ler `SecondBrain/projetos/{slug}/CLAUDE.md` — extrair: o que é, público, cidades, stakeholders, regras editoriais críticas, aprovadores.
2. Consultar ClickUp (se solicitado) para levantar tasks de vídeo existentes na lista da editora.
3. Confirmar com Lucas: fotógrafo confirmado (nome + telefone), datas por cidade, Drive IDs.

**Perguntas padrão se informação estiver faltando:**
- Fotógrafo confirmado? Nome + telefone?
- Datas por cidade?
- Há tasks ClickUp já criadas para esses vídeos? Quais IDs?
- Drive ID da pasta de evidências?

---

## Track A: Captação em campo (HTML)

**Arquivo:** `output/marketing/briefings-videomaker/{AAAA-MM-DD}/index.html`
**Publicado em:** `https://arte3-star.github.io/ntics-project-sites/marketing/briefings-videomaker/{DATA}/`

### Estrutura do HTML

```
<html>
  <head>
    <style>  ← CSS centralizado: cores por projeto, todos os componentes
  <body>
    <nav>   ← sidebar: um botão .nav-item[data-view="NNN"] por projeto + aba Aline
    <main>
      <section id="view-NNN" class="view view-NNN">  ← uma section por projeto
        A1. hero
        A2. banner de contexto (regras editoriais críticas)
        A3. agenda de campo (datas + fotógrafo)
        A4. personas e perguntas
        A5. b-roll prioritário
        A6. stories (arco de 10)
        A7. estrutura de pastas Drive
      <section id="view-aline">  ← aba onboarding da editora
        (ver Track B — seção de referência cruzada no HTML)
```

### A1. Hero

```html
<div class="hero">
  <div class="hero-inner">
    <div class="overline">Projeto NNN · Nome curto</div>
    <h1>Headline narrativa do projeto</h1>
    <p class="lead">Uma frase que explica o que está sendo feito e para quem.</p>
    <div class="hero-meta">
      Patrocinador | Cidade(s) | Nº de pessoas | GP: Nome
    </div>
  </div>
</div>
```

### A2. Banner de contexto

Caixa de alerta com as regras editoriais mais críticas do projeto — o que o captador não pode esquecer no dia. Exemplo: "Cliente não estará presente na sexta. Stories podem ser feitos nos 3 dias. Nada sem aprovação FSB." Tom direto, não institucional.

```html
<div class="context-banner">
  <strong>Atenção em campo:</strong> [regra crítica 1] · [regra crítica 2]
</div>
```

### A3. Agenda de campo

Só aparece quando há fotógrafo e datas confirmadas. Um bloco por projeto.

```html
<section class="block">
  <div class="block-header">
    <div class="overline">Agenda confirmada</div>
    <h2>Datas de campo</h2>
  </div>
  <div class="photographer-badge">
    Fotógrafo: Nome · (DDD) XXXXX-XXXX
  </div>
  <table class="schedule-table">
    <thead><tr><th>Data</th><th>Cidade / Atividade</th><th>Observação</th></tr></thead>
    <tbody>
      <tr>
        <td class="sched-date">DD/MM</td>
        <td>Nome da cidade — atividade que acontece</td>
        <td class="sched-note">Observação crítica do dia</td>
      </tr>
    </tbody>
  </table>
</section>
```

### A4. Personas e perguntas

Um card `.persona` por personagem a ser entrevistado. Baseado na diretriz `captacao-audio-visual.md` seção 6.2.

```html
<div class="personas-grid">
  <div class="persona">
    <div class="persona-name">Nome / papel do personagem</div>

    <span class="q-main-badge">Pergunta principal</span>
    <p class="question-main">
      Pergunta que gera resposta de impacto — não factual.
      Ex.: "O que mudou na sua forma de ver o futuro depois desse projeto?"
    </p>

    <p class="question">Pergunta de contexto 1 (quem é, o que faz)</p>
    <p class="question">Pergunta de desenvolvimento (como foi, o que aprendeu)</p>
    <p class="question">Pergunta de virada (o que muda daqui para frente)</p>
    <p class="question">Pergunta de fechamento (mensagem para o patrocinador)</p>

    <!-- Apenas para representantes de empresa: bloco RSC -->
    <span class="q-rsc-badge">Responsabilidade Corporativa</span>
    <p class="question-rsc">Como este projeto se conecta à estratégia de RSC/ESG da empresa?</p>
    <p class="question-rsc">O que muda no território onde a empresa opera depois de um projeto como esse?</p>
    <p class="question-rsc">Isso é uma ação pontual ou faz parte de uma estratégia de longo prazo?</p>
    <p class="question-rsc">O que a empresa aprende com um projeto como esse? O que volta para dentro da organização?</p>
    <p class="question-rsc">Que mensagem você daria para outra empresa que ainda não faz esse tipo de investimento social?</p>
  </div>
</div>
```

**Personas padrão por projeto** (adaptar para o contexto):

| Persona | Badge RSC | Foco das perguntas |
|---------|-----------|--------------------|
| Representante / Voluntário da empresa | Sim | Percepção, cena marcante, motivação + 5 RSC |
| Participante / Beneficiário | Não | Nome completo, o que fez, o que mudou, recomendação |
| Educador / Facilitador | Não | O que foi trabalhado, desenvolvimento, impacto pedagógico |
| Coordenação NTICS | Não | Do que se trata, grande entrega, importância social |
| Parceiro local (secretaria, ONG) | Não | Por que é importante, agradecimento ao patrocinador |

**Regra de ouro das perguntas:** uma pergunta por vez, combinar antes ("responde em até 20 segundos"), começar pelo contexto da atividade. A pergunta principal (`q-main-badge`) é a que abre o depoimento e decide o corte do vídeo.

### A5. B-roll prioritário

Lista dos planos específicos que o captador precisa garantir para esse projeto. Baseado na diretriz seção 4.2 e adaptado para o contexto.

```html
<section class="block">
  <div class="block-header">
    <div class="overline">B-roll prioritário</div>
    <h2>Cenas que não podem faltar</h2>
  </div>
  <ul class="broll-list">
    <li><strong>Chegada:</strong> fachada do local, público chegando, plano geral</li>
    <li><strong>Ação central:</strong> [descrição específica do projeto — mãos, ferramenta, produto]</li>
    <li><strong>Interação:</strong> participantes + educador, cooperação em grupo</li>
    <li><strong>Detalhe:</strong> close de mãos, expressão, material em uso</li>
    <li><strong>Resultado:</strong> entrega, exposição, apresentação final</li>
    <li><strong>Marca aplicada:</strong> banner, camiseta, sinalização no ambiente</li>
  </ul>
</section>
```

### A6. Stories para Instagram (arco de 10)

Arco narrativo fixo. Adaptar "Ação 1" e "Ação 2" para o contexto do projeto. Cada card é um `.story-card`.

| # | Momento | Instrução universal |
|---|---------|---------------------|
| S01 | Chegada | Captador na entrada, câmera selfie: "Hoje estou aqui em [local]" |
| S02 | Antes | Setup sendo montado, participantes chegando, energia de expectativa |
| S03 | Apresentação | Dinâmica de abertura — nome + expectativa em 5s cada |
| S04 | Ação 1 | Momento mais visual do projeto (mãos, ferramenta, produto em progresso) |
| S05 | Ação 2 | Interação entre participantes, cooperação, energia coletiva |
| S06 | Bastidores | 15s de algo espontâneo — não roteirizar |
| S07 | Pergunta rápida | "Uma palavra pra descrever hoje" — 3 a 4 respostas em sequência rápida |
| S08 | Depoimento relâmpago | 1 participante, 20s direto, sem roteiro prévio |
| S09 | Virada | Momento de entrega, apresentação ou culminância — pico do dia |
| S10 | Saída | Captador encerrando, frame final do espaço, sensação de fechamento |

### A7. Estrutura de pastas Drive

```html
<div class="folder-tree">
  <span class="folder">[NNN] Nome do Projeto</span>
  ├── 01_DEPOIMENTOS
  │   ├── PATROCINADOR
  │   ├── PROFESSORES
  │   └── ALUNOS
  ├── 02_STORIES
  ├── 03_BROLL
  │   ├── CHEGADA
  │   └── GERAL
  ├── 04_FOTOS
  │   ├── SELECIONADAS
  │   ├── SENSIBILIDADE
  │   └── TOP15
  └── 05_BRUTO
</div>
<div class="naming-rule">
  <h4>Convenção de nomeação</h4>
  Depoimentos: <code>captador_depoente_descricao.mp4</code>
  Stories: <code>S01_chegada.mp4</code>
  B-roll: <code>BROLL_descricao.mp4</code>
  Fotos: <code>FOTO_001_descricao.jpg</code>
</div>
<a href="https://drive.google.com/drive/folders/{DRIVE_ID}" class="drive-badge" target="_blank">
  Abrir pasta Drive →
</a>
```

---

## Track B: Criação do vídeo (ClickUp tasks)

Cada vídeo previsto é uma task no ClickUp, atribuída à editora. A task deve ter tudo que ela precisa para montar o vídeo do zero — sem precisar perguntar nada a mais.

### Estrutura completa de uma task de criação

**Nome da task:**
```
[Tipo] · [Projeto NNN] · [Cidade / Contexto]
Ex.: Reel Durante · 116 Áster · Sidrolândia
```

**Descrição da task** (campo `description` via API — tudo junto, não em comentários):

```
CONTEXTO DO VIDEO
[2-3 frases descrevendo o que aconteceu/acontece no projeto nessa cidade.
Tom jornalístico. É o "antes de assistir" da editora.]

PERSONAGEM CENTRAL
[Quem fala no vídeo. Nome/perfil + por que esse personagem foi escolhido.]

PERGUNTA GUIA DO DEPOIMENTO
[A pergunta principal que foi feita para gerar o depoimento central.
Isso orienta a editora sobre o que procurar no material bruto.]

SCRIPT DE NARRACAO

[00s - HOOK - legenda animada na tela]
"Frase de abertura impactante."

[05s - B-ROLL DE CONTEXTO]
Imagens sugeridas: [lista de planos específicos]

[15s - DEPOIMENTO]
>> ESPACO DO DEPOIMENTO — 15 a 20 segundos <<
Buscar no bruto: resposta à pergunta "[pergunta guia]"
Instrução de edição: [corte rápido / deixar respirar / etc.]

[35s - FECHAMENTO]
"Frase de encerramento."

[38s - CREDITO INSTITUCIONAL]
"Projeto NTICS com [Patrocinador]"
Logo NTICS (2s)

OPCOES DE TITULO (escolher 1 para legenda do Reel)
1. [Opção A — gancho emocional]
2. [Opção B — dado/território]
3. [Opção C — virada narrativa]

DESCRICAO DO POST (legenda pronta para Instagram)
[3 a 5 linhas de legenda. Tom do projeto. Sem em-dashes.
Inclui: contexto, impacto, CTA ou tag do patrocinador se aplicável.
Termina com 3 a 5 hashtags relevantes.]

PLANO VISUAL (referencia de estilo e ritmo)
Formato: Reel 9:16 vertical | Duração: ~40s
Ritmo de corte: [rápido com música / lento e contemplativo / etc.]
Paleta: cores do projeto ([accent color])
Fontes: [fonte institucional do patrocinador se houver / padrão NTICS]
Abertura: [legenda animada sobre b-roll / logo do projeto / etc.]
Referência de projeto anterior: [link ou nome de vídeo similar já feito]

APROVACAO
Quem aprova antes de publicar: [Nome] ([empresa/função])
Prazo de aprovação: [N dias úteis]
Canal de envio: [Teams / WhatsApp / etc.]

RESPONSAVEL PELA CRIACAO
Editora: Aline
Entrega bruta para revisão: [data]
Publicação prevista: [data]
```

### Criar task via API

```python
import requests, os

HEADERS = {"Authorization": os.environ["CLICKUP_TOKEN"], "Content-Type": "application/json"}

def criar_task_video(list_id, nome, descricao, assignee_id=87429810):
    resp = requests.post(
        f"https://api.clickup.com/api/v2/list/{list_id}/task",
        headers=HEADERS,
        json={"name": nome, "description": descricao, "assignees": [assignee_id]}
    )
    resp.raise_for_status()
    task_id = resp.json()["id"]
    # Verificar criação
    check = requests.get(f"https://api.clickup.com/api/v2/task/{task_id}", headers=HEADERS)
    assert check.json()["name"] == nome, "Task não encontrada após criação"
    return task_id
```

### Quando a task já existe: atualizar via comentário

Se a task já existe e precisa receber script ou opções de título:

```python
def comentar_task(task_id, texto):
    requests.post(
        f"https://api.clickup.com/api/v2/task/{task_id}/comment",
        headers=HEADERS,
        json={"comment_text": texto}
    ).raise_for_status()
```

Usar comentários para: iterações de script, revisões de título, notas de aprovação. Não repetir conteúdo que já está na descrição.

---

## Fase 2: Aba da editora no HTML (referência cruzada)

A aba `view-aline` no HTML não é o briefing completo da editora — as tasks ClickUp têm isso. A aba serve de **painel de produção**: o que está na fila, quando o bruto chega, quando entregar.

### A. Fila de edição por projeto

Tabela com: projeto, vídeos previstos, data de entrega, aprovador, observação editorial.

### B. Calendário cruzado

Tabela cronológica: Data | Projeto | O que chega do campo | Entrega Aline | Stories.

Badge `cal-stories-flag` ("Stories: capturar e postar hoje") nas linhas em que o fotógrafo estará em campo.

### C. Fila detalhada com links ClickUp

Tabela de 4 colunas por projeto:

```
Data / Fotógrafo | Vídeo (nome + aprovador) | Opções de título | Task (#ID linkado)
```

Fotógrafo e horário na coluna de data. Cada linha de captura recebe o badge de Stories.

---

## Fase 3: Scripts Python de manutenção do HTML

Todos os scripts seguem este padrão para evitar problemas de encoding no Windows:

```python
# -*- coding: utf-8 -*-
from pathlib import Path

TARGET = Path(r"...\index.html")
content = TARGET.read_text(encoding="utf-8")

# str.replace() com strings literais — acentos preservados pelo encoding="utf-8"
content = content.replace("texto antigo", "texto novo com acentos: captação, narração")

# Verificação obrigatória antes de salvar
assert content.count("—") == 0, "Em-dash encontrado — remover antes de salvar"

TARGET.write_text(content, encoding="utf-8")
print(f"Salvo: {len(content)} chars")
```

**Regra absoluta:** NUNCA usar `—` (em-dash U+2014) em nenhum texto publicado. Substituir por vírgula, ponto ou reescrita.

---

## Fase 4: Publicar no GitHub Pages

Repositório: `arte3-star/ntics-project-sites` (clone local em `.tmp/ntics-pages/`).

```bash
cp output/marketing/briefings-videomaker/{DATA}/index.html \
   .tmp/ntics-pages/marketing/briefings-videomaker/{DATA}/index.html

cd .tmp/ntics-pages
git add marketing/briefings-videomaker/{DATA}/index.html
git commit -m "update: {descrição curta}"
git push origin master
```

URL pública: `https://arte3-star.github.io/ntics-project-sites/marketing/briefings-videomaker/{DATA}/`

---

## Output esperado

**Track A (campo):**
- `output/marketing/briefings-videomaker/{DATA}/index.html` com todas as abas
- URL GitHub Pages funcional, testada no navegador

**Track B (edição):**
- Task ClickUp por vídeo previsto, atribuída à editora
- Descrição completa: contexto + personagem + script + opções de título + descrição do post + plano visual + aprovação
- Verificação `GET /api/v2/task/{id}` após cada criação

---

## Checklist de qualidade

**HTML (Track A):**
- [ ] Zero em-dashes no arquivo
- [ ] Todos os acentos presentes
- [ ] Cada projeto tem: hero + contexto + agenda + personas + b-roll + stories + pastas
- [ ] Agenda só aparece quando há fotógrafo confirmado
- [ ] Badge RSC presente nos representantes de empresa
- [ ] Aba Aline tem fila de edição + calendário + fila detalhada com links ClickUp

**Tasks ClickUp (Track B):**
- [ ] Uma task por vídeo previsto
- [ ] Descrição tem: contexto + personagem + pergunta guia + script + opções de título + descrição do post + plano visual + aprovação + responsável
- [ ] Task verificada com `GET` após criação
- [ ] Editora (Aline) como assignee

---

## Fontes de informação

| O que precisa | Onde buscar |
|---------------|------------|
| Contexto, stakeholders, regras editoriais do projeto | `SecondBrain/projetos/{slug}/CLAUDE.md` |
| Perguntas base por persona | `captacao-audio-visual.md` seção 6.2 |
| Perguntas RSC (representantes de empresa) | As 5 perguntas fixas da seção A4 deste workflow |
| Datas de campo, fotógrafo, telefone | Informado por Lucas ou ClickUp |
| IDs de tasks ClickUp | URL do app ClickUp ou `GET /api/v2/list/{list_id}/task` |
| Drive IDs de evidências | Informado por Lucas ou Drive do projeto |
| Tom, identidade verbal | `brand-book/02-identidade-verbal/tom-de-voz.md` |
| Descrição do post: hashtags, tom do projeto | `brand-book/data/brand-data.yaml` + CLAUDE.md do projeto |
| Referência de plano visual de projeto anterior | HTML do ciclo mais recente / vídeos aprovados anteriores |

---

## Dependências

**Upstream:**
- `SecondBrain/projetos/{slug}/CLAUDE.md` existente com stakeholders e regras editoriais
- Fotógrafo e datas confirmados por Lucas
- IDs das listas ClickUp

**Downstream:**
- Captador/fotógrafo recebe link do HTML antes do dia de campo
- Editora (Aline) consulta o HTML (painel) e as tasks ClickUp (briefing completo) durante edição
- Tasks criadas aqui são monitoradas pelo `/relatorio-pmo`
- Vídeos aprovados seguem para `/publicar-drive` e publicação no Instagram
