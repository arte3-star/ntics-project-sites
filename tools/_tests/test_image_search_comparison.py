"""
test_image_search_comparison.py — Compara Serper.dev vs DuckDuckGo para busca de imagens
de carrosseis de noticias ESG.

Usa stories reais do noticias_raw.json para testar:
- DuckDuckGo Images (biblioteca duckduckgo_search, sem API key)
- Serper.dev (requer SERPER_API_KEY no .env)

Testa 3 estratégias de query para cada story:
  A) título da notícia (busca direta pela foto do artigo)
  B) keywords_unsplash (termos mais genéricos, qualidade editorial)
  C) cena_foto (descrição de cena, mais criativo)

Output: relatório visual com URLs de imagens encontradas e download de amostra.
"""

import json
import os
import sys
import time
from pathlib import Path
import requests
from dotenv import load_dotenv

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

load_dotenv(Path(__file__).parents[2] / ".env")

OUTPUT_DIR = Path(".tmp/image_search_test")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ─────────────────────────────────────────────
# DUCKDUCKGO
# ─────────────────────────────────────────────

def search_ddg(query: str, max_results: int = 5) -> list[dict]:
    """Busca imagens via DuckDuckGo. Sem API key necessária."""
    try:
        from duckduckgo_search import DDGS
        with DDGS() as ddgs:
            results = list(ddgs.images(
                query,
                max_results=max_results,
                safesearch="moderate",
                size="Large",
                type_image="photo",
            ))
        return results  # cada item: {image, title, url, source, width, height}
    except Exception as e:
        print(f"    DDG error: {e}")
        return []


# ─────────────────────────────────────────────
# SERPER.DEV
# ─────────────────────────────────────────────

def search_serper(query: str, num: int = 5, api_key: str = None) -> list[dict]:
    """Busca imagens via Serper.dev (Google Images). Requer SERPER_API_KEY."""
    key = api_key or os.getenv("SERPER_API_KEY")
    if not key:
        return []
    try:
        resp = requests.post(
            "https://google.serper.dev/images",
            headers={"X-API-KEY": key, "Content-Type": "application/json"},
            json={"q": query, "num": num, "gl": "br", "hl": "pt"},
            timeout=15,
        )
        if not resp.ok:
            print(f"    Serper {resp.status_code}: {resp.text[:100]}")
            return []
        return resp.json().get("images", [])  # {title, imageUrl, imageWidth, imageHeight, source, link}
    except Exception as e:
        print(f"    Serper error: {e}")
        return []


# ─────────────────────────────────────────────
# VALIDAÇÃO E DOWNLOAD
# ─────────────────────────────────────────────

def is_valid_image_url(url: str) -> tuple[bool, str]:
    """Verifica se a URL retorna uma imagem acessível."""
    if not url or not url.startswith("http"):
        return False, "URL inválida"
    try:
        resp = requests.head(url, timeout=8, allow_redirects=True,
                             headers={"User-Agent": "Mozilla/5.0"})
        ct = resp.headers.get("Content-Type", "")
        if resp.status_code == 200 and "image" in ct:
            return True, f"{resp.status_code} {ct.split(';')[0]}"
        return False, f"{resp.status_code} {ct}"
    except Exception as e:
        return False, str(e)[:50]


def download_sample(url: str, path: Path) -> bool:
    """Baixa amostra de imagem."""
    try:
        resp = requests.get(url, timeout=20, headers={"User-Agent": "Mozilla/5.0"})
        resp.raise_for_status()
        if "image" not in resp.headers.get("Content-Type", ""):
            return False
        path.write_bytes(resp.content)
        return True
    except Exception:
        return False


# ─────────────────────────────────────────────
# TESTE PRINCIPAL
# ─────────────────────────────────────────────

def test_story(story: dict, story_idx: int, has_serper: bool) -> dict:
    """Testa DDG e Serper para uma story com 3 estratégias de query."""
    titulo = story["titulo"]
    keywords = story.get("keywords_unsplash", [])
    cena = story.get("cena_foto", "")

    queries = {
        "A_titulo": titulo,
        "B_keywords": " ".join(keywords[:3]) if keywords else titulo,
        "C_cena": cena[:80] if cena else titulo,
    }

    story_dir = OUTPUT_DIR / f"{story_idx:02d}-{titulo[:30].lower().replace(' ', '-').replace('/', '')}"
    story_dir.mkdir(parents=True, exist_ok=True)

    result = {"titulo": titulo, "queries": {}}

    for qkey, query in queries.items():
        print(f"\n  [{qkey}] '{query[:70]}'")
        q_result = {"query": query, "ddg": [], "serper": []}

        # DDG
        print(f"    DuckDuckGo...", end=" ", flush=True)
        ddg_items = search_ddg(query, max_results=5)
        time.sleep(1.5)  # respeitar rate limit DDG

        ddg_valid = 0
        for i, item in enumerate(ddg_items[:3]):
            url = item.get("image", "")
            w, h = item.get("width", 0), item.get("height", 0)
            ok, reason = is_valid_image_url(url)
            entry = {
                "url": url,
                "width": w,
                "height": h,
                "title": item.get("title", "")[:60],
                "source": item.get("source", ""),
                "valid": ok,
                "reason": reason,
            }
            if ok and ddg_valid == 0:
                # Download a primeira imagem válida como amostra
                sample_path = story_dir / f"{qkey}_ddg.jpg"
                if download_sample(url, sample_path):
                    entry["downloaded"] = str(sample_path)
                    ddg_valid += 1
            q_result["ddg"].append(entry)
        print(f"{len(ddg_items)} resultados, {ddg_valid} válida(s) baixada(s)")

        # Serper
        if has_serper:
            print(f"    Serper.dev...", end=" ", flush=True)
            serper_items = search_serper(query, num=5)
            serper_valid = 0
            for i, item in enumerate(serper_items[:3]):
                url = item.get("imageUrl", "")
                w, h = item.get("imageWidth", 0), item.get("imageHeight", 0)
                ok, reason = is_valid_image_url(url)
                entry = {
                    "url": url,
                    "width": w,
                    "height": h,
                    "title": item.get("title", "")[:60],
                    "source": item.get("source", ""),
                    "valid": ok,
                    "reason": reason,
                }
                if ok and serper_valid == 0:
                    sample_path = story_dir / f"{qkey}_serper.jpg"
                    if download_sample(url, sample_path):
                        entry["downloaded"] = str(sample_path)
                        serper_valid += 1
                q_result["serper"].append(entry)
            print(f"{len(serper_items)} resultados, {serper_valid} válida(s) baixada(s)")
        else:
            print(f"    Serper.dev: sem SERPER_API_KEY — pulando")

        result["queries"][qkey] = q_result

    return result


