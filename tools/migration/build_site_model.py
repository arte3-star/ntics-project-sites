"""Monta site modelo (baseado em padrao RF-origin 81) para o projeto 116 como piloto.
HISTORICAL: script já executado. Assets agora em SecondBrain/projetos/116-aster/assets/

Estrutura:
  1. Header sticky colored (logo + nav)
  2. Hero 80vh com foto real + overlay + logo grande centralizado
  3. Sobre (grid 2col: logo | texto)
  4. Atividades (uma secao por atividade, foto + texto)
  5. Galeria masonry
  6. Democratizacao
  7. Regua grande
  8. Footer
"""
import json
from pathlib import Path

ROOT = Path(r"g:\O meu disco\AUTOMAÇÕES")

def build_116():
    content = json.loads((ROOT/"output/_116_content.json").read_text(encoding="utf-8"))
    assigns = json.loads((ROOT/"output/rankings/assignments.json").read_text(encoding="utf-8"))["116"]

    title = content["title"]                 # "Cultura Robótica"
    subtitle = content["hero_subtitle"]      # "Tecnologia, Sustentabilidade e Educação nas Escolas"
    atividades = content["atividades"]       # [(h3, desc), ...]
    sobre_paragraphs = content["sobre_paragraphs"]
    logo_file = "116_cultura_robotica.png"
    regua_file = "Régua - 116.png"

    # Paleta 116 (azul)
    color_main = "#2196F3"
    color_dark = "#1565C0"
    color_accent = "#E91E63"

    # Atividades ordenadas por slot
    act_slots = [a for a in assigns["assignments"] if a["slot"].startswith("atividade_")]
    act_slots.sort(key=lambda x: int(x["slot"].split("_")[1]))
    # Galeria
    gal_slots = [a for a in assigns["assignments"] if a["slot"].startswith("galeria_")]
    gal_slots.sort(key=lambda x: int(x["slot"].split("_")[1]))

    atividades_html = []
    for i, (h3, desc) in enumerate(atividades, 1):
        photo_slot = f"atividade_{i}"
        photo_exists = (ROOT / "assets/projetos/116. CULTURA ROBÓTICA (ÁSTER)/FOTOS" / f"{photo_slot}.jpg").exists()
        photo_src = f"FOTOS/{photo_slot}.jpg" if photo_exists else ""
        side = "reveal-left" if i % 2 == 1 else "reveal-right"
        order_img = "lg:order-1" if i % 2 == 1 else "lg:order-2"
        order_text = "lg:order-2" if i % 2 == 1 else "lg:order-1"
        img_or_ph = (f'<img src="{photo_src}" alt="{h3}" loading="lazy" class="w-full h-full object-cover">'
                     if photo_src else
                     f'<div class="w-full h-full flex items-center justify-center text-white/70 text-sm">{h3}</div>')
        atividades_html.append(f'''
      <div class="grid lg:grid-cols-2 gap-10 lg:gap-16 items-center {side}">
        <div class="{order_text}">
          <div class="flex items-center gap-4 mb-6">
            <div class="w-14 h-14 rounded-2xl flex items-center justify-center font-display text-2xl text-white" style="background: {color_main}; box-shadow: 0 8px 24px {color_main}40;">
              {i:02d}
            </div>
            <div class="h-px flex-1" style="background: linear-gradient(90deg, {color_main}30, transparent);"></div>
          </div>
          <h3 class="font-display text-2xl sm:text-3xl lg:text-4xl mb-5" style="color: {color_main}; letter-spacing: -0.02em; line-height: 1.15;">
            {h3}
          </h3>
          <p class="text-base lg:text-lg text-slate-600" style="line-height: 1.8;">{desc}</p>
        </div>
        <div class="{order_img}">
          <div class="rounded-3xl aspect-[16/10] overflow-hidden shadow-xl" style="background: {color_main}15;">
            {img_or_ph}
          </div>
        </div>
      </div>''')

    # Galeria (masonry-style CSS grid)
    gal_layouts = ["md:col-span-2 md:row-span-2", "", "", "", "md:col-span-2", ""]
    gal_items = []
    for i, a in enumerate(gal_slots[:6]):
        cls = gal_layouts[i] if i < len(gal_layouts) else ""
        gal_items.append(f'''
        <div class="{cls} aspect-[4/3] md:aspect-auto rounded-2xl overflow-hidden shadow-md hover:shadow-2xl transition">
          <img src="FOTOS/galeria_{i+1}.jpg" alt="" loading="lazy" class="w-full h-full object-cover hover:scale-105 transition duration-700">
        </div>''')

    sobre_text = "".join([f'<p class="text-base lg:text-lg text-slate-700 leading-relaxed mb-6">{p}</p>' for p in sobre_paragraphs])

    html = f"""<!DOCTYPE html>
<html lang="pt-BR" class="scroll-smooth">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title} | Tecnologia e Educação nas Escolas Públicas</title>
  <meta name="description" content="{title}: tecnologia, sustentabilidade e educação nas escolas públicas por meio de teatro interativo e oficinas maker de robótica com materiais recicláveis.">
  <script src="https://cdn.tailwindcss.com"></script>
  <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;800;900&family=Space+Grotesk:wght@500;600;700&display=swap" rel="stylesheet">
  <style>
    :root {{
      --main: {color_main};
      --dark: {color_dark};
      --accent: {color_accent};
    }}
    body {{ font-family: 'Poppins', system-ui, sans-serif; }}
    .font-display {{ font-family: 'Space Grotesk', sans-serif; }}
    .bg-main {{ background-color: var(--main); }}
    .bg-dark {{ background-color: var(--dark); }}
    .text-main {{ color: var(--main); }}
    .hero-overlay {{
      background: linear-gradient(135deg, rgba(21,101,192,0.75) 0%, rgba(33,150,243,0.55) 50%, rgba(21,101,192,0.85) 100%);
    }}
    .reveal {{ opacity: 0; transform: translateY(30px); transition: all 0.8s cubic-bezier(0.22, 1, 0.36, 1); }}
    .reveal.visible {{ opacity: 1; transform: translateY(0); }}
    .reveal-left {{ opacity: 0; transform: translateX(-40px); transition: all 0.8s cubic-bezier(0.22, 1, 0.36, 1); }}
    .reveal-left.visible {{ opacity: 1; transform: translateX(0); }}
    .reveal-right {{ opacity: 0; transform: translateX(40px); transition: all 0.8s cubic-bezier(0.22, 1, 0.36, 1); }}
    .reveal-right.visible {{ opacity: 1; transform: translateX(0); }}
    .site-header {{ transition: padding 0.3s ease, box-shadow 0.3s ease; }}
    .site-header.scrolled {{ padding-top: 0.5rem; padding-bottom: 0.5rem; box-shadow: 0 6px 24px rgba(0,0,0,0.12); }}
  </style>
</head>
<body class="bg-white text-slate-800">

  <!-- Scroll progress -->
  <div id="scroll-progress" style="position: fixed; top: 0; left: 0; height: 3px; background: var(--accent); z-index: 100; width: 0%; transition: width 0.1s linear;"></div>

  <!-- ═══════════════ HEADER ═══════════════ -->
  <header class="site-header bg-main text-white sticky top-0 z-50 shadow-lg">
    <div class="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
      <a href="#" class="flex items-center gap-3">
        <img src="LOGOS/{logo_file}" alt="{title}" class="h-12 bg-white rounded-lg p-1.5">
      </a>
      <nav class="hidden md:flex gap-8 text-sm font-semibold uppercase tracking-wide">
        <a href="#sobre" class="hover:opacity-80 transition">Sobre</a>
        <a href="#atividades" class="hover:opacity-80 transition">Atividades</a>
        <a href="#galeria" class="hover:opacity-80 transition">Galeria</a>
        <a href="#democratizacao" class="hover:opacity-80 transition">Democratização</a>
      </nav>
      <button class="md:hidden text-white" id="menu-btn" aria-label="Menu">
        <svg class="w-7 h-7" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" d="M4 6h16M4 12h16M4 18h16"/></svg>
      </button>
    </div>
  </header>

  <!-- ═══════════════ HERO ═══════════════ -->
  <section class="relative min-h-[80vh] flex items-center justify-center overflow-hidden">
    <img src="FOTOS/hero_bg.jpg" alt="Projeto {title}" class="absolute inset-0 w-full h-full object-cover">
    <div class="absolute inset-0 hero-overlay"></div>
    <div class="relative z-10 text-center text-white px-6 max-w-4xl">
      <img src="LOGOS/{logo_file}" alt="Logo {title}" class="h-32 md:h-40 mx-auto mb-8 bg-white/95 rounded-2xl p-4 shadow-2xl">
      <h1 class="font-display text-5xl md:text-7xl font-black mb-4 drop-shadow-2xl" style="letter-spacing: -0.03em;">{title}</h1>
      <p class="text-xl md:text-2xl font-light mb-2">{subtitle}</p>
    </div>
    <div class="absolute bottom-0 left-0 right-0 z-10">
      <svg viewBox="0 0 1440 80" fill="none" class="w-full" preserveAspectRatio="none">
        <path d="M0 40C240 70 480 10 720 40C960 70 1200 10 1440 40V80H0V40Z" fill="white"/>
      </svg>
    </div>
  </section>

  <!-- ═══════════════ SOBRE ═══════════════ -->
  <section id="sobre" class="py-20 lg:py-28 px-6 lg:px-10">
    <div class="max-w-5xl mx-auto grid md:grid-cols-2 gap-12 items-center">
      <div class="reveal-left">
        <div class="rounded-3xl overflow-hidden shadow-xl aspect-square bg-slate-100">
          <img src="FOTOS/sobre.jpg" alt="Projeto {title}" class="w-full h-full object-cover" loading="lazy">
        </div>
      </div>
      <div class="reveal-right">
        <div class="inline-flex items-center gap-2 px-4 py-2 rounded-full text-xs font-bold uppercase tracking-[0.2em] mb-6" style="background: var(--main); color: white; opacity: 0.95;">
          <span class="w-2 h-2 rounded-full bg-white"></span>
          Sobre o Projeto
        </div>
        <h2 class="font-display text-3xl md:text-4xl lg:text-5xl font-extrabold mb-6 text-main" style="letter-spacing: -0.02em;">{title}</h2>
        {sobre_text}
        <div class="mt-6 inline-flex items-center gap-3 px-5 py-3 rounded-full bg-slate-100">
          <svg class="w-5 h-5 text-main" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/></svg>
          <span class="text-sm font-semibold text-slate-700">Fevereiro a Março de 2026</span>
        </div>
      </div>
    </div>
  </section>

  <!-- ═══════════════ ATIVIDADES ═══════════════ -->
  <section id="atividades" class="py-20 lg:py-28 px-6 lg:px-10 bg-slate-50">
    <div class="max-w-6xl mx-auto">
      <div class="text-center mb-20 reveal">
        <div class="inline-flex items-center gap-2 px-4 py-2 rounded-full text-xs font-bold uppercase tracking-[0.2em] mb-6" style="background: {color_main}15; color: {color_main};">
          <span class="w-2 h-2 rounded-full" style="background: {color_main};"></span>
          Programação
        </div>
        <h2 class="font-display text-3xl sm:text-4xl lg:text-5xl font-extrabold text-main" style="letter-spacing: -0.03em;">Atividades do Projeto</h2>
      </div>
      <div class="space-y-24 lg:space-y-28">{"".join(atividades_html)}
      </div>
    </div>
  </section>

  <!-- ═══════════════ GALERIA ═══════════════ -->
  <section id="galeria" class="py-20 lg:py-28 px-6 lg:px-10">
    <div class="max-w-6xl mx-auto">
      <div class="text-center mb-16 reveal">
        <div class="inline-flex items-center gap-2 px-4 py-2 rounded-full text-xs font-bold uppercase tracking-[0.2em] mb-6 bg-slate-100 text-slate-600">
          <span class="w-2 h-2 rounded-full bg-slate-400"></span>
          Registros
        </div>
        <h2 class="font-display text-3xl sm:text-4xl lg:text-5xl font-extrabold text-main" style="letter-spacing: -0.03em;">Galeria do Projeto</h2>
      </div>
      <div class="grid grid-cols-2 md:grid-cols-3 gap-4 lg:gap-6">{"".join(gal_items)}
      </div>
    </div>
  </section>

  <!-- ═══════════════ DEMOCRATIZAÇÃO ═══════════════ -->
  <section id="democratizacao" class="py-20 lg:py-28 px-6 lg:px-10 bg-main text-white">
    <div class="max-w-6xl mx-auto">
      <div class="text-center mb-16 reveal">
        <div class="inline-flex items-center gap-2 px-4 py-2 rounded-full text-xs font-bold uppercase tracking-[0.2em] mb-6 bg-white/15">
          <span class="w-2 h-2 rounded-full bg-white"></span>
          Acessibilidade
        </div>
        <h2 class="font-display text-3xl sm:text-4xl lg:text-5xl font-extrabold" style="letter-spacing: -0.03em;">Democratização de Acesso</h2>
        <p class="text-lg md:text-xl opacity-90 mt-4 max-w-3xl mx-auto">Como o projeto garante que educação e cultura cheguem a todas e todos</p>
      </div>
      <div class="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div class="bg-white/10 backdrop-blur rounded-2xl p-6 reveal">
          <div class="w-12 h-12 rounded-xl bg-white/20 flex items-center justify-center mb-4">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" d="M4.26 10.147a60.436 60.436 0 00-.491 6.347A48.627 48.627 0 0112 20.904a48.627 48.627 0 018.232-4.41 60.46 60.46 0 00-.491-6.347m-15.482 0a50.57 50.57 0 00-2.658-.813A59.905 59.905 0 0112 3.493a59.902 59.902 0 0110.399 5.84c-.896.248-1.783.52-2.658.814"/></svg>
          </div>
          <h4 class="font-bold text-lg mb-2">Escolas Públicas</h4>
          <p class="text-sm opacity-90">Realização gratuita em escolas públicas, com parceria com Secretarias Municipais de Educação.</p>
        </div>
        <div class="bg-white/10 backdrop-blur rounded-2xl p-6 reveal">
          <div class="w-12 h-12 rounded-xl bg-white/20 flex items-center justify-center mb-4">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" d="M12 6.375a3.375 3.375 0 11-6.75 0 3.375 3.375 0 016.75 0z"/></svg>
          </div>
          <h4 class="font-bold text-lg mb-2">Aprendizagem Maker</h4>
          <p class="text-sm opacity-90">Metodologia baseada em aprendizagem maker e em projetos, acessível a crianças de 8 a 11 anos.</p>
        </div>
        <div class="bg-white/10 backdrop-blur rounded-2xl p-6 reveal">
          <div class="w-12 h-12 rounded-xl bg-white/20 flex items-center justify-center mb-4">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M19.5 12c0-1.232-.046-2.453-.138-3.662a4.006 4.006 0 00-3.7-3.7 48.678 48.678 0 00-7.324 0 4.006 4.006 0 00-3.7 3.7"/></svg>
          </div>
          <h4 class="font-bold text-lg mb-2">Sustentabilidade</h4>
          <p class="text-sm opacity-90">Integração entre educação, cultura, tecnologia e sustentabilidade com materiais recicláveis.</p>
        </div>
        <div class="bg-white/10 backdrop-blur rounded-2xl p-6 reveal">
          <div class="w-12 h-12 rounded-xl bg-white/20 flex items-center justify-center mb-4">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" d="M9 17.25v1.007a3 3 0 01-.879 2.122L7.5 21h9l-.621-.621A3 3 0 0115 18.257V17.25"/></svg>
          </div>
          <h4 class="font-bold text-lg mb-2">Conteúdo Digital</h4>
          <p class="text-sm opacity-90">Palestra virtual para professores ampliando o alcance e continuidade pedagógica.</p>
        </div>
      </div>
    </div>
  </section>

  <!-- ═══════════════ RÉGUA DE PATROCINADORES ═══════════════ -->
  <section class="py-16 lg:py-20 px-6 lg:px-10 bg-white">
    <div class="max-w-6xl mx-auto reveal">
      <img src="REGUAS/{regua_file}" alt="Régua de patrocinadores" class="w-full h-auto">
    </div>
  </section>

  <!-- ═══════════════ FOOTER ═══════════════ -->
  <footer class="bg-dark text-white py-12 px-6">
    <div class="max-w-6xl mx-auto flex flex-col md:flex-row items-center justify-between gap-6">
      <div class="flex items-center gap-4">
        <img src="LOGOS/{logo_file}" alt="{title}" class="h-14 bg-white/10 rounded-lg p-2">
        <div>
          <p class="font-display font-bold text-lg">{title}</p>
          <p class="text-sm text-white/70">Realização NTICS Projetos</p>
        </div>
      </div>
      <p class="text-sm text-white/60">© 2026 {title}. Todos os direitos reservados.</p>
    </div>
  </footer>

  <!-- ═══════════════ SCRIPTS ═══════════════ -->
  <script>
    // Reveal animation
    const observer = new IntersectionObserver((entries) => {{
      entries.forEach(entry => {{
        if (entry.isIntersecting) {{
          entry.target.classList.add('visible');
          observer.unobserve(entry.target);
        }}
      }});
    }}, {{ threshold: 0.15, rootMargin: '0px 0px -40px 0px' }});
    document.querySelectorAll('.reveal, .reveal-left, .reveal-right').forEach(el => observer.observe(el));

    // Scroll progress
    window.addEventListener('scroll', () => {{
      const scrollTop = window.scrollY;
      const height = document.documentElement.scrollHeight - window.innerHeight;
      document.getElementById('scroll-progress').style.width = (scrollTop / height * 100) + '%';
      document.querySelector('.site-header').classList.toggle('scrolled', scrollTop > 40);
    }});
  </script>
</body>
</html>
"""
    out_path = ROOT / "assets/projetos/116. CULTURA ROBÓTICA (ÁSTER)/site.html"
    # Backup first
    bak = out_path.with_suffix(".html.bak")
    if not bak.exists():
        bak.write_text(out_path.read_text(encoding="utf-8"), encoding="utf-8")
    out_path.write_text(html, encoding="utf-8")
    print(f"Wrote {out_path} ({len(html)} bytes)")
    print(f"Backup: {bak}")

if __name__ == "__main__":
    build_116()
