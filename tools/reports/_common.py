"""Helpers compartilhados pelos scripts do relatório diário PMO."""

from __future__ import annotations

import os
import sys
import time
import json
import unicodedata
from pathlib import Path
from datetime import datetime, timezone, timedelta, date

import urllib3
import yaml
import requests
from dotenv import load_dotenv

# Windows: certifi doesn't include the Windows certificate store.
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = ROOT / "tools" / "reports" / "config" / "pmo_diario.yaml"
TMP_DIR = ROOT / ".tmp"
OUTPUT_DIR = ROOT / "output" / "relatorios" / "pmo-diario"

CLICKUP_BASE = "https://api.clickup.com/api/v2"
BR_TZ = timezone(timedelta(hours=-3))


def load_env():
    load_dotenv(ROOT / ".env", override=True)


def load_config() -> dict:
    with CONFIG_PATH.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def clickup_headers() -> dict:
    return {
        "Authorization": os.environ["CLICKUP_API_KEY"],
        "Content-Type": "application/json",
    }


def clickup_get(path: str, params: dict | None = None, max_retries: int = 3) -> dict:
    """GET com backoff exponencial em 429/5xx."""
    url = f"{CLICKUP_BASE}{path}"
    delay = 1.0
    for attempt in range(max_retries):
        r = requests.get(url, headers=clickup_headers(), params=params, timeout=30, verify=False)
        if r.status_code == 429 or r.status_code >= 500:
            if attempt == max_retries - 1:
                r.raise_for_status()
            time.sleep(delay)
            delay *= 2
            continue
        r.raise_for_status()
        return r.json()
    raise RuntimeError(f"Falha após {max_retries} tentativas: {url}")


def normalize(text: str) -> str:
    """lowercase + remove acentos. Para comparar status/tags sem se preocupar com acento."""
    if not text:
        return ""
    nfkd = unicodedata.normalize("NFKD", text)
    return "".join(c for c in nfkd if not unicodedata.combining(c)).lower().strip()


def in_set_normalized(text: str, options: list[str]) -> bool:
    n = normalize(text)
    return any(normalize(o) == n for o in options)


def epoch_ms_to_datetime(value: str | int | None):
    if value in (None, "", "null"):
        return None
    try:
        ms = int(value)
    except (TypeError, ValueError):
        return None
    return datetime.fromtimestamp(ms / 1000, tz=BR_TZ)


def now_brt() -> datetime:
    return datetime.now(BR_TZ)


def today_brt() -> date:
    return now_brt().date()


def ensure_dirs():
    TMP_DIR.mkdir(exist_ok=True, parents=True)
    OUTPUT_DIR.mkdir(exist_ok=True, parents=True)


def setup_utf8_stdout():
    """Windows: força UTF-8 no stdout/stderr para emojis e acentos."""
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


def write_json(path: Path, data) -> None:
    path.parent.mkdir(exist_ok=True, parents=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, default=str), encoding="utf-8")


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))
