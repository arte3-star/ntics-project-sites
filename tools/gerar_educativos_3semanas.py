"""
gerar_educativos_3semanas.py
Gera carrosseis educativos para S03, S04, S05 via Leonardo AI.
8 cards por semana (capa + 5 conteudo + metodo + CTA).
"""
import os, sys, time
from pathlib import Path
import requests
from dotenv import load_dotenv

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

load_dotenv()
LEO_KEY = os.getenv("LEONARDO_API_KEY")
BASE_V2 = "https://cloud.leonardo.ai/api/rest/v2"
BASE_V1 = "https://cloud.leonardo.ai/api/rest/v1"

# ─── Conteúdo dos 3 carrosseis ───────────────────────────────────────────────

SEMANAS = {
    "S03": {
        "tema": "5 sinais de maturidade em Responsabilidade Social",
        "cta_pergunta": "Quer aplicar esses 5 sinais na sua empresa?",
        "capa_cena": "a professional woman presenting ESG impact data on a screen to engaged corporate team in a modern office with large windows and green city view",
        "capa_subtitulo": "Como identificar se sua empresa esta no caminho certo",
        "metodo_frase": "24 ANOS DE METODO QUE ENTREGA",
        "metodo_metricas": [
            ("1.060+", "projetos executados"),
            ("11,4M", "pessoas impactadas"),
            ("9,32", "nota media satisfacao"),
            ("88", "NPS dos clientes"),
        ],
        "cards": [
            {
                "slug": "02-programa",
                "titulo": "TRATA COMO PROGRAMA NAO EVENTO",
                "icone": "a calendar with recurring circular arrows showing continuity",
                "texto": "Empresas maduras nao fazem acoes pontuais. Elas constroem programas continuos com comeco, meio e legado. Cada ciclo aprende com o anterior e aprofunda o impacto.",
                "frase": "Acao pontual passa. Programa transforma.",
            },
            {
                "slug": "03-envolve",
                "titulo": "ENVOLVE QUEM SERA IMPACTADO",
                "icone": "two hands working together building something, symbol of collaboration",
                "texto": "A comunidade e parceira desde o primeiro dia. Nao um objeto do projeto — um agente de mudanca. Quando as pessoas participam da construcao, o resultado e delas.",
                "frase": "Co-criar e respeitar.",
            },
            {
                "slug": "04-mede",
                "titulo": "MEDE O QUE REALMENTE IMPORTA",
                "icone": "a gauge or compass pointing to the word impact, measurement symbol",
                "texto": "Numero de participantes e so o comeco. O que muda na vida das pessoas? O que elas fazem diferente depois? Essas perguntas guiam os indicadores que importam.",
                "frase": "Indicadores de transformacao, nao de presenca.",
            },
            {
                "slug": "05-comunica",
                "titulo": "COMUNICA COM TRANSPARENCIA",
                "icone": "a megaphone with data charts floating around it, representing clear communication",
                "texto": "Resultados reais sao compartilhados — os bons e os aprendizados. Transparencia nao e vulnerabilidade. E autoridade. Quem compartilha dados, constroi confianca.",
                "frase": "Quem tem dados, tem credibilidade.",
            },
            {
                "slug": "06-conecta",
                "titulo": "CONECTA AO NEGOCIO",
                "icone": "interlocking gears with a green leaf growing from the center, ESG and business",
                "texto": "Responsabilidade Social madura faz parte da estrategia. Melhora o rating ESG, fortalece a marca e cria valor para o negocio. Proposito e performance andam juntos.",
                "frase": "RS nao e custo. E diferencial competitivo.",
            },
        ],
    },
    "S04": {
        "tema": "O poder do territorio",
        "cta_pergunta": "Pronto para construir projetos que pertencem ao territorio?",
        "capa_cena": "a group of community members and corporate professionals sitting in a circle in an open-air space in a Brazilian neighborhood, co-creating together with maps and materials spread around",
        "capa_subtitulo": "Por que o lugar e o ponto de partida do impacto real",
        "metodo_frase": "24 ANOS CONSTRUINDO COM OS TERRITORIOS",
        "metodo_metricas": [
            ("165+", "cidades atendidas"),
            ("868", "cidades Conhecendo ODS"),
            ("1.060+", "projetos executados"),
            ("11,4M", "pessoas impactadas"),
        ],
        "cards": [
            {
                "slug": "02-diagnostico",
                "titulo": "DIAGNOSTICO TERRITORIAL",
                "icone": "a map with pins and a magnifying glass, exploring territory",
                "texto": "Antes de qualquer acao, entender o contexto: quem vive aqui, o que ja existe, quais sao as necessidades reais. O diagnostico e a fundacao de tudo.",
                "frase": "Nao se pode transformar o que nao se conhece.",
            },
            {
                "slug": "03-escuta",
                "titulo": "ESCUTA ATIVA",
                "icone": "a large ear with sound waves and a heart inside, representing deep listening",
                "texto": "Rodas de conversa, visitas, entrevistas com liderancas locais. A escuta ativa nao e protocolo — e o gesto que gera confianca e abre espaco para a mudanca real.",
                "frase": "Quem escuta, constroi junto.",
            },
            {
                "slug": "04-cocriacao",
                "titulo": "COCRIACAO COM A COMUNIDADE",
                "icone": "multiple hands placing puzzle pieces together, building collaboratively",
                "texto": "A comunidade nao e publico-alvo do projeto. Ela e coautora. Quando as pessoas participam da construcao, o projeto tem raizes — e as raizes dao sustentabilidade.",
                "frase": "Parceria real. Impacto real.",
            },
            {
                "slug": "05-legitimidade",
                "titulo": "LEGITIMIDADE QUE DURA",
                "icone": "a strong tree with deep roots growing from the ground, symbol of durability",
                "texto": "Projetos territoriais geram engajamento que nao precisa de incentivo externo. A propria comunidade se torna guardia do projeto — porque ele tambem e dela.",
                "frase": "Pertencimento e o maior indicador de sucesso.",
            },
            {
                "slug": "06-resultados",
                "titulo": "RESULTADOS MAIS PROFUNDOS",
                "icone": "a upward arrow growing from soil into a plant, representing sustainable growth",
                "texto": "Quando o projeto nasce do territorio, o impacto e mais duradouro. A transformacao nao termina com o financiamento — ela continua sendo cultivada pela propria comunidade.",
                "frase": "Impacto real comeca quando voce conhece o lugar onde esta.",
            },
        ],
    },
    "S05": {
        "tema": "Impacto que multiplica",
        "cta_pergunta": "Seu projeto tem uma historia que merece ser contada?",
        "capa_cena": "a documentary filmmaker interviewing a smiling woman in a community garden who is telling her story of transformation, golden hour light, authentic candid moment",
        "capa_subtitulo": "Por que projetos bem comunicados geram mais valor",
        "metodo_frase": "COMO O IMPACTO NTICS SE MULTIPLICA",
        "metodo_metricas": [
            ("326 mil", "pessoas diretas ODS"),
            ("1,19M", "impacto indireto"),
            ("868", "cidades alcancadas"),
            ("4x", "multiplicador de alcance"),
        ],
        "cards": [
            {
                "slug": "02-multiplicam",
                "titulo": "PROGRAMAS QUE SE MULTIPLICAM",
                "icone": "a single point of light dividing into many, cascade multiplication symbol",
                "texto": "Projetos que terminam deixam uma lembranca. Programas que se multiplicam deixam uma transformacao — passada de pessoa para pessoa, de escola para escola.",
                "frase": "Impacto que nao precisa de autorizacao para crescer.",
            },
            {
                "slug": "03-historia",
                "titulo": "A HISTORIA RECRUTA NOVOS PARCEIROS",
                "icone": "a microphone with speech bubbles spreading outward, storytelling symbol",
                "texto": "Quando um beneficiario conta sua historia, outros se reconhecem nela. O relato autentico e o melhor instrumento de captacao — porque nao vende, inspira.",
                "frase": "Historia verdadeira vale mais que qualquer anuncio.",
            },
            {
                "slug": "04-dados",
                "titulo": "DADOS REAIS INSPIRAM INVESTIMENTOS",
                "icone": "a bar chart with upward trend and a lightbulb above it, data inspiring action",
                "texto": "Uma empresa que documenta resultados com indicadores verificaveis inspira outras a seguir o mesmo caminho. Transparencia gera emulacao — e o impacto se multiplica.",
                "frase": "Dado verificavel e convite a agir.",
            },
            {
                "slug": "05-celebrar",
                "titulo": "CELEBRAR MANTEM A NARRATIVA VIVA",
                "icone": "people raising hands in celebration with stars around them, community joy",
                "texto": "Comunidades que celebram sua transformacao sao comunidades que continuam transformando. A celebracao nao e vaidade — e renovacao de proposito coletivo.",
                "frase": "Celebrar e comprometer-se de novo.",
            },
            {
                "slug": "06-cascata",
                "titulo": "IMPACTO EM CASCATA",
                "icone": "concentric ripple circles in water spreading outward, cascade effect",
                "texto": "Cada pessoa diretamente impactada leva o aprendizado para sua familia, trabalho e escola. O alcance real de um programa e sempre muito maior do que os numeros diretos mostram.",
                "frase": "1 pessoa transformada impacta muitas outras.",
            },
        ],
    },
}


