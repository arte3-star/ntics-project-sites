"""
enrich_projects_metadata.py

One-shot (idempotente) que enriquece assets/projetos/_metadata-sites-2026.json
com 3 campos derivados do SecondBrain:

  - status       : "ativo" | "planejamento" | "encerrado"
  - start_date   : "YYYY-MM-DD"
  - end_date     : "YYYY-MM-DD"

Fonte de verdade, em ordem:
  1. frontmatter do README.md de SecondBrain/projetos/{codigo}-*/
     (status textual -> mapeado; ano para ano base)
  2. tap.md "Periodo Macro" no bloco "0) Identificacao"
  3. fallback: string `period` do proprio JSON ("Fevereiro a Marco de 2026")

Uso:
  python tools/publishing/enrich_projects_metadata.py --dry-run
  python tools/publishing/enrich_projects_metadata.py
  python tools/publishing/enrich_projects_metadata.py --project 116_cultura_robotica
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from calendar import monthrange
from datetime import date
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent.parent
JSON_PATH = REPO_ROOT / "assets" / "projetos" / "_metadata-sites-2026.json"
PROJETOS_DIR = REPO_ROOT / "SecondBrain" / "projetos"

MES_PT_TO_NUM = {
    "janeiro": 1, "fevereiro": 2, "marco": 3, "abril": 4,
    "maio": 5, "junho": 6, "julho": 7, "agosto": 8,
    "setembro": 9, "outubro": 10, "novembro": 11, "dezembro": 12,
    # abreviacoes usadas em TAPs ("Fev/2026")
    "jan": 1, "fev": 2, "mar": 3, "abr": 4, "mai": 5, "jun": 6,
    "jul": 7, "ago": 8, "set": 9, "out": 10, "nov": 11, "dez": 12,
}

STATUS_MAP = {
    "execucao": "ativo",
    "em execucao": "ativo",
    "ativo": "ativo",
    "em_execucao": "ativo",
    "planejamento": "planejamento",
    "em planejamento": "planejamento",
    "encerrado": "encerrado",
    "fechamento": "encerrado",
    "em fechamento": "encerrado",
    "concluido": "encerrado",
}


def _norm(s: str) -> str:
    """lowercase + remove acentos, para comparar mes/status."""
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return s.lower().strip()


def _project_code(project_id: str) -> str | None:
    """'116_cultura_robotica' -> '116'."""
    m = re.match(r"^(\d+)", project_id or "")
    return m.group(1) if m else None


def _find_project_folder(code: str) -> Path | None:
    if not code:
        return None
    for p in PROJETOS_DIR.iterdir():
        if p.is_dir() and p.name.startswith(f"{code}-"):
            return p
    return None


def _parse_frontmatter(md_path: Path) -> dict:
    """Parser minimo de YAML frontmatter. Suporta escalares e listas inline."""
    if not md_path.exists():
        return {}
    text = md_path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {}
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}
    fm_raw = parts[1]
    out: dict = {}
    for line in fm_raw.splitlines():
        line = line.rstrip()
        if not line or line.lstrip().startswith("#"):
            continue
        if ":" not in line:
            continue
        key, _, val = line.partition(":")
        key = key.strip()
        val = val.strip()
        if "#" in val and not val.startswith('"'):
            val = val.split("#", 1)[0].strip()
        if val.startswith("[") and val.endswith("]"):
            inner = val[1:-1].strip()
            out[key] = [x.strip().strip('"').strip("'") for x in inner.split(",") if x.strip()]
        else:
            out[key] = val.strip('"').strip("'")
    return out


def _parse_period_macro_from_tap(tap_path: Path) -> tuple[str, str] | None:
    """Extrai "Periodo Macro | Fev/2026 -> Mar/2026" ou variacoes."""
    if not tap_path.exists():
        return None
    text = tap_path.read_text(encoding="utf-8")
    # Pega linha que contem "periodo macro"
    for line in text.splitlines():
        if _norm(line).startswith("| periodo macro") or "periodo macro" in _norm(line):
            return _parse_period_range(line)
    return None


def _parse_period_range(text: str) -> tuple[str, str] | None:
    """
    Tenta extrair (start_date, end_date) de strings livres tipo:
      "Fev/2026 -> Mar/2026"
      "Fevereiro a Marco de 2026"
      "Fevereiro -> Junho 2026"
      "Marco/2026 a Abril/2026"
    """
    t = _norm(text)
    # Ano(s)
    years = [int(y) for y in re.findall(r"20\d{2}", text)]
    if not years:
        return None
    start_year = years[0]
    end_year = years[-1]

    # Meses na ordem que aparecem
    months_found: list[int] = []
    for token in re.findall(r"[a-z]+", t):
        if token in MES_PT_TO_NUM:
            months_found.append(MES_PT_TO_NUM[token])
    # Deduplicar preservando ordem
    seen = set()
    months = []
    for m in months_found:
        if m not in seen:
            months.append(m)
            seen.add(m)

    if not months:
        return None
    start_month = months[0]
    end_month = months[-1]

    start = date(start_year, start_month, 1)
    last_day = monthrange(end_year, end_month)[1]
    end = date(end_year, end_month, last_day)
    return (start.isoformat(), end.isoformat())


def _derive_dates(project: dict, folder: Path | None, fm: dict) -> tuple[str, str] | None:
    """Prioridade: TAP periodo macro > period string do JSON > README texto."""
    if folder is not None:
        tap_dates = _parse_period_macro_from_tap(folder / "tap.md")
        if tap_dates:
            return tap_dates

    period_json = project.get("period", "")
    if period_json:
        d = _parse_period_range(period_json)
        if d:
            return d

    # Fallback: procurar linha "Periodo:" no README
    if folder is not None:
        readme = folder / "README.md"
        if readme.exists():
            for line in readme.read_text(encoding="utf-8").splitlines():
                ln = _norm(line)
                if ln.startswith("**periodo") or ln.startswith("periodo:") or ln.startswith("- **periodo"):
                    d = _parse_period_range(line)
                    if d:
                        return d

    # Ultimo fallback: so o ano
    ano = fm.get("ano")
    if ano and re.match(r"^\d{4}$", str(ano)):
        y = int(ano)
        return (f"{y}-01-01", f"{y}-12-31")
    return None


def _derive_status(fm: dict, start_iso: str | None, end_iso: str | None, today: date) -> str:
    """status explicito do frontmatter > inferencia por data."""
    raw = _norm(fm.get("status", "")) if fm else ""
    if raw in STATUS_MAP:
        return STATUS_MAP[raw]
    # Inferencia
    if start_iso and end_iso:
        s = date.fromisoformat(start_iso)
        e = date.fromisoformat(end_iso)
        if today < s:
            return "planejamento"
        if today > e:
            return "encerrado"
        return "ativo"
    return "planejamento"


def enrich_project(project: dict, today: date) -> dict:
    code = _project_code(project.get("id", ""))
    folder = _find_project_folder(code) if code else None
    fm = _parse_frontmatter(folder / "README.md") if folder else {}

    dates = _derive_dates(project, folder, fm)
    if dates:
        start_iso, end_iso = dates
    else:
        start_iso, end_iso = None, None

    status = _derive_status(fm, start_iso, end_iso, today)

    enriched = dict(project)
    enriched["status"] = status
    if start_iso:
        enriched["start_date"] = start_iso
    if end_iso:
        enriched["end_date"] = end_iso
    return enriched


def main() -> int:
    ap = argparse.ArgumentParser(description="Enriquece _metadata-sites-2026.json com status e datas")
    ap.add_argument("--dry-run", action="store_true", help="mostra diff sem gravar")
    ap.add_argument("--project", help="enriquece apenas o projeto com este id")
    ap.add_argument("--json-path", default=str(JSON_PATH))
    args = ap.parse_args()

    json_path = Path(args.json_path)
    projects: list = json.loads(json_path.read_text(encoding="utf-8"))
    today = date.today()

    changes = []
    for i, p in enumerate(projects):
        if args.project and p.get("id") != args.project:
            continue
        before = {k: p.get(k) for k in ("status", "start_date", "end_date")}
        enriched = enrich_project(p, today)
        after = {k: enriched.get(k) for k in ("status", "start_date", "end_date")}
        if before != after:
            changes.append((p.get("id"), before, after))
            projects[i] = enriched

    print(f"Projetos avaliados: {len(projects)}")
    print(f"Mudancas: {len(changes)}")
    for pid, b, a in changes:
        print(f"  - {pid}")
        print(f"      antes: {b}")
        print(f"      depois: {a}")

    if args.dry_run:
        print("\n[dry-run] nenhum arquivo foi gravado.")
        return 0

    if changes:
        json_path.write_text(
            json.dumps(projects, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        print(f"\nOK gravado em {json_path}")
    else:
        print("\nNada a gravar (ja estava atualizado).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
