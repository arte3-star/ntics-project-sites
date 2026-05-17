"""Refinamentos v2:
- Remove logo duplicada no hero (era overlay duplicado)
- Substitui imagem manual do header por logo real (LOGOS/)
- Substitui imagem manual do hero por foto real (FOTOS/hero_bg.jpg)
- Adiciona imagem real no sobre (FOTOS/sobre.jpg)
- Menu superior com fundo semi-transparente pra nao ficar escondido
- Remove bordas pontilhadas da galeria (127)
- Substitui placeholder KV do Sobre por foto real (127)
- Filtra fotos com marcas de outros patrocinadores da galeria
"""
import json
import re
import shutil
from pathlib import Path
from PIL import Image

ROOT = Path(r"g:\O meu disco\AUTOMAÇÕES")
assignments = json.loads((ROOT/"output/rankings/assignments.json").read_text(encoding="utf-8"))

SITES = {
    "116": "116. CULTURA ROBÓTICA (ÁSTER)",
    "117": "117. TEATRO E OFICINA ROBÓTICA 4ED (WHIRLPOOL)",
    "119": "119. PEC EU FAÇO PARTE 2ªED (SYLVAMO)",
    "124": "124. EXPOSIÇÃO - GASTRONOMIA TAMBÉM É ARTE (COMPAGAS)",
    "125": "125. EXPOSIÇÃO - GASTRONOMIA TAMBÉM É ARTE 2ED (GRU)",
    "127G": "127. PIE EMPREENDEDORISMO É ARTE 2ED (GRU)",
    "127S": "127. PIE EMPREENDEDORISMO É ARTE 2ED (SOTREQ)",
}

# Brand keywords que NÃO devem aparecer em NENHUM dos 7 novos sites
BRAND_BLACKLIST = [
    "sada", "pague menos", "wilson sons", "statkraft",
    "whirlpool", "áster", "aster", "sylvamo", "compagás", "compagas",
    "nereu ramos", "semec", "tecnoarte", "circuiteira",
    "revolucionários verdes", "revolucionarios verdes",
    "engrenagens da imaginação", "engrenagens da imaginacao",
    "pague menos",
]

def is_branded(caption):
    c = caption.lower()
    return any(b in c for b in BRAND_BLACKLIST)

def filter_galeria(site_id, pool_categories, used_stems, n=6):
    """Re-seleciona galeria filtrando fotos com marcas de outros patrocinadores.
    pool_categories: list de chaves de sonnet/*.json para escolher.
    used_stems: stems ja usados em atividade/hero (evitar repetir na galeria)
    """
    candidates = []
    for cat in pool_categories:
        data = json.loads((ROOT/f"output/rankings/sonnet/{cat}.json").read_text(encoding="utf-8"))
        for entry in data:
            if entry.get("quality_issues") == "screenshot":
                continue
            if is_branded(entry["caption"]):
                continue
            if Path(entry["file"]).stem in used_stems:
                continue
            candidates.append((entry["galeria_score"], entry, cat))
    candidates.sort(key=lambda x: -x[0])
    selected = []
    selected_stems = set()
    for score, entry, cat in candidates:
        stem = Path(entry["file"]).stem
        if stem in selected_stems: continue
        selected.append((entry, cat))
        selected_stems.add(stem)
        if len(selected) == n: break
    return selected

SONNET_CAT_MAP = {
    "robotica":  "5. ROBÓTICA NAS ESCOLAS",
    "pec":       "2. PEC   PIE   PED/PEC",
    "pie":       "2. PEC   PIE   PED/PIE",
    "culinaria": "7. CULINÁRIA SUSTENTÁVEL",
    "oficina_foto": "OFICINA DE FOTOGRAFIA",
}

def copy_photo_from_sonnet(entry, cat_key, dst):
    """Copia foto original (melhor resolucao) do melhores-fotos/ para dst.jpg"""
    src_dir = ROOT / "SecondBrain/banco-fotos" / SONNET_CAT_MAP[cat_key]
    stem = Path(entry["file"]).stem
    # Busca arquivo com esse stem em src_dir
    for f in src_dir.rglob("*"):
        if f.suffix.lower() not in {".jpg",".jpeg",".png",".webp"}: continue
        if f.stem == stem:
            if f.suffix.lower() in {".jpg",".jpeg"}:
                shutil.copy(f, dst)
            else:
                Image.open(f).convert("RGB").save(dst, "JPEG", quality=92)
            return True
    return False

SITE_POOLS = {
    "116": ["robotica"],
    "117": ["robotica"],
    "119": ["pec"],
    "124": ["culinaria"],
    "125": ["culinaria"],
    "127G": ["pie"],
    "127S": ["pie"],
}

def pick_hero_bg(site_id, used_stems):
    """Seleciona melhor foto para background do hero (sem marca de outro patroc.)."""
    cats = SITE_POOLS[site_id]
    best = None
    for cat in cats:
        data = json.loads((ROOT/f"output/rankings/sonnet/{cat}.json").read_text(encoding="utf-8"))
        for e in data:
            if e.get("quality_issues") in ("screenshot","blurry"): continue
            if is_branded(e["caption"]): continue
            stem = Path(e["file"]).stem
            if stem in used_stems: continue
            score = e["hero_score"]
            if best is None or score > best[0]:
                best = (score, e, cat)
    return best

