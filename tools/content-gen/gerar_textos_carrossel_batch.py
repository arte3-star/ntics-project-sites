#!/usr/bin/env python3
"""
gerar_textos_carrossel_batch.py

Gera textos dos 7 cards de conteudo + captions Instagram/LinkedIn para cada
task "Carrossel Projeto" da lista ClickUp, sem gerar imagens via Leonardo AI.
Atualiza a markdown_description de cada task com o briefing completo.

Uso:
  python tools/content-gen/gerar_textos_carrossel_batch.py
  python tools/content-gen/gerar_textos_carrossel_batch.py --dry-run
  python tools/content-gen/gerar_textos_carrossel_batch.py --semana S03
  python tools/content-gen/gerar_textos_carrossel_batch.py --task-id 868j1upwu

Fontes:
  - MAPPING abaixo: task_id + dados de cada projeto (mesmo do _update_carrossel_projeto_tasks.py)
  - SecondBrain/projetos-anteriores/{num}-*/README.md: texto rico para geracao
  - DRIVE_FOLDER_MAP: pasta Drive curada por numero de projeto (assets/projetos/ espelhado)

APIs:
  - Anthropic (claude-haiku-4-5-20251001): geracao de textos dos cards + captions
  - ClickUp API v2: atualizacao de markdown_description
"""

import os
import sys
import glob
import time
import json
import argparse
import re

import requests
import httpx
import anthropic
from dotenv import load_dotenv

load_dotenv()

CLICKUP_TOKEN = os.getenv("CLICKUP_API_KEY") or os.getenv("CLICKUP_TOKEN")
ANTHROPIC_KEY = os.getenv("ANTHROPIC_API_KEY")
BASE_URL = "https://api.clickup.com/api/v2"
CLICKUP_HEADERS = {"Authorization": CLICKUP_TOKEN, "Content-Type": "application/json"}

SB_BASE = "SecondBrain/projetos-anteriores"

# Mapa numero_projeto (int) -> Drive folder ID (pasta curada em assets/projetos/ no Drive)
# Descobertos via MCP Google Drive em 2026-05-16, pasta pai: 1IKnNdkdqgmdYP2US1vJO-B3OoekXcSiq
DRIVE_FOLDER_MAP = {
    50:  "1IeUPazGbQNncfEzvvs2QyKF4S-ZJS2j5",   # FESTIVAL CINEGASTROARTE
    60:  "1n8i25hmvk9q3oTFWIfLTi5HUTEqvEjdd",   # CIRCO NO BRASIL
    85:  "1yWzrx13nSyruVe7l_o912ajjGg8XSQJk",   # MEUS HABITOS 2ED (IMETAME)
    86:  "1Ljwdg2obVjOGg9stcaT2KFeTDxqhQEtS",   # TEATRO DOS BONS HABITOS (FERROPORTE)
    87:  "1Em6hvZ_1aD962cTMkEFUyl210THZqR5w",   # CULINARIA SUSTENTAVEL (IMETAME)
    88:  "117fEnJ8pCpJFyNBUzD0l1gfOPcLLww-3",   # FESTIVAL ARTE E CULTURA (WHIRLPOOL)
    89:  "1WGCvW6h4cOpdnidWc_ShA_HiAvlnUs6Z",   # OFICINA DE TEATRO SUSTENTAVEL (FERROPORT)
    90:  "1SVlSJeowU26YYp4qiKiOHrQToolPc-EE",   # TEATRO DOS ODS (REPSOL)
    91:  "1V1bntov1EuruMfROgTMMZOQA4-cfQJkL",   # TEATRO NAS ESCOLAS - ODS (CTG)
    92:  "1uh8VXrMAdbPHLGdZqh26EsFKfK45-lEH",   # CULTURA NA COMUNIDADE (RABOBANK)
    93:  "1ucQVt__Ys422jG2O5EhKDTNf1fi-y4-J",   # CAMINHAO ODS ARTISTICO
    98:  "1RBmP8eFqLVmsf7JTSFhSKnGj7pwvMJJb",   # CONHECENDO OS ODS (WILSON)
    103: "1dW2NotXNRui1zXh2ifKLpzGnPtfq3Vy3",   # GASTRONOMIA TAMBEM E ARTE (WHIRLPOOL)
    107: "162ZxQvyiddKunMCLIiKgUzLhlXdJtafd",   # TEATRO E OFICINA ROBOTICA 3ED (WHIRLPOOL)
    108: "1qRW-6JjS313sj4lq4PLp7mVCKG-a7_Xx",   # ODS CULTURAL NAS ESCOLAS (REPSOL)
    109: "1XqwkOLfugFCisw4jxB5Ytitw4cYsilE-",   # PEC EU FACO PARTE 2ED (STATKRAFT)
    110: "1o6fXg_zTZSRdpERnIG47rfliRkhIM329",   # CAMINHAO DA CULTURA E SUSTENTABILIDADE (JAEPEL)
    111: "11qDPQ9uv7WCIT-U5SeVcs1BJ9CzcbzIi",   # FESTIVAL ODS DAS ARTES - CAMINHAO ODS (RABOBANK)
}

