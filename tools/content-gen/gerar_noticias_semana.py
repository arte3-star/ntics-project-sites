"""
gerar_noticias_semana.py — Curadoria semanal de noticias ESG/RSC para briefing do designer.

Fluxo:
  0. Anti-repeticao: le semanas anteriores (manifest.json v3 + descricao.txt v2)
  1. Perplexity sonar-pro: 3 queries — clientes NTICS, ESG Brasil, sustentabilidade global
  1b. Verificacao de URLs: HEAD requests com timeout 5s
  2. Claude Haiku: curadoria + redacao de todos os campos (8-10 noticias)
  3. Gera noticias.md (briefing designer) + manifest.json

Output:
  output/marketing/carrosseis/noticias/semana-YYYY-MM-DD/noticias.md
  output/marketing/carrosseis/noticias/semana-YYYY-MM-DD/manifest.json

Usage:
  python tools/content-gen/gerar_noticias_semana.py --semana 2026-05-12
  python tools/content-gen/gerar_noticias_semana.py --semana 2026-05-12 --skip-perplexity
  python tools/content-gen/gerar_noticias_semana.py --semana 2026-05-12 --n 8
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path

import urllib3
import requests
import yaml
from dotenv import load_dotenv

# Norton intercepta certificados SSL no Windows — desabilita verificacao local
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
    sys.stderr.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)

load_dotenv(override=True)

ROOT = Path(__file__).parent.parent.parent
OUTPUT_BASE = ROOT / "output" / "marketing" / "carrosseis" / "noticias"
CLIENTES_YAML = ROOT / "brand-book" / "data" / "clientes-newsroom.yaml"
CLICKUP_MAP = Path(__file__).parent / "noticias_clickup_map.yaml"

CLICKUP_BASE = "https://api.clickup.com/api/v2"


# ── Fase 0: Anti-repeticao ──────────────────────────────────────────────────

def load_exclusao(semana_atual: str) -> dict:
    """Le semanas anteriores e monta lista de exclusao."""
    urls: set[str] = set()
    titulos: list[str] = []
    empresas: list[str] = []

    for semana_dir in sorted(OUTPUT_BASE.glob("semana-*")):
        if semana_dir.name >= f"semana-{semana_atual}":
            continue

        # v3: manifest.json
        manifest_path = semana_dir / "manifest.json"
        if manifest_path.exists():
            try:
                data = json.loads(manifest_path.read_text(encoding="utf-8"))
                for item in data.get("noticias", []):
                    if item.get("url"):
                        urls.add(item["url"])
                    if item.get("titulo_noticia"):
                        titulos.append(item["titulo_noticia"][:60])
                    if item.get("empresa_cliente_ntics"):
                        empresas.append(item["empresa_cliente_ntics"])
            except Exception:
                pass

        # v2 legado: descricao.txt
        descricao_path = semana_dir / "descricao.txt"
        if descricao_path.exists():
            try:
                for line in descricao_path.read_text(encoding="utf-8").split("\n"):
                    stripped = line.strip()
                    if stripped.startswith("http"):
                        urls.add(stripped)
                    elif stripped.startswith("URL:"):
                        url = stripped[4:].strip()
                        if url:
                            urls.add(url)
            except Exception:
                pass

    return {
        "urls": list(urls)[-60:],
        "titulos": titulos[-21:],
        "empresas": empresas[-14:],
    }


# ── Fase 1: Perplexity ──────────────────────────────────────────────────────

PERPLEXITY_SYSTEM = """You are a research assistant for weekly ESG/CSR news curation.

Find POSITIVE news stories about companies making real, measurable progress. Focus on:
- Corporate social responsibility achievements and milestones
- ESG goals reached (emissions, water, diversity, governance)
- Sustainability programs with concrete results
- Social impact: education, health, community development
- Environmental wins: renewable energy, conservation, circular economy
- Positive company actions recognized by awards or certifications

For each story provide clearly:
1. Headline (the actual title from the source)
2. Company/Organization name
3. Source publication name
4. URL
5. Date
6. 2-3 sentence summary with specific data (numbers, percentages, names)

