"""
Gera artigo de noticias ESG para o site NTICS a partir do carrossel semanal.

Uso:
    python tools/content-gen/gerar_artigo_noticias_site.py --semana 2026-05-11
    python tools/content-gen/gerar_artigo_noticias_site.py --semana 2026-05-11 --skip-images

Output:
    output/marketing/artigos/artigo-noticias-esg-semana-{YYYY-MM-DD}.html
    output/marketing/artigos/hero-noticias-{YYYY-MM-DD}.jpg
"""

import os
import sys
import time
import json
import argparse
import requests
from pathlib import Path
import anthropic

ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = ROOT / "output" / "marketing" / "artigos"
TMP_DIR = ROOT / ".tmp" / "marketing" / "carrosseis"

LEONARDO_KEY = os.environ.get("LEONARDO_API_KEY", "")
ANTHROPIC_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

if not LEONARDO_KEY or not ANTHROPIC_KEY:
    from dotenv import load_dotenv
    load_dotenv(ROOT / ".env")
    LEONARDO_KEY = os.environ.get("LEONARDO_API_KEY", "")
    ANTHROPIC_KEY = os.environ.get("ANTHROPIC_API_KEY", "")


# ── Leonardo AI ──────────────────────────────────────────────────────────────
def gerar_hero_leonardo(prompt: str) -> str:
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": f"Bearer {LEONARDO_KEY}",
    }
    payload = {
        "model": "nano-banana-2",
        "parameters": {
            "prompt": prompt,
            "width": 2048,
            "height": 1152,
            "quantity": 1,
            "prompt_enhance": "OFF",
        },
        "public": False,
    }
    resp = requests.post(
        "https://cloud.leonardo.ai/api/rest/v2/generations",
        headers=headers, json=payload, timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()
    if isinstance(data, list):
        raise RuntimeError(f"Leonardo retornou lista (erro de API): {data[0] if data else 'vazio'}")
    gen_id = None
    for v in data.values():
        if isinstance(v, dict):
            gen_id = v.get("generationId") or v.get("id")
            if gen_id:
                break
    if not gen_id:
        raise RuntimeError(f"gen_id nao encontrado: {data}")

    print(f"  Hero submetido: {gen_id[:12]}... aguardando 60s...")
    time.sleep(60)
    poll_headers = {"accept": "application/json", "authorization": f"Bearer {LEONARDO_KEY}"}
    for attempt in range(12):
        r = requests.get(
            f"https://cloud.leonardo.ai/api/rest/v1/generations/{gen_id}",
            headers=poll_headers, timeout=20,
        )
        job = r.json().get("generations_by_pk", {})
        status = job.get("status", "PENDING")
        print(f"  Status [{attempt+1}/12]: {status}")
        if status == "COMPLETE":
            imgs = job.get("generated_images", [])
            if imgs:
                return imgs[0]["url"]
        elif status == "FAILED":
            raise RuntimeError(f"Geracao falhou: {gen_id}")
        time.sleep(10)
    raise TimeoutError(f"Timeout: {gen_id}")


def baixar_imagem(url: str, caminho: Path) -> None:
    resp = requests.get(url, timeout=60)
    resp.raise_for_status()
    caminho.write_bytes(resp.content)
    print(f"  Salvo: {caminho.name} ({len(resp.content)//1024} KB)")


# ── Claude: gera HTML do artigo ──────────────────────────────────────────────
SYSTEM_PROMPT = """Voce e redator especializado em sustentabilidade e ESG para o site da NTICS Projetos.
Tom: profissional, direto, acessivel. Sem travessao (—). Sem emojis.
Idioma: portugues brasileiro, acentuado corretamente.
Retorne APENAS o HTML do corpo do artigo, sem <html>, <head> ou <body>.
Use as classes CSS ja definidas: article-body, article-lead, executive-summary, section-number, article-image, stats-row, stat-item, blockquote."""

def gerar_html_artigo(noticias: list, semana: str, hero_filename: str) -> str:
    client = anthropic.Anthropic(api_key=ANTHROPIC_KEY)

    noticias_txt = "\n".join(
        f"{i+1}. [{n['categoria']}] {n['titulo']}\n   Resumo: {n['resumo']}\n   Fonte: {n['fonte']} — {n['url']}"
        for i, n in enumerate(noticias)
    )

    user_prompt = f"""Crie o corpo HTML de um artigo de noticias ESG para o site NTICS, semana {semana}.

NOTICIAS DA SEMANA:
{noticias_txt}

ESTRUTURA OBRIGATORIA:
1. <article class="article-body">
2. Lead paragraph curto (<p class="article-lead">) — narrativa que conecta as 7 noticias em um tema da semana
3. Executive Summary (<div class="executive-summary">) — 2-3 paragrafos sintetizando o que a semana revelou sobre o avanco ESG
4. Uma secao por noticia (<h2> com <span class="section-number">0N</span> + titulo contextualizado)
   - 2-3 paragrafos aprofundando cada noticia
   - Link para a fonte original (<a href="URL">Leia o artigo completo</a>)
5. Conclusao com chamada para acao: convite para seguir o perfil @nticsprojetos no Instagram para mais boas noticias ESG toda semana
6. Hero image: <figure class="article-image"><img src="{hero_filename}" alt="..."></figure> logo apos o lead

REGRAS:
- Sem travessao (—). Use virgula ou ponto para separar ideias.
- Sem emojis.
- Numeros e dados das noticias devem ser precisos (nao invente).
- Mencao a NTICS apenas na conclusao, de forma sutil.
- HTML semantico correto, sem erros de tag.
- Retorne APENAS o HTML, sem markdown ao redor.
"""

    print("  Gerando texto via Claude...")
    msg = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=8192,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_prompt}],
    )
    text = msg.content[0].text.strip()
    # Remove markdown code fences se o modelo os incluiu
    if text.startswith("```"):
        text = text.split("\n", 1)[1] if "\n" in text else text
    if text.endswith("```"):
        text = text.rsplit("```", 1)[0].strip()
    return text