# task_id, semana, num_projeto, nome_projeto, patrocinador, atendidos, relatorio, fotos_bruto, video
MAPPING = [
    ("868j1upu7", "S02", 50,    "Festival Cinegastroarte",       "—",          53262, "https://drive.google.com/drive/folders/1MZCXGw5voeLoQTGSXtpS2g1xpLHOD28C", "https://drive.google.com/drive/folders/144ZJc0NoF-tWqlnJx2vzsb10SiELcJEX", "https://youtu.be/4YNknU0eDqo"),
    ("868j1upwu", "S03", 111,   "Caminhao ODS",                  "Rabobank",   24063, "https://drive.google.com/file/d/1ux-JrC6pIkVbZiGXu8olYRPxhkvbQFvb/view", "https://drive.google.com/drive/folders/1yQvGP-kfvsFBRM4e0_KvBfYpcWF46EQ0", "https://drive.google.com/file/d/1dUUXvDgRc1eCQTORJ_srwXizZnwAw1d7/view"),
    ("868j1upv0", "S04", 60,    "Circo no Brasil",               "—",          20930, "https://drive.google.com/file/d/1lkYuHqCfB-jNLAeH7SShz_0nlzKmxMNh/view", "https://drive.google.com/drive/folders/1uyXL8ufX4_MrIYEYgaGZm9_q1mqUlaYk", "https://youtu.be/iENALeCLQnM"),
    ("868j1upv4", "S05", 88,    "Festival ODS Pocket",           "Whirlpool",  17646, "https://drive.google.com/file/d/1Iy24N-ubvgiT4wWFcE10ZXAZHRUKwRpb/view", "https://drive.google.com/drive/folders/1mBxJnYXaheOPdwhgb_z12fN2EaNBy50a", "https://youtu.be/2kMu-chR2qA"),
    ("868j1upv7", "S06", 92,    "Cultura na Comunidade",         "Rabobank",    9107, "https://drive.google.com/file/d/1Vu3Y05JEirBOjFjPx0HAf1-EoaqTEgWP/view", "https://drive.google.com/drive/u/0/folders/1CJ72V5btu7J0hMfP2ntg-AI1k20xoRpS", "https://youtu.be/H1ouuOtrNIE"),
    ("868j1upx2", "S07", 90,    "Teatro dos ODS",                "Repsol",      7210, "https://drive.google.com/file/d/1Qsq1S8kGFLjjOTDhAiT1pC-pW5qEB7kV/view", "https://drive.google.com/drive/u/0/folders/1iBTzkAqZIuHPMsLu2WkKgu8PBGL9HXha", "https://youtu.be/n6fN5kb6f5s"),
    ("868j1upx6", "S08", 108,   "ODS Cultural nas Escolas",      "Repsol",      7045, "https://drive.google.com/file/d/1cP_QrcL8q1VUKk_rvsvAViTfduyVzChn/view", "https://drive.google.com/drive/folders/1oR7HDoQnoLV5Nzc1J7PfSWO4eGk4ZrPl", "https://drive.google.com/file/d/1BzVxrjQGssC5dUjkJkrdr2lUi3VbaQ_o/view"),
    ("868j1upzv", "S09", 98,    "Conhecendo os ODS",             "Wilson Sons", 7045, "https://drive.google.com/drive/folders/1gobYgEMhZy-p_0oXrfIo0rlN679zLeWq", "https://drive.google.com/drive/folders/1EQ3gaiiz8AprsQ7KHGomC10wo3_DFRiL", "https://drive.google.com/drive/folders/1zkJ_ra1jvThc_zeAEe46bocPcYCjV5lX"),
    ("868j1uq30", "S10", 97,    "Conhecendo os ODS",             "Moove",       6032, "https://drive.google.com/file/d/1w-Ux_k8Z8kR12l4NeOCtinVNs4RTQK0u/view", "https://drive.google.com/drive/folders/1IyEpcr3RH4cNy5SJ3KLTddwf36k1iG1i", "https://youtu.be/kVt4KwdlUKQ"),
    ("868j1uq39", "S11", 107,   "Teatro e Oficina Robotica 3Ed", "Whirlpool",   5893, "https://drive.google.com/file/d/1xazMwdum_Ew_6YeiYBJKgMCBTH9iF3n9/view", "https://drive.google.com/drive/folders/1KNjZOGwEesCfF0y8l7IsC-jYZbcHlWw_", "https://drive.google.com/file/d/1WWo9UWyeTVIxr027jO3lDHxFmUw2dEPU/view"),
    ("868j1uq44", "S12", "93a", "Caminhao ODS Artistico",        "TCP",         5741, "https://drive.google.com/file/d/1kSsIBVfWoVR4Znjq75s4ug_oRLxE8qs0/view", "https://drive.google.com/drive/u/0/folders/1BFIn0vsQ8YkXVjzZCE3k4f_M1bCqhXVT", "https://youtu.be/wxT0gyL3SRA"),
    ("868j1uq4f", "S13", "93b", "Caminhao ODS Artistico",        "Moove",       5568, "https://drive.google.com/file/d/1kzwvyk_YOwvnop-fkpI-ssXwkTXuNkYF/view", "https://drive.google.com/drive/u/0/folders/1YqDhyGk5BYFsNjGb5IxGlDv4aTBuHzTt", "https://youtu.be/Ix4aErTsbqE"),
    ("868j1uq4t", "S14", 91,    "Caminhao Energia",              "CTG",         5532, "https://drive.google.com/file/d/1hSe74SrRckXFx674ev3g4hWA8Bojov7/view", "https://drive.google.com/drive/u/0/folders/13bkWbsdXZFywC_OB5-k4roRmH0sdZezW", "https://youtu.be/5oOZyQy_9FE"),
    ("868j1uq53", "S15", 103,   "Gastronomia Tambem e Arte",     "Whirlpool",   4414, "https://drive.google.com/file/d/19Enw68ah6iKcJQVsaTPgW2bc5R7_1IdV/view", "https://drive.google.com/drive/folders/1uRpRKc8AoQJon7P9drMHSdwTCT7O6Ktc", "https://youtu.be/7IByvjNUegA"),
    ("868j1uq5g", "S16", 87,    "Culinaria Sustentavel",         "Enercan",     4173, "https://drive.google.com/file/d/1WgI3Fm4marQcdbQ1P3jivkj3v2ayvW4V/view", "https://drive.google.com/drive/folders/1c3WZux8KOSuLM7EBumpAo44lt2T7GGot", "https://youtu.be/fkeCjDIHmno"),
    ("868j1uq4e", "S17", 89,    "Oficina Teatro Sustentavel",    "Ferroport",   4157, "https://drive.google.com/file/d/1AUsccvkp5GaAXScbhZuTOY3h_bxJe5ul/view", "https://drive.google.com/drive/folders/136QiLGdqGhBNC93QLjU0cvU13AlJpP0P", "https://youtu.be/XZoUilKuTUw"),
    ("868j1uq5h", "S18", 86,    "Teatro Bons Habitos",           "Ferroporte",  4080, "https://drive.google.com/file/d/1CEJvI0mYBw9JtzVC7k4H7Xb5AUxFZqdB/view", "https://drive.google.com/drive/folders/12-qi422ADABQwchqltnv_ZK9h5z4JxoF", "https://youtu.be/HjOhoGgKZXY"),
    ("868j1uq7j", "S19", 109,   "Educacao Cultural",             "Statkraft",   3356, "https://drive.google.com/file/d/1btI4lsFwRxbmozcn3JUjrAtRloahyU0f/view", "https://drive.google.com/drive/folders/15AEtyTCdH8UszEon00Bbg1FeSRqKvzkT", "https://drive.google.com/file/d/1bbxcNQ1EjrpiapEuZv-i5Ap9oMZAM2pn/view"),
    ("868j1uq8c", "S20", 110,   "Caminhao da Cultura",           "Jaepel",      3317, "https://drive.google.com/file/d/1enG2PAOibudA7W1pMmhQq6-cVmyFksTB6/view", "https://drive.google.com/drive/folders/1SQY61xbxIqXnVu9G7_SWEzzLZqDlNamD", "https://drive.google.com/file/d/1Bln0BByuxaF_Rim5GkRjt7KFt_1oKeRY/view"),
    ("868j1uqe9", "S21", 85,    "Meus Habitos 2Ed",              "Imetame",     3187, "https://drive.google.com/file/d/1bPs2ibE5QkZFBl1j-hiyZEqectb1rjne/view", "https://drive.google.com/drive/folders/1qa5N3IHb596N8vI4gDETc7O6Ktc", "https://youtu.be/BD7bU-aytVk"),
    ("868j1uqjy", "S22", 50,    "Festival Cinegastroarte",       "—",           53262, "https://drive.google.com/drive/folders/1MZCXGw5voeLoQTGSXtpS2g1xpLHOD28C", "https://drive.google.com/drive/folders/144ZJc0NoF-tWqlnJx2vzsb10SiELcJEX", "https://youtu.be/4YNknU0eDqo"),
    ("868j1uqpd", "S23", 111,   "Caminhao ODS",                  "Rabobank",    24063, "https://drive.google.com/file/d/1ux-JrC6pIkVbZiGXu8olYRPxhkvbQFvb/view", "https://drive.google.com/drive/folders/1yQvGP-kfvsFBRM4e0_KvBfYpcWF46EQ0", "https://drive.google.com/file/d/1dUUXvDgRc1eCQTORJ_srwXizZnwAw1d7/view"),
    ("868j1uqqk", "S24", 60,    "Circo no Brasil",               "—",           20930, "https://drive.google.com/file/d/1lkYuHqCfB-jNLAeH7SShz_0nlzKmxMNh/view", "https://drive.google.com/drive/folders/1uyXL8ufX4_MrIYEYgaGZm9_q1mqUlaYk", "https://youtu.be/iENALeCLQnM"),
]


