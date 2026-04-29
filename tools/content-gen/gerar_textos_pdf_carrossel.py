"""
Gera textos Instagram + LinkedIn e exporta PDF LinkedIn para um carrossel case.

USO:
  1. Preencha as seções TEXTOS e PROJETOS_PDF abaixo com os dados do novo projeto.
  2. Execute: python tools/content-gen/gerar_textos_pdf_carrossel.py

SAÍDAS (por projeto, em output/marketing/carrosseis/cases/{slug}/):
  - texto_instagram.txt
  - texto_linkedin.txt
  - linkedin-carrossel.pdf  (4:5 completo, sem crop — preserva todos os textos)

DEPENDÊNCIAS: pip install fpdf2 Pillow
"""
import sys
from pathlib import Path
from fpdf import FPDF

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE = Path("g:/O meu disco/AUTOMA\u00c7\u00d5ES")

# ══════════════════════════════════════════════════════════════════════════════
# CONFIGURAÇÃO — edite aqui para cada novo carrossel
# ══════════════════════════════════════════════════════════════════════════════

TEXTOS = {
    # ── Projeto 1 ─────────────────────────────────────────────────────────────
    "caminhao-ods-rabobank": {
        "instagram": """Um caminhão que transforma praças em espaços de vivência dos ODS. 🌍

Em 2025, o Caminhão Conhecendo os ODS percorreu 3 cidades no Mato Grosso levando arte, ciência e experiências sobre os Objetivos de Desenvolvimento Sustentável para escolas e comunidades públicas.

📊 Os números falam por si:
→ 24.063 pessoas impactadas diretamente
→ 72.189 indiretamente
→ 42 parcerias locais firmadas
→ Nota 10 com 100% de satisfação
→ Evento carbono neutro ✅

Um projeto viabilizado pela Lei Rouanet com apoio do Rabobank — transformando incentivo fiscal em impacto real.

Salve este carrossel e compartilhe com quem precisa conhecer o poder da cultura como ferramenta de transformação. 💚

#CaminhaoODS #ImpactoSocial #ODS #Sustentabilidade #LeideIncentivo #ESG #Rabobank #NTICSProjetos #Educacao #AgendaDiamante2030""",

        "linkedin": """Em 3 cidades do Mato Grosso, um caminhão se tornou um espaço de vivência dos ODS.

O Caminhão Conhecendo os ODS — realizado com patrocínio do Rabobank via Lei Rouanet — levou educação, arte e ciência para praças públicas, transformando comunidades em agentes da Agenda 2030.

**Resultados da edição 2025:**
• 24.063 pessoas impactadas diretamente
• 72.189 alcançadas indiretamente
• 42 parcerias locais firmadas
• 13 apresentações artísticas
• Nota média de satisfação: 10 (100% de aprovação)
• Evento certificado carbono neutro

O projeto integra metodologia STEAM, espetáculos teatrais, oficinas interativas e consultoria de empregabilidade — tudo dentro de um circuito itinerante projetado para democratizar o acesso à cultura e ao conhecimento sustentável.

Para empresas comprometidas com ESG e com a Agenda 2030: este é o tipo de projeto que transforma incentivo fiscal em indicadores de impacto mensuráveis e verificáveis.

Saiba como viabilizar a próxima edição: nticsprojetos.com.br

#ImpactoSocial #ESG #LeiRouanet #ODS #Sustentabilidade #AgendaDiamante2030 #EducacaoSTEAM #NTICSProjetos #Rabobank #ResponsabilidadeSocial""",
    },

    # ── Projeto 3 ─────────────────────────────────────────────────────────────
    "cinegastroarte": {
        "instagram": """Cinema, gastronomia e arte como ferramentas de transformação social. 🎬🍽️

O Festival CineGastroArte levou cultura de verdade para 53 mil pessoas em 3 cidades — com sessões de cinema gratuitas, oficinas com chefs renomados e uma exposição fotográfica aberta a todos.

📊 Os números que contam a história:
→ 53.262 pessoas impactadas
→ 1.465 alunos formados nas oficinas
→ 13 chefs participantes
→ 32 sessões de cinema
→ 15 mil visitantes na exposição
→ 3.069 ingressos gratuitos para comunidades

Viabilizado pela Teleperformance via Lei de Incentivo Cultural. Um exemplo real de ESG que transforma vidas. 💚

Salve e compartilhe com quem acredita no poder da cultura! 👇

#CineGastroArte #ImpactoSocial #ESG #Teleperformance #LeidIncentivoCultural #NTICSProjetos #Cinema #Gastronomia #ODS4 #ODS10 #Sustentabilidade""",

        "linkedin": """53.262 pessoas impactadas. 3 cidades. Cinema, gastronomia e arte como vetores de transformação social.

O Festival CineGastroArte — realizado pela NTICS com patrocínio da Teleperformance via Lei de Incentivo Cultural — demonstrou como projetos culturais bem estruturados entregam indicadores ESG mensuráveis e impacto comunitário duradouro.

**Resultados verificados:**
• 53.262 pessoas impactadas diretamente
• 1.465 alunos formados em oficinas de gastronomia
• 13 chefs e profissionais envolvidos
• 32 sessões de cinema acessíveis
• 15.000 visitantes na exposição fotográfica
• 3.069 ingressos gratuitos para populações de baixa renda
• 100 influenciadores mobilizados
• 31 matérias publicadas na imprensa regional e nacional

O projeto está alinhado ao ODS 4 (Educação de Qualidade) e ODS 10 (Redução das Desigualdades) da Agenda 2030.

Para empresas que buscam associar sua marca a cultura, impacto social e visibilidade de mídia: o modelo CineGastroArte pode ser replicado em sua cidade.

Entre em contato: ntics.com.br

#ImpactoSocial #ESG #LeiDeIncentivo #ODS #Sustentabilidade #Teleperformance #CineGastroArte #NTICSProjetos #ResponsabilidadeSocial #Cultura""",
    },

    # ── Projeto 4 ─────────────────────────────────────────────────────────────
    "educacao-cultural-statkraft": {
        "instagram": """Programa de Educação Cultural em 3 cidades. 🌱📸

Em 2025, o P.E.C Eu Faço Parte levou educação ambiental, fotografia digital e Feira de Ideias para escolas públicas em Osório/RS, Uibaí/BA e Ibipeba/BA — com patrocínio Statkraft via Lei Rouanet.

📊 Resultados da edição:
→ 3.177 alunos formados (105,9% da meta)
→ 179 professores atendidos
→ 10.068 pessoas impactadas indiretamente
→ 3 cidades · 12 empregos locais gerados
→ Nota média 9,4 de avaliação
→ 98% dos alunos querem participar de novo

Oficinas de educação ambiental, visitas a unidades de conservação, exposição fotográfica em Ibipeba e Feira de Ideias premiando soluções criativas dos estudantes. Alunos de observadores a protagonistas. 💚

Salve e compartilhe com quem acredita em educação como motor de transformação. 👇

#PEC #EuFacoParte #ImpactoSocial #Statkraft #LeiRouanet #ODS #EducacaoAmbiental #NTICSProjetos #ESG #AgendaDiamante2030""",

        "linkedin": """3.177 alunos formados. 179 professores. 3 cidades. Nota 9,4 de avaliação.

O P.E.C — Programa de Educação Cultural Eu Faço Parte — foi realizado pela NTICS Projetos com patrocínio Statkraft via Lei Rouanet em Osório/RS, Uibaí/BA e Ibipeba/BA em 2025. O projeto conectou educação ambiental, fotografia digital e protagonismo juvenil em escolas públicas com realidades territoriais distintas.

**Indicadores verificados:**
• 3.177 alunos contemplados (105,9% da meta de 3.000)
• 179 professores atendidos presencialmente
• 3.356 pessoas impactadas diretamente
• 10.068 pessoas impactadas indiretamente
• 12 empregos locais gerados
• 98% dos alunos manifestaram interesse em participar novamente
• Nota média de avaliação: 9,4

**Metodologia em 6 etapas:** workshop de professores, evento de abertura, 3 oficinas de educação ambiental, oficina de fotografia digital, visitas a unidades de conservação e Feira de Ideias com premiação de soluções estudantis. Em Ibipeba, exposição fotográfica aberta à comunidade.

O projeto está alinhado aos ODS 4 (Educação de Qualidade), ODS 6 (Água Potável e Saneamento), ODS 12 (Consumo Responsável), ODS 14 (Vida na Água) e ODS 17 (Parcerias).

Para empresas que buscam associar marca a educação, pertencimento territorial e indicadores ESG mensuráveis — esse é o modelo PEC.

Saiba mais: nticsprojetos.com.br

#ImpactoSocial #ESG #LeiRouanet #EducacaoAmbiental #ODS #AgendaDiamante2030 #Statkraft #NTICSProjetos #ResponsabilidadeSocial #Cultura""",
    },

    # ── Projeto Festival ODS Pocket ──────────────────────────────────────────
    "festival-ods-pocket": {
        "instagram": """Arte, cultura e sustentabilidade para 17 mil estudantes da rede pública. 🌍🎭

O Festival ODS Pocket levou espetáculos teatrais, oficinas de arte, fotografia e mostra audiovisual para escolas públicas em Joinville, Manaus e Rio Claro — com patrocínio da Whirlpool via Lei Rouanet.

📊 Resultados da edição 2024:
→ 17.646 pessoas impactadas diretamente
→ 4.440 alunos contemplados
→ 210 professores atendidos
→ 3 cidades em 3 estados
→ 17 empregos locais gerados
→ Nota 9.7 de avaliação

Cada atividade traduziu os ODS em experiência prática, transformando o olhar de jovens sobre o futuro do planeta. 💚

Salve e compartilhe com quem acredita que cultura transforma. 👇

#FestivalODS #ImpactoSocial #ODS #Sustentabilidade #Whirlpool #LeiRouanet #NTICSProjetos #Educacao #ESG #AgendaDiamante2030""",

        "linkedin": """17.646 pessoas impactadas. 4 linguagens artísticas. 3 cidades. Nota 9.7.

O Festival ODS Pocket — realizado pela NTICS Projetos com patrocínio da Whirlpool via Lei Rouanet — levou arte e cultura para escolas públicas de Joinville (SC), Manaus (AM) e Rio Claro (SP) em 2024, traduzindo os Objetivos de Desenvolvimento Sustentável em experiências práticas para estudantes da rede pública.

**Indicadores verificados:**
• 17.646 pessoas impactadas diretamente
• 4.440 alunos contemplados
• 210 professores atendidos
• 17 empregos locais gerados
• Nota média de avaliação: 9.7
• 3 cidades em 3 estados brasileiros

**Metodologia em 4 linguagens:** espetáculo teatral, oficinas de arte, oficina de fotografia e mostra audiovisual. Cada atividade foi desenvolvida com foco nos ODS, promovendo pertencimento e protagonismo juvenil.

O projeto está alinhado aos ODS 4 (Educação de Qualidade), ODS 11 (Cidades e Comunidades Sustentáveis), ODS 13 (Ação Climática) e ODS 17 (Parcerias para a Implementação).

Para empresas que buscam associar marca a educação, cultura e impacto mensurávelvia Lei de Incentivo Cultural: este é o modelo Festival ODS.

Saiba mais: nticsprojetos.com.br

#ImpactoSocial #ESG #LeiRouanet #ODS #Sustentabilidade #Whirlpool #NTICSProjetos #ResponsabilidadeSocial #Cultura #AgendaDiamante2030""",
    },

    # ── Projeto 2 ─────────────────────────────────────────────────────────────
    "teatro-robotica-cnh": {
        "instagram": """Crianças do interior do Piauí construindo robôs com materiais recicláveis. 🤖♻️

O projeto Robótica nas Escolas 2ª Edição levou arte, tecnologia e sustentabilidade para escolas públicas de Uruçuí e Baixa Grande do Ribeiro — dois municípios com IDH baixo no Piauí — com apoio da CNH Capital via Lei Rouanet.

📊 Resultados:
→ 1.888 pessoas impactadas diretamente
→ 1.843 alunos do Ensino Fundamental I
→ 48% de meninas nas oficinas de robótica
→ 100% das oficinas com materiais recicláveis
→ Nota média 9,7 de avaliação
→ 4 empregos locais gerados

Uma prova de que tecnologia e cultura, juntas, constroem novos futuros. 💡

Deslize para ver como foi. 👉

#RoboticaNasEscolas #ImpactoSocial #EducacaoSTEAM #CNHCapital #LeideIncentivo #ESG #NTICSProjetos #Sustentabilidade #ODS #Piaui""",

        "linkedin": """48% das crianças que participaram das oficinas de robótica eram meninas. Em municípios com IDH baixo, no interior do Piauí.

O projeto Robótica nas Escolas 2ª Edição — viabilizado com patrocínio da CNH Capital via Lei Rouanet — chegou a Uruçuí e Baixa Grande do Ribeiro com uma proposta educacional imersiva: espetáculo teatral tecnológico, oficinas maker de robótica com materiais recicláveis e feira de robótica com protagonismo estudantil.

**Indicadores ESG da edição 2025:**
• 1.888 pessoas impactadas diretamente
• 5.664 impactadas indiretamente
• 1.843 alunos do Ensino Fundamental I atendidos
• 48% de participação feminina nas oficinas de robótica
• 100% das oficinas com materiais recicláveis
• Nota média de satisfação: 9,7
• 4 empregos locais gerados
• Evento carbono neutro

O projeto está alinhado aos ODS 4 (Educação de Qualidade), ODS 9 (Indústria, Inovação e Infraestrutura) e ODS 12 (Consumo e Produção Responsáveis).

Para empresas que buscam associar sua marca a inovação, educação e impacto social mensurável: a próxima edição está em captação.

#ImpactoSocial #ESG #LeiRouanet #EducacaoSTEAM #Robotica #ODS #Sustentabilidade #CNHCapital #NTICSProjetos #ResponsabilidadeSocial #Piaui""",
    },

    # ── Projeto 5: Circo no Brasil ────────────────────────────────────────────
    "circo-no-brasil": {
        "instagram": """A magia do circo chegou ao Mato Grosso e transformou 20.930 vidas. 🎪

Em 2024, o Circo no Brasil levou o espetáculo A Magia da Lona para 8 cidades, unindo arte circense, educação ambiental e valorização da vida no campo.

📊 Os números que contam a história:
→ 20.930 pessoas impactadas diretamente
→ 10.070 crianças de escola pública
→ 34 apresentações de A Magia da Lona
→ 8 cidades atendidas em Mato Grosso
→ 150 empregos gerados
→ 38 matérias em mídia nacional (TV Globo, Record, SBT)

Patrocínio Agro Baggio via Lei Rouanet, alinhado aos ODS 3, 4, 10, 11 e 13.

Arte como ponte entre campo e futuro. 💚

#CircoNoBrasil #ImpactoSocial #ESG #LeiRouanet #CulturaEDireito #AgroBaggio #NTICSProjetos #ResponsabilidadeSocial #ODS #MatoGrosso""",

        "linkedin": """Em 2024, o projeto Circo no Brasil percorreu 8 cidades do Mato Grosso com impacto real e mensurável.

Com patrocínio da Agro Baggio via Lei Rouanet, o espetáculo A Magia da Lona levou teatro, dança e técnicas circenses para regiões rurais e urbanas, retratando a vida no campo, a sustentabilidade e a educação ambiental.

**Resultados da edição 2024:**
• 20.930 pessoas impactadas diretamente
• 10.070 crianças de escola pública beneficiadas
• 34 apresentações de A Magia da Lona
• 8 cidades: Sorriso, Lucas do Rio Verde, Nova Mutum, Sinop, Alta Floresta, Matupá, Boa Esperança do Norte e Tapurah
• 150 empregos gerados
• 38 matérias em mídia nacional (TV Globo, Record, SBT e Rádio Meridional)

Trilha NTICS de projetos circenses (2024 e 2025): 27.975 pessoas impactadas diretamente, 16.609 alunos, 15 cidades e 208 empregos gerados em 2 projetos com patrocínio de Agro Baggio e Repsol.

Alinhado aos ODS 3 (Saúde e Bem-Estar), 4 (Educação), 10 (Redução das Desigualdades), 11 (Cidades Sustentáveis) e 13 (Ação Climática).

Para empresas comprometidas com ESG e com o desenvolvimento das comunidades rurais: a cultura é um instrumento concreto de transformação social sustentável.

#ImpactoSocial #ESG #LeiRouanet #ODS #CulturaEDireito #ResponsabilidadeSocial #AgroBaggio #NTICSProjetos #MatoGrosso""",
    },
}

