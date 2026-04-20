"""Gamma API: cria deck a partir de um arquivo .md de input e faz polling ate completar.

Uso:
    python gamma_create.py <input.md> [--format presentation|document|social]
                                       [--text-mode preserve|generate|condense]
                                       [--num-cards N]
                                       [--theme NOME]
                                       [--language pt-br|en]

Variaveis de ambiente:
    GAMMA_API_KEY  -> obrigatorio. Pegue em gamma.app/account/api
"""
import argparse
import json
import os
import sys
import time
from pathlib import Path

import urllib.request
import urllib.error

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parents[2] / ".env")
except ImportError:
    pass

API_BASE = "https://public-api.gamma.app/v1.0"


UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"


def post(path: str, api_key: str, body: dict) -> dict:
    req = urllib.request.Request(
        f"{API_BASE}{path}",
        data=json.dumps(body).encode("utf-8"),
        headers={
            "X-API-KEY": api_key,
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": UA,
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        sys.stderr.write(f"HTTP {e.code}: {e.read().decode('utf-8', 'ignore')}\n")
        raise


def get(path: str, api_key: str) -> dict:
    req = urllib.request.Request(
        f"{API_BASE}{path}",
        headers={
            "X-API-KEY": api_key,
            "Accept": "application/json",
            "User-Agent": UA,
        },
        method="GET",
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("input_file")
    p.add_argument("--format", default="presentation",
                   choices=["presentation", "document", "social", "webpage"])
    p.add_argument("--text-mode", default="preserve",
                   choices=["preserve", "generate", "condense"])
    p.add_argument("--card-split", default="inputTextBreaks",
                   choices=["inputTextBreaks", "auto"])
    p.add_argument("--num-cards", type=int, default=None)
    p.add_argument("--language", default="pt-br")
    p.add_argument("--tone", default="instructional, friendly, professor-to-professor")
    p.add_argument("--audience", default="professores de ensino fundamental e medio")
    p.add_argument("--amount", default="detailed",
                   choices=["brief", "medium", "detailed"])
    p.add_argument("--image-style", default="modern educational illustration, clean, friendly")
    p.add_argument("--image-source", default="aiGenerated")
    p.add_argument("--image-model", default="imagen-4-pro")
    p.add_argument("--dimensions", default="16x9")
    p.add_argument("--export", default=None, choices=[None, "pptx", "pdf", "png"])
    p.add_argument("--poll-interval", type=int, default=10)
    p.add_argument("--poll-timeout", type=int, default=600)
    p.add_argument("--api-key", default=os.environ.get("GAMMA_API_KEY"))
    p.add_argument("--additional-instructions", default="")
    args = p.parse_args()

    if not args.api_key:
        sys.exit("GAMMA_API_KEY nao definido (env ou --api-key)")

    text = Path(args.input_file).read_text(encoding="utf-8")
    if not text.strip():
        sys.exit(f"Input vazio: {args.input_file}")

    body = {
        "inputText": text,
        "textMode": args.text_mode,
        "format": args.format,
        "cardSplit": args.card_split,
        "textOptions": {
            "amount": args.amount,
            "tone": args.tone,
            "audience": args.audience,
            "language": args.language,
        },
        "imageOptions": {
            "model": args.image_model,
            "style": args.image_style,
            "source": args.image_source,
        },
        "cardOptions": {"dimensions": args.dimensions},
    }
    if args.num_cards:
        body["numCards"] = args.num_cards
    if args.export:
        body["exportAs"] = args.export
    if args.additional_instructions:
        body["additionalInstructions"] = args.additional_instructions

    print(f"[gamma] criando ({len(text)} chars, format={args.format}, mode={args.text_mode})")
    res = post("/generations", args.api_key, body)
    gen_id = res.get("generationId")
    if not gen_id:
        sys.exit(f"Sem generationId na resposta: {res}")
    print(f"[gamma] generationId={gen_id}")

    deadline = time.time() + args.poll_timeout
    last_status = None
    while time.time() < deadline:
        time.sleep(args.poll_interval)
        st = get(f"/generations/{gen_id}", args.api_key)
        status = st.get("status")
        if status != last_status:
            print(f"[gamma] status={status}")
            last_status = status
        if status == "completed":
            url = st.get("gammaUrl")
            export_url = st.get("exportUrl")
            credits = st.get("credits")
            print(f"\n=== DECK PRONTO ===")
            print(f"URL:     {url}")
            if export_url:
                print(f"Export:  {export_url}")
            if credits:
                print(f"Credits: {json.dumps(credits)}")
            print(f"==================")
            return 0
        if status == "failed":
            sys.exit(f"[gamma] falhou: {json.dumps(st)}")
    sys.exit(f"[gamma] timeout apos {args.poll_timeout}s")


if __name__ == "__main__":
    raise SystemExit(main())