# ── CSS (identico ao gerar_artigo_site.py) ───────────────────────────────────
ARTICLE_CSS = """
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
.article-body { max-width: 760px; margin: 0 auto; }
.article-lead {
  font-size: 20px; font-weight: 400; line-height: 1.6;
  color: var(--azul-petroleo); margin-bottom: 48px;
  padding-bottom: 48px; border-bottom: 1px solid var(--cinza-claro);
}
.executive-summary {
  background: var(--cinza-claro); border-radius: 16px;
  padding: 48px; margin-bottom: 64px; border-top: 4px solid var(--azul-petroleo);
}
.executive-summary h3 {
  font-size: 13px; font-weight: 700; text-transform: uppercase;
  letter-spacing: 0.1em; color: var(--azul-petroleo); margin: 0 0 24px 0;
}
.executive-summary p { font-size: 15px; line-height: 1.7; color: var(--grafite); margin-bottom: 16px; }
.executive-summary p:last-child { margin-bottom: 0; }
.article-body h2 {
  font-size: clamp(26px, 3.5vw, 36px); font-weight: 700;
  color: var(--azul-petroleo); letter-spacing: -0.01em;
  margin-top: 64px; margin-bottom: 24px; line-height: 1.2;
}
.section-number {
  display: block; font-size: 12px; font-weight: 700;
  color: var(--verde-regeneracao); text-transform: uppercase;
  letter-spacing: 0.15em; margin-bottom: 4px;
}
.article-body h3 {
  font-size: clamp(20px, 2vw, 24px); font-weight: 600;
  color: var(--grafite); margin-top: 48px; margin-bottom: 16px; line-height: 1.3;
}
.article-body p { font-size: 16px; line-height: 1.75; color: var(--grafite); margin-bottom: 24px; }
.article-body strong { color: var(--grafite); font-weight: 600; }
.article-body a { color: var(--teal-futuro); text-decoration: none; }
.article-body a:hover { color: var(--azul-petroleo); }
.article-body em { font-style: italic; }
.article-body ul, .article-body ol { margin: 16px 0 24px 32px; }
.article-body li { font-size: 16px; line-height: 1.75; margin-bottom: 8px; }
.article-body ul li::marker { color: var(--verde-regeneracao); }
blockquote {
  background: var(--cinza-claro); border-left: 4px solid var(--verde-regeneracao);
  border-radius: 0 8px 8px 0; padding: 24px 32px; margin: 48px 0;
}
blockquote p { color: var(--azul-petroleo); font-size: 17px; font-style: italic; margin-bottom: 0 !important; }
.article-image { margin: 48px 0; }
.article-image img { border-radius: 16px; width: 100%; object-fit: cover; max-height: 480px; }
.article-image figcaption { font-size: 12px; color: var(--cinza-medio); margin-top: 8px; text-align: center; }
.stats-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin: 48px 0; }
.stat-item { text-align: center; padding: 24px; background: var(--cinza-claro); border-radius: 12px; }
.stat-number { font-size: clamp(24px, 3vw, 32px); font-weight: 700; color: var(--azul-petroleo); line-height: 1; }
.stat-label { font-size: 12px; color: var(--cinza-medio); margin-top: 4px; line-height: 1.3; }
@media (max-width: 639px) {
  body { padding: 24px 16px; }
  .executive-summary { padding: 24px; }
  .stats-row { grid-template-columns: repeat(2, 1fr); }
}
"""


