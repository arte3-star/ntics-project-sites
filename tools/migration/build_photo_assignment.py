"""Combina LAION (estetica) + Sonnet (semantica) e atribui fotos a slots de cada site."""
import csv
import json
from pathlib import Path

ROOT = Path(r"g:\O meu disco\AUTOMAÇÕES")
THUMBS = ROOT / "output" / "thumbs"
SRC_POOLS = ROOT / "SecondBrain" / "banco-fotos"
SONNET = ROOT / "output" / "rankings" / "sonnet"
LAION = ROOT / "output" / "rankings"

POOLS = {
    "robotica":  ("5. ROBÓTICA NAS ESCOLAS",         "laion_5._ROBÓTICA_NAS_ESCOLAS.csv",   "robotica.json"),
    "pec":       ("2. PEC   PIE   PED/PEC",          "laion_2._PEC_PIE_PED_PEC.csv",        "pec.json"),
    "pie":       ("2. PEC   PIE   PED/PIE",          "laion_2._PEC_PIE_PED_PIE.csv",        "pie.json"),
    "culinaria": ("7. CULINÁRIA SUSTENTÁVEL",        "laion_7._CULINÁRIA_SUSTENTÁVEL.csv",  "culinaria.json"),
    "ofoto":     ("OFICINA DE FOTOGRAFIA",           "laion_OFICINA_DE_FOTOGRAFIA.csv",     "oficina_foto.json"),
}

