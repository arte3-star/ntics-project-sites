"""
Pipeline completo de stories v21 para artigo NTICS.
  1. Leonardo nano-banana-2 gera 4 BGs consistentes (mesma familia visual)
  2. HTML+Playwright sobrepoe v21-style: fullbleed + headline gigante + pill verde + destaques amarelos
  3. Output: 4 JPGs 1080x1920

Estilo v21: pill verde topo, headline branco bold gigante, faixa com dados destacados.
"""
import os, json, time, sys
from pathlib import Path
import requests
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
for line in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
    if "=" in line and not line.startswith("#"):
        k, v = line.split("=", 1); os.environ.setdefault(k.strip(), v.strip())

KEY = os.environ["LEONARDO_API_KEY"]
H = {"Authorization": f"Bearer {KEY}", "Content-Type": "application/json", "accept": "application/json"}
OUT = ROOT / "output/marketing/stories/artigo-5-sinais-responsabilidade-social"
OUT.mkdir(parents=True, exist_ok=True)

ARTIGO_URL = "ntics.com.br"
INSTA = "@nticsprojetos"

# === PROMPTS LEONARDO ===
BASE = (
    "Abstract corporate visualization: floating translucent hexagonal shapes and geometric polyhedra "
    "connected by luminous thin lines forming an organic network pattern, {mood}, "
    "deep teal to dark-teal gradient background, subtle green and yellow accent glows on selected nodes, "
    "soft depth-of-field blur, corporate-editorial aesthetic, full-bleed composition, "
    "photographic quality with subtle film grain. No text, no logos, no watermarks, no faces, no people."
)
MOODS = {
    "1-capa":   "dense vibrant cluster with upward-flowing energy rising from the lower portion of the frame",
    "2-gancho": "sparser composition with a luminous focal node in the center, contemplative and introspective mood",
    "3-lista":  "balanced wide-spread network covering the whole frame evenly",
    "4-cta":    "radiant rays of light emerging from the center flowing forward, open and inviting mood",
}

def leonardo_bg(slug, mood):
    """Gera BG 1856x2304 via nano-banana-2, salva em OUT/story-N-bg-leonardo.jpg."""
    out = OUT / f"story-{slug}-bg-leonardo.jpg"
    if out.exists():
        print(f"  [skip] {out.name} já existe")
        return out
    prompt = BASE.format(mood=mood)
    payload = {
        "model": "nano-banana-2",
        "parameters": {
            "prompt": prompt,
            "width": 1856, "height": 2304,
            "quantity": 1, "prompt_enhance": "OFF",
        },
        "public": False,
    }
    print(f"  [{slug}] submetendo...")
    r = requests.post("https://cloud.leonardo.ai/api/rest/v2/generations", headers=H, json=payload, timeout=60)
    r.raise_for_status()
    resp = r.json()
    gen_id = resp.get("generate", {}).get("generationId") or resp.get("generationId")
    if not gen_id:
        print("RESP:", resp); sys.exit()
    print(f"  [{slug}] gen_id={gen_id}")
    url = f"https://cloud.leonardo.ai/api/rest/v1/generations/{gen_id}"
    for _ in range(75):
        time.sleep(4)
        data = (requests.get(url, headers=H, timeout=30).json().get("generations_by_pk") or {})
        status = data.get("status")
        if status == "COMPLETE":
            imgs = data.get("generated_images") or []
            if imgs:
                out.write_bytes(requests.get(imgs[0]["url"], timeout=60).content)
                print(f"  [{slug}] OK -> {out}")
                return out
            sys.exit(f"[{slug}] COMPLETE sem imagens")
        if status == "FAILED":
            sys.exit(f"[{slug}] FAILED")
    sys.exit(f"[{slug}] timeout")

