"""
4 cards estilo v21-fullbleed-headline-topo para divulgacao do artigo
"Os 5 Sinais de Maturidade em Responsabilidade Social".

Mesmo padrao dos carrosseis NTICS: Leonardo nano-banana-2 com image_reference HIGH,
4:5 (1856x2304), prompt seguindo gramatica validada (zonas %, hex sem #, [YELLOW] tags).
Sem Pillow, sem HTML overlay. Leonardo gera tudo.
"""
import json, os, sys, time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import requests

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parents[2]
for line in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
    if "=" in line and not line.startswith("#"):
        k, v = line.split("=", 1); os.environ.setdefault(k.strip(), v.strip())

API_KEY = os.environ["LEONARDO_API_KEY"]
HEADERS = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
BASE_V1 = "https://cloud.leonardo.ai/api/rest/v1"
BASE_V2 = "https://cloud.leonardo.ai/api/rest/v2"

OUT_DIR = ROOT / "output/marketing/stories/artigo-5-sinais-responsabilidade-social/v21"
OUT_DIR.mkdir(parents=True, exist_ok=True)

W, H = 1856, 2304

# Layout v21 (mesmo em todos os cards - coerencia visual)
LAYOUT = ("Top 45 percent solid dark teal 005F73 background. "
          "Bottom 55 percent full-bleed reference photograph preserving exact natural colors, "
          "smooth gradient transition between teal and photo.")

FOOTER = ("Bottom edge: thin horizontal gradient stripe LEFT to RIGHT green 3DAA35 "
          "teal 00A5B8 pink D41A6A orange E86428. Portuguese accents preserved, "
          "no layout markers.")

PHOTO_DIR = ROOT / "output/marketing/artigos/antigo"

CARDS = {
    "1-capa": {
        "photo": PHOTO_DIR / "ntics-aluna-robo-cartolina.jpg",
        "role": (
            "very top center small rounded pill badge bright green 3DAA35 "
            "white bold uppercase ARTIGO NTICS NOTES. "
            "Massive monumental bold white uppercase sans-serif headline three lines "
            "filling teal area: OS 5 SINAIS / DE MATURIDADE / EM RESPONSABILIDADE SOCIAL. "
            "Small white body text over photo top edge semi-transparent dark strip: "
            "sua empresa está no [YELLOW]caminho certo[/YELLOW]?"
        ),
    },
    "2-gancho": {
        "photo": PHOTO_DIR / "ntics-passaporte-ods.jpg",
        "role": (
            "very top center small rounded pill badge bright green 3DAA35 "
            "white bold uppercase 5 SINAIS. "
            "Massive monumental bold white uppercase sans-serif headline two lines "
            "filling teal area: VOCÊ RECONHECE / ESSES 5 SINAIS? "
            "Small white body text over photo top edge semi-transparent dark strip: "
            "arrasta pra ver [YELLOW]cada sinal detalhado[/YELLOW] →"
        ),
    },
    "3-lista": {
        "photo": PHOTO_DIR / "ntics-vr-ods.jpg",
        "role": (
            "very top center small rounded pill badge bright green 3DAA35 "
            "white bold uppercase OS 5 SINAIS. "
            "Five vertical compact rows in teal area each row contains "
            "large bold yellow F5B800 two digit number followed by white bold uppercase sans-serif word: "
            "01 ESTRATÉGIA, 02 MÉTRICAS, 03 ENGAJAMENTO, 04 TERRITÓRIO, 05 APRENDIZADO. "
            "Small white body text over photo top edge semi-transparent dark strip: "
            "leia o [YELLOW]artigo completo[/YELLOW] →"
        ),
    },
    "4-cta": {
        "photo": PHOTO_DIR / "ntics-robotica-escola.jpg",
        "role": (
            "very top center small rounded pill badge bright green 3DAA35 "
            "white bold uppercase NTICS NOTES. "
            "Massive monumental bold white uppercase sans-serif headline two lines "
            "filling teal area: LEIA O ARTIGO / COMPLETO. "
            "Small white body text over photo top edge semi-transparent dark strip: "
            "acesse [YELLOW]ntics.com.br/artigos[/YELLOW]"
        ),
    },
}


def build_prompt(role_desc: str) -> str:
    return (
        "Social media carousel card, Instagram 4:5 format, edge to edge, no white borders. "
        "Uses uploaded reference image. "
        + LAYOUT + " " + role_desc + " " + FOOTER
    )


def upload_ref(photo: Path) -> str:
    r = requests.post(f"{BASE_V1}/init-image", headers=HEADERS,
                      json={"extension": "jpg"}, timeout=30)
    r.raise_for_status()
    up = r.json()["uploadInitImage"]
    fields = json.loads(up["fields"])
    with open(photo, "rb") as f:
        requests.post(up["url"], data=fields, files={"file": f}, timeout=90).raise_for_status()
    return up["id"]


def generate(prompt: str, ref_id: str) -> str:
    payload = {
        "model": "nano-banana-2",
        "parameters": {
            "width": W, "height": H,
            "prompt": prompt, "quantity": 1, "prompt_enhance": "OFF",
            "guidances": {"image_reference": [
                {"image": {"id": ref_id, "type": "UPLOADED"}, "strength": "HIGH"},
            ]},
        },
        "public": False,
    }
    r = requests.post(f"{BASE_V2}/generations", headers=HEADERS, json=payload, timeout=30)
    r.raise_for_status()
    data = r.json()
    return (data.get("generate", {}).get("generationId")
            or data.get("sdGenerationJob", {}).get("generationId"))


def poll(gen_id: str, timeout: int = 540) -> str:
    time.sleep(20); elapsed = 20
    while elapsed < timeout:
        time.sleep(10); elapsed += 10
        r = requests.get(f"{BASE_V1}/generations/{gen_id}", headers=HEADERS, timeout=30).json()
        d = r.get("generations_by_pk", {})
        if d.get("status") == "COMPLETE":
            imgs = d.get("generated_images", [])
            if imgs: return imgs[0]["url"]
        if d.get("status") == "FAILED":
            raise RuntimeError(f"FAILED {gen_id}")
    raise TimeoutError(gen_id)


def run_card(slug: str, card: dict):
    try:
        prompt = build_prompt(card["role"])
        print(f"  [{slug}] chars={len(prompt)} uploading photo...")
        ref_id = upload_ref(card["photo"])
        print(f"  [{slug}] submitting...")
        gen_id = generate(prompt, ref_id)
        print(f"  [{slug}] gen_id={gen_id[:12]}... polling")
        url = poll(gen_id)
        out = OUT_DIR / f"card-{slug}.jpg"
        out.write_bytes(requests.get(url, timeout=60).content)
        print(f"  [{slug}] OK -> {out.name} ({out.stat().st_size//1024} KB)")
        return slug, out, None
    except Exception as e:
        print(f"  [{slug}] FAIL: {e}")
        return slug, None, str(e)


def main():
    print(f"Gerando {len(CARDS)} cards v21 em {OUT_DIR}")
    print(f"Custo estimado: ${len(CARDS)*0.058:.2f}")
    results = []
    with ThreadPoolExecutor(max_workers=4) as ex:
        futures = {ex.submit(run_card, s, c): s for s, c in CARDS.items()}
        for fut in as_completed(futures):
            results.append(fut.result())
    print("\nSummary:")
    for slug, out, err in sorted(results):
        print(f"  {slug}: {'OK' if out else 'FAIL - ' + (err or '')}")


if __name__ == "__main__":
    main()
