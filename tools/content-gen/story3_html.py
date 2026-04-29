"""
Gera story-3-lista.jpg a partir de HTML+CSS moderno renderizado via Playwright.
Mesma saida visual que um Artifact do claude.ai teria.
"""
from playwright.sync_api import sync_playwright
from pathlib import Path

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
    --teal: #005F73;
    --teal-dark: #003C49;
    --verde: #3DAA35;
    --amarelo: #F5B800;
    --rosa: #D41A6A;
    --teal-futuro: #00A5B8;
    --roxo: #6B2D7B;
    --branco: #FFFFFF;
    --graphite: #1A2930;
  }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  html, body { width: 1080px; height: 1920px; overflow: hidden; }
  body {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    background:
      radial-gradient(circle at 85% 15%, rgba(255,255,255,0.08) 0%, transparent 40%),
      radial-gradient(circle at 15% 85%, rgba(255,255,255,0.06) 0%, transparent 40%),
      linear-gradient(160deg, var(--teal) 0%, var(--teal-dark) 100%);
    color: var(--branco);
    padding: 72px 60px 52px 60px;
    display: flex;
    flex-direction: column;
    position: relative;
  }
  /* Engrenagens decorativas */
  .gear {
    position: absolute;
    width: 440px; height: 440px;
    background-image: url('file:///G:/O meu disco/AUTOMA%C3%87%C3%95ES/brand-book/site/assets/engrenagens.png');
    background-size: contain;
    background-repeat: no-repeat;
    opacity: 0.09;
    pointer-events: none;
  }
  .gear-1 { top: -180px; right: -120px; transform: rotate(22deg); width: 520px; height: 520px; }
  .gear-2 { bottom: -150px; left: -130px; transform: rotate(-18deg); width: 460px; height: 460px; }

  header {
    display: flex; align-items: flex-start; justify-content: space-between;
    margin-bottom: 28px;
  }
  .pill {
    display: inline-flex; align-items: center; gap: 8px;
    background: var(--verde);
    color: #fff;
    padding: 12px 28px;
    border-radius: 100px;
    font-weight: 800;
    font-size: 26px;
    letter-spacing: 0.06em;
    text-transform: uppercase;
  }
  .pill::before {
    content: ""; width: 8px; height: 8px; border-radius: 50%; background: #fff;
  }
  .hero-photo {
    width: 220px; height: 220px;
    -webkit-clip-path: polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%);
    clip-path: polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%);
    background-image: url('file:///G:/O meu disco/AUTOMA%C3%87%C3%95ES/assets/melhores-fotos/1. CONHECENDO OS ODS NAS ESCOLAS/002_ods-cultural-escolas_tecnologia_A_menino-vr-espanto-educador-mural-oceano.jpg');
    background-size: cover; background-position: center;
    flex-shrink: 0;
  }

  .title-block {
    margin-bottom: 40px;
  }
  h1 {
    font-size: 78px; font-weight: 900; letter-spacing: -0.02em; line-height: 0.95;
    text-transform: uppercase;
  }
  h1 .yellow { color: var(--amarelo); display: block; font-size: 44px; font-weight: 800; margin-top: 12px; text-transform: none; letter-spacing: -0.01em;}

  .cards { display: flex; flex-direction: column; gap: 18px; flex: 1; }
  .card {
    position: relative;
    background: rgba(255, 255, 255, 0.07);
    backdrop-filter: blur(2px);
    border-radius: 18px;
    padding: 26px 32px 26px 48px;
    display: grid;
    grid-template-columns: 110px 1fr;
    gap: 28px;
    align-items: center;
    overflow: hidden;
    box-shadow: 0 10px 30px rgba(0,0,0,0.15);
  }
  .card::before {
    content: ""; position: absolute; left: 0; top: 0; bottom: 0; width: 12px;
  }
  .card-1::before { background: var(--verde); }
  .card-2::before { background: var(--teal-futuro); }
  .card-3::before { background: var(--roxo); }
  .card-4::before { background: var(--amarelo); }
  .card-5::before { background: var(--rosa); }

  .num {
    font-size: 72px; font-weight: 900; line-height: 1;
    text-align: left;
  }
  .card-1 .num { color: var(--verde); }
  .card-2 .num { color: var(--teal-futuro); }
  .card-3 .num { color: #9c6cac; }
  .card-4 .num { color: var(--amarelo); }
  .card-5 .num { color: var(--rosa); }

  .content h3 {
    font-size: 36px; font-weight: 800; line-height: 1.15; margin-bottom: 6px;
  }
  .content p {
    font-size: 24px; font-weight: 400; color: rgba(255,255,255,0.8); line-height: 1.35;
  }

  .cta {
    margin-top: 32px;
    background: var(--verde);
    border-radius: 22px;
    padding: 30px 40px;
    display: flex; align-items: center; justify-content: center;
    gap: 20px;
    box-shadow: 0 18px 40px rgba(61, 170, 53, 0.35);
  }
  .cta .label { font-size: 38px; font-weight: 900; letter-spacing: 0.01em; text-transform: uppercase; }
  .cta .arrow { font-size: 42px; font-weight: 900; }

  footer {
    margin-top: 18px;
    display: flex; justify-content: space-between;
    font-size: 20px; font-weight: 600;
    color: rgba(255,255,255,0.65); letter-spacing: 0.06em; text-transform: uppercase;
  }
</style>
</head>
<body>
  <div class="gear gear-1"></div>
  <div class="gear gear-2"></div>

  <header>
    <span class="pill">Os 5 Sinais</span>
    <div class="hero-photo"></div>
  </header>

  <div class="title-block">
    <h1>de Maturidade<span class="yellow">em Responsabilidade Social</span></h1>
  </div>

  <div class="cards">
    <div class="card card-1">
      <div class="num">01</div>
      <div class="content">
        <h3>Integração à estratégia</h3>
        <p>no planejamento, não só no relatório</p>
      </div>
    </div>
    <div class="card card-2">
      <div class="num">02</div>
      <div class="content">
        <h3>Métricas de longo prazo</h3>
        <p>medem transformação real, não evento</p>
      </div>
    </div>
    <div class="card card-3">
      <div class="num">03</div>
      <div class="content">
        <h3>Engajamento interno</h3>
        <p>propósito compartilhado com o time</p>
      </div>
    </div>
    <div class="card card-4">
      <div class="num">04</div>
      <div class="content">
        <h3>Diálogo com o território</h3>
        <p>projetos COM a comunidade, não PARA</p>
      </div>
    </div>
    <div class="card card-5">
      <div class="num">05</div>
      <div class="content">
        <h3>Aprendizado contínuo</h3>
        <p>dados viram combustível, não só relato</p>
      </div>
    </div>
  </div>

  <div class="cta">
    <span class="label">Leia o artigo completo</span>
    <span class="arrow">↑</span>
  </div>

  <footer>
    <span>ntics.com.br</span>
    <span>@nticsprojetos</span>
  </footer>
</body>
</html>
"""

OUT_HTML = Path(".tmp/story-3-design.html")
OUT_JPG = Path("output/marketing/stories/artigo-5-sinais-responsabilidade-social/story-3-lista.jpg")
OUT_HTML.parent.mkdir(parents=True, exist_ok=True)
OUT_HTML.write_text(HTML, encoding="utf-8")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_context(viewport={"width": 1080, "height": 1920}, device_scale_factor=2).new_page()
    page.goto("file:///" + str(OUT_HTML.resolve()).replace("\\", "/"))
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(800)
    page.screenshot(path=str(OUT_JPG), type="jpeg", quality=94, full_page=False, clip={"x":0,"y":0,"width":1080,"height":1920})
    browser.close()
print(f"[OK] {OUT_JPG}")
