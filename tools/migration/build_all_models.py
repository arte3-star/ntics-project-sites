"""Gera site.html modelo para todos os 6 sites (116/117/119/125/127G/127S)
usando conteudo REAL do Lovable e padrao de estrutura RF-origin.
"""
import json
import re
import unicodedata
from pathlib import Path

ROOT = Path(r"g:\O meu disco\AUTOMAÇÕES")

# Config por site
SITES = {
    "116": {
        "dir": "116. CULTURA ROBÓTICA (ÁSTER)",
        "logo": "116_cultura_robotica.png",
        "regua": "Régua - 116.png",
        "color_main": "#2196F3",
        "color_dark": "#1565C0",
        "hero_subtitle": "Tecnologia, Sustentabilidade e Educação nas Escolas",
        "sonnet_pool": "robotica",
        "include_oficina_foto": False,
        # Ordem: 1=Palestra, 2=Artes Plásticas, 3=Robótica, 4=Feira, 5=Espetáculo
        "force_atividade_photo_file": {
            1: r"g:\O meu disco\AUTOMAÇÕES\assets\melhores-fotos\2. PEC   PIE   PED\061_pec-pie-ped_evento_grande-plateia-criancas-adultos-auditorio-escolar.jpg",
            2: r"g:\O meu disco\AUTOMAÇÕES\assets\melhores-fotos\2. PEC   PIE   PED\PEC\082_pec-pie-ped_oficina_crianca-criando-globo-terrestre-colorido.jpeg",
            3: r"g:\O meu disco\AUTOMAÇÕES\assets\melhores-fotos\5. ROBÓTICA NAS ESCOLAS\082_robotica-escolas_robotica_criancas-montando-kit-robotica-com-instrutor.jpg",
            4: r"g:\O meu disco\AUTOMAÇÕES\assets\melhores-fotos\5. ROBÓTICA NAS ESCOLAS\087_robotica-escolas_robotica_criancas-explorando-kit-robotica-com-educadora.jpg",
            5: r"g:\O meu disco\AUTOMAÇÕES\assets\melhores-fotos\5. ROBÓTICA NAS ESCOLAS\091_robotica-escolas_robotica_criancas-personificadas-robos-apresentacao-palco.jpg",
        },
    },
    "117": {
        "dir": "117. TEATRO E OFICINA ROBÓTICA 4ED (WHIRLPOOL)",
        "logo": "117_teatro_robotica.png",
        "regua": "Régua - 117.png",
        "color_main": "#0891B2",
        "color_dark": "#155E75",
        "hero_subtitle": "Teatro, robótica e criatividade nas escolas públicas",
        "sonnet_pool": "robotica",
        "include_oficina_foto": False,
        # Ordem: 1=Arte+Criatividade, 2=Robótica reciclados, 3=Feira, 4=Espetáculo
        "force_atividade_photo_file": {
            1: r"g:\O meu disco\AUTOMAÇÕES\assets\melhores-fotos\5. ROBÓTICA NAS ESCOLAS\33_cultura-robotica_oficina_B_aluna-cola-quente-robo-papelao.jpg",
            2: r"g:\O meu disco\AUTOMAÇÕES\assets\melhores-fotos\5. ROBÓTICA NAS ESCOLAS\072_robotica-escolas_robotica_criancas-apresentando-robo-feito-papelao.jpg",
            3: r"g:\O meu disco\AUTOMAÇÕES\assets\melhores-fotos\5. ROBÓTICA NAS ESCOLAS\087_robotica-escolas_robotica_criancas-explorando-kit-robotica-com-educadora.jpg",
            4: r"g:\O meu disco\AUTOMAÇÕES\assets\melhores-fotos\5. ROBÓTICA NAS ESCOLAS\091_robotica-escolas_robotica_criancas-personificadas-robos-apresentacao-palco.jpg",
        },
    },
    "119": {
        "dir": "119. PEC EU FAÇO PARTE 2ªED (SYLVAMO)",
        "logo": "119_pec.png",
        "regua": "Régua - 119.png",
        "color_main": "#16A34A",
        "color_dark": "#14532D",
        "hero_subtitle": "Educação, cidadania e protagonismo juvenil",
        "sonnet_pool": "pec",
        "include_oficina_foto": True,  # tem Oficinas de Fotografia Digital
        # Ordem: 1=Workshop Formação Professores, 2=Oficina Educação Ambiental, 3=Oficina Fotografia, 4=Feira de Ideias
        "force_atividade_photo_file": {
            1: r"g:\O meu disco\AUTOMAÇÕES\assets\melhores-fotos\2. PEC   PIE   PED\061_pec-pie-ped_evento_grande-plateia-criancas-adultos-auditorio-escolar.jpg",
            3: r"g:\O meu disco\AUTOMAÇÕES\assets\melhores-fotos\OFICINA DE FOTOGRAFIA\029_oficina-fotografia_oficina_crianca-fotografando-camera-canon-outdoor.jpg",
            4: r"g:\O meu disco\AUTOMAÇÕES\assets\melhores-fotos\2. PEC   PIE   PED\PEC\065_pec-pie-ped_oficina_criancas-explorando-experimento-agua-com-educadores.jpeg",
        },
    },
    "125": {
        "dir": "125. EXPOSIÇÃO - GASTRONOMIA TAMBÉM É ARTE 2ED (GRU)",
        "logo": "125_gastronomia.png",
        "regua": "Régua - 125 - GRU.png",
        "color_main": "#EA580C",
        "color_dark": "#9A3412",
        "hero_subtitle": "Gastronomia sustentável como linguagem artística",
        "sonnet_pool": "culinaria",
        "include_oficina_foto": True,  # tem Oficina de Fotografia
        "galeria_n": 12,  # pool grande de culinaria — mais fotos
        # Ordem: 1=Culinária, 2=Workshop Foto, 3=Exposição (sem foto), 4=Palestra Educadores
        "force_atividade_photo_file": {
            1: r"g:\O meu disco\AUTOMAÇÕES\assets\melhores-fotos\7. CULINÁRIA SUSTENTÁVEL\093_culinaria-sustentavel_culinaria_mulher-preparando-pratos-culinaria-sustentavel_enercan.png",
            2: r"g:\O meu disco\AUTOMAÇÕES\assets\melhores-fotos\OFICINA DE FOTOGRAFIA\029_oficina-fotografia_oficina_crianca-fotografando-camera-canon-outdoor.jpg",
            3: "__NONE__",  # exposição sem foto (Lucas pediu para deixar sem)
            4: r"g:\O meu disco\AUTOMAÇÕES\assets\melhores-fotos\2. PEC   PIE   PED\PEC\074_pec-pie-ped_palestra_educadora-apresentando-projeto-sala-aula.jpg",
        },
    },
    "124": {
        "dir": "124. EXPOSIÇÃO - GASTRONOMIA TAMBÉM É ARTE (COMPAGAS)",
        "logo": "Logo - gastronomia.png",
        "regua": "Régua - 124 (1).png",
        "color_main": "#EA580C",
        "color_dark": "#9A3412",
        "hero_subtitle": "Gastronomia sustentável como linguagem artística em Lapa/PR",
        "sonnet_pool": "culinaria",
        "include_oficina_foto": True,
        "galeria_n": 12,
        "galeria_pool_priority": ["culinaria","oficina_foto"],  # culinaria primeiro, foto no fim
        # Ordem: 1=Palestra, 2=Culinária, 3=Workshop Foto, 4=Exposição
        "force_atividade_photo_file": {
            1: r"g:\O meu disco\AUTOMAÇÕES\assets\melhores-fotos\10 - Negócio Cultural\03_negocio-cultural_capacitacao_A_facilitadora-amarelo-plateia-sala.jpg",
            2: r"g:\O meu disco\AUTOMAÇÕES\assets\melhores-fotos\7. CULINÁRIA SUSTENTÁVEL\093_culinaria-sustentavel_culinaria_mulher-preparando-pratos-culinaria-sustentavel_enercan.png",
            3: r"g:\O meu disco\AUTOMAÇÕES\assets\melhores-fotos\OFICINA DE FOTOGRAFIA\029_oficina-fotografia_oficina_crianca-fotografando-camera-canon-outdoor.jpg",
            4: r"g:\O meu disco\AUTOMAÇÕES\assets\melhores-fotos\7. CULINÁRIA SUSTENTÁVEL\085_culinaria-sustentavel_exposicao_visitantes-observando-paineis-gastronomia-arte.jpg",
        },
    },
    "127G": {
        "dir": "127. PIE EMPREENDEDORISMO É ARTE 2ED (GRU)",
        "logo": "127_pie_GRU.png",
        "regua": "Régua - 127 - GRU.png",
        "color_main": "#DB2777",
        "color_dark": "#9D174D",
        "hero_subtitle": "Programa de Inovação e Empreendedorismo nas escolas",
        "sonnet_pool": "pie",
        "include_oficina_foto": False,
        # Ordem: 1=Palestra Abertura, 2=EU CRIADOR (artes), 3=PROBLEMAS VIRAM IDEIAS, 4=Feira de Ideias
        "force_atividade_photo_file": {
            1: r"g:\O meu disco\AUTOMAÇÕES\assets\melhores-fotos\2. PEC   PIE   PED\PIE\096_pec-pie-ped_palestra_agente-educador-apresentando-para-plateia-sentada.jpg",
            2: r"g:\O meu disco\AUTOMAÇÕES\assets\melhores-fotos\2. PEC   PIE   PED\PEC\082_pec-pie-ped_oficina_crianca-criando-globo-terrestre-colorido.jpeg",
            3: r"g:\O meu disco\AUTOMAÇÕES\assets\melhores-fotos\2. PEC   PIE   PED\PIE\095_pec-pie-ped_oficina_instrutor-orientando-grupo-adolescentes-mesa.jpg",
            4: r"g:\O meu disco\AUTOMAÇÕES\assets\melhores-fotos\2. PEC   PIE   PED\PIE\099_pec-pie-ped_evento_grupo-jovens-segurando-cartazes-pie-programa.jpg",
        },
    },
    "127S": {
        "dir": "127. PIE EMPREENDEDORISMO É ARTE 2ED (SOTREQ)",
        "logo": "127_pie_SOTREQ.png",
        "regua": "Régua - 127 - SOTREQ.png",
        "color_main": "#DB2777",
        "color_dark": "#9D174D",
        "hero_subtitle": "Programa de Inovação e Empreendedorismo nas escolas",
        "sonnet_pool": "pie",
        "include_oficina_foto": False,
        # Mesma sequência do 127G
        "force_atividade_photo_file": {
            1: r"g:\O meu disco\AUTOMAÇÕES\assets\melhores-fotos\2. PEC   PIE   PED\PIE\096_pec-pie-ped_palestra_agente-educador-apresentando-para-plateia-sentada.jpg",
            2: r"g:\O meu disco\AUTOMAÇÕES\assets\melhores-fotos\2. PEC   PIE   PED\PEC\082_pec-pie-ped_oficina_crianca-criando-globo-terrestre-colorido.jpeg",
            3: r"g:\O meu disco\AUTOMAÇÕES\assets\melhores-fotos\2. PEC   PIE   PED\PIE\095_pec-pie-ped_oficina_instrutor-orientando-grupo-adolescentes-mesa.jpg",
            4: r"g:\O meu disco\AUTOMAÇÕES\assets\melhores-fotos\2. PEC   PIE   PED\PIE\099_pec-pie-ped_evento_grupo-jovens-segurando-cartazes-pie-programa.jpg",
        },
    },
}

