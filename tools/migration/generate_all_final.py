#!/usr/bin/env python3
"""
generate_all_final.py — Gera HTML fiel para todos os 9 sites.

Usa section_map.json de cada projeto para respeitar a estrutura exata do RF.
"""

import json
import re
import sys
import io
from pathlib import Path
from html import escape

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = Path(__file__).resolve().parents[2]


def get_cidades(scrape_h2: list) -> list:
    """Extrai lista de cidades dos h2 (formato 'CIDADE - UF' ou 'Cidade/UF')."""
    ufs = ['SC', 'SP', 'RJ', 'RS', 'ES', 'MG', 'PR', 'BA', 'PI', 'PA', 'GO', 'MA', 'AM', 'DF', 'CE']
    cidades = []
    for h in scrape_h2:
        h_clean = h.replace('\n', ' ').strip()
        # Match "Cidade - UF" or "Cidade/UF"
        m = re.match(r'^([A-Za-záéíóúâêôãõçÁÉÍÓÚÂÊÔÃÕÇ\s]+?)\s*[\-/]\s*([A-Z]{2})\s*$', h_clean)
        if m:
            cidade, uf = m.group(1).strip(), m.group(2)
            if uf in ufs:
                cidades.append({'cidade': cidade, 'uf': uf})
    return cidades


def pick_overall_layout(total_photos: int, grid_sections: int) -> dict:
    """Decide grid layout based on photo count."""
    if total_photos <= 4:
        return {'cols': 'grid-cols-2', 'cols_md': 'md:grid-cols-2'}
    if total_photos <= 9:
        return {'cols': 'grid-cols-2', 'cols_md': 'md:grid-cols-3'}
    return {'cols': 'grid-cols-2', 'cols_md': 'md:grid-cols-3 lg:grid-cols-4'}


def get_regua_hashes(project_num: int) -> set:
    """Retorna set de hashes que SÃO a régua do projeto (para filtrar da galeria)."""
    hashes = set()
    for d in (ROOT / 'assets' / 'projetos').iterdir():
        if d.name.startswith(f'{project_num}. '):
            reguas_dir = d / 'REGUAS'
            if reguas_dir.exists():
                for f in reguas_dir.iterdir():
                    if f.suffix.lower() in ('.jpg', '.jpeg', '.png') and f.name != 'desktop.ini':
                        # Extract hash from regua_HASH.jpg or rf-NNN-HASH.jpg
                        name = f.name.replace('regua_', '')
                        h = name.split('.')[0]
                        # If name is rf-NNN-HASH, get the HASH part
                        if h.startswith('rf-'):
                            parts = h.split('-')
                            if len(parts) >= 3:
                                h = parts[-1]
                        hashes.add(h)
            break
    return hashes


def is_regua(filename: str, regua_hashes: set) -> bool:
    """Detecta se filename é uma régua."""
    if 'regua' in filename.lower() or 'REGUAS' in filename:
        return True
    for h in regua_hashes:
        if h in filename:
            return True
    return False


