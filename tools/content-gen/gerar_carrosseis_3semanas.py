"""
gerar_carrosseis_3semanas.py
Gera carrosseis de noticias ESG para S03, S04, S05.
Usa as 18 noticias em .tmp/noticias_esg_parsed.json (6 por semana).

📚 Ref: workflows/marketing/referencia/leonardo_ai_core.md — consulte em caso de erro ou
dúvida sobre payloads, modos, erros conhecidos.
"""
import json, os, sys, time
from pathlib import Path
import requests
from dotenv import load_dotenv

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

load_dotenv()
LEO_KEY = os.getenv("LEONARDO_API_KEY")
BASE_V2 = "https://cloud.leonardo.ai/api/rest/v2"
BASE_V1 = "https://cloud.leonardo.ai/api/rest/v1"

# ─── Cores dos badges por categoria ──────────────────────────────────────────
BADGE_CORES = {
    "ESTRATEGIA CORPORATIVA": "green",
    "INFRAESTRUTURA": "green",
    "RECURSOS HIDRICOS": "blue",
    "EDUCACAO": "yellow",
    "COOPERACAO GLOBAL": "purple",
    "FINANCAS VERDES": "green",
    "ENERGIA": "orange",
    "BIODIVERSIDADE": "green",
    "TECNOLOGIA": "teal",
}

ICONES = {
    "ESTRATEGIA CORPORATIVA": "a green shield with a white checkmark",
    "INFRAESTRUTURA": "a construction crane silhouette",
    "RECURSOS HIDRICOS": "a blue water drop",
    "EDUCACAO": "an open book with a graduation cap",
    "COOPERACAO GLOBAL": "two hands clasped in solidarity",
    "FINANCAS VERDES": "a green leaf growing from gold coins",
    "ENERGIA": "a bright glowing sun with solar rays",
    "BIODIVERSIDADE": "a green leaf with veins",
    "TECNOLOGIA": "a glowing green circuit board leaf",
}

CAPAS = {
    "S03": {
        "cena": "a diverse group of corporate sustainability professionals reviewing ESG impact reports together around a modern office table with large windows overlooking a green city",
        "titulo": "6 AVANCOS EM SUSTENTABILIDADE QUE MARCARAM ESTA SEMANA",
    },
    "S04": {
        "cena": "a Brazilian environmental researcher in a field measuring water quality in a clean river surrounded by Atlantic Forest vegetation",
        "titulo": "O LADO POSITIVO DO ESG QUE VOCE PRECISA CONHECER",
    },
    "S05": {
        "cena": "a group of community members and corporate volunteers celebrating the completion of a solar energy installation in a Brazilian favela, smiling and pointing at the panels",
        "titulo": "6 BOAS NOTICIAS SOBRE RESPONSABILIDADE SOCIAL DESTA SEMANA",
    },
}

CTA_PROMPT = (
    "A social media carousel final CTA card for Instagram 4:5 format. Clean solid dark teal "
    "005F73 background covering the entire card. The top 15 percent is empty dark teal space "
    "reserved for a logo. In the center of the card vertically large bold white sans-serif "
    "text reads: Siga para mais boas noticias toda semana. Below in smaller white text: "
    "@nticsprojetos. Below that in even smaller elegant white italic text: Inovacao Impacto "
    "e Regeneracao. At the very bottom edge flush with zero margin a thick prominent "
    "horizontal gradient stripe bar spanning full width approximately 2 percent of total "
    "height with smooth color flow from bright green to teal to magenta to orange. "
    "Minimalist professional design no images just elegant typography centered on solid "
    "dark teal background with generous empty space at the top."
)