# Cards por projeto — ordem de aparição no PDF
# Padrão 8 cards: 01-capa … 07-impacto … 08-cta
PROJETOS_PDF = [
    {
        "slug": "cinegastroarte",
        "cards": [
            "01-capa.jpg", "02-o-projeto.jpg", "03-metodologia.jpg", "04-alcance.jpg",
            "05-a-empresa.jpg", "06-resultados.jpg", "07-impacto.jpg", "08-cta.jpg",
        ],
    },
    {
        "slug": "caminhao-ods-rabobank",
        "cards": [
            "01-capa.jpg", "02-o-projeto.jpg", "03-metodologia.jpg", "04-alcance.jpg",
            "05-a-empresa.jpg", "06-resultados.jpg", "07-impacto.jpg", "08-cta.jpg",
        ],
    },
    {
        "slug": "teatro-robotica-cnh",
        "cards": [
            "01-capa.jpg", "02-o-projeto.jpg", "03-metodologia.jpg", "04-alcance.jpg",
            "05-a-empresa.jpg", "06-resultados.jpg", "07-impacto.jpg", "08-cta.jpg",
        ],
    },
    {
        "slug": "educacao-cultural-statkraft",
        "cards": [
            "01-capa.jpg", "02-o-projeto.jpg", "03-metodologia.jpg", "04-alcance.jpg",
            "05-a-empresa.jpg", "06-resultados.jpg", "07-impacto.jpg",
            "08-trilha-pec.jpg", "09-cta.jpg",
        ],
    },
    {
        "slug": "festival-ods-pocket",
        "cards": [
            "01-capa.jpg", "02-o-projeto.jpg", "03-metodologia.jpg", "04-alcance.jpg",
            "05-a-empresa.jpg", "06-resultados.jpg", "07-impacto.jpg",
            "08-trilha-festival-ods.jpg", "09-cta.jpg",
        ],
    },
    {
        "slug": "circo-no-brasil",
        "cards": [
            "01-capa.jpg", "02-o-projeto.jpg", "03-metodologia.jpg", "04-alcance.jpg",
            "05-a-empresa.jpg", "06-resultados.jpg", "07-impacto.jpg",
            "08-trilha-ntics.jpg", "09-cta.jpg",
        ],
    },
]