def pick_sobre(site_id, used_stems):
    """Seleciona foto pra secao Sobre (grupo/atividade, medio hero_score)."""
    cats = SITE_POOLS[site_id]
    best = None
    for cat in cats:
        data = json.loads((ROOT/f"output/rankings/sonnet/{cat}.json").read_text(encoding="utf-8"))
        for e in data:
            if e.get("quality_issues") == "screenshot": continue
            if is_branded(e["caption"]): continue
            stem = Path(e["file"]).stem
            if stem in used_stems: continue
            # Prefere scene grupo ou oficina
            if e.get("scene") not in ("grupo_posando","oficina_pratica","oficina_aula","plateia_publico","feira_cientifica","aula_show_chef"): continue
            score = e["hero_score"] + e["galeria_score"]
            if best is None or score > best[0]:
                best = (score, e, cat)
    return best

def refine_site(site_id, site_dir):
    html_path = site_dir / "site.html"
    html = html_path.read_text(encoding="utf-8", errors="replace")
    fotos_dir = site_dir / "FOTOS"
    fotos_dir.mkdir(exist_ok=True)

    # Stems ja usados em atividades (evitar repetir)
    used = set()
    for a in assignments[site_id]["assignments"]:
        if a["slot"].startswith("atividade_"):
            used.add(a["stem"])

    changes = []

    # 1. Pick hero_bg foto
    hero = pick_hero_bg(site_id, used)
    if hero:
        _, entry, cat = hero
        dst = fotos_dir / "hero_bg.jpg"
        if copy_photo_from_sonnet(entry, cat, dst):
            used.add(Path(entry["file"]).stem)
            changes.append(f"hero_bg={entry['caption'][:40]}")

    # 2. Pick sobre foto
    sobre = pick_sobre(site_id, used)
    if sobre:
        _, entry, cat = sobre
        dst = fotos_dir / "sobre.jpg"
        if copy_photo_from_sonnet(entry, cat, dst):
            used.add(Path(entry["file"]).stem)
            changes.append(f"sobre={entry['caption'][:40]}")

    # 3. Regenera galeria filtrada (sem marcas)
    galeria_fotos = filter_galeria(site_id, SITE_POOLS[site_id], used, n=6)
    for i, (entry, cat) in enumerate(galeria_fotos, 1):
        dst = fotos_dir / f"galeria_{i}.jpg"
        copy_photo_from_sonnet(entry, cat, dst)
        used.add(Path(entry["file"]).stem)
    if galeria_fotos:
        changes.append(f"galeria={len(galeria_fotos)}")

    is_type_b = "gal-item" in html

    if not is_type_b:
        # ═════ TYPE A (116/117/119/124/125) ═════
        # 3.1 Remove LOGO_OVERLAY (redundante com header)
        html = re.sub(
            r'<!-- LOGO_OVERLAY_MARKER -->.*?</div>\s*(?=<!-- Decorative|<!--)',
            '', html, flags=re.DOTALL, count=1
        )

        # 3.2 Substitui imagem do HEADER LOGO (Google Drive manual) por LOGOS/
        logo_file = None
        logos_dir = site_dir / "LOGOS"
        if logos_dir.exists():
            for f in logos_dir.glob("*.png"):
                if f.name != "desktop.ini":
                    logo_file = f.name; break
        if logo_file:
            # Header img
            html = re.sub(
                r'<img\s+alt="[^"]*"\s+class="h-12\s+w-auto\s+drop-shadow-lg"\s+src="https://lh3\.googleusercontent\.com[^"]*"\s*/>',
                f'<img alt="Logo do projeto" class="h-12 w-auto drop-shadow-lg" src="LOGOS/{logo_file}"/>',
                html
            )
            changes.append("header_logo")

        # 3.3 Substitui imagem do HERO (manual) por foto FOTOS/hero_bg.jpg
        if (fotos_dir / "hero_bg.jpg").exists():
            html = re.sub(
                r'<img\s+alt="[^"]*"\s+class="w-full h-full object-cover object-center"\s+src="https://lh3\.googleusercontent\.com[^"]*"\s*/>',
                '<img alt="Imagem do projeto" class="w-full h-full object-cover object-center" src="FOTOS/hero_bg.jpg"/>',
                html
            )
            changes.append("hero_bg")

        # 3.4 Menu: adiciona fundo quando scroll (script simples)
        # Muda o <header> pra ter class "site-header" e adiciona script + CSS
        if "site-header" not in html:
            html = html.replace(
                '<header class="absolute',
                '<header class="site-header absolute',
                1
            )
            # CSS + JS
            style_block = '''
<style>
.site-header { transition: background 0.3s ease, backdrop-filter 0.3s ease; }
.site-header.scrolled { background: rgba(15, 23, 42, 0.85) !important; backdrop-filter: blur(12px); }
</style>
<script>
  window.addEventListener('scroll', () => {
    const h = document.querySelector('.site-header');
    if (!h) return;
    if (window.scrollY > 40) h.classList.add('scrolled'); else h.classList.remove('scrolled');
  });
</script>
'''
            html = html.replace('</body>', style_block + '\n</body>', 1)
            changes.append("menu_bg")

        # 3.5 Transforma Sobre em 2-col grid com imagem
        # Localiza o H2 "Cultura Robótica"/title dentro de id="projeto" e embrulha com imagem
        # Target: <section id="projeto" class=...> ... <div class="max-w-5xl mx-auto text-center reveal"> ... </section>
        # Simplificacao: procura por h2 inside sobre section and wrap with grid
        if (fotos_dir / "sobre.jpg").exists() and "sobre-image-injected" not in html:
            # Padrao: <section id="projeto" class="py-20 lg:py-28 px-6 lg:px-10">\n<div class="max-w-5xl mx-auto text-center reveal">
            sobre_pattern = re.compile(
                r'(<section id="projeto"[^>]*>\s*<div class="max-w-5xl mx-auto)(\s+text-center)?(\s+reveal[^"]*)?(")',
                re.DOTALL
            )
            # Em vez de alterar estrutura complexa, apenas adicionamos uma imagem antes do texto
            # Injetamos um bloco de imagem depois da abertura da secao sobre
            sobre_image_html = '''
      <!-- sobre-image-injected -->
      <div class="max-w-5xl mx-auto mb-12 reveal">
        <div class="rounded-3xl overflow-hidden shadow-2xl aspect-[21/9]">
          <img src="FOTOS/sobre.jpg" alt="Imagem do projeto" class="w-full h-full object-cover" loading="lazy">
        </div>
      </div>
'''
            html = re.sub(
                r'(<section id="projeto"[^>]*>)',
                r'\1' + sobre_image_html,
                html, count=1
            )
            changes.append("sobre_image")

        # 3.6 Regeneration galeria HTML se existir secao galeria
        if "id=\"galeria\"" in html:
            # Rebuild galeria section inner HTML
            galeria_inner = ''.join([
                f'''
      <div class="{'md:col-span-2 md:row-span-2 aspect-[4/3] md:aspect-auto' if i==0 else ('md:col-span-2 aspect-[16/9]' if i==4 else 'aspect-[4/3]')} rounded-2xl overflow-hidden card-hover">
        <img src="FOTOS/galeria_{i+1}.jpg" alt="Galeria do projeto" class="w-full h-full object-cover" loading="lazy">
      </div>'''
                for i in range(len(galeria_fotos))
            ])
            html = re.sub(
                r'(<div class="grid grid-cols-2 md:grid-cols-3 gap-4 lg:gap-6">).*?(</div>\s*</div>\s*</section>)',
                r'\1' + galeria_inner + r'\n      \2',
                html, flags=re.DOTALL, count=1
            )
            changes.append("galeria_rebuilt")

    else:
        # ═════ TYPE B (127G/127S) ═════
        # 4.1 Remove dashed borders from .gal-item
        html = re.sub(
            r'border: 2px dashed var\(--gray-200\);',
            'border: none;',
            html
        )
        changes.append("dashed_removed")

        # 4.2 Substitui placeholder KV no Sobre por foto real
        if (fotos_dir / "sobre.jpg").exists():
            # pattern: <div class="img-placeholder"> ... </div>
            sobre_img_html = '<img src="FOTOS/sobre.jpg" alt="Imagem do projeto" style="width:100%; height:400px; object-fit:cover; border-radius: var(--radius-lg);" loading="lazy"/>'
            html = re.sub(
                r'<div class="img-placeholder">.*?</div>',
                sobre_img_html,
                html, flags=re.DOTALL, count=1
            )
            changes.append("sobre_kv_replaced")

        # 4.3 Regenera galeria (fotos filtradas)
        for i, (entry, _cat) in enumerate(galeria_fotos, 1):
            pass  # imgs ja copiadas acima como galeria_N.jpg
        # Substituir src dos gal-items
        gal_idx = [0]
        def replace_gal(m):
            gal_idx[0] += 1
            return f'<img src="FOTOS/galeria_{gal_idx[0]}.jpg" alt="Galeria" loading="lazy" style="width:100%; height:100%; object-fit:cover;"/>'
        # Replace existing atividade_N refs in gal-items with galeria_N
        html = re.sub(
            r'<img[^>]*src="FOTOS/atividade_\d+\.jpg"[^>]*/>',
            replace_gal,
            html
        )
        changes.append("galeria_rebuilt_127")

    html_path.write_text(html, encoding="utf-8")
    return changes

def main():
    for site_id, dir_name in SITES.items():
        if site_id == "124":
            print(f"[{site_id}] SKIP (sem logo/regua)")
            continue
        site_dir = ROOT / "assets/projetos" / dir_name
        changes = refine_site(site_id, site_dir)
        print(f"[{site_id}] {len(changes)} changes: {', '.join(changes)}")

if __name__ == "__main__":
    main()
