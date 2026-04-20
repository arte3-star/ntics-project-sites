"""
build_newsletter.py — Renders the newsletter HTML from stories + infographics data.

Usage:
  python tools/build_newsletter.py \
    --stories .tmp/stories_2026-03-20.json \
    --infographics '[{"title":"...","gamma_url":"...","description":"..."}]' \
    --edition "March 20, 2026" \
    --name "Good Signal" \
    --output .tmp/newsletter_2026-03-20.html

  Or with a data file:
  python tools/build_newsletter.py --data .tmp/newsletter_data.json
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

try:
    from jinja2 import Environment, FileSystemLoader
except ImportError:
    print("ERROR: jinja2 not installed. Run: pip install jinja2")
    sys.exit(1)

from active_projects import get_active_projects, apply_overrides

try:
    import premailer
    HAS_PREMAILER = True
except ImportError:
    HAS_PREMAILER = False
    print("WARNING: premailer not installed. CSS won't be inlined. Run: pip install premailer")


TEMPLATE_DIR = Path(__file__).parent / "templates"
DEFAULT_OUTPUT_DIR = Path(__file__).parent.parent / ".tmp"

CATEGORY_MAP = {
    "environment": "wins_environment",
    "meio ambiente": "wins_environment",
    "social": "wins_social",
    "governance": "wins_governance",
    "governança": "wins_governance",
    "governanca": "wins_governance",
}


def load_stories(path: str) -> list:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def group_stories_by_category(stories: list) -> tuple:
    """Returns (story_of_week, env_list, social_list, governance_list)."""
    if not stories:
        return None, [], [], []

    # First story is featured (story of the week)
    featured = stories[0]
    rest = stories[1:]

    env, social, gov = [], [], []
    for s in rest:
        cat = s.get("category", "").lower().strip()
        bucket = CATEGORY_MAP.get(cat, "wins_environment")
        if bucket == "wins_environment":
            env.append(s)
        elif bucket == "wins_social":
            social.append(s)
        else:
            gov.append(s)

    return featured, env, social, gov


def build_stat_of_week(story: dict) -> dict:
    """Extract the hero stat from the featured story."""
    return {
        "number": story.get("headline_stat", "—"),
        "label": story.get("stat_label", story.get("title", "")),
        "source": story.get("source", ""),
        "source_url": story.get("url", "#"),
    }


def render_newsletter(
    stories: list,
    infographics: list,
    edition: str,
    newsletter_name: str,
    tagline: str,
    trend_watch: str,
    logo_url: str = "",
    unsubscribe_url: str = "#",
    archive_url: str = "#",
    incentives: list = None,
    article: dict = None,
    periodicidade: str = "mensal",
    numero_edicao: int = 1,
    destaques: list = None,
    noticias: list = None,
    isd_data: list = None,
    isd_total: str = "",
    projetos_ctx: dict = None,
) -> str:
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATE_DIR)),
        autoescape=False,
    )
    template = env.get_template("newsletter.html")

    story_of_week, wins_env, wins_social, wins_gov = group_stories_by_category(stories)

    stat = build_stat_of_week(story_of_week) if story_of_week else {
        "number": "—", "label": "", "source": "", "source_url": "#"
    }

    # Build preheader from trend_watch or first story
    preheader = trend_watch[:120] if trend_watch else (
        story_of_week.get("summary", "")[:120] if story_of_week else ""
    )

    # If article present, use its title as preheader (more impactful than trend_watch)
    if article and article.get("title"):
        preheader = article.get("excerpt", article["title"])[:120]

    html = template.render(
        newsletter_name=newsletter_name,
        tagline=tagline,
        edition=edition,
        preheader_text=preheader,
        logo_url=logo_url or os.getenv("NEWSLETTER_LOGO_URL",
            "https://ntics.com.br/wp-content/uploads/2023/05/logo-ntics-branco-01.svg"),
        stat_of_week=stat,
        story_of_week=story_of_week or {},
        wins_environment=wins_env,
        wins_social=wins_social,
        wins_governance=wins_gov,
        infographics=infographics or [],
        trend_watch=trend_watch or "",
        unsubscribe_url=unsubscribe_url,
        archive_url=archive_url,
        incentives=incentives or [],
        article=article or {},
        periodicidade=periodicidade,
        numero_edicao=numero_edicao,
        destaques=destaques or [],
        noticias=noticias or [],
        isd_data=isd_data or [],
        isd_total=isd_total,
        projetos_ctx=projetos_ctx or {},
    )

    # Inline CSS for email client compatibility
    if HAS_PREMAILER:
        try:
            html = premailer.transform(html)
        except Exception as e:
            print(f"WARNING: premailer transform failed ({e}). Using raw HTML.")

    return html


_MES_PT_LOOKUP = {
    "janeiro": 1, "fevereiro": 2, "marco": 3, "março": 3, "abril": 4,
    "maio": 5, "junho": 6, "julho": 7, "agosto": 8,
    "setembro": 9, "outubro": 10, "novembro": 11, "dezembro": 12,
}


def _resolve_mes_referencia(arg: str | None) -> tuple[int, int]:
    """Aceita '2026-04', 'Abril/2026', 'abril 2026' ou None (usa hoje)."""
    if not arg:
        today = datetime.today()
        return today.year, today.month
    s = arg.strip().lower()
    # Formato ISO YYYY-MM
    import re as _re
    m = _re.match(r"^(\d{4})-(\d{1,2})$", s)
    if m:
        return int(m.group(1)), int(m.group(2))
    # Formato "Mes/YYYY" ou "Mes YYYY"
    year_match = _re.search(r"(20\d{2})", s)
    year = int(year_match.group(1)) if year_match else datetime.today().year
    month = None
    for name, num in _MES_PT_LOOKUP.items():
        if name in s:
            month = num
            break
    if not month:
        raise ValueError(f"Nao consegui parsear --mes-referencia '{arg}' (tente 'YYYY-MM' ou 'Abril/2026')")
    return year, month


def main():
    parser = argparse.ArgumentParser(description="Build newsletter HTML")
    parser.add_argument("--stories", help="Path to stories JSON file")
    parser.add_argument("--infographics", help="JSON string or path to infographics JSON")
    parser.add_argument("--edition", default=datetime.today().strftime("%B %d, %Y"))
    parser.add_argument("--name", default="ESG em Foco", help="Newsletter name")
    parser.add_argument("--tagline", default="Notícias que transformam — curadoria ESG/CSR semanal da NTICS Projetos")
    parser.add_argument("--logo", default="", help="URL of logo image for email header")
    parser.add_argument("--trend", default="", help="Trend Watch commentary text")
    parser.add_argument("--output", help="Output HTML path")
    parser.add_argument("--periodicidade", default="mensal", choices=["semanal", "mensal"])
    parser.add_argument("--numero-edicao", type=int, default=1, help="Edition number")
    parser.add_argument("--data", help="Load all params from a single JSON file")
    parser.add_argument("--mes-referencia", help='Override do mes da secao "Projetos em Execucao" (ex: "2026-04" ou "Abril/2026"). Padrao: mes atual.')
    parser.add_argument("--no-projetos", action="store_true", help='Desliga a secao "Projetos em Execucao"')
    args = parser.parse_args()

    # Load from single data file if provided
    if args.data:
        with open(args.data, "r", encoding="utf-8") as f:
            data = json.load(f)
        stories = data.get("stories", [])
        infographics = data.get("infographics", [])
        incentives = data.get("incentives", [])
        edition = data.get("edition", args.edition)
        name = data.get("newsletter_name", args.name)
        tagline = data.get("tagline", args.tagline)
        trend_watch = data.get("trend_watch", args.trend)
        logo_url = data.get("logo_url", args.logo)
        article = data.get("article", {})
        periodicidade = data.get("periodicidade", args.periodicidade)
        numero_edicao = data.get("numero_edicao", args.numero_edicao)
        destaques = data.get("destaques", [])
        noticias = data.get("noticias", [])
        isd_data = data.get("isd_data", [])
        isd_total = data.get("isd_total", "")
        projetos_ctx = data.get("projetos_ctx")  # pode ser None ou dict explicito
        projetos_overrides = data.get("projetos_overrides") or {}
        projetos_ids = data.get("projetos_ids")  # lista opcional de ids para filtrar
    else:
        if not args.stories:
            parser.error("--stories or --data is required")

        stories = load_stories(args.stories)

        # Infographics: JSON string or file path
        infographics = []
        if args.infographics:
            if args.infographics.strip().startswith("["):
                infographics = json.loads(args.infographics)
            elif os.path.exists(args.infographics):
                with open(args.infographics, "r", encoding="utf-8") as f:
                    infographics = json.load(f)

        edition = args.edition
        name = args.name
        tagline = args.tagline
        trend_watch = args.trend
        logo_url = args.logo
        incentives = []
        article = {}
        periodicidade = args.periodicidade
        numero_edicao = args.numero_edicao
        destaques = []
        noticias = []
        isd_data = []
        isd_total = ""
        projetos_ctx = None
        projetos_overrides = {}
        projetos_ids = None

    # Resolver --mes-referencia e --no-projetos
    if args.no_projetos:
        projetos_ctx = {}  # forca desligado, template oculta
    elif projetos_ctx is None:
        year, month = _resolve_mes_referencia(args.mes_referencia)
        try:
            projetos_ctx = get_active_projects(year, month, ids=projetos_ids)
        except Exception as e:
            print(f"WARNING: nao foi possivel carregar projetos ativos ({e}). Secao ocultada.")
            projetos_ctx = {}

    # Aplicar overrides editoriais (photo_url, editorial_text)
    if projetos_ctx and projetos_overrides:
        projetos_ctx = apply_overrides(projetos_ctx, projetos_overrides)

    html = render_newsletter(
        stories=stories,
        infographics=infographics,
        incentives=incentives,
        edition=edition,
        newsletter_name=name,
        tagline=tagline,
        trend_watch=trend_watch,
        logo_url=logo_url,
        article=article,
        periodicidade=periodicidade,
        numero_edicao=numero_edicao,
        destaques=destaques,
        noticias=noticias,
        isd_data=isd_data,
        isd_total=isd_total,
        projetos_ctx=projetos_ctx,
    )

    # Determine output path
    if args.output:
        output_path = Path(args.output)
    else:
        DEFAULT_OUTPUT_DIR.mkdir(exist_ok=True)
        date_str = datetime.today().strftime("%Y-%m-%d")
        output_path = DEFAULT_OUTPUT_DIR / f"newsletter_{date_str}.html"

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"OK Newsletter built: {output_path}")
    print(f"  Stories: {len(stories)} | Infographics: {len(infographics)}")
    return str(output_path)


if __name__ == "__main__":
    main()