def parse_num(num):
    """Retorna (int_num, suffix) de numeros como 93, '93a', '93b'."""
    if isinstance(num, int):
        return num, None
    s = str(num)
    m = re.match(r"(\d+)(.*)", s)
    return int(m.group(1)), m.group(2) or None


def find_sb_readme(num_int, patrocinador=None):
    """Localiza README.md do SecondBrain para um numero de projeto."""
    pattern = os.path.join(SB_BASE, f"{num_int}-*", "README.md")
    matches = glob.glob(pattern)
    if not matches:
        return None
    if len(matches) == 1 or not patrocinador or patrocinador == "—":
        return matches[0]
    hint = patrocinador.lower()
    for m in matches:
        folder = os.path.basename(os.path.dirname(m)).lower()
        if hint in folder:
            return m
    return matches[0]


def read_sb_text(readme_path, max_chars=4000):
    """Le SecondBrain README e retorna secoes relevantes (sem frontmatter/assets/relacionados)."""
    if not readme_path or not os.path.exists(readme_path):
        return ""
    with open(readme_path, encoding="utf-8") as f:
        text = f.read()
    if text.startswith("---"):
        end = text.find("---", 3)
        if end > 0:
            text = text[end + 3:]
    for stop in ("## Assets", "## Projetos Relacionados", "## Relatório Completo"):
        idx = text.find(stop)
        if idx > 0:
            text = text[:idx]
    return text.strip()[:max_chars]


