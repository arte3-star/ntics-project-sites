"""
gerar_carrossel_noticias_v2.py — Pipeline completo de carrossel de noticias ESG.

📚 Ref: workflows/marketing/referencia/leonardo_ai_core.md — consulte em caso de erro ou
dúvida sobre payloads, modos, erros conhecidos (duplicação, acentos, init_image vs image_reference).

Fluxo:
  1. Anti-repeticao: varre carrosseis anteriores
  2. Serper /news: busca noticias reais com URLs verificadas + Claude redige campos do carrossel
     (titulo, resumo, texto_card, highlight_words, fonte, url, imageUrl, categoria, cena_foto)
  3. Imagens: imageUrl do Serper /news (thumbnail real da materia) → fallback Leonardo AI
     Fotos salvas em .tmp/.../fotos_originais/ E copiadas para output/.../fotos/ (para artigo)
  4. Cards: Leonardo AI gera cada card completo (foto + layout)
     Pillow usado APENAS para colar logo NTICS no CTA
  5. Entrega: cards + descricao.txt + manifest.json

Usage:
  python tools/content-gen/gerar_carrossel_noticias_v2.py --semana 2026-04-05
  python tools/content-gen/gerar_carrossel_noticias_v2.py --semana 2026-04-05 --tematica "economia circular"
  python tools/content-gen/gerar_carrossel_noticias_v2.py --semana 2026-04-05 --skip-perplexity --skip-images
"""

import argparse
import hashlib
import json
import os
import re
import sys
import textwrap
import time
from pathlib import Path

import requests
import yaml
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
    sys.stderr.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
else:
    sys.stdout = open(sys.stdout.fileno(), 'w', encoding='utf-8', buffering=1)

load_dotenv(override=True)

# ── Constantes visuais ──────────────────────────────────────────────────────

W, H = 1856, 2304

TEAL = (0, 95, 115)
YELLOW = (245, 184, 0)
WHITE = (255, 255, 255)
GREEN = (61, 170, 53)
TEAL_BAR = (0, 165, 184)
PINK = (212, 26, 106)
ORANGE = (232, 100, 40)

BADGE_COLORS = {
    "ESTRATEGIA CORPORATIVA": (61, 170, 53),
    "INFRAESTRUTURA": (61, 170, 53),
    "RECURSOS HIDRICOS": (0, 120, 180),
    "EDUCACAO": (200, 170, 0),
    "COOPERACAO GLOBAL": (130, 60, 180),
    "FINANCAS VERDES": (61, 170, 53),
    "ENERGIA": (232, 100, 40),
    "BIODIVERSIDADE": (61, 170, 53),
    "TECNOLOGIA": (0, 165, 184),
    "AGRONEGOCIO": (61, 170, 53),
}

FONT_BOLD = "C:/Windows/Fonts/segoeuib.ttf"
FONT_REGULAR = "C:/Windows/Fonts/segoeui.ttf"
FONT_ITALIC = "C:/Windows/Fonts/segoeuii.ttf"

PHOTO_END = 0.55
GRAD_END = 0.72
BADGE_Y = 0.725
HEADLINE_Y = 0.755
BODY_Y = 0.86
SOURCE_Y = 0.945
BAR_START = 0.975

CARROSSEIS_DIR = Path("output/marketing/carrosseis/noticias")
CARROSSEIS_TMP = Path(".tmp/marketing/carrosseis")  # historico legado para anti-repeticao

HEADERS_BROWSER = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "text/html,application/xhtml+xml,*/*",
}


# ══════════════════════════════════════════════════════════════════════════════
# FASE 0: ANTI-REPETICAO
# ══════════════════════════════════════════════════════════════════════════════

_PALAVRAS_COMUNS = {
    "Uma", "Um", "Os", "As", "Em", "No", "Na", "De", "Do", "Da", "Com", "Para",
    "Por", "Que", "São", "Nova", "Novo", "Este", "Esta", "Seu", "Sua", "Mais",
    "Nos", "Nas", "Dos", "Das", "Pelo", "Pela", "Pelos", "Pelas", "Num", "Numa",
}


def _extrair_empresa(titulo):
    """Extrai nome de empresa/organização do título (primeira palavra capitalizada não-comum)."""
    for word in titulo.split():
        w = word.strip(".,;:!?()[]'\"")
        if len(w) > 2 and w[0].isupper() and not w.isupper() and w not in _PALAVRAS_COMUNS:
            return w
    return None


def coletar_historico():
    """Varre manifest.json e descricao.txt anteriores para anti-repeticao completa.

    Lê manifest.json (fonte primária — dados estruturados) e descricao.txt (fallback legado).
    Retorna URLs, títulos, fontes E nomes de empresas/organizações já destacadas.
    """
    urls_usadas = set()
    titulos_usados = set()
    fontes_usadas = set()
    empresas_destacadas = set()  # nomes de empresas/orgs já cobertas (ex: "Natura", "Zurich")

    dirs_para_varrer = [d for d in [CARROSSEIS_DIR, CARROSSEIS_TMP] if d.exists()]
    if not dirs_para_varrer:
        return urls_usadas, titulos_usados, fontes_usadas, empresas_destacadas

    for base_dir in dirs_para_varrer:
        # ── Fonte primária: manifest.json (dados estruturados) ──
        for manifest_file in base_dir.rglob("manifest.json"):
            try:
                manifest = json.loads(manifest_file.read_text(encoding="utf-8", errors="replace"))
            except Exception:
                continue
            if not isinstance(manifest, dict):
                continue
            for noticia in manifest.get("noticias", []):
                url = noticia.get("url_real") or noticia.get("url", "")
                if url:
                    urls_usadas.add(url.rstrip(".,;)"))
                titulo = noticia.get("titulo", "")
                if titulo:
                    titulos_usados.add(titulo)
                    empresa = _extrair_empresa(titulo)
                    if empresa:
                        empresas_destacadas.add(empresa)
                fonte = noticia.get("fonte", "")
                if fonte:
                    fontes_usadas.add(fonte.strip())

        # ── Fallback: descricao.txt (cobre carrosseis sem manifest) ──
        for desc_file in base_dir.rglob("descricao.txt"):
            try:
                texto = desc_file.read_text(encoding="utf-8", errors="replace")
            except Exception:
                continue
            for url in re.findall(r'https?://\S+', texto):
                urls_usadas.add(url.rstrip('.,;)'))
            for match in re.findall(r'\.jpg\s*[—-]\s*(.+)', texto):
                titulo = match.strip()
                if not titulo.lower().startswith(("capa:", "cta:")):
                    titulos_usados.add(titulo)
                    empresa = _extrair_empresa(titulo)
                    if empresa:
                        empresas_destacadas.add(empresa)
            for match in re.findall(r'Fonte:\s*(.+)', texto):
                fontes_usadas.add(match.strip())

    return urls_usadas, titulos_usados, fontes_usadas, empresas_destacadas


# ══════════════════════════════════════════════════════════════════════════════
# FASE 1: PESQUISA DE NOTICIAS (PERPLEXITY)
# ══════════════════════════════════════════════════════════════════════════════

def carregar_clientes_ntics():
    """Carrega mapa cliente->dominio de brand-book/data/clientes-newsroom.yaml.

    Retorna lista de dicts com {nome, dominio, aliases} ou [] se arquivo nao existir.
    """
    yaml_path = Path("brand-book/data/clientes-newsroom.yaml")
    if not yaml_path.exists():
        print("  [CLIENTES] YAML nao encontrado, pulando priorizacao de cliente")
        return []
    try:
        data = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
        return data.get("clientes", []) or []
    except Exception as e:
        print(f"  [CLIENTES] Erro ao ler YAML: {e}")
        return []


