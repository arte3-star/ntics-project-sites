"""Renomeia fotos de assets/melhores-fotos/ com descricao do conteudo via Haiku 4.5.

Padrao: {NN}_{programa-slug}_{categoria}_{cena}[_{patrocinador}].jpg
Gera _INDEX.csv por pasta com descricao completa para busca textual.

Uso:
    python tools/media/renomear_melhores_fotos.py --folder "5. ROBOTICA NAS ESCOLAS"
    python tools/media/renomear_melhores_fotos.py --all
    python tools/media/renomear_melhores_fotos.py --all --dry-run
"""
from __future__ import annotations

import argparse
import base64
import csv
import json
import os
import re
import sys
import unicodedata
from pathlib import Path

import anthropic
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

ROOT = Path(__file__).resolve().parents[2]
PHOTOS_ROOT = ROOT / "assets" / "melhores-fotos"

# Slug fixo por pasta (para nao depender de Haiku inferir programa)
FOLDER_SLUGS = {
    "1. CONHECENDO OS ODS NAS ESCOLAS": "ods-escolas",
    "2. PEC   PIE   PED": "pec-pie-ped",
    "3. CAMINHÃO HÁBITOS SAUDÁVEIS": "caminhao-habitos-saudaveis",
    "4. FESTIVAL CONHECENDO OS ODS": "festival-ods",
    "5. ROBÓTICA NAS ESCOLAS": "robotica-escolas",
    "6. CAMINHAO CONHECENDO OS ODS": "caminhao-ods",
    "7. CULINÁRIA SUSTENTÁVEL": "culinaria-sustentavel",
    "8. FESTIVAL CINEGASTROARTE": "festival-cinegastroarte",
    "9 - HUB ESG no AGRO": "hub-agro",
    "10 - Negócio Cultural": "negocio-cultural",
    "11 -  CIRCO": "circo",
    "OFICINA DE FOTOGRAFIA": "oficina-fotografia",
    "PEÇAS TEATRAIS": "pecas-teatrais",
}

# Ja no padrao: NN_slug_categoria_... (skip)
ALREADY_NAMED = re.compile(r"^\d{2,3}_[a-z0-9-]+_[a-z]+_", re.IGNORECASE)

EXTS = {".jpg", ".jpeg", ".png", ".webp"}

SYSTEM_PROMPT = """Voce analisa fotos de projetos sociais/educacionais da NTICS Projetos.
Retorna APENAS JSON valido, sem markdown, sem explicacao.

Formato:
{
  "categoria": "uma-palavra-em-portugues",
  "cena": "sujeito-e-acao-3-a-6-palavras-separadas-por-hifen",
  "detalhes": "descricao completa da foto em 1-2 frases para busca textual",
  "patrocinador": "nome-da-logo-visivel-ou-null"
}

Regras:
- categoria: 1 palavra lowercase sem acento (ex: oficina, teatro, plateia, palestra, crianca, culinaria, robotica, evento, bastidor)
- cena: 3-6 palavras lowercase sem acento, separadas por hifen, descreve sujeito+acao+contexto visual
  bom: "crianca-montando-kit-robotica"
  bom: "mulher-falando-microfone-painel"
  ruim: "foto" / "imagem-bonita"
- detalhes: frase natural em portugues para busca textual rica (roupas, ambiente, expressoes, objetos)
- patrocinador: SO se houver logo/marca visivel de empresa (ex: "samarco", "statkraft", "gru-airport", "sylvamo"). Se so tiver logo NTICS ou nenhuma logo, retorna null."""


def slugify(text: str) -> str:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    text = re.sub(r"[^a-zA-Z0-9]+", "-", text).strip("-").lower()
    return text


def encode_image(path: Path, max_bytes: int = 3_500_000) -> tuple[str, str]:
    data = path.read_bytes()
    # Se muito grande, reduz via PIL
    if len(data) > max_bytes:
        from PIL import Image
        import io
        img = Image.open(path)
        img.thumbnail((1600, 1600))
        buf = io.BytesIO()
        img.convert("RGB").save(buf, format="JPEG", quality=80)
        data = buf.getvalue()
        media = "image/jpeg"
    else:
        ext = path.suffix.lower()
        media = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png", ".webp": "image/webp"}.get(ext, "image/jpeg")
    return base64.standard_b64encode(data).decode(), media


