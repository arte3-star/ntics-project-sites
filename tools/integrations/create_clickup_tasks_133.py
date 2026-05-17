#!/usr/bin/env python3
"""
create_clickup_tasks_133.py
Cria subtarefas no ClickUp para o Projeto 133 — Ecoarte Vibra 2026.

Usage:
  python tools/integrations/create_clickup_tasks_133.py [--dry-run]

Requer: CLICKUP_API_KEY (env var)

Roteamento:
  Email / WhatsApp / Redes Sociais / Assessoria de Imprensa
      Pré    → 868j97001  (Posts pré projeto)
      Durante → 868j970hb (Posts durante)
      Pós    → 868j970du  (Posts pós)
  Mídia Kit Vibra  → 868j96znb (Lista de Peças)
  Peças do Evento  → 868j96znb (Lista de Peças)
"""
import os, sys, time, calendar
from datetime import datetime, timezone

try:
    import requests
except ImportError:
    print("requests nao instalado. Execute: pip install requests")
    sys.exit(1)

# ── Config ──────────────────────────────────────────────────────────────────

CLICKUP_API_KEY = os.environ.get("CLICKUP_API_KEY", "")
LIST_ID         = "901113597559"

PARENT_PRE     = "868j97001"
PARENT_DURANTE = "868j970hb"
PARENT_POS     = "868j970du"
PARENT_PECAS   = "868j96znb"

DRY_RUN = "--dry-run" in sys.argv

# ── Instagram referencias curadas ────────────────────────────────────────────

IG_REFS = {
    "lancamento": [
        ("Vem aí o Caminhão ODS — reel lançamento 2025", "https://www.instagram.com/conhecendoosods/reel/DMaW6pBsmY1/"),
        ("Vem aí: Caminhão ODS no Rio de Janeiro — foto 2024", "https://www.instagram.com/conhecendoosods/p/DBe_wUBPLLr/"),
        ("Vem aí: RJ + Paranaguá — reel 2024", "https://www.instagram.com/conhecendoosods/reel/DBcSincPHPr/"),
    ],
    "programacao": [
        ("Programação Completa — Itapoá (foto 2023)", "https://www.instagram.com/conhecendoosods/p/C0znhbcPfFd/"),
        ("Programação Completa — São Luís (foto 2023)", "https://www.instagram.com/conhecendoosods/p/C0NUgEJLmvE/"),
        ("Programação Rondonópolis — chega com conteúdo (foto 2025)", "https://www.instagram.com/conhecendoosods/p/DN5m8BNjhSl/"),
    ],
    "melhores_momentos": [
        ("Melhores Momentos — Rondonópolis (reel 2025)", "https://www.instagram.com/conhecendoosods/reel/DOOszQbEQ1j/"),
        ("Melhores Momentos — Lucas do Rio Verde (reel 2025)", "https://www.instagram.com/conhecendoosods/reel/DNyvlOfYlec/"),
        ("Melhores Momentos — Rio de Janeiro / Moove (reel 2024)", "https://www.instagram.com/nticsprojetos/reel/DCPDoCIPMhO/"),
        ("Melhores Momentos — Itapoá (reel 2023)", "https://www.instagram.com/conhecendoosods/reel/C1A9YH2tQUx/"),
    ],
    "talks": [
        ("Talks Cuiabá — convite (foto 2025)", "https://www.instagram.com/conhecendoosods/p/DNQ6qA4uOur/"),
        ("Talks Rondonópolis — convite (foto 2025)", "https://www.instagram.com/conhecendoosods/p/DN26rr9XGNW/"),
        ("ODS Talks Rio de Janeiro — convite (foto 2024)", "https://www.instagram.com/conhecendoosods/p/DBqx4HoJFOn/"),
    ],
    "carrossel_educativo": [
        ("O que são os ODS — carrossel educativo (foto 2025)", "https://www.instagram.com/conhecendoosods/p/DMgUxVQOF1w/"),
        ("Aprender brincando nas tendas (foto 2025)", "https://www.instagram.com/conhecendoosods/p/DNk0nZtuYha/"),
    ],
    "numeralha": [
        ("Encerramento Rondonópolis com dados de impacto (reel 2025)", "https://www.instagram.com/conhecendoosods/reel/DOOszQbEQ1j/"),
        ("Melhores Momentos RJ com dados Moove (reel 2024)", "https://www.instagram.com/nticsprojetos/reel/DCPDoCIPMhO/"),
    ],
    "bastidores": [
        ("Bastidores do Caminhão ODS — equipe (reel 2025)", "https://www.instagram.com/nticsprojetos/reel/DOhAwhjgeDX/"),
    ],
    "parceiros": [
        ("Parceiros Cuiabá — tendas e ações (foto 2025)", "https://www.instagram.com/nticsprojetos/p/DM-2CgJPGBM/"),
    ],
    "foto_evento": [
        ("Fotos do evento — Cuiabá (foto 2025)", "https://www.instagram.com/conhecendoosods/p/DNaz4cwNSys/"),
        ("Fotos do evento — Lucas do Rio Verde (foto 2025)", "https://www.instagram.com/conhecendoosods/p/DNtkJ_53CT9/"),
    ],
}


def get_ig_refs(item_name, canal):
    """Retorna até 3 referencias Instagram para o item."""
    n = item_name.lower()
    refs = []

    kw_map = [
        (["vem aí", "anúncio do ecoarte", "chamada", "card convite", "convite escolas",
          "convite comunidade", "lançamento"], "lancamento"),
        (["programação do dia", "programação completa", "card programação"], "programacao"),
        (["melhores momentos"], "melhores_momentos"),
        (["talks", "palestras", "paineis"], "talks"),
        (["numeralha", "impacto total", "impacto final", "resultados finais",
          "agradecimento + numeralha", "relatório de impacto"], "numeralha"),
        (["o que esperar", "ods do ecoarte", "educativo", "linkedin: vibra"], "carrossel_educativo"),
        (["cobertura ao vivo", "estamos ao vivo", "release do dia d", "ao vivo"], "bastidores"),
        (["mailing", "convite para imprensa", "nota exclusiva", "release pós", "release final"], None),
    ]

    seen_keys = set()
    for keywords, ref_key in kw_map:
        if ref_key and any(kw in n for kw in keywords):
            if ref_key not in seen_keys:
                refs.extend(IG_REFS[ref_key])
                seen_keys.add(ref_key)

    # Assessoria nao precisa de ref Instagram
    if canal == "imprensa":
        return []

    return refs[:3]


# ── Dados: Comunicacao Digital ───────────────────────────────────────────────