def pesquisar_noticias(tematica=None, urls_excluir=None, titulos_excluir=None, fontes_excluir=None, empresas_excluir=None):
    """Busca 7 noticias ESG via Serper /news (URLs reais verificadas) + Claude para redigir campos.

    Prioridade: primeiro roda queries `site:{dominio}` para clientes NTICS (carregados de
    brand-book/data/clientes-newsroom.yaml). Depois roda queries genericas ESG como fallback.
    Candidatos de cliente sao tagueados com is_cliente_ntics=True + cliente_nome, e o Claude
    recebe instrucao para priorizar esses ao selecionar 7.
    """
    serper_key = os.getenv("SERPER_API_KEY")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    if not serper_key:
        raise RuntimeError("SERPER_API_KEY nao definida no .env")
    if not anthropic_key:
        raise RuntimeError("ANTHROPIC_API_KEY nao definida no .env")

    # ── FASE 1A: Serper /news — busca noticias reais com URLs verificadas ──────
    from collections import Counter

    clientes_ntics = carregar_clientes_ntics()

    queries = [
        "ESG sustentabilidade responsabilidade social corporativa Brasil 2026",
        "ESG sustainability corporate social responsibility impact 2026",
        "energia renovavel biodiversidade financas verdes economia circular Brasil 2026",
    ]
    if tematica:
        queries.insert(0, f"{tematica} ESG sustentabilidade 2026")

    candidatos_raw = {}  # dedup por URL

    # Camada 1 — queries por cliente (site: filter) — prioridade
    if clientes_ntics:
        print(f"  Buscando noticias por cliente NTICS ({len(clientes_ntics)} dominios)...")
        for cliente in clientes_ntics:
            nome = cliente.get("nome", "")
            dominio = cliente.get("dominio", "")
            if not dominio:
                continue
            q = f"site:{dominio} ESG sustentabilidade responsabilidade social 2026"
            payload = json.dumps({"q": q, "hl": "pt", "gl": "br", "num": 5, "tbs": "qdr:m"}).encode()
            try:
                r = requests.post(
                    "https://google.serper.dev/news",
                    data=payload,
                    headers={"X-API-KEY": serper_key, "Content-Type": "application/json"},
                    timeout=15,
                )
                if not r.ok:
                    continue
                items = r.json().get("news", [])
                for item in items:
                    url = item.get("link", "")
                    if url and url not in candidatos_raw:
                        item["is_cliente_ntics"] = True
                        item["cliente_nome"] = nome
                        candidatos_raw[url] = item
                if items:
                    print(f"    {nome}: {len(items)} candidatos")
            except Exception:
                continue

    # Camada 2 — queries genericas ESG (fallback + diversidade)
    print("  Buscando noticias ESG genericas...")
    for q in queries:
        payload = json.dumps({"q": q, "hl": "pt", "gl": "br", "num": 10, "tbs": "qdr:m"}).encode()
        r = requests.post(
            "https://google.serper.dev/news",
            data=payload,
            headers={"X-API-KEY": serper_key, "Content-Type": "application/json"},
            timeout=15,
        )
        if not r.ok:
            print(f"  Serper erro {r.status_code} para query: {q[:50]}")
            continue
        for item in r.json().get("news", []):
            url = item.get("link", "")
            if url and url not in candidatos_raw:
                item["is_cliente_ntics"] = False
                candidatos_raw[url] = item

    n_cliente = sum(1 for i in candidatos_raw.values() if i.get("is_cliente_ntics"))
    print(f"  {len(candidatos_raw)} candidatos unicos ({n_cliente} de clientes NTICS)")

    # ── Verificar URLs (HTTP 200) ──────────────────────────────────────────────
    candidatos_ok = []
    urls_excluir_set = set(urls_excluir or [])
    fontes_excluir_set = set(f.lower() for f in (fontes_excluir or []))

    for url, item in candidatos_raw.items():
        if url in urls_excluir_set:
            continue
        fonte = item.get("source", "").lower()
        if any(f in fonte for f in fontes_excluir_set):
            continue
        try:
            head = requests.head(url, headers=HEADERS_BROWSER, timeout=6, allow_redirects=True)
            if head.status_code < 400:
                item["url_verificada"] = True
                candidatos_ok.append(item)
            else:
                pass  # descarta silenciosamente URLs mortas
        except Exception:
            item["url_verificada"] = None  # timeout — inclui mesmo assim, URL pode ser valida
            candidatos_ok.append(item)

    print(f"  {len(candidatos_ok)} candidatos com URL acessivel")

    if len(candidatos_ok) < 7:
        raise RuntimeError(f"Serper retornou apenas {len(candidatos_ok)} noticias acessiveis — insuficiente para 7 cards")

    # ── FASE 1B: Claude seleciona 7 e redige campos do carrossel ─────────────
    candidatos_txt = ""
    for i, item in enumerate(candidatos_ok):
        tag_cliente = ""
        if item.get("is_cliente_ntics"):
            tag_cliente = f"[CLIENTE NTICS: {item.get('cliente_nome','')}] "
        candidatos_txt += (
            f"[{i+1}] {tag_cliente}fonte={item.get('source','')} | url={item.get('link','')}\n"
            f"     titulo={item.get('title','')}\n"
            f"     snippet={item.get('snippet','')[:200]}\n"
            f"     imageUrl={item.get('imageUrl','')}\n\n"
        )

    titulos_excluidos_hint = ""
    if titulos_excluir or empresas_excluir:
        partes = []
        if empresas_excluir:
            lista = ", ".join(sorted(empresas_excluir))
            partes.append(
                f"EMPRESAS/ORGANIZACOES JA DESTACADAS — DESCARTE AUTOMATICO: {lista}\n"
                f"Regra absoluta: se o titulo OU snippet do candidato mencionar qualquer uma dessas empresas/organizacoes, "
                f"DESCARTAR imediatamente, independente do angulo ou URL. Mesmo empresa = mesma historia para o leitor."
            )
        if titulos_excluir:
            todos = "; ".join(titulos_excluir)
            partes.append(
                f"TITULOS/TEMAS JA COBERTOS (nao repetir tema, mesmo que URL seja diferente): {todos}"
            )
        titulos_excluidos_hint = "\n" + "\n".join(partes)

    prompt_claude = f"""Você é o editor do carrossel ESG semanal da NTICS Projetos.

Abaixo estão {len(candidatos_ok)} noticias ESG reais coletadas pelo Serper (Google News). Selecione as 7 melhores e retorne os dados para o carrossel.

CRITERIO DE SELECAO (em ordem de prioridade):
1. PRIORIDADE MAXIMA: noticias marcadas com [CLIENTE NTICS: Nome] sao de patrocinadores/clientes da NTICS Projetos — selecione quantas estiverem POSITIVAS e relevantes (ideal 3-4 de clientes, mas nao force se nao houver qualidade). Se houver menos de 3 noticias de clientes positivas, completa com as melhores genericas ESG — NAO forcar noticia fraca so porque e cliente.
2. SOMENTE NOTICIAS POSITIVAS. Cada noticia deve celebrar um avanco, conquista, resultado ou iniciativa inspiradora. REJEITAR noticias com framing negativo — palavras como "trava", "enfrenta", "sofre", "cai", "desacelera", "crise", "problema", "fracasso" no titulo/snippet sao sinal de rejeicao. Regra vale TAMBEM para noticias de cliente — nao selecionar noticia negativa de cliente (ex: multa ambiental, acidente).
3. Impacto concreto: dados, numeros, metas alcancadas, projetos lancados
4. Tom positivo e inspirador para gestores de empresas brasileiras
5. Diversidade TEMATICA: cada noticia deve cobrir um TEMA diferente (ex: nao escolher duas sobre energia, ou duas sobre reportes/regulacao). Buscar variedade: uma de biodiversidade, uma de tecnologia, uma de educacao, etc.
6. Diversidade de FONTES: no maximo 2 noticias do mesmo veiculo/fonte
7. Categorias DIFERENTES para cada noticia{titulos_excluidos_hint}

CANDIDATOS:
{candidatos_txt}

Para cada uma das 7 noticias selecionadas, retorne um JSON com os campos:
- titulo: titulo curto (max 10 palavras), framing positivo
- resumo: 3-4 frases — O QUE aconteceu, QUEM fez, QUAL O IMPACTO, POR QUE importa para empresas brasileiras. Use APENAS informacoes do snippet — nao invente dados.
- texto_card: max 2 frases, 25 palavras, direto e positivo
- fonte: nome do veiculo (campo "fonte=" do candidato)
- url: URL exata do candidato (campo "url=" — nao altere)
- imageUrl: imageUrl exata do candidato (campo "imageUrl=" — nao altere)
- categoria: uma entre ESTRATEGIA CORPORATIVA, INFRAESTRUTURA, RECURSOS HIDRICOS, EDUCACAO, COOPERACAO GLOBAL, FINANCAS VERDES, ENERGIA, BIODIVERSIDADE, TECNOLOGIA, AGRONEGOCIO
- highlight_words: lista de 2-4 palavras individuais do titulo para destacar em amarelo
- cena_foto: descricao em ingles para Leonardo AI gerar foto hiperrealista do card. REGRA PRINCIPAL: use o contexto real da noticia — empresa especifica, local geografico, setor, produto ou evento mencionado no titulo/snippet — para criar uma cena visual concreta e especifica. NAO seja generico. Se a noticia menciona uma empresa (ex: FIEB, KPMG, Sabesp), local (ex: Bahia, Sao Paulo, Amazonia) ou tema (ex: energia solar, saneamento, construcao), use isso como ancora visual. Estrutura: [angulo de camera] + [objeto/local especifico da noticia] + [elementos visuais concretos] + [condicao de luz]. Pode ter ou nao pessoas conforme o contexto — se a noticia e sobre um evento ou premiacao, pessoas fazem sentido; se e sobre infraestrutura ou natureza, foque no ambiente. NUNCA: escritorio generco, mesa de reuniao generica, tela de computador, stock photo corporativa sem contexto. Ex bom: "aerial view of FIEB industrial complex Bahia Brazil at golden hour, modern factory buildings with solar panels on rooftops, green vegetation surrounding the facility, warm amber light"; "wide shot of Sabesp water treatment plant Sao Paulo, large circular treatment tanks reflecting blue sky, modern infrastructure alongside Tiete river, morning light"

Responda SOMENTE com um JSON array valido, sem texto adicional."""

    print("  Claude selecionando e redigindo 7 noticias...")
    r = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": anthropic_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        json={
            "model": "claude-haiku-4-5-20251001",
            "max_tokens": 4096,
            "messages": [{"role": "user", "content": prompt_claude}],
        },
        timeout=60,
    )
    if not r.ok:
        raise RuntimeError(f"Claude API error {r.status_code}: {r.text[:300]}")

    content = r.json()["content"][0]["text"]

    # Parse JSON
    if "```json" in content:
        json_text = content.split("```json")[1].split("```")[0].strip()
    elif "```" in content:
        json_text = content.split("```")[1].split("```")[0].strip()
    else:
        start = content.find("[")
        end = content.rfind("]")
        json_text = content[start:end + 1] if start != -1 else content.strip()

    try:
        noticias = json.loads(json_text)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Claude retornou JSON invalido: {e}\n{content[:500]}")

    # Normalizar
    for n in noticias:
        if "categoria" in n:
            n["categoria"] = n["categoria"].replace("_", " ").strip().upper()
        n["url_real"] = n.get("url", "")
        n["url_verificada"] = True  # URL vem do Serper — real e verificada
        hw = n.get("highlight_words", [])
        if isinstance(hw, str):
            hw = re.sub(r'\*\*(.+?)\*\*', r'\1', hw)
            n["highlight_words"] = [w.strip() for w in re.split(r'[,;]', hw) if w.strip()]

    # Garantir diversidade de fontes
    contagem_fontes: Counter = Counter()
    noticias_filtradas = []
    for n in noticias:
        fonte = n.get("fonte", "").strip()
        if contagem_fontes[fonte] < 2:
            noticias_filtradas.append(n)
            contagem_fontes[fonte] += 1
        else:
            print(f"  fonte repetida removida: {fonte}")
    noticias = noticias_filtradas

    print(f"  {len(noticias)} noticias selecionadas (URLs reais verificadas)")
    return noticias