Format as a numbered list. Exclude negative news, controversies, vague pledges."""


def run_perplexity(queries: list[str], days: int, api_key: str) -> list[dict]:
    """Roda Perplexity sonar-pro para cada query. Retorna lista de resultados."""
    try:
        from openai import OpenAI
    except ImportError:
        print("ERROR: openai nao instalado. Execute: pip install openai")
        sys.exit(1)

    client = OpenAI(api_key=api_key, base_url="https://api.perplexity.ai")
    date_filter = (datetime.today() - timedelta(days=days)).strftime("%B %d, %Y")

    results = []
    for i, query in enumerate(queries, 1):
        print(f"  [{i}/{len(queries)}] {query[:70]}...")
        try:
            resp = client.chat.completions.create(
                model="sonar-pro",
                messages=[
                    {"role": "system", "content": PERPLEXITY_SYSTEM},
                    {
                        "role": "user",
                        "content": (
                            f"Find positive ESG/CSR/sustainability news published between "
                            f"{date_filter} and today. Search query: {query}"
                        ),
                    },
                ],
                temperature=0.2,
            )
            content = resp.choices[0].message.content
            citations = list(getattr(resp, "citations", None) or [])
            results.append({"query": query, "content": content, "citations": citations})
            print(f"         ok — {len(content)} chars, {len(citations)} citations")
        except Exception as e:
            print(f"         erro: {e}")
            results.append({"query": query, "content": "", "citations": [], "error": str(e)})

    return results


# ── Fase 1b: Verificacao de URLs ────────────────────────────────────────────

def verify_urls(citations: list[str]) -> dict[str, bool]:
    """HEAD requests para cada URL. Retorna {url: acessivel}."""
    unique = list(dict.fromkeys(u for u in citations if u.startswith("http")))
    if not unique:
        return {}

    print(f"\n  Verificando {len(unique)} URLs...")
    verified: dict[str, bool] = {}
    for url in unique:
        try:
            r = requests.head(
                url,
                timeout=5,
                allow_redirects=True,
                verify=False,
                headers={"User-Agent": "Mozilla/5.0"},
            )
            ok = r.status_code < 400
        except Exception:
            ok = False
        verified[url] = ok
        badge = "ok" if ok else "fail"
        print(f"         {badge}  {url[:90]}")

    ok_count = sum(1 for v in verified.values() if v)
    print(f"  {ok_count}/{len(verified)} URLs acessiveis")
    return verified


# ── Fase 2: Claude Haiku curadoria ─────────────────────────────────────────

HAIKU_PROMPT_TEMPLATE = """Voce e o editor do boletim semanal de noticias ESG/RSC da NTICS Projetos.

CONTEUDO PESQUISADO PELO PERPLEXITY:
{content_block}

URLS ENCONTRADAS (prefira as marcadas como [OK]):
{url_list}

HISTORICO — NAO REPETIR:
{exclusao_block}

TAREFA: Selecione as {n} melhores noticias e redija todos os campos abaixo.

CRITERIOS DE SELECAO (por ordem de prioridade):
1. Somente framing POSITIVO — conquistas, metas atingidas, lancamentos de programas.
   REJEITAR: crises, multas, quedas, demissoes, controversias, acusacoes.
2. Prioridade a noticias de empresas parceiras NTICS: {clientes_str}
3. Diversidade de TEMAS — nunca dois sobre o mesmo assunto (ex: nao duas sobre energia solar)
4. Diversidade de FONTES — maximo 2 noticias do mesmo veiculo
5. Preferencia por fontes reconhecidas: Reuters, BBC, G1, Valor Economico, Exame, Agencia Brasil, Folha, Estadao, El Pais, Le Monde
6. URLs marcadas [OK] tem prioridade sobre [FAIL]
7. Nao repetir URLs nem temas do historico acima

