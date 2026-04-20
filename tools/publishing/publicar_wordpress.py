"""
Publica artigo HTML no WordPress da NTICS (ntics.com.br).

Fluxo:
  1. Le o HTML do artigo
  2. Faz upload das imagens locais para a midia do WP
  3. Substitui caminhos locais pelas URLs do WP
  4. Remove wrapper <article>/<h1> (WP ja renderiza titulo)
  5. Cria post como rascunho ou publicado
  6. Define a primeira imagem como featured image

Uso pelo agente:
    python tools/publishing/publicar_wordpress.py \
        --html output/marketing/artigos/Artigo-noticias/artigo-noticias-esg-semana-2026-04-14.html \
        --titulo "Titulo do Artigo" \
        --categoria artigos \
        --status draft

    # Publicar rascunho existente:
    python tools/publishing/publicar_wordpress.py --publish 124357

Output JSON (stdout):
    {"post_id": 12345, "status": "draft", "url": "https://ntics.com.br/?p=12345", "images_uploaded": 3}
"""

import os
import re
import sys
import json
import base64
import mimetypes
import ssl
import urllib.request
import urllib.parse
from pathlib import Path
from html.parser import HTMLParser

# ── Config ──────────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parents[2]

def _load_env():
    """Carrega variaveis do .env se nao estiverem no ambiente."""
    env_file = ROOT / ".env"
    if not env_file.exists():
        return
    for line in env_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            key, _, val = line.partition("=")
            key, val = key.strip(), val.strip()
            if key and val and key not in os.environ:
                os.environ[key] = val

_load_env()

WP_URL = os.environ.get("WP_URL", "").rstrip("/")
WP_USER = os.environ.get("WP_USER", "")
WP_APP_PASSWORD = os.environ.get("WP_APP_PASSWORD", "")

CATEGORIAS = {
    "artigos": 73,
    "cases": 77,
    "ebooks": 168,
    "geral": 1,
}

# SSL context (ntics.com.br tem cert issues as vezes)
_ssl_ctx = ssl.create_default_context()
_ssl_ctx.check_hostname = False
_ssl_ctx.verify_mode = ssl.CERT_NONE


# ── WordPress API ───────────────────────────────────────────────────────────
def _auth_header():
    creds = base64.b64encode(f"{WP_USER}:{WP_APP_PASSWORD}".encode()).decode()
    return f"Basic {creds}"


def _wp_request(method, endpoint, data=None, content_type="application/json"):
    """Faz request autenticado para a API REST do WordPress."""
    url = f"{WP_URL}/wp-json/wp/v2/{endpoint}"
    headers = {"Authorization": _auth_header()}

    if data is not None and content_type == "application/json":
        body = json.dumps(data).encode("utf-8")
        headers["Content-Type"] = "application/json"
    elif data is not None:
        body = data
        headers["Content-Type"] = content_type
    else:
        body = None

    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    with urllib.request.urlopen(req, context=_ssl_ctx) as resp:
        return json.loads(resp.read())


def upload_image(filepath, alt_text=""):
    """Faz upload de imagem para a biblioteca de midia do WP. Retorna {id, url}."""
    filepath = Path(filepath)
    if not filepath.exists():
        print(f"  [SKIP] Imagem nao encontrada: {filepath.name}", file=sys.stderr)
        return None

    mime, _ = mimetypes.guess_type(str(filepath))
    if not mime:
        mime = "image/jpeg"

    img_data = filepath.read_bytes()
    filename = filepath.name

    url = f"{WP_URL}/wp-json/wp/v2/media"
    headers = {
        "Authorization": _auth_header(),
        "Content-Type": mime,
        "Content-Disposition": f'attachment; filename="{filename}"',
    }

    req = urllib.request.Request(url, data=img_data, headers=headers, method="POST")
    with urllib.request.urlopen(req, context=_ssl_ctx) as resp:
        result = json.loads(resp.read())

    media_id = result["id"]
    media_url = result.get("source_url", result.get("guid", {}).get("rendered", ""))

    # Definir alt text
    if alt_text:
        try:
            _wp_request("POST", f"media/{media_id}", {"alt_text": alt_text})
        except Exception:
            pass

    print(f"  [OK] Upload: {filename} -> ID {media_id}")
    return {"id": media_id, "url": media_url}