def load_pool(key):
    src_folder, laion_csv, sonnet_json = POOLS[key]
    # Load LAION
    laion = {}
    with open(LAION / laion_csv, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            # score column name varies; find first numeric
            fname = row.get("filename") or row.get("file") or list(row.values())[0]
            score_col = next((c for c in row if "score" in c.lower() or "laion" in c.lower()), list(row.keys())[-1])
            stem = Path(fname).stem
            laion[stem] = float(row[score_col])
    # Load Sonnet
    sonnet = {}
    raw = json.loads((SONNET / sonnet_json).read_text(encoding="utf-8"))
    for entry in raw:
        stem = Path(entry["file"]).stem
        sonnet[stem] = entry
    # Resolve original paths from melhores-fotos (match by stem, allow different extension)
    src_dir = SRC_POOLS / src_folder
    originals = {}
    for f in src_dir.rglob("*"):
        if f.suffix.lower() not in {".jpg",".jpeg",".png",".webp"}: continue
        originals[f.stem] = f
    # Merge
    merged = []
    for stem, son in sonnet.items():
        merged.append({
            "stem": stem,
            "source": str(originals.get(stem, "")),
            "laion": laion.get(stem, 5.0),
            "caption": son["caption"],
            "scene": son["scene"],
            "activity_match": son["activity_match"],
            "hero_score": son["hero_score"],
            "galeria_score": son["galeria_score"],
            "quality": son["quality_issues"],
        })
    return merged

def score_for_slot(p, want_tags, mode="hero"):
    """Score photo for slot. Higher = better match."""
    if p["quality"] == "screenshot": return -1000
    # Semantic match bonus
    tag_hit = any(t in p["activity_match"] for t in want_tags)
    tag_bonus = 20 if tag_hit else 0
    base_score = p["hero_score"] if mode == "hero" else p["galeria_score"]
    laion_bonus = (p["laion"] - 4.0) * 2  # 4.0 -> 0, 6.0 -> 4
    return base_score + tag_bonus * 0.5 + laion_bonus

def pick(pool, want_tags, mode="hero", exclude=None, n=1):
    exclude = exclude or set()
    scored = [(score_for_slot(p, want_tags, mode), p) for p in pool if p["stem"] not in exclude]
    scored.sort(key=lambda x: -x[0])
    return [p for _, p in scored[:n]]

# Site configs: slot_name -> (pool_key, want_tags, mode)
SITES = {
    "116": {
        "dir": "116. CULTURA ROBÓTICA (ÁSTER)",
        "slots": [
            ("hero",        "robotica", ["apresentacao_teatro","feira","palestra"], "hero"),
            ("atividade_1", "robotica", ["workshop_teorico","oficina_pratica","palestra"], "hero"),
            ("atividade_2", "robotica", ["oficina_pratica"], "hero"),
            ("atividade_3", "robotica", ["oficina_artes","oficina_pratica"], "hero"),
            ("atividade_4", "robotica", ["feira","apresentacao_teatro"], "hero"),
            ("atividade_5", "robotica", ["apresentacao_teatro","feira"], "hero"),
            ("atividade_6", "robotica", ["palestra"], "hero"),
            ("atividade_7", "robotica", ["apresentacao_teatro"], "hero"),
        ],
        "galeria_n": 6,
        "galeria_pool": "robotica",
    },
    "117": {
        "dir": "117. TEATRO E OFICINA ROBÓTICA 4ED (WHIRLPOOL)",
        "slots": [
            ("hero",        "robotica", ["apresentacao_teatro","feira"], "hero"),
            ("atividade_1", "robotica", ["workshop_teorico","palestra"], "hero"),
            ("atividade_2", "robotica", ["oficina_pratica","oficina_artes"], "hero"),
            ("atividade_3", "robotica", ["feira","apresentacao_teatro"], "hero"),
            ("atividade_4", "robotica", ["apresentacao_teatro","feira"], "hero"),
            ("atividade_5", "robotica", ["grupo_posando","palestra"], "hero"),
            ("atividade_6", "robotica", ["palestra","workshop_teorico"], "hero"),
        ],
        "galeria_n": 6,
        "galeria_pool": "robotica",
    },
    "119": {
        "dir": "119. PEC EU FAÇO PARTE 2ªED (SYLVAMO)",
        "slots": [
            ("hero",        "pec", ["palestra_sensibilizacao","oficina_problemas"], "hero"),
            ("atividade_1", "pec", ["formacao_professores"], "hero"),
            ("atividade_2", "pec", ["palestra_sensibilizacao"], "hero"),
            ("atividade_3", "pec", ["oficina_problemas","oficina_criador"], "hero"),
            ("atividade_4", "ofoto", ["workshop_fotografia"], "hero"),
            ("atividade_5", "pec", ["atividade_artes_plasticas","oficina_criador"], "hero"),
            ("atividade_6", "pec", ["palestra_sensibilizacao"], "hero"),
        ],
        "galeria_n": 6,
        "galeria_pool": "pec",
    },
    "124": {
        "dir": "124. EXPOSIÇÃO - GASTRONOMIA TAMBÉM É ARTE (COMPAGAS)",
        "slots": [
            ("hero",        "culinaria", ["aula_culinaria"], "hero"),
            ("atividade_1", "culinaria", ["exposicao_gastronomica"], "hero"),
            ("atividade_2", "culinaria", ["aula_culinaria"], "hero"),
            ("atividade_3", "culinaria", ["aula_culinaria","palestra_virtual"], "hero"),
            ("atividade_4", "ofoto", ["workshop_fotografia"], "hero"),
            ("atividade_5", "culinaria", ["palestra_virtual","aula_culinaria"], "hero"),
        ],
        "galeria_n": 6,
        "galeria_pool": "culinaria",
    },
    "125": {
        "dir": "125. EXPOSIÇÃO - GASTRONOMIA TAMBÉM É ARTE 2ED (GRU)",
        "slots": [
            ("hero",        "culinaria", ["aula_culinaria"], "hero"),
            ("atividade_1", "culinaria", ["exposicao_gastronomica"], "hero"),
            ("atividade_2", "culinaria", ["aula_culinaria"], "hero"),
            ("atividade_3", "culinaria", ["aula_culinaria","palestra_virtual"], "hero"),
            ("atividade_4", "ofoto", ["workshop_fotografia"], "hero"),
            ("atividade_5", "culinaria", ["palestra_virtual","aula_culinaria"], "hero"),
        ],
        "galeria_n": 6,
        "galeria_pool": "culinaria",
    },
    "127G": {
        "dir": "127. PIE EMPREENDEDORISMO É ARTE 2ED (GRU)",
        "slots": [
            ("hero",        "pie", ["palestra_abertura"], "hero"),
            ("atividade_1", "pie", ["palestra_abertura"], "hero"),
            ("atividade_2", "pie", ["formacao_professores"], "hero"),
            ("atividade_3", "pie", ["oficina_eu_criador"], "hero"),
            ("atividade_4", "pie", ["oficina_problemas_ideias"], "hero"),
            ("atividade_5", "pie", ["oficina_ideia_voz"], "hero"),
            ("atividade_6", "pie", ["palestra_virtual","palestra_abertura"], "hero"),
        ],
        "galeria_n": 6,
        "galeria_pool": "pie",
    },
    "127S": {
        "dir": "127. PIE EMPREENDEDORISMO É ARTE 2ED (SOTREQ)",
        "slots": [
            ("hero",        "pie", ["palestra_abertura"], "hero"),
            ("atividade_1", "pie", ["palestra_abertura"], "hero"),
            ("atividade_2", "pie", ["formacao_professores"], "hero"),
            ("atividade_3", "pie", ["oficina_eu_criador"], "hero"),
            ("atividade_4", "pie", ["oficina_problemas_ideias"], "hero"),
            ("atividade_5", "pie", ["oficina_ideia_voz"], "hero"),
            ("atividade_6", "pie", ["palestra_virtual","palestra_abertura"], "hero"),
        ],
        "galeria_n": 6,
        "galeria_pool": "pie",
    },
}

def main():
    pools = {k: load_pool(k) for k in POOLS}
    output = {}
    for site_id, cfg in SITES.items():
        used = set()  # unique per site
        assigned = []
        for slot_name, pool_key, tags, mode in cfg["slots"]:
            candidates = pick(pools[pool_key], tags, mode, exclude=used, n=1)
            if candidates:
                p = candidates[0]
                used.add(p["stem"])
                assigned.append({"slot": slot_name, "pool": pool_key, "tags": tags, **p})
        # Galeria
        galeria_pool = pools[cfg["galeria_pool"]]
        gcands = pick(galeria_pool, [], mode="galeria", exclude=used, n=cfg["galeria_n"])
        for i, p in enumerate(gcands, 1):
            used.add(p["stem"])
            assigned.append({"slot": f"galeria_{i}", "pool": cfg["galeria_pool"], "tags": [], **p})
        output[site_id] = {"dir": cfg["dir"], "assignments": assigned}
    out_path = ROOT / "output" / "rankings" / "assignments.json"
    out_path.write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Saved {out_path}")
    # Summary table
    for site_id, data in output.items():
        print(f"\n=== {site_id} {data['dir']} ===")
        for a in data["assignments"]:
            print(f"  {a['slot']:14s} [{a['pool']:9s}] h={a['hero_score']} g={a['galeria_score']} L={a['laion']:.1f}  {a['caption'][:70]}")

if __name__ == "__main__":
    main()
