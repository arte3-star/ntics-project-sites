#!/usr/bin/env python3
"""
recap_semanal.py — Recap semanal de drift por projeto.

Le os ultimos 7 dias de output/sync/*.md + execucao.md de cada projeto + state.yaml,
e usa Sonnet para gerar 1 pagina respondendo: o que cada projeto disse que ia fazer
(state.yaml.proxima_acao) vs o que efetivamente saiu (eventos da semana).

Uso:
    python tools/sync/recap_semanal.py
"""

from __future__ import annotations

import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests
import yaml
from dotenv import load_dotenv

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

ROOT = Path(__file__).resolve().parents[2]
PROJECTS_DIR = ROOT / "projects"
SYNC_OUT = ROOT / "output" / "sync"
AUTOMACOES_ENV = ROOT.parent / "AUTOMAÇÕES" / ".env"

SONNET_MODEL = "claude-sonnet-4-6"
ANTHROPIC_API = "https://api.anthropic.com/v1/messages"


def load_env() -> None:
    if AUTOMACOES_ENV.exists():
        load_dotenv(AUTOMACOES_ENV)
    env_local = ROOT / ".env"
    if env_local.exists():
        load_dotenv(env_local, override=True)


def find_sb_dir(slug: str) -> Path | None:
    sb_root = ROOT / "SecondBrain" / "projetos"
    exact = sb_root / slug
    if exact.exists():
        return exact
    prefix = slug.split("-", 1)[0]
    if prefix.isdigit() and sb_root.exists():
        for child in sb_root.iterdir():
            if child.is_dir() and child.name.startswith(f"{prefix}-"):
                return child
    return None


def gather_week_for_project(slug: str, since: datetime) -> dict:
    project_dir = PROJECTS_DIR / slug
    state_path = project_dir / "state.yaml"
    state = yaml.safe_load(state_path.read_text(encoding="utf-8")) if state_path.exists() else {}

    eventos_semana: list[str] = []
    sb_dir = find_sb_dir(slug)
    if sb_dir:
        execucao = sb_dir / "execucao.md"
        if execucao.exists():
            for line in execucao.read_text(encoding="utf-8").splitlines():
                if not line.startswith("["):
                    continue
                try:
                    ts_str = line[1:line.index("]")]
                    ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
                    if ts >= since:
                        eventos_semana.append(line)
                except (ValueError, IndexError):
                    continue

    return {
        "slug": slug,
        "fase": state.get("fase"),
        "proxima_acao": state.get("proxima_acao"),
        "blockers": state.get("blockers", []),
        "deliverables_pendentes": [
            d.get("nome") for d in state.get("deliverables_design", [])
            if d.get("status") not in ("concluido", "aprovado")
        ][:8],
        "eventos_semana": eventos_semana[-30:],
    }


def call_sonnet(prompt: str, max_tokens: int = 3000) -> str:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY nao encontrado")
    r = requests.post(
        ANTHROPIC_API,
        headers={
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        json={
            "model": SONNET_MODEL,
            "max_tokens": max_tokens,
            "messages": [{"role": "user", "content": prompt}],
        },
        timeout=120,
    )
    if not r.ok:
        raise RuntimeError(f"Sonnet API error {r.status_code}: {r.text[:300]}")
    return r.json()["content"][0]["text"]


def main() -> None:
    load_env()
    now = datetime.now(timezone.utc)
    since = now - timedelta(days=7)
    iso_week = now.strftime("%G-W%V")

    slugs = [c.name for c in sorted(PROJECTS_DIR.iterdir())
             if c.is_dir() and (c / "tasks.yaml").exists()]
    if not slugs:
        print("Nenhum projeto com tasks.yaml.", file=sys.stderr)
        return

    print(f"> Recap semanal {iso_week} para {len(slugs)} projeto(s)...", file=sys.stderr)
    dados = [gather_week_for_project(s, since) for s in slugs]

    prompt = f"""Voce e o PMO da NTICS Projetos. Faca um recap da semana {iso_week} (ultimos 7 dias).

Para cada projeto abaixo, voce tem:
- fase atual e proxima_acao declarada (state.yaml)
- deliverables ainda pendentes
- blockers ativos
- todos os eventos da semana (operacionais que sairam no execucao.md)

Dados:
{yaml.safe_dump(dados, allow_unicode=True, sort_keys=False, default_flow_style=False)}

Produza um markdown com a seguinte estrutura, em portugues, conciso (max 1 pagina):

# Recap semanal {iso_week}

## TL;DR
- 3-5 bullets do que precisa de atencao do Lucas/Bruna NA SEGUNDA.

## Por projeto

Para cada projeto que TEVE eventos na semana:

### {{slug}} — {{fase}}
- **Disse que ia:** {{proxima_acao}}
- **Aconteceu:** 1-2 frases do que de fato saiu (sintetizar eventos_semana).
- **Drift:** "alinhado" | "drift baixo" | "drift alto: {{razao}}". Drift alto = proxima_acao nao avancou ha 3+ dias E nao ha blocker registrado que justifique.
- **Blockers:** lista curta se houver.

Projetos sem eventos na semana: lista curta no final em "## Silenciosos".

Regras:
- Nao invente eventos que nao estao em eventos_semana.
- Se eventos_semana esta vazio, marque como silencioso.
- Drift alto SO se nao avancou E nao tem blocker. Se tem blocker, e bloqueado, nao drift.
"""

    md = call_sonnet(prompt, max_tokens=3500)
    SYNC_OUT.mkdir(parents=True, exist_ok=True)
    out_path = SYNC_OUT / f"semana-{iso_week}.md"
    out_path.write_text(md, encoding="utf-8")
    print(f"[ok] Recap salvo em {out_path}", file=sys.stderr)
    print(md)


if __name__ == "__main__":
    main()
