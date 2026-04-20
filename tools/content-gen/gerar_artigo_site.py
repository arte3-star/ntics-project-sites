"""
Gera artigo de site NTICS — corpo do texto + imagens Leonardo AI.

📚 Ref: workflows/marketing/referencia/leonardo_ai_core.md — consulte em caso de erro ou
dúvida sobre payloads, modos, dimensões de hero/inline, erros conhecidos.

Uso pelo agente:
    python tools/content-gen/gerar_artigo_site.py \\
        --slug consciencia-e-proposito-m01 \\
        --content-file .tmp/artigo-m01.md

Ou importado como modulo para montar o HTML a partir de string.

Output:
    output/marketing/artigos/artigo-{slug}.html   (body only, preview no navegador)
    output/marketing/artigos/hero-{slug}.jpg
    output/marketing/artigos/img-*.jpg
"""

import os
import sys
import time
import json
import argparse
import requests
from pathlib import Path

# ── Config ──────────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = ROOT / "output" / "marketing" / "artigos"
API_KEY = os.environ.get("LEONARDO_API_KEY", "")

if not API_KEY:
    from dotenv import load_dotenv
    load_dotenv(ROOT / ".env")
    API_KEY = os.environ.get("LEONARDO_API_KEY", "")


# ── Leonardo AI ──────────────────────────────────────────────────────────────
def gerar_imagem_leonardo(prompt: str, api_key: str = "") -> str:
    """Submete geracao no Leonardo AI Nano Banana 2 e retorna URL da imagem."""
    key = api_key or API_KEY
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": f"Bearer {key}",
    }
    payload = {
        "model": "nano-banana-2",
        "parameters": {
            "prompt": prompt,
            "width": 1152,
            "height": 896,
            "quantity": 1,
            "prompt_enhance": "OFF",
        },
        "public": False,
    }

    resp = requests.post(
        "https://cloud.leonardo.ai/api/rest/v2/generations",
        headers=headers, json=payload, timeout=30,
    )
    if not resp.ok:
        print(f"    Leonardo erro: {resp.status_code} -- {resp.text[:300]}")
        resp.raise_for_status()

    data = resp.json()
    gen_id = None
    for v in data.values():
        if isinstance(v, dict):
            gen_id = v.get("generationId") or v.get("id")
            if gen_id:
                break
    if not gen_id:
        raise RuntimeError(f"gen_id nao encontrado: {data}")

    print(f"    Geracao submetida: {gen_id[:12]}...")

    # Poll
    poll_headers = {"accept": "application/json", "authorization": f"Bearer {key}"}
    print(f"    Aguardando 55s...")
    time.sleep(55)
    for attempt in range(12):
        r = requests.get(
            f"https://cloud.leonardo.ai/api/rest/v1/generations/{gen_id}",
            headers=poll_headers, timeout=20,
        )
        job = r.json().get("generations_by_pk", {})
        status = job.get("status", "PENDING")
        print(f"    Status [{attempt+1}/12]: {status}")
        if status == "COMPLETE":
            imgs = job.get("generated_images", [])
            if imgs:
                return imgs[0]["url"]
        elif status == "FAILED":
            raise RuntimeError(f"Geracao falhou: {gen_id}")
        time.sleep(10)

    raise TimeoutError(f"Timeout aguardando geracao {gen_id}")


def baixar_imagem(url: str, caminho: Path) -> None:
    """Baixa imagem de URL para arquivo local."""
    resp = requests.get(url, timeout=60)
    resp.raise_for_status()
    caminho.write_bytes(resp.content)
    print(f"    Salvo: {caminho.name} ({len(resp.content)//1024} KB)")


def gerar_imagens(prompts: list[dict], output_dir: Path) -> dict:
    """
    Gera imagens sequencialmente.
    prompts: [{"key": "hero", "filename": "hero-slug.jpg", "prompt": "..."}]
    Retorna: {"hero": "hero-slug.jpg", ...}
    """
    resultado = {}
    for i, img in enumerate(prompts):
        caminho = output_dir / img["filename"]
        if caminho.exists():
            print(f"  [SKIP] {img['filename']} ja existe")
            resultado[img["key"]] = img["filename"]
            continue
        print(f"  Gerando: {img['key']} ({i+1}/{len(prompts)})")
        url = gerar_imagem_leonardo(img["prompt"])
        baixar_imagem(url, caminho)
        resultado[img["key"]] = img["filename"]
        if i < len(prompts) - 1:
            time.sleep(3)
    return resultado


