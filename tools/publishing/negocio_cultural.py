"""
API client para o site Negócio Cultural (negociocultural.com.br).

Autenticação:
  - WordPress REST API (wp/v2/*): token customizado via header X-WP-Token
  - Tutor LMS REST API (tutor/v1/*): Basic Auth com API Key + Secret

Uso:
    python tools/publishing/negocio_cultural.py --listar-cursos
    python tools/publishing/negocio_cultural.py --curso 1123
    python tools/publishing/negocio_cultural.py --topicos-curso 1123
    python tools/publishing/negocio_cultural.py --aulas-topico 456
    python tools/publishing/negocio_cultural.py --paginas

Output: JSON (stdout)
"""

import os
import json
import ssl
import base64
import urllib.request
import urllib.error
import urllib.parse
import sys
from pathlib import Path

# ── Config ───────────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parents[2]

def _load_env():
    env_file = ROOT / ".env"
    if not env_file.exists():
        return
    for line in env_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        key, val = key.strip(), val.strip()
        if key and val and key not in os.environ:
            os.environ[key] = val

_load_env()

WP_URL       = os.environ.get("WP2_URL", "https://negociocultural.com.br").rstrip("/")
WP_TOKEN     = os.environ.get("WP2_TOKEN", "")
TUTOR_KEY    = os.environ.get("WP2_TUTOR_KEY", "")
TUTOR_SECRET = os.environ.get("WP2_TUTOR_SECRET", "")

_ssl_ctx = ssl.create_default_context()
_ssl_ctx.check_hostname = False
_ssl_ctx.verify_mode = ssl.CERT_NONE


# ── HTTP helpers ──────────────────────────────────────────────────────────────
def _wp_request(endpoint, method="GET", data=None):
    """Requisição autenticada via token customizado (wp/v2/*)."""
    url = f"{WP_URL}/wp-json/{endpoint}"
    headers = {"X-WP-Token": WP_TOKEN, "Content-Type": "application/json"}
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    with urllib.request.urlopen(req, context=_ssl_ctx, timeout=30) as r:
        return json.loads(r.read())


def _tutor_request(endpoint, method="GET", data=None):
    """Requisição autenticada via Tutor LMS API Key (tutor/v1/*)."""
    url = f"{WP_URL}/wp-json/{endpoint}"
    creds = base64.b64encode(f"{TUTOR_KEY}:{TUTOR_SECRET}".encode()).decode()
    headers = {"Authorization": f"Basic {creds}", "Content-Type": "application/json"}
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    with urllib.request.urlopen(req, context=_ssl_ctx, timeout=30) as r:
        return json.loads(r.read())


# ── WordPress padrão ──────────────────────────────────────────────────────────
def listar_paginas(per_page=20):
    return _wp_request(f"wp/v2/pages?per_page={per_page}&context=edit")


def listar_posts(per_page=20):
    return _wp_request(f"wp/v2/posts?per_page={per_page}&context=edit")


def obter_pagina(page_id):
    return _wp_request(f"wp/v2/pages/{page_id}?context=edit")


def atualizar_pagina(page_id, dados):
    """dados: dict com campos a atualizar (title, content, etc.)"""
    return _wp_request(f"wp/v2/pages/{page_id}", method="POST", data=dados)


def criar_post(titulo, conteudo, status="draft", categoria_ids=None):
    payload = {"title": titulo, "content": conteudo, "status": status}
    if categoria_ids:
        payload["categories"] = categoria_ids
    return _wp_request("wp/v2/posts", method="POST", data=payload)


# ── Tutor LMS ─────────────────────────────────────────────────────────────────
def listar_cursos(per_page=20):
    resp = _tutor_request(f"tutor/v1/courses?per_page={per_page}")
    if resp.get("code") == "success":
        return resp["data"]["posts"]
    return resp


def obter_curso(curso_id):
    resp = _tutor_request(f"tutor/v1/courses/{curso_id}")
    if resp.get("code") == "success":
        return resp["data"]
    return resp


def listar_topicos_curso(curso_id):
    """Tópicos (módulos/seções) de um curso."""
    resp = _tutor_request(f"tutor/v1/topics?course_id={curso_id}")
    if resp.get("code") == "success":
        return resp["data"]
    return resp


def listar_aulas_topico(topic_id):
    """Aulas de um tópico."""
    resp = _tutor_request(f"tutor/v1/lessons?topic_id={topic_id}")
    if resp.get("code") == "success":
        return resp["data"]
    return resp


def obter_aula(lesson_id):
    resp = _tutor_request(f"tutor/v1/lessons/{lesson_id}")
    if resp.get("code") == "success":
        return resp["data"]
    return resp


def listar_quizzes(curso_id):
    resp = _tutor_request(f"tutor/v1/quizzes?course_id={curso_id}")
    if resp.get("code") == "success":
        return resp["data"]
    return resp


def conteudo_curso(curso_id):
    """Estrutura completa do curso: tópicos + aulas de cada tópico."""
    resp = _tutor_request(f"tutor/v1/course-contents/{curso_id}")
    if resp.get("code") == "success":
        return resp["data"]
    return resp


def listar_matriculas(status="approved"):
    resp = _tutor_request(f"tutor/v1/enrollments/{status}")
    if resp.get("code") == "success":
        return resp["data"]
    return resp


# ── CLI ───────────────────────────────────────────────────────────────────────
def main():
    import argparse
    parser = argparse.ArgumentParser(description="API client para negociocultural.com.br")
    parser.add_argument("--listar-cursos", action="store_true")
    parser.add_argument("--curso", type=int, metavar="ID")
    parser.add_argument("--topicos-curso", type=int, metavar="CURSO_ID")
    parser.add_argument("--aulas-topico", type=int, metavar="TOPIC_ID")
    parser.add_argument("--conteudo-curso", type=int, metavar="CURSO_ID")
    parser.add_argument("--listar-quizzes", type=int, metavar="CURSO_ID")
    parser.add_argument("--matriculas", action="store_true")
    parser.add_argument("--paginas", action="store_true")
    parser.add_argument("--posts", action="store_true")
    parser.add_argument("--pagina", type=int, metavar="ID")
    args = parser.parse_args()

    result = None

    if args.listar_cursos:
        result = listar_cursos()
        if isinstance(result, list):
            print(f"[{len(result)} cursos]", file=sys.stderr)
            for c in result:
                print(f"  id={c.get('ID')} | {c.get('post_title','')[:60]}", file=sys.stderr)
    elif args.curso:
        result = obter_curso(args.curso)
    elif args.topicos_curso:
        result = listar_topicos_curso(args.topicos_curso)
    elif args.aulas_topico:
        result = listar_aulas_topico(args.aulas_topico)
    elif args.conteudo_curso:
        result = conteudo_curso(args.conteudo_curso)
    elif args.listar_quizzes:
        result = listar_quizzes(args.listar_quizzes)
    elif args.matriculas:
        result = listar_matriculas()
    elif args.paginas:
        result = listar_paginas()
        if isinstance(result, list):
            print(f"[{len(result)} páginas]", file=sys.stderr)
            for p in result:
                t = p.get("title", {}).get("rendered", "")
                print(f"  id={p.get('id')} | {t[:60]}", file=sys.stderr)
    elif args.posts:
        result = listar_posts()
    elif args.pagina:
        result = obter_pagina(args.pagina)
    else:
        parser.print_help()
        return

    if result is not None:
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