# === HTML TEMPLATES (estilo v21 adaptado pra 9:16) ===
CSS_BASE = r"""
:root {
  --teal: #005F73; --teal-dark: #003C49; --verde: #3DAA35;
  --amarelo: #F5B800; --rosa: #D41A6A; --teal-futuro: #00A5B8; --roxo: #6B2D7B;
}
* { box-sizing: border-box; margin: 0; padding: 0; }
html, body { width: 1080px; height: 1920px; overflow: hidden; font-family: 'Inter', -apple-system, sans-serif; color: #fff; }
body { position: relative; background: #002a33; }
.bg { position: absolute; inset: 0; background-size: cover; background-position: center; }
.ovr {
  position: absolute; inset: 0;
  background:
    linear-gradient(180deg, rgba(0,40,50,0.78) 0%, rgba(0,40,50,0.30) 30%, rgba(0,40,50,0.30) 60%, rgba(0,40,50,0.92) 100%);
}
.wrap { position: relative; padding: 80px 60px 60px 60px; height: 100%; display: flex; flex-direction: column; }
.pill {
  display: inline-flex; align-items: center; gap: 10px;
  background: var(--verde); padding: 14px 32px; border-radius: 100px;
  font-weight: 800; font-size: 26px; letter-spacing: 0.08em; text-transform: uppercase; color: #fff;
  box-shadow: 0 10px 28px rgba(61,170,53,0.4);
}
.pill::before { content: ""; width: 10px; height: 10px; border-radius: 50%; background: #fff; }
h1 {
  font-size: 120px; font-weight: 900; letter-spacing: -0.03em; line-height: 0.90;
  text-transform: uppercase;
  text-shadow: 0 6px 30px rgba(0,0,0,0.55);
}
h1.sm { font-size: 92px; }
h1.xsm { font-size: 74px; }
h1 .yellow { color: var(--amarelo); display: block; }
h1 .small { font-size: 0.45em; font-weight: 800; margin-top: 16px; display: block; color: var(--amarelo); text-transform: none; letter-spacing: -0.01em; }
.faixa {
  background: linear-gradient(90deg, rgba(0,165,184,0.95), rgba(0,95,115,0.95));
  border-radius: 18px;
  padding: 22px 28px;
  font-size: 28px; font-weight: 700; color: #fff;
  box-shadow: 0 14px 36px rgba(0,0,0,0.3);
  border: 1px solid rgba(255,255,255,0.1);
}
.faixa b { color: var(--amarelo); font-weight: 900; }
.cta {
  background: linear-gradient(135deg, var(--verde), #2f8a28);
  border-radius: 24px; padding: 32px 40px;
  display: flex; align-items: center; justify-content: center; gap: 22px;
  box-shadow: 0 22px 50px rgba(61,170,53,0.5);
}
.cta .label { font-size: 42px; font-weight: 900; text-transform: uppercase; letter-spacing: 0.02em; }
.cta .arrow { font-size: 48px; font-weight: 900; }
footer {
  display: flex; justify-content: space-between;
  font-size: 20px; font-weight: 700;
  color: rgba(255,255,255,0.65); letter-spacing: 0.08em; text-transform: uppercase;
}
.spacer { flex: 1; }
.top-area { display: flex; flex-direction: column; align-items: flex-start; gap: 36px; }
"""

def render_html(html_body: str, slug: str, bg_path: Path):
    """Renderiza HTML+BG para JPG 1080x1920 via Playwright."""
    bg_url = "file:///" + str(bg_path.resolve()).replace("\\", "/").replace(" ", "%20")
    full_html = (
        "<!DOCTYPE html><html lang='pt-BR'><head><meta charset='UTF-8'>"
        "<link rel='preconnect' href='https://fonts.googleapis.com'>"
        "<link rel='preconnect' href='https://fonts.gstatic.com' crossorigin>"
        "<link href='https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap' rel='stylesheet'>"
        f"<style>{CSS_BASE}\n.bg{{background-image:url('{bg_url}');}}</style></head>"
        f"<body><div class='bg'></div><div class='ovr'></div>{html_body}</body></html>"
    )
    tmp = ROOT / f".tmp/story-{slug}-v21.html"
    tmp.parent.mkdir(parents=True, exist_ok=True)
    tmp.write_text(full_html, encoding="utf-8")
    out = OUT / f"story-{slug}.jpg"
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_context(viewport={"width": 1080, "height": 1920}, device_scale_factor=2).new_page()
        page.goto("file:///" + str(tmp.resolve()).replace("\\", "/"))
        page.wait_for_load_state("networkidle"); page.wait_for_timeout(1200)
        page.screenshot(path=str(out), type="jpeg", quality=94, clip={"x":0,"y":0,"width":1080,"height":1920})
        browser.close()
    print(f"  [OK] {out}")

# === BODIES (cada story) ===
BODY_1_CAPA = """
<div class='wrap'>
  <div class='top-area'>
    <span class='pill'>Artigo · NTICS Notes</span>
    <h1 class='sm'>Os 5 Sinais<br><span class='yellow'>de Maturidade</span><span class='small'>em Responsabilidade Social</span></h1>
  </div>
  <div class='spacer'></div>
  <div class='faixa'>Sua empresa está no caminho certo? <b>Descubra nos próximos cards →</b></div>
  <div style='height:20px'></div>
  <footer><span>ntics.com.br</span><span>@nticsprojetos</span></footer>
</div>
"""

BODY_2_GANCHO = """
<div class='wrap'>
  <div class='top-area'>
    <span class='pill'>5 Sinais</span>
    <h1 class='sm'>Você reconhece<br><span class='yellow'>esses 5 sinais?</span></h1>
  </div>
  <div style='margin-top:50px; display:flex; flex-direction:column; gap:14px;'>
    """ + "\n".join([
        "<div style=\"background:rgba(0,30,40,0.75); backdrop-filter:blur(14px); border:1px solid rgba(255,255,255,0.08); border-radius:18px; padding:20px 28px; display:flex; align-items:center; gap:24px;\">"
        f"<span style=\"font-size:44px; font-weight:900; color:{c}; min-width:70px;\">{n}</span>"
        f"<span style=\"font-size:34px; font-weight:800;\">{nome}</span></div>"
        for n, nome, c in [
            ("01", "Integração à estratégia", "#3DAA35"),
            ("02", "Métricas de longo prazo", "#00A5B8"),
            ("03", "Engajamento interno", "#c18ad1"),
            ("04", "Diálogo com o território", "#F5B800"),
            ("05", "Aprendizado contínuo", "#D41A6A"),
        ]
    ]) + """
  </div>
  <div class='spacer'></div>
  <div class='faixa'>Arrasta pra ver <b>cada sinal detalhado →</b></div>
  <div style='height:20px'></div>
  <footer><span>ntics.com.br</span><span>@nticsprojetos</span></footer>
</div>
"""