def get_drive_url(num_int):
    """Retorna URL da pasta Drive curada para o projeto."""
    folder_id = DRIVE_FOLDER_MAP.get(num_int)
    if folder_id:
        return f"https://drive.google.com/drive/folders/{folder_id}"
    return "https://drive.google.com/drive/folders/1IKnNdkdqgmdYP2US1vJO-B3OoekXcSiq"


def fmt_num(n):
    """Formata numero inteiro no padrao brasileiro (ponto como separador de milhar)."""
    return f"{n:,}".replace(",", ".")


def generate_card_texts(entry, sb_text):
    """Chama Claude Haiku para gerar textos dos 7 cards + captions. Retorna dict."""
    task_id, semana, num, projeto, patrocinador, atendidos, relatorio, fotos_bruto, video = entry

    pat_str = f"Patrocinador: {patrocinador}" if patrocinador != "—" else "Sem patrocinador externo"

    system = (
        "Voce e redator de marketing da NTICS Projetos. "
        "Gera textos para carrosseis de case de projetos de impacto social e cultural. "
        "Sempre em portugues brasileiro com acentos corretos. "
        "NUNCA use travessao (em-dash —). Use virgula ou ponto no lugar. "
        "Tom institucional mas acessivel. Headlines em CAIXA ALTA, maximo 12 palavras."
    )

    user = f"""Projeto: {projeto}
{pat_str}
Pessoas impactadas diretamente: {fmt_num(atendidos)}

Contexto do SecondBrain:
{sb_text or "(sem texto, use apenas os dados acima)"}

---

Gere o JSON com os textos do carrossel de case. Regras:
- c0X_titulo: CAIXA ALTA, max 12 palavras, palavras-chave entre [YELLOW]...[/YELLOW]
- c0X_corpo: 2-3 frases, acentuacao correta, sem travessao
- c04_bullets: lista com 3 a 5 itens (alcance numerico: cidades, pessoas, empregos, nota)
- c05_titulo e c05_corpo: mencionar o patrocinador pelo nome
- c07_titulo: incluir "{fmt_num(atendidos)} PESSOAS" em destaque
- instagram: ate 150 chars + linha separada com hashtags (6 a 8 tags)
- linkedin: formal, 3 bullets de metricas ESG, CTA consultivo, ate 5 hashtags

Responda SOMENTE o JSON valido, sem markdown nem texto adicional:

{{
  "c01_titulo": "...",
  "c01_corpo": "...",
  "c02_titulo": "...",
  "c02_corpo": "...",
  "c03_titulo": "...",
  "c03_corpo": "...",
  "c04_bullets": ["...", "..."],
  "c05_titulo": "...",
  "c05_corpo": "...",
  "c06_titulo": "...",
  "c06_corpo": "...",
  "c07_titulo": "...",
  "c07_corpo": "...",
  "instagram": "...",
  "linkedin": "..."
}}"""

    client = anthropic.Anthropic(
        api_key=ANTHROPIC_KEY,
        http_client=httpx.Client(verify=False),
    )
    msg = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1800,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    raw = msg.content[0].text.strip()
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)
    return json.loads(raw)