# ══════════════════════════════════════════════════════════════════════════════
# FASE 2: BUSCA DE IMAGENS (Serper → Leonardo)
# ══════════════════════════════════════════════════════════════════════════════

def upload_init_image_leonardo(api_key, image_path):
    """Faz upload de imagem de referencia para o Leonardo AI. Retorna o init_image_id."""
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": f"Bearer {api_key}",
    }
    # Passo 1: solicitar URL de upload
    resp = requests.post(
        "https://cloud.leonardo.ai/api/rest/v1/init-image",
        headers=headers,
        json={"extension": "jpg"},
        timeout=15,
    )
    if not resp.ok:
        return None
    upload_data = resp.json().get("uploadInitImage", {})
    image_id = upload_data.get("id")
    upload_url = upload_data.get("url")
    fields = upload_data.get("fields", {})
    if not image_id or not upload_url:
        return None

    # Passo 2: fazer upload para S3
    if isinstance(fields, str):
        import json as _json
        try:
            fields = _json.loads(fields)
        except Exception:
            fields = {}
    form_data = {k: v for k, v in fields.items()} if isinstance(fields, dict) else {}
    with open(image_path, "rb") as f:
        upload_resp = requests.post(
            upload_url,
            data=form_data,
            files={"file": ("image.jpg", f, "image/jpeg")},
            timeout=30,
        )
    if upload_resp.status_code not in (200, 204):
        return None

    return image_id


def gerar_leonardo(prompt_descricao, init_image_path=None):
    """Gera imagem via Leonardo AI.
    - Se init_image_path fornecido: usa img2img com a foto real como referencia (init_strength=0.35)
    - Caso contrario: gera foto do zero a partir do prompt
    Retorna URL da imagem gerada.
    """
    api_key = os.getenv("LEONARDO_API_KEY")
    if not api_key:
        return None

    prompt = (
        f"A hyperrealistic photograph of {prompt_descricao}, "
        "candid unposed moment, Canon 50mm f1.4 natural bokeh warm tones, "
        "visible film grain ISO 800, natural imperfect lighting, "
        "NOT AI generated NOT illustration. Landscape orientation."
    )

    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": f"Bearer {api_key}",
    }

    params = {
        "prompt": prompt,
        "width": 1472,
        "height": 832,
        "quantity": 1,
        "prompt_enhance": "OFF",
    }

    # img2img: se tem foto de referencia, fazer upload e usar como init_image
    if init_image_path:
        print("    Leonardo: fazendo upload da imagem de referencia...")
        init_id = upload_init_image_leonardo(api_key, init_image_path)
        if init_id:
            params["init_image_id"] = init_id
            params["init_strength"] = 0.35  # 0.35 = mantem composicao da foto, adapta ao prompt
            print(f"    Leonardo: img2img com init_image_id={init_id[:8]}...")
        else:
            print("    Leonardo: upload falhou, gerando do zero...")

    payload = {
        "model": "nano-banana-2",
        "parameters": params,
        "public": False,
    }

    try:
        resp = requests.post(
            "https://cloud.leonardo.ai/api/rest/v2/generations",
            headers=headers, json=payload, timeout=30,
        )
        if not resp.ok:
            return None

        data = resp.json()
        if isinstance(data, list):
            return None  # erro da API (ex: tokens insuficientes)

        gen_id = None
        for v in data.values():
            if isinstance(v, dict):
                gen_id = v.get("generationId") or v.get("id")
                if gen_id:
                    break

        if not gen_id:
            return None

        print("    Leonardo: aguardando 55s...")
        time.sleep(55)

        poll_url = f"https://cloud.leonardo.ai/api/rest/v1/generations/{gen_id}"
        for _ in range(12):
            resp = requests.get(poll_url, headers={"accept": "application/json", "authorization": f"Bearer {api_key}"}, timeout=15)
            job = resp.json().get("generations_by_pk", {})
            if job.get("status") == "COMPLETE":
                images = job.get("generated_images", [])
                if images:
                    return images[0]["url"]
            elif job.get("status") == "FAILED":
                return None
            time.sleep(10)
    except Exception:
        pass
    return None


def baixar_imagem(url, path):
    """Baixa imagem de URL para arquivo local. Retorna True se sucesso."""
    try:
        resp = requests.get(url, headers=HEADERS_BROWSER, timeout=20)
        if resp.status_code == 200 and len(resp.content) > 5000:
            path.write_bytes(resp.content)
            return True
    except Exception:
        pass
    return False


def buscar_melhor_imagem(noticia, output_dir):
    """Busca imagem editorial para o card.

    Cascata:
    0. imageUrl do Serper /news (thumbnail real da materia — vem direto da noticia)
    1. Leonardo AI (gera foto realista a partir de cena_foto — fallback)

    Retorna (path_local, fonte_descricao) ou (None, None).
    """
    titulo = noticia.get("titulo", "")
    img_path = output_dir / "foto_temp.jpg"

    # ── Camada 0: imageUrl do Serper /news (thumbnail real da materia) ──
    image_url = noticia.get("imageUrl", "")
    if image_url:
        try:
            if baixar_imagem(image_url, img_path):
                im = Image.open(img_path)
                w, h = im.width, im.height
                if w >= 300 and h >= 200:
                    print(f"    ✓ Serper imageUrl OK ({w}x{h})")
                    return img_path, "Serper (imageUrl noticia)"
                else:
                    print(f"    ✗ Serper imageUrl: thumbnail pequeno ({w}x{h}) — usando Leonardo")
        except Exception as e:
            print(f"    ✗ Serper imageUrl erro: {e}")

    # ── Camada 1: Leonardo AI (fallback com cena_foto) ──
    cena = noticia.get("cena_foto", "") or titulo
    if cena and os.getenv("LEONARDO_API_KEY"):
        print(f"    Leonardo fallback com cena: '{cena[:60]}'...")
        leo_url = gerar_leonardo(cena)
        if leo_url and baixar_imagem(leo_url, img_path):
            print(f"    ✓ Leonardo OK — {leo_url[:60]}...")
            return img_path, "Leonardo (cena_foto)"

    return None, None


# ══════════════════════════════════════════════════════════════════════════════
# FASE 3: COMPOSICAO DOS CARDS (PILLOW)
# ══════════════════════════════════════════════════════════════════════════════

def load_font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return ImageFont.load_default()