def build_capa_prompt(s):
    return (
        f"A social media educational carousel cover card Instagram 4:5 format. "
        f"The top 50 percent is a full-bleed hyperrealistic photograph of {s['capa_cena']}, "
        f"candid unposed moment, Canon EOS R5 35mm lens, natural warm light, photojournalistic "
        f"documentary style, visible film grain ISO 800, NOT AI generated NOT illustration. "
        f"From 50 to 68 percent smooth dark gradient from transparent to solid dark teal 005F73. "
        f"From 68 to 78 percent over solid dark teal centered small bold white uppercase sans-serif "
        f"text: RESPONSABILIDADE SOCIAL QUE RESOLVE. "
        f"From 78 to 92 percent large bold white uppercase text: {s['tema'].upper()}. "
        f"From 92 to 97 percent smaller white italic text: {s['capa_subtitulo']}. "
        f"At the very bottom a thick gradient stripe from green 3DAA35 to teal 00A5B8 "
        f"to pink D41A6A to orange E86428. Professional editorial design."
    )


def build_card_prompt(card):
    return (
        f"A social media educational carousel card Instagram 4:5 format. "
        f"Clean solid dark teal 005F73 background filling the entire card. "
        f"At the top 8 percent a subtle thin gradient stripe from green 3DAA35 to teal 00A5B8. "
        f"From 10 to 28 percent centered large flat icon illustration of {card['icone']}, "
        f"white and yellow tones on teal background, modern minimalist style. "
        f"From 30 to 45 percent bold large white uppercase sans-serif text centered: "
        f"{card['titulo']}. "
        f"From 48 to 72 percent regular white sans-serif body text centered with generous "
        f"line spacing: {card['texto']}. "
        f"From 76 to 86 percent a highlighted rectangle with yellow F5B800 left border and "
        f"yellow italic text: {card['frase']}. "
        f"At the very bottom a thick gradient stripe from green 3DAA35 to teal 00A5B8 "
        f"to pink D41A6A to orange E86428. Professional clean educational card design."
    )