def montar_html(titulo: str, body: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{titulo}</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
  <style>{ARTICLE_CSS}</style>
</head>
<body>
  {body}
</body>
</html>"""


# ── Main ─────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--semana", required=True, help="Ex: 2026-05-11")
    parser.add_argument("--skip-images", action="store_true")
    args = parser.parse_args()

    semana = args.semana
    slug = f"noticias-esg-semana-{semana}"
    titulo = f"ESG em Movimento: 7 Noticias que Marcaram a Semana de {semana}"

    # Carrega noticias
    raw_path = TMP_DIR / f"semana-{semana}" / "noticias_raw.json"
    if not raw_path.exists():
        print(f"ERRO: {raw_path} nao encontrado.")
        sys.exit(1)
    noticias = json.loads(raw_path.read_text(encoding="utf-8"))
    print(f"Carregadas {len(noticias)} noticias de {raw_path}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    hero_filename = f"hero-{slug}.jpg"
    hero_path = OUTPUT_DIR / hero_filename

    # Hero image
    if not args.skip_images:
        print("\n[1/3] Gerando hero image via Leonardo AI...")
        hero_prompt = (
            "aerial wide-angle view of diverse Brazilian sustainable business ecosystem, "
            "mix of green urban buildings with solar panels, corporate headquarters alongside community gardens, "
            "wind turbines visible on horizon, clean modern infrastructure, lush green vegetation integrated throughout, "
            "golden hour warm light from above, hyperrealistic drone photography, no people, no text"
        )
        url = gerar_hero_leonardo(hero_prompt)
        baixar_imagem(url, hero_path)
    else:
        print(f"\n[1/3] Imagem: usando existente (--skip-images) — {hero_filename}")

    # Gera HTML via Claude
    print("\n[2/3] Gerando texto do artigo via Claude Haiku...")
    body_html = gerar_html_artigo(noticias, semana, hero_filename)

    # Salva HTML
    print("\n[3/3] Salvando HTML...")
    html_path = OUTPUT_DIR / f"artigo-{slug}.html"
    full_html = montar_html(titulo, body_html)
    html_path.write_text(full_html, encoding="utf-8")
    print(f"  Salvo: {html_path}")

    # Abre no navegador
    import subprocess
    subprocess.Popen(["start", "", str(html_path)], shell=True)

    print(f"\nPronto!")
    print(f"  HTML: {html_path}")
    print(f"  Hero: {hero_path}")


if __name__ == "__main__":
    main()