def draw_gradient_overlay(img, y_start, y_end, color):
    overlay = Image.new("RGBA", (W, y_end - y_start), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    for y in range(overlay.height):
        progress = y / max(overlay.height - 1, 1)
        alpha = int(255 * progress)
        draw.line([(0, y), (W, y)], fill=(*color, alpha))
    region = img.crop((0, y_start, W, y_end)).convert("RGBA")
    composited = Image.alpha_composite(region, overlay)
    img.paste(composited, (0, y_start))


def _sanitize_prompt(text):
    """Sanitiza prompt para Leonardo. R$/US$ preservados (testar; se VALIDATION_ERROR, voltar substituição)."""
    return str(text)


def gerar_card_leonardo(photo_path, categoria, titulo, highlight_words, corpo, fonte_nome, output_path, numero=None, total=None, cena_foto=""):
    """Gera o card completo via Leonardo AI com a foto editorial como init_image.

    Leonardo recebe a foto real como referencia (init_strength 0.55 — mantem a foto,
    aplica o layout por cima) e gera o card com:
    - Foto no topo (55%), gradiente de transicao, fundo teal solido
    - Badge da categoria, headline com palavras em amarelo, corpo do texto, fonte
    - Barra gradiente no rodape (verde → teal → rosa → laranja)

    Retorna True se gerou com sucesso, False para fallback no Pillow.
    """
    import unicodedata

    def _normalize_word(text):
        """Strip accents/punctuation for highlight matching only — NOT for rendering."""
        return re.sub(r'[^\w]', '', unicodedata.normalize("NFKD", str(text)).encode("ascii", "ignore").decode("ascii"))

    api_key = os.getenv("LEONARDO_API_KEY")
    if not api_key:
        return False

    # Montar headline com indicacao de quais palavras ficam em amarelo
    # Passa o titulo COM acentos para Leonardo renderizar corretamente
    titulo_upper = _sanitize_prompt(titulo).upper()
    hl_normalized = set()
    for phrase in (highlight_words or []):
        for w in str(phrase).upper().split():
            hl_normalized.add(_normalize_word(w))

    headline_parts = []
    for word in titulo_upper.split():
        if _normalize_word(word) in hl_normalized:
            headline_parts.append(f"[YELLOW]{word}[/YELLOW]")
        else:
            headline_parts.append(word)
    headline_formatted = " ".join(headline_parts)

    # Passar texto COM acentos — Leonardo renderiza melhor com UTF-8 explicito
    _CATEGORIA_ACENTOS = {
        "ESTRATEGIA CORPORATIVA": "ESTRATÉGIA CORPORATIVA",
        "COOPERACAO GLOBAL": "COOPERAÇÃO GLOBAL",
        "RECURSOS HIDRICOS": "RECURSOS HÍDRICOS",
        "EDUCACAO": "EDUCAÇÃO",
        "FINANCAS VERDES": "FINANÇAS VERDES",
        "AGRONEGOCIO": "AGRONEGÓCIO",
    }
    categoria_str = _CATEGORIA_ACENTOS.get(categoria.upper(), categoria.upper())
    corpo_str = _sanitize_prompt(corpo)
    fonte_str = _sanitize_prompt(fonte_nome)
    pag = f"{numero}/{total}" if numero and total else ""

    # Build headline text — no bracket markup (causes VALIDATION_ERROR)
    titulo_plain = _sanitize_prompt(titulo).upper()

    # Prompt must stay under ~1000 chars — Leonardo v2 API VALIDATION_ERROR acima desse limite
    # Truncar cena_foto em 150 chars pra garantir margem com titulo/corpo/fonte longos
    cena_curta = (cena_foto or "")[:150].rstrip().rstrip(",.")
    _com_foto_real = photo_path and Path(photo_path).exists()

    if _com_foto_real:
        # Silencioso sobre a imagem: so aponta onde fica, image_reference HIGH cuida do resto
        upper_half_desc = "UPPER HALF of the card: reference image, full-bleed, no text, no watermarks. "
    elif cena_curta:
        upper_half_desc = f"UPPER HALF photo: {cena_curta}. Natural light, film grain, real, not stock. "
    else:
        upper_half_desc = "UPPER HALF: hyperrealistic photograph, natural lighting. "

    def _build(upper_desc_local):
        return (
            f"Instagram 4:5 card, no borders. "
            f"{upper_desc_local}"
            f"LOWER HALF: solid teal 005F73. TALL TEAL FADE at top of lower half, photo dissolves slowly into teal over long distance, monochromatic blend, diffuse like fog, NO rainbow here, only teal and photo. "
            f"Lower half: rounded pill badge white uppercase '{categoria_str}', "
            f"below LARGE white uppercase HEADLINE: {titulo_plain}, "
            f"below body white: '{corpo_str}', "
            f"below tiny italic gray: 'Fonte: {fonte_str}'. "
            f"Top right: counter badge '{pag}'. "
            f"BOTTOM EDGE only: thin rainbow stripe green to teal to pink to orange, separate from top fade. "
            f"Editorial, no markers."
        )

    prompt = _build(upper_half_desc)
    if len(prompt) > 1000 and not _com_foto_real:
        # truncar cena_foto mais agressivamente (nao aplica quando ha foto real de referencia)
        excess = len(prompt) - 995
        cena_curta = cena_curta[:max(50, len(cena_curta) - excess)].rstrip().rstrip(",.")
        upper_half_desc = f"UPPER HALF photo: {cena_curta}. Natural light, film grain, real, not stock. "
        prompt = _build(upper_half_desc)
        print(f"    [INFO] prompt truncado para {len(prompt)} chars")

    # Quando ha foto real como referencia, o negative_prompt "anti-people" conflita com rostos reais.
    # Sem foto: aplica o filtro completo (evita stock photos corporativos gerados por Leonardo)
    # Com foto: negative minimo (apenas evitar ilustracao/CGI, mantem pessoas/rostos da foto real)
    if _com_foto_real:
        negative_prompt = (
            "illustration, painting, CGI, render, cartoon, "
            "text overlay on photo, watermark, logo on photo"
        )
    else:
        negative_prompt = (
            "people, person, human, face, portrait, man, woman, worker, crowd, "
            "computer screen, laptop screen, TV screen, monitor, digital display, "
            "office, desk, table, meeting room, boardroom, chair, "
            "staged photo, stock photo, posed composition, "
            "artificial lighting, studio setup, "
            "illustration, painting, CGI, render, cartoon, "
            "text overlay on photo, watermark, logo on photo"
        )

    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": f"Bearer {api_key}",
    }

    params = {
        "prompt": prompt,
        "width": W,
        "height": H,
        "quantity": 1,
        "prompt_enhance": "OFF",
    }
    # negative_prompt apenas quando NAO ha foto real (evitar stock photo gerado)
    # Com foto real: padrao case carousel nao usa negative_prompt (evita conflito com rostos reais)
    if not _com_foto_real:
        params["negative_prompt"] = negative_prompt

    # Crop init_image para proporcao do card (1856x2304) — evita letterbox branco
    if photo_path and Path(photo_path).exists():
        try:
            _img = Image.open(photo_path).convert("RGB")
            target_ratio = W / H  # 1856/2304 = 0.8055
            current_ratio = _img.width / _img.height
            if abs(current_ratio - target_ratio) > 0.02:  # diff > 2% — precisa cortar
                if current_ratio > target_ratio:
                    new_w = int(_img.height * target_ratio)
                    left = (_img.width - new_w) // 2
                    _img = _img.crop((left, 0, left + new_w, _img.height))
                else:
                    new_h = int(_img.width / target_ratio)
                    top = (_img.height - new_h) // 2
                    _img = _img.crop((0, top, _img.width, top + new_h))
                _cropped_path = Path(photo_path).with_suffix(".cropped.jpg")
                _img.save(str(_cropped_path), "JPEG", quality=95)
                photo_path = str(_cropped_path)
        except Exception as _e:
            print(f"    [CROP] Erro ao cortar imagem: {_e}")

    # Upload da foto editorial como init_image APENAS se for foto real de qualidade
    # (não usar thumbnails do Serper /news — causam people/stock-photo no output)
    _use_init = False
    if photo_path and Path(photo_path).exists():
        try:
            _check = Image.open(photo_path)
            _w, _h = _check.size
            # Só usa init_image se a foto tiver resolução minima (>= 400px) — thumbnails ~300px são descartados
            # Threshold considera crop 4:5 que reduz largura (ex: Natura 800x533 → cropped 429x533)
            if _w >= 400 and _h >= 400:
                _use_init = True
        except Exception:
            pass

    if _use_init:
        init_id = upload_init_image_leonardo(api_key, photo_path)
        if init_id:
            # image_reference com strength HIGH preserva composicao/rostos fielmente
            # (init_image+init_strength reinterpretava a foto, especialmente em portraits com rostos)
            params["guidances"] = {
                "image_reference": [
                    {"image": {"id": init_id, "type": "UPLOADED"}, "strength": "HIGH"}
                ]
            }
            print(f"    Leonardo card: image_reference HIGH ({_w}x{_h})...")
        else:
            print(f"    Leonardo card: upload falhou, gerando do zero...")
    else:
        print(f"    Leonardo card: gerando do zero via cena_foto (sem init_image)...")

    payload = {"model": "nano-banana-2", "parameters": params, "public": False}

    try:
        resp = requests.post(
            "https://cloud.leonardo.ai/api/rest/v2/generations",
            headers=headers, json=payload, timeout=30,
        )
        if not resp.ok:
            print(f"    Leonardo card erro: {resp.status_code} — {resp.text[:200]}")
            return False

        data = resp.json()
        if isinstance(data, list):
            print(f"    Leonardo card erro API: {data[0]}")
            return False

        gen_id = None
        for v in data.values():
            if isinstance(v, dict):
                gen_id = v.get("generationId") or v.get("id")
                if gen_id:
                    break
        if not gen_id:
            return False

        print(f"    Leonardo card ID: {gen_id[:12]}... aguardando 70s...")
        time.sleep(70)

        poll_url = f"https://cloud.leonardo.ai/api/rest/v1/generations/{gen_id}"
        poll_headers = {"accept": "application/json", "authorization": f"Bearer {api_key}"}
        for attempt in range(10):
            r = requests.get(poll_url, headers=poll_headers, timeout=20)
            job = r.json().get("generations_by_pk", {})
            status = job.get("status", "PENDING")
            if status == "COMPLETE":
                imgs = job.get("generated_images", [])
                if imgs:
                    img_data = requests.get(imgs[0]["url"], timeout=60).content
                    # Salvar resultado
                    from io import BytesIO
                    img = Image.open(BytesIO(img_data)).convert("RGB")
                    img.save(str(output_path), "JPEG", quality=95)
                    print(f"    ✓ Leonardo card salvo: {output_path.name}")
                    return True
            elif status == "FAILED":
                print(f"    Leonardo card falhou")
                return False
            print(f"    aguardando... ({attempt+1}/10)")
            time.sleep(20)

    except Exception as e:
        print(f"    Leonardo card excecao: {e}")

    return False


