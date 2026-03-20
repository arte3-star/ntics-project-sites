"""
search_perplexity.py — Searches for positive CSR/ESG news using the Perplexity API.

The Perplexity API uses the OpenAI SDK client format pointed at Perplexity's base URL.
Model: sonar-pro (real-time web search with citations).

Usage:
  python tools/search_perplexity.py --days 7 --output .tmp/raw_search_2026-03-20.json

  Or with custom queries:
  python tools/search_perplexity.py \
    --queries '["ESG positive news this week", "CSR achievement corporate 2026"]' \
    --days 7

Environment:
  PERPLEXITY_API_KEY=pplx-... (in .env)
"""

import argparse
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

try:
    from openai import OpenAI
except ImportError:
    print("ERROR: openai package not installed. Run: pip install openai")
    sys.exit(1)

DEFAULT_OUTPUT_DIR = Path(__file__).parent.parent / ".tmp"

# Default search queries for positive CSR/ESG news
DEFAULT_QUERIES = [
    "positive ESG CSR news corporate sustainability achievement past 7 days 2026",
    "renewable energy milestone company announcement this week 2026",
    "corporate social responsibility win social impact news 2026",
    "ESG investment record green bond sustainability finance this week",
    "net zero carbon neutrality company pledge achievement news recent",
    "circular economy biodiversity corporate initiative positive news 2026",
]

# Queries específicas para leis e incentivos fiscais no Brasil relevantes para patrocinadores corporativos
INCENTIVE_QUERIES = [
    "leis incentivos fiscais patrocinio projetos sociais culturais ESG Brasil 2026 novidades atualizações",
    "incentivo fiscal responsabilidade social corporativa Lei Rouanet Lei do Bem dedução IR IRPJ empresas Brasil 2026",
]

SYSTEM_PROMPT = """You are a research assistant specialized in CSR (Corporate Social Responsibility) and ESG (Environmental, Social, Governance) news.

Your task: Find and summarize POSITIVE news stories from the past {days} days about companies making real, measurable progress on ESG and CSR topics.

For each story you find, provide:
1. Company name
2. Story title
3. What they achieved (with specific numbers/metrics when available)
4. Source publication and URL
5. Date
6. Category: Environment, Social, or Governance

Focus on:
- Concrete achievements with quantitative data (CO2 reduced, $ invested, # employees affected)
- Verified announcements from credible companies
- Real milestones, not just pledges without action
- Global scope (not just one region)

Exclude:
- Greenwashing or vague commitments without metrics
- Opinion pieces
- Negative news or controversies
- Stories older than {days} days

Format your response as a structured list with clear sections for each story."""

INCENTIVE_SYSTEM_PROMPT = """Você é um especialista em legislação de incentivos fiscais para responsabilidade social corporativa e ESG no Brasil.

Seu objetivo: Encontrar e explicar leis, regulamentações ou atualizações relevantes dos últimos {days} dias (ou leis vigentes importantes que empresas patrocinadoras de projetos sociais precisam conhecer) no Brasil.

Para cada lei ou incentivo, forneça:
1. Nome da lei / mecanismo (ex: Lei Rouanet, Lei do Bem, ICMS Ecológico, Debentures de Infraestrutura)
2. Headline curta (o que mudou ou por que é relevante agora)
3. Benefício fiscal concreto (ex: dedução de até 80% do IRPJ, isenção de IPI)
4. Quem pode usar (tipo de empresa: Lucro Real, PMEs, qualquer pessoa jurídica)
5. Prazo ou contexto de aplicação
6. Fonte e URL

Foco em:
- Leis que permitem dedução de patrocínio a projetos sociais, culturais, esportivos ou ambientais
- Atualizações recentes de regulamentações ESG no Brasil (CVM, B3, Banco Central)
- Novas oportunidades de incentivo fiscal para empresas que investem em impacto social
- Legislação aplicável a empresas de médio e grande porte (perfil de patrocinadores NTICS)

Formato: lista estruturada, em português, com destaque para o benefício prático ao empresário."""


