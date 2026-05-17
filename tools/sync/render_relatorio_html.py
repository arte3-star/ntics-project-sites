#!/usr/bin/env python3
"""
render_relatorio_html.py — Gera HTML agregando tudo que a automação capturou.

Lê:
- execucao.md (linhas com [auto:...])
- decisoes.md (linhas com [AUTO])
- CLAUDE.md (bloco "## Atualizações automáticas")
- output/sync/*-resumo.md (todos os resumos diários)

Saída: output/sync/relatorio-automacao.html
"""

from __future__ import annotations

import re
import sys
from datetime import datetime, timezone
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

ROOT = Path(__file__).resolve().parents[2]
SB = ROOT / "SecondBrain" / "projetos"
SYNC_OUT = ROOT / "output" / "sync"


def parse_auto_event(line: str) -> dict | None:
    m = re.match(r"\[(?P<ts>[^\]]+)\] \[auto:(?P<fonte>[^/]+)/(?P<tipo>[^\]]+)\] (?P<resumo>.+?)(?:\s+→\s+(?P<acao>.+))?$", line)
    if not m:
        return None
    return m.groupdict()


def parse_auto_decision(line: str) -> dict | None:
    m = re.match(r"\[(?P<ts>[^\]]+)\]\s+\[AUTO\]\s+(?P<texto>.+)$", line)
    if not m:
        return None
    return m.groupdict()


def collect_for_project(slug: str) -> dict:
    sb_dir = SB / slug
    eventos: list[dict] = []
    decisoes: list[dict] = []
    brand_block: list[str] = []

    exec_path = sb_dir / "execucao.md"
    if exec_path.exists():
        for line in exec_path.read_text(encoding="utf-8").splitlines():
            if "[auto:" in line:
                parsed = parse_auto_event(line)
                if parsed:
                    parsed["slug"] = slug
                    eventos.append(parsed)

    dec_path = sb_dir / "decisoes.md"
    if dec_path.exists():
        for line in dec_path.read_text(encoding="utf-8").splitlines():
            if "[AUTO]" in line and not line.startswith("Append-only"):
                parsed = parse_auto_decision(line)
                if parsed:
                    parsed["slug"] = slug
                    decisoes.append(parsed)

    claude_path = sb_dir / "CLAUDE.md"
    if not claude_path.exists():
        # Pode estar no projects/{slug}/CLAUDE.md
        alt = ROOT / "projects" / slug / "CLAUDE.md"
        if alt.exists():
            claude_path = alt
    if claude_path.exists():
        body = claude_path.read_text(encoding="utf-8")
        marker = "## Atualizações automáticas"
        if marker in body:
            block = body.split(marker, 1)[1]
            for line in block.splitlines():
                line = line.strip()
                if line.startswith("- **"):
                    brand_block.append(line)

    return {"slug": slug, "eventos": eventos, "decisoes": decisoes, "brand": brand_block}


def collect_resumos() -> list[tuple[str, str]]:
    items = []
    for p in sorted(SYNC_OUT.glob("*-resumo.md"), reverse=True):
        items.append((p.stem.replace("-resumo", ""), p.read_text(encoding="utf-8")))
    return items


