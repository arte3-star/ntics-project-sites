"""Adiciona logo, regua e galeria nos site.html.

Type A (116/117/119/124/125): Tailwind CDN template
  - Adiciona logo do projeto no hero (top overlay)
  - Adiciona secao galeria (6 fotos) antes dos patrocinadores
  - Substitui blocos de patrocinio/realizacao por imagem da regua
  - Substitui imagem do footer pela logo do projeto

Type B (127G/127S): CSS vars template (Lovable)
  - Corrige paths assets/logos/* -> LOGOS/*
  - Corrige paths assets/reguas/* -> REGUAS/*
  - Galeria ja tem fotos injetadas
"""
import json
import re
import shutil
from pathlib import Path

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

def find_asset(site_dir, subdir, patterns):
    """Busca primeira ocorrencia de arquivo em LOGOS ou REGUAS."""
    d = site_dir / subdir
    if not d.exists(): return None
    for pat in patterns:
        for f in d.glob(pat):
            if f.name != "desktop.ini":
                return f.name
    return None

def build_galeria_html(site_id):
    """HTML da secao galeria com 6 fotos."""
    assigns = [a for a in assignments[site_id]["assignments"] if a["slot"].startswith("galeria_")]
    assigns.sort(key=lambda x: int(x["slot"].split("_")[1]))
    if not assigns: return ""
    cards = []
    # Layout: 1 grande (col-span-2) + 2 + 3 (grid de 3 cols, masonry-like via aspect ratios)
    layouts = [
        ("md:col-span-2 md:row-span-2 aspect-[4/3] md:aspect-auto", ""),
        ("aspect-[4/3]", ""),
        ("aspect-[4/3]", ""),
        ("aspect-[4/3]", ""),
        ("md:col-span-2 aspect-[16/9]", ""),
        ("aspect-[4/3]", ""),
    ]
    for i, a in enumerate(assigns[:6]):
        span, _ = layouts[i] if i < len(layouts) else ("aspect-[4/3]", "")
        cards.append(f'''
      <div class="{span} rounded-2xl overflow-hidden card-hover">
        <img src="FOTOS/{a['slot']}.jpg" alt="{a['caption']}" class="w-full h-full object-cover" loading="lazy">
      </div>''')
    return f'''
  <!-- ═══════════════ GALERIA ═══════════════ -->
  <section id="galeria" class="py-20 lg:py-28 px-6 lg:px-10 bg-slate-50">
    <div class="max-w-6xl mx-auto">
      <div class="text-center mb-16 reveal">
        <div class="inline-flex items-center gap-2 px-4 py-2 rounded-full text-xs font-bold uppercase tracking-[0.2em] mb-6 bg-slate-100 text-slate-600">
          <span class="w-2 h-2 rounded-full bg-slate-400"></span>
          Registros
        </div>
        <h2 class="font-display text-3xl sm:text-4xl lg:text-5xl text-slate-800" style="letter-spacing: -0.03em;">
          Galeria do Projeto
        </h2>
      </div>
      <div class="grid grid-cols-2 md:grid-cols-3 gap-4 lg:gap-6">{"".join(cards)}
      </div>
    </div>
  </section>
'''