# ── CSS do corpo do artigo ───────────────────────────────────────────────────
ARTICLE_CSS = """
/* NTICS Brand Book v2.0 — Artigo Body CSS */
:root {
  --verde-regeneracao: #3DAA35;
  --azul-petroleo: #005F73;
  --rosa-transformacao: #D41A6A;
  --laranja-acao: #E86428;
  --amarelo-consciencia: #F5B800;
  --teal-futuro: #00A5B8;
  --roxo-inovacao: #6B2D7B;
  --branco: #FFFFFF;
  --cinza-claro: #F4F4F4;
  --cinza-medio: #6B7280;
  --grafite: #2D2D2D;
  --font-primary: 'Inter', 'Helvetica Neue', Arial, sans-serif;
}

*, *::before, *::after { box-sizing: border-box; }
body {
  font-family: var(--font-primary);
  color: var(--grafite);
  background: var(--branco);
  line-height: 1.6;
  margin: 0;
  padding: 48px 24px;
}

.article-body {
  max-width: 760px;
  margin: 0 auto;
}

/* Lead */
.article-lead {
  font-size: 20px;
  font-weight: 400;
  line-height: 1.6;
  color: var(--azul-petroleo);
  margin-bottom: 48px;
  padding-bottom: 48px;
  border-bottom: 1px solid var(--cinza-claro);
}

/* Executive Summary */
.executive-summary {
  background: var(--cinza-claro);
  border-radius: 16px;
  padding: 48px;
  margin-bottom: 64px;
  border-top: 4px solid var(--azul-petroleo);
}
.executive-summary h3 {
  font-size: 13px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--azul-petroleo);
  margin: 0 0 24px 0;
}
.executive-summary p {
  font-size: 15px;
  line-height: 1.7;
  color: var(--grafite);
  margin-bottom: 16px;
}
.executive-summary p:last-child { margin-bottom: 0; }

/* Headings */
.article-body h2 {
  font-size: clamp(26px, 3.5vw, 36px);
  font-weight: 700;
  color: var(--azul-petroleo);
  letter-spacing: -0.01em;
  margin-top: 64px;
  margin-bottom: 24px;
  line-height: 1.2;
}
.section-number {
  display: block;
  font-size: 12px;
  font-weight: 700;
  color: var(--verde-regeneracao);
  text-transform: uppercase;
  letter-spacing: 0.15em;
  margin-bottom: 4px;
}
.article-body h3 {
  font-size: clamp(20px, 2vw, 24px);
  font-weight: 600;
  color: var(--grafite);
  margin-top: 48px;
  margin-bottom: 16px;
  line-height: 1.3;
}

/* Body text */
.article-body p {
  font-size: 16px;
  line-height: 1.75;
  color: var(--grafite);
  margin-bottom: 24px;
}
.article-body strong { color: var(--grafite); font-weight: 600; }
.article-body a { color: var(--teal-futuro); text-decoration: none; }
.article-body a:hover { color: var(--azul-petroleo); }
.article-body em { font-style: italic; }

/* Lists */
.article-body ul, .article-body ol {
  margin: 16px 0 24px 32px;
}
.article-body li {
  font-size: 16px;
  line-height: 1.75;
  margin-bottom: 8px;
}
.article-body ul li::marker { color: var(--verde-regeneracao); }

/* Blockquote */
blockquote {
  background: var(--cinza-claro);
  border-left: 4px solid var(--verde-regeneracao);
  border-radius: 0 8px 8px 0;
  padding: 24px 32px;
  margin: 48px 0;
}
blockquote p {
  color: var(--azul-petroleo);
  font-size: 17px;
  font-style: italic;
  margin-bottom: 0 !important;
}

/* Inline images */
.article-image { margin: 48px 0; }
.article-image img {
  border-radius: 16px;
  width: 100%;
  object-fit: cover;
  max-height: 420px;
}
.article-image figcaption {
  font-size: 12px;
  color: var(--cinza-medio);
  margin-top: 8px;
  text-align: center;
}

/* Stats row */
.stats-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin: 48px 0;
}
.stat-item {
  text-align: center;
  padding: 24px;
  background: var(--cinza-claro);
  border-radius: 12px;
}
.stat-number {
  font-size: clamp(24px, 3vw, 32px);
  font-weight: 700;
  color: var(--azul-petroleo);
  line-height: 1;
}
.stat-label {
  font-size: 12px;
  color: var(--cinza-medio);
  margin-top: 4px;
  line-height: 1.3;
}

/* Signs grid (5 cards) */
.signs-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  margin: 48px 0;
}
.sign-card {
  background: var(--cinza-claro);
  border-radius: 12px;
  padding: 32px;
  border-top: 3px solid;
}
.sign-card:nth-child(1) { border-color: var(--verde-regeneracao); }
.sign-card:nth-child(2) { border-color: var(--teal-futuro); }
.sign-card:nth-child(3) { border-color: var(--azul-petroleo); }
.sign-card:nth-child(4) { border-color: var(--amarelo-consciencia); }
.sign-card:nth-child(5) { border-color: var(--rosa-transformacao); }
.sign-number {
  font-size: 28px;
  font-weight: 700;
  color: var(--azul-petroleo);
  line-height: 1;
  margin-bottom: 8px;
}
.sign-card h4 {
  font-size: 15px;
  font-weight: 700;
  color: var(--grafite);
  margin: 0 0 8px 0;
}
.sign-card p {
  font-size: 14px;
  color: var(--cinza-medio);
  margin-bottom: 0;
  line-height: 1.6;
}

/* Elements grid */
.elements-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  margin: 48px 0;
}
.element-card {
  background: var(--cinza-claro);
  border-radius: 12px;
  padding: 32px;
  border-top: 3px solid var(--verde-regeneracao);
}
.element-card h4 {
  font-size: 15px;
  font-weight: 700;
  color: var(--grafite);
  margin: 0 0 8px 0;
}
.element-card p {
  font-size: 14px;
  color: var(--cinza-medio);
  margin: 0;
  line-height: 1.6;
}

/* Tables */
.table-wrapper { margin: 48px 0; overflow-x: auto; }
.table-wrapper table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}
.table-wrapper thead th {
  background: var(--azul-petroleo);
  color: var(--branco);
  padding: 12px 16px;
  text-align: left;
  font-weight: 600;
}
.table-wrapper tbody td {
  padding: 12px 16px;
  border-bottom: 1px solid var(--cinza-claro);
}
.table-wrapper tbody tr:hover { background: var(--cinza-claro); }

/* Video reference */
.video-ref {
  display: inline-block;
  margin: 16px 0 24px;
  font-size: 14px;
  color: var(--teal-futuro);
  font-weight: 500;
}

/* Responsive */
@media (max-width: 639px) {
  body { padding: 24px 16px; }
  .executive-summary { padding: 24px; }
  .stats-row { grid-template-columns: repeat(2, 1fr); }
  .signs-grid { grid-template-columns: 1fr; }
  .elements-grid { grid-template-columns: 1fr; }
}
"""