def generate_html(project: dict, colors: dict, scrape: dict) -> str:
    """Gera HTML fiel ao RF usando section_map."""
    num = project['numero']
    nome = project['nome']
    slug = project['slug']
    logo = project['logo']
    regua = project['regua']
    youtube_ids = project['youtube_ids']
    sections = project['sections']

    # Get regua hashes to filter from galleries
    regua_hashes = get_regua_hashes(num)

    BASE = f'https://raw.githubusercontent.com/arte3-star/ntics-project-sites/master/{slug}'

    primary = colors.get('primary', '#1E3A8A')
    secondary = colors.get('secondary', '#E91E63')
    dark = colors.get('dark', '#0F1F4D')
    light = colors.get('light', '#EFF6FF')

    # Cities from h2
    cidades = get_cidades(scrape.get('h2', []))

    # Paragraphs
    paragraphs = [p for p in scrape.get('paragraphs', []) if 'Renderforest' not in p]

    # Main intro paragraph (first long one)
    intro_p = next((p for p in paragraphs if len(p) > 80), '')

    # Democratização text
    demo_p = next((p for p in paragraphs if 'democra' in p.lower()), '')

    # Title (h1 first) — skip "MINISTÉRIO DA CULTURA APRESENTA:" prefix
    hero_title_raw = scrape.get('h1', [nome])[0] if scrape.get('h1') else nome
    # Split by newline - if first line is "O MINISTÉRIO DA CULTURA APRESENTA:", use next line
    parts = [p.strip() for p in hero_title_raw.split('\n') if p.strip()]
    if parts and 'MINISTÉRIO DA CULTURA' in parts[0].upper():
        hero_title = parts[1] if len(parts) > 1 else nome
    else:
        hero_title = parts[0] if parts else nome
    hero_title = hero_title[:60]

    # Hero subtitle (h2 second or h1 second)
    hero_subtitle = ''
    h1s = scrape.get('h1', [])
    if len(h1s) > 1:
        hero_subtitle = h1s[1][:80]
    elif scrape.get('h2'):
        for h in scrape['h2']:
            if h and h != hero_title and len(h) < 80 and not any(uf in h for uf in ['SC', 'SP', 'RJ']):
                hero_subtitle = h
                break
    if not hero_subtitle:
        hero_subtitle = 'Projeto NTICS • Lei de Incentivo à Cultura'

    # Build sections HTML based on section_map
    sections_html = []

    # Find hero image (first image or first bg image)
    hero_img_name = None
    for s in sections:
        if s['imgs']:
            hero_img_name = s['imgs'][0]
            break
    if not hero_img_name:
        for s in sections:
            if s['bgs']:
                hero_img_name = s['bgs'][0]
                break

    # Mark which photos are used in sections vs galeria
    used_in_sections = set()

    # Merge consecutive sections without titles into the previous section (like 87's 4 grids)
    merged_sections = []
    for s in sections:
        if not s['title'].strip() and (s['imgs'] or s['bgs']) and merged_sections and merged_sections[-1]['title'].strip():
            # Merge into previous
            merged_sections[-1]['imgs'].extend(s['imgs'])
            merged_sections[-1]['bgs'].extend(s['bgs'])
            merged_sections[-1]['_multi_grid'] = True
        else:
            merged_sections.append({**s})
    sections = merged_sections

    # Process each section according to its pattern
    for s in sections:
        title = s['title'].strip()
        # Filter out reguas from any section's photos
        imgs = [f for f in s['imgs'] if not is_regua(f, regua_hashes)]
        bgs = [f for f in s['bgs'] if not is_regua(f, regua_hashes)]
        all_photos = imgs + bgs

        if not title and not all_photos:
            continue

        title_upper = title.upper()

        # Skip hero/first section (handled separately)
        if s['idx'] == 0 or 'SOBRE' in title_upper and s['idx'] <= 1:
            if all_photos:
                used_in_sections.update(all_photos)
            continue

        # POR ONDE PASSAMOS (cities section)
        if 'POR ONDE' in title_upper:
            used_in_sections.update(all_photos)
            bg_url = f'{BASE}/FOTOS/{all_photos[0]}' if all_photos else ''
            cidades_html = '\n        '.join([
                f'<div class="bg-white/10 backdrop-blur rounded-2xl p-5 text-center border border-white/15 hover:bg-white/20 transition"><p class="font-bold text-white">{escape(c["cidade"])}</p><p class="text-sm text-white/60">{c["uf"]}</p></div>'
                for c in cidades
            ])
            bg_html = f'<div class="absolute inset-0 opacity-15"><img src="{bg_url}" alt="" class="w-full h-full object-cover"></div>' if bg_url else ''
            sections_html.append(f'''
  <section id="cidades" class="relative py-20 px-6 overflow-hidden" style="background-color: {dark};">
    {bg_html}
    <div class="relative z-10 max-w-5xl mx-auto">
      <h2 class="text-3xl md:text-5xl font-extrabold text-center mb-12 tracking-wide text-white">POR ONDE PASSAMOS</h2>
      <div class="grid grid-cols-2 md:grid-cols-{min(len(cidades), 5)} gap-5">
        {cidades_html}
      </div>
    </div>
  </section>''')
            continue

        # DEMOCRATIZAÇÃO DE ACESSO
        if 'DEMOCRATIZAÇÃO' in title_upper or 'DEMOCRATIZACAO' in title_upper:
            used_in_sections.update(all_photos)
            video_html = ''
            if youtube_ids:
                video_html = f'''
      <div class="max-w-4xl mx-auto rounded-3xl overflow-hidden shadow-2xl">
        <iframe src="https://www.youtube.com/embed/{youtube_ids[0]}" width="100%" height="500" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen class="w-full aspect-video"></iframe>
      </div>'''
            sections_html.append(f'''
  <section id="democratizacao" class="py-20 px-6 bg-white">
    <div class="max-w-5xl mx-auto text-center">
      <h2 class="text-3xl md:text-5xl font-extrabold mb-8 tracking-wide" style="color: {secondary};">DEMOCRATIZAÇÃO DE ACESSO</h2>
      <p class="text-lg text-slate-700 leading-relaxed mb-10 max-w-3xl mx-auto">{escape(demo_p or "O projeto conta com a disponibilização online para democratizar o acesso à cultura.")}</p>
      {video_html}
    </div>
  </section>''')
            continue

        # ASSISTA AOS VÍDEOS / ASSISTA O VÍDEO (additional video sections)
        if 'ASSISTA' in title_upper or ('VÍDEO' in title_upper and 'GALERIA' not in title_upper):
            # Use next available youtube IDs
            video_section_idx = len([sh for sh in sections_html if 'youtube' in sh])
            if video_section_idx < len(youtube_ids):
                yt_id = youtube_ids[video_section_idx] if video_section_idx < len(youtube_ids) else youtube_ids[0]
                sections_html.append(f'''
  <section class="py-20 px-6" style="background-color: {light};">
    <div class="max-w-5xl mx-auto text-center">
      <h2 class="text-3xl md:text-4xl font-extrabold mb-8 tracking-wide" style="color: {primary};">{escape(title)}</h2>
      <div class="max-w-4xl mx-auto rounded-3xl overflow-hidden shadow-2xl">
        <iframe src="https://www.youtube.com/embed/{yt_id}" width="100%" height="500" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen class="w-full aspect-video"></iframe>
      </div>
    </div>
  </section>''')
            continue

        # GALERIA DE FOTOS
        if 'GALERIA' in title_upper:
            # Filter out reguas from galeria
            all_photos = [f for f in all_photos if not is_regua(f, regua_hashes)]
            used_in_sections.update(all_photos)
            if not all_photos:
                continue
            # Masonry-style layout with variable sizes (like RF)
            items_html = []
            sizes = ['col-span-2 md:col-span-2', 'col-span-1', 'col-span-1',
                     'col-span-1 md:col-span-2', 'col-span-2 md:col-span-2',
                     'col-span-1', 'col-span-1', 'col-span-1', 'col-span-2']
            for i, f in enumerate(all_photos):
                sz = sizes[i % len(sizes)]
                items_html.append(
                    f'<div class="{sz} overflow-hidden rounded-xl shadow-lg"><img src="{BASE}/FOTOS/{f}" alt="{escape(nome)} - momento" loading="lazy" class="w-full h-64 object-cover hover:scale-105 transition duration-500"></div>'
                )
            gal_html = '\n        '.join(items_html)
            sections_html.append(f'''
  <section id="galeria" class="py-20 px-6" style="background-color: {dark};">
    <div class="max-w-6xl mx-auto">
      <h2 class="text-3xl md:text-5xl font-extrabold text-white text-center mb-4 tracking-wide">GALERIA DE FOTOS</h2>
      <p class="text-white/60 text-center mb-12">{len(all_photos)} registros do projeto</p>
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
        {gal_html}
      </div>
    </div>
  </section>''')
            continue

        # Any other content section (OFICINA, APRESENTAÇÃO, WORKSHOP, PEÇA, PALESTRA, etc.)
        if all_photos:
            used_in_sections.update(all_photos)
            # Find related paragraph
            related_p = ''
            for p in paragraphs:
                if any(word in p.lower() for word in title.lower().split()[:2]):
                    related_p = p
                    break
            if not related_p:
                # Use next unused paragraph > 80 chars
                for p in paragraphs:
                    if len(p) > 80 and p != intro_p and p != demo_p:
                        related_p = p
                        break

            # If section has many photos (>=8), render as large photo grid (like RF exposition)
            if len(all_photos) >= 8:
                # Split into rows of 4
                grid_rows = []
                for i in range(0, len(all_photos), 4):
                    row_imgs = all_photos[i:i+4]
                    row_html = '\n        '.join([
                        f'<div class="aspect-square overflow-hidden rounded-2xl"><img src="{BASE}/FOTOS/{f}" alt="{escape(title[:30] or nome)}" loading="lazy" class="w-full h-full object-cover hover:scale-105 transition duration-500"></div>'
                        for f in row_imgs
                    ])
                    grid_rows.append(f'<div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">\n        {row_html}\n      </div>')
                grids_html = '\n      '.join(grid_rows)
                sections_html.append(f'''
  <section class="py-20 px-6" style="background-color: {primary};">
    <div class="max-w-6xl mx-auto">
      <h2 class="text-3xl md:text-5xl font-extrabold text-white text-center mb-4 tracking-wide">{escape(title)}</h2>
      {f'<p class="text-lg text-white/80 text-center max-w-3xl mx-auto mb-12 leading-relaxed">{escape(related_p)}</p>' if related_p else '<div class="mb-12"></div>'}
      {grids_html}
    </div>
  </section>''')
                continue

            # Alternate dark/light styling for small sections (2-6 photos)
            is_dark = (len([sh for sh in sections_html if f'background-color: {primary}' in sh or f'background-color: {dark}' in sh]) % 2) == 0
            bg_color = primary if is_dark else '#ffffff'
            para_color = 'text-white/90' if is_dark else 'text-slate-700'

            # Build image grid
            if len(all_photos) <= 2:
                img_class = 'grid-cols-2'
            elif len(all_photos) <= 4:
                img_class = 'grid-cols-2'
            else:
                img_class = 'grid-cols-2 md:grid-cols-3'

            imgs_html = '\n        '.join([
                f'<div class="rounded-2xl overflow-hidden shadow-xl"><img src="{BASE}/FOTOS/{f}" alt="{escape(title)}" loading="lazy" class="w-full h-52 object-cover"></div>'
                for f in all_photos
            ])

            if is_dark:
                sections_html.append(f'''
  <section class="py-20 px-6" style="background-color: {bg_color};">
    <div class="max-w-6xl mx-auto grid md:grid-cols-2 gap-12 items-center">
      <div class="text-white">
        <h2 class="text-3xl md:text-4xl font-extrabold mb-6 tracking-wide">{escape(title)}</h2>
        {f'<p class="text-lg {para_color} leading-relaxed">{escape(related_p)}</p>' if related_p else ''}
      </div>
      <div class="grid {img_class} gap-4">
        {imgs_html}
      </div>
    </div>
  </section>''')
            else:
                sections_html.append(f'''
  <section class="py-20 px-6 bg-white">
    <div class="max-w-6xl mx-auto grid md:grid-cols-2 gap-12 items-center">
      <div class="grid {img_class} gap-4">
        {imgs_html}
      </div>
      <div>
        <h2 class="text-3xl md:text-4xl font-extrabold mb-6 tracking-wide" style="color: {primary};">{escape(title)}</h2>
        {f'<p class="text-lg {para_color} leading-relaxed">{escape(related_p)}</p>' if related_p else ''}
      </div>
    </div>
  </section>''')

    # Full HTML
    body_sections_html = '\n'.join(sections_html)

    html = f'''<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{escape(nome)} — NTICS Projetos</title>
  <meta name="description" content="{escape(intro_p[:160] if intro_p else f"Projeto {nome} - NTICS Projetos via Lei Rouanet.")}">
  <script src="https://cdn.tailwindcss.com"></script>
  <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">
  <style>
    * {{ font-family: 'Poppins', system-ui, sans-serif; }}
    html {{ scroll-behavior: smooth; }}
    .hero-overlay {{
      background: linear-gradient(135deg, {primary}E6 0%, {dark}B3 100%);
    }}
  </style>
</head>
<body class="bg-white text-slate-800">

  <!-- HEADER / NAV -->
  <header class="sticky top-0 z-50 shadow-md" style="background-color: {primary};">
    <div class="max-w-7xl mx-auto px-6 py-3 flex items-center justify-between">
      <div class="flex items-center gap-3">
        <img src="{BASE}/LOGOS/{logo}" alt="Logo {escape(nome)}" class="h-10 bg-white rounded-lg p-1">
        <span class="text-white font-bold text-sm hidden md:inline">{escape(hero_title[:40])}</span>
      </div>
      <nav class="hidden md:flex gap-6 text-sm font-medium text-white">
        <a href="#home" class="hover:opacity-80 transition">Home</a>
        <a href="#sobre" class="hover:opacity-80 transition">Sobre</a>
        <a href="#cidades" class="hover:opacity-80 transition">Cidades</a>
        <a href="#democratizacao" class="hover:opacity-80 transition">Democratização</a>
        <a href="#galeria" class="hover:opacity-80 transition">Galeria</a>
      </nav>
    </div>
  </header>

  <!-- HERO -->
  <section id="home" class="relative h-[85vh] min-h-[550px] flex items-center justify-center overflow-hidden">
    {f'<img src="{BASE}/FOTOS/{hero_img_name}" alt="{escape(nome)}" class="absolute inset-0 w-full h-full object-cover">' if hero_img_name else ''}
    <div class="absolute inset-0 hero-overlay"></div>
    <div class="relative z-10 text-center text-white px-6 max-w-4xl">
      <img src="{BASE}/LOGOS/{logo}" alt="Logo" class="h-28 md:h-36 mx-auto mb-6 bg-white/95 rounded-2xl p-4 shadow-2xl">
      <h1 class="text-4xl md:text-6xl font-black mb-4 drop-shadow-2xl">{escape(hero_title)}</h1>
      <p class="text-xl md:text-2xl font-light">{escape(hero_subtitle)}</p>
    </div>
  </section>

  <!-- SOBRE O PROJETO -->
  <section id="sobre" class="py-20 px-6 bg-white">
    <div class="max-w-5xl mx-auto grid md:grid-cols-2 gap-12 items-center">
      <div>
        <img src="{BASE}/LOGOS/{logo}" alt="Logo {escape(nome)}" class="w-full max-w-sm mx-auto">
      </div>
      <div>
        <h2 class="text-3xl md:text-4xl font-extrabold mb-6 tracking-wide" style="color: {primary};">Sobre o Projeto</h2>
        {f'<p class="text-lg text-slate-700 leading-relaxed mb-4">{escape(intro_p)}</p>' if intro_p else ''}
      </div>
    </div>
  </section>

{body_sections_html}

  <!-- FOOTER + RÉGUA -->
  <footer class="py-12 px-6 bg-white" style="border-top: 4px solid {primary};">
    <div class="max-w-5xl mx-auto text-center">
      <p class="text-sm uppercase tracking-widest text-slate-500 mb-6 font-semibold">Patrocínio &amp; Realização</p>
      {f'<img src="{BASE}/REGUAS/{regua}" alt="Régua de patrocinadores" class="max-w-4xl w-full mx-auto mb-8">' if regua else ''}
      <p class="text-xs text-slate-400">
        Projeto realizado via Lei de Incentivo à Cultura (Lei Rouanet) — Ministério da Cultura — Governo Federal
      </p>
    </div>
  </footer>

</body>
</html>
'''
    return html