# Story 3 já foi feita (lista detalhada). Vou regerar com consistência v21.
BODY_3_LISTA = """
<div class='wrap'>
  <div style='display:flex; justify-content:space-between; align-items:flex-start;'>
    <span class='pill'>Os 5 Sinais</span>
    <div style="width:180px; height:180px; clip-path: polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%); -webkit-clip-path: polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%); background-image: url('file:///G:/O meu disco/AUTOMA%C3%87%C3%95ES/SecondBrain/banco-fotos/1. CONHECENDO OS ODS NAS ESCOLAS/002_ods-cultural-escolas_tecnologia_A_menino-vr-espanto-educador-mural-oceano.jpg'); background-size:cover; background-position:center; border:3px solid rgba(255,255,255,0.18);"></div>
  </div>
  <div style='margin-top:30px;'>
    <h1 class='xsm'>De Maturidade<span class='small'>em Responsabilidade Social</span></h1>
  </div>
  <div style='margin-top:36px; display:flex; flex-direction:column; gap:14px; flex:1;'>
    """ + "\n".join([
        "<div style=\""
        "position:relative; background:rgba(0,30,40,0.72); backdrop-filter:blur(14px);"
        "border:1px solid rgba(255,255,255,0.08); border-radius:20px;"
        "padding:22px 28px 22px 52px; display:grid; grid-template-columns:110px 1fr; gap:22px; align-items:center;"
        "box-shadow:0 14px 40px rgba(0,0,0,0.3); overflow:hidden;\">"
        f"<span style=\"position:absolute; left:0; top:0; bottom:0; width:14px; background:{c}; box-shadow:0 0 24px {c};\"></span>"
        f"<span style=\"font-size:72px; font-weight:900; color:{c}; line-height:1;\">{n}</span>"
        f"<div><div style=\"font-size:34px; font-weight:800; line-height:1.1; margin-bottom:4px;\">{t}</div>"
        f"<div style=\"font-size:22px; font-weight:400; color:rgba(255,255,255,0.75); line-height:1.3;\">{d}</div></div></div>"
        for n, t, d, c in [
            ("01", "Integração à estratégia", "no planejamento, não só no relatório", "#3DAA35"),
            ("02", "Métricas de longo prazo", "medem transformação real, não evento", "#00A5B8"),
            ("03", "Engajamento interno", "propósito compartilhado com o time", "#c18ad1"),
            ("04", "Diálogo com o território", "projetos COM a comunidade, não PARA", "#F5B800"),
            ("05", "Aprendizado contínuo", "dados viram combustível, não só relato", "#D41A6A"),
        ]
    ]) + """
  </div>
  <div class='cta' style='margin-top:24px;'><span class='label'>Leia o artigo completo</span><span class='arrow'>↑</span></div>
  <div style='height:14px'></div>
  <footer><span>ntics.com.br</span><span>@nticsprojetos</span></footer>
</div>
"""

BODY_4_CTA = """
<div class='wrap'>
  <div class='top-area'>
    <span class='pill'>NTICS Notes</span>
    <h1>Leia o artigo<br><span class='yellow'>completo</span></h1>
  </div>
  <div style='margin-top:60px;'>
    <div class='faixa' style='font-size:32px; line-height:1.4;'>
      Os <b>5 sinais</b>, o <b>método NTICS</b> e como identificar a maturidade em Responsabilidade Social na sua empresa.
    </div>
  </div>
  <div class='spacer'></div>
  <div class='cta'><span class='label'>Toque no link</span><span class='arrow'>↑</span></div>
  <div style='height:20px'></div>
  <footer><span>ntics.com.br</span><span>@nticsprojetos</span></footer>
</div>
"""

BODIES = {
    "1-capa":   BODY_1_CAPA,
    "2-gancho": BODY_2_GANCHO,
    "3-lista":  BODY_3_LISTA,
    "4-cta":    BODY_4_CTA,
}

# === PIPELINE ===
if __name__ == "__main__":
    print("== Fase 1: Gerar BGs Leonardo ==")
    bgs = {}
    for slug, mood in MOODS.items():
        bgs[slug] = leonardo_bg(slug, mood)

    print("== Fase 2: Compor stories ==")
    for slug, body in BODIES.items():
        render_html(body, slug, bgs[slug])

    print("Pronto. 4 stories em", OUT)