def draw_top_stripe(draw):
    """Faixa gradiente decorativa no topo (verde → teal)."""
    stripe_h = int(H * 0.012)
    colors = [GREEN, TEAL_BAR]
    for x in range(W):
        progress = x / max(W - 1, 1)
        c1, c2 = colors[0], colors[1]
        r = int(c1[0] + (c2[0] - c1[0]) * progress)
        g = int(c1[1] + (c2[1] - c1[1]) * progress)
        b = int(c1[2] + (c2[2] - c1[2]) * progress)
        draw.line([(x, 0), (x, stripe_h)], fill=(r, g, b))


def draw_gradient_bar(img):
    bar_y = int(BAR_START * H)
    draw = ImageDraw.Draw(img)
    colors = [GREEN, TEAL_BAR, PINK, ORANGE]
    segment_w = W / (len(colors) - 1)
    for x in range(W):
        seg_idx = min(int(x / segment_w), len(colors) - 2)
        progress = (x - seg_idx * segment_w) / segment_w
        c1, c2 = colors[seg_idx], colors[seg_idx + 1]
        r = int(c1[0] + (c2[0] - c1[0]) * progress)
        g = int(c1[1] + (c2[1] - c1[1]) * progress)
        b = int(c1[2] + (c2[2] - c1[2]) * progress)
        draw.line([(x, bar_y), (x, H)], fill=(r, g, b))


def compor_card_noticia(photo_path, categoria, titulo, highlight_words, corpo, fonte_nome, output_path, numero=None, total=None):
    """Compoe um card de noticia completo. photo_path pode ser None (zona teal solida).
    numero/total: ex. 2, 6 → mostra "2 / 6" no canto superior direito.
    """
    card = Image.new("RGBA", (W, H), (*TEAL, 255))

    # Foto no topo (ou zona teal se sem foto)
    photo_h = int(PHOTO_END * H)
    if photo_path:
        photo = Image.open(photo_path).convert("RGBA")
        scale = max(W / photo.width, photo_h / photo.height)
        resized = photo.resize((int(photo.width * scale), int(photo.height * scale)), Image.LANCZOS)
        crop_x = (resized.width - W) // 2
        crop_y = (resized.height - photo_h) // 2
        cropped = resized.crop((crop_x, crop_y, crop_x + W, crop_y + photo_h))
        card.paste(cropped, (0, 0))

    # Degrade
    grad_start = int(PHOTO_END * H) - int(0.20 * H)
    grad_end = int(GRAD_END * H)
    draw_gradient_overlay(card, grad_start, grad_end, TEAL)

    # Bloco teal solido
    draw = ImageDraw.Draw(card)
    draw.rectangle([(0, int(GRAD_END * H)), (W, int(BAR_START * H))], fill=(*TEAL, 255))

    # Badge
    badge_color = BADGE_COLORS.get(categoria.upper(), GREEN)
    font_badge = load_font(FONT_BOLD, 38)
    cat_text = categoria.upper()
    bbox = font_badge.getbbox(cat_text)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    pad_x, pad_y = 30, 14
    badge_x = 100
    badge_y = int(BADGE_Y * H) - (text_h + pad_y * 2) // 2
    draw.rounded_rectangle(
        [(badge_x, badge_y), (badge_x + text_w + pad_x * 2, badge_y + text_h + pad_y * 2)],
        radius=(text_h + pad_y * 2) // 2,
        fill=badge_color,
    )
    draw.text((badge_x + pad_x, badge_y + pad_y - bbox[1]), cat_text, fill=WHITE, font=font_badge)

    # Headline com highlights — font escalona automaticamente para caber em ≤4 linhas
    margin_x = 100
    max_w = W - margin_x * 2

    def wrap_headline(font_size):
        font = load_font(FONT_BOLD, font_size)
        words_h = titulo.upper().split()
        ls, cur = [], ""
        for w in words_h:
            test = f"{cur} {w}".strip()
            if font.getbbox(test)[2] - font.getbbox(test)[0] <= max_w:
                cur = test
            else:
                if cur:
                    ls.append(cur)
                cur = w
        if cur:
            ls.append(cur)
        return font, ls

    # Escalonar: 72 → 60 → 52px; hard cap 4 linhas
    for font_size in (72, 60, 52):
        font_head, lines = wrap_headline(font_size)
        if len(lines) <= 3:
            break
    if len(lines) > 4:
        lines = lines[:4]
        lines[-1] = lines[-1][:lines[-1].rfind(" ") or len(lines[-1])] + "..."

    line_spacing = int(font_size * 1.25)
    y = int(HEADLINE_Y * H)

    # Flatten highlight_words: "1.200 toneladas CO2" → {"1.200", "TONELADAS", "CO2"}
    hl_upper = set()
    for phrase in (highlight_words or []):
        for w in str(phrase).upper().split():
            hl_upper.add(w)

    for line in lines:
        x = margin_x
        for word in line.split():
            color = YELLOW if word in hl_upper else WHITE
            draw.text((x, y), word, fill=color, font=font_head)
            x += font_head.getbbox(word + " ")[2] - font_head.getbbox(word + " ")[0]
        y += line_spacing

    # Body text — usa texto_card se disponivel; fallback: extrair primeiras 2 frases do resumo
    def _extrair_texto_card(texto):
        """Extrai max 2 frases completas do texto, respeitando limites de frase."""
        import re as _re
        frases = _re.split(r'(?<=[.!?])\s+', texto.strip())
        frases = [f for f in frases if f.strip()]
        if len(frases) >= 2:
            return " ".join(frases[:2])
        return frases[0] if frases else texto[:120]

    corpo_card = corpo if corpo else _extrair_texto_card(noticia.get("resumo", "") if False else corpo or "")

    font_body = load_font(FONT_REGULAR, 44)
    y_body = int(BODY_Y * H)
    line_h_body = 58
    max_body_y = int(SOURCE_Y * H) - 20
    max_lines = (max_body_y - y_body) // line_h_body

    # Quebra palavra por palavra respeitando largura real de pixels
    max_body_w = W - margin_x * 2
    body_lines = []
    words_b = corpo_card.split()
    cur_b = ""
    for wb in words_b:
        test_b = f"{cur_b} {wb}".strip()
        if font_body.getbbox(test_b)[2] - font_body.getbbox(test_b)[0] <= max_body_w:
            cur_b = test_b
        else:
            if cur_b:
                body_lines.append(cur_b)
            cur_b = wb
    if cur_b:
        body_lines.append(cur_b)

    if len(body_lines) > max_lines:
        body_lines = body_lines[:max_lines]
        # Terminar na ultima palavra completa sem reticencias (o texto_card ja eh curto)
        last = body_lines[-1]
        last_bbox_w = font_body.getbbox(last)[2] - font_body.getbbox(last)[0]
        if last_bbox_w > max_body_w - 40:
            body_lines[-1] = last.rsplit(" ", 1)[0]

    for line in body_lines:
        draw.text((margin_x, y_body), line, fill=WHITE, font=font_body)
        y_body += line_h_body

    # Fonte
    font_src = load_font(FONT_ITALIC, 36)
    draw.text((100, int(SOURCE_Y * H)), f"Fonte: {fonte_nome}", fill=(200, 200, 200), font=font_src)

    # Paginacao — "2 / 6" no canto superior direito
    if numero is not None and total is not None:
        font_page = load_font(FONT_BOLD, 36)
        page_text = f"{numero} / {total}"
        pt_bbox = font_page.getbbox(page_text)
        pt_w = pt_bbox[2] - pt_bbox[0]
        padding = 20
        pill_x1 = W - pt_w - padding * 2 - 30
        pill_y1 = 30
        pill_x2 = W - 30
        pill_y2 = 30 + (pt_bbox[3] - pt_bbox[1]) + padding
        draw.rounded_rectangle([(pill_x1, pill_y1), (pill_x2, pill_y2)], radius=20, fill=(0, 0, 0, 130))
        draw.text((pill_x1 + padding, pill_y1 + padding // 2), page_text, fill=WHITE, font=font_page)

    # Barra gradiente
    draw_gradient_bar(card)

    card.convert("RGB").save(output_path, "JPEG", quality=95)
    return output_path


def gerar_titulo_capa_dinamico(noticias, fallback_n):
    """Gera titulo contextual da capa via Claude Haiku baseado nas noticias reais da semana.

    O titulo deve: mencionar semana/semanal, ser curto (max 8 palavras, ~60 chars),
    positivo, e refletir os temas da semana atual. Se Haiku falhar, cai num fallback generico.
    """
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    if not anthropic_key:
        return f"{fallback_n} Boas Not\u00edcias ESG desta Semana"

    # Montar resumo das noticias para o prompt
    resumo_noticias = ""
    for i, n in enumerate(noticias):
        resumo_noticias += f"- [{n.get('categoria','')}] {n.get('titulo','')}\n"

    prompt = f"""Voce e editor-chefe do carrossel ESG semanal da NTICS Projetos. Abaixo estao as {len(noticias)} noticias desta semana:

{resumo_noticias}

Escreva UM titulo de capa para o carrossel. Requisitos:
- Max 8 palavras (vai em duas linhas no card)
- DEVE mencionar "semana" ou "semanal" (ex: "desta semana", "da semana")
- Tom positivo e editorial
- Reflita o fio condutor tematico das noticias acima (nao seja generico)
- Pode usar o numero {len(noticias)} se couber naturalmente
- Nao use dois-pontos nem hifen
- Nao use emojis
- ATENCAO: as noticias cobrem Brasil E mundo (internacionais tambem). NAO restrinja o titulo apenas ao Brasil — use framing global/universal ou mencione "Brasil e mundo" se fizer sentido

Exemplos de BONS titulos contextuais (GLOBAIS, nao so-Brasil):
- "Do laboratorio aos mercados verdes desta semana"
- "Ciencia e clima lideram as boas noticias da semana"
- "{len(noticias)} conquistas que marcaram a semana ESG"
- "Brasil e mundo avancam em ESG esta semana"
- "Impacto global em sete frentes desta semana"
- "Avancos ESG que marcaram a semana no mundo"

Responda SOMENTE com o titulo, sem aspas, sem explicacao."""

    try:
        r = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": anthropic_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": "claude-haiku-4-5-20251001",
                "max_tokens": 100,
                "messages": [{"role": "user", "content": prompt}],
            },
            timeout=30,
        )
        if not r.ok:
            return f"{fallback_n} Boas Not\u00edcias ESG desta Semana"
        titulo = r.json()["content"][0]["text"].strip().strip('"').strip("'").strip(".")
        # Sanitizar — remover linhas extras, pegar so a primeira
        titulo = titulo.split("\n")[0].strip()
        if len(titulo) < 20 or len(titulo) > 80:
            return f"{fallback_n} Boas Not\u00edcias ESG desta Semana"
        return titulo
    except Exception:
        return f"{fallback_n} Boas Not\u00edcias ESG desta Semana"