def build_description(entry, texts):
    """Monta markdown_description completa para a task ClickUp."""
    task_id, semana, num, projeto, patrocinador, atendidos, relatorio, fotos_bruto, video = entry
    num_int, _ = parse_num(num)

    pat_line = f"**Patrocinador:** {patrocinador} | " if patrocinador != "—" else ""
    drive_url = get_drive_url(num_int)
    t = texts

    bullets = "\n".join(f"- {b}" for b in t.get("c04_bullets", []))

    return f"""## Briefing Carrossel — {projeto.upper()}

{pat_line}**Pessoas impactadas diretamente:** {fmt_num(atendidos)}

### Fontes
- [Assets do projeto (fotos + logos)]({drive_url})
- [Relatorio PDF]({relatorio})
- [Video]({video})

---

### Cards do Carrossel

**Card 01 — Capa** `Badge: PROJETO DE IMPACTO (verde)`
Titulo: {t.get("c01_titulo", "")}
Corpo: {t.get("c01_corpo", "")}

**Card 02 — O Projeto** `Badge: O PROJETO (teal)`
Titulo: {t.get("c02_titulo", "")}
Corpo: {t.get("c02_corpo", "")}

**Card 03 — Metodologia** `Badge: METODOLOGIA (amarelo)`
Titulo: {t.get("c03_titulo", "")}
Corpo: {t.get("c03_corpo", "")}

**Card 04 — Alcance** `Badge: ALCANCE (teal)`
{bullets}

**Card 05 — A Empresa** `Badge: A EMPRESA (verde)`
Titulo: {t.get("c05_titulo", "")}
Corpo: {t.get("c05_corpo", "")}

**Card 06 — Resultados** `Badge: RESULTADOS (laranja)`
Titulo: {t.get("c06_titulo", "")}
Corpo: {t.get("c06_corpo", "")}

**Card 07 — Impacto** `Badge: IMPACTO (rosa)`
Titulo: {t.get("c07_titulo", "")}
Corpo: {t.get("c07_corpo", "")}

**Card 08 — CTA**
Reutilizar: `output/marketing/carrosseis/cases/cinegastroarte/08-cta.jpg`

---

### Instagram
{t.get("instagram", "")}

---

### LinkedIn
{t.get("linkedin", "")}
"""


