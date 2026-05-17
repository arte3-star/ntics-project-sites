#!/usr/bin/env python3
"""
generate_site_html.py — Gera index.html a partir de scrape.json + cores.json.

Cores por projeto (lidas de cores.json), galeria com TODAS as fotos, régua no footer.

Uso:
  python tools/migration/generate_site_html.py \
    --project-dir "SecondBrain/projetos-anteriores/86-teatro-dos-bons-habitos-culinaria-sustentavel-ferroporte/assets" \
    --project-name "Teatro dos Bons Hábitos" \
    --github-base "https://raw.githubusercontent.com/arte3-star/ntics-project-sites/master/86_teatro_bons_habitos_ferroporte/"

Se --github-base for omitido, usa paths relativos locais (FOTOS/, LOGOS/, REGUAS/).
"""

import argparse
import json
import os
import re
from html import escape
from pathlib import Path


# ── Defaults (fallback se cores.json não existir) ──
DEFAULT_COLORS = {
    "primary": "#1E3A8A",
    "secondary": "#E91E63",
    "accent": "#F472B6",
    "dark": "#0F1F4D",
    "light": "#EFF6FF",
}


def slugify_id(text: str) -> str:
    s = text.lower().strip()
    s = re.sub(r'[^a-z0-9]+', '-', s)
    s = s.strip('-')
    return s[:40] or 'sec'


def pick_hero_img(scrape: dict) -> str | None:
    imgs = scrape.get('images', [])
    if not imgs:
        return None
    landscape = [i for i in imgs if i.get('w', 0) > 800 and i.get('w', 0) >= i.get('h', 1)]
    if landscape:
        landscape.sort(key=lambda x: -x.get('w', 0) * x.get('h', 0))
        return Path(landscape[0]['local']).name
    imgs_sorted = sorted(imgs, key=lambda x: -x.get('size', 0))
    return Path(imgs_sorted[0]['local']).name if imgs_sorted else None


def is_logo_file(name: str) -> bool:
    """Detecta se um nome de arquivo é logo (não foto do projeto)."""
    lower = name.lower()
    return 'logo' in lower or lower.endswith('.png') and any(k in lower for k in ['_logo', '-logo', 'logo_', 'logo-'])


def is_regua_file(name: str) -> bool:
    lower = name.lower()
    return 'regua' in lower or 'patrocinadores' in lower


def get_logo_filename(project_dir: Path, scrape: dict) -> str | None:
    """Pega o primeiro logo disponível de LOGOS/ (não depende de scrape.json)."""
    logos_dir = project_dir / "LOGOS"
    if logos_dir.exists():
        files = [f.name for f in logos_dir.iterdir() if f.suffix.lower() in ('.png', '.jpg', '.jpeg', '.svg', '.webp') and f.name != 'desktop.ini']
        if files:
            return files[0]
    # Fallback: scrape.json logo_detected
    return scrape.get('logo_detected')


def get_regua_files(project_dir: Path, scrape: dict) -> list[str]:
    """Pega todas as réguas de REGUAS/ (não depende de scrape.json)."""
    reguas_dir = project_dir / "REGUAS"
    files = []
    if reguas_dir.exists():
        files = [f.name for f in reguas_dir.iterdir() if f.suffix.lower() in ('.png', '.jpg', '.jpeg', '.webp') and f.name != 'desktop.ini']
    if not files:
        files = scrape.get('reguas_detected', []) or []
    return files


def get_all_fotos(project_dir: Path, scrape: dict) -> list[str]:
    """Retorna TODAS as fotos de FOTOS/, filtrando logos e réguas."""
    fotos_dir = project_dir / "FOTOS"
    if fotos_dir.exists():
        all_files = [f.name for f in fotos_dir.iterdir()
                     if f.suffix.lower() in ('.jpg', '.jpeg', '.png', '.webp')
                     and f.name != 'desktop.ini'
                     and not is_logo_file(f.name)
                     and not is_regua_file(f.name)]
        return sorted(all_files)
    # Fallback: scrape.json images
    return [Path(im['local']).name for im in scrape.get('images', [])
            if not is_logo_file(Path(im['local']).name) and not is_regua_file(Path(im['local']).name)]