# Keywords -> activity_match tags (para pareamento semantico)
def match_tags_for_title(titulo):
    t = titulo.lower()
    tags = []
    if any(k in t for k in ["teatro","espetáculo","espetaculo","apresentação","apresentacao"]):
        tags += ["apresentacao_teatro","feira"]
    if any(k in t for k in ["artes plásticas","artes plasticas","colagem","criatividade","criador"]):
        tags += ["oficina_pratica","oficina_artes","oficina_eu_criador"]
    if "palestra" in t:
        tags += ["palestra","palestra_abertura","palestra_virtual","formacao_professores"]
    if any(k in t for k in ["fotografia","foto","digital"]):
        tags += ["workshop_fotografia"]
    if any(k in t for k in ["exposição","exposicao","exposiç"]):
        tags += ["exposicao_gastronomica"]
    if any(k in t for k in ["culinária","culinaria","aula-show","gastronom"]):
        tags += ["aula_culinaria"]
    if any(k in t for k in ["oficina"]):
        tags += ["oficina_pratica","oficina_aula","oficina_problemas"]
    if any(k in t for k in ["problemas","ideias"]):
        tags += ["oficina_problemas_ideias"]
    if any(k in t for k in ["ideia","voz"]):
        tags += ["oficina_ideia_voz"]
    return list(set(tags))