def gerar_capa_leonardo(titulo_capa, noticias, output_path, photo_path=None, cena_override=None):
    """Gera o card capa completo via Leonardo AI (foto + layout em uma chamada).

    Se photo_path fornecido: usa image_reference HIGH (preserva a foto real).
    Se cena_override fornecido: usa diretamente essa cena, sem scoring.
    Senao: constroi cena sintetica a partir dos cena_foto das noticias.
    """
    api_key = os.getenv("LEONARDO_API_KEY")
    if not api_key:
        return None

    titulo_upper = _sanitize_prompt(titulo_capa).upper()

    if cena_override:
        cena = cena_override
    else:
        # Escolher cena da noticia com mais elementos visuais especificos (usado apenas se sem foto real)
        def _score_cena(c):
            especifico = sum(c.lower().count(w) for w in ["port", "solar", "farm", "plant", "forest", "factory", "terminal", "station"])
            outdoor = sum(c.lower().count(w) for w in ["aerial", "field", "construction", "outdoor", "nature", "landscape"])
            return especifico * 2 + outdoor

        cenas = [(n.get("cena_foto", ""), _score_cena(n.get("cena_foto", ""))) for n in noticias if n.get("cena_foto")]
        cenas.sort(key=lambda x: x[1], reverse=True)
        cena = cenas[0][0] if cenas else "diverse professionals working on sustainability projects in Brazil, solar panels and green infrastructure visible"

    # Silencioso sobre a imagem: so aponta onde fica, image_reference HIGH cuida do resto
    if photo_path and Path(photo_path).exists():
        upper_desc = "UPPER HALF of the card: reference image, full-bleed, no text, no watermarks. "
    else:
        upper_desc = f"UPPER HALF of the card: full-bleed hyperrealistic photojournalistic photograph of {cena}. Natural light, film grain, real photograph, NOT AI looking. "

    prompt = (
        f"Social media carousel cover card, Instagram portrait format, no white borders, fills entire frame. "
        f"IMPORTANT: Do NOT render any percentage signs, numbers, rulers or layout markers. "
        f"{upper_desc}"
        f"LOWER HALF: solid dark teal 005F73. "
        f"TALL TEAL FADE zone at top of lower half, photo dissolves slowly into teal, monochromatic blend, NO rainbow here. "
        f"CENTERED near top of lower half: small rounded green pill badge with white bold uppercase text "
        f"'NOT\u00cdCIAS DA SEMANA'. "
        f"VERY LARGE BOLD HEADLINE below badge, occupies most of lower half, multiple lines centered, highly impactful typography: white uppercase sans-serif: {titulo_upper}. "
        f"BOTTOM EDGE ONLY: thin rainbow stripe green to teal to pink to orange, separate from top fade. "
        f"Professional editorial cover design. No borders, no padding."
    )

    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": f"Bearer {api_key}",
    }
    params = {"prompt": prompt, "width": W, "height": H, "quantity": 1, "prompt_enhance": "OFF"}

    # Se photo_path fornecido, sobe como image_reference HIGH (preserva a foto real)
    if photo_path and Path(photo_path).exists():
        try:
            _img = Image.open(photo_path).convert("RGB")
            target_ratio = W / H
            if abs(_img.width / _img.height - target_ratio) > 0.02:
                if _img.width / _img.height > target_ratio:
                    new_w = int(_img.height * target_ratio)
                    left = (_img.width - new_w) // 2
                    _img = _img.crop((left, 0, left + new_w, _img.height))
                else:
                    new_h = int(_img.width / target_ratio)
                    top = (_img.height - new_h) // 2
                    _img = _img.crop((0, top, _img.width, top + new_h))
                _cp = Path(photo_path).with_suffix(".capa-crop.jpg")
                _img.save(str(_cp), "JPEG", quality=95)
                photo_path = str(_cp)
        except Exception as _e:
            print(f"  [CAPA] crop falhou: {_e}")
        init_id = upload_init_image_leonardo(api_key, photo_path)
        if init_id:
            params["guidances"] = {"image_reference": [{"image": {"id": init_id, "type": "UPLOADED"}, "strength": "HIGH"}]}
            print("  [CAPA] image_reference HIGH ativo")

    payload = {"model": "nano-banana-2", "parameters": params, "public": False}

    print("  [CAPA] Iniciando geracao Leonardo AI...")
    try:
        resp = requests.post(
            "https://cloud.leonardo.ai/api/rest/v2/generations",
            headers=headers, json=payload, timeout=30,
        )
        if not resp.ok:
            print(f"  [CAPA] Erro Leonardo: {resp.status_code}")
            return None

        data = resp.json()
        if isinstance(data, list):
            return None

        gen_id = None
        for v in data.values():
            if isinstance(v, dict):
                gen_id = v.get("generationId") or v.get("id")
                if gen_id:
                    break
        if not gen_id:
            return None

        print(f"  [CAPA] ID: {gen_id[:12]}... aguardando 90s...")
        time.sleep(90)

        poll_url = f"https://cloud.leonardo.ai/api/rest/v1/generations/{gen_id}"
        poll_headers = {"accept": "application/json", "authorization": f"Bearer {api_key}"}
        for attempt in range(10):
            r = requests.get(poll_url, headers=poll_headers, timeout=20)
            job = r.json().get("generations_by_pk", {})
            status = job.get("status", "PENDING")
            if status == "COMPLETE":
                imgs = job.get("generated_images", [])
                if imgs:
                    from io import BytesIO
                    img_data = requests.get(imgs[0]["url"], timeout=60).content
                    img = Image.open(BytesIO(img_data)).convert("RGB")
                    img.save(str(output_path), "JPEG", quality=95)
                    print(f"  [CAPA] ✓ salvo: {output_path.name}")
                    return output_path
            elif status == "FAILED":
                print("  [CAPA] Leonardo falhou")
                return None
            print(f"  [CAPA] aguardando... ({attempt+1}/10)")
            time.sleep(20)
    except Exception as e:
        print(f"  [CAPA] excecao: {e}")
    return None


