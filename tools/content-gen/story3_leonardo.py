"""
Gera story-3 com pipeline hibrido:
  1. Leonardo nano-banana-2 gera BACKGROUND abstrato 1856x2304
  2. HTML+Playwright sobrepoe cards/texto em 1080x1920
"""
import os, json, time, sys
from pathlib import Path
import requests
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
for line in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
    if "=" in line and not line.startswith("#"):
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())

KEY = os.environ["LEONARDO_API_KEY"]
HEADERS = {"Authorization": f"Bearer {KEY}", "Content-Type": "application/json", "accept": "application/json"}
OUT = ROOT / "output/marketing/stories/artigo-5-sinais-responsabilidade-social"
BG = OUT / "story-3-bg-leonardo.jpg"

PROMPT = (
    "Abstract modern visualization of interconnected luminous nodes and floating geometric shapes, "
    "deep teal to dark-teal gradient background, subtle green and yellow accent glows forming an organic network pattern, "
    "sense of depth with soft depth-of-field blur, corporate-editorial aesthetic, full-bleed composition, "
    "photographic quality, subtle film grain. "
    "No text, no logos, no watermarks, no faces, no people."
)

# 1. Gerar
payload = {
    "model": "nano-banana-2",
    "parameters": {
        "prompt": PROMPT,
        "width": 1856, "height": 2304,
        "quantity": 1,
        "prompt_enhance": "OFF",
    },
    "public": False,
}
print("Submetendo geração nano-banana-2 1856x2304...")
r = requests.post("https://cloud.leonardo.ai/api/rest/v2/generations", headers=HEADERS, json=payload, timeout=60)
r.raise_for_status()
resp = r.json()
# Extrair generationId (localização pode variar entre v1 e v2)
gen_id = resp.get("generationId") or resp.get("sdGenerationJob", {}).get("generationId") or resp.get("id")
if not gen_id:
    print("RESP:", json.dumps(resp, indent=2)[:1000])
    sys.exit("Sem generationId")
print(f"  gen_id={gen_id}")

# 2. Poll
url = f"https://cloud.leonardo.ai/api/rest/v1/generations/{gen_id}"
for attempt in range(60):
    time.sleep(4)
    r = requests.get(url, headers=HEADERS, timeout=30)
    j = r.json()
    data = j.get("generations_by_pk") or {}
    status = data.get("status")
    print(f"  poll {attempt+1}: {status}")
    if status == "COMPLETE":
        imgs = data.get("generated_images") or []
        if not imgs:
            sys.exit("COMPLETE sem imagens")
        img_url = imgs[0]["url"]
        print(f"  URL: {img_url}")
        ib = requests.get(img_url, timeout=60).content
        OUT.mkdir(parents=True, exist_ok=True)
        BG.write_bytes(ib)
        print(f"  Saved: {BG}")
        break
    if status == "FAILED":
        sys.exit("Geração FAILED")
else:
    sys.exit("Timeout polling")

# 3. Verificar dimensoes e comprimir se grande
im = Image.open(BG)
print(f"  BG size: {im.size}, bytes: {BG.stat().st_size/1024:.0f} KB")

print("Pronto. Background em:", BG)