def build_metodo_prompt(s):
    m = s["metodo_metricas"]
    metricas_desc = " | ".join([f"{v} {d}" for v, d in m])
    return (
        f"A social media educational carousel card Instagram 4:5 format. "
        f"Clean solid dark teal 005F73 background. "
        f"At top 8 percent thin gradient stripe from green 3DAA35 to teal 00A5B8. "
        f"From 10 to 22 percent small white uppercase text centered: METODO NTICS. "
        f"From 24 to 38 percent large bold white text centered: {s['metodo_frase']}. "
        f"From 42 to 75 percent a clean 2x2 grid of metric boxes each with a yellow F5B800 "
        f"number large bold above and white descriptor text below: "
        f"box1 {m[0][0]} {m[0][1]}, box2 {m[1][0]} {m[1][1]}, "
        f"box3 {m[2][0]} {m[2][1]}, box4 {m[3][0]} {m[3][1]}. "
        f"From 78 to 86 percent small white text centered: "
        f"Certificacao ISO 9001 | Pacto Global ONU | GRI Standards. "
        f"At the very bottom a thick gradient stripe from green 3DAA35 to teal 00A5B8 "
        f"to pink D41A6A to orange E86428. Professional data visualization card."
    )


def build_cta_prompt(s):
    return (
        f"A social media educational carousel CTA card Instagram 4:5 format. "
        f"Clean solid dark teal 005F73 background. "
        f"Top 15 percent empty teal space reserved for logo. "
        f"From 22 to 42 percent centered large bold white sans-serif text: "
        f"{s['cta_pergunta']}. "
        f"From 46 to 56 percent centered medium white text: Fale com a NTICS. "
        f"From 60 to 70 percent centered white rounded button outline shape with "
        f"white text inside: ntics.com.br. "
        f"From 74 to 82 percent small white text centered: @nticsprojetos. "
        f"At the very bottom a thick gradient stripe from green 3DAA35 to teal 00A5B8 "
        f"to pink D41A6A to orange E86428. Minimalist professional CTA design."
    )


def start_gen(prompt):
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": f"Bearer {LEO_KEY}",
    }
    payload = {
        "model": "nano-banana-2",
        "parameters": {
            "prompt": prompt,
            "width": 1856,
            "height": 2304,
            "quantity": 1,
            "prompt_enhance": "OFF",
        },
        "public": False,
    }
    r = requests.post(f"{BASE_V2}/generations", headers=headers, json=payload, timeout=30)
    if not r.ok:
        raise RuntimeError(f"{r.status_code}: {r.text[:200]}")
    data = r.json()
    # handle both dict and list responses
    if isinstance(data, list):
        raise RuntimeError(f"API error list: {str(data)[:200]}")
    # try direct key
    for key in ["generationId", "id"]:
        if data.get(key):
            return data[key]
    # try nested dict
    for v in data.values():
        if isinstance(v, dict):
            for k in ["generationId", "id"]:
                if v.get(k):
                    return v[k]
    raise RuntimeError(f"No ID in: {str(data)[:200]}")


