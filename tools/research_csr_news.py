"""
research_csr_news.py — Validates and persists curated CSR/ESG stories to .tmp/.

This script is the bridge between the agent's curation work and the newsletter build step.
The agent reads raw Perplexity output, curates 10-15 stories, and passes them here as JSON.

Usage:
  python tools/research_csr_news.py --stories '[{...}, {...}]' --output .tmp/stories_2026-03-20.json

  Or from a file:
  python tools/research_csr_news.py --stories-file .tmp/curated_stories.json

Story schema (each story must have these fields):
  {
    "title": str,           # Story headline
    "company": str,         # Company name (can be empty "")
    "source": str,          # Publication name (e.g., "ESG Today")
    "url": str,             # Full article URL
    "date": str,            # ISO date YYYY-MM-DD
    "summary": str,         # 2-3 sentence summary
    "category": str,        # "environment" | "social" | "governance"
    "headline_stat": str,   # Key metric (e.g., "34% reduction in Scope 1 emissions")
    "stat_label": str,      # Description of the hero stat (for story of the week)
    "what_it_means": str    # One sentence of significance (for story of the week)
  }
"""

import argparse
import json
import sys
from datetime import datetime, date
from pathlib import Path

DEFAULT_OUTPUT_DIR = Path(__file__).parent.parent / ".tmp"

REQUIRED_FIELDS = ["title", "summary", "category", "url"]
VALID_CATEGORIES = {"environment", "social", "governance", "meio ambiente", "governança", "governanca"}


def validate_story(story: dict, index: int) -> list:
    """Returns list of validation errors for a story."""
    errors = []
    for field in REQUIRED_FIELDS:
        if not story.get(field, "").strip():
            errors.append(f"Story {index}: missing required field '{field}'")

    cat = story.get("category", "").lower().strip()
    if cat and cat not in VALID_CATEGORIES:
        errors.append(f"Story {index}: unknown category '{cat}' (use environment/social/governance)")

    return errors


def normalize_story(story: dict) -> dict:
    """Fill in defaults and normalize field values."""
    cat = story.get("category", "environment").lower().strip()
    if cat in ("meio ambiente",):
        cat = "environment"
    if cat in ("governança", "governanca"):
        cat = "governance"

    return {
        "title": story.get("title", "").strip(),
        "company": story.get("company", "").strip(),
        "source": story.get("source", "").strip(),
        "url": story.get("url", "#").strip(),
        "date": story.get("date", str(date.today())),
        "summary": story.get("summary", "").strip(),
        "category": cat,
        "headline_stat": story.get("headline_stat", "").strip(),
        "stat_label": story.get("stat_label", story.get("title", "")).strip(),
        "what_it_means": story.get("what_it_means", "").strip(),
    }


def main():
    parser = argparse.ArgumentParser(description="Persist curated CSR/ESG stories")
    parser.add_argument("--stories", help="JSON array of story objects (as string)")
    parser.add_argument("--stories-file", help="Path to JSON file with story array")
    parser.add_argument("--output", help="Output path for persisted stories JSON")
    parser.add_argument("--strict", action="store_true", help="Fail on any validation error")
    args = parser.parse_args()

    # Load stories
    if args.stories_file:
        with open(args.stories_file, "r", encoding="utf-8") as f:
            stories_raw = json.load(f)
    elif args.stories:
        stories_raw = json.loads(args.stories)
    else:
        parser.error("--stories or --stories-file is required")

    if not isinstance(stories_raw, list):
        print("ERROR: stories must be a JSON array")
        sys.exit(1)

    print(f"Validating {len(stories_raw)} stories...")

    # Validate and normalize
    all_errors = []
    stories = []
    for i, raw in enumerate(stories_raw):
        errors = validate_story(raw, i + 1)
        if errors:
            all_errors.extend(errors)
            if args.strict:
                for e in errors:
                    print(f"  ✗ {e}")
                continue
            else:
                for e in errors:
                    print(f"  ⚠ {e}")
        stories.append(normalize_story(raw))

    if args.strict and all_errors:
        print(f"\nERROR: {len(all_errors)} validation errors in strict mode. Fix and retry.")
        sys.exit(1)

    if len(stories) < 3:
        print(f"WARNING: Only {len(stories)} valid stories. Newsletter may look sparse.")

    # Category summary
    by_cat = {"environment": 0, "social": 0, "governance": 0}
    for s in stories:
        by_cat[s["category"]] = by_cat.get(s["category"], 0) + 1
    print(f"  Environment: {by_cat['environment']} | Social: {by_cat['social']} | Governance: {by_cat['governance']}")

    # Output path
    if args.output:
        output_path = Path(args.output)
    else:
        DEFAULT_OUTPUT_DIR.mkdir(exist_ok=True)
        date_str = datetime.today().strftime("%Y-%m-%d")
        output_path = DEFAULT_OUTPUT_DIR / f"stories_{date_str}.json"

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(stories, f, ensure_ascii=False, indent=2)

    print(f"\n✓ {len(stories)} stories saved to: {output_path}")
    print(f"\nNext step:")
    print(f"  python tools/build_newsletter.py --stories {output_path}")
    return str(output_path)


if __name__ == "__main__":
    main()