def gerar_cta_leonardo(output_path):
    """Gera o card CTA base via Leonardo AI (fundo teal + texto). Sem logo."""
    api_key = os.getenv("LEONARDO_API_KEY")
    if not api_key:
        return None

    prompt = (
        "Minimalist social media CTA card, Instagram portrait format. "
        "IMPORTANT: Do NOT render any percentage signs, numbers, rulers or layout markers. "
        "ENTIRE CARD: solid dark teal background color 005F73, clean and flat. "
        "TOP AREA of card: large empty teal space reserved for a logo (leave blank, no decoration). "
        "CENTER of card: large bold white sans-serif text: 'Siga para mais boas not\u00edcias toda semana'. "
        "BELOW CENTER: medium white text '@nticsprojetos'. "
        "BELOW THAT: small elegant white italic text 'Inova\u00e7\u00e3o, Impacto e Regenera\u00e7\u00e3o'. "
        "BOTTOM EDGE flush: thick horizontal gradient stripe spanning full width, "
        "colors flow smoothly from bright green to teal to magenta pink to orange. "
        "Minimalist typography only, no images, no patterns, no borders."
    )

    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": f"Bearer {api_key}",
    }
    payload = {
        "model": "nano-banana-2",
        "parameters": {"prompt": prompt, "width": W, "height": H, "quantity": 1, "prompt_enhance": "OFF"},
        "public": False,
    }

    print("  [CTA] Iniciando geracao Leonardo AI...")
    try:
        resp = requests.post(
            "https://cloud.leonardo.ai/api/rest/v2/generations",
            headers=headers, json=payload, timeout=30,
        )
        if not resp.ok:
            print(f"  [CTA] Erro: {resp.status_code}")
            return None

        data = resp.json()
        if isinstance(data, list):
            return None

        gen_id = None
        for v in data.values():
            if isinstance(v, dict):
                gen_id = v.get("generationId") or v.get("id")
                if gen_id:
                    break
        if not gen_id:
            return None

        print(f"  [CTA] ID: {gen_id[:12]}... aguardando 70s...")
        time.sleep(70)

        poll_url = f"https://cloud.leonardo.ai/api/rest/v1/generations/{gen_id}"
        poll_headers = {"accept": "application/json", "authorization": f"Bearer {api_key}"}
        for attempt in range(10):
            r = requests.get(poll_url, headers=poll_headers, timeout=20)
            job = r.json().get("generations_by_pk", {})
            status = job.get("status", "PENDING")
            if status == "COMPLETE":
                imgs = job.get("generated_images", [])
                if imgs:
                    from io import BytesIO
                    img_data = requests.get(imgs[0]["url"], timeout=60).content
                    img = Image.open(BytesIO(img_data)).convert("RGB")
                    img.save(str(output_path), "JPEG", quality=95)
                    print(f"  [CTA] ✓ base salvo: {output_path.name}")
                    return output_path
            elif status == "FAILED":
                print("  [CTA] Leonardo falhou")
                return None
            print(f"  [CTA] aguardando... ({attempt+1}/10)")
            time.sleep(20)
    except Exception as e:
        print(f"  [CTA] excecao: {e}")
    return None


def aplicar_logo_pillow(cta_path):
    """Aplica logo NTICS sobre o card CTA via Pillow. Unica funcao Pillow permitida."""
    logo_path = Path("brand-book/site/assets/LOGO NTICS - BRANCA.png")
    if not logo_path.exists() or not Path(cta_path).exists():
        return
    cta = Image.open(str(cta_path)).convert("RGBA")
    logo = Image.open(str(logo_path)).convert("RGBA")
    W_c, H_c = cta.size
    logo_max_h = int(H_c * 0.14)
    ratio = logo_max_h / logo.height
    logo_w = int(logo.width * ratio)
    logo_resized = logo.resize((logo_w, logo_max_h), Image.LANCZOS)
    logo_x = (W_c - logo_w) // 2
    logo_y = int(H_c * 0.06)
    cta.paste(logo_resized, (logo_x, logo_y), logo_resized)
    cta.convert("RGB").save(str(cta_path), "JPEG", quality=95)
    print(f"  [CTA] ✓ logo NTICS aplicado")


# ══════════════════════════════════════════════════════════════════════════════
# FASE 4: DESCRICAO E ENTREGA
# ══════════════════════════════════════════════════════════════════════════════