SECOES = [
    {
        "label": "EMAIL MARKETING — 14 pecas",
        "canal": "email",
        "label_display": "Email Marketing",
        "items": [
            (1,  "Chamada p/ Participacao — Escolas (Manaus)",     "Pre",     "Manaus", "mai/26", "", "Diretores e coordenadores", "Bruna", "Lucas / Designer"),
            (2,  "Chamada p/ Participacao — Comunidade (Manaus)",  "Pre",     "Manaus", "mai/26", "", "Lista geral Manaus", "Bruna", "Lucas / Designer"),
            (3,  "Confirmacao de Inscricao (automatico — Manaus)", "Pre",     "Manaus", "mai/26", "Fluxo automatico pos-inscricao", "Inscritos", "Bruna", "Lucas / Designer"),
            (4,  "Lembrete — 1 semana antes (Manaus)",             "Pre",     "Manaus", "07/jun", "", "Inscritos confirmados", "Bruna", "Lucas / Designer"),
            (5,  "Lembrete — Amanha comeca (Manaus)",              "Pre",     "Manaus", "13/jun", "", "Inscritos confirmados", "Bruna", "Lucas / Designer"),
            (6,  "Estamos ao vivo! (Manaus)",                      "Durante", "Manaus", "14/jun", "", "Inscritos + lista geral", "Bruna", "Lucas / Designer"),
            (7,  "Melhores momentos + Obrigado (Manaus)",          "Pos",     "Manaus", "16/jun", "", "Participantes + lista geral", "Bruna", "Lucas / Designer"),
            (8,  "Chamada p/ Participacao — Escolas (RJ)",         "Pre",     "RJ",     "jul/26", "", "Diretores e coordenadores RJ", "Bruna", "Lucas / Designer"),
            (9,  "Chamada p/ Participacao — Comunidade (RJ)",      "Pre",     "RJ",     "jul/26", "", "Lista geral RJ", "Bruna", "Lucas / Designer"),
            (10, "Lembrete — 1 semana antes (RJ)",                 "Pre",     "RJ",     "22/ago", "", "Inscritos confirmados RJ", "Bruna", "Lucas / Designer"),
            (11, "Lembrete — Amanha comeca (RJ)",                  "Pre",     "RJ",     "28/ago", "", "Inscritos confirmados RJ", "Bruna", "Lucas / Designer"),
            (12, "Estamos ao vivo! (RJ)",                          "Durante", "RJ",     "29/ago", "", "Inscritos + lista geral RJ", "Bruna", "Lucas / Designer"),
            (13, "Melhores momentos + Obrigado (RJ)",              "Pos",     "RJ",     "31/ago", "", "Participantes + lista geral RJ", "Bruna", "Lucas / Designer"),
            (14, "Relatorio de Impacto Final (Vibra)",             "Pos",     "Ambas",  "out/26", "One Page Report + numeralha Cota 2", "Equipe Vibra (patrocinio)", "Bruna", "Lucas / Designer"),
        ]
    },
    {
        "label": "WHATSAPP — 8 pecas",
        "canal": "whatsapp",
        "label_display": "WhatsApp",
        "items": [
            (15, "Card Convite Escolas (Manaus)",              "Pre",     "Manaus", "mai/26", "", "Grupos de diretores/professores", "Bruna", "Equipe"),
            (16, "Card Convite Comunidade (Manaus)",           "Pre",     "Manaus", "mai/26", "", "Grupos comunitarios Manaus", "Bruna", "Equipe"),
            (17, "Card Programacao do Dia D (Manaus)",         "Durante", "Manaus", "14/jun", "", "Todos os grupos Manaus", "Bruna", "Equipe"),
            (18, "Card Agradecimento + Numeralha (Manaus)",    "Pos",     "Manaus", "15/jun", "", "Todos os grupos Manaus", "Bruna", "Equipe"),
            (19, "Card Convite Escolas (RJ)",                  "Pre",     "RJ",     "jul/26", "", "Grupos de diretores/professores RJ", "Bruna", "Equipe"),
            (20, "Card Convite Comunidade (RJ)",               "Pre",     "RJ",     "jul/26", "", "Grupos comunitarios RJ", "Bruna", "Equipe"),
            (21, "Card Programacao do Dia D (RJ)",             "Durante", "RJ",     "29/ago", "", "Todos os grupos RJ", "Bruna", "Equipe"),
            (22, "Card Agradecimento + Numeralha (RJ)",        "Pos",     "RJ",     "30/ago", "", "Todos os grupos RJ", "Bruna", "Equipe"),
        ]
    },
    {
        "label": "REDES SOCIAIS (Instagram + LinkedIn) — 15 pecas",
        "canal": "social",
        "label_display": "Redes Sociais",
        "items": [
            (23, "Vem ai! Ecoarte em Manaus — post lancamento (1)",        "Pre",     "Manaus", "mai/26", "Post unico", "Seguidores Instagram", "Bruna", "Designer"),
            (24, "Vem ai! Ecoarte em Manaus — carrossel (2)",              "Pre",     "Manaus", "mai/26", "Carrossel 8 cards", "Seguidores Instagram", "Bruna", "Designer"),
            (25, "O que esperar: Meu Corpo, Minhas Regras",                "Pre",     "Ambas",  "jun/26", "Carrossel educativo — tema sensivel", "Seguidores Instagram", "Bruna", "Designer"),
            (26, "Os ODS do Ecoarte (carrossel educativo)",                "Pre",     "Ambas",  "jun/26", "17 ODS atendidos", "Seguidores Instagram", "Bruna", "Designer"),
            (27, "Programacao do Dia D Manaus",                            "Durante", "Manaus", "14/jun", "Post + Story", "Seguidores Instagram", "Bruna", "Designer"),
            (28, "Cobertura ao vivo Manaus (Stories)",                     "Durante", "Manaus", "14/jun", "Stories em tempo real", "Seguidores Instagram", "Bruna", "Designer / Equipe"),
            (29, "Melhores Momentos Manaus (carrossel pos)",               "Pos",     "Manaus", "16/jun", "Carrossel 8-10 cards", "Seguidores Instagram", "Bruna", "Designer"),
            (30, "Numeralha de Impacto Manaus",                            "Pos",     "Manaus", "jun/26", "Post unico com numeros", "Seguidores Instagram", "Bruna", "Designer"),
            (31, "LinkedIn: Vibra + Ecoarte (institucional)",              "Pre",     "Ambas",  "jun/26", "Post institucional collab", "Seguidores LinkedIn", "Bruna", "Designer"),
            (32, "Vem ai! Ecoarte no Rio de Janeiro",                      "Pre",     "RJ",     "jul/26", "Post + carrossel", "Seguidores Instagram", "Bruna", "Designer"),
            (33, "Programacao do Dia D RJ",                                "Durante", "RJ",     "29/ago", "Post + Story", "Seguidores Instagram", "Bruna", "Designer"),
            (34, "Cobertura ao vivo RJ (Stories)",                         "Durante", "RJ",     "29/ago", "Stories em tempo real", "Seguidores Instagram", "Bruna", "Designer / Equipe"),
            (35, "Melhores Momentos RJ (carrossel pos)",                   "Pos",     "RJ",     "ago/set","Carrossel 8-10 cards", "Seguidores Instagram", "Bruna", "Designer"),
            (36, "Numeralha de Impacto Total — Cota 2",                    "Pos",     "Ambas",  "set/26", "Post unico + LinkedIn", "Seguidores Instagram + LinkedIn", "Bruna", "Designer"),
            (37, "LinkedIn: Resultados finais para Vibra",                  "Pos",     "Ambas",  "set/26", "Post institucional ESG", "Seguidores LinkedIn", "Bruna", "Designer"),
        ]
    },
    {
        "label": "ASSESSORIA DE IMPRENSA — 13 pecas",
        "canal": "imprensa",
        "label_display": "Assessoria de Imprensa",
        "items": [
            (38, "Release: Anuncio do Ecoarte Manaus",               "Pre",     "Manaus", "mai/26", "Distribuicao para veiculos AM", "Veiculos regionais Manaus", "Bruna", "Angelo"),
            (39, "Convite para Imprensa — Manaus",                   "Pre",     "Manaus", "jun/26", "E-mail de convite credenciado", "Jornalistas Manaus", "Bruna", "Angelo"),
            (40, "Mailing de Imprensa — Manaus",                     "Pre",     "Manaus", "mai/26", "Lista de contatos da imprensa AM", "Interno", "Bruna", "Angelo"),
            (41, "Nota Exclusiva (1 veiculo local) — Manaus",        "Pre",     "Manaus", "jun/26", "1 veiculo estrategico AM", "1 veiculo exclusivo", "Bruna", "Angelo"),
            (42, "Release do Dia D — Manaus",                        "Durante", "Manaus", "14/jun", "Release com numeralha parcial", "Veiculos AM + nacionais", "Bruna", "Angelo"),
            (43, "Release Pos-Evento com Numeralha — Manaus",        "Pos",     "Manaus", "15/jun", "Numeralha completa + fotos", "Veiculos AM + nacionais", "Bruna", "Angelo"),
            (44, "Release: Anuncio do Ecoarte RJ",                   "Pre",     "RJ",     "jul/26", "Distribuicao para veiculos RJ", "Veiculos regionais RJ", "Bruna", "Angelo"),
            (45, "Mailing de Imprensa — RJ",                         "Pre",     "RJ",     "jul/26", "Lista de contatos da imprensa RJ", "Interno", "Bruna", "Angelo"),
            (46, "Convite para Imprensa — RJ",                       "Pre",     "RJ",     "ago/26", "E-mail de convite credenciado RJ", "Jornalistas RJ", "Bruna", "Angelo"),
            (47, "Nota Exclusiva (1 veiculo) — RJ",                  "Pre",     "RJ",     "ago/26", "1 veiculo estrategico RJ", "1 veiculo exclusivo RJ", "Bruna", "Angelo"),
            (48, "Release do Dia D — RJ",                            "Durante", "RJ",     "29/ago", "Release com numeralha parcial", "Veiculos RJ + nacionais", "Bruna", "Angelo"),
            (49, "Release Pos-Evento com Numeralha — RJ",            "Pos",     "RJ",     "ago/set","Numeralha completa + fotos", "Veiculos RJ + nacionais", "Bruna", "Angelo"),
            (50, "Release Final Cota 2 — Impacto Total",             "Pos",     "Ambas",  "set/26", "Resultado consolidado 2 cidades", "Nacional + Vibra", "Bruna", "Angelo"),
        ]
    },
    {
        "label": "MIDIA KIT VIBRA ENERGIA — 4 pecas",
        "canal": "kit",
        "label_display": "Midia Kit Vibra",
        "items": [
            (51, "Posts Instagram para Vibra compartilhar (3 posts)", "Pre", "Ambas", "jun/26", "Co-assinatura: Realizacao NTICS / Patrocinio Vibra", "Canal Vibra Energia", "Bruna / Vibra", "Vibra"),
            (52, "Card LinkedIn para Vibra (collab)",                 "Pre", "Ambas", "jun/26", "Post collab Vibra + NTICS", "Canal Vibra LinkedIn", "Bruna / Vibra", "Vibra"),
            (53, "Copy sugerido para Vibra (redes)",                  "Pre", "Ambas", "jun/26", "Texto pronto para uso da equipe Vibra", "Equipe comun. Vibra", "Bruna / Vibra", "Vibra"),
            (54, "Logo co-assinatura Realizacao NTICS / Patrocinio Vibra", "Pre", "Ambas", "mai/26", "Arquivo fonte (PNG + AI)", "Designer / Vibra", "Bruna / Vibra", "—"),
        ]
    },
]

