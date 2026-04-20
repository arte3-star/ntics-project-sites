"""
generate_project_site.py — Generates project website HTML files from briefing data.

Usage:
  python tools/generate_project_site.py --data .tmp/sites/projects_data.json
  python tools/generate_project_site.py --data .tmp/sites/projects_data.json --project 127_pie
"""

import argparse
import json
import sys
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
    print("WARNING: premailer not installed. CSS won't be inlined.")

TEMPLATE_DIR = Path(__file__).parent / "templates"
DEFAULT_OUTPUT_DIR = Path(__file__).parent.parent / "output" / "marketing" / "sites" / "projetos-ativos"


def render_site(project: dict) -> str:
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATE_DIR)),
        autoescape=False,
    )
    template = env.get_template("project_site.html")

    html = template.render(**project)

    # Note: premailer is NOT used here — these HTMLs target Lovable (modern browser),
    # not email clients. Premailer mangles modern CSS (flexbox, grid, rem units).
    return html


def main():
    parser = argparse.ArgumentParser(description="Generate project website HTML")
    parser.add_argument("--data", required=True, help="Path to projects JSON data file")
    parser.add_argument("--project", help="Generate only this project ID (e.g. 127_pie)")
    parser.add_argument("--output-dir", help="Output directory", default=str(DEFAULT_OUTPUT_DIR))
    args = parser.parse_args()

    with open(args.data, "r", encoding="utf-8") as f:
        projects = json.load(f)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    if args.project:
        projects = [p for p in projects if p["id"] == args.project]
        if not projects:
            print(f"ERROR: Project '{args.project}' not found in data file.")
            sys.exit(1)

    generated = []
    for project in projects:
        pid = project["id"]
        print(f"Generating: {project['project_name']}...")

        html = render_site(project)

        output_path = output_dir / f"{pid}.html"
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html)

        print(f"  -> {output_path}")
        generated.append(str(output_path))

    print(f"\nDone! Generated {len(generated)} site(s)")
    for path in generated:
        print(f"  {path}")

    return generated


if __name__ == "__main__":
    main()