def load_colors(project_dir: Path) -> dict:
    cores_file = project_dir / "cores.json"
    if cores_file.exists():
        try:
            return json.loads(cores_file.read_text(encoding='utf-8'))
        except Exception:
            pass
    return DEFAULT_COLORS.copy()


def build_section_dark(sid, title, paragraph, img_url, alt, colors):
    img_block = ''
    if img_url:
        img_block = f'<div class="rounded-2xl overflow-hidden shadow-2xl"><img src="{img_url}" alt="{escape(alt)}" class="w-full h-full object-cover"></div>'
    p = f'<p class="text-lg leading-relaxed opacity-90">{escape(paragraph)}</p>' if paragraph else ''
    return f'''
  <section id="{sid}" style="background-color: {colors['dark']};" class="py-20 px-6 text-white">
    <div class="max-w-6xl mx-auto grid md:grid-cols-2 gap-12 items-center">
      <div>
        <h2 class="text-3xl md:text-5xl font-extrabold mb-6 tracking-wide">{escape(title)}</h2>
        {p}
      </div>
      {img_block}
    </div>
  </section>
'''


def build_section_light(sid, title, paragraph, img_url, alt, colors):
    img_block = ''
    if img_url:
        img_block = f'<div class="rounded-2xl overflow-hidden shadow-2xl"><img src="{img_url}" alt="{escape(alt)}" class="w-full h-full object-cover"></div>'
    p = f'<p class="text-lg leading-relaxed text-slate-700">{escape(paragraph)}</p>' if paragraph else ''
    return f'''
  <section id="{sid}" style="background-color: {colors['light']};" class="py-20 px-6">
    <div class="max-w-6xl mx-auto grid md:grid-cols-2 gap-12 items-center">
      {img_block}
      <div>
        <h2 class="text-3xl md:text-5xl font-extrabold mb-6 tracking-wide" style="color: {colors['primary']};">{escape(title)}</h2>
        {p}
      </div>
    </div>
  </section>
'''


def build_section_center(title, paragraph, colors):
    p = f'<p class="text-lg leading-relaxed text-slate-700">{escape(paragraph)}</p>' if paragraph else ''
    return f'''
  <section class="py-20 px-6 bg-white">
    <div class="max-w-3xl mx-auto text-center">
      <h2 class="text-3xl md:text-5xl font-extrabold mb-6 tracking-wide" style="color: {colors['primary']};">{escape(title)}</h2>
      {p}
    </div>
  </section>
'''