def score_photo(entry, want_tags, mode="hero"):
    if entry.get("quality_issues") == "screenshot": return -1000
    base = entry["hero_score"] if mode == "hero" else entry["galeria_score"]
    tag_bonus = 0
    for t in want_tags:
        if t in entry.get("activity_match", []):
            tag_bonus = 15; break
    return base * 2 + tag_bonus

def load_pool(sonnet_key, include_oficina_foto=True):
    """Carrega pool de fotos. Inclui oficina_foto só se o projeto tiver atividade de fotografia."""
    base = json.loads((ROOT / f"output/rankings/sonnet/{sonnet_key}.json").read_text(encoding="utf-8"))
    for e in base: e["__pool__"] = sonnet_key
    if include_oficina_foto:
        ofoto = json.loads((ROOT / "output/rankings/sonnet/oficina_foto.json").read_text(encoding="utf-8"))
        for e in ofoto: e["__pool__"] = "oficina_foto"
        return base + ofoto
    return base

SONNET_CAT_MAP = {
    "robotica":  "5. ROBÓTICA NAS ESCOLAS",
    "pec":       "2. PEC   PIE   PED/PEC",
    "pie":       "2. PEC   PIE   PED/PIE",
    "culinaria": "7. CULINÁRIA SUSTENTÁVEL",
    "oficina_foto": "OFICINA DE FOTOGRAFIA",
}

BRAND_BLACKLIST = [
    "sada","pague menos","wilson sons","statkraft",
    "whirlpool","áster","aster","sylvamo","compagás","compagas",
    "nereu ramos","semec","tecnoarte","circuiteira",
    "revolucionários verdes","revolucionarios verdes",
    "engrenagens da imaginação","engrenagens da imaginacao",
]
def is_branded(caption):
    c = caption.lower()
    return any(b in c for b in BRAND_BLACKLIST)

def copy_photo(entry, dst_path):
    """Copia foto original do melhores-fotos para dst_path (como .jpg)."""
    import shutil
    from PIL import Image
    pool_key = entry["__pool__"]
    src_dir = ROOT / "assets/melhores-fotos" / SONNET_CAT_MAP[pool_key]
    stem = Path(entry["file"]).stem
    for f in src_dir.rglob("*"):
        if f.suffix.lower() not in {".jpg",".jpeg",".png",".webp"}: continue
        if f.stem == stem:
            if f.suffix.lower() in {".jpg",".jpeg"}:
                shutil.copy(f, dst_path)
            else:
                Image.open(f).convert("RGB").save(dst_path, "JPEG", quality=92)
            return True
    return False

SLUG_BY_SITE = {
    "116": "cultura-robotica-aster",
    "117": "teatro-oficina-robotica-4ed-whirlpool",
    "119": "pec-eu-faco-parte-2ed-sylvamo",
    "124": "gastronomia-tambem-e-arte-compagas",
    "125": "gastronomia-tambem-e-arte-2ed-gru",
    "127G": "pie-empreendedorismo-e-arte-2ed-gru",
    "127S": "pie-empreendedorismo-e-arte-2ed-sotreq",
}


def _normalize_atividades(atividades):
    """Editorial usa 'nome'/'descricao'; Lovable usa 'titulo'/'descricao'. Unifica."""
    out = []
    for a in atividades or []:
        out.append({
            "titulo": a.get("titulo") or a.get("nome") or "Atividade",
            "descricao": a.get("descricao") or "",
        })
    return out


def _load_content(site_id):
    """Carrega editorial JSON se existir; senão Lovable. Retorna content + cronograma."""
    slug = SLUG_BY_SITE.get(site_id)
    editorial_path = ROOT / f"output/_editorial_{slug}_content.json" if slug else None
    lovable_path = ROOT / f"output/_lovable_{site_id}_content.json"
    cronograma_path = ROOT / f"output/cronogramas/{slug}.json" if slug else None

    if editorial_path and editorial_path.exists():
        content = json.loads(editorial_path.read_text(encoding="utf-8"))
        content["_source"] = "editorial"
        # garante chaves do schema antigo
        content.setdefault("cidades", [])
    elif lovable_path.exists():
        content = json.loads(lovable_path.read_text(encoding="utf-8"))
        content["_source"] = "lovable"
    else:
        return None, None
    content["atividades"] = _normalize_atividades(content.get("atividades", []))

    cronograma = None
    if cronograma_path and cronograma_path.exists():
        cron = json.loads(cronograma_path.read_text(encoding="utf-8"))
        if cron.get("total_escolas", 0) > 0:
            cronograma = cron
            # popula cidades a partir do cronograma se vazio
            if not content.get("cidades"):
                content["cidades"] = sorted({c["cidade"] for c in cron["cards"]})
    return content, cronograma


