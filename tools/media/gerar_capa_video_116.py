"""
Gera 3 variações de capa de vídeo 9:16 para o projeto 116 Cultura Robótica (Áster).
Modelo: nano-banana-2, dimensões 1536x2752 (Medium 9:16).
"""

import os
import json
import time
import requests
import concurrent.futures
from pathlib import Path

API_KEY = os.environ.get("LEONARDO_API_KEY")
HEADERS = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

BASE = Path("g:/O meu disco/Claude-NTICS-Projetos")
OUTPUT_DIR = BASE / "output/marketing/carrosseis/projetos/116-cultura-robotica-aster/capa-video"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

PHOTO    = BASE / "SecondBrain/banco-fotos/5. ROBÓTICA NAS ESCOLAS/082_robotica-escolas_robotica_criancas-montando-kit-robotica-com-instrutor.jpg"

WIDTH, HEIGHT = 1536, 2752  # nano-banana-2, 9:16 Medium


def upload_image(path: Path) -> str:
    ext = path.suffix.lstrip(".")
    r = requests.post(
        "https://cloud.leonardo.ai/api/rest/v1/init-image",
        headers=HEADERS,
        json={"extension": ext},
    )
    r.raise_for_status()
    upload = r.json()["uploadInitImage"]
    init_id = upload["id"]
    fields = json.loads(upload["fields"])
    with open(path, "rb") as f:
        resp = requests.post(upload["url"], data=fields, files={"file": f})
    resp.raise_for_status()
    print(f"  Uploaded {path.name} -> {init_id}")
    return init_id


def make_guidance(ids):
    return {
        "image_reference": [
            {"image": {"id": iid, "type": "UPLOADED"}, "strength": "HIGH"}
            for iid in ids
        ]
    }


_BASE = (
    "Vertical 9:16 social media video cover, full bleed, no borders. "
    "Uses ONE reference image: children assembling robotics kit with instructor. "
    "SAFE ZONE RULE: top 25% and bottom 25% must remain free of text and logos. "
    "All text MUST be placed only in the MIDDLE 50% of the image (25% to 75%). "
    "BACKGROUND full bleed 0% to 100%: reference photo extends edge to edge. "
    "In the top 25% and bottom 25% zones apply soft gaussian blur overlay, "
    "slightly desaturated dreamy atmosphere, no text or elements whatsoever. "
)

PROMPTS = {
    "v1": (
        _BASE +
        "UPPER ZONE 25% to 48%: reference photo visible through soft blur, no text. "
        "SMOOTH GRADIENT TRANSITION at 48%: seamless blend from photo into solid dark green #367C2B below. "
        "TEXT ZONE 48% to 73%: solid dark green #367C2B background. All text centered strictly here. "
        "LARGE BOLD UPPERCASE white sans-serif two lines: CULTURA / ROBOTICA. "
        "Below: medium white text: Sidrolandia, Maracaju e Sao Gabriel recebem "
        "teatro, arte e robotica na escola publica. "
        "Highlight in bright yellow: Sao Gabriel, teatro, arte e robotica. "
        "BOTTOM MARGIN 73% to 75%: dark green #367C2B, empty. "
        "BOTTOM ZONE 75% to 100%: blurred photo background only, absolutely no text. "
        "No tricolor stripe. No logos."
    ),
    "v2": (
        _BASE +
        "UPPER ZONE 25% to 45%: reference photo visible through soft blur, no text. "
        "SMOOTH GRADIENT TRANSITION at 45%: seamless blend from photo into solid dark green #367C2B below. "
        "TEXT ZONE 45% to 73%: solid dark green #367C2B background. All text centered strictly here. "
        "Small white uppercase at top of zone: ASTER APRESENTA. "
        "LARGE BOLD UPPERCASE white sans-serif two lines: CULTURA / ROBOTICA. "
        "Below: medium white text: Teatro, arte e robotica chegam as escolas de "
        "Sidrolandia, Maracaju e Sao Gabriel. Uma jornada de 1.800 estudantes e 180 professores. "
        "Highlight in bright yellow: Sidrolandia, Maracaju e Sao Gabriel, 1.800 estudantes. "
        "BOTTOM MARGIN 73% to 75%: dark green #367C2B, empty. "
        "BOTTOM ZONE 75% to 100%: blurred photo background only, absolutely no text. "
        "No tricolor stripe. No logos."
    ),
    "v3": (
        _BASE +
        "UPPER ZONE 25% to 50%: reference photo visible through soft blur, no text. "
        "SMOOTH GRADIENT TRANSITION at 50%: seamless blend from photo into solid dark green #367C2B below. "
        "TEXT ZONE 50% to 73%: solid dark green #367C2B background. All text centered strictly here. "
        "LARGE BOLD UPPERCASE white sans-serif two lines: CULTURA / ROBOTICA. "
        "Thin bright yellow horizontal line separator below headline. "
        "Below: white body text: Quando teatro, arte e robotica entram na escola, "
        "o aprendizado ganha pratica e futuro. "
        "Highlight in bright yellow: teatro, arte e robotica. "
        "Below in bright yellow: Sidrolandia, Maracaju e Sao Gabriel — MS. "
        "BOTTOM MARGIN 73% to 75%: dark green #367C2B, empty. "
        "BOTTOM ZONE 75% to 100%: blurred photo background only, absolutely no text. "
        "No tricolor stripe. No logos."
    ),
}