def analyze_photo(client: anthropic.Anthropic, path: Path, programa_context: str) -> dict:
    b64, media = encode_image(path)
    resp = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=300,
        system=SYSTEM_PROMPT,
        messages=[{
            "role": "user",
            "content": [
                {"type": "image", "source": {"type": "base64", "media_type": media, "data": b64}},
                {"type": "text", "text": f"Programa: {programa_context}. Analisa a foto."},
            ],
        }],
    )
    text = resp.content[0].text.strip()
    # Limpa cercas eventuais
    text = re.sub(r"^```(?:json)?|```$", "", text, flags=re.MULTILINE).strip()
    return json.loads(text)


def process_folder(folder: Path, client: anthropic.Anthropic, dry_run: bool = False) -> None:
    slug = FOLDER_SLUGS.get(folder.name)
    if not slug:
        print(f"[skip] {folder.name} (sem slug)")
        return

    images = sorted([p for p in folder.rglob("*") if p.suffix.lower() in EXTS])
    if not images:
        return

    print(f"\n=== {folder.name} ({len(images)} imgs) ===")
    index_path = folder / "_INDEX.csv"

    # Anexa em INDEX existente se houver
    existing_rows = []
    existing_new_names = set()
    if index_path.exists():
        with index_path.open(encoding="utf-8") as f:
            existing_rows = list(csv.DictReader(f))
            existing_new_names = {r["novo"] for r in existing_rows}

    rows = list(existing_rows)
    # Conta NN ja usados
    nn_used = set()
    for p in images:
        m = re.match(r"^(\d{2,3})_", p.name)
        if m:
            nn_used.add(int(m.group(1)))
    nn_counter = max(nn_used) if nn_used else 0

    for img in images:
        if ALREADY_NAMED.match(img.name):
            print(f"  [ok ] {img.name}")
            continue

        try:
            meta = analyze_photo(client, img, folder.name)
        except Exception as e:
            print(f"  [err] {img.name}: {e}")
            continue

        nn_counter += 1
        nn = f"{nn_counter:03d}"
        cena = slugify(meta.get("cena", "sem-cena"))[:60]
        categoria = slugify(meta.get("categoria", "foto"))[:20]
        patrocinador = meta.get("patrocinador")
        patrocinador_slug = slugify(patrocinador) if patrocinador else None

        parts = [nn, slug, categoria, cena]
        if patrocinador_slug:
            parts.append(patrocinador_slug)
        new_name = "_".join(parts) + img.suffix.lower()

        # Evita colisao
        counter = 2
        while new_name in existing_new_names or (img.parent / new_name).exists() and (img.parent / new_name) != img:
            new_name = "_".join(parts + [f"v{counter}"]) + img.suffix.lower()
            counter += 1
        existing_new_names.add(new_name)

        print(f"  [new] {img.name}  ->  {new_name}")
        print(f"        {meta.get('detalhes', '')[:90]}")

        if not dry_run:
            new_path = img.parent / new_name
            img.rename(new_path)

        rows.append({
            "antigo": img.name,
            "novo": new_name,
            "categoria": meta.get("categoria", ""),
            "cena": meta.get("cena", ""),
            "detalhes": meta.get("detalhes", ""),
            "patrocinador": patrocinador or "",
            "subpasta": str(img.parent.relative_to(folder)) if img.parent != folder else "",
        })

        if not dry_run and len(rows) % 10 == 0:
            _write_index(index_path, rows)

    if not dry_run:
        _write_index(index_path, rows)
    print(f"  -> INDEX: {index_path}")


def _write_index(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["antigo", "novo", "categoria", "cena", "detalhes", "patrocinador", "subpasta"])
        w.writeheader()
        w.writerows(rows)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--folder", help="Nome exato da subpasta (usa --all se omitido)")
    ap.add_argument("--all", action="store_true", help="Processa todas as pastas conhecidas")
    ap.add_argument("--dry-run", action="store_true", help="So imprime, nao renomeia")
    args = ap.parse_args()

    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        sys.exit("ANTHROPIC_API_KEY ausente no .env")
    client = anthropic.Anthropic(api_key=key)

    if args.folder:
        folder = PHOTOS_ROOT / args.folder
        if not folder.exists():
            sys.exit(f"Pasta nao existe: {folder}")
        process_folder(folder, client, dry_run=args.dry_run)
    elif args.all:
        for name in FOLDER_SLUGS:
            folder = PHOTOS_ROOT / name
            if folder.exists():
                process_folder(folder, client, dry_run=args.dry_run)
    else:
        ap.error("use --folder NOME ou --all")


if __name__ == "__main__":
    main()