# ── Dados: Pecas do Evento ───────────────────────────────────────────────────
# (nome, secao, objetivo, specs, ref_desc, ref_folder_id, adaptacoes)

REF_BASE = "https://drive.google.com/drive/folders/"

PECAS = [
    ("Logomarca do Projeto", "A. Identidade Visual",
     "Versao oficial da marca 'Ecoarte / Caminhao ODS' para uso em todas as pecas de comunicacao, sinalizacao e impressos do evento de Manaus.",
     "Formatos: .ai (fonte), .pdf (impressao), .png (digital), .svg\nVersoes: (1) sem cidade — uso nacional; (2) com cidade 'Manaus, AM'\nFundo: versao branco + transparente\nPaleta: identidade ODS adaptada ao tema Ecoarte\nAprovacao Vibra: necessaria antes de qualquer uso publico",
     "Na edicao 2019 havia versao 'sem cidades' (PDF+PNG+AI) e subpasta 'POR CIDADE' com versoes personalizadas. Arquivos criados por Bruna Seibel.",
     "1PsXpAcRi93eCB5-egV9BIrMn4s-S8E0R",
     "Atualizar nome para 'Ecoarte Container Itinerante / Caminhao ODS'\nIncluir referencia ao ODS 3 no layout\nCriar versao 'Manaus, AM 2026' na subpasta Por Cidade\nSubstituir nome do patrocinador: Whirlpool → Vibra Energia\nGarantir co-assinatura NTICS + Vibra conforme aprovacao"),

    ("Logomarca Parcerias / Co-assinatura NTICS+Vibra", "A. Identidade Visual",
     "Layout padrao de co-assinatura para uso em todas as pecas onde NTICS e Vibra Energia aparecem juntos como realizacao e patrocinio.",
     "Formatos: .ai, .pdf, .png fundo branco, .png fundo transparente\nVersoes: horizontal e vertical\nTextos: 'Realizacao: NTICS Projetos' | 'Patrocinio: Vibra Energia'",
     "Na edicao 2019 havia pasta 'LOGOMARCA PARCERIAS' com co-assinatura para Whirlpool e parceiros institucionais.",
     "1k8yMrtwrC2KFn3Wzk6uTnj7aNYNiQh_7",
     "Substituir logos parceiros 2019 (Whirlpool)\nIncluir logo Vibra Energia com proporcoes corretas\nCriar versao especifica 'SEMED Manaus' se parceria confirmada\nValidar regras de marca Vibra com contato responsavel"),

    ("Assinatura de E-mail Institucional", "A. Identidade Visual",
     "Assinatura padronizada de e-mail para todos os membros da equipe durante o periodo de divulgacao e realizacao do evento.",
     "Formato: HTML + PNG\nCampos: Nome | Cargo | NTICS Projetos | Logo NTICS | Logo Vibra (pequena) | Links: Instagram + Site\nDimensoes: 500-600px largura maxima\nPrazo: antes do Release 1 (~18/05/2026)",
     "Na edicao 2019 havia variantes HTML/PNG com campo de cidade e logo Whirlpool.",
     "1yRSiHYSOdOe9Rne3ayJMduFwrXzO5sa6",
     "Atualizar logo para Vibra Energia\nRemover referencias a cidades 2019\nIncluir hashtag #EcoarteManaus ou #CaminhaoODS"),

    ("Envelopamento do Container (arte lateral/traseira)", "B. Sinalizacao do Container",
     "Arte completa para envelopamento externo do container: paineis laterais, traseira e cabine — identifica visualmente o projeto durante transporte e na praca.",
     "Subconjuntos: (a) lateral esquerda, (b) lateral direita, (c) traseira, (d) adesivo cabine\nArquivo fonte: .ai em escala, sangria minima 5mm\nResolucao: 72-100dpi em escala real\nMaterial: adesivo vinil com laminacao",
     "Na edicao 2019 havia 3 subpastas: EXTERNO, INTERNO e ADESIVO CABINE. Arquivos .ai em escala 1:10.",
     "1abp4KsXv5KTKjmEt-6-uJ7Jwh48HWqz5",
     "Atualizar tema: Conhecendo os ODS → Ecoarte + ODS 3\nSubstituir Whirlpool → Vibra Energia\nAdaptar elementos ao tema 'Meu Corpo, Minhas Regras'\nVerificar se dimensoes do container sao as mesmas de 2019"),

    ("Lona Testeira Principal", "B. Sinalizacao do Container",
     "Lona de grande formato na frente do palco/container, visivel a distancia, identificando o evento para o publico na Praia de Ponta Negra.",
     "Dimensao sugerida: 8m x 3m (confirmar com producao)\nArquivo fonte: .ai\nMaterial: lona blackout 380g com ilhos a cada 50cm\nElementos obrigatorios: nome do evento, data (14/06/2026), local, logos NTICS + Vibra, ODS 3",
     "Na edicao 2019 o arquivo era 'lona-palco_joinville_final.ai' (10MB). Usado como fundo de palco em Joinville.",
     "1xuChsLSc0YPtK33x-JuE5JpJH7NnPWcY",
     "Adaptar layout para 'Praia de Ponta Negra — Manaus'\nAtualizar data para 14/06/2026\nSubstituir logos Whirlpool → Vibra Energia\nConfirmar dimensoes com empresa de sinalizacao local"),

    ("Backdrop Entrada / Painel de Abertura", "B. Sinalizacao do Container",
     "Painel de fundo na entrada do container: area de foto para visitantes e identificacao visual do espaco.",
     "Dimensoes referencia 2019: 460cm x 460cm\nArquivo fonte: .ai\nMaterial: lona blackout 380g com estrutura de aluminio\nElementos: logomarca evento, ODS 3, hashtag, logos patrocinadores",
     "Na edicao 2019 havia backdrop de 460x460cm (arquivo 20MB .ai). Subpastas: MAPA VERSAO A4 e ARQUIVO.",
     "16DzuDDz1aEouJwOCu9BvEK-3ZMIppvVD",
     "Confirmar tamanho 460x460cm para o espaco em Ponta Negra\nAtualizar data, cidade e logos\nIncluir ODS 3 em destaque\nCriar versao A4 do mapa do evento adaptada para Manaus"),

    ("Totens de Sinalizacao", "B. Sinalizacao do Container",
     "Totens verticais de piso para sinalizar as diferentes zonas de atividades dentro e ao redor do container.",
     "Dimensao padrao: 60cm x 180cm\nQuantidade estimada: 8-12 unidades\nMaterial: PVC rigido ou lona com chassi de aluminio\nConteudo: icone da zona + nome da atividade + ODS relacionado",
     "Na edicao 2019 havia pasta 'TOTENS' com sinalizacao vertical para as zonas internas do caminhao e das tendas ODS.",
     "1nzJOXZ7cmutGz7nyIncXuZonPaom2KFY",
     "Mapear zonas de atividade do Ecoarte 2026 (confirmar programacao)\nAdaptar tema visual para cada zona ao contexto de Manaus\nODS 3 em destaque mas manter referencia aos demais ODS"),

    ("Plaquinhas Internas", "B. Sinalizacao do Container",
     "Sinalizacao interna de mesa e parede: identificacao de estacoes, instrucoes de atividades, identificacao de artefatos expositivos.",
     "Formatos: A5 (mesa) e A4 (parede)\nImpressao: papel couche 250g plastificado ou acrilico\nQuantidade: 20-30 unidades\nArquivo fonte: .ai com template padrao",
     "Na edicao 2019 havia pasta 'PLAQUINHAS' com variantes de sinalizacao interna para as 4 estacoes do caminhao.",
     "1tvYdBRco3xlYdyTgqz_n-rY3LwryEMYN",
     "Mapear estacoes internas do container Ecoarte 2026\nAdaptar textos para tema ODS 3 / Ecoarte\nIncluir instrucoes em portugues simples para publico escolar\nVerificar necessidade de plaquinhas bilingues (portugues/indigena) em Manaus"),

    ("Wide Banner / Faixa Externa", "B. Sinalizacao do Container",
     "Faixa horizontal de grande formato para uso externo, aumentando visibilidade do evento a distancia na Praia de Ponta Negra.",
     "Dimensoes estimadas: 10m x 1m ou 15m x 1m\nMaterial: lona blackout 380g com ilhos\nConteudo: nome do evento + data + logo NTICS/Vibra\nArquivo fonte: .ai horizontal",
     "Na edicao 2019 havia pasta 'WIDE BANNER' com faixas horizontais para uso externo na praca.",
     "1R6gHlaaNzrR4s9jhAfn7R_bilpML0_sR",
     "Verificar ponto de fixacao disponivel na Praia de Ponta Negra\nConfirmar dimensoes com equipe de producao local\nAtualizar data e cidade"),

    ("Banners ODS / Bandeiras Tematicas", "B. Sinalizacao do Container",
     "Conjunto de banners ou bandeiras representando os ODS presentes no evento, sinalizando as tendas/zonas tematicas.",
     "Quantidade: 1 banner por ODS presente (minimo ODS 3 + 4-6 ODS adicionais)\nFormato: roll-up 80x200cm ou bandeiras 60x90cm\nConteudo: icone oficial ODS + numero + nome",
     "Na edicao 2019 a pasta 'BANNER CODS PRE ACAO' tinha banners dos 17 ODS para uso nas tendas e na praca.",
     "11h31i0vnClKYLxMaABXuj9L2xeiZWxB0",
     "Definir quais ODS serao trabalhados em Manaus (ODS 3 principal + outros)\nVerificar se e preciso redesenhar os banners ou usar icones ODS padrao\nAdaptar para o espaco da Praia de Ponta Negra"),

    ("Banners Parceiros / Patrocinadores", "B. Sinalizacao do Container",
     "Banners de sinalizacao com logos dos parceiros e patrocinadores, posicionados na entrada e nas principais areas do evento.",
     "Formato: roll-up 80x200cm\nQuantidade: 4-6 unidades\nConteudo: logos Vibra Energia, NTICS Projetos, parceiros institucionais Manaus",
     "Na edicao 2019 havia pasta 'BANNERS MIDIAS PARTNER' com variantes para parceiros de midia e institucionais.",
     "1vX1aqRW3vp8YfTgHaVg8X-d85uFAz-mb",
     "Atualizar lista de parceiros para Manaus 2026\nAguardar confirmacao de parceiros locais (prefeitura, SEMED, universidades)\nIncluir regras de proporcao da marca Vibra conforme manual"),

    ("Lona Area de Atividade (tema Ecoarte)", "B. Sinalizacao do Container",
     "Lona de delimitacao e identificacao visual para a area de atividade Ecoarte (arte com materiais reutilizados), criando espaco imersivo na praca.",
     "Dimensoes: ~6m x 4m (estimar com espaco disponivel)\nMaterial: lona colorida\nConteudo: identidade visual Ecoarte + elementos de atividade (cores, texturas, ODS 3)",
     "Na edicao 2019 havia pasta 'LONA CULINARIA SUSTENTAVEL'. Em 2026 o equivalente e a area de atividade Ecoarte.",
     "1kiEAVczWEL0NsrDtzVe1HpPCQgJRIATf",
     "Redesenhar para tema Ecoarte: arte com materiais reutilizados\nIncorporar ODS 3 e elementos visuais de saude/bem-estar\nDefinir tamanho exato com equipe de producao"),

    ("Cartaz do Evento", "C. Impressos do Evento",
     "Cartaz oficial do evento Ecoarte Manaus 2026 para distribuicao em escolas publicas, pontos de cultura e secretarias.",
     "Formato: A2 (420x594mm) e A3 (297x420mm)\nImpressao: couche 150g 4x0\nTiragem: 200 unidades A2 + 300 A3\nConteudo obrigatorio: nome do evento, data (14/06/2026), local (Praia de Ponta Negra), logos, hashtag, URL/Instagram",
     "Na edicao 2019 o cartaz foi criado como 'cartaz_caminhao-ods.ai'. Design de Bruna Seibel.",
     "13akTex84PIrf1IZHAaTbHIf0T1u8_VRc",
     "Trocar nome para Ecoarte\nAtualizar data, local e cidade\nSubstituir visual Whirlpool → Vibra Energia\nIncluir ODS 3 como tema central"),

    ("Folder / Programacao do Dia", "C. Impressos do Evento",
     "Material impresso com programacao completa do dia 14/06/2026 para distribuir ao publico na entrada. Guia de atividades.",
     "Formato: A4 dobrado (fechado A5) ou A5\nImpressao: couche 120g 4x4\nTiragem: 1.000 unidades\nConteudo: grade horaria, descricao de atividades, mapa do espaco, logos",
     "Na edicao 2019 havia pasta 'FOLDER programacao joinville' com folder do dia.",
     "12iSCvcRwT3E5FjC78L9WH2d_yOIRUAJ8",
     "Aguardar programacao completa do dia 14/06 (Angelo confirma)\nIncluir 3 turnos: manha regenerativa, tarde escolar, noite MPB + influenciadores\nIncluir mapa simplificado do espaco em Ponta Negra"),

    ("Mapa do Evento / Layout do Espaco", "C. Impressos do Evento",
     "Mapa impresso e/ou em banner com o layout do espaco do evento, indicando zonas de atividades, palco, banheiros, entrada, saida.",
     "Formato impresso: A3 ou A4\nFormato banner: 80x120cm\nConteudo: planta do espaco com zonas numeradas + legenda",
     "Na edicao 2019 havia 'MAPA DO EVENTO GERAL JOINVILLE' com versao impressa.",
     "1ulavfp7JM3Wfju6GjlG0Uj9pQKArRRKJ",
     "Adaptar planta para Praia de Ponta Negra (espaco ao ar livre)\nCoordenar com producao antes de criar arte\nCriar versao digital para WhatsApp e Stories"),

    ("Certificado de Participacao", "C. Impressos do Evento",
     "Certificado para escolas participantes, educadores e voluntarios do evento Ecoarte Manaus 2026.",
     "Formato: A4 horizontal\nImpressao: couche 150g 1x0\nCampos variaveis: nome do participante, carga horaria, data\nAssinaturas: Diretor NTICS + representante Vibra ou SEMED",
     "Na edicao 2019 havia pasta 'CERTIFICADO' com template para participantes de oficinas e talks.",
     "1TkPKbCwAEvw8PM-DAXWt_f1TTk",
     "Incluir referencias ao Ecoarte e ODS 3\nSubstituir assinaturas conforme parceiros confirmados\nCriar versao digital (PDF) para envio por e-mail apos o evento"),

    ("Imantado / Brinde Lembranca", "C. Impressos do Evento",
     "Imantado personalizado do projeto para distribuicao ao publico como brinde de lembranca do evento.",
     "Formato: 9x6cm ou 10x7cm\nMaterial: papel fotografico com adesivo magnetico\nTiragem: 500-1.000 unidades\nConteudo: logomarca Ecoarte + ODS 3 + hashtag + Instagram",
     "Na edicao 2019 havia pasta 'IMANTADO' com arte de imantado personalizado do Caminhao ODS.",
     "1THMqcDtuGmPNqeOrnB2ef4BemKgJdfEI",
     "Adaptar arte para Ecoarte 2026 e ODS 3\nVerificar orcamento de producao (Abilio aprova)\nConfirmar tiragem com base na estimativa de publico (6.000 pessoas)"),

    ("Camisetas da Equipe", "D. Vestuario e Uniformes",
     "Camisetas personalizadas para identificacao da equipe NTICS e voluntarios durante o evento.",
     "Tecido: malha PV ou algodao 30.1\nEstampa: serigrafia ou sublimacao frontal — logo Ecoarte + 'EQUIPE'\nTamanhos: P, M, G, GG\nQuantidade: ~30 unidades (equipe NTICS + voluntarios locais)",
     "Na edicao 2019 havia pasta 'CAMISETAS engajamento' com arte para serigrafia frontal com logomarca e verso com ODS.",
     "1p39yoI5XIe13fYQPfndCnDVikhCSaYba",
     "Atualizar estampa para Ecoarte 2026\nVerificar regras de uso da marca Vibra em vestuario\nLevantar tamanhos da equipe com antecedencia (minimo 30 dias antes)"),

    ("Coletes de Identificacao", "D. Vestuario e Uniformes",
     "Coletes para identificacao de coordenadores e membros com funcao de apoio ao visitante durante o evento.",
     "Tipo: colete de pano com bolso\nQuantidade: 10-15 unidades\nIdentificacao: logo Ecoarte + cargo (COORDENACAO / APOIO / VOLUNTARIO)\nCores: diferenciar cargos por cor",
     "Na edicao 2019 havia pasta 'COLETES' com arte diferenciando cargos por cor.",
     "1diPSiBIhqQZf_rvSL6xAQrJSHRyU7FiD",
     "Confirmar quantidade por funcao com Abilio/Angelo\nVerificar se fornecedor de camisetas tambem faz coletes\nDefinir sistema de cores: coordenadores, monitores, voluntarios"),

    ("Kit Pedagogico / Material do Professor", "E. Materiais Educacionais",
     "Material de apoio pedagogico enviado as escolas antes do evento, para professores prepararem os alunos para a visita ao Ecoarte.",
     "Componentes: (a) Guia do Educador (PDF 4-8 pag), (b) Material do Aluno (folha A4 frente/verso), (c) Atividade pre-evento\nDistribuicao: envio digital para SEMED + impressao nas escolas\nPrazo: disponivel 30 dias antes do evento (14/05/2026)",
     "Na edicao 2019 havia pasta 'MATERIAIS EDUCACIONAIS PED' com Guia do Educador, Material do Aluno, Oficinas e Workshops. Enviado 1 mes antes.",
     "1yOboTs-axkTh4jk1AFLkc5n0iRW1gkYz",
     "Adaptar tema ODS 3 / 'Meu Corpo, Minhas Regras' para linguagem escolar\nIncluir atividade sobre saude alinhada a BNCC\nCoordenar com SEMED Manaus para validacao pedagogica\nCriar versao para ensino fundamental I e II separadamente"),

    ("Jogo Conhecendo os ODS (adaptado para Ecoarte)", "E. Materiais Educacionais",
     "Jogo educativo adaptado da versao 2019 para o tema Ecoarte, usando os ODS como base para atividade ludica.",
     "Tipo: jogo de cartas ou tabuleiro simplificado\nTiragem: 50-100 kits\nComponentes: cards, tabuleiro impresso, instrucoes\nArquivo fonte: .ai",
     "Na edicao 2019 havia pasta 'JOGO CONHECENDO OS ODS' com jogo de cartas/tabuleiro sobre os 17 ODS.",
     "17N0qY-ig2CxuG5XXHNXANxFjXguk92xW",
     "Verificar se o jogo original pode ser reaproveitado com ajustes minimos\nAdaptar para dar destaque ao ODS 3\nConsiderar versao digital (Kahoot) para escolas sem recurso de impressao"),

    ("Jogo Ecoarte / Atividade Interativa", "E. Materiais Educacionais",
     "Atividade interativa especifica do Ecoarte — criacao artistica com materiais reutilizados — conectando expressao artistica a temas de saude e sustentabilidade.",
     "Formato: instrucoes em banner A2 ou em cards\nPublico: criancas e adolescentes de escolas publicas\nTempo de atividade: 20-30 minutos\nProducao do kit: Abilio orcar",
     "Na edicao 2019 havia pasta 'JOGO ECOGAME DA RECICLAGEM' com atividade interativa de reciclagem para criancas.",
     "1XQVFnkO9ykS6JcWmRXEc",
     "Repensar atividade para tema Ecoarte: arte com materiais reutilizados + ODS 3\nConectar ao tema 'Meu Corpo, Minhas Regras' de forma ludica\nDefinir quem facilita a atividade (monitor treinado)"),

    ("Rota dos ODS / Trilha Tematica do Container", "E. Materiais Educacionais",
     "Roteiro de visita guiada dentro e ao redor do container, com sinalizacao que orienta o visitante pela trilha tematica dos ODS.",
     "Formato: sinalizacao no chao (adesivos) + cards de parede numerados\nNumero de estacoes: 5-8\nArquivo fonte: .ai (mapa da rota)",
     "Na edicao 2019 havia pasta 'ROTA DOS ODS' guiando visitantes pelas atividades dos 17 ODS.",
     "1ndBAj1LVm95XYBO1X7y2UiexbQVNRlo5",
     "Adaptar rota para Praia de Ponta Negra\nFocar no ODS 3 como estacao principal, com estacoes complementares\nCriar versao impressa para distribuir como mapa-roteiro"),

    ("Copo / Brinde do Evento", "F. Brindes",
     "Copo personalizado Ecoarte como brinde para participantes selecionados (escolas, imprensa, parceiros).",
     "Material: copo de plastico reusavel ou caneca de ceramica\nQuantidade: 200-500 unidades\nPersonalizacao: logo Ecoarte + ODS 3 + hashtag\nOrcamento: Abilio aprova",
     "Na edicao 2019 havia pasta 'COPO' com arte de copo personalizado do Caminhao ODS para publico selecionado.",
     "1niGvs5xqrQblNY6F1n6Wgqu4uClJ7uWG",
     "Verificar alinhamento com Vibra (marca no copo?)\nConsiderar copo ecologico (aluminio ou bambu) para reforcar sustentabilidade\nConfirmar tiragem com base em publico-alvo"),

    ("Apresentacao Institucional do Projeto", "G. Institucional",
     "Deck de apresentacao do Ecoarte Manaus 2026 para reunioes com secretarias, parceiros, imprensa e autoridades.",
     "Formato: Google Slides ou PowerPoint\nExtensao: 15-20 slides\nPublico: secretarias de educacao, parceiros, imprensa\nConteudo: contexto NTICS, historico do projeto, proposta Manaus 2026, ODS 3, patrocinio Vibra, impacto esperado (6.000 pessoas, 400+ alunos)",
     "Na edicao 2019 havia 'APRESENTACAO CONHECENDO OS ODS WHIRLPOOL.pdf' (1.3MB). Estrutura: conceito, engajamento, atividades, plano de comunicacao, legado.",
     "1g3TobtJwgynYYFf2TiqeRc-LtjZ4w-0r",
     "Atualizar todo conteudo para Ecoarte 2026 e Vibra Energia\nIncluir dados de Manaus (parceiros locais, escolas, alunos esperados)\nFocar no ODS 3 como tema central\nValidar com Abilio antes de reunioes externas"),

    ("Convite Oficial para Secretarias de Educacao", "G. Institucional",
     "Documento formal de convite enviado pela NTICS para a SEMED e demais secretarias parceiras.",
     "Formato: carta em papel timbrado NTICS (PDF)\nConteudo: apresentacao breve do projeto, proposta de parceria, data e local, solicitacao de mobilizacao de escolas\nAssinatura: Abilio Martins ou representante legal NTICS\nPrazo de envio: ate 01/05/2026",
     "Na edicao 2019 havia pasta 'CONVITE SECRETARIA' com carta-convite para secretarias das cidades do roteiro.",
     "1QwpBkDaGRr2jfaFEonjwZS4CM3KPHUTo",
     "Personalizar para SEMED Manaus\nIncluir informacoes sobre ODS 3 e tema do evento\nMencionar numero estimado de alunos a atender (400+)\nVerificar outros orgaos a convidar (Secretaria de Saude, UFAM)"),

    ("Talks / Agenda de Palestras e Paineis", "G. Institucional",
     "Material de apresentacao e divulgacao da programacao de Talks no dia anterior ao evento (12/06/2026) em universidade parceira.",
     "Formato: PDF de programacao (A4) + arte para divulgacao digital\nConteudo: tema do Talk, palestrantes confirmados, universidade anfitria, data (12/06/2026), horario\nArte digital: feed Instagram + story",
     "Na edicao 2019 havia pasta 'TALKS' com material para talks realizados no dia anterior ao evento em cada cidade.",
     "1sm1VrsiZZc7H5vwO4nCyngy9GGAzAlBN",
     "Confirmar universidade parceira em Manaus (Angelo / Abilio)\nConfirmar palestrantes e tema do Talk de 12/06\nCriar programacao visual alinhada com identidade Ecoarte\nDefinir canal de transmissao (presencial / online / hibrido)"),

    ("Relatorio de Impacto do Evento", "G. Institucional",
     "Documento final de prestacao de contas e impacto do evento Ecoarte Manaus 2026 para a Vibra Energia.",
     "Formato: PDF 20-30 paginas + versao executiva 4-6 pag\nConteudo: numeros do evento (publico, escolas, alunos), cobertura de midia, fotos, depoimentos, ODS impactados, legado\nPrazo: rascunho 30 dias apos o evento",
     "Na edicao 2019 havia pasta 'RELATORIOS' com relatorio de impacto das 3 cidades.",
     "15D2khnHu1Bs1MO_BBJhofWOi0F-gtCnP",
     "Criar template antes do evento para facilitar preenchimento\nIncluir pagina de resultados por cidade (Manaus separado de RJ)\nAlinhar com Vibra quais KPIs sao prioritarios"),

    ("Plano de Midia", "G. Institucional",
     "Documento estrategico de midia paga e espontanea para o evento Ecoarte Manaus 2026.",
     "Formato: Google Slides ou PDF\nConteudo: canais organicos, assessoria de imprensa, parceiros de midia, impulsionamento pago (se houver), cronograma de publicacoes por fase\nPrazo: versao inicial ate 15/05/2026",
     "Na edicao 2019 havia pasta 'PLANO DE MIDIA' com documento estrategico para as 3 cidades.",
     "1VM0IIgle-RDmLm-Dj9j-TS4qzb26dSE1",
     "Adaptar para Manaus 2026\nIncluir assessoria de imprensa com releases e mailing Manaus\nDefinir se ha orcamento para midia paga (Instagram Ads)"),

    ("Apresentacao / Deck Executivo do Projeto", "H. Elementos de Producao",
     "Deck resumido para reunioes rapidas de prospecao de parceiros, autoridades e patrocinadores para futuras edicoes.",
     "Formato: Google Slides (maximo 10 slides)\nPublico: executivos, decisores\nConteudo: problema, solucao, impacto 2019-2025, proposta 2026, patrocinio",
     "Nao ha referencia direta de 2019 para este item especifico.",
     "",
     "Criar do zero com base na apresentacao institucional mais completa\nFoco em dados de impacto e proposta de valor para novos patrocinadores"),

    ("Video de Abertura (para telas no container)", "H. Elementos de Producao",
     "Video institucional de 2-4 minutos exibido nas telas internas do container, introduzindo os ODS e o projeto Ecoarte.",
     "Duracao: 2-4 minutos (loop)\nFormato: MP4 1080p ou 4K\nConteudo: o que sao os ODS, o que e o Ecoarte, ODS 3, mensagem do projeto\nProducao: video maker NTICS ou terceirizado",
     "O container ja tinha telas com videos sobre os ODS em 2019, mas nao ha briefing especifico.",
     "",
     "Definir se sera producao propria ou reaproveitamento de conteudo existente\nVerificar se Vibra tem video institucional para incluir\nTestar resolucao nas telas do container antes do evento"),

    ("Kit de Onboarding da Equipe / Voluntarios", "H. Elementos de Producao",
     "Material de boas-vindas e instrucoes para membros da equipe e voluntarios, garantindo alinhamento antes do evento.",
     "Formato: Google Doc ou PDF + slides\nConteudo: missao do evento, calendario, fluxograma de responsabilidades, contatos chave, FAQ\nDistribuicao: grupo WhatsApp da equipe + Drive\nPrazo: 1 semana antes do evento (07/06/2026)",
     "Nao ha referencia direta de 2019.",
     "",
     "Criar template adaptavel para cada evento do roteiro\nIncluir mapa do espaco e posicoes de cada membro\nIncluir script de resposta para perguntas frequentes sobre ODS 3"),

    ("PPT de Capacitacao da Equipe", "H. Elementos de Producao",
     "Apresentacao de treinamento para monitores e voluntarios, cobrindo conteudo do evento (ODS 3, Ecoarte, dinamicas) e funcoes.",
     "Formato: Google Slides\nExtensao: 20-30 slides\nConteudo: o que sao os ODS, ODS 3, sobre o Ecoarte, como facilitar cada atividade, duvidas frequentes\nPrazo: pronto ate 07/06/2026",
     "Nao ha referencia direta de 2019.",
     "",
     "Basear no conteudo da apresentacao institucional e no kit pedagogico\nIncluir exercicios praticos para fixacao\nPreparar com linguagem acessivel para voluntarios sem formacao em sustentabilidade"),

    ("Programacao Completa do Evento (doc oficial)", "H. Elementos de Producao",
     "Documento de referencia interno com grade horaria completa do dia 14/06/2026 — coordenacao da producao e base para o folder impresso.",
     "Formato: Google Doc ou Planilha\nConteudo: horarios por turno, responsaveis por atividade, palco, nome do artista/palestrante\nPrazo: versao final ate 31/05/2026",
     "Nao ha referencia direta de 2019.",
     "",
     "Usar como base o plano de 3 turnos\nSincronizar com Angelo para confirmar artistas MPB da noite\nConfirmar faixas horarias com producao local"),

    ("Registro Fotografico Profissional", "H. Elementos de Producao",
     "Cobertura fotografica do evento 14/06/2026 por fotografo profissional, para relatorio de impacto e portfolio NTICS.",
     "Formato de entrega: RAW + JPEG 300dpi\nQuantidade minima: 200-300 fotos editadas\nCobertura: setup, abertura, atividades, publico, palco, equipe, autoridades\nFornecedor: fotografo local Manaus\nPrazo entrega: 5 dias uteis",
     "O projeto tinha cobertura fotografica em todas as edicoes, mas sem briefing especifico.",
     "",
     "Contatar fotografos locais de Manaus com antecedencia\nPassar briefing visual: fotos com pessoas, emocao, diversidade, ODS visiveis\nGarantir autorizacao de uso de imagem (foco em menores de idade)"),

    ("Registro em Video / Filmagem do Evento", "H. Elementos de Producao",
     "Captacao de video para aftermovie e conteudo pos-evento, incluindo depoimentos de participantes.",
     "Formato de entrega: MP4 1080p\nDuracao do aftermovie: 2-3 minutos\nMaterial bruto: 2-4 horas de captacao\nDepoimentos: 5-10 entrevistas curtas\nFornecedor: videomaker NTICS ou terceirizado local",
     "Nao ha referencia de briefing especifico de 2019.",
     "",
     "Verificar se o video maker do projeto cobre este evento\nPreparar roteiro de entrevistas e perguntas\nGarantir autorizacao de imagem para todos os entrevistados"),

    ("Clipping de Midia (monitoramento de mencoes)", "H. Elementos de Producao",
     "Compilacao de todas as publicacoes e mencoes do evento na imprensa e redes sociais.",
     "Periodo: 01/06 a 30/06/2026\nCanais: G1 Amazonas, portais regionais, CBN Amazonas, Instagram\nEntregavel: planilha com links + prints + metricas de alcance\nResponsavel: Angelo (imprensa) + Lucas (redes)",
     "Nao ha referencia de briefing especifico de 2019.",
     "",
     "Configurar Google Alerts para 'Ecoarte Manaus', 'Caminhao ODS Manaus', 'Vibra Energia Manaus'\nIncluir mencoes organicas em Instagram no monitoramento"),

    ("Relatorio Parcial (para Vibra — durante evento)", "H. Elementos de Producao",
     "Relatorio intermediario enviado a Vibra durante ou logo apos o evento com primeiros numeros e registros fotograficos.",
     "Formato: PDF 2-4 paginas\nConteudo: publico estimado, fotos do evento, destaques da programacao, primeiras mencoes de imprensa\nPrazo: ate 48h apos o evento (16/06/2026)",
     "Nao ha referencia direta de 2019.",
     "",
     "Criar template antes do evento para agilizar preenchimento\nDefinir com Vibra quais KPIs sao prioritarios\nIncluir fotos selecionadas pelo fotografo sem edicao completa"),

    ("Relatorio Final de Impacto (com fotos e dados)", "H. Elementos de Producao",
     "Documento completo consolidando os dois eventos (Manaus + RJ) para a Vibra Energia, referente a Cota 2 do patrocinio.",
     "Formato: PDF 20-30 paginas + versao executiva 4-6 pag\nConteudo: resultados quantitativos, fotos profissionais, depoimentos, ODS impactados, legado\nPrazo: rascunho 30 dias apos evento RJ (28/09/2026)",
     "Nao ha referencia direta de 2019.",
     "",
     "Criar template unificado consolidando Manaus e RJ\nReservar secao para carta de agradecimento da NTICS a Vibra\nIncluir proposta de continuidade / edicoes futuras"),
]

