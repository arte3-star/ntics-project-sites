"""
Seleção automatizada de fotos NTICS via Claude Vision API.
Analisa, classifica (A-E), renomeia e copia melhores para subpasta.
"""

import os
import sys
import json
import base64
import shutil
import re
import time
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

import anthropic

client = anthropic.Anthropic()

VISION_PROMPT = """Você é um curador de fotos para a NTICS Projetos (ONG de impacto social: educação, cultura, sustentabilidade).

Avalie esta foto de projeto social usando estas 6 dimensões (peso entre parênteses):
- Nitidez/Foco (15%)
- Exposição & Cor (15%)
- Composição (20%)
- Emoção/História (20%)
- Scroll-Stop Power (15%)
- Brand Fit NTICS (15%)

Padrão cinematográfico: enquadramento próximo/médio, emoção de pico, luz direcional, bokeh, história em um frame.

Responda APENAS em JSON, sem markdown:
{"nota": "A", "categoria": "culinaria", "descricao": "educadora-criancas-avental-sorrindo"}

Notas:
A = Excepcional, publicar direto no Instagram
B = Muito boa, publicável com mínima edição
C = Adequada para relatórios, não para social
D = Aceitável como evidência, qualidade baixa
E = Descartar

Categoria: uma palavra entre culinaria/tecnologia/branding/atividade/oficina/apresentacao/grupo/palco/exposicao/fotografia/esporte/teatro/evento/reciclagem
Descrição: 3-5 palavras hifenizadas, sem acentos, descrevendo o conteúdo principal.

O nome do projeto é: {projeto}"""


def analyze_photo(image_path: Path, projeto: str) -> dict | None:
    """Send a single photo to Claude Vision and get rating."""
    try:
        with open(image_path, "rb") as f:
            img_data = base64.standard_b64encode(f.read()).decode("utf-8")

        ext = image_path.suffix.lower()
        media_type = "image/jpeg" if ext in (".jpg", ".jpeg") else "image/png"

        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=150,
            messages=[{
                "role": "user",
                "content": [
                    {"type": "image", "source": {"type": "base64", "media_type": media_type, "data": img_data}},
                    {"type": "text", "text": VISION_PROMPT.format(projeto=projeto)}
                ]
            }]
        )

        text = response.content[0].text.strip()
        # Try to parse JSON from response
        # Remove markdown fences if present
        text = re.sub(r'^```json?\s*', '', text)
        text = re.sub(r'\s*```$', '', text)
        return json.loads(text)
    except json.JSONDecodeError as e:
        print(f"  ⚠ JSON parse error for {image_path.name}: {e} | raw: {text[:200]}")
        return None
    except Exception as e:
        print(f"  ✗ Error analyzing {image_path.name}: {e}")
        return None


def sanitize_filename(s: str) -> str:
    """Remove accents and special chars for filenames."""
    replacements = {
        'á': 'a', 'à': 'a', 'ã': 'a', 'â': 'a',
        'é': 'e', 'è': 'e', 'ê': 'e',
        'í': 'i', 'ì': 'i', 'î': 'i',
        'ó': 'o', 'ò': 'o', 'õ': 'o', 'ô': 'o',
        'ú': 'u', 'ù': 'u', 'û': 'u',
        'ç': 'c', 'ñ': 'n',
    }
    result = s.lower()
    for k, v in replacements.items():
        result = result.replace(k, v)
    return result