def build_site(site_id, cfg):
    content, cronograma = _load_content(site_id)
    if not content:
        print(f"[{site_id}] SKIP - no content")
        return
    site_dir = ROOT / "assets/projetos" / cfg["dir"]
    fotos_dir = site_dir / "FOTOS"
    fotos_dir.mkdir(exist_ok=True)

    pool = load_pool(cfg["sonnet_pool"], cfg.get("include_oficina_foto", False))

    def find_in_pool_by_stem(stem):
        for e in pool:
            if Path(e["file"]).stem == stem:
                return e
        # Fallback: include oficina_foto se necessario
        if stem.startswith("57_") or stem.startswith("59_") or stem.startswith("Lais"):
            for pool_key in ("culinaria","pie","oficina_foto"):
                try:
                    extra = json.loads((ROOT / f"output/rankings/sonnet/{pool_key}.json").read_text(encoding="utf-8"))
                    for e in extra:
                        if Path(e["file"]).stem == stem:
                            e["__pool__"] = pool_key
                            return e
                except: pass
        return None

    used = set()

    # 1. Hero bg — plateia/grupo ampla, sem marca
    hero_cands = [e for e in pool if not is_branded(e["caption"]) and e.get("quality_issues") != "screenshot"]
    hero_cands.sort(key=lambda e: -(e["hero_score"]*2 + (5 if e.get("scene") in ("plateia_publico","apresentacao_teatro","aula_show_chef","palestra_plateia") else 0)))
    hero = hero_cands[0] if hero_cands else None
    if hero:
        copy_photo(hero, fotos_dir / "hero_bg.jpg")
        used.add(Path(hero["file"]).stem)

    # 2. Sobre — forced ou grupo/atividade
    sobre = None
    if cfg.get("force_sobre_photo"):
        sobre = find_in_pool_by_stem(cfg["force_sobre_photo"])
    if not sobre:
        sobre_cands = [e for e in pool if not is_branded(e["caption"]) and Path(e["file"]).stem not in used and e.get("quality_issues") != "screenshot"]
        sobre_cands.sort(key=lambda e: -(e["hero_score"] + e["galeria_score"] + (4 if e.get("scene") in ("grupo_posando","oficina_pratica","aula_show_chef","oficina_aula","detalhe_maos") else 0)))
        sobre = sobre_cands[0] if sobre_cands else None
    if sobre:
        copy_photo(sobre, fotos_dir / "sobre.jpg")
        used.add(Path(sobre["file"]).stem)

    # 3. Atividades (photos) — com force override opcional
    ativ_photos = []
    force_map = cfg.get("force_atividade_photo", {})
    force_file_map = cfg.get("force_atividade_photo_file", {})
    for i, a in enumerate(content.get("atividades",[]), 1):
        chosen = None
        # Prioridade 0: __NONE__ explicit = renderiza sem foto
        if force_file_map.get(i) == "__NONE__":
            ativ_photos.append((a["titulo"], a["descricao"], None))
            continue
        # Prioridade 1: arquivo absoluto (de outra pasta)
        if i in force_file_map:
            src = Path(force_file_map[i])
            if src.exists():
                import shutil
                from PIL import Image
                dst = fotos_dir / f"atividade_{i}.jpg"
                if src.suffix.lower() in {".jpg",".jpeg"}:
                    shutil.copy(src, dst)
                else:
                    Image.open(src).convert("RGB").save(dst, "JPEG", quality=92)
                ativ_photos.append((a["titulo"], a["descricao"], f"FOTOS/atividade_{i}.jpg"))
                continue
        # Prioridade 2: stem do pool
        if i in force_map:
            chosen = find_in_pool_by_stem(force_map[i])
        if not chosen:
            tags = match_tags_for_title(a["titulo"])
            cands = [e for e in pool if Path(e["file"]).stem not in used and e.get("quality_issues") != "screenshot" and not is_branded(e["caption"])]
            cands.sort(key=lambda e: -score_photo(e, tags, mode="hero"))
            chosen = cands[0] if cands else None
        if chosen:
            copy_photo(chosen, fotos_dir / f"atividade_{i}.jpg")
            used.add(Path(chosen["file"]).stem)
            ativ_photos.append((a["titulo"], a["descricao"], f"FOTOS/atividade_{i}.jpg"))
        else:
            ativ_photos.append((a["titulo"], a["descricao"], None))

    # 4. Galeria (N fotos restantes, priorizando galeria_score alto e sem marca)
    galeria_n = cfg.get("galeria_n", 6)
    gal_cands = [e for e in pool if Path(e["file"]).stem not in used and e.get("quality_issues") != "screenshot" and not is_branded(e["caption"])]
    # Sort: pool_priority primeiro (se definido), depois galeria_score
    pool_priority = cfg.get("galeria_pool_priority", [])
    def gal_sort_key(e):
        pool_rank = pool_priority.index(e["__pool__"]) if e["__pool__"] in pool_priority else len(pool_priority)
        return (pool_rank, -e["galeria_score"])
    gal_cands.sort(key=gal_sort_key)
    galeria = gal_cands[:galeria_n]
    for i, g in enumerate(galeria, 1):
        copy_photo(g, fotos_dir / f"galeria_{i}.jpg")
        used.add(Path(g["file"]).stem)

    # 5. Build HTML
    title = content.get("hero_title","Projeto").replace("\n"," ").strip()
    subtitle = content.get("hero_subtitle") or cfg["hero_subtitle"]
    democratizacao_text = content.get("democratizacao")
    video_palestra = content.get("video_palestra")
    sobre_paragraphs = content.get("sobre_paragraphs", [])
    cidades = content.get("cidades", [])
    cidades_desc = content.get("cidades_desc", [])

    sobre_text_html = "".join([
        f'<p class="text-base lg:text-lg text-slate-700 leading-relaxed mb-4">{p}</p>'
        for p in sobre_paragraphs if p and "Ministério da Cultura apresenta" not in p
    ])

    # Atividades HTML
    ativ_html_parts = []
    for i, (titulo, desc, img) in enumerate(ativ_photos, 1):
        side = "reveal-left" if i % 2 == 1 else "reveal-right"
        order_img = "lg:order-1" if i % 2 == 1 else "lg:order-2"
        order_text = "lg:order-2" if i % 2 == 1 else "lg:order-1"
        if not img:
            # Layout sem foto — ocupa coluna única, mais elegante
            ativ_html_parts.append(f'''
      <div class="max-w-3xl mx-auto text-center {side}">
        <div class="flex items-center gap-4 mb-6 justify-center">
          <div class="w-14 h-14 rounded-2xl flex items-center justify-center font-display text-2xl text-white" style="background: {cfg['color_main']}; box-shadow: 0 8px 24px {cfg['color_main']}40;">
            {i:02d}
          </div>
        </div>
        <h3 class="font-display text-2xl sm:text-3xl lg:text-4xl mb-5" style="color: {cfg['color_main']}; letter-spacing: -0.02em; line-height: 1.15;">
          {titulo}
        </h3>
        <p class="text-base lg:text-lg text-slate-600" style="line-height: 1.8;">{desc}</p>
      </div>''')
            continue
        img_html = f'<img src="{img}" alt="{titulo}" loading="lazy" class="w-full h-full object-cover">'
        ativ_html_parts.append(f'''
      <div class="grid lg:grid-cols-2 gap-10 lg:gap-16 items-center {side}">
        <div class="{order_text}">
          <div class="flex items-center gap-4 mb-6">
            <div class="w-14 h-14 rounded-2xl flex items-center justify-center font-display text-2xl text-white" style="background: {cfg['color_main']}; box-shadow: 0 8px 24px {cfg['color_main']}40;">
              {i:02d}
            </div>
            <div class="h-px flex-1" style="background: linear-gradient(90deg, {cfg['color_main']}30, transparent);"></div>
          </div>
          <h3 class="font-display text-2xl sm:text-3xl lg:text-4xl mb-5" style="color: {cfg['color_main']}; letter-spacing: -0.02em; line-height: 1.15;">
            {titulo}
          </h3>
          <p class="text-base lg:text-lg text-slate-600" style="line-height: 1.8;">{desc}</p>
        </div>
        <div class="{order_img}">
          <div class="rounded-3xl aspect-[16/10] overflow-hidden shadow-xl" style="background: {cfg['color_main']}15;">
            {img_html}
          </div>
        </div>
      </div>''')

    # Cidades section (optional). Se 1 cidade só, centraliza com texto descritivo.
    cidades_html = ""
    cidades_uma_so = len(cidades) == 1
    if cidades:
        cidade_cards = "".join([
            f'''<div class="bg-white rounded-2xl p-6 text-center shadow-md hover:shadow-xl transition reveal">
                  <div class="w-12 h-12 rounded-full mx-auto mb-3 flex items-center justify-center" style="background: {cfg['color_main']}15;">
                    <svg class="w-6 h-6" style="color: {cfg['color_main']};" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" d="M15 10.5a3 3 0 11-6 0 3 3 0 016 0z"/><path stroke-linecap="round" d="M19.5 10.5c0 7.142-7.5 11.25-7.5 11.25S4.5 17.642 4.5 10.5a7.5 7.5 0 1115 0z"/></svg>
                  </div>
                  <h4 class="font-bold text-lg text-slate-800">{c}</h4>
                </div>''' for c in cidades
        ])
        # Layout adapta por número de cidades — 1 cidade fica centralizada com texto descritivo
        if cidades_uma_so:
            cidade_unica = cidades[0]
            descricao_cidade = f"O projeto acontece em <strong>{cidade_unica}</strong>, articulado com escolas, secretarias municipais e organizações parceiras locais."
            cidade_cards_wrapper = f'''<div class="max-w-md mx-auto">
                <div class="bg-white rounded-3xl p-10 text-center shadow-lg reveal">
                  <div class="w-20 h-20 rounded-full mx-auto mb-5 flex items-center justify-center" style="background: {cfg['color_main']}15;">
                    <svg class="w-10 h-10" style="color: {cfg['color_main']};" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" d="M15 10.5a3 3 0 11-6 0 3 3 0 016 0z"/><path stroke-linecap="round" d="M19.5 10.5c0 7.142-7.5 11.25-7.5 11.25S4.5 17.642 4.5 10.5a7.5 7.5 0 1115 0z"/></svg>
                  </div>
                  <h3 class="font-display text-3xl font-extrabold mb-3" style="color: {cfg['color_main']};">{cidade_unica}</h3>
                  <p class="text-slate-600 text-base leading-relaxed">{descricao_cidade}</p>
                </div>
              </div>'''
        else:
            cidade_cards_wrapper = f'<div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 max-w-3xl mx-auto">{cidade_cards}</div>'
        cidades_html = f'''
  <!-- ═══════════════ CIDADES ═══════════════ -->
  <section id="cidades" class="py-20 lg:py-28 px-6 lg:px-10 bg-slate-50">
    <div class="max-w-5xl mx-auto">
      <div class="text-center mb-12 reveal">
        <div class="inline-flex items-center gap-2 px-4 py-2 rounded-full text-xs font-bold uppercase tracking-[0.2em] mb-6" style="background: {cfg['color_main']}15; color: {cfg['color_main']};">
          <span class="w-2 h-2 rounded-full" style="background: {cfg['color_main']};"></span>
          {'Onde Acontece' if cidades_uma_so else 'Cidades Atendidas'}
        </div>
        <h2 class="font-display text-3xl sm:text-4xl lg:text-5xl font-extrabold" style="color: {cfg['color_main']}; letter-spacing: -0.03em;">Por Onde Passamos</h2>
      </div>
      {cidade_cards_wrapper}
    </div>
  </section>'''

    # Cronograma section — board por cidade: cada cidade como tile com total alunos +
    # mini-lista de escolas dentro. Lucas pediu visão "small board" agregada por cidade.
    cronograma_html = ""
    if cronograma and cronograma.get("cards"):
        cards = cronograma["cards"]
        # Agrega por cidade
        cidade_buckets = {}
        for c in cards:
            cidade = c["cidade"]
            b = cidade_buckets.setdefault(cidade, {"cidade": cidade, "escolas": [], "total_alunos": 0})
            escola_short = c["escola"] if len(c["escola"]) <= 50 else c["escola"][:47] + "…"
            b["escolas"].append({"nome": escola_short, "alunos": c["total_alunos"], "publico": c.get("publico", "alunos")})
            b["total_alunos"] += c["total_alunos"]
        cidade_list = sorted(cidade_buckets.values(), key=lambda x: -x["total_alunos"])
        n_cidades = len(cidade_list)
        rotativo = n_cidades > 3

        cards_html_parts = []
        for cb in cidade_list:
            esc_lines = []
            for e in cb["escolas"]:
                alunos_fmt = f"{e['alunos']:,}".replace(",", ".")
                pub = e.get("publico", "alunos")
                esc_lines.append(
                    f'<li class="flex justify-between items-baseline gap-3 py-1.5 border-t border-slate-100 first:border-0 text-sm">'
                    f'<span class="text-slate-600 truncate">{e["nome"]}</span>'
                    f'<span class="font-semibold text-slate-700 tabular-nums shrink-0">{alunos_fmt} {pub}</span>'
                    f'</li>'
                )
            escolas_html = "".join(esc_lines)
            cards_html_parts.append(f'''<div class="snap-start shrink-0 w-80 lg:w-auto bg-white rounded-2xl p-6 shadow-md hover:shadow-xl transition reveal flex flex-col">
                  <div class="flex items-center gap-2 mb-2">
                    <svg class="w-4 h-4" style="color: {cfg['color_main']};" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" d="M15 10.5a3 3 0 11-6 0 3 3 0 016 0z"/><path stroke-linecap="round" d="M19.5 10.5c0 7.142-7.5 11.25-7.5 11.25S4.5 17.642 4.5 10.5a7.5 7.5 0 1115 0z"/></svg>
                    <div class="text-xs font-bold uppercase tracking-[0.18em]" style="color: {cfg['color_main']};">{cb['cidade']}</div>
                  </div>
                  <div class="flex items-baseline gap-2 mb-4">
                    <span class="font-display text-4xl font-extrabold" style="color: {cfg['color_main']};">{f"{cb['total_alunos']:,}".replace(",", ".")}</span>
                    <span class="text-sm text-slate-500">{'alunos' if all(e.get('publico','alunos')=='alunos' for e in cb['escolas']) else 'participantes'} · {len(cb['escolas'])} {('local' if len(cb['escolas']) == 1 else 'locais') if not all(e.get('publico','alunos')=='alunos' for e in cb['escolas']) else ('escola' if len(cb['escolas']) == 1 else 'escolas')}</span>
                  </div>
                  <ul class="mt-auto">{escolas_html}</ul>
                </div>''')
        if rotativo:
            wrapper_class = "flex gap-5 overflow-x-auto snap-x snap-mandatory pb-4 -mx-6 px-6 lg:mx-0 lg:px-0"
        else:
            grid_cols = "lg:grid-cols-2" if n_cidades == 2 else "lg:grid-cols-3"
            wrapper_class = f"grid grid-cols-1 sm:grid-cols-2 {grid_cols} gap-5 max-w-5xl mx-auto"
        total_alunos = cronograma.get("total_alunos", 0)
        total_escolas = cronograma.get("total_escolas", 0)
        atualizado = cronograma.get("atualizado_em", "")
        cronograma_html = f'''
  <!-- ═══════════════ CRONOGRAMA ═══════════════ -->
  <section id="cronograma" class="py-20 lg:py-28 px-6 lg:px-10 bg-white">
    <div class="max-w-6xl mx-auto">
      <div class="text-center mb-12 reveal">
        <div class="inline-flex items-center gap-2 px-4 py-2 rounded-full text-xs font-bold uppercase tracking-[0.2em] mb-6" style="background: {cfg['color_main']}15; color: {cfg['color_main']};">
          <span class="w-2 h-2 rounded-full" style="background: {cfg['color_main']};"></span>
          Onde Estamos
        </div>
        <h2 class="font-display text-3xl sm:text-4xl lg:text-5xl font-extrabold text-main" style="letter-spacing: -0.03em;">Onde Estamos</h2>
        <p class="text-slate-600 mt-4 text-lg">{n_cidades} cidade{'s' if n_cidades != 1 else ''}, {total_escolas} {('escolas' if total_escolas != 1 else 'escola') if all(e.get('publico','alunos')=='alunos' for cb in cidade_list for e in cb['escolas']) else ('locais' if total_escolas != 1 else 'local')}, {f"{total_alunos:,}".replace(",", ".")} {('estudantes alcançados' if all(e.get('publico','alunos')=='alunos' for cb in cidade_list for e in cb['escolas']) else 'participantes alcançados')}.</p>
        <p class="text-xs text-slate-400 mt-2">Atualizado em {atualizado}</p>
      </div>
      <div class="{wrapper_class}">{"".join(cards_html_parts)}</div>
    </div>
  </section>'''

    # Vídeo da palestra (opcional, parte da seção democratização)
    video_palestra_html = ""
    if video_palestra:
        v_titulo = video_palestra.get("titulo", "Palestra")
        v_sub = video_palestra.get("subtitulo", "")
        yt_id = video_palestra.get("youtube_id")
        is_placeholder = video_palestra.get("placeholder", False) or not yt_id
        if is_placeholder:
            video_inner = f'''<div class="aspect-video rounded-2xl flex flex-col items-center justify-center text-center p-8 border-2 border-dashed" style="border-color: {cfg['color_main']}40; background: {cfg['color_main']}08;">
                  <svg class="w-16 h-16 mb-4" style="color: {cfg['color_main']};" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M15.91 11.672a.375.375 0 010 .656l-5.603 3.113a.375.375 0 01-.557-.328V8.887c0-.286.307-.466.557-.327l5.603 3.112z"/><path stroke-linecap="round" stroke-linejoin="round" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
                  <p class="text-sm font-semibold uppercase tracking-wider" style="color: {cfg['color_main']};">Em breve</p>
                  <p class="text-slate-600 text-sm mt-2 max-w-md">Vídeo da palestra disponível em breve no canal NTICS Projetos.</p>
                </div>'''
        else:
            thumb = video_palestra.get("thumbnail_url") or f"https://img.youtube.com/vi/{yt_id}/maxresdefault.jpg"
            video_inner = f'''<a href="https://youtu.be/{yt_id}" target="_blank" rel="noopener" class="block group relative aspect-video rounded-2xl overflow-hidden shadow-xl">
                  <img src="{thumb}" alt="{v_titulo}" class="absolute inset-0 w-full h-full object-cover group-hover:scale-105 transition duration-500">
                  <div class="absolute inset-0 bg-black/30 group-hover:bg-black/40 transition flex items-center justify-center">
                    <div class="w-20 h-20 rounded-full bg-white/95 flex items-center justify-center shadow-2xl group-hover:scale-110 transition">
                      <svg class="w-8 h-8 ml-1" style="color: {cfg['color_main']};" fill="currentColor" viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg>
                    </div>
                  </div>
                </a>'''
        video_palestra_html = f'''
  <!-- ═══════════════ VÍDEO PALESTRA ═══════════════ -->
  <section id="video-palestra" class="py-20 lg:py-28 px-6 lg:px-10 bg-white">
    <div class="max-w-4xl mx-auto">
      <div class="text-center mb-10 reveal">
        <div class="inline-flex items-center gap-2 px-4 py-2 rounded-full text-xs font-bold uppercase tracking-[0.2em] mb-6" style="background: {cfg['color_main']}15; color: {cfg['color_main']};">
          <span class="w-2 h-2 rounded-full" style="background: {cfg['color_main']};"></span>
          Vídeo
        </div>
        <h2 class="font-display text-3xl sm:text-4xl lg:text-5xl font-extrabold text-main" style="letter-spacing: -0.03em;">{v_titulo}</h2>
        <p class="text-slate-600 mt-4 text-base">{v_sub}</p>
      </div>
      <div class="reveal">{video_inner}</div>
    </div>
  </section>'''

    # Galeria HTML — padrao masonry repetido a cada 6 (destaque-grande + 4 pequenas + banner largo)
    base_layouts = ["md:col-span-2 md:row-span-2","","","","md:col-span-2",""]
    gal_items = "".join([
        f'''<div class="{base_layouts[i % 6]} aspect-[4/3] md:aspect-auto rounded-2xl overflow-hidden shadow-md hover:shadow-2xl transition">
             <img src="FOTOS/galeria_{i+1}.jpg" alt="" loading="lazy" class="w-full h-full object-cover hover:scale-105 transition duration-700">
           </div>'''
        for i in range(len(galeria))
    ])

    html = f"""<!DOCTYPE html>
<html lang="pt-BR" class="scroll-smooth">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
  <meta name="description" content="{title} — {subtitle}">
  <script src="https://cdn.tailwindcss.com"></script>
  <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;800;900&family=Space+Grotesk:wght@500;600;700&display=swap" rel="stylesheet">
  <style>
    :root {{ --main: {cfg['color_main']}; --dark: {cfg['color_dark']}; }}
    body {{ font-family: 'Poppins', system-ui, sans-serif; }}
    .font-display {{ font-family: 'Space Grotesk', sans-serif; }}
    .bg-main {{ background-color: var(--main); }}
    .bg-dark {{ background-color: var(--dark); }}
    .text-main {{ color: var(--main); }}
    .hero-overlay {{ background: linear-gradient(135deg, {cfg['color_dark']}cc 0%, {cfg['color_main']}88 50%, {cfg['color_dark']}dd 100%); }}
    .reveal, .reveal-left, .reveal-right {{ opacity: 0; transition: all 0.8s cubic-bezier(0.22,1,0.36,1); }}
    .reveal {{ transform: translateY(30px); }}
    .reveal-left {{ transform: translateX(-40px); }}
    .reveal-right {{ transform: translateX(40px); }}
    .reveal.visible, .reveal-left.visible, .reveal-right.visible {{ opacity: 1; transform: none; }}
    .site-header {{ transition: padding 0.3s ease, box-shadow 0.3s ease; }}
    .site-header.scrolled {{ padding-top: 0.5rem; padding-bottom: 0.5rem; box-shadow: 0 6px 24px rgba(0,0,0,0.15); }}
  </style>
</head>
<body class="bg-white text-slate-800">
  <div id="scroll-progress" style="position: fixed; top: 0; left: 0; height: 3px; background: var(--main); z-index: 100; width: 0%; transition: width 0.1s linear;"></div>

  <!-- HEADER -->
  <header class="site-header bg-main text-white sticky top-0 z-50 shadow-lg">
    <div class="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
      <a href="#" class="flex items-center gap-3">
        <img src="LOGOS/{cfg['logo']}" alt="{title}" class="h-12 bg-white rounded-lg p-1.5">
      </a>
      <nav class="hidden md:flex gap-8 text-sm font-semibold uppercase tracking-wide">
        <a href="#sobre" class="hover:opacity-80 transition">Sobre</a>
        {'<a href="#cidades" class="hover:opacity-80 transition">Cidades</a>' if cidades else ''}
        <a href="#atividades" class="hover:opacity-80 transition">Atividades</a>
        {'<a href="#cronograma" class="hover:opacity-80 transition">Onde Estamos</a>' if cronograma else ''}
        <a href="#galeria" class="hover:opacity-80 transition">Galeria</a>
        <a href="#democratizacao" class="hover:opacity-80 transition">Democratização</a>
      </nav>
    </div>
  </header>

  <!-- HERO -->
  <section class="relative min-h-[80vh] flex items-center justify-center overflow-hidden">
    <img src="FOTOS/hero_bg.jpg" alt="{title}" class="absolute inset-0 w-full h-full object-cover">
    <div class="absolute inset-0 hero-overlay"></div>
    <div class="relative z-10 text-center text-white px-6 max-w-4xl">
      <img src="LOGOS/{cfg['logo']}" alt="Logo {title}" class="h-32 md:h-40 mx-auto mb-8 bg-white/95 rounded-2xl p-4 shadow-2xl">
      <h1 class="font-display text-5xl md:text-7xl font-black mb-4 drop-shadow-2xl" style="letter-spacing: -0.03em;">{title}</h1>
      <p class="text-xl md:text-2xl font-light">{subtitle}</p>
    </div>
    <div class="absolute bottom-0 left-0 right-0 z-10">
      <svg viewBox="0 0 1440 80" fill="none" class="w-full" preserveAspectRatio="none"><path d="M0 40C240 70 480 10 720 40C960 70 1200 10 1440 40V80H0V40Z" fill="white"/></svg>
    </div>
  </section>

  <!-- SOBRE -->
  <section id="sobre" class="py-20 lg:py-28 px-6 lg:px-10">
    <div class="max-w-5xl mx-auto grid md:grid-cols-2 gap-12 items-center">
      <div class="reveal-left">
        <div class="rounded-3xl overflow-hidden shadow-xl aspect-square bg-slate-100">
          <img src="FOTOS/sobre.jpg" alt="{title}" class="w-full h-full object-cover" loading="lazy">
        </div>
      </div>
      <div class="reveal-right">
        <div class="inline-flex items-center gap-2 px-4 py-2 rounded-full text-xs font-bold uppercase tracking-[0.2em] mb-6" style="background: var(--main); color: white;">
          <span class="w-2 h-2 rounded-full bg-white"></span>
          Sobre o Projeto
        </div>
        <h2 class="font-display text-3xl md:text-4xl lg:text-5xl font-extrabold mb-6 text-main" style="letter-spacing: -0.02em;">{title}</h2>
        {sobre_text_html}
      </div>
    </div>
  </section>
{cidades_html}
  <!-- ATIVIDADES -->
  <section id="atividades" class="py-20 lg:py-28 px-6 lg:px-10 bg-slate-50">
    <div class="max-w-6xl mx-auto">
      <div class="text-center mb-20 reveal">
        <div class="inline-flex items-center gap-2 px-4 py-2 rounded-full text-xs font-bold uppercase tracking-[0.2em] mb-6" style="background: {cfg['color_main']}15; color: {cfg['color_main']};">
          <span class="w-2 h-2 rounded-full" style="background: {cfg['color_main']};"></span>
          Programação
        </div>
        <h2 class="font-display text-3xl sm:text-4xl lg:text-5xl font-extrabold text-main" style="letter-spacing: -0.03em;">Atividades do Projeto</h2>
      </div>
      <div class="space-y-24 lg:space-y-28">{"".join(ativ_html_parts)}
      </div>
    </div>
  </section>
{cronograma_html}
  <!-- GALERIA -->
  <section id="galeria" class="py-20 lg:py-28 px-6 lg:px-10">
    <div class="max-w-6xl mx-auto">
      <div class="text-center mb-16 reveal">
        <div class="inline-flex items-center gap-2 px-4 py-2 rounded-full text-xs font-bold uppercase tracking-[0.2em] mb-6 bg-slate-100 text-slate-600">
          <span class="w-2 h-2 rounded-full bg-slate-400"></span>
          Registros
        </div>
        <h2 class="font-display text-3xl sm:text-4xl lg:text-5xl font-extrabold text-main" style="letter-spacing: -0.03em;">Galeria do Projeto</h2>
      </div>
      <div class="grid grid-cols-2 md:grid-cols-3 gap-4 lg:gap-6">{gal_items}</div>
    </div>
  </section>

  <!-- DEMOCRATIZACAO -->
  <section id="democratizacao" class="py-20 lg:py-28 px-6 lg:px-10 bg-main text-white">
    <div class="max-w-6xl mx-auto">
      <div class="text-center mb-16 reveal">
        <div class="inline-flex items-center gap-2 px-4 py-2 rounded-full text-xs font-bold uppercase tracking-[0.2em] mb-6 bg-white/15">
          <span class="w-2 h-2 rounded-full bg-white"></span>
          Acessibilidade
        </div>
        <h2 class="font-display text-3xl sm:text-4xl lg:text-5xl font-extrabold" style="letter-spacing: -0.03em;">Democratização de Acesso</h2>
        <p class="text-lg md:text-xl opacity-90 mt-4 max-w-3xl mx-auto">{democratizacao_text or 'Como o projeto garante que educação e cultura cheguem a todas e todos'}</p>
      </div>
      <div class="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div class="bg-white/10 backdrop-blur rounded-2xl p-6 reveal">
          <h4 class="font-bold text-lg mb-2">Escolas Públicas</h4>
          <p class="text-sm opacity-90">Realização gratuita em escolas públicas, com parceria com Secretarias Municipais de Educação.</p>
        </div>
        <div class="bg-white/10 backdrop-blur rounded-2xl p-6 reveal">
          <h4 class="font-bold text-lg mb-2">Metodologia Prática</h4>
          <p class="text-sm opacity-90">Baseada em aprendizagem ativa e projetos, acessível aos públicos atendidos.</p>
        </div>
        <div class="bg-white/10 backdrop-blur rounded-2xl p-6 reveal">
          <h4 class="font-bold text-lg mb-2">Sustentabilidade</h4>
          <p class="text-sm opacity-90">Integração entre educação, cultura, tecnologia e sustentabilidade.</p>
        </div>
        <div class="bg-white/10 backdrop-blur rounded-2xl p-6 reveal">
          <h4 class="font-bold text-lg mb-2">Conteúdo Digital</h4>
          <p class="text-sm opacity-90">Palestra virtual para professores ampliando o alcance e continuidade pedagógica.</p>
        </div>
      </div>
    </div>
  </section>

  {video_palestra_html}
  <!-- REGUA -->
  <section class="py-16 lg:py-20 px-6 lg:px-10 bg-white">
    <div class="max-w-6xl mx-auto reveal">
      <img src="REGUAS/{cfg['regua']}" alt="Régua de patrocinadores" class="w-full h-auto">
    </div>
  </section>

  <!-- FOOTER -->
  <footer class="bg-dark text-white py-12 px-6">
    <div class="max-w-6xl mx-auto flex flex-col md:flex-row items-center justify-between gap-6">
      <div class="flex items-center gap-4">
        <img src="LOGOS/{cfg['logo']}" alt="{title}" class="h-14 bg-white/10 rounded-lg p-2">
        <div>
          <p class="font-display font-bold text-lg">{title}</p>
          <p class="text-sm text-white/70">Realização NTICS Projetos</p>
        </div>
      </div>
      <p class="text-sm text-white/60">© 2026 {title}. Todos os direitos reservados.</p>
    </div>
  </footer>

  <script>
    const observer = new IntersectionObserver((entries) => {{
      entries.forEach(entry => {{
        if (entry.isIntersecting) {{ entry.target.classList.add('visible'); observer.unobserve(entry.target); }}
      }});
    }}, {{ threshold: 0.15, rootMargin: '0px 0px -40px 0px' }});
    document.querySelectorAll('.reveal, .reveal-left, .reveal-right').forEach(el => observer.observe(el));
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
    out_path = site_dir / "site.html"
    # Backup if not already
    bak = out_path.with_suffix(".html.bak2")
    if not bak.exists() and out_path.exists():
        bak.write_text(out_path.read_text(encoding="utf-8"), encoding="utf-8")
    out_path.write_text(html, encoding="utf-8")
    print(f"[{site_id}] {len(content.get('atividades',[]))} atividades, {len(cidades)} cidades, {len(galeria)} galeria  ✓")

def main():
    for sid, cfg in SITES.items():
        try:
            build_site(sid, cfg)
        except Exception as e:
            print(f"[{sid}] ERROR: {e}")
            import traceback; traceback.print_exc()

if __name__ == "__main__":
    main()