# ── HTML Processing ─────────────────────────────────────────────────────────
def _extract_images(html, html_dir):
    """Extrai caminhos de imagens locais do HTML. Retorna [(src, alt)]."""
    pattern = r'<img\s+[^>]*src=["\']([^"\']+)["\'][^>]*>'
    images = []
    for match in re.finditer(pattern, html, re.IGNORECASE):
        src = match.group(1)
        # So imagens locais (nao URLs absolutas)
        if not src.startswith(("http://", "https://", "data:")):
            # Extrair alt text
            alt_match = re.search(r'alt=["\']([^"\']*)["\']', match.group(0))
            alt = alt_match.group(1) if alt_match else ""
            images.append((src, alt))
    return images


def _clean_html_for_wp(html):
    """Remove wrappers desnecessarios e duplicacoes de titulo para WP."""
    # Remover tag </output> espuria no final
    html = re.sub(r'</output>\s*$', '', html, flags=re.IGNORECASE)

    # Remover wrapper <article ...> e </article>
    html = re.sub(r'<article\s+[^>]*>', '', html, count=1, flags=re.IGNORECASE)
    html = re.sub(r'</article>\s*$', '', html, flags=re.IGNORECASE)

    # Remover o <h1> interno (WP usa o titulo do post)
    html = re.sub(r'<h1\s+[^>]*>.*?</h1>', '', html, count=1, flags=re.DOTALL | re.IGNORECASE)

    # Remover a linha de data/subtitulo logo apos o h1 (ex: <p style="...">Semana 07/04/2026 ...</p>)
    html = re.sub(
        r'<p\s+style="[^"]*color:\s*#666[^"]*"[^>]*>\s*Semana\s+\d{2}/\d{2}/\d{4}[^<]*</p>',
        '', html, count=1, flags=re.IGNORECASE
    )

    # Limpar linhas vazias excessivas
    html = re.sub(r'\n{3,}', '\n\n', html)

    return html.strip()


def preparar_html_wp(html_path):
    """Processa HTML: limpa, faz upload de imagens, substitui URLs. Retorna (html_final, featured_media_id, n_imgs)."""
    html_path = Path(html_path)
    html_dir = html_path.parent
    html = html_path.read_text(encoding="utf-8")

    # 1. Limpar HTML
    html = _clean_html_for_wp(html)

    # 2. Encontrar e fazer upload de imagens locais
    images = _extract_images(html, html_dir)
    featured_media_id = None
    n_uploaded = 0

    for src, alt in images:
        # Resolver caminho relativo
        img_path = html_dir / src
        if not img_path.exists():
            # Tentar na pasta da semana
            parts = src.replace("\\", "/").split("/")
            for i in range(len(parts)):
                candidate = html_dir / "/".join(parts[i:])
                if candidate.exists():
                    img_path = candidate
                    break

        result = upload_image(img_path, alt_text=alt)
        if result:
            # Substituir caminho local pela URL do WP
            html = html.replace(src, result["url"])
            n_uploaded += 1
            # Primeira imagem = featured image
            if featured_media_id is None:
                featured_media_id = result["id"]

    return html, featured_media_id, n_uploaded


def criar_post(titulo, html_content, categoria="artigos", status="draft",
               excerpt="", slug="", featured_media_id=None, author=None):
    """Cria post no WordPress. Retorna dict com post_id, status, url."""
    cat_id = CATEGORIAS.get(categoria, CATEGORIAS["artigos"])

    payload = {
        "title": titulo,
        "content": html_content,
        "status": status,
        "categories": [cat_id],
    }
    if excerpt:
        payload["excerpt"] = excerpt
    if slug:
        payload["slug"] = slug
    if featured_media_id:
        payload["featured_media"] = featured_media_id
    if author:
        payload["author"] = int(author)

    result = _wp_request("POST", "posts", payload)

    return {
        "post_id": result["id"],
        "status": result["status"],
        "url": result["link"],
        "slug": result["slug"],
    }


