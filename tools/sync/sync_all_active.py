#!/usr/bin/env python3
"""
sync_all_active.py — Roda projeto_sync.py para todo projeto em SecondBrain/projetos/ que tenha tasks.yaml.

Gera um resumo agregado em output/sync/YYYY-MM-DD-resumo.md (1 página: o que mudou onde,
agrupado por projeto, ranqueado por relevância).

Uso:
    python tools/sync/sync_all_active.py
    python tools/sync/sync_all_active.py --dry-run
    python tools/sync/sync_all_active.py --only 132-estacao-samarco,115-peroxidos
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from email.mime.text import MIMEText
import base64
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

ROOT = Path(__file__).resolve().parents[2]
PROJECTS_DIR = ROOT / "SecondBrain" / "projetos"
SYNC_OUT = ROOT / "output" / "sync"
SYNC_SCRIPT = ROOT / "tools" / "sync" / "projeto_sync.py"
AUTOMACOES_TOOLS = ROOT.parent / "AUTOMAÇÕES" / "tools"
HEALTH_LOOKBACK_DAYS = 5
HEALTH_MIN_RESUMOS = 3  # se < N de últimos 5 dias têm resumo, alertar
HEALTH_ALERT_FILE = SYNC_OUT / ".health-alert.txt"
HEALTH_LAST_NOTIFIED = SYNC_OUT / ".health-last-notified"
ALERT_EMAIL_TO = "lucas@sbsustainablebusiness.com"


def discover_projects(only: set[str] | None = None) -> list[str]:
    slugs = []
    for child in sorted(PROJECTS_DIR.iterdir()):
        if not child.is_dir():
            continue
        if not (child / "tasks.yaml").exists():
            continue
        if only and child.name not in only:
            continue
        slugs.append(child.name)
    return slugs


def run_sync_one(slug: str, dry_run: bool) -> dict:
    cmd = [sys.executable, str(SYNC_SCRIPT), slug, "--quiet", "--json"]
    if dry_run:
        cmd.append("--dry-run")
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=180, encoding="utf-8")
    except subprocess.TimeoutExpired:
        return {"status": "timeout", "slug": slug}
    if r.returncode != 0:
        return {"status": "erro", "slug": slug, "stderr": (r.stderr or "")[-500:]}
    try:
        data = json.loads(r.stdout) if r.stdout.strip() else {"status": "vazio"}
    except json.JSONDecodeError:
        data = {"status": "saida_invalida", "raw": (r.stdout or "")[-500:]}
    data["slug"] = slug
    return data


def render_resumo(results: list[dict], hoje: str) -> str:
    linhas = [f"# Resumo diário de sync — {hoje}", ""]
    com_mudanca = [r for r in results if r.get("status") == "sincronizado"]
    sem_mudanca = [r for r in results if r.get("status") == "sem_mudancas"]
    com_erro = [r for r in results if r.get("status") not in ("sincronizado", "sem_mudancas")]

    linhas.append(f"**{len(com_mudanca)} projeto(s) com novidades** · {len(sem_mudanca)} estáveis · {len(com_erro)} com erro")
    linhas.append("")

    if com_mudanca:
        linhas.append("## Projetos com novidades")
        linhas.append("")
        for r in com_mudanca:
            slug = r["slug"]
            eventos = r.get("eventos", [])
            altas = [e for e in eventos if e.get("relevancia") == "alta"]
            medias = [e for e in eventos if e.get("relevancia") == "media"]
            decisoes = r.get("decisoes", [])
            linhas.append(f"### {slug}")
            for e in altas:
                fonte = e.get("fonte", "?")
                linhas.append(f"- [!] **[{fonte}]** {e.get('resumo', '').strip()}"
                              + (f" → _{e.get('acao_sugerida')}_" if e.get('acao_sugerida') else ""))
            for e in medias[:5]:
                fonte = e.get("fonte", "?")
                linhas.append(f"- [·] [{fonte}] {e.get('resumo', '').strip()}")
            for d in decisoes:
                if d and d.strip():
                    linhas.append(f"- [DECISAO] {d.strip()}")
            linhas.append("")

    if sem_mudanca:
        linhas.append("## Sem mudanças")
        linhas.append(", ".join(r["slug"] for r in sem_mudanca))
        linhas.append("")

    if com_erro:
        linhas.append("## Com erro")
        for r in com_erro:
            linhas.append(f"- **{r['slug']}** — {r.get('status')}: {(r.get('stderr') or r.get('motivo') or '').strip()[:200]}")
        linhas.append("")

    return "\n".join(linhas)


def health_check(today: str) -> dict:
    """Verifica se últimos N dias têm resumo. Retorna dict {ok: bool, faltando: [...]}."""
    today_dt = datetime.strptime(today, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    esperados = [(today_dt - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(HEALTH_LOOKBACK_DAYS)]
    presentes = {p.stem.replace("-resumo", "") for p in SYNC_OUT.glob("*-resumo.md")}
    faltando = [d for d in esperados if d not in presentes]
    ok = (HEALTH_LOOKBACK_DAYS - len(faltando)) >= HEALTH_MIN_RESUMOS
    return {"ok": ok, "faltando": faltando, "esperados": esperados, "presentes": sorted(presentes)[-10:]}


def should_renotify() -> bool:
    """Evita spam: só re-notifica se passou >24h desde último alerta."""
    if not HEALTH_LAST_NOTIFIED.exists():
        return True
    try:
        last = datetime.fromtimestamp(HEALTH_LAST_NOTIFIED.stat().st_mtime, tz=timezone.utc)
        return (datetime.now(timezone.utc) - last) > timedelta(hours=24)
    except Exception:
        return True


def send_alert_gmail(subject: str, body: str) -> bool:
    """Cria draft no Gmail piggybackando token Google de AUTOMAÇÕES. Retorna True se ok."""
    sys.path.insert(0, str(AUTOMACOES_TOOLS))
    try:
        from gws.gws_auth import get_credentials  # type: ignore
        from googleapiclient.discovery import build  # type: ignore
    except Exception as e:
        print(f"[health] Gmail import falhou: {e}", file=sys.stderr)
        return False
    try:
        creds = get_credentials()
        service = build("gmail", "v1", credentials=creds, cache_discovery=False)
        msg = MIMEText(body, _charset="utf-8")
        msg["to"] = ALERT_EMAIL_TO
        msg["subject"] = subject
        raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
        service.users().drafts().create(userId="me", body={"message": {"raw": raw}}).execute()
        return True
    except Exception as e:
        print(f"[health] Gmail draft falhou: {e}", file=sys.stderr)
        return False


def run_health_check(today: str) -> None:
    health = health_check(today)
    if health["ok"]:
        if HEALTH_ALERT_FILE.exists():
            HEALTH_ALERT_FILE.unlink()
        return

    body = (
        f"Sync NTICS: detecção de gap.\n\n"
        f"Hoje: {today}\n"
        f"Últimos {HEALTH_LOOKBACK_DAYS} dias esperados: {health['esperados']}\n"
        f"Faltando: {health['faltando']}\n"
        f"Presentes (recentes): {health['presentes']}\n\n"
        f"Verificações sugeridas:\n"
        f"  - schtasks /Query /TN \"NTICS-sync-all-active\" /V /FO LIST\n"
        f"  - tail output/sync/cron.log\n"
        f"  - python tools/sync/sync_all_active.py  (rodar manual)\n"
    )
    HEALTH_ALERT_FILE.write_text(body, encoding="utf-8")
    print(f"[health] ALERTA: {len(health['faltando'])} dia(s) sem resumo nos últimos {HEALTH_LOOKBACK_DAYS}.", file=sys.stderr)

    if should_renotify():
        if send_alert_gmail(f"[NTICS sync] gap detectado em {today}", body):
            HEALTH_LAST_NOTIFIED.touch()
            print("[health] Draft Gmail criado.", file=sys.stderr)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--only", default="", help="Lista de slugs separados por vírgula")
    parser.add_argument("--log-to", default="", help="Arquivo onde redireciona stdout+stderr (append)")
    args = parser.parse_args()

    if args.log_to:
        try:
            log_path = Path(args.log_to)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            log_fh = open(log_path, "a", encoding="utf-8", buffering=1)
            log_fh.write(f"\n=== run @ {datetime.now(timezone.utc).isoformat()} ===\n")
            sys.stdout = log_fh
            sys.stderr = log_fh
        except Exception as e:
            print(f"[warn] --log-to falhou: {e}", file=sys.stderr)

    only = set(s.strip() for s in args.only.split(",") if s.strip()) if args.only else None
    slugs = discover_projects(only)
    if not slugs:
        print("Nenhum projeto com tasks.yaml encontrado.", file=sys.stderr)
        sys.exit(0)

    print(f"> Sincronizando {len(slugs)} projeto(s)...", file=sys.stderr)
    results = []
    for slug in slugs:
        print(f"  · {slug}", file=sys.stderr)
        results.append(run_sync_one(slug, args.dry_run))

    hoje = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    resumo = render_resumo(results, hoje)

    SYNC_OUT.mkdir(parents=True, exist_ok=True)
    out_path = SYNC_OUT / f"{hoje}-resumo.md"
    out_path.write_text(resumo, encoding="utf-8")
    print(f"[ok] Resumo salvo em {out_path}", file=sys.stderr)
    print(resumo)

    # Self-check de saúde: gap de N dias dispara draft Gmail.
    run_health_check(hoje)


if __name__ == "__main__":
    main()
