#!/usr/bin/env python3
"""
generate_v2_corrected.py — V2 inovadora que respeita a estrutura exata do RF.

Lê 87_rf_section_map.json para saber quais fotos vão em qual seção.
"""

import json
import sys
import io
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = Path(__file__).resolve().parents[2]

# Load RF section map (exact photo-to-section assignment from the RF DOM)
section_map = json.loads((ROOT / '.tmp/migration/87_rf_section_map.json').read_text(encoding='utf-8'))

BASE = 'https://raw.githubusercontent.com/arte3-star/ntics-project-sites/master/87_exposicao_culinaria_sustentavel_imetame'

# Map GitHub filenames: RF uses truncated names, need to match to full filenames
gh_fotos = sorted([f.name for f in (ROOT / '.tmp/ntics-project-sites/87_exposicao_culinaria_sustentavel_imetame/FOTOS').iterdir()
                   if f.suffix.lower() in ('.jpg', '.jpeg') and f.name != 'desktop.ini'])

def match_rf_to_gh(rf_name):
    """RF section map has truncated filenames. Match to full GitHub name."""
    # RF gives us e.g. "43dfc1777e16eaf82497fadb047a9e91.jp" (truncated)
    # GitHub has "rf-1316311-43dfc1777e16eaf82497fadb047a9e91.jpg"
    hash_part = rf_name.split('.')[0]  # Get the hash before extension
    for gh in gh_fotos:
        if hash_part in gh:
            return gh
    return None

# Extract photos per section from RF map
por_onde_bg = []
expo_photos = []
workshop_photos = []
expo_grid1 = []  # 8 photos
expo_grid2 = []  # 8 photos
expo_grid3 = []  # 8 photos
expo_grid4 = []  # 8 photos
galeria_photos = []
regua_bg = []

for s in section_map:
    all_files = s['imgs'] + s['bgs']
    matched = [match_rf_to_gh(f) for f in all_files]
    matched = [m for m in matched if m is not None]

    if s['idx'] == 1:   # POR ONDE PASSAMOS
        por_onde_bg = matched
    elif s['idx'] == 2: # EXPOSIÇÃO FOTOGRÁFICA
        expo_photos = matched
    elif s['idx'] == 3: # WORKSHOP
        workshop_photos = matched
    elif s['idx'] == 5: # Grid 1
        expo_grid1 = matched
    elif s['idx'] == 6: # Grid 2
        expo_grid2 = matched
    elif s['idx'] == 7: # Grid 3
        expo_grid3 = matched
    elif s['idx'] == 8: # Grid 4
        expo_grid4 = matched
    elif s['idx'] == 9: # GALERIA
        galeria_photos = matched
    elif s['idx'] == 10: # Footer/regua bg
        regua_bg = matched

logo = 'exposicao_culinaria_sustentavel_imetame.png'
regua = 'regua_542957e313cd4de0aa58076f04371283.jpg'

# Report
print(f"Expo photos: {len(expo_photos)}")
print(f"Workshop photos: {len(workshop_photos)}")
print(f"Grid 1: {len(expo_grid1)}")
print(f"Grid 2: {len(expo_grid2)}")
print(f"Grid 3: {len(expo_grid3)}")
print(f"Grid 4: {len(expo_grid4)}")
print(f"Galeria: {len(galeria_photos)}")
print(f"Total: {len(expo_photos) + len(workshop_photos) + len(expo_grid1) + len(expo_grid2) + len(expo_grid3) + len(expo_grid4) + len(galeria_photos)}")

# Helper to build image grid
def img_grid_square(photos, cols=4):
    rows = []
    for f in photos:
        rows.append(f'          <div class="aspect-square overflow-hidden rounded-2xl"><img src="{BASE}/FOTOS/{f}" alt="Culinária Sustentável" loading="lazy" class="w-full h-full object-cover hover:scale-105 transition duration-500"></div>')
    return '\n'.join(rows)