def publicar_post(post_id):
    """Muda status de um post existente para 'publish'. Retorna URL final."""
    result = _wp_request("POST", f"posts/{post_id}", {"status": "publish"})
    return {
        "post_id": result["id"],
        "status": result["status"],
        "url": result["link"],
    }


def deletar_post(post_id, force=False):
    """Deleta um post (move para lixeira, ou force=True para deletar permanente)."""
    endpoint = f"posts/{post_id}"
    if force:
        endpoint += "?force=true"
    result = _wp_request("DELETE", endpoint)
    return {"deleted": True, "post_id": post_id}


def verificar_post(post_id):
    """Verifica se um post existe e retorna seus dados basicos."""
    result = _wp_request("GET", f"posts/{post_id}")
    return {
        "post_id": result["id"],
        "title": result["title"]["rendered"],
        "status": result["status"],
        "url": result["link"],
        "categories": result["categories"],
    }


# ── CLI ─────────────────────────────────────────────────────────────────────
def main():
    import argparse
    parser = argparse.ArgumentParser(description="Publica artigo no WordPress NTICS")
    parser.add_argument("--html", help="Caminho do arquivo HTML do artigo")
    parser.add_argument("--titulo", help="Titulo do post")
    parser.add_argument("--categoria", default="artigos", choices=list(CATEGORIAS.keys()))
    parser.add_argument("--status", default="draft", choices=["draft", "publish"])
    parser.add_argument("--excerpt", default="", help="Resumo/excerpt do post")
    parser.add_argument("--slug", default="", help="Slug do post (URL)")
    parser.add_argument("--publish", type=int, help="Publicar rascunho existente (ID)")
    parser.add_argument("--delete", type=int, help="Deletar post (ID)")
    parser.add_argument("--verify", type=int, help="Verificar post (ID)")
    parser.add_argument("--quiet", action="store_true", help="Output apenas JSON")
    parser.add_argument("--author", type=int, default=1, help="ID do autor WP (default 1 = Ntics Projetos; 15 = arte3)")
    args = parser.parse_args()

    if not all([WP_URL, WP_USER, WP_APP_PASSWORD]):
        print("ERRO: WP_URL, WP_USER e WP_APP_PASSWORD devem estar no .env", file=sys.stderr)
        sys.exit(1)

    # Publicar rascunho existente
    if args.publish:
        result = publicar_post(args.publish)
        print(json.dumps(result, ensure_ascii=False))
        return

    # Deletar post
    if args.delete:
        result = deletar_post(args.delete)
        print(json.dumps(result, ensure_ascii=False))
        return

    # Verificar post
    if args.verify:
        result = verificar_post(args.verify)
        print(json.dumps(result, ensure_ascii=False))
        return

    # Criar post novo
    if not args.html or not args.titulo:
        parser.error("--html e --titulo sao obrigatorios para criar post")

    if not args.quiet:
        print(f"Publicando: {args.titulo}", file=sys.stderr)
        print(f"  HTML: {args.html}", file=sys.stderr)

    # Processar HTML e fazer upload de imagens
    html_content, featured_id, n_imgs = preparar_html_wp(args.html)

    if not args.quiet:
        print(f"  Imagens uploaded: {n_imgs}", file=sys.stderr)

    # Criar post
    result = criar_post(
        titulo=args.titulo,
        html_content=html_content,
        categoria=args.categoria,
        status=args.status,
        excerpt=args.excerpt,
        slug=args.slug,
        featured_media_id=featured_id,
        author=args.author,
    )
    result["images_uploaded"] = n_imgs

    if not args.quiet:
        print(f"  Post ID: {result['post_id']}", file=sys.stderr)
        print(f"  Status: {result['status']}", file=sys.stderr)
        print(f"  URL: {result['url']}", file=sys.stderr)

    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
