"""
Remove fotos dentro de cada site que não são mais referenciadas pelo index.html.
Preserva logos, réguas e qualquer arquivo usado no HTML.
"""
from pathlib import Path
import re

REPO = Path(r"G:/O meu disco/AUTOMAÇÕES/.tmp/ntics-project-sites")

IMG_RE = re.compile(r'["\'](https://raw\.githubusercontent\.com/[^"\']+|(?:assets|FOTOS)/[^"\']+?\.(?:jpg|jpeg|png|webp))["\']', re.IGNORECASE)

PHOTO_DIRS = ["FOTOS", "assets/imagens", "assets/galeria"]

def get_referenced_files(html: str, site_dir: Path) -> set[Path]:
    refs: set[Path] = set()
    for m in IMG_RE.finditer(html):
        url = m.group(1)
        if url.startswith("http"):
            # Extract path after <slug>/
            tail = url.split(f"{site_dir.name}/", 1)
            if len(tail) == 2:
                refs.add(site_dir / tail[1])
        else:
            refs.add(site_dir / url)
    return refs

def main():
    total_deleted = 0
    for site_dir in sorted(REPO.iterdir()):
        if not site_dir.is_dir() or site_dir.name.startswith("."):
            continue
        html_path = site_dir / "index.html"
        if not html_path.exists():
            continue
        html = html_path.read_text(encoding="utf-8")
        referenced = get_referenced_files(html, site_dir)
        # Also keep anything in LOGOS/ and REGUAS/
        for photo_dir_rel in PHOTO_DIRS:
            pdir = site_dir / photo_dir_rel
            if not pdir.exists():
                continue
            for photo in pdir.rglob("*"):
                if photo.is_file() and photo.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}:
                    if photo.resolve() not in {r.resolve() for r in referenced}:
                        # Keep desktop.ini and hidden files
                        if photo.name == "desktop.ini":
                            continue
                        photo.unlink()
                        total_deleted += 1
                        print(f"deleted {photo.relative_to(REPO)}")
    print(f"\nTotal deleted: {total_deleted}")

if __name__ == "__main__":
    main()