def process_folder(folder_path: str, projeto_slug: str, skip_files: set = None, preset_renames: dict = None):
    """Process all JPGs in a folder: analyze, rename, copy A/B to fotos selecionadas."""
    folder = Path(folder_path)
    if not folder.exists():
        print(f"✗ Folder not found: {folder}")
        return

    print(f"\n{'='*60}")
    print(f"📁 {projeto_slug} — {folder}")
    print(f"{'='*60}")

    # Collect JPGs (not in subfolders, not .CR2/.ARW)
    jpgs = sorted([
        f for f in folder.iterdir()
        if f.is_file() and f.suffix.lower() in ('.jpg', '.jpeg')
        and not f.name.startswith('.')
        and 'desktop.ini' not in f.name
    ])

    print(f"  Found {len(jpgs)} JPG files")

    renames = {}  # old_name -> (new_name, nota)

    # Apply preset renames (from handoff)
    if preset_renames:
        for old_name, (new_name, nota) in preset_renames.items():
            renames[old_name] = (new_name, nota)
            print(f"  📋 Preset: {old_name} → {new_name} [{nota}]")

    # Skip files already processed
    skip_files = skip_files or set()

    # Analyze remaining files
    to_analyze = [f for f in jpgs if f.name not in renames and f.name not in skip_files]
    print(f"  To analyze: {len(to_analyze)} photos")

    for i, photo in enumerate(to_analyze, 1):
        print(f"  [{i}/{len(to_analyze)}] Analyzing {photo.name}...", end=" ", flush=True)
        result = analyze_photo(photo, projeto_slug)
        if result:
            nota = result.get("nota", "C").upper()
            cat = sanitize_filename(result.get("categoria", "atividade"))
            desc = sanitize_filename(result.get("descricao", "sem-descricao"))
            new_name = f"{projeto_slug}_{cat}_{nota}_{desc}{photo.suffix.lower()}"
            renames[photo.name] = (new_name, nota)
            print(f"→ {nota} ({cat})")
        else:
            # Default to C if analysis fails
            new_name = f"{projeto_slug}_atividade_C_analise-falhou{photo.suffix.lower()}"
            renames[photo.name] = (new_name, "C")
            print(f"→ C (fallback)")

        # Small delay to avoid rate limits
        if i % 10 == 0:
            time.sleep(1)

    # Execute renames
    print(f"\n  Renaming {len(renames)} files...")
    renamed_files = {}  # new_path for A/B copy
    rename_conflicts = {}  # track used names to avoid collisions

    for old_name, (new_name, nota) in renames.items():
        old_path = folder / old_name
        if not old_path.exists():
            print(f"  ⚠ File not found, skipping: {old_name}")
            continue

        # Handle name collisions
        base_new = new_name
        counter = 2
        while new_name in rename_conflicts:
            stem, ext = os.path.splitext(base_new)
            new_name = f"{stem}-{counter}{ext}"
            counter += 1
        rename_conflicts[new_name] = True

        new_path = folder / new_name
        try:
            old_path.rename(new_path)
            renamed_files[new_name] = (new_path, nota)
            print(f"  ✓ {old_name} → {new_name}")
        except Exception as e:
            print(f"  ✗ Failed to rename {old_name}: {e}")

    # Create fotos selecionadas and copy A/B
    sel_folder = folder / "fotos selecionadas"
    sel_folder.mkdir(exist_ok=True)

    ab_count = 0
    for new_name, (new_path, nota) in renamed_files.items():
        if nota in ("A", "B"):
            try:
                shutil.copy2(new_path, sel_folder / new_name)
                ab_count += 1
            except Exception as e:
                print(f"  ✗ Failed to copy {new_name}: {e}")

    print(f"\n  ✅ Done! {ab_count} photos (A/B) copied to fotos selecionadas/")
    return renames