def generate(project_dir: Path, project_name: str, github_base: str = '') -> Path:
    scrape = json.loads((project_dir / 'scrape.json').read_text(encoding='utf-8'))
    colors = load_colors(project_dir)

    img_prefix = f'{github_base}FOTOS/' if github_base else 'FOTOS/'
    logo_prefix = f'{github_base}LOGOS/' if github_base else 'LOGOS/'
    regua_prefix = f'{github_base}REGUAS/' if github_base else 'REGUAS/'

    # Assets reais do filesystem
    logo = get_logo_filename(project_dir, scrape)
    reguas = get_regua_files(project_dir, scrape)
    all_fotos = get_all_fotos(project_dir, scrape)
    hero_img = pick_hero_img(scrape)

    title = f"{project_name} — NTICS Projetos"
    description = ''
    for p in scrape.get('paragraphs', []):
        if len(p) > 80 and 'Renderforest' not in p:
            description = p[:160]
            break

    # Hero title
    hero_title = project_name
    if scrape.get('h1'):
        for h1 in scrape['h1']:
            if h1 and len(h1) < 60:
                hero_title = h1
                break

    hero_subtitle = ''
    for p in scrape.get('paragraphs', []):
        if 15 < len(p) < 120 and 'Renderforest' not in p and p != hero_title:
            hero_subtitle = p
            break
    if not hero_subtitle:
        hero_subtitle = 'Projeto NTICS Projetos • Lei Rouanet'

    # HTML fragments
    hero_bg_html = ''
    if hero_img:
        hero_bg_html = f'<img src="{img_prefix}{hero_img}" alt="{escape(project_name)}" class="absolute inset-0 w-full h-full object-cover">'

    hero_logo_html = ''
    header_logo_html = ''
    sobre_logo_html = ''
    if logo:
        hero_logo_html = f'<img src="{logo_prefix}{logo}" alt="Logo {escape(project_name)}" class="h-32 md:h-40 mx-auto mb-6 bg-white/95 rounded-2xl p-4 shadow-2xl">'
        header_logo_html = f'<img src="{logo_prefix}{logo}" alt="Logo" class="h-10 bg-white rounded-lg p-1">'
        sobre_logo_html = f'<img src="{logo_prefix}{logo}" alt="Logo {escape(project_name)}" class="w-full max-w-sm">'

    # Sobre paragraphs (2 mais longos)
    long_paragraphs = [p for p in scrape.get('paragraphs', []) if len(p) > 80 and 'Renderforest' not in p][:2]
    sobre_paragraphs_html = '\n        '.join(
        f'<p class="text-lg text-slate-700 leading-relaxed mb-4">{escape(p)}</p>' for p in long_paragraphs
    )

    # Nav
    nav_items = [f'<a href="#sobre" class="hover:opacity-80 transition">Sobre</a>']
    primary_title = scrape.get('h1', [''])[0] if scrape.get('h1') else ''
    count = 0
    seen_nav_ids = set()
    for h2 in scrape.get('h2', []):
        if not h2 or len(h2) > 30 or h2 == primary_title:
            continue
        if count >= 4:
            break
        sid = slugify_id(h2)
        if sid in seen_nav_ids:
            continue
        seen_nav_ids.add(sid)
        label = h2.split()[0].title() if h2.split() else h2
        nav_items.append(f'<a href="#{sid}" class="hover:opacity-80 transition">{escape(label)}</a>')
        count += 1
    nav_items.append(f'<a href="#galeria" class="hover:opacity-80 transition">Galeria</a>')
    nav_links_html = '\n        '.join(nav_items)

    # Dynamic sections based on h2s
    dynamic_sections = ''
    valid_h2s = []
    for h2 in scrape.get('h2', []):
        if not h2 or len(h2) < 3 or h2 == primary_title:
            continue
        if re.match(r'^(s[aã]o|rio|cidade|[A-Z][a-z]+ ?[A-Z]{2})$', h2[:30].lower()):
            continue
        valid_h2s.append(h2)
    valid_h2s = valid_h2s[:5]

    style_cycle = ['dark', 'light', 'dark', 'center', 'dark']
    # Fotos para seções temáticas (primeiras fotos, hero excluído)
    section_img_pool = [n for n in all_fotos if n != hero_img]
    used_paragraphs = set()
    used_section_imgs = set()

    for i, h2 in enumerate(valid_h2s):
        # Parágrafo associado
        related_p = ''
        for j, p in enumerate(scrape.get('paragraphs', [])):
            if j in used_paragraphs:
                continue
            if 50 < len(p) < 800 and 'Renderforest' not in p:
                related_p = p
                used_paragraphs.add(j)
                break

        style = style_cycle[i % len(style_cycle)]
        sid = slugify_id(h2)
        img_url = ''
        if style != 'center' and i < len(section_img_pool):
            img_name = section_img_pool[i]
            img_url = f'{img_prefix}{img_name}'
            used_section_imgs.add(img_name)

        if style == 'dark':
            dynamic_sections += build_section_dark(sid, h2, related_p, img_url, h2, colors)
        elif style == 'light':
            dynamic_sections += build_section_light(sid, h2, related_p, img_url, h2, colors)
        else:
            dynamic_sections += build_section_center(h2, related_p, colors)

    # Galeria: TODAS as fotos que NÃO são hero e NÃO foram usadas em seções
    gallery_fotos = [n for n in all_fotos if n != hero_img and n not in used_section_imgs]
    # Grid adaptativo
    if len(gallery_fotos) <= 4:
        grid_class = "grid-cols-2"
    elif len(gallery_fotos) <= 9:
        grid_class = "grid-cols-2 md:grid-cols-3"
    else:
        grid_class = "grid-cols-2 md:grid-cols-3 lg:grid-cols-4"

    gallery_items = []
    for name in gallery_fotos:
        gallery_items.append(
            f'<img src="{img_prefix}{escape(name)}" alt="{escape(project_name)} - momento" '
            f'class="w-full h-64 object-cover rounded-xl shadow-lg hover:scale-105 transition">'
        )
    gallery_html = '\n        '.join(gallery_items)
    gallery_count_html = f'<p class="text-white/60 text-sm text-center mb-8">{len(gallery_fotos)} fotos do projeto</p>'

    # Footer regua
    footer_regua = ''
    if reguas:
        footer_regua = f'<img src="{regua_prefix}{escape(reguas[0])}" alt="Régua de patrocinadores" class="max-w-4xl w-full mx-auto">'

    # Hero overlay usando cores do projeto
    overlay_css = f"background: linear-gradient(135deg, {colors['primary']}D9 0%, {colors['secondary']}88 100%);"

    html = f'''<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{escape(title)}</title>
  <meta name="description" content="{escape(description)}">
  <script src="https://cdn.tailwindcss.com"></script>
  <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
  <style>
    * {{ font-family: 'Poppins', system-ui, sans-serif; }}
    .hero-overlay {{ {overlay_css} }}
  </style>
</head>
<body class="bg-white text-slate-800">

  <header style="background-color: {colors['primary']};" class="text-white sticky top-0 z-50 shadow-lg">
    <div class="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
      <div class="flex items-center gap-3">
        {header_logo_html}
        <span class="font-bold text-lg hidden md:inline">{escape(hero_title)}</span>
      </div>
      <nav class="hidden md:flex gap-8 text-sm font-medium">
        {nav_links_html}
      </nav>
    </div>
  </header>

  <section class="relative h-[80vh] min-h-[500px] flex items-center justify-center overflow-hidden">
    {hero_bg_html}
    <div class="absolute inset-0 hero-overlay"></div>
    <div class="relative z-10 text-center text-white px-6 max-w-4xl">
      {hero_logo_html}
      <h1 class="text-5xl md:text-7xl font-black mb-4 drop-shadow-2xl">{escape(hero_title)}</h1>
      <p class="text-xl md:text-2xl font-light">{escape(hero_subtitle)}</p>
    </div>
  </section>

  <section id="sobre" class="py-20 px-6">
    <div class="max-w-5xl mx-auto grid md:grid-cols-2 gap-12 items-center">
      <div>
        {sobre_logo_html}
      </div>
      <div>
        <h2 class="text-3xl md:text-4xl font-extrabold mb-6 tracking-wide" style="color: {colors['primary']};">Sobre o Projeto</h2>
        {sobre_paragraphs_html}
      </div>
    </div>
  </section>

{dynamic_sections}

  <section id="galeria" style="background-color: {colors['dark']};" class="py-20 px-6">
    <div class="max-w-6xl mx-auto">
      <h2 class="text-3xl md:text-5xl font-extrabold text-white text-center mb-4 tracking-wide">GALERIA DE FOTOS</h2>
      {gallery_count_html}
      <div class="grid {grid_class} gap-4">
        {gallery_html}
      </div>
    </div>
  </section>

  <footer class="bg-white py-12 px-6" style="border-top: 4px solid {colors['primary']};">
    <div class="max-w-5xl mx-auto text-center">
      <p class="text-sm uppercase tracking-widest text-slate-500 mb-6 font-semibold">Patrocínio &amp; Realização</p>
      {footer_regua}
      <p class="text-xs text-slate-400 mt-8">
        Projeto realizado via Lei de Incentivo à Cultura (Lei Rouanet) — Ministério da Cultura — Governo Federal
      </p>
    </div>
  </footer>

</body>
</html>
'''

    out = project_dir / 'index.html'
    out.write_text(html, encoding='utf-8')
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--project-dir', required=True)
    ap.add_argument('--project-name', required=True)
    ap.add_argument('--github-base', default='')
    args = ap.parse_args()

    out = generate(Path(args.project_dir), args.project_name, args.github_base)
    print(f'Generated: {out}')


if __name__ == '__main__':
    main()