def montar_html_wrapper(titulo: str, article_body_html: str) -> str:
    """Monta HTML completo para preview no navegador (wrapper minimo + body)."""
    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{titulo} -- Preview NTICS</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
  <style>{ARTICLE_CSS}</style>
</head>
<body>
  {article_body_html}
</body>
</html>"""


# ── Artigo M01 hardcoded (para primeira execucao) ───────────────────────────
def artigo_m01_body(imgs: dict) -> str:
    """Retorna HTML do corpo do artigo M01 — Consciencia e Proposito."""
    img_rs = imgs.get("inline-rs-estrategica", "img-rs-estrategica.jpg")
    img_edu = imgs.get("inline-educacao", "img-educacao-territorio.jpg")

    return """<article class="article-body">

    <!-- LEAD -->
    <p class="article-lead">
      Empresas que tratam responsabilidade social como estrategia — e nao como obrigacao — constroem marcas mais resilientes, engajam melhor suas comunidades e geram indicadores ESG que transformam o relatorio de sustentabilidade em evidencia de valor. Este e o ponto de partida do mes de abril na NTICS.
    </p>

    <!-- RESUMO EXECUTIVO -->
    <div class="executive-summary">
      <h3>Resumo Executivo</h3>
      <p>
        Com 1.060+ projetos executados em 22 anos de operacao e NPS de 88, a NTICS Projetos acompanhou de perto a evolucao da responsabilidade social corporativa no Brasil: de acoes pontuais a programas estruturados, de compliance obrigatorio a diferencial competitivo. Clientes como Nubank, Bayer, Eneva e Whirlpool ja compreendem que programas de RSC bem desenhados fortalecem indicadores de materialidade, ampliam o engajamento com stakeholders e geram impacto mensuravel alinhado aos ODS da ONU.
      </p>
      <p>
        Este artigo sintetiza quatro dimensoes que marcam o salto de maturidade em responsabilidade social: a integracao a estrategia de negocio, o papel da educacao como vetor de transformacao, os cinco sinais que distinguem empresas maduras em RSC, e o poder do territorio como dimensao essencial de qualquer programa de impacto real. Sao perspectivas complementares — e caminhos praticos para empresas que querem ir alem do cumprimento de obrigacoes.
      </p>
      <p>
        <strong>Metodologia:</strong> ISO 9001 | GRI Standards | Pacto Global ONU desde 2018 | Alinhamento aos ODS 4, 8, 12 e 17
      </p>
    </div>

    <!-- SECAO 1: RS ESTRATEGICA -->
    <h2>
      <span class="section-number">01</span>
      Responsabilidade Social como Motor Estrategico
    </h2>

    <p>
      Por muito tempo, a pergunta das empresas sobre responsabilidade social foi: <em>"Quanto precisamos investir?"</em> Hoje, as empresas mais maduras fazem uma pergunta diferente: <em>"Como esse investimento se conecta a nossa estrategia?"</em>
    </p>

    <p>
      A mudanca de perspectiva nao e cosmetica — ela transforma a natureza dos programas. Quando responsabilidade social entra no planejamento estrategico, os projetos deixam de competir com o orcamento operacional e passam a ser tratados como o que de fato sao: investimentos com retorno mensuravel em marca, em reputacao, em indicadores ESG e em licenca social para operar.
    </p>

    <figure class="article-image">
      <img src=\"""" + img_rs + """\" alt="Lideres corporativos discutindo estrategia ESG" loading="lazy">
      <figcaption>Programas de RSC integrados a estrategia geram indicadores que fortalecem relatorios de sustentabilidade e a reputacao corporativa.</figcaption>
    </figure>

    <p>
      Leis de incentivo como a Lei Rouanet, a Lei do Esporte e o FIA/FUMCAD sao o mecanismo que viabiliza esse investimento com eficiencia fiscal — mas o mecanismo, sozinho, nao cria estrategia. A estrategia nasce quando a empresa pergunta: <em>qual e a comunidade com que nos importamos? Qual e o tema que reflete nossos valores? Qual e o impacto que queremos poder medir daqui a tres anos?</em>
    </p>

    <blockquote>
      <p>"Transformamos o proposito da sua empresa em projetos de impacto social — com metodologia ISO 9001 e 22 anos de experiencia em execucao via leis de incentivo."</p>
    </blockquote>

    <p>
      A NTICS Projetos atuou em mais de 165 cidades com programas alinhados a materialidade ESG de cada cliente. Em 2023-2024, foram 326.240 pessoas impactadas diretamente — cada uma delas parte de um programa desenhado sob medida para a estrategia de quem investiu.
    </p>

    <!-- STATS -->
    <div class="stats-row">
      <div class="stat-item">
        <div class="stat-number">1.060+</div>
        <div class="stat-label">Projetos executados</div>
      </div>
      <div class="stat-item">
        <div class="stat-number">11,4M+</div>
        <div class="stat-label">Pessoas impactadas</div>
      </div>
      <div class="stat-item">
        <div class="stat-number">165+</div>
        <div class="stat-label">Cidades atendidas</div>
      </div>
      <div class="stat-item">
        <div class="stat-number">NPS 88</div>
        <div class="stat-label">Satisfacao de clientes</div>
      </div>
    </div>

    <p>
      <a href="#" class="video-ref">Assista ao video: S01 — Por que RS estrategica importa agora</a>
    </p>

    <!-- SECAO 2: EDUCACAO -->
    <h2>
      <span class="section-number">02</span>
      Educacao: o Vetor de Transformacao que Ninguem Ignora Mais
    </h2>

    <p>
      Se ha um terreno onde o impacto se torna visivel com clareza — e onde a mensuracao encontra seu significado humano mais profundo — e o da educacao.
    </p>

    <p>
      Em 2023-2024, a NTICS impactou diretamente 201.000 alunos e capacitou 10.300 professores em 165 cidades brasileiras. O programa <strong>Robotica nas Escolas</strong> chegou a 2.693 alunos com nota media de avaliacao de 9,74 — evidencia de que qualidade e escala nao sao opostos quando ha metodo. O programa <strong>Conhecendo os ODS</strong> traduziu a Agenda 2030 da ONU em experiencias praticas para 326.086 pessoas em 868 cidades, com o apoio de educadores capacitados para liderar a conversa sobre sustentabilidade em sala de aula.
    </p>

    <figure class="article-image">
      <img src=\"""" + img_edu + """\" alt="Educacao transformadora: programa de impacto social" loading="lazy">
      <figcaption>Programas educacionais continuos transformam a relacao de estudantes, professores e comunidades com o conhecimento — e geram indicadores ESG alinhados ao ODS 4.</figcaption>
    </figure>

    <p>
      O que distingue educacao transformadora de uma acao pontual? Tres elementos:
    </p>

    <ol>
      <li><strong>Continuidade</strong> — um unico evento nao muda comportamento. Programas com multiplas interacoes e acompanhamento geram transformacao duradoura.</li>
      <li><strong>Metodologia</strong> — o conteudo precisa ser adaptado a realidade local, ao nivel de cada turma e as necessidades da comunidade.</li>
      <li><strong>Vinculo com o contexto</strong> — quando o programa conecta a escola a empresa, ao territorio e a agenda global, o estudante se torna agente — nao apenas beneficiario.</li>
    </ol>

    <p>
      Para empresas que investem via Lei Rouanet ou FIA/FUMCAD, programas educacionais bem estruturados geram indicadores alinhados ao <strong>ODS 4 (Educacao de Qualidade)</strong> e ao <strong>ODS 8 (Trabalho Decente e Crescimento Economico)</strong> — duas das metas mais relevantes para relatorios de materialidade ESG no Brasil.
    </p>

    <p>
      <a href="#" class="video-ref">Assista ao video: S02 — Educacao como vetor de impacto</a>
    </p>

    <!-- SECAO 3: 5 SINAIS DE MATURIDADE -->
    <h2>
      <span class="section-number">03</span>
      Os 5 Sinais de Maturidade em Responsabilidade Social
    </h2>

    <p>
      Ao longo de 22 anos e 1.060+ projetos, a NTICS identificou padroes consistentes em empresas que fizeram o salto de responsabilidade social como obrigacao para responsabilidade social como estrategia. Sao cinco sinais que aparecem juntos nas organizacoes mais maduras.
    </p>

    <div class="signs-grid">
      <div class="sign-card">
        <div class="sign-number">01</div>
        <h4>Integracao a estrategia</h4>
        <p>RSC aparece no planejamento estrategico — nao apenas no relatorio anual. Os programas tem metas, indicadores e donos claros dentro da organizacao.</p>
      </div>
      <div class="sign-card">
        <div class="sign-number">02</div>
        <h4>Metricas de longo prazo</h4>
        <p>Os indicadores vao alem do evento e medem transformacao real: mudanca de comportamento, aquisicao de habilidades, melhoria de condicoes de vida.</p>
      </div>
      <div class="sign-card">
        <div class="sign-number">03</div>
        <h4>Engajamento interno</h4>
        <p>Colaboradores conhecem, se identificam e participam dos programas. RSC deixa de ser "o que o departamento juridico cuida" e vira proposito compartilhado.</p>
      </div>
      <div class="sign-card">
        <div class="sign-number">04</div>
        <h4>Dialogo com o territorio</h4>
        <p>Os programas sao desenvolvidos <em>com</em> as comunidades — nao apenas <em>para</em> elas. A empresa escuta antes de propor e ajusta conforme aprende.</p>
      </div>
      <div class="sign-card">
        <div class="sign-number">05</div>
        <h4>Aprendizado continuo</h4>
        <p>A empresa usa os dados de impacto para evoluir os programas — nao apenas para reportar. Cada ciclo comeca mais informado que o anterior.</p>
      </div>
    </div>

    <p>
      Esses sinais nao aparecem de uma vez. A maturidade em RSC e um processo — e empresas em diferentes estagios podem estar avancadas em alguns sinais e incipientes em outros. O importante e reconhecer onde esta e avancar com metodo.
    </p>

    <p>
      <a href="#" class="video-ref">Assista ao video: S03 — Os 5 sinais de maturidade em RSC</a>
    </p>

    <!-- SECAO 4: PODER DO TERRITORIO -->
    <h2>
      <span class="section-number">04</span>
      O Poder do Territorio: Onde o Proposito se Torna Real
    </h2>

    <p>
      Territorio nao e apenas o local onde o projeto acontece. E o contexto que determina se o impacto sera superficial ou transformador.
    </p>

    <p>
      Cada territorio tem sua historia, seus lideres, suas necessidades urgentes e suas oportunidades latentes. Programas que chegam sem escutar o territorio tendem a reproduzir solucoes que funcionam em outro lugar — mas nao ali. Programas que partem do territorio constroem algo que a comunidade reconhece como seu.
    </p>

    <p>
      O projeto <strong>Amazonia 2030</strong>, executado com a comunidade Kambeba no Amazonas, exemplifica essa logica. Nao chegamos com um projeto pronto: construimos junto, respeitando a cultura, a lingua e a visao de futuro da comunidade. O resultado foi um documentario, um centro comunitario e um modelo de intervencao que hoje serve como referencia para programas em territorios indigenas.
    </p>

    <p>
      O programa <strong>Culinaria Sustentavel</strong>, que capacitou 10.884 pessoas em 6 cidades, tambem nasceu da escuta ativa: o que as mulheres das comunidades precisavam nao era apenas renda — era autonomia, rede de apoio e conexao com a cadeia produtiva local. O programa respondeu a isso.
    </p>

    <blockquote>
      <p>Quando uma empresa compreende o territorio — seus lideres, suas necessidades, suas oportunidades — ela para de fazer projetos <em>para</em> comunidades e comeca a fazer projetos <em>com</em> comunidades. Essa distincao muda tudo.</p>
    </blockquote>

    <p>
      Territorios tambem sao alvos de legislacoes especificas — e compreender essa dimensao e parte do trabalho estrategico. As Leis de Incentivo preveem destinacoes para determinadas regioes ou publicos, e empresas que entendem essa geografia podem ampliar o alcance do seu investimento social com precisao.
    </p>

    <p>
      <a href="#" class="video-ref">Assista ao video: S04 — O poder do territorio</a>
    </p>

    <!-- CONCLUSAO -->
    <h2>
      <span class="section-number">05</span>
      Consciencia e o Ponto de Partida. Proposito e o Motor.
    </h2>

    <p>
      Abril abre o ano com uma pergunta que vale para qualquer empresa que investe em responsabilidade social: <em>voce esta fazendo isso por obrigacao ou por conviccao?</em>
    </p>

    <p>
      A resposta muda tudo. Empresas que operam por conviccao integram RSC a estrategia, escolhem programas que fazem sentido para seu territorio e seus valores, medem o impacto com rigor e aprendem com ele. Empresas que operam por obrigacao cumprem o minimo — e perdem a oportunidade de transformar um custo em diferencial competitivo.
    </p>

    <p>
      Os quatro temas deste mes — RS estrategica, educacao, maturidade e territorio — sao partes de um mesmo movimento. Nao sao topicos isolados: sao dimensoes de uma empresa que decidiu que impacto social e parte do seu modelo de negocio.
    </p>

    <p>
      A NTICS Projetos foi fundada em 2002 com uma conviccao: o investimento social corporativo pode — e deve — transformar realidades de verdade. Ao longo de 22 anos, essa conviccao se traduziu em 1.060+ projetos, 11,4 milhoes de pessoas impactadas e NPS de 88. Nao por acidente — por metodo.
    </p>

  </article>"""


# ── Main ─────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="Gera artigo de site NTICS")
    parser.add_argument("--slug", default="consciencia-e-proposito-m01")
    parser.add_argument("--titulo", default="Do Proposito ao Impacto: RS Estrategica como diferencial")
    parser.add_argument("--content-file", help="Arquivo .md com conteudo (futuro)")
    parser.add_argument("--skip-images", action="store_true", help="Pular geracao de imagens")
    args = parser.parse_args()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print(f"Artigo Site NTICS: {args.slug}")
    print("=" * 60)

    # Imagens
    imgs = {}
    if not args.skip_images:
        prompts = [
            {
                "key": "hero",
                "filename": f"hero-{args.slug}.jpg",
                "prompt": (
                    "Candid documentary photograph of a Brazilian corporate executive and a community leader "
                    "in an informal meeting outdoors in a urban park in Brazil, reviewing a social impact project report together. "
                    "Both engaged, genuine expressions. Natural golden hour lighting. "
                    "Shot with Canon EOS R5, 35mm f1.8, editorial documentary photography, ultra realistic. "
                    "No text no watermarks no logos."
                ),
            },
            {
                "key": "inline-rs-estrategica",
                "filename": "img-rs-estrategica.jpg",
                "prompt": (
                    "Photojournalistic photograph of a diverse group of Brazilian business professionals "
                    "in a modern conference room reviewing ESG sustainability charts on a laptop screen, "
                    "collaborative discussion, genuine engagement. Warm natural daylight from large windows. "
                    "Nikon Z6, 50mm f2, candid moment, editorial style. No text no watermarks no logos."
                ),
            },
            {
                "key": "inline-educacao",
                "filename": "img-educacao-territorio.jpg",
                "prompt": (
                    "Authentic documentary photograph of a Brazilian teacher leading an outdoor activity "
                    "with a group of elementary school children in a community park, hands-on learning session, "
                    "children engaged and curious. Overcast natural light. "
                    "Sony A7III, 35mm f2.8, photojournalistic, editorial photography. No text no watermarks no logos."
                ),
            },
        ]
        print("\n[1/2] Gerando imagens via Leonardo AI...")
        imgs = gerar_imagens(prompts, OUTPUT_DIR)
        print(f"  OK: {len(imgs)} imagens prontas")
    else:
        # Usar imagens existentes
        imgs = {
            "hero": f"hero-{args.slug}.jpg",
            "inline-rs-estrategica": "img-rs-estrategica.jpg",
            "inline-educacao": "img-educacao-territorio.jpg",
        }
        print("\n[1/2] Imagens: usando existentes (--skip-images)")

    # HTML
    print("\n[2/2] Montando HTML (body only)...")
    body_html = artigo_m01_body(imgs)
    full_html = montar_html_wrapper(args.titulo, body_html)

    html_path = OUTPUT_DIR / f"artigo-{args.slug}.html"
    html_path.write_text(full_html, encoding="utf-8")
    print(f"  Salvo: {html_path}")

    # Abrir no navegador
    print("\nPronto! Abrindo no navegador...")
    import subprocess
    subprocess.Popen(["start", "", str(html_path)], shell=True)


if __name__ == "__main__":
    main()