def main():
    all_maps = json.loads((ROOT / '.tmp/migration/all_section_maps.json').read_text(encoding='utf-8'))

    for project in all_maps:
        num = project['numero']
        # Find project folder
        folder = None
        for d in (ROOT / 'assets/projetos').iterdir():
            if d.name.startswith(f'{num}. '):
                folder = d
                break
        if not folder:
            print(f'{num}: NO FOLDER')
            continue

        # Load colors
        cores_file = folder / 'cores.json'
        colors = json.loads(cores_file.read_text(encoding='utf-8')) if cores_file.exists() else {}

        # Load scrape
        scrape = json.loads((folder / 'scrape.json').read_text(encoding='utf-8'))

        # Generate HTML
        html = generate_html(project, colors, scrape)

        # Save to project dir
        (folder / 'index.html').write_text(html, encoding='utf-8')

        # Copy to GitHub repo
        gh_dir = ROOT / '.tmp/ntics-project-sites' / project['slug']
        gh_dir.mkdir(parents=True, exist_ok=True)
        (gh_dir / 'index.html').write_text(html, encoding='utf-8')

        total_photos = sum(len(s['imgs']) + len(s['bgs']) for s in project['sections'])
        print(f"  {num:>3}: generated ({total_photos} photos, {len(project['youtube_ids'])} videos)")


if __name__ == '__main__':
    main()