def build_capa_prompt(semana):
    c = CAPAS[semana]
    return (
        f"A social media carousel cover card for Instagram 4:5 format. The top 60 percent is a "
        f"full-bleed hyperrealistic photograph of {c['cena']}, "
        f"candid unposed moment, Canon EOS R5 35mm lens, natural warm sunlight, photojournalistic "
        f"documentary style, visible film grain ISO 800, looks exactly like a real photograph, "
        f"NOT AI generated NOT illustration. "
        f"From 60 to 80 percent a smooth dark gradient overlay transitions from transparent to "
        f"solid dark teal 005F73. "
        f"From 80 to 98 percent over the solid dark teal background centered large bold white "
        f"sans-serif text reads: {c['titulo']}. "
        f"At the very bottom edge flush with zero margin a thick prominent horizontal gradient "
        f"stripe bar spanning full width approximately 2 percent of total height with smooth "
        f"color flow from bright green to teal to magenta to orange. "
        f"No logo no branding text. Professional editorial cover design."
    )


def build_noticia_prompt(n):
    cat = n["categoria"]
    cor = BADGE_CORES.get(cat, "green")
    icone = ICONES.get(cat, "a green leaf")
    titulo = n["titulo"].upper()
    resumo = n["resumo"][:180]
    fonte = n["fonte"]
    keyword = n["keyword_imagem"]
    return (
        f"A social media carousel card Instagram 4:5 format. The top 55 percent is a full-bleed "
        f"hyperrealistic photograph of a real candid scene related to {keyword}, "
        f"documentary photojournalism style, Canon 50mm f1.4 natural bokeh warm tones, visible "
        f"film grain ISO 800, natural imperfect lighting, NOT AI generated NOT illustration. "
        f"In the upper right corner overlapping the photo a circular bubble icon approximately 12 "
        f"percent width showing {icone}, surrounded by a glowing golden ring with soft amber light. "
        f"From 55 to 72 percent a smooth dark gradient overlay transitions from transparent to "
        f"solid dark teal 005F73. "
        f"From 72 to 75 percent a small rounded {cor} badge with white text {cat}. "
        f"From 75 to 88 percent large bold white uppercase sans-serif headline with key words "
        f"in yellow F5B800: {titulo}. "
        f"From 88 to 96 percent smaller white sans-serif body text: {resumo}. "
        f"At 97 percent tiny white text: Fonte: {fonte}. "
        f"At the very bottom edge flush a thick gradient stripe bar from green 3DAA35 to teal "
        f"00A5B8 to pink D41A6A to orange E86428. Professional editorial card."
    )


def start_gen(prompt):
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": f"Bearer {LEO_KEY}",
    }
    payload = {
        "model": "nano-banana-2",
        "parameters": {
            "prompt": prompt,
            "width": 1856,
            "height": 2304,
            "quantity": 1,
            "prompt_enhance": "OFF",
        },
        "public": False,
    }
    r = requests.post(f"{BASE_V2}/generations", headers=headers, json=payload, timeout=30)
    if not r.ok:
        raise RuntimeError(f"{r.status_code}: {r.text[:200]}")
    data = r.json()
    # extract ID
    for key in ["generationId", "id"]:
        if data.get(key):
            return data[key]
    for v in data.values():
        if isinstance(v, dict):
            for k in ["generationId", "id"]:
                if v.get(k):
                    return v[k]
    raise RuntimeError(f"No ID in: {str(data)[:200]}")


def poll_gen(gen_id, max_wait=180):
    headers = {"accept": "application/json", "authorization": f"Bearer {LEO_KEY}"}
    url = f"{BASE_V1}/generations/{gen_id}"
    waited = 0
    while waited < max_wait:
        r = requests.get(url, headers=headers, timeout=30)
        r.raise_for_status()
        job = r.json().get("generations_by_pk", {})
        status = job.get("status", "")
        if status == "COMPLETE":
            imgs = job.get("generated_images", [])
            if imgs:
                return imgs[0]["url"]
            raise RuntimeError("Complete but no images")
        if status == "FAILED":
            raise RuntimeError(f"FAILED: {job}")
        time.sleep(8)
        waited += 8
        print(f"    ...{waited}s", flush=True)
    raise TimeoutError(f"Timeout {max_wait}s")


def download(url, path):
    r = requests.get(url, timeout=60)
    r.raise_for_status()
    path.write_bytes(r.content)