def render_html(projetos: list[dict], resumos: list[tuple[str, str]]) -> str:
    total_eventos = sum(len(p["eventos"]) for p in projetos)
    total_decisoes = sum(len(p["decisoes"]) for p in projetos)
    total_brand = sum(len(p["brand"]) for p in projetos)
    total_resumos = len(resumos)
    gerado_em = datetime.now(timezone.utc).strftime("%d/%m/%Y %H:%M UTC")

    html_parts = [f"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Relatório da automação · NTICS sync</title>
<style>
  :root {{
    --verde: #2c8d3e;
    --verde-escuro: #1e5e2a;
    --verde-claro: #e8f5ec;
    --amarelo: #f9c80e;
    --cinza-fundo: #f7f7f5;
    --cinza-borda: #e5e5e1;
    --cinza-texto: #6b6b66;
    --texto: #1a1a1a;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
    background: var(--cinza-fundo);
    color: var(--texto);
    margin: 0;
    padding: 0;
    line-height: 1.55;
  }}
  .container {{
    max-width: 1100px;
    margin: 0 auto;
    padding: 32px 24px;
  }}
  header {{
    border-bottom: 4px solid var(--verde);
    padding-bottom: 20px;
    margin-bottom: 32px;
  }}
  h1 {{
    margin: 0 0 6px;
    font-size: 28px;
    color: var(--verde-escuro);
    letter-spacing: -0.5px;
  }}
  .subtitulo {{ color: var(--cinza-texto); font-size: 14px; }}
  .stats {{
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 14px;
    margin: 28px 0;
  }}
  .stat {{
    background: white;
    border: 1px solid var(--cinza-borda);
    border-radius: 8px;
    padding: 18px;
    text-align: center;
  }}
  .stat-num {{
    display: block;
    font-size: 32px;
    font-weight: 700;
    color: var(--verde);
    line-height: 1;
  }}
  .stat-label {{
    font-size: 12px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    color: var(--cinza-texto);
    margin-top: 6px;
  }}
  section {{
    background: white;
    border: 1px solid var(--cinza-borda);
    border-radius: 8px;
    padding: 24px;
    margin-bottom: 22px;
  }}
  h2 {{
    margin: 0 0 18px;
    font-size: 18px;
    color: var(--verde-escuro);
    border-left: 4px solid var(--verde);
    padding-left: 12px;
  }}
  h3 {{
    margin: 20px 0 10px;
    font-size: 14px;
    color: var(--cinza-texto);
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }}
  ul.eventos {{
    list-style: none;
    padding: 0;
    margin: 0;
  }}
  ul.eventos li {{
    padding: 10px 12px;
    border-bottom: 1px solid var(--cinza-borda);
    display: grid;
    grid-template-columns: 110px 90px 1fr;
    gap: 12px;
    align-items: start;
  }}
  ul.eventos li:last-child {{ border-bottom: none; }}
  .ts {{ color: var(--cinza-texto); font-size: 12px; font-variant-numeric: tabular-nums; }}
  .badge {{
    display: inline-block;
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.4px;
    background: var(--verde-claro);
    color: var(--verde-escuro);
  }}
  .badge.gmail {{ background: #fff5cc; color: #8a6d00; }}
  .acao {{
    display: block;
    margin-top: 4px;
    font-size: 13px;
    color: var(--cinza-texto);
    font-style: italic;
  }}
  .acao::before {{ content: "→ "; }}
  details {{ margin-top: 12px; }}
  summary {{
    cursor: pointer;
    font-weight: 600;
    color: var(--verde-escuro);
    padding: 8px 0;
  }}
  pre {{
    background: var(--cinza-fundo);
    border: 1px solid var(--cinza-borda);
    border-radius: 6px;
    padding: 16px;
    overflow-x: auto;
    font-size: 13px;
    line-height: 1.5;
  }}
  .resumo-dia {{
    border-left: 3px solid var(--verde-claro);
    padding: 4px 0 4px 14px;
    margin: 14px 0;
  }}
  .resumo-dia .data {{ font-weight: 600; color: var(--verde-escuro); margin-bottom: 4px; }}
  footer {{
    margin-top: 40px;
    padding-top: 20px;
    border-top: 1px solid var(--cinza-borda);
    color: var(--cinza-texto);
    font-size: 12px;
    text-align: center;
  }}
</style>
</head>
<body>
<div class="container">
<header>
  <h1>Relatório da automação · NTICS sync</h1>
  <div class="subtitulo">Tudo que o sistema capturou automaticamente desde que entrou no ar · gerado em {gerado_em}</div>
</header>

<div class="stats">
  <div class="stat"><span class="stat-num">{total_eventos}</span><div class="stat-label">eventos<br>operacionais</div></div>
  <div class="stat"><span class="stat-num">{total_decisoes}</span><div class="stat-label">decisões<br>capturadas</div></div>
  <div class="stat"><span class="stat-num">{total_brand}</span><div class="stat-label">atualizações<br>de brand</div></div>
  <div class="stat"><span class="stat-num">{total_resumos}</span><div class="stat-label">resumos<br>diários</div></div>
</div>
"""]

    # Por projeto
    for p in projetos:
        if not (p["eventos"] or p["decisoes"] or p["brand"]):
            continue
        html_parts.append(f'<section><h2>{p["slug"]}</h2>')

        if p["brand"]:
            html_parts.append("<h3>Atualizações de brand / escopo (CLAUDE.md)</h3><ul class='eventos'>")
            for line in p["brand"]:
                # remove markdown bold
                clean = line.replace("- **", "").replace("**", "")
                html_parts.append(f"<li><span></span><span class='badge'>brand</span><div>{clean}</div></li>")
            html_parts.append("</ul>")

        if p["decisoes"]:
            html_parts.append("<h3>Decisões capturadas (decisoes.md)</h3><ul class='eventos'>")
            for d in reversed(p["decisoes"]):
                ts = d["ts"][:16].replace("T", " ").replace("+00:00", "")
                html_parts.append(
                    f"<li><span class='ts'>{ts}</span>"
                    f"<span class='badge'>decisão</span>"
                    f"<div>{d['texto']}</div></li>"
                )
            html_parts.append("</ul>")

        if p["eventos"]:
            html_parts.append("<h3>Eventos operacionais (execucao.md)</h3><ul class='eventos'>")
            for e in reversed(p["eventos"]):
                ts = e["ts"][:16].replace("T", " ").replace("+00:00", "")
                badge_class = "badge gmail" if e["fonte"] == "gmail" else "badge"
                acao_html = f"<span class='acao'>{e['acao']}</span>" if e.get("acao") else ""
                html_parts.append(
                    f"<li><span class='ts'>{ts}</span>"
                    f"<span class='{badge_class}'>{e['fonte']}</span>"
                    f"<div>{e['resumo']}{acao_html}</div></li>"
                )
            html_parts.append("</ul>")

        html_parts.append("</section>")

    # Resumos diários
    if resumos:
        html_parts.append("<section><h2>Resumos diários</h2>")
        for data, conteudo in resumos:
            html_parts.append(f'<details><summary>{data}</summary><pre>{conteudo}</pre></details>')
        html_parts.append("</section>")

    html_parts.append(f"""<footer>
Gerado por <code>tools/sync/render_relatorio_html.py</code> · automação NTICS sync
</footer>
</div></body></html>""")

    return "".join(html_parts)


def main() -> None:
    if not SB.exists():
        print("SecondBrain/projetos não encontrado", file=sys.stderr)
        sys.exit(1)
    slugs = sorted([c.name for c in SB.iterdir() if c.is_dir()])
    projetos = [collect_for_project(s) for s in slugs]
    resumos = collect_resumos()
    html = render_html(projetos, resumos)
    out = SYNC_OUT / "relatorio-automacao.html"
    SYNC_OUT.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    print(f"[ok] Relatório salvo em {out}")


if __name__ == "__main__":
    main()