def search_perplexity(query: str, days: int, api_key: str) -> dict:
    """Run a single Perplexity search and return the result."""
    client = OpenAI(
        api_key=api_key,
        base_url="https://api.perplexity.ai",
    )

    date_filter = (datetime.today() - timedelta(days=days)).strftime("%B %d, %Y")
    system = SYSTEM_PROMPT.format(days=days)
    user_msg = f"Find positive CSR/ESG news from {date_filter} until today. Query: {query}"

    response = client.chat.completions.create(
        model="sonar-pro",
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user_msg},
        ],
        temperature=0.2,
    )

    content = response.choices[0].message.content

    # Extract citations if available
    citations = []
    if hasattr(response, "citations"):
        citations = response.citations or []

    return {
        "query": query,
        "content": content,
        "citations": citations,
        "model": response.model,
        "timestamp": datetime.now().isoformat(),
    }


def search_incentives(query: str, days: int, api_key: str) -> dict:
    """Run a Perplexity search focused on Brazilian ESG/CSR tax incentives and legislation."""
    client = OpenAI(
        api_key=api_key,
        base_url="https://api.perplexity.ai",
    )

    system = INCENTIVE_SYSTEM_PROMPT.format(days=days)
    user_msg = f"Pesquise leis e incentivos fiscais relevantes para patrocinadores de projetos ESG/CSR no Brasil. Query: {query}"

    response = client.chat.completions.create(
        model="sonar-pro",
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user_msg},
        ],
        temperature=0.1,
    )

    content = response.choices[0].message.content
    citations = []
    if hasattr(response, "citations"):
        citations = response.citations or []

    return {
        "query": query,
        "content": content,
        "citations": citations,
        "model": response.model,
        "timestamp": datetime.now().isoformat(),
        "type": "incentive",
    }


def main():
    parser = argparse.ArgumentParser(description="Search Perplexity for CSR/ESG news")
    parser.add_argument("--days", type=int, default=7, help="Look back N days (default: 7)")
    parser.add_argument("--queries", help="JSON array of custom queries (optional)")
    parser.add_argument("--output", help="Output JSON path")
    parser.add_argument("--no-incentives", action="store_true", help="Skip incentive/law queries")
    args = parser.parse_args()

    api_key = os.getenv("PERPLEXITY_API_KEY")
    if not api_key:
        print("ERROR: PERPLEXITY_API_KEY not set in .env")
        sys.exit(1)

    queries = DEFAULT_QUERIES
    if args.queries:
        queries = json.loads(args.queries)

    print(f"Searching Perplexity for CSR/ESG news (past {args.days} days)...")
    print(f"Running {len(queries)} queries...\n")

    results = []
    for i, query in enumerate(queries, 1):
        print(f"  [{i}/{len(queries)}] {query[:60]}...")
        try:
            result = search_perplexity(query, args.days, api_key)
            results.append(result)
            print(f"         ✓ {len(result['content'])} chars, {len(result['citations'])} citations")
        except Exception as e:
            print(f"         ✗ Error: {e}")
            results.append({"query": query, "error": str(e), "timestamp": datetime.now().isoformat()})

    # Search for Brazilian incentives/laws
    incentive_results = []
    if not args.no_incentives:
        print(f"\nSearching for Brazilian ESG/CSR incentive laws ({len(INCENTIVE_QUERIES)} queries)...")
        for i, query in enumerate(INCENTIVE_QUERIES, 1):
            print(f"  [{i}/{len(INCENTIVE_QUERIES)}] {query[:60]}...")
            try:
                result = search_incentives(query, args.days, api_key)
                incentive_results.append(result)
                print(f"         ✓ {len(result['content'])} chars, {len(result['citations'])} citations")
            except Exception as e:
                print(f"         ✗ Error: {e}")
                incentive_results.append({"query": query, "error": str(e), "timestamp": datetime.now().isoformat()})

    # Save output
    output_data = {
        "search_date": datetime.now().isoformat(),
        "days_lookback": args.days,
        "query_count": len(queries),
        "results": results,
        "incentive_results": incentive_results,
    }

    if args.output:
        output_path = Path(args.output)
    else:
        DEFAULT_OUTPUT_DIR.mkdir(exist_ok=True)
        date_str = datetime.today().strftime("%Y-%m-%d")
        output_path = DEFAULT_OUTPUT_DIR / f"raw_search_{date_str}.json"

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    successful = sum(1 for r in results if "error" not in r)
    print(f"\n✓ Search complete: {successful}/{len(queries)} queries succeeded")
    print(f"  Saved to: {output_path}")
    print(f"\nNext step: Run research_csr_news.py with this output to curate the stories.")
    return str(output_path)


if __name__ == "__main__":
    main()
