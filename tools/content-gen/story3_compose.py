"""
Compoe story-3-lista.jpg finalizando:
  background Leonardo (story-3-bg-leonardo.jpg) + overlay HTML com 5 cards, titulo e CTA.
Render via Playwright em 1080x1920.
"""
from playwright.sync_api import sync_playwright
from pathlib import Path

ROOT = Path.cwd()
BG = ROOT / "output/marketing/stories/artigo-5-sinais-responsabilidade-social/story-3-bg-leonardo.jpg"
OUT_HTML = ROOT / ".tmp/story-3-final.html"
OUT_JPG = ROOT / "output/marketing/stories/artigo-5-sinais-responsabilidade-social/story-3-lista.jpg"

HTML = r"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
<style>
  :root {
    --teal: #005F73; --teal-dark: #003C49; --verde: #3DAA35;
    --amarelo: #F5B800; --rosa: #D41A6A; --teal-futuro: #00A5B8; --roxo: #6B2D7B;
  }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  html, body { width: 1080px; height: 1920px; overflow: hidden; }
  body {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    color: #fff;
    position: relative;
    background: #002a33;
  }
  /* BG Leonardo */
  .bg {
    position: absolute; inset: 0;
    background-image: url('{BG_URL}');
    background-size: cover;
    background-position: center;
  }
  /* Overlay escuro gradiente pra legibilidade */
  .overlay {
    position: absolute; inset: 0;
    background:
      linear-gradient(180deg, rgba(0,40,50,0.55) 0%, rgba(0,40,50,0.15) 30%, rgba(0,40,50,0.55) 60%, rgba(0,40,50,0.92) 100%);
  }
  .content {
    position: relative;
    padding: 80px 60px 52px 60px;
    height: 100%;
    display: flex; flex-direction: column;
  }
  header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 24px; }
  .pill {
    display: inline-flex; align-items: center; gap: 10px;
    background: var(--verde); padding: 14px 32px; border-radius: 100px;
    font-weight: 800; font-size: 28px; letter-spacing: 0.06em; text-transform: uppercase;
    box-shadow: 0 8px 24px rgba(61,170,53,0.35);
  }
  .pill::before { content: ""; width: 10px; height: 10px; border-radius: 50%; background: #fff; }
  .hero-photo {
    width: 220px; height: 220px;
    -webkit-clip-path: polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%);
    clip-path: polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%);
    background-image: url('file:///G:/O meu disco/AUTOMA%C3%87%C3%95ES/SecondBrain/banco-fotos/1. CONHECENDO OS ODS NAS ESCOLAS/002_ods-cultural-escolas_tecnologia_A_menino-vr-espanto-educador-mural-oceano.jpg');
    background-size: cover; background-position: center;
    border: 4px solid rgba(255,255,255,0.18);
  }
  .title-block { margin-bottom: 44px; }
  h1 {
    font-size: 88px; font-weight: 900; letter-spacing: -0.025em; line-height: 0.92;
    text-transform: uppercase;
    text-shadow: 0 4px 20px rgba(0,0,0,0.35);
  }
  h1 .yellow {
    color: var(--amarelo); display: block; font-size: 44px; font-weight: 700;
    margin-top: 14px; text-transform: none; letter-spacing: -0.01em;
  }
  .cards { display: flex; flex-direction: column; gap: 16px; flex: 1; }
  .card {
    position: relative;
    background: rgba(0, 30, 40, 0.72);
    backdrop-filter: blur(14px);
    -webkit-backdrop-filter: blur(14px);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 22px;
    padding: 24px 30px 24px 52px;
    display: grid; grid-template-columns: 120px 1fr; gap: 24px;
    align-items: center;
    overflow: hidden;
    box-shadow: 0 14px 40px rgba(0,0,0,0.3);
  }
  .card::before {
    content: ""; position: absolute; left: 0; top: 0; bottom: 0; width: 14px;
    box-shadow: 0 0 24px currentColor;
  }
  .card-1 { color: var(--verde); } .card-1::before { background: var(--verde); }
  .card-2 { color: var(--teal-futuro); } .card-2::before { background: var(--teal-futuro); }
  .card-3 { color: #c18ad1; } .card-3::before { background: var(--roxo); }
  .card-4 { color: var(--amarelo); } .card-4::before { background: var(--amarelo); }
  .card-5 { color: var(--rosa); } .card-5::before { background: var(--rosa); }
  .num { font-size: 78px; font-weight: 900; line-height: 1; }
  .c-text h3 { font-size: 38px; font-weight: 800; line-height: 1.1; margin-bottom: 6px; color: #fff; }
  .c-text p { font-size: 24px; font-weight: 400; color: rgba(255,255,255,0.75); line-height: 1.3; }
  .cta {
    margin-top: 28px;
    background: linear-gradient(135deg, var(--verde), #2f8a28);
    border-radius: 24px;
    padding: 30px 40px;
    display: flex; align-items: center; justify-content: center; gap: 22px;
    box-shadow: 0 22px 50px rgba(61,170,53,0.45);
  }
  .cta .label { font-size: 40px; font-weight: 900; text-transform: uppercase; letter-spacing: 0.02em; }
  .cta .arrow { font-size: 46px; font-weight: 900; }
  footer {
    margin-top: 16px;
    display: flex; justify-content: space-between;
    font-size: 20px; font-weight: 700;
    color: rgba(255,255,255,0.6); letter-spacing: 0.08em; text-transform: uppercase;
  }
</style>
</head>
<body>
<div class="bg"></div>
<div class="overlay"></div>
<div class="content">
  <header>
    <span class="pill">Os 5 Sinais</span>
    <div class="hero-photo"></div>
  </header>
  <div class="title-block">
    <h1>de Maturidade<span class="yellow">em Responsabilidade Social</span></h1>
  </div>
  <div class="cards">
    <div class="card card-1"><div class="num">01</div><div class="c-text"><h3>Integração à estratégia</h3><p>no planejamento, não só no relatório</p></div></div>
    <div class="card card-2"><div class="num">02</div><div class="c-text"><h3>Métricas de longo prazo</h3><p>medem transformação real, não evento</p></div></div>
    <div class="card card-3"><div class="num">03</div><div class="c-text"><h3>Engajamento interno</h3><p>propósito compartilhado com o time</p></div></div>
    <div class="card card-4"><div class="num">04</div><div class="c-text"><h3>Diálogo com o território</h3><p>projetos COM a comunidade, não PARA</p></div></div>
    <div class="card card-5"><div class="num">05</div><div class="c-text"><h3>Aprendizado contínuo</h3><p>dados viram combustível, não só relato</p></div></div>
  </div>
  <div class="cta"><span class="label">Leia o artigo completo</span><span class="arrow">↑</span></div>
  <footer><span>ntics.com.br</span><span>@nticsprojetos</span></footer>
</div>
</body>
</html>
"""

# Injetar URL do BG
bg_url = "file:///" + str(BG.resolve()).replace("\\", "/").replace(" ", "%20")
html_final = HTML.replace("{BG_URL}", bg_url)
OUT_HTML.parent.mkdir(parents=True, exist_ok=True)
OUT_HTML.write_text(html_final, encoding="utf-8")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_context(viewport={"width": 1080, "height": 1920}, device_scale_factor=2).new_page()
    page.goto("file:///" + str(OUT_HTML.resolve()).replace("\\", "/"))
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(1500)
    page.screenshot(path=str(OUT_JPG), type="jpeg", quality=94, clip={"x":0,"y":0,"width":1080,"height":1920})
    browser.close()
print(f"[OK] {OUT_JPG}")
