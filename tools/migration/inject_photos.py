"""Injeta fotos nos site.html substituindo placeholders SVG por <img>."""
import json
import re
from pathlib import Path
from bs4 import BeautifulSoup

ROOT = Path(r"g:\O meu disco\AUTOMAÇÕES")
assignments = json.loads((ROOT / "output/rankings/assignments.json").read_text(encoding="utf-8"))

def inject_type_a(site_id, site_dir, html_path):
    """Template atividades (116/117/119/124/125): substitui placeholders SVG das atividades."""
    html = html_path.read_text(encoding="utf-8", errors="replace")
    soup = BeautifulSoup(html, "html.parser")
    placeholders = soup.select("div.rounded-3xl.aspect-\\[16\\/10\\].relative.overflow-hidden.grain.card-hover")
    # Map atividade_1..N to placeholders in order
    ativ_slots = [a for a in assignments[site_id]["assignments"] if a["slot"].startswith("atividade_")]
    ativ_slots.sort(key=lambda x: int(x["slot"].split("_")[1]))
    if len(placeholders) != len(ativ_slots):
        print(f"WARN {site_id}: {len(placeholders)} placeholders vs {len(ativ_slots)} atividades")
    for ph, ativ in zip(placeholders, ativ_slots):
        # Extract caption for alt text
        alt = ativ["caption"]
        img_tag = soup.new_tag(
            "img",
            src=f"FOTOS/{ativ['slot']}.jpg",
            alt=alt,
            attrs={"class": "rounded-3xl aspect-[16/10] object-cover w-full h-full card-hover", "loading": "lazy"},
        )
        ph.replace_with(img_tag)
    html_path.write_text(str(soup), encoding="utf-8")
    return len(ativ_slots)

def inject_type_b(site_id, site_dir, html_path):
    """Template galeria (127G/127S): substitui <span class='gal-ph'> por <img>."""
    html = html_path.read_text(encoding="utf-8", errors="replace")
    soup = BeautifulSoup(html, "html.parser")
    gal_items = soup.select("div.gal-item")
    # Use atividade_N as the 6 galeria images (semantically pre-matched)
    ativ = [a for a in assignments[site_id]["assignments"] if a["slot"].startswith("atividade_")]
    ativ.sort(key=lambda x: int(x["slot"].split("_")[1]))
    for i, item in enumerate(gal_items):
        if i >= len(ativ): break
        # Clear children (svg + span)
        for child in list(item.children):
            if getattr(child, "decompose", None):
                child.decompose()
            elif str(child).strip():
                child.extract()
        img = soup.new_tag(
            "img",
            src=f"FOTOS/{ativ[i]['slot']}.jpg",
            alt=ativ[i]["caption"],
            attrs={"loading": "lazy", "style": "width:100%; height:100%; object-fit:cover;"},
        )
        item.append(img)
    html_path.write_text(str(soup), encoding="utf-8")
    return len(gal_items)

def main():
    for site_id, d in assignments.items():
        site_dir = ROOT / "assets/projetos" / d["dir"]
        html_path = site_dir / "site.html"
        html = html_path.read_text(encoding="utf-8", errors="replace")
        if "gal-item" in html:
            n = inject_type_b(site_id, site_dir, html_path)
            print(f"[{site_id}] type B: {n} galeria slots injetados")
        else:
            n = inject_type_a(site_id, site_dir, html_path)
            print(f"[{site_id}] type A: {n} atividades injetadas")

if __name__ == "__main__":
    main()