assert len(PECAS) == 39, f"Esperado 39 pecas, encontradas {len(PECAS)}"

# ── Date parsing ─────────────────────────────────────────────────────────────

MONTH_MAP = {
    "jan": 1, "fev": 2, "mar": 3, "abr": 4, "mai": 5, "jun": 6,
    "jul": 7, "ago": 8, "set": 9, "out": 10, "nov": 11, "dez": 12
}


def parse_date_ms(date_str):
    """Converte string de data para milissegundos (ClickUp).
    Formatos: "07/jun" (DD/mmm), "ago/set" (mmm/mmm), "mai/26" (mmm/YY).
    """
    s = date_str.lower().strip()
    if "/" not in s:
        return None
    parts = s.split("/")
    if len(parts) != 2:
        return None
    left, right = parts

    # "DD/mmm" → data especifica (ex: "07/jun" → 2026-06-07)
    if left.isdigit() and right in MONTH_MAP:
        day = int(left)
        month = MONTH_MAP[right]
        dt = datetime(2026, month, day, tzinfo=timezone.utc)
        return int(dt.timestamp() * 1000)

    # "mmm/mmm" → usa o primeiro mes, fim do mes (ex: "ago/set" → 31/08/2026)
    if left in MONTH_MAP and right in MONTH_MAP:
        month = MONTH_MAP[left]
        last_day = calendar.monthrange(2026, month)[1]
        dt = datetime(2026, month, last_day, tzinfo=timezone.utc)
        return int(dt.timestamp() * 1000)

    # "mmm/YY" → fim do mes (ex: "mai/26" → 31/05/2026)
    if left in MONTH_MAP:
        try:
            year = 2000 + int(right) if len(right) <= 2 else int(right)
        except ValueError:
            year = 2026
        month = MONTH_MAP[left]
        last_day = calendar.monthrange(year, month)[1]
        dt = datetime(year, month, last_day, tzinfo=timezone.utc)
        return int(dt.timestamp() * 1000)

    return None