# ══════════════════════════════════════════════════════════════════════════════
# LÓGICA — não editar
# ══════════════════════════════════════════════════════════════════════════════

# Cards são 4:5 (1856x2304). LinkedIn aceita PDFs em qualquer proporção.
# Mantemos o 4:5 original sem crop para não cortar texto.
# fpdf2: 210mm × 262.5mm (proporção exata 4:5 = 210 × 2304/1856)
PAGE_W = 210    # mm
PAGE_H = 262.5  # mm

for projeto, textos in TEXTOS.items():
    out_dir = BASE / "output/marketing/carrosseis/cases" / projeto
    out_dir.mkdir(parents=True, exist_ok=True)
    for canal, texto in textos.items():
        path = out_dir / f"texto_{canal}.txt"
        path.write_text(texto, encoding="utf-8")
        print(f"SAVED: {path}")

for proj in PROJETOS_PDF:
    slug = proj["slug"]
    cards_dir = BASE / "output/marketing/carrosseis/cases" / slug
    out_pdf = cards_dir / "linkedin-carrossel.pdf"

    pdf = FPDF(orientation="P", unit="mm", format=(PAGE_W, PAGE_H))
    pdf.set_auto_page_break(False)

    added = 0
    for card_name in proj["cards"]:
        card_path = cards_dir / card_name
        if not card_path.exists():
            print(f"  AVISO: {card_path} nao encontrado, pulando")
            continue
        pdf.add_page()
        pdf.image(str(card_path), x=0, y=0, w=PAGE_W, h=PAGE_H)
        added += 1

    pdf.output(str(out_pdf))
    print(f"SAVED PDF ({added} paginas): {out_pdf}")

print("\nConcluido.")