def update_clickup_task(task_id, description, dry_run=False):
    if dry_run:
        return True
    r = requests.put(
        f"{BASE_URL}/task/{task_id}",
        headers=CLICKUP_HEADERS,
        json={"markdown_description": description},
        timeout=30,
        verify=False,
    )
    if not r.ok:
        print(f"    ERRO ClickUp {r.status_code}: {r.text[:200]}")
        return False
    return True


def main():
    parser = argparse.ArgumentParser(description="Gera textos de carrossel e atualiza tasks ClickUp.")
    parser.add_argument("--dry-run", action="store_true", help="Nao atualizar ClickUp, apenas exibir output")
    parser.add_argument("--semana", help="Processar so essa semana (ex: S03)")
    parser.add_argument("--task-id", dest="task_id", help="Processar so esse task_id")
    args = parser.parse_args()

    if not os.path.isdir(SB_BASE):
        sys.exit("Execute a partir da raiz do projeto: python tools/content-gen/gerar_textos_carrossel_batch.py")
    if not CLICKUP_TOKEN:
        sys.exit("CLICKUP_API_KEY nao definido no .env")
    if not ANTHROPIC_KEY:
        sys.exit("ANTHROPIC_API_KEY nao definido no .env")

    entries = list(MAPPING)
    if args.semana:
        entries = [e for e in entries if e[1] == args.semana]
    if args.task_id:
        entries = [e for e in entries if e[0] == args.task_id]
    if not entries:
        sys.exit("Nenhuma task encontrada com os filtros informados.")

    print(f"{'[DRY-RUN] ' if args.dry_run else ''}Processando {len(entries)} tasks...\n")

    # Cache por (num_int, patrocinador) — projetos repetidos entre semanas reusam textos
    text_cache = {}
    ok_count = 0

    for entry in entries:
        task_id, semana, num, projeto, patrocinador, atendidos, relatorio, fotos_bruto, video = entry
        num_int, _ = parse_num(num)

        print(f"[{semana}] #{num} {projeto} ({patrocinador})")

        cache_key = (num_int, patrocinador)

        if cache_key not in text_cache:
            readme = find_sb_readme(num_int, patrocinador)
            sb_text = read_sb_text(readme)
            if readme:
                print(f"  SB: {os.path.relpath(readme)}")
            else:
                print(f"  SB: nao encontrado para #{num_int}, usando so dados do MAPPING")

            print("  Gerando textos (Claude Haiku)...", end=" ", flush=True)
            try:
                texts = generate_card_texts(entry, sb_text)
                text_cache[cache_key] = texts
                print("OK")
            except Exception as e:
                print(f"ERRO: {e}")
                continue
        else:
            print("  Textos em cache (mesmo projeto)")
            texts = text_cache[cache_key]

        description = build_description(entry, texts)

        if args.dry_run:
            print(f"  --- PREVIEW ---\n{description[:600]}\n  [... truncado]\n")

        ok = update_clickup_task(task_id, description, args.dry_run)
        if ok:
            print(f"  ClickUp: {'simulado' if args.dry_run else 'atualizado'}")
            ok_count += 1

        time.sleep(0.5)

    print(f"\nConcluido: {ok_count}/{len(entries)} tasks {'simuladas' if args.dry_run else 'atualizadas'}.")


if __name__ == "__main__":
    main()