# ── Description builders ──────────────────────────────────────────────────────

def build_comm_desc(item, canal_label, ig_refs):
    num, nome, fase, cidade, data, desc, dist, resp_a, resp_p = item
    lines = [
        f"**Canal:** {canal_label}  |  **Fase:** {fase}  |  **Cidade:** {cidade}  |  **Data:** {data}",
        f"**Publico:** {dist}",
        f"**Resp. Aprovacao:** {resp_a}  |  **Resp. Envio/Postagem:** {resp_p}",
        "",
    ]
    if desc:
        lines += ["---", "", "## NOTAS", desc, ""]
    if ig_refs:
        lines += ["---", "", "## REFERENCIA INSTAGRAM (edicoes anteriores)"]
        for label, url in ig_refs:
            lines.append(f"- [{label}]({url})")
        lines.append("")
    return "\n".join(lines)


def build_pecas_desc(peca):
    nome, secao, objetivo, specs, ref_desc, ref_id, adaptacoes = peca
    ref_url = f"{REF_BASE}{ref_id}" if ref_id else ""
    lines = [
        f"**Secao:** {secao}",
        "**Evento:** Ecoarte Container Itinerante nas Escolas — Vibra 2026",
        "**Cidade:** Manaus, AM — Praia de Ponta Negra — 14/06/2026",
        "",
        "---",
        "",
        "## OBJETIVO",
        objetivo,
        "",
        "## ESPECIFICACOES TECNICAS",
        specs,
        "",
        "## REFERENCIA 2019",
        ref_desc,
    ]
    if ref_url:
        lines.append(f"\n[Pasta Drive 2019]({ref_url})")
    lines += [
        "",
        "## ADAPTACOES PARA 2026",
        adaptacoes,
        "",
        "---",
        "",
        "## FLUXO DE APROVACAO",
        "- **Producao:** Designer NTICS",
        "- **Revisao de conteudo:** Lucas Rotta",
        "- **Aprovacao interna:** Bruna Seibel",
        "- **Aprovacao patrocinador:** Vibra Energia (via Angelo)",
    ]
    return "\n".join(lines)