def gerar_descricao(semana, noticias, card_files, img_sources):
    """Gera o descricao.txt com captions e links."""
    n_total = len(noticias)

    # Bullets Instagram: usa texto_card (curto) se disponivel, senão titulo
    bullets_ig = "\n".join(
        f"✅ {n.get('texto_card', n['titulo'])}" for n in noticias
    )

    # Bullets LinkedIn: titulo + texto_card ou primeira frase do resumo
    def primeira_frase(texto):
        frase = texto.split(".")[0].strip()
        return frase[:100] + ("..." if len(frase) > 100 else "")

    bullets_li = "\n".join(
        f"{i+1}. {n['titulo']} — {primeira_frase(n.get('texto_card') or n['resumo'])}"
        for i, n in enumerate(noticias)
    )

    # Links com url_real (verificada) quando disponivel
    links = "\n".join(
        f"{i+1}. {n['fonte']} — {n['titulo']}\n{n.get('url_real') or n['url']}\n"
        for i, n in enumerate(noticias)
    )

    ordem = "\n".join(
        f"{Path(f).name} — {n['titulo']} [img: {img_sources.get(i, '?')}]"
        for i, (f, n) in enumerate(zip(card_files[1:-1], noticias))
    )

    # Temas para hook do LinkedIn
    categorias = list(dict.fromkeys(n.get("categoria", "") for n in noticias))
    temas_li = ", ".join(c.lower() for c in categorias[:3] if c)

    return f"""========================================
CARROSSEL: BOAS NOTICIAS ESG
Semana {semana}
========================================

--- CAPTION INSTAGRAM ---

Enquanto o mundo discute, algumas empresas ja estao fazendo acontecer. 🌱

Esta semana: {n_total} avancos reais em sustentabilidade e responsabilidade social.

{bullets_ig}

Qual dessas te surpreendeu mais? Comenta aqui embaixo 👇
Salva esse post — essas historias merecem ser lembradas.

#ESG #Sustentabilidade #ResponsabilidadeSocial #ImpactoPositivo #BoasNoticias #NTICSProjetos #ODS

--- CAPTION LINKEDIN ---

O progresso em sustentabilidade nao espera. Esta semana, {n_total} noticias mostram empresas e organizacoes transformando compromisso em resultado concreto.

{bullets_li}

O que conecta essas noticias: quando a agenda ESG deixa de ser discurso e vira operacao, os numeros aparecem — em emissoes evitadas, pessoas beneficiadas e capital mobilizado.

Qual dessas iniciativas mais se aproxima do que sua empresa ja faz (ou quer fazer)?

#ESG #Sustentabilidade #ResponsabilidadeSocial #ImpactoSocial #NTICSProjetos #ODS

--- COMENTARIO COM LINKS (fixar como primeiro comentario) ---

Fontes das materias desta semana:

{links}
--- ORDEM DOS CARDS ---

01-capa.jpg — Capa: {n_total} avancos em sustentabilidade que marcaram esta semana
{ordem}
08-cta.jpg — CTA: Siga @nticsprojetos + logo NTICS
"""


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--semana", required=True, help="Data da semana (ex: 2026-04-05)")
    parser.add_argument("--tematica", default=None, help="Tema especifico (opcional)")
    parser.add_argument("--skip-perplexity", action="store_true", help="Pular pesquisa, usar noticias_raw.json existente")
    parser.add_argument("--skip-images", action="store_true", help="Pular download de imagens, usar fotos_originais existentes")
    parser.add_argument("--skip-capa-leo", action="store_true", help="Pular geracao Leonardo para capa (usa fundo teal)")
    parser.add_argument("--cards", default=None, help="Regenerar apenas cards especificos. Ex: --cards capa,2,5,cta")
    parser.add_argument("--titulo-capa", default=None, help="Titulo fixo para a capa (pula geracao dinamica)")
    parser.add_argument("--cena-capa", default=None, help="Descricao da cena foto para a capa (override da selecao automatica)")
    args = parser.parse_args()

    # Parsear --cards em conjunto de indices/tokens a regenerar
    regen_cards: set | None = None
    if args.cards:
        regen_cards = set()
        for token in args.cards.split(","):
            token = token.strip().lower()
            if token in ("capa", "1"):
                regen_cards.add("capa")
            elif token in ("cta",):
                regen_cards.add("cta")
            else:
                try:
                    regen_cards.add(int(token))
                except ValueError:
                    pass

    output_dir = CARROSSEIS_DIR / f"semana-{args.semana}"
    output_dir.mkdir(parents=True, exist_ok=True)
    # Fotos brutas ficam no .tmp (nao polui o output final)
    fotos_dir = CARROSSEIS_TMP / f"semana-{args.semana}" / "fotos_originais"
    fotos_dir.mkdir(parents=True, exist_ok=True)

    # ── FASE 0: Anti-repeticao ──
    print("\n" + "=" * 60)
    print("FASE 0: Verificando historico de carrosseis anteriores...")
    urls_usadas, titulos_usados, fontes_usadas, empresas_destacadas = coletar_historico()
    print(f"  Historico: {len(urls_usadas)} URLs, {len(titulos_usados)} titulos, {len(fontes_usadas)} fontes, {len(empresas_destacadas)} empresas")

    # ── FASE 1: Pesquisa ──
    print("\n" + "=" * 60)
    tmp_semana_dir = CARROSSEIS_TMP / f"semana-{args.semana}"
    tmp_semana_dir.mkdir(parents=True, exist_ok=True)
    raw_json = tmp_semana_dir / "noticias_raw.json"
    if args.skip_perplexity and raw_json.exists():
        print("FASE 1: Carregando noticias existentes (--skip-perplexity)...")
        noticias = json.loads(raw_json.read_text(encoding="utf-8"))
        # Normalizar categoria tambem no cache (pode ter underscore de runs anteriores)
        for n in noticias:
            if "categoria" in n:
                n["categoria"] = n["categoria"].replace("_", " ").strip().upper()
        print(f"  {len(noticias)} noticias carregadas de {raw_json}")
    else:
        print("FASE 1: Pesquisando noticias via Perplexity...")
        noticias = pesquisar_noticias(
            tematica=args.tematica,
            urls_excluir=urls_usadas,
            titulos_excluir=titulos_usados,
            fontes_excluir=fontes_usadas,
            empresas_excluir=empresas_destacadas,
        )
        with open(raw_json, "w", encoding="utf-8") as f:
            json.dump(noticias, f, ensure_ascii=False, indent=2)

    # ── FASE 2: Imagens ──
    print("\n" + "=" * 60)
    img_sources = {}
    if args.skip_images:
        print("FASE 2: Reusando fotos existentes (--skip-images)...")
        for i, noticia in enumerate(noticias):
            final_path = fotos_dir / f"{i+1:02d}-original.jpg"
            if final_path.exists():
                noticia["_foto_local"] = str(final_path)
                img_sources[i] = "REUSED"
                print(f"  [{i+1}/{len(noticias)}] Reusando {final_path.name}")
            else:
                noticia["_foto_local"] = None
                img_sources[i] = "NENHUMA"
                print(f"  [{i+1}/{len(noticias)}] Sem foto disponivel")
    else:
        print("FASE 2: Buscando imagens (Serper → Leonardo AI)...")
        for i, noticia in enumerate(noticias):
            print(f"\n  [{i+1}/{len(noticias)}] {noticia['titulo']}")
            foto_dir = fotos_dir / f"{i+1:02d}"
            foto_dir.mkdir(exist_ok=True)
            img_path, source = buscar_melhor_imagem(noticia, foto_dir)
            if img_path:
                final_path = fotos_dir / f"{i+1:02d}-original.jpg"
                Image.open(img_path).convert("RGB").save(final_path, "JPEG", quality=95)
                noticia["_foto_local"] = str(final_path)
                img_sources[i] = source
            else:
                noticia["_foto_local"] = None
                img_sources[i] = "NENHUMA"

    # ── Copiar fotos para output/fotos/ (disponivel para artigo do site) ──
    fotos_output_dir = output_dir / "fotos"
    fotos_output_dir.mkdir(exist_ok=True)
    fotos_para_artigo = {}  # indice → path em output/fotos/
    for i, noticia in enumerate(noticias):
        foto_local = noticia.get("_foto_local")
        if foto_local and Path(foto_local).exists():
            cat_slug = noticia["categoria"].lower().replace(" ", "-")
            dest = fotos_output_dir / f"{i+1:02d}-{cat_slug}.jpg"
            Image.open(foto_local).convert("RGB").save(dest, "JPEG", quality=95)
            fotos_para_artigo[i] = str(dest)
        else:
            fotos_para_artigo[i] = None

    # ── FASE 3: Geracao Leonardo AI ──
    print("\n" + "=" * 60)
    print("FASE 3: Gerando cards via Leonardo AI (Pillow apenas para logo CTA)...")
    card_files = []

    # Capa
    total_cards = len(noticias) + 2  # capa + noticias + cta
    print(f"  [1/{total_cards}] Capa")
    capa_path = output_dir / "01-capa.jpg"
    # Titulo da capa: gerado dinamicamente pelo Claude Haiku a partir das noticias da semana
    n = len(noticias)
    if args.titulo_capa:
        titulo_capa = args.titulo_capa
        print(f"  Titulo da capa (override): {titulo_capa}")
    else:
        titulo_capa = gerar_titulo_capa_dinamico(noticias, n)
        print(f"  Titulo da capa (gerado dinamicamente): {titulo_capa}")
    if args.skip_capa_leo:
        print("  Capa: --skip-capa-leo ativo, pulando geracao")
    elif regen_cards is not None and "capa" not in regen_cards:
        print("  Capa: pulando (nao incluida em --cards)")
    else:
        # Capa pode opcionalmente usar foto real como referencia via env var CAPA_PHOTO_PATH
        capa_photo = os.getenv("CAPA_PHOTO_PATH") or None
        if capa_photo and not Path(capa_photo).exists():
            capa_photo = None
        gerar_capa_leonardo(titulo_capa, noticias, capa_path, photo_path=capa_photo, cena_override=args.cena_capa or None)
    if capa_path.exists():
        card_files.append(str(capa_path))

    # Cards de noticias — Leonardo gera o card completo, sem Pillow fallback
    for i, noticia in enumerate(noticias):
        num = i + 2
        cat_slug = noticia["categoria"].lower().replace(" ", "-")
        card_path = output_dir / f"{num:02d}-{cat_slug}.jpg"
        print(f"  [{num}/{total_cards}] {noticia['titulo'][:50]}...")

        if regen_cards is not None and num not in regen_cards:
            print(f"    Pulando (nao incluido em --cards)")
            if card_path.exists():
                card_files.append(str(card_path))
            continue

        gerado = gerar_card_leonardo(
            photo_path=noticia.get("_foto_local"),
            categoria=noticia["categoria"],
            titulo=noticia["titulo"],
            highlight_words=noticia.get("highlight_words", []),
            corpo=noticia.get("texto_card", noticia["resumo"]),
            fonte_nome=noticia["fonte"],
            output_path=card_path,
            numero=num,
            total=total_cards,
            cena_foto=noticia.get("cena_foto", ""),
        )

        if not gerado:
            print(f"    [SKIP] Leonardo nao gerou {card_path.name} — verificar creditos/timeout")

        if card_path.exists():
            card_files.append(str(card_path))

    # CTA — Leonardo base + Pillow aplica logo
    cta_num = len(noticias) + 2
    print(f"  [{cta_num}/{total_cards}] CTA")
    cta_path = output_dir / f"{cta_num:02d}-cta.jpg"
    if regen_cards is not None and "cta" not in regen_cards:
        print("  CTA: pulando (nao incluido em --cards)")
    else:
        gerar_cta_leonardo(cta_path)
        if cta_path.exists():
            aplicar_logo_pillow(cta_path)
    if cta_path.exists():
        card_files.append(str(cta_path))

    # ── FASE 4: Descricao ──
    print("\n" + "=" * 60)
    print("FASE 4: Gerando descricao.txt...")
    descricao = gerar_descricao(args.semana, noticias, card_files, img_sources)
    (output_dir / "descricao.txt").write_text(descricao, encoding="utf-8")

    # Manifest
    manifest = {
        "semana": args.semana,
        "tematica": args.tematica,
        "noticias": [{k: v for k, v in n.items() if not k.startswith("_")} for n in noticias],
        "img_sources": img_sources,
        "fotos_artigo": fotos_para_artigo,  # fotos originais prontas para uso no artigo do site
        "cards": card_files,
        "anti_repeticao": {
            "urls_excluidas": len(urls_usadas),
            "titulos_excluidos": len(titulos_usados),
        },
    }
    with open(output_dir / "manifest.json", "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

    # ── Resumo ──
    print("\n" + "=" * 60)
    print("PIPELINE COMPLETO!")
    print(f"  Pasta: {output_dir}")
    print(f"  Cards: {len(card_files)}")
    print(f"  Fontes de imagem:")
    for i, src in img_sources.items():
        print(f"    Card {i+2:02d}: {src}")
    print(f"\n  >> Abra os cards para REVISAO VISUAL antes de publicar <<")


if __name__ == "__main__":
    main()