def adjust_type_a(site_id, site_dir):
    html_path = site_dir / "site.html"
    html = html_path.read_text(encoding="utf-8", errors="replace")
    logo = find_asset(site_dir, "LOGOS", ["*.png", "*.svg"])
    regua = find_asset(site_dir, "REGUAS", ["*.png", "*.jpg"])
    changes = []

    # 1. Inserir logo no hero (top-left overlay) — se logo existir
    if logo:
        # Proteger contra dupla insercao
        if "LOGO_OVERLAY_MARKER" not in html:
            logo_html = f'''
    <!-- LOGO_OVERLAY_MARKER -->
    <div class="absolute top-6 left-6 lg:top-10 lg:left-10 z-20">
      <img src="LOGOS/{logo}" alt="Logo do projeto" class="h-16 md:h-20 lg:h-24 drop-shadow-lg">
    </div>
'''
            # Inserir logo apos a abertura da secao hero (primeira <section> com min-h-[100vh])
            html = re.sub(
                r'(<section[^>]*min-h-\[100vh\][^>]*>)',
                r'\1' + logo_html,
                html, count=1
            )
            changes.append("logo_hero")

    # 2. Substituir bloco patrocinio+realizacao por regua
    if regua:
        regua_html = f'''
<!-- ═══════════════ RÉGUA DE PATROCINADORES ═══════════════ -->
<section class="py-16 lg:py-20 px-6 lg:px-10 bg-white">
  <div class="max-w-6xl mx-auto reveal">
    <img src="REGUAS/{regua}" alt="Régua de patrocinadores" class="w-full h-auto">
  </div>
</section>'''
        # O bloco inteiro da secao de patrocinio/realizacao começa com o comentario PATROCINADORES
        pattern = r'<!-- ═══════════════ PATROCINADORES ═══════════════ -->.*?</section>'
        if re.search(pattern, html, flags=re.DOTALL):
            html = re.sub(pattern, regua_html.strip(), html, flags=re.DOTALL, count=1)
            changes.append("regua_footer")

    # 3. Substituir imagem do footer (lh3.googleusercontent / data-manual) por logo local
    if logo:
        # Pattern: <img ... class="h-14 mx-auto..." src="https://lh3.google..."/>
        footer_img_pattern = r'<img\s+alt="[^"]*"\s+class="h-\d+\s+mx-auto[^"]*"\s+src="https://lh3\.googleusercontent\.com[^"]*"\s*/>'
        new_footer = f'<img alt="Logo do projeto" class="h-14 mx-auto mb-6" src="LOGOS/{logo}"/>'
        if re.search(footer_img_pattern, html):
            html = re.sub(footer_img_pattern, new_footer, html, count=1)
            changes.append("logo_footer")

    # 4. Adicionar galeria antes do PATROCINADORES ou do footer (usa marker de insercao)
    if "galeria_1.jpg" not in html and "id=\"galeria\"" not in html:
        galeria_html = build_galeria_html(site_id)
        if galeria_html:
            # Inserir antes da secao de regua/patrocinadores
            target = "<!-- ═══════════════ RÉGUA DE PATROCINADORES ═══════════════ -->"
            if target not in html:
                target = "<!-- ═══════════════ FOOTER ═══════════════ -->"
            html = html.replace(target, galeria_html + "\n  " + target, 1)
            changes.append("galeria")

    html_path.write_text(html, encoding="utf-8")
    return changes, {"logo": logo, "regua": regua}

def adjust_type_b(site_id, site_dir):
    html_path = site_dir / "site.html"
    html = html_path.read_text(encoding="utf-8", errors="replace")
    logo = find_asset(site_dir, "LOGOS", ["*.png", "*.svg"])
    regua = find_asset(site_dir, "REGUAS", ["*.png", "*.jpg"])
    changes = []

    # Fix paths: assets/logos/XXX -> LOGOS/XXX (and reguas)
    if logo:
        html = re.sub(r'src="assets/logos/[^"]+\.png"', f'src="LOGOS/{logo}"', html)
        html = re.sub(r'src="assets/logos/[^"]+\.svg"', f'src="LOGOS/{logo}"', html)
        changes.append("logo_paths")
    if regua:
        html = re.sub(r'src="assets/reguas/[^"]+"', f'src="REGUAS/{regua}"', html)
        changes.append("regua_path")
    # KV paths — no KV local, remove the placeholder or leave as-is
    # For now just strip assets/imagens paths (they'd 404) — replace with nothing
    html = re.sub(r'<span class="ph-path">assets/imagens/[^<]+</span>', '', html)

    html_path.write_text(html, encoding="utf-8")
    return changes, {"logo": logo, "regua": regua}

def main():
    for site_id, dir_name in SITES.items():
        site_dir = ROOT / "assets/projetos" / dir_name
        if site_id in ("127G", "127S"):
            changes, assets = adjust_type_b(site_id, site_dir)
        else:
            changes, assets = adjust_type_a(site_id, site_dir)
        missing = []
        if not assets["logo"]: missing.append("LOGO")
        if not assets["regua"]: missing.append("RÉGUA")
        mflag = f"  ⚠️ FALTANDO: {', '.join(missing)}" if missing else ""
        print(f"[{site_id}] {', '.join(changes) or 'no-changes'}  logo={assets['logo']}  regua={assets['regua']}{mflag}")

if __name__ == "__main__":
    main()