def build_descricao(semana, noticias_semana):
    n_list = "\n".join([f"{i+1}. {n['titulo']} — Fonte: {n['fonte']}" for i, n in enumerate(noticias_semana)])
    caption_ig = (
        f"Esta semana, 6 avancos em sustentabilidade e responsabilidade social que merecem ser celebrados! "
        f"Salve este carrossel para nao esquecer:\n\n"
        + "\n".join([f"✅ {n['titulo']}" for n in noticias_semana]) +
        f"\n\nO mundo avanca quando empresas e pessoas escolhem o caminho certo. "
        f"Siga @nticsprojetos para mais boas noticias toda semana!\n\n"
        f"#ESG #Sustentabilidade #ResponsabilidadeSocial #ImpactoSocial #ODS #NTICS"
    )
    caption_li = (
        f"6 avancos em ESG e sustentabilidade desta semana:\n\n"
        + "\n".join([f"{i+1}. {n['titulo']}" for i, n in enumerate(noticias_semana)]) +
        f"\n\nO que mais chamou sua atencao? Compartilhe nos comentarios.\n\n"
        f"#ESG #Sustentabilidade #ResponsabilidadeSocial #NTICS"
    )
    return f"""========================================
CARROSSEL: BOAS NOTICIAS ESG
Semana {semana}
========================================

--- CAPTION INSTAGRAM ---
{caption_ig}

--- CAPTION LINKEDIN ---
{caption_li}

--- NOTICIAS (para comentario fixo) ---
{n_list}

--- ORDEM DOS CARDS ---
01-capa.jpg — Capa: {CAPAS[semana]['titulo']}
""" + "\n".join([f"0{i+2}-{n['categoria'].lower().replace(' ', '-')}.jpg — {n['titulo']}" for i, n in enumerate(noticias_semana)]) + "\n08-cta.jpg — CTA: Siga @nticsprojetos\n"


def main():
    # Load news
    with open(".tmp/noticias_esg_parsed.json", "r", encoding="utf-8") as f:
        todas = json.load(f)

    semanas = {
        "S03": todas[0:6],
        "S04": todas[6:12],
        "S05": todas[12:18],
    }

    for semana, noticias_semana in semanas.items():
        print(f"\n{'='*50}")
        print(f"SEMANA {semana}")
        print(f"{'='*50}")

        out_dir = Path(f".tmp/marketing/carrosseis/noticias/{semana}")
        out_dir.mkdir(parents=True, exist_ok=True)

        # Build prompts
        prompts = {"01-capa": build_capa_prompt(semana)}
        for i, n in enumerate(noticias_semana):
            slug = n["categoria"].lower().replace(" ", "-")
            key = f"0{i+2}-{slug}"
            prompts[key] = build_noticia_prompt(n)
        prompts["08-cta"] = CTA_PROMPT

        # Submit all generations
        jobs = {}
        for name, prompt in prompts.items():
            print(f"  >> Starting: {name}", flush=True)
            try:
                gen_id = start_gen(prompt)
                jobs[name] = gen_id
                print(f"     ID: {gen_id}", flush=True)
                time.sleep(1)  # small delay between submissions
            except Exception as e:
                print(f"     FAILED to start: {e}", flush=True)

        if not jobs:
            print(f"  No jobs for {semana}")
            continue

        print(f"\n  Waiting 60s for {len(jobs)} generations...", flush=True)
        time.sleep(60)

        # Poll and download
        results = []
        for name, gen_id in jobs.items():
            print(f"  >> Polling: {name}", flush=True)
            try:
                img_url = poll_gen(gen_id)
                path = out_dir / f"{name}.jpg"
                download(img_url, path)
                print(f"     SAVED: {path}", flush=True)
                results.append({"name": name, "ok": True, "path": str(path)})
            except Exception as e:
                print(f"     FAILED: {e}", flush=True)
                results.append({"name": name, "ok": False, "error": str(e)})

        # Save descricao.txt
        desc = build_descricao(semana, noticias_semana)
        (out_dir / "descricao.txt").write_text(desc, encoding="utf-8")

        ok = sum(1 for r in results if r["ok"])
        print(f"\n  {semana}: {ok}/{len(prompts)} imagens geradas → {out_dir}")

    print("\n\nCONCLUIDO!")


if __name__ == "__main__":
    main()