def print_summary(all_results: list[dict], has_serper: bool):
    """Imprime relatório comparativo."""
    print("\n" + "=" * 70)
    print("RELATÓRIO COMPARATIVO: DuckDuckGo vs Serper.dev")
    print("=" * 70)

    ddg_total_valid = 0
    serper_total_valid = 0
    ddg_total_downloaded = 0
    serper_total_downloaded = 0

    for story_result in all_results:
        print(f"\n{story_result['titulo']}")
        for qkey, q in story_result["queries"].items():
            ddg_valid = sum(1 for r in q["ddg"] if r["valid"])
            ddg_downloaded = sum(1 for r in q["ddg"] if r.get("downloaded"))
            serper_valid = sum(1 for r in q["serper"] if r["valid"]) if q["serper"] else 0
            serper_downloaded = sum(1 for r in q["serper"] if r.get("downloaded")) if q["serper"] else 0

            ddg_total_valid += ddg_valid
            ddg_total_downloaded += ddg_downloaded
            serper_total_valid += serper_valid
            serper_total_downloaded += serper_downloaded

            serper_str = f"Serper: {serper_valid}/3 válidas, {serper_downloaded} baixadas" if has_serper else "Serper: n/a"
            print(f"  {qkey}: DDG={ddg_valid}/3 válidas, {ddg_downloaded} baixadas | {serper_str}")

    stories_count = len(all_results)
    queries_count = len(all_results[0]["queries"]) if all_results else 3
    total_tests = stories_count * queries_count

    print("\n" + "-" * 70)
    print(f"TOTAL ({stories_count} stories × {queries_count} queries = {total_tests} testes por serviço):")
    print(f"  DuckDuckGo: {ddg_total_valid} URLs válidas, {ddg_total_downloaded} imagens baixadas")
    if has_serper:
        print(f"  Serper.dev: {serper_total_valid} URLs válidas, {serper_total_downloaded} imagens baixadas")
    print(f"\nImagens salvas em: {OUTPUT_DIR.resolve()}")

    # Qual estratégia de query foi melhor?
    print("\n  MELHOR ESTRATÉGIA DE QUERY (DDG):")
    strategy_scores = {"A_titulo": 0, "B_keywords": 0, "C_cena": 0}
    for story_result in all_results:
        for qkey, q in story_result["queries"].items():
            strategy_scores[qkey] += sum(1 for r in q["ddg"] if r.get("downloaded"))
    for s, score in sorted(strategy_scores.items(), key=lambda x: -x[1]):
        print(f"    {s}: {score} imagens baixadas com sucesso")


def main():
    # Carregar stories reais
    stories_path = Path(".tmp/marketing/carrosseis/semana-2026-04-07/noticias_raw.json")
    if not stories_path.exists():
        print(f"ERROR: {stories_path} não encontrado")
        sys.exit(1)

    stories = json.loads(stories_path.read_text(encoding="utf-8"))
    print(f"Stories carregadas: {len(stories)} notícias")

    has_serper = bool(os.getenv("SERPER_API_KEY"))
    if not has_serper:
        print("INFO: SERPER_API_KEY não encontrada no .env — testando apenas DuckDuckGo")
        print("      Para testar Serper.dev: cadastre em serper.dev e adicione SERPER_API_KEY=... ao .env")
    else:
        print("✓ SERPER_API_KEY detectada — testando ambos")

    print(f"\nTestando {len(stories)} stories com 3 estratégias de query cada...")
    print("(estratégias: A=título, B=keywords, C=cena_foto)\n")

    all_results = []
    for i, story in enumerate(stories, 1):
        print(f"\n{'─'*60}")
        print(f"[{i}/{len(stories)}] {story['titulo']}")
        result = test_story(story, i, has_serper)
        all_results.append(result)

    # Salvar JSON detalhado
    report_path = OUTPUT_DIR / "comparison_report.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)

    print_summary(all_results, has_serper)
    print(f"\nRelatório JSON detalhado: {report_path}")


if __name__ == "__main__":
    main()