CAMPOS OBRIGATORIOS POR NOTICIA:
- titulo_noticia: titulo da noticia como publicado na midia (pode ser em portugues ou ingles)
- fonte: nome do veiculo de comunicacao (ex: "Valor Economico", "Reuters", "G1")
- url: URL exata (copie sem modificar)
- url_ok: true se a URL estava marcada [OK], false se [FAIL]
- area: tema livre em portugues (ex: "Energia Renovavel", "Saneamento Basico", "Diversidade e Inclusao")
- resumo: 3-4 frases — o que aconteceu, quem fez, qual o impacto numerico, por que importa para empresas. Use SOMENTE dados do conteudo acima — nunca invente numeros.
- card_titulo: maximo 8 palavras, framing positivo, sem ponto final
- card_texto: array de 3 strings, cada uma = 1 linha do card (maximo 10 palavras por linha, maximo 25 palavras no total das 3 linhas)
- legenda_post: caption completo para Instagram e LinkedIn — 2-3 paragrafos envolventes + hashtags em portugues (#ESG #Sustentabilidade #ResponsabilidadeSocial #NTICS). Tom: inspirador, concreto, acessivel para gestores de empresas brasileiras.
- empresa_cliente_ntics: nome da empresa se for cliente/parceiro NTICS, ou null

Responda SOMENTE com um JSON array valido, sem texto adicional, sem markdown code fences:
[
  {{
    "titulo_noticia": "...",
    "fonte": "...",
    "url": "...",
    "url_ok": true,
    "area": "...",
    "resumo": "...",
    "card_titulo": "...",
    "card_texto": ["linha 1", "linha 2", "linha 3"],
    "legenda_post": "...",
    "empresa_cliente_ntics": null
  }}
]"""


def curar_com_haiku(
    perplexity_results: list[dict],
    verified_urls: dict[str, bool],
    exclusao: dict,
    n_noticias: int,
    clientes_nomes: list[str],
    anthropic_key: str,
) -> list[dict]:
    """Haiku seleciona e redige todos os campos para n_noticias itens."""

    # Bloco de conteudo Perplexity (truncado para caber no contexto)
    content_parts = []
    all_citations: list[str] = []
    for r in perplexity_results:
        if r.get("content"):
            content_parts.append(f"=== Query: {r['query']} ===\n{r['content']}")
        for url in r.get("citations", []):
            if url not in all_citations:
                all_citations.append(url)
    content_block = "\n\n".join(content_parts)[:7000]

    # Lista de URLs com status
    url_lines = []
    for url in all_citations[:60]:
        ok = verified_urls.get(url, False)
        url_lines.append(f"[{'OK' if ok else 'FAIL'}] {url}")
    url_list = "\n".join(url_lines) if url_lines else "Nenhuma URL retornada pelo Perplexity."

    # Bloco de exclusao
    excl_parts = []
    if exclusao["urls"]:
        excl_parts.append("URLs ja usadas (descartar): " + "; ".join(list(exclusao["urls"])[:30]))
    if exclusao["titulos"]:
        excl_parts.append("Temas/titulos ja cobertos (evitar repetir): " + "; ".join(exclusao["titulos"][:15]))
    if exclusao["empresas"]:
        excl_parts.append("Empresas ja destacadas recentemente (diversificar): " + "; ".join(exclusao["empresas"][:10]))
    exclusao_block = "\n".join(excl_parts) if excl_parts else "Nenhum historico anterior."

    clientes_str = ", ".join(clientes_nomes[:15])

    prompt = HAIKU_PROMPT_TEMPLATE.format(
        content_block=content_block,
        url_list=url_list,
        exclusao_block=exclusao_block,
        n=n_noticias,
        clientes_str=clientes_str,
    )

    print("\n  Claude Haiku curando e redigindo noticias...")
    r = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": anthropic_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        json={
            "model": "claude-haiku-4-5-20251001",
            "max_tokens": 7000,
            "messages": [{"role": "user", "content": prompt}],
        },
        timeout=120,
        verify=False,
    )
    if not r.ok:
        raise RuntimeError(f"Claude API error {r.status_code}: {r.text[:400]}")

    raw = r.json()["content"][0]["text"].strip()

    # Strip markdown code fences if present
    raw = re.sub(r"^```[a-z]*\n?", "", raw)
    raw = re.sub(r"\n?```$", "", raw.strip())

    return json.loads(raw)


# ── Fase 3: Documento markdown ─────────────────────────────────────────────

_MESES = [
    "janeiro", "fevereiro", "marco", "abril", "maio", "junho",
    "julho", "agosto", "setembro", "outubro", "novembro", "dezembro",
]


def _periodo_label(semana: str) -> str:
    try:
        inicio = datetime.strptime(semana, "%Y-%m-%d")
        fim = inicio + timedelta(days=6)
        if inicio.month == fim.month:
            return f"{inicio.day} a {fim.day} de {_MESES[inicio.month - 1]} de {inicio.year}"
        return (
            f"{inicio.day} de {_MESES[inicio.month - 1]} "
            f"a {fim.day} de {_MESES[fim.month - 1]} de {fim.year}"
        )
    except Exception:
        return semana


def gerar_documento(noticias: list[dict], semana: str, output_dir: Path) -> Path:
    """Gera noticias.md + manifest.json na pasta da semana."""
    periodo = _periodo_label(semana)
    hoje = datetime.now().strftime("%Y-%m-%d")
    clientes_desta_semana = [n["empresa_cliente_ntics"] for n in noticias if n.get("empresa_cliente_ntics")]

    linhas = [
        f"# Noticias da Semana — {periodo}",
        "",
        f"> Gerado em {hoje} | {len(noticias)} noticias selecionadas",
    ]
    if clientes_desta_semana:
        linhas.append(f"> Clientes NTICS nesta edicao: {', '.join(clientes_desta_semana)}")
    linhas += ["", "---", ""]

    for i, n in enumerate(noticias, 1):
        url_badge = "URL verificada" if n.get("url_ok") else "URL nao verificada"
        cliente_tag = f" | Cliente NTICS: {n['empresa_cliente_ntics']}" if n.get("empresa_cliente_ntics") else ""

        card_texto = n.get("card_texto", [])
        if isinstance(card_texto, list):
            card_texto_fmt = "\n".join(card_texto)
        else:
            card_texto_fmt = str(card_texto)

        linhas += [
            f"## {i}. {n['titulo_noticia']}",
            "",
            f"**Fonte:** {n['fonte']} | [Ver noticia]({n['url']})  [{url_badge}]{cliente_tag}",
            f"**Area:** {n['area']}",
            "",
            "**Resumo:**",
            n["resumo"],
            "",
            f"**Card — Titulo:** {n['card_titulo']}",
            "**Card — Texto:**",
            card_texto_fmt,
            "",
            "**Legenda do post:**",
            n["legenda_post"],
            "",
            "---",
            "",
        ]

    md_content = "\n".join(linhas)
    md_path = output_dir / "noticias.md"
    md_path.write_text(md_content, encoding="utf-8")

    manifest = {
        "semana": semana,
        "gerado_em": datetime.now().isoformat(),
        "n_noticias": len(noticias),
        "noticias": noticias,
    }
    json_path = output_dir / "manifest.json"
    json_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    return md_path


# ── ClickUp: lookup + postagem ──────────────────────────────────────────────

def lookup_clickup_tasks(semana: str) -> dict | None:
    """Retorna o registro do mapa YAML para a semana dada (YYYY-MM-DD), ou None."""
    if not CLICKUP_MAP.exists():
        return None
    data = yaml.safe_load(CLICKUP_MAP.read_text(encoding="utf-8"))
    for entry in data.get("semanas", []):
        if entry.get("semana_inicio") == semana:
            return entry
    return None


def postar_no_clickup(md_path: Path, task_id: str, clickup_key: str, task_label: str) -> bool:
    """Atualiza a descricao da task ClickUp com o conteudo do noticias.md."""
    content = md_path.read_text(encoding="utf-8")
    url = f"{CLICKUP_BASE}/task/{task_id}"
    headers = {
        "Authorization": clickup_key,
        "Content-Type": "application/json",
    }
    payload = {"description": content}
    r = requests.put(url, headers=headers, json=payload, timeout=30, verify=False)
    if r.ok:
        print(f"  ok — {task_label} atualizada: https://app.clickup.com/t/{task_id}")
        return True
    else:
        print(f"  erro {r.status_code} ao atualizar {task_label}: {r.text[:200]}")
        return False


# ── Main ────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Gera documento de noticias ESG da semana")
    parser.add_argument("--semana", required=True, help="Data de inicio da semana (YYYY-MM-DD)")
    parser.add_argument("--skip-perplexity", action="store_true", help="Reutiliza raw_perplexity.json do cache")
    parser.add_argument("--n", type=int, default=9, help="Numero de noticias a selecionar (padrao: 9)")
    parser.add_argument("--post-clickup", action="store_true", help="Posta o documento nas tasks ClickUp da semana")
    args = parser.parse_args()

    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    perplexity_key = os.getenv("PERPLEXITY_API_KEY")

    if not anthropic_key:
        print("ERROR: ANTHROPIC_API_KEY nao configurado no .env")
        sys.exit(1)

    OUTPUT_BASE.mkdir(parents=True, exist_ok=True)
    output_dir = OUTPUT_BASE / f"semana-{args.semana}"
    output_dir.mkdir(parents=True, exist_ok=True)
    cache_path = output_dir / "raw_perplexity.json"

    # Carrega clientes NTICS para queries e curadoria
    clientes_nomes: list[str] = []
    if CLIENTES_YAML.exists():
        clientes_data = yaml.safe_load(CLIENTES_YAML.read_text(encoding="utf-8"))
        clientes_nomes = [c["nome"] for c in clientes_data.get("clientes", [])]

    # ── Fase 0 ──
    print("=" * 60)
    print(f"NOTICIAS DA SEMANA — {args.semana}")
    print("=" * 60)
    print("\nFase 0: Carregando historico de semanas anteriores...")
    exclusao = load_exclusao(args.semana)
    print(
        f"  {len(exclusao['urls'])} URLs | "
        f"{len(exclusao['titulos'])} titulos | "
        f"{len(exclusao['empresas'])} empresas no historico"
    )

    # ── Fase 1 ──
    clientes_query = " OR ".join(clientes_nomes[:12]) if clientes_nomes else "ESG companies"
    queries = [
        f"positive ESG sustainability news this week {clientes_query} achievement award 2026",
        "boas noticias responsabilidade social ESG empresas Brasil semana sustentabilidade conquista resultado",
        "positive sustainability ESG corporate social responsibility good news world week 2026 milestone impact",
    ]

    if args.skip_perplexity and cache_path.exists():
        print(f"\nFase 1: Reutilizando cache ({cache_path.name})")
        perplexity_results = json.loads(cache_path.read_text(encoding="utf-8"))
    else:
        if not perplexity_key:
            print("ERROR: PERPLEXITY_API_KEY nao configurado no .env")
            sys.exit(1)
        print(f"\nFase 1: Pesquisando no Perplexity ({len(queries)} queries)...")
        perplexity_results = run_perplexity(queries, days=7, api_key=perplexity_key)
        cache_path.write_text(
            json.dumps(perplexity_results, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    # ── Fase 1b ──
    all_citations: list[str] = []
    for r in perplexity_results:
        for url in r.get("citations", []):
            if url not in all_citations:
                all_citations.append(url)

    print(f"\nFase 1b: Verificacao de URLs ({len(all_citations)} encontradas)...")
    verified_urls = verify_urls(all_citations)

    # ── Fase 2 ──
    print("\nFase 2: Curadoria e redacao com Claude Haiku...")
    noticias = curar_com_haiku(
        perplexity_results, verified_urls, exclusao, args.n, clientes_nomes, anthropic_key
    )
    print(f"  {len(noticias)} noticias selecionadas e redigidas")

    # ── Fase 3 ──
    print("\nFase 3: Gerando documento...")
    md_path = gerar_documento(noticias, args.semana, output_dir)

    clientes_semana = [n["empresa_cliente_ntics"] for n in noticias if n.get("empresa_cliente_ntics")]
    urls_ok = sum(1 for n in noticias if n.get("url_ok"))

    print(f"\n{'=' * 60}")
    print(f"CONCLUIDO — {len(noticias)} noticias | semana {args.semana}")
    print(f"  URLs verificadas: {urls_ok}/{len(noticias)}")
    if clientes_semana:
        print(f"  Clientes NTICS: {', '.join(clientes_semana)}")
    print(f"  Documento: {md_path}")

    # ── Fase 4: ClickUp (opcional) ──
    entry = lookup_clickup_tasks(args.semana)
    if entry:
        numero = entry.get("numero", "?")
        print(f"\n  Semana mapeada: {numero} ({entry.get('semana_inicio')})")
        print(f"  Carrossel task: {entry.get('carrossel_task_id') or 'nao mapeada'}")
        print(f"  Artigo task:    {entry.get('artigo_task_id') or 'nao mapeada'}")
    else:
        print(f"\n  Semana {args.semana} nao encontrada em noticias_clickup_map.yaml.")
        print("  Adicione a entrada no mapa e rode com --post-clickup.")

    if args.post_clickup:
        clickup_key = os.getenv("CLICKUP_API_KEY")
        if not clickup_key:
            print("\nERROR: CLICKUP_API_KEY nao configurado no .env — nao foi possivel postar.")
        elif not entry:
            print("\nERROR: semana nao mapeada — impossivel postar no ClickUp.")
        else:
            print(f"\nFase 4: Postando no ClickUp ({numero})...")
            if entry.get("carrossel_task_id"):
                postar_no_clickup(md_path, entry["carrossel_task_id"], clickup_key, f"Carrossel {numero}")
            if entry.get("artigo_task_id"):
                postar_no_clickup(md_path, entry["artigo_task_id"], clickup_key, f"Artigo {numero}")
    else:
        print(f"\n  Para postar no ClickUp: adicione --post-clickup ao comando")

    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