def poll_gen(gen_id, max_wait=180):
    headers = {"accept": "application/json", "authorization": f"Bearer {LEO_KEY}"}
    url = f"{BASE_V1}/generations/{gen_id}"
    waited = 0
    while waited < max_wait:
        r = requests.get(url, headers=headers, timeout=30)
        r.raise_for_status()
        job = r.json().get("generations_by_pk", {})
        status = job.get("status", "")
        if status == "COMPLETE":
            imgs = job.get("generated_images", [])
            if imgs:
                return imgs[0]["url"]
            raise RuntimeError("Complete but no images")
        if status == "FAILED":
            raise RuntimeError(f"FAILED")
        time.sleep(8)
        waited += 8
        print(f"    ...{waited}s", flush=True)
    raise TimeoutError(f"Timeout {max_wait}s")


def download(url, path):
    r = requests.get(url, timeout=60)
    r.raise_for_status()
    path.write_bytes(r.content)


def build_descricao(semana_key, s):
    cards_list = "\n".join([f"0{i+2}-{c['slug'].split('-', 1)[1]}.jpg — {c['titulo']}" for i, c in enumerate(s["cards"])])
    caption_ig = (
        f"Como sua empresa pode evoluir em {s['tema']}? "
        f"Este carrossel traz os conceitos essenciais para você aplicar hoje mesmo. "
        f"Salve para consultar sempre que precisar!\n\n"
        f"@nticsprojetos | #ResponsabilidadeSocial #ESG #ImpactoSocial #ODS #NTICS"
    )
    caption_li = (
        f"Compartilhando nosso framework sobre: {s['tema']}\n\n"
        f"Em 6 cards, os conceitos fundamentais para empresas que querem ir além do discurso.\n\n"
        f"O que mais ressoou com a realidade da sua empresa? Comente abaixo.\n\n"
        f"#ResponsabilidadeSocial #ESG #NTICS #ImpactoSocial"
    )
    return f"""========================================
CARROSSEL EDUCATIVO
Tema: {s['tema']}
Semana {semana_key}
========================================

--- CAPTION INSTAGRAM ---
{caption_ig}

--- CAPTION LINKEDIN ---
{caption_li}

--- ORDEM DOS CARDS ---
01-capa.jpg — Capa: {s['tema']}
{cards_list}
07-metodo.jpg — Método NTICS: {s['metodo_frase']}
08-cta.jpg — CTA: {s['cta_pergunta']}
"""


def main():
    for semana_key, s in SEMANAS.items():
        print(f"\n{'='*50}")
        print(f"EDUCATIVO {semana_key} — {s['tema']}")
        print(f"{'='*50}")

        out_dir = Path(f".tmp/marketing/carrosseis/educativo-{semana_key}")
        out_dir.mkdir(parents=True, exist_ok=True)

        # Build all prompts
        prompts = {"01-capa": build_capa_prompt(s)}
        for card in s["cards"]:
            prompts[card["slug"]] = build_card_prompt(card)
        prompts["07-metodo"] = build_metodo_prompt(s)
        prompts["08-cta"] = build_cta_prompt(s)

        # Submit all generations
        jobs = {}
        for name, prompt in prompts.items():
            print(f"  >> Starting: {name}", flush=True)
            try:
                gen_id = start_gen(prompt)
                jobs[name] = gen_id
                print(f"     ID: {gen_id}", flush=True)
                time.sleep(1)
            except Exception as e:
                print(f"     FAILED: {e}", flush=True)

        if not jobs:
            continue

        print(f"\n  Waiting 60s for {len(jobs)} generations...", flush=True)
        time.sleep(60)

        # Poll and download
        results = []
        for name, gen_id in jobs.items():
            print(f"  >> Polling: {name}", flush=True)
            try:
                img_url = poll_gen(gen_id)
                path = out_dir / f"{name}.jpg"
                download(img_url, path)
                print(f"     SAVED: {path}", flush=True)
                results.append({"name": name, "ok": True})
            except Exception as e:
                print(f"     FAILED: {e}", flush=True)
                results.append({"name": name, "ok": False, "error": str(e)})

        # Save descricao.txt
        (out_dir / "descricao.txt").write_text(build_descricao(semana_key, s), encoding="utf-8")

        ok = sum(1 for r in results if r["ok"])
        print(f"\n  {semana_key}: {ok}/{len(prompts)} imagens → {out_dir}")

    print("\n\nCONCLUIDO!")


if __name__ == "__main__":
    main()
