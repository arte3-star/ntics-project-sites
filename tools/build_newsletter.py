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
        logo_url=logo_url or os.getenv("NEWSLETTER_LOGO_URL", ""),
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
    )

    # Inline CSS for email client compatibility
    if HAS_PREMAILER:
        try:
            html = premailer.transform(html)
        except Exception as e:
            print(f"WARNING: premailer transform failed ({e}). Using raw HTML.")

    return html


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
    parser.add_argument("--data", help="Load all params from a single JSON file")
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

    print(f"✓ Newsletter built: {output_path}")
    print(f"  Stories: {len(stories)} | Infographics: {len(infographics)}")
    return str(output_path)


if __name__ == "__main__":
    main()