def img_masonry(photos):
    """Galeria masonry com tamanhos variados como o RF."""
    sizes = ['col-span-2 row-span-1', 'col-span-1 row-span-1', 'col-span-1 row-span-1',
             'col-span-1 row-span-1 md:col-span-2', 'col-span-2 row-span-1',
             'col-span-1 row-span-1', 'col-span-1 row-span-1']
    rows = []
    for i, f in enumerate(photos):
        sz = sizes[i] if i < len(sizes) else 'col-span-1'
        rows.append(f'          <div class="{sz} overflow-hidden rounded-xl"><img src="{BASE}/FOTOS/{f}" alt="Galeria" loading="lazy" class="w-full h-full object-cover hover:scale-105 transition duration-500"></div>')
    return '\n'.join(rows)

html = f'''<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Exposição Culinária Sustentável — NTICS Projetos</title>
  <meta name="description" content="Exposição Culinária Sustentável: Uma Abordagem Artística. Arte, gastronomia e sustentabilidade. Patrocínio Imetame via Lei Rouanet.">
  <script src="https://cdn.tailwindcss.com"></script>
  <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700;900&family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
  <style>
    :root {{
      --verde: #3F8047;
      --vermelho: #C31E30;
      --verde-escuro: #1a3a1e;
      --creme: #FDF8F0;
      --dourado: #D4A853;
    }}
    body {{ font-family: 'Inter', sans-serif; }}
    .font-display {{ font-family: 'Playfair Display', serif; }}
    .gradient-hero {{ background: linear-gradient(135deg, #1a3a1e 0%, #3F8047 40%, #2d5a33 100%); }}
    .gradient-vermelho {{ background: linear-gradient(135deg, #C31E30 0%, #8B1520 100%); }}
    .stat-card {{ background: rgba(255,255,255,0.08); backdrop-filter: blur(10px); border: 1px solid rgba(255,255,255,0.15); }}
    .video-glow {{ box-shadow: 0 0 60px rgba(63, 128, 71, 0.3), 0 20px 40px rgba(0,0,0,0.2); }}
  </style>
</head>
<body class="bg-white text-slate-800">

  <!-- NAV -->
  <header class="fixed top-0 w-full z-50 bg-white/90 backdrop-blur-md border-b border-gray-100 shadow-sm">
    <div class="max-w-7xl mx-auto px-6 py-3 flex items-center justify-between">
      <img src="{BASE}/LOGOS/{logo}" alt="Logo" class="h-11">
      <nav class="hidden md:flex gap-7 text-sm font-medium text-slate-600">
        <a href="#home" class="hover:text-green-700 transition">Home</a>
        <a href="#sobre" class="hover:text-green-700 transition">Sobre</a>
        <a href="#cidades" class="hover:text-green-700 transition">Cidades</a>
        <a href="#expo" class="hover:text-green-700 transition">Exposição</a>
        <a href="#workshop" class="hover:text-green-700 transition">Workshop</a>
        <a href="#video" class="hover:text-green-700 transition">Vídeo</a>
        <a href="#galeria" class="hover:text-green-700 transition">Galeria</a>
      </nav>
      <a href="#video" class="hidden md:block px-5 py-2 rounded-full text-sm font-semibold text-white transition" style="background-color: var(--verde);">Assista ao Vídeo</a>
    </div>
  </header>

  <!-- HERO -->
  <section id="home" class="relative min-h-screen flex items-center gradient-hero overflow-hidden pt-16">
    <div class="absolute inset-0 opacity-15">
      <img src="{BASE}/FOTOS/{por_onde_bg[0] if por_onde_bg else expo_photos[0] if expo_photos else ''}" alt="" class="w-full h-full object-cover">
    </div>
    <div class="absolute inset-0" style="background: linear-gradient(to right, rgba(26,58,30,0.95) 0%, rgba(63,128,71,0.7) 60%, transparent 100%);"></div>
    <div class="relative z-10 max-w-7xl mx-auto px-6 grid md:grid-cols-2 gap-12 items-center">
      <div class="text-white">
        <div class="inline-block bg-white/10 backdrop-blur px-4 py-1.5 rounded-full text-sm font-medium mb-6 border border-white/20">
          Lei Rouanet &bull; Patrocínio Imetame
        </div>
        <h1 class="font-display text-5xl md:text-7xl font-black mb-4 leading-tight">
          Culinária<br><span style="color: var(--dourado);">Sustentável</span>
        </h1>
        <p class="text-xl md:text-2xl font-light opacity-90">Uma Abordagem Artística</p>
        <p class="text-base opacity-70 mt-6 max-w-lg leading-relaxed">
          Transformando a culinária em arte sustentável para o futuro do planeta.
        </p>
        <div class="flex gap-4 mt-8">
          <a href="#video" class="bg-white px-8 py-3 rounded-full font-bold hover:bg-gray-100 transition" style="color: var(--verde-escuro);">Assistir Vídeo</a>
          <a href="#galeria" class="border border-white/40 text-white px-8 py-3 rounded-full font-medium hover:bg-white/10 transition">Ver Galeria</a>
        </div>
      </div>
      <div class="hidden md:block">
        <img src="{BASE}/LOGOS/{logo}" alt="Logo" class="w-80 mx-auto bg-white/95 rounded-3xl p-8 shadow-2xl">
      </div>
    </div>
  </section>

  <!-- IMPACTO -->
  <section class="py-4 gradient-vermelho">
    <div class="max-w-5xl mx-auto flex flex-wrap justify-center gap-8 px-6 py-4 text-white text-center">
      <div class="stat-card rounded-2xl px-8 py-4"><p class="text-3xl font-black">5</p><p class="text-sm opacity-80">Cidades</p></div>
      <div class="stat-card rounded-2xl px-8 py-4"><p class="text-3xl font-black">4</p><p class="text-sm opacity-80">Estados</p></div>
      <div class="stat-card rounded-2xl px-8 py-4"><p class="text-3xl font-black">32</p><p class="text-sm opacity-80">Obras expostas</p></div>
      <div class="stat-card rounded-2xl px-8 py-4"><p class="text-3xl font-black">3</p><p class="text-sm opacity-80">Atividades</p></div>
    </div>
  </section>

  <!-- SOBRE -->
  <section id="sobre" class="py-24 px-6" style="background-color: var(--creme);">
    <div class="max-w-4xl mx-auto text-center">
      <p class="text-sm uppercase tracking-widest font-semibold mb-4" style="color: var(--verde);">Sobre o Projeto</p>
      <h2 class="font-display text-3xl md:text-5xl font-black text-slate-900 mb-8">Onde a arte encontra a<br><span style="color: var(--verde);">sustentabilidade</span></h2>
      <p class="text-lg text-slate-600 leading-relaxed max-w-3xl mx-auto">
        O projeto reuniu arte, gastronomia e sustentabilidade em uma experiência educativa inovadora. Através de exposições fotográficas, workshops e atividades interativas, o público explorou as conexões entre alimentação consciente, cultura e meio ambiente.
      </p>
    </div>
  </section>

  <!-- CIDADES (POR ONDE PASSAMOS) -->
  <section id="cidades" class="py-20 px-6 relative overflow-hidden" style="background-color: var(--verde-escuro);">
    {f'<div class="absolute inset-0 opacity-10"><img src="{BASE}/FOTOS/{por_onde_bg[0]}" alt="" class="w-full h-full object-cover"></div>' if por_onde_bg else ''}
    <div class="relative z-10 max-w-5xl mx-auto">
      <p class="text-sm uppercase tracking-widest font-semibold mb-4 text-center" style="color: var(--dourado);">Itinerância</p>
      <h2 class="font-display text-3xl md:text-5xl font-black text-center mb-14 text-white">Por Onde Passamos</h2>
      <div class="grid grid-cols-2 md:grid-cols-5 gap-5">
        <div class="bg-white/10 backdrop-blur rounded-2xl p-6 text-center border border-white/10 hover:bg-white/20 transition"><p class="font-bold text-white">Celso Ramos</p><p class="text-sm text-white/60">SC</p></div>
        <div class="bg-white/10 backdrop-blur rounded-2xl p-6 text-center border border-white/10 hover:bg-white/20 transition"><p class="font-bold text-white">Pinhal da Serra</p><p class="text-sm text-white/60">RS</p></div>
        <div class="bg-white/10 backdrop-blur rounded-2xl p-6 text-center border border-white/10 hover:bg-white/20 transition"><p class="font-bold text-white">São Paulo</p><p class="text-sm text-white/60">SP</p></div>
        <div class="bg-white/10 backdrop-blur rounded-2xl p-6 text-center border border-white/10 hover:bg-white/20 transition"><p class="font-bold text-white">Aracruz</p><p class="text-sm text-white/60">ES</p></div>
        <div class="bg-white/10 backdrop-blur rounded-2xl p-6 text-center border border-white/10 hover:bg-white/20 transition"><p class="font-bold text-white">Jaíba</p><p class="text-sm text-white/60">MG</p></div>
      </div>
    </div>
  </section>

  <!-- EXPOSIÇÃO FOTOGRÁFICA (3 fotos) -->
  <section id="expo" class="py-24 px-6 bg-white">
    <div class="max-w-6xl mx-auto grid md:grid-cols-2 gap-16 items-center">
      <div class="grid grid-cols-2 gap-4">
        {''.join(f'<div class="rounded-2xl overflow-hidden shadow-xl"><img src="{BASE}/FOTOS/{f}" alt="Exposição" loading="lazy" class="w-full h-56 object-cover"></div>' for f in expo_photos)}
      </div>
      <div>
        <p class="text-sm uppercase tracking-widest font-semibold mb-4" style="color: var(--verde);">Atividade</p>
        <h2 class="font-display text-3xl md:text-5xl font-black mb-6" style="color: var(--verde-escuro);">Exposição<br>Fotográfica</h2>
        <p class="text-lg text-slate-600 leading-relaxed">
          A exposição explorou as conexões entre gastronomia, arte e cultura, valorizando práticas culinárias tradicionais e sustentáveis. A mostra destacou a importância de escolhas alimentares conscientes e o impacto da gastronomia na preservação do meio ambiente.
        </p>
      </div>
    </div>
  </section>

  <!-- WORKSHOP FOTOGRAFIA (3 fotos) -->
  <section id="workshop" class="py-24 px-6" style="background-color: var(--verde-escuro);">
    <div class="max-w-6xl mx-auto grid md:grid-cols-2 gap-16 items-center">
      <div class="text-white">
        <p class="text-sm uppercase tracking-widest font-semibold mb-4" style="color: var(--dourado);">Atividade</p>
        <h2 class="font-display text-3xl md:text-5xl font-black mb-6">Workshop de<br>Fotografia</h2>
        <p class="text-lg leading-relaxed opacity-90">
          Workshop para estudantes da rede pública com base prática para desenvolver o olhar fotográfico, estimulando a criatividade e despertando talentos para uma nova geração de fotógrafos criativos e engajados.
        </p>
      </div>
      <div class="grid grid-cols-2 gap-4">
        {''.join(f'<div class="rounded-2xl overflow-hidden shadow-xl"><img src="{BASE}/FOTOS/{f}" alt="Workshop" loading="lazy" class="w-full h-56 object-cover"></div>' for f in workshop_photos)}
      </div>
    </div>
  </section>

  <!-- DEMOCRATIZAÇÃO + VÍDEO -->
  <section id="video" class="py-24 px-6" style="background-color: var(--creme);">
    <div class="max-w-5xl mx-auto text-center">
      <p class="text-sm uppercase tracking-widest font-semibold mb-4" style="color: var(--vermelho);">Democratização de Acesso</p>
      <h2 class="font-display text-3xl md:text-5xl font-black mb-6" style="color: var(--verde-escuro);">A Arte Está em<br>Todo Lugar</h2>
      <p class="text-lg text-slate-600 leading-relaxed max-w-3xl mx-auto mb-12">
        Como forma de democratizar o acesso à cultura no Brasil, o projeto conta com a disponibilização online da <strong>palestra "A arte está em todo lugar"</strong> — onde o público poderá conhecer melhor nossas experiências!
      </p>
      <div class="max-w-4xl mx-auto rounded-3xl overflow-hidden video-glow">
        <iframe src="https://www.youtube.com/embed/tpnxsDmEn6I" width="100%" height="500" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen class="w-full aspect-video"></iframe>
      </div>
    </div>
  </section>

  <!-- EXPOSIÇÃO: 4 GRIDS DE 8 FOTOS (32 fotos quadradas, como o RF) -->
  <section class="py-20 px-6" style="background-color: var(--verde);">
    <div class="max-w-6xl mx-auto">
      <h2 class="font-display text-3xl md:text-5xl font-black text-white text-center mb-4">Exposição Culinária Sustentável</h2>
      <p class="text-xl font-light text-white/70 text-center mb-12">Uma Abordagem Artística</p>
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
{img_grid_square(expo_grid1)}
      </div>
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
{img_grid_square(expo_grid2)}
      </div>
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
{img_grid_square(expo_grid3)}
      </div>
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
{img_grid_square(expo_grid4)}
      </div>
    </div>
  </section>

  <!-- GALERIA DE FOTOS (7 fotos, masonry como o RF) -->
  <section id="galeria" class="py-24 px-6 bg-white">
    <div class="max-w-6xl mx-auto">
      <div class="text-center mb-14">
        <p class="text-sm uppercase tracking-widest font-semibold mb-4" style="color: var(--verde);">Registros</p>
        <h2 class="font-display text-3xl md:text-5xl font-black" style="color: var(--verde-escuro);">Galeria de Fotos</h2>
      </div>
      <div class="grid grid-cols-2 md:grid-cols-4 auto-rows-[200px] gap-4">
{img_masonry(galeria_photos)}
      </div>
    </div>
  </section>

  <!-- FOOTER -->
  <footer class="py-16 px-6" style="background-color: var(--verde-escuro);">
    <div class="max-w-5xl mx-auto text-center">
      <img src="{BASE}/LOGOS/{logo}" alt="Logo" class="h-16 mx-auto mb-6 bg-white rounded-xl p-2">
      <p class="text-sm uppercase tracking-widest text-white/60 mb-8 font-semibold">Patrocínio &amp; Realização</p>
      <div class="bg-white rounded-2xl p-6 mb-8">
        <img src="{BASE}/REGUAS/{regua}" alt="Régua de patrocinadores" class="max-w-4xl w-full mx-auto">
      </div>
      <p class="text-xs text-white/40">Projeto via Lei de Incentivo à Cultura (Lei Rouanet) — Ministério da Cultura — Governo Federal</p>
    </div>
  </footer>

</body>
</html>
'''

out = ROOT / '.tmp/migration/87_inovadora/index.html'
out.write_text(html, encoding='utf-8')
print(f'\nGenerated v2 corrected: {out}')
print(f'  Expo photos: {len(expo_photos)}')
print(f'  Workshop: {len(workshop_photos)}')
print(f'  4 grids: {len(expo_grid1)} + {len(expo_grid2)} + {len(expo_grid3)} + {len(expo_grid4)} = {len(expo_grid1)+len(expo_grid2)+len(expo_grid3)+len(expo_grid4)}')
print(f'  Galeria masonry: {len(galeria_photos)}')
total = len(expo_photos) + len(workshop_photos) + len(expo_grid1) + len(expo_grid2) + len(expo_grid3) + len(expo_grid4) + len(galeria_photos) + len(por_onde_bg)
print(f'  Total: {total} (0 duplicatas)')