# ── ClickUp API ───────────────────────────────────────────────────────────────

created = 0
failed  = 0


def create_task(name, description, parent_id, due_date_ms=None):
    global created, failed
    payload = {
        "name": name,
        "description": description,
        "parent": parent_id,
    }
    if due_date_ms:
        payload["due_date"] = due_date_ms

    if DRY_RUN:
        print(f"  [DRY] '{name[:60]}' -> parent:{parent_id}")
        created += 1
        return

    headers = {
        "Authorization": CLICKUP_API_KEY,
        "Content-Type": "application/json",
    }
    try:
        resp = requests.post(
            f"https://api.clickup.com/api/v2/list/{LIST_ID}/task",
            headers=headers,
            json=payload,
            timeout=15,
        )
        if resp.status_code == 200:
            task_id = resp.json().get("id", "?")
            print(f"  OK  '{name[:60]}' -> {task_id}")
            created += 1
        else:
            print(f"  ERR '{name[:60]}' -> {resp.status_code}: {resp.text[:120]}")
            failed += 1
    except Exception as e:
        print(f"  EXC '{name[:60]}' -> {e}")
        failed += 1

    time.sleep(0.6)  # rate limit: ~100 req/min


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    if not CLICKUP_API_KEY and not DRY_RUN:
        print("ERRO: CLICKUP_API_KEY nao definido.")
        print("Execute: set CLICKUP_API_KEY=pk_... && python tools/integrations/create_clickup_tasks_133.py")
        print("Ou: python tools/integrations/create_clickup_tasks_133.py --dry-run")
        sys.exit(1)

    mode = "DRY-RUN" if DRY_RUN else "LIVE"
    print(f"\n=== create_clickup_tasks_133 | {mode} ===\n")

    print("--- COMUNICACAO DIGITAL (Manaus) ---\n")

    # Numeros a excluir: RJ-only e Ambas pos-RJ (set/out 2026)
    EXCLUIR = {
        8, 9, 10, 11, 12, 13,     # Email RJ
        19, 20, 21, 22,            # WhatsApp RJ
        32, 33, 34, 35,            # Redes Sociais RJ
        44, 45, 46, 47, 48, 49,   # Assessoria RJ
        14,  # Relatorio Impacto Final Vibra (Ambas, out/26)
        36,  # Numeralha Impacto Total Cota 2 (Ambas, set/26)
        37,  # LinkedIn Resultados Vibra (Ambas, set/26)
        50,  # Release Final Cota 2 (Ambas, set/26)
    }

    FASE_PARENT = {"Pre": PARENT_PRE, "Durante": PARENT_DURANTE, "Pos": PARENT_POS}

    for secao in SECOES:
        canal    = secao["canal"]
        label    = secao["label_display"]
        print(f"\n[{label}]")

        for item in secao["items"]:
            num, nome, fase, cidade, data, desc, dist, resp_a, resp_p = item
            if num in EXCLUIR:
                continue
            parent_id = PARENT_PECAS if canal == "kit" else FASE_PARENT.get(fase, PARENT_PRE)
            ig_refs   = get_ig_refs(nome, canal)
            description = build_comm_desc(item, label, ig_refs)
            due_ms    = parse_date_ms(data)
            create_task(nome, description, parent_id, due_ms)

    print("\n\n--- PECAS DO EVENTO (39 itens) ---\n")

    for peca in PECAS:
        nome = peca[0]
        description = build_pecas_desc(peca)
        create_task(nome, description, PARENT_PECAS)

    print(f"\n=== Concluido: {created} criadas | {failed} erros ===")


if __name__ == "__main__":
    main()