def generate_version(version: str, guidance_ids: list) -> dict:
    prompt = PROMPTS[version]
    print(f"  Gerando {version} ({len(prompt)} chars)...")
    payload = {
        "model": "nano-banana-2",
        "parameters": {
            "prompt": prompt,
            "width": WIDTH,
            "height": HEIGHT,
            "quantity": 1,
            "prompt_enhance": "OFF",
            "guidances": make_guidance(guidance_ids),
        },
        "public": False,
    }
    r = requests.post(
        "https://cloud.leonardo.ai/api/rest/v2/generations",
        headers=HEADERS,
        json=payload,
    )
    r.raise_for_status()
    data = r.json()
    if isinstance(data, list):
        raise RuntimeError(f"API returned list (error?): {data}")
    gen_id = (
        (data.get("generate") or {}).get("generationId")
        or data.get("sdGenerationJob", {}).get("generationId")
        or data.get("generationId")
    )
    print(f"  {version} gen_id: {gen_id}")
    return {"version": version, "gen_id": gen_id}


def poll_generation(gen_id: str, timeout=300) -> str:
    url = f"https://cloud.leonardo.ai/api/rest/v1/generations/{gen_id}"
    deadline = time.time() + timeout
    while time.time() < deadline:
        r = requests.get(url, headers=HEADERS)
        r.raise_for_status()
        data = r.json().get("generations_by_pk", {})
        status = data.get("status", "")
        if status == "COMPLETE":
            imgs = data.get("generated_images", [])
            if imgs:
                return imgs[0]["url"]
        elif status == "FAILED":
            raise RuntimeError(f"Generation {gen_id} FAILED")
        time.sleep(8)
    raise TimeoutError(f"Generation {gen_id} timed out")


def download(url: str, path: Path):
    r = requests.get(url, timeout=60)
    r.raise_for_status()
    path.write_bytes(r.content)
    print(f"  Salvo: {path.name} ({len(r.content)//1024} KB)")


def main():
    if not API_KEY:
        raise EnvironmentError("LEONARDO_API_KEY não definida")

    print("=== Upload de referências ===")
    id_photo = upload_image(PHOTO)
    guidance_ids = [id_photo]

    print("\n=== Disparando 3 gerações em paralelo ===")
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:
        futures = {ex.submit(generate_version, v, guidance_ids): v for v in PROMPTS}
        jobs = [f.result() for f in concurrent.futures.as_completed(futures)]

    log_path = OUTPUT_DIR / "geracao.log"
    with open(log_path, "w", encoding="utf-8") as lf:
        json.dump(jobs, lf, indent=2, ensure_ascii=False)
    print(f"\ngen_ids salvos em {log_path}")

    print("\n=== Aguardando e baixando resultados ===")
    for job in jobs:
        v, gen_id = job["version"], job["gen_id"]
        print(f"  Polling {v}...")
        img_url = poll_generation(gen_id)
        job["url"] = img_url
        download(img_url, OUTPUT_DIR / f"capa-video-{v}.jpg")

    with open(log_path, "w", encoding="utf-8") as lf:
        json.dump(jobs, lf, indent=2, ensure_ascii=False)

    print("\n=== Concluído ===")
    for job in jobs:
        print(f"  {job['version']}: {OUTPUT_DIR / ('capa-video-' + job['version'] + '.jpg')}")


if __name__ == "__main__":
    main()
