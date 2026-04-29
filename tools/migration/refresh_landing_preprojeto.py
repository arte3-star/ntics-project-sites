"""
refresh_landing_preprojeto.py — pipeline completo para enriquecer uma landing
pré-projeto NTICS com cronograma + reescrita editorial.

Etapas:
1. parse_cronograma → output/cronogramas/{slug}.json
2. editorial_rewrite (Sonnet) → output/_editorial_{slug}_content.json
3. build_all_models (build_site único) → assets/projetos/{folder}/site.html
4. upload_new_sites --only {id} → ntics.com.br/{slug}/
5. HTTP HEAD na URL final (verificação)

Usage:
  python tools/migration/refresh_landing_preprojeto.py --projeto 119
  python tools/migration/refresh_landing_preprojeto.py --projeto 119 --skip-upload
"""
import argparse
import os
import subprocess
import sys
import urllib.request
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

REPO_ROOT = Path(__file__).resolve().parents[2]

PROJECT_SLUGS = {
    "116": "cultura-robotica-aster",
    "117": "teatro-oficina-robotica-4ed-whirlpool",
    "119": "pec-eu-faco-parte-2ed-sylvamo",
    "124": "gastronomia-tambem-e-arte-compagas",
    "125": "gastronomia-tambem-e-arte-2ed-gru",
    "127G": "pie-empreendedorismo-e-arte-2ed-gru",
    "127S": "pie-empreendedorismo-e-arte-2ed-sotreq",
}


def run(cmd, label):
    print(f"\n>> {label}")
    print(f"   $ {' '.join(cmd)}")
    res = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if res.stdout:
        print(res.stdout, end="")
    if res.returncode != 0:
        print(res.stderr, end="", file=sys.stderr)
        raise SystemExit(f"Falhou: {label} (exit {res.returncode})")
    return res


def verify_url(slug):
    url = f"https://ntics.com.br/{slug}/"
    try:
        req = urllib.request.Request(url, method="HEAD")
        resp = urllib.request.urlopen(req, timeout=15)
        status = resp.status
    except Exception as e:
        return url, f"erro: {e}"
    return url, status


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--projeto", required=True, choices=list(PROJECT_SLUGS.keys()))
    p.add_argument("--skip-cronograma", action="store_true", help="pula parse_cronograma (usa JSON existente)")
    p.add_argument("--skip-editorial", action="store_true", help="pula reescrita Sonnet (usa JSON existente)")
    p.add_argument("--skip-upload", action="store_true", help="só gera HTML, não publica")
    args = p.parse_args()

    proj = args.projeto
    slug = PROJECT_SLUGS[proj]
    py = sys.executable

    # 1. Cronograma
    if not args.skip_cronograma:
        run([py, "tools/integrations/parse_cronograma.py", "--projeto", proj],
            f"1/4 parse_cronograma {proj}")

    # 2. Editorial
    if not args.skip_editorial:
        run([py, "tools/migration/editorial_rewrite.py", "--projeto", proj],
            f"2/4 editorial_rewrite {proj}")

    # 3. Build (chama build_site direto, sem reexecutar todos)
    print(f"\n>> 3/4 build_site {proj}")
    sys.path.insert(0, str(REPO_ROOT / "tools/migration"))
    from build_all_models import build_site, SITES  # noqa
    build_site(proj, SITES[proj])

    # 4. Upload
    if args.skip_upload:
        print("\n[skip-upload]")
        return
    run([py, "tools/migration/upload_new_sites.py", "--only", proj],
        f"4/4 upload {proj}")

    # 5. Verify
    url, status = verify_url(slug)
    print(f"\n>> Verificação: {url} → {status}")
    if status != 200:
        raise SystemExit(f"URL não retornou 200: {status}")
    print(f"\n✓ Pipeline completo: {url}")


if __name__ == "__main__":
    main()