def main():
    # ── 1. GASTRONOMIA TAMBÉM É ARTE (2025) — finalize ──
    gastro_path = "G:/.shortcut-targets-by-id/1q8_C64qkkJy-E-0U7cyVtRGZVXQ5pB9e/MELHORES FOTOS - 2025/GASTRONOMIA TAMBÉM É ARTE   FOTOS"

    # Preset renames from handoff (15 already evaluated)
    gastro_presets = {
        "Cópia de 1Q0A0858.jpg": ("gastronomia-arte_branding_B_pilha-cartilhas-gastronomia-arte.jpg", "B"),
        "Cópia de 1Q0A0859.jpg": ("gastronomia-arte_branding_B_sacolas-logos-gastronomia-whirlpool.jpg", "B"),
        "Cópia de 1Q0A0874.jpg": ("gastronomia-arte_atividade_C_mulher-lendo-cartilha-costas.jpg", "C"),
        "Cópia de 1Q0A1066.jpg": ("gastronomia-arte_culinaria_A_educadora-criancas-avental-sorrindo.jpg", "A"),
        "Cópia de 1Q0A1073.jpg": ("gastronomia-arte_grupo_B_grupo-grande-avental-formatura.jpg", "B"),
        "Cópia de 20250815_164438.jpg": ("gastronomia-arte_exposicao_C_paineis-sala-vazia.jpg", "C"),
        "Cópia de Cópia de Cópia de 1Q0A0871.jpg": ("gastronomia-arte_atividade_C_pessoa-lendo-cartilha-costas.jpg", "C"),
        "Cópia de Cópia de Cópia de 1Q0A1105.jpg": ("gastronomia-arte_culinaria_A_adultos-servindo-balcao-gastronomia.jpg", "A"),
        "Cópia de Cópia de Cópia de Oficina de Culinária 07.07.2025 - Lr135.jpg": ("gastronomia-arte_culinaria_B_participantes-mesas-aula-culinaria.jpg", "B"),
        "Cópia de Cópia de Cópia de Oficina de Culinária 07.07.2025 - Lr48.jpg": ("gastronomia-arte_culinaria_C_participantes-culinaria-07jul.jpg", "C"),
        "Cópia de Cópia de Cópia de Oficina de Culinária 07.07.2025 - Lr86.jpg": ("gastronomia-arte_culinaria_C_oficina-culinaria-07jul-lr86.jpg", "C"),
        "Cópia de Cópia de Cópia de Oficina de Culinária 14.07.2025 - Lr114.jpg": ("gastronomia-arte_culinaria_B_participantes-culinaria-14jul-lr114.jpg", "B"),
        "Cópia de Cópia de Cópia de Oficina de Culinária 14.07.2025 - Lr54.jpg": ("gastronomia-arte_culinaria_C_oficina-culinaria-14jul-lr54.jpg", "C"),
        "Cópia de Cópia de Cópia de Oficina de Culinária 14.07.2025 - Lr76.jpg": ("gastronomia-arte_culinaria_B_participantes-atividade-culinaria-14jul.jpg", "B"),
        "Cópia de Cópia de Oficina de Culinária 27.09.2025 - Lr74.jpg": ("gastronomia-arte_culinaria_C_oficina-culinaria-27set-lr74.jpg", "C"),
    }

    process_folder(gastro_path, "gastronomia-arte", preset_renames=gastro_presets)

    # ── 2. ALL 25 FOLDERS FROM 2024 ──
    folders_2024 = [
        ("144ZJc0NoF-tWqlnJx2vzsb10SiELcJEX", "festival-cinegastroarte"),
        ("1uyXL8ufX4_MrIYEYgaGZm9_q1mqUlaYk", "circo-no-brasil"),
        ("1TDUXdDaEF6EzhXaKQXDcDXk7A0JXB_P3", "cpc"),
        ("1CG-fLpsiFu3ygnUeEtOrFnLoMLVS8fGc", "cultura-robotica-ferroporte"),
        ("1FT6SqdeWytfyfIYf0m7rulaUphKgZqSd", "robotica-cultural-mahle"),
        ("1pQiSubNam42AY7IjbyrzZt1AjOj8cKl1", "robotica-cultural-peroxidos"),
        ("18XYsVoBjNM_qTa9vQRVexudEmdOzL5J5", "teatro-oficinas-robotica-cnh"),
        ("1n_cpJkU3470n066xdTufyqyg7pnrLQhB", "empreendedorismo-3ed-cnh"),
        ("1uPePXkXQ4_QJ0JM2Hmb48KbuHDWAGp_j", "empreendedorismo-3ed-bic"),
        ("12-qi422ADABQwchqltnv_ZK9h5z4JxoF", "teatro-bons-habitos-ferroporte"),
        ("1EoSxDvgTuvGLAHXGqshenLsiAw5BL6uL", "culinaria-sustentavel-teleperformance"),
        ("1c3WZux8KOSuLM7EBumpAo44lt2T7GGot", "culinaria-sustentavel-enercan"),
        ("1CJ72V5btu7J0hMfP2ntg-AI1k20xoRpS", "caminhao-mhs-rabobank"),
        ("1mBxJnYXaheOPdwhgb_z12fN2EaNBy50a", "festival-artes-cultura-whirlpool"),
        ("136QiLGdqGhBNC93QLjU0cvU13AlJpP0P", "oficina-teatro-sustentavel-ferroport"),
        ("1rEqeCW3HAsH-qWPivqPGelrY1jgkK0hk", "oficina-teatro-sustentavel-cnh"),
        ("1iBTzkAqZIuHPMsLu2WkKgu8PBGL9HXha", "teatro-dos-ods-repsol"),
        ("1KpYenjKV84fGoz6mHsV7W4iMu3j0QiT4", "teatro-dos-ods-isa-cteep"),
        ("1QLF6qRF4LmDyfOl97b66Y4MRFn0XFiFA", "teatro-dos-ods-copergas"),
        ("13bkWbsdXZFywC_OB5-k4roRmH0sdZezW", "teatro-nas-escolas-ctg"),
        ("1YqDhyGk5BYFsNjGb5IxGlDv4aTBuHzTt", "caminhao-ods-moove"),
        ("1BFIn0vsQ8YkXVjzZCE3k4f_M1bCqhXVT", "caminhao-ods-tcp"),
        ("1fZVEh34PXCDCSMitMzJtzLdrdZi73WsU", "caminhao-reciclagem-jaepel"),
        ("1IyEpcr3RH4cNy5SJ3KLTddwf36k1iG1i", "conhecendo-os-ods-moove"),
        ("1ccAuHYYRPDpmew4CQ7P6SsVegYA_gyDo", "palestra-ods-anjo-quimica"),
    ]

    for drive_id, slug in folders_2024:
        folder_path = f"G:/.shortcut-targets-by-id/{drive_id}"
        # Check if folder exists, try to find actual subfolder
        base = Path(folder_path)
        if not base.exists():
            print(f"\n⚠ Cannot access: {folder_path}")
            continue

        # The shortcut might resolve to a folder with contents directly, or have a subfolder
        # List contents to find JPGs
        jpgs_direct = list(base.glob("*.jpg")) + list(base.glob("*.JPG"))
        if jpgs_direct:
            process_folder(str(base), slug)
        else:
            # Maybe there's a subfolder
            subdirs = [d for d in base.iterdir() if d.is_dir() and "selecionadas" not in d.name.lower()]
            if subdirs:
                for sd in subdirs:
                    jpgs_sub = list(sd.glob("*.jpg")) + list(sd.glob("*.JPG"))
                    if jpgs_sub:
                        process_folder(str(sd), slug)
            else:
                print(f"\n⚠ No JPGs found in {folder_path}")

    print("\n" + "="*60)
    print("🏁 SELEÇÃO DE FOTOS COMPLETA!")
    print("="*60)


if __name__ == "__main__":
    main()
