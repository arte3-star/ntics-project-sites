"""
editorial_rewrite.py — Reescreve content do landing page com tom editorial NTICS
de comunicação externa.

Input: output/_lovable_{projeto}_content.json + output/cronogramas/{slug}.json
Output: output/_editorial_{slug}_content.json (mesmo schema + atividades enriquecidas)

Sonnet recebe content original + lista de atividades únicas do cronograma e
devolve nomes próprios + descrições externas.
"""
import argparse
import json
import os
import re
import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

REPO_ROOT = Path(__file__).resolve().parents[2]
CRONO_DIR = REPO_ROOT / "output" / "cronogramas"
OUT_DIR = REPO_ROOT / "output"

# Mapeamento projeto → arquivo Lovable + slug do cronograma
PROJECT_FILES = {
    "116": ("116", "cultura-robotica-aster"),
    "117": ("117", "teatro-oficina-robotica-4ed-whirlpool"),
    "119": ("119", "pec-eu-faco-parte-2ed-sylvamo"),
    "124": ("124", "gastronomia-tambem-e-arte-compagas"),
    "125": ("125", "gastronomia-tambem-e-arte-2ed-gru"),
    "127G": ("127G", "pie-empreendedorismo-e-arte-2ed-gru"),
    "127S": ("127S", "pie-empreendedorismo-e-arte-2ed-sotreq"),
}

SYSTEM = """Você é editor da NTICS Projetos, escrevendo a página pública de um projeto socioambiental ainda em fase pré-execução.

Voz NTICS: informativa, confiante, inspiradora, acessível. 65% formal, 55% técnica, 70% séria. Não usa jargão corporativo nem clichês de impacto. Não pede permissão para liderar — afirma.

Regras de escrita:
- NUNCA usar travessão "—" (em-dash). Use vírgula, ponto ou reescreva.
- Frases curtas, voz ativa.
- Evite "atividade 1", "atividade 2" — cada atividade tem nome próprio (oficina, workshop, exposição, feira, palestra etc).
- Foque no benefício para o estudante/educador/cidade, não na operação interna.
- Não invente números nem cidades novas que não estejam no input.
- Linguagem para imprensa, secretarias de educação e família dos estudantes."""

USER_TEMPLATE = """Reescreva o conteúdo da landing page do projeto abaixo para comunicação externa.

# Conteúdo original (Lovable, primeira versão crua):
```json
{content_original}
```

# Cronograma real (cidades, escolas, atividades, alunos):
```json
{cronograma_resumo}
```

# Atividades únicas presentes no cronograma:
{atividades_unicas}

# O que devolver
Devolva APENAS um JSON válido com esta estrutura (sem markdown, sem explicações):

```
{{
  "hero_title": "...",
  "hero_subtitle": "...",
  "sobre_paragraphs": ["...", "...", "..."],
  "atividades": [
    {{"nome": "Nome próprio da atividade", "descricao": "1-2 frases sobre o que é e o impacto."}}
  ],
  "democratizacao": "frase curta sobre acesso e impacto territorial"
}}
```

Diretrizes específicas:
- hero_title: nome curto do projeto (não slogan)
- hero_subtitle: uma linha que explica o programa em uma frase
- sobre_paragraphs: 2 a 3 parágrafos curtos que explicam objetivo + público + escopo (cidades/escolas se relevante)
- atividades: 4 a 7 entradas. Use as atividades únicas do cronograma como base; renomeie para forma de comunicação externa (ex: "OFICINA EDUCAÇÃO AMBIENTAL 1 e 2" vira "Oficina de Educação Ambiental"). Agrupe variações da mesma atividade em uma única entrada quando fizer sentido.
- democratizacao: uma frase sobre como o projeto democratiza acesso (educação, cultura, oportunidades)
- Todo o conteúdo em português brasileiro, sem travessão.
"""


def _load_api_key() -> str:
    if os.environ.get("ANTHROPIC_API_KEY"):
        return os.environ["ANTHROPIC_API_KEY"]
    env = REPO_ROOT / ".env"
    if env.exists():
        for line in env.read_text(encoding="utf-8").splitlines():
            if line.startswith("ANTHROPIC_API_KEY="):
                return line.split("=", 1)[1].strip()
    raise SystemExit("ANTHROPIC_API_KEY não encontrada")


def call_sonnet(content_original: dict, cronograma: dict | None) -> dict:
    from anthropic import Anthropic

    client = Anthropic(api_key=_load_api_key())

    if cronograma:
        atividades_set = set()
        for c in cronograma.get("cards", []):
            for a in c.get("atividades", []):
                atividades_set.add(a)
        atividades_list = sorted(atividades_set)
        cronograma_resumo = {
            "total_alunos": cronograma.get("total_alunos"),
            "total_escolas": cronograma.get("total_escolas"),
            "cidades": list({c["cidade"] for c in cronograma["cards"]}),
            "escolas_por_cidade": [
                {"cidade": c["cidade"], "escola": c["escola"], "alunos": c["total_alunos"]}
                for c in cronograma["cards"]
            ],
        }
    else:
        atividades_list = []
        cronograma_resumo = {}

    user = USER_TEMPLATE.format(
        content_original=json.dumps(content_original, ensure_ascii=False, indent=2),
        cronograma_resumo=json.dumps(cronograma_resumo, ensure_ascii=False, indent=2),
        atividades_unicas="\n".join(f"- {a}" for a in atividades_list) or "(nenhuma)",
    )

    resp = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2500,
        temperature=0.4,
        system=SYSTEM,
        messages=[{"role": "user", "content": user}],
    )
    text = "".join(b.text for b in resp.content if hasattr(b, "text")).strip()
    # remove fences se vierem
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    return json.loads(text)


def rewrite(projeto: str) -> dict:
    proj_id, slug = PROJECT_FILES[projeto]
    content_path = OUT_DIR / f"_lovable_{proj_id}_content.json"
    crono_path = CRONO_DIR / f"{slug}.json"

    content_orig = json.loads(content_path.read_text(encoding="utf-8"))
    cronograma = None
    if crono_path.exists():
        cron = json.loads(crono_path.read_text(encoding="utf-8"))
        if cron.get("total_escolas", 0) > 0:
            cronograma = cron

    result = call_sonnet(content_orig, cronograma)
    # sanity: garante nada com travessão
    def strip_dash(s):
        return s.replace(" — ", ", ").replace("—", ",") if isinstance(s, str) else s

    def deep_strip(o):
        if isinstance(o, str):
            return strip_dash(o)
        if isinstance(o, list):
            return [deep_strip(x) for x in o]
        if isinstance(o, dict):
            return {k: deep_strip(v) for k, v in o.items()}
        return o

    return deep_strip(result)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--projeto", required=True)
    p.add_argument("--output", help="default: output/_editorial_{slug}_content.json")
    args = p.parse_args()

    proj_id, slug = PROJECT_FILES[args.projeto]
    out = Path(args.output) if args.output else OUT_DIR / f"_editorial_{slug}_content.json"
    out.parent.mkdir(parents=True, exist_ok=True)

    print(f"Reescrevendo {args.projeto} ({slug}) ...", file=sys.stderr)
    result = rewrite(args.projeto)
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Salvo: {out}", file=sys.stderr)
    # preview
    print(f"\nHero: {result.get('hero_title')}")
    print(f"Sub:  {result.get('hero_subtitle')}")
    print(f"Atividades ({len(result.get('atividades', []))}):")
    for a in result.get("atividades", []):
        print(f"  - {a.get('nome')}: {a.get('descricao')[:90]}...")


if __name__ == "__main__":
    main()
