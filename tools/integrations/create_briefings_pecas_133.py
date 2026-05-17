#!/usr/bin/env python3
"""
create_briefings_pecas_133.py
Cria 39 Google Docs de briefing para as Pecas do Evento (tab 3 da planilha v2 P133).
Popula coluna L "Link Briefing" em cada linha de item da aba "Pecas do Evento".

Estrutura de cada doc:
  Secao 1: Identificacao (nome, secao, cidade, evento, data)
  Secao 2: Objetivo da Peca
  Secao 3: Especificacoes Tecnicas
  Secao 4: Referencia 2019 (link + descricao)
  Secao 5: Adaptacoes para 2026
  Secao 6: Fluxo de Aprovacao
"""
import sys, time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "gws"))
from gws_auth import get_credentials
from googleapiclient.discovery import build

SS_ID       = "1fccNKRv-OVwlk9Y4OyUNI3TzXN32GRqCC-qj-cgQ8c0"
TAB_PECAS   = "Pecas do Evento"
FOLDER_ID   = "1n6nvn0CWSzcidtjKlGGqMHIyccvCF09G"   # 02_Briefings — Pecas do Evento
REF_BASE    = "https://drive.google.com/drive/folders/"

EVENTO = "Ecoarte Container Itinerante nas Escolas — Vibra 2026"
CIDADE = "Manaus, AM — Praia de Ponta Negra — 14/06/2026"

# ─── Dados de cada peca ───────────────────────────────────────────────────────
# (nome_curto, secao, objetivo, specs, ref_descricao, ref_folder_id, adaptacoes)
# ref_folder_id = "" para itens sem referencia 2019 (secao H)

PECAS = [

    # ── A. IDENTIDADE VISUAL ──────────────────────────────────────────────────
    (
        "Logomarca do Projeto",
        "A. Identidade Visual",
        "Versao oficial da marca 'Ecoarte / Caminhao ODS' para uso em todas as pecas de comunicacao, sinalizacao e impressos do evento de Manaus.",
        (
            "Formatos necessarios: .ai (fonte), .pdf (impressao), .png (uso digital) e .svg\n"
            "Versoes: (1) sem cidade — uso nacional/institucional; (2) com cidade 'Manaus, AM' — uso local\n"
            "Fundo: versao fundo branco + versao fundo transparente\n"
            "Paleta: seguir identidade ODS (multicolorido) adaptada ao tema Ecoarte\n"
            "Aprovacao Vibra: necessaria antes de qualquer uso publico"
        ),
        "Na edicao 2019 a logomarca 'Caminhao Conhecendo os ODS' tinha versao 'sem cidades' (PDF+PNG+AI) e subpasta 'POR CIDADE' com versoes personalizadas para cada cidade do roteiro. Arquivos criados por Bruna Seibel (designer NTICS).",
        "1PsXpAcRi93eCB5-egV9BIrMn4s-S8E0R",
        (
            "Atualizar nome do projeto para 'Ecoarte Container Itinerante / Caminhao ODS'\n"
            "Incluir referencia ao ODS 3 (saude e bem-estar) no layout\n"
            "Criar versao 'Manaus, AM 2026' na subpasta Por Cidade\n"
            "Substituir nome do patrocinador (Whirlpool → Vibra Energia)\n"
            "Garantir co-assinatura NTICS + Vibra conforme aprovacao"
        ),
    ),
    (
        "Logomarca Parcerias / Co-assinatura NTICS+Vibra",
        "A. Identidade Visual",
        "Layout padrao de co-assinatura para uso em todas as pecas onde NTICS e Vibra Energia aparecem juntos como realizacao e patrocinio.",
        (
            "Formatos: .ai, .pdf, .png fundo branco, .png fundo transparente\n"
            "Versoes: horizontal e vertical\n"
            "Proporcao: respeitar area de respiro minima de cada marca (solicitar manual de marca Vibra)\n"
            "Textos padroes: 'Realizacao: NTICS Projetos' | 'Patrocinio: Vibra Energia'"
        ),
        "Na edicao 2019 havia pasta 'LOGOMARCA PARCERIAS' com variantes de co-assinatura para Whirlpool, instituicoes parceiras e secretarias de educacao.",
        "1k8yMrtwrC2KFn3Wzk6uTnj7aNYNiQh_7",
        (
            "Substituir logos de parceiros 2019 (Whirlpool, instituicoes regionais)\n"
            "Incluir logo Vibra Energia com proporcoes corretas (solicitar vetor oficial a Vibra)\n"
            "Criar versao especifica 'Secretaria de Educacao de Manaus' se houver parceria confirmada\n"
            "Validar regras de uso da marca Vibra com o contato responsavel"
        ),
    ),
    (
        "Assinatura de E-mail Institucional",
        "A. Identidade Visual",
        "Assinatura padronizada de e-mail para todos os membros da equipe do projeto durante o periodo de divulgacao e realizacao do evento.",
        (
            "Formato: HTML + PNG (para clientes sem suporte HTML)\n"
            "Campos: Nome | Cargo no projeto | NTICS Projetos | Logo NTICS | Logo Vibra (pequena) | Links: Instagram + Site\n"
            "Dimensoes imagem: 500-600px largura maxima\n"
            "Fonte: compativel com clientes de e-mail (Arial/Helvetica)\n"
            "Prazo de implantacao: antes do envio do Release 1 (~18/05/2026)"
        ),
        "Na edicao 2019 havia pasta 'ASSINATURA' com variantes de assinatura HTML/PNG, incluindo campo de cidade e logo do patrocinador Whirlpool.",
        "1yRSiHYSOdOe9Rne3ayJMduFwrXzO5sa6",
        (
            "Atualizar logo patrocinador para Vibra Energia\n"
            "Remover referencias a cidades 2019 (Joinville, Rio Claro)\n"
            "Incluir hashtag #EcoarteManaus ou #CaminhaoODS\n"
            "Criar variante para equipe local Manaus se necessario"
        ),
    ),

    # ── B. SINALIZACAO DO CONTAINER ───────────────────────────────────────────
    (
        "Envelopamento do Container (arte lateral/traseira)",
        "B. Sinalizacao do Container",
        "Arte completa para o envelopamento externo do container-caminhao: paineis laterais, traseira e cabine, que identificam visualmente o projeto na cidade durante o transporte e na praca.",
        (
            "Especificacoes do veiculo: confirmar dimensoes exatas com equipe de logistica\n"
            "Subconjuntos: (a) lateral esquerda, (b) lateral direita, (c) traseira, (d) adesivo cabine\n"
            "Arquivo fonte: .ai em escala, sangria minima 5mm\n"
            "Resolucao impressao: 72-100dpi em escala real (grande formato)\n"
            "Material impressao: adesivo vinil com laminacao\n"
            "Fornecedor: empresa de grafica grande formato local ou de SP"
        ),
        "Na edicao 2019 havia 3 subpastas: EXTERNO (paineis laterais/traseira), INTERNO e ADESIVO CABINE. Os arquivos eram .ai em escala 1:10 com dimensoes do caminhao modelo.",
        "1abp4KsXv5KTKjmEt-6-uJ7Jwh48HWqz5",
        (
            "Atualizar tema: Conhecendo os ODS → Ecoarte + ODS 3 (saude)\n"
            "Substituir patrocinador Whirlpool → Vibra Energia\n"
            "Adaptar elementos visuais ao tema 'Meu Corpo, Minhas Regras'\n"
            "Verificar se dimensoes do container sao as mesmas de 2019\n"
            "Incluir URL e @handle Instagram atualizados"
        ),
    ),
    (
        "Lona Testeira Principal",
        "B. Sinalizacao do Container",
        "Lona de grande formato posicionada na frente do palco/container, visivel a distancia, identificando o evento para o publico que circula na Praia de Ponta Negra.",
        (
            "Dimensoes referencia 2019: verificar arquivo 'lona-palco_joinville_final' (fundo de palco)\n"
            "Dimensao sugerida: 8m x 3m (confirmar com equipe de producao)\n"
            "Arquivo fonte: .ai\n"
            "Material: lona blackout 380g com ilhos a cada 50cm\n"
            "Elementos obrigatorios: nome do evento, data (14/06/2026), logos NTICS + Vibra, ODS 3"
        ),
        "Na edicao 2019 o arquivo era 'lona-palco_joinville_final.ai' (10MB). Usado como fundo de palco e testeira principal do container em Joinville.",
        "1xuChsLSc0YPtK33x-JuE5JpJH7NnPWcY",
        (
            "Adaptar layout para 'Praia de Ponta Negra — Manaus'\n"
            "Atualizar data para 14/06/2026\n"
            "Substituir logos Whirlpool → Vibra Energia\n"
            "Confirmar dimensoes com empresa de sinalizacao local"
        ),
    ),
    (
        "Backdrop Entrada / Painel de Abertura",
        "B. Sinalizacao do Container",
        "Painel de fundo posicionado na entrada do container, serve como area de foto para visitantes e como identificacao visual do espaco ao entrar no evento.",
        (
            "Dimensoes referencia 2019: 460cm x 460cm (arquivo 'backdrop-inicial_joinville_final_460x460')\n"
            "Arquivo fonte: .ai\n"
            "Material: lona blackout 380g com estrutura de aluminio\n"
            "Elementos: logomarca evento, ODS 3, hastag, logos patrocinadores\n"
            "Tambem havia 'MAPA VERSAO A4' e 'regua-joinville.ai' na mesma pasta"
        ),
        "Na edicao 2019 havia backdrop de 460x460cm (arquivo 20MB .ai). Subpastas: 'MAPA VERSAO A4' (mapa do evento em A4) e 'ARQUIVO' (versoes antigas).",
        "16DzuDDz1aEouJwOCu9BvEK-3ZMIppvVD",
        (
            "Confirmar que 460x460cm ainda e o tamanho adequado para o espaco em Ponta Negra\n"
            "Atualizar data, cidade e logos\n"
            "Incluir ODS 3 em destaque (tema Saude/Ecoarte)\n"
            "Criar versao A4 do mapa do evento adaptada para Manaus\n"
            "Definir se habra estrutura de aluminio propria ou alugada"
        ),
    ),
    (
        "Totens de Sinalizacao",
        "B. Sinalizacao do Container",
        "Totens verticais de piso para sinalizar as diferentes zonas de atividades dentro e ao redor do container, auxiliando o fluxo de visitantes.",
        (
            "Dimensao padrao: 60cm x 180cm (confirmar com producao)\n"
            "Quantidade estimada: 8-12 unidades (1 por zona de atividade + entrada/saida)\n"
            "Material: PVC rigido ou lona com chassi de aluminio\n"
            "Conteudo: icone da zona + nome da atividade + ODS relacionado\n"
            "Arquivo fonte: .ai (template com variantes por zona)"
        ),
        "Na edicao 2019 havia pasta 'TOTENS' com arquivos de sinalizacao vertical para as zonas internas do caminhao e das tendas ODS na praca.",
        "1nzJOXZ7cmutGz7nyIncXuZonPaom2KFY",
        (
            "Mapear as zonas de atividade do Ecoarte 2026 (confirmar programacao)\n"
            "Adaptar tema visual para cada zona ao contexto de Manaus\n"
            "ODS 3 em destaque — mas manter referencia aos demais ODS presentes\n"
            "Verificar se ha zonas novas que precisam de totem proprio"
        ),
    ),
    (
        "Plaquinhas Internas",
        "B. Sinalizacao do Container",
        "Sinalizacao interna de mesa e parede dentro do container: identificacao de estacoes, instrucoes de atividades, identificacao de artefatos expositivos.",
        (
            "Formatos: A5 (mesa) e A4 (parede)\n"
            "Impressao: papel couche 250g plastificado ou acrílico\n"
            "Quantidade: definir por estacao (estimativa: 20-30 unidades)\n"
            "Conteudo varia: nome da estacao, instrucoes da atividade, ODS relacionado\n"
            "Arquivo fonte: .ai com template padrao"
        ),
        "Na edicao 2019 havia pasta 'PLAQUINHAS' com variantes de sinalizacao interna para as 4 estacoes do caminhao.",
        "1tvYdBRco3xlYdyTgqz_n-rY3LwryEMYN",
        (
            "Mapear estacoes internas do container Ecoarte 2026\n"
            "Adaptar textos para tema ODS 3 / Ecoarte\n"
            "Incluir instrucoes em portugues simples para publico escolar\n"
            "Verificar se ha plaquinhas bilingues (portugues/indigena) necessarias para Manaus"
        ),
    ),
    (
        "Wide Banner / Faixa Externa",
        "B. Sinalizacao do Container",
        "Faixa horizontal de grande formato para uso externo, suspensa entre estruturas, aumentando a visibilidade do evento a distancia no espaco da Praia de Ponta Negra.",
        (
            "Dimensoes estimadas: 10m x 1m ou 15m x 1m\n"
            "Material: lona blackout 380g com ilhos\n"
            "Conteudo: nome do evento + data + logo NTICS/Vibra\n"
            "Arquivo fonte: .ai horizontal"
        ),
        "Na edicao 2019 havia pasta 'WIDE BANNER' com faixas horizontais para uso externo na praca.",
        "1R6gHlaaNzrR4s9jhAfn7R_bilpML0_sR",
        (
            "Verificar ponto de fixacao disponivel na Praia de Ponta Negra\n"
            "Confirmar dimensoes com equipe de producao local\n"
            "Atualizar data e cidade"
        ),
    ),
    (
        "Banners ODS / Bandeiras Tematicas",
        "B. Sinalizacao do Container",
        "Conjunto de banners ou bandeiras representando os ODS presentes no evento, sinalizando as tendas/zonas tematicas na area da praca.",
        (
            "Quantidade: 1 banner por ODS presente (minimo ODS 3 + 4 a 6 ODS adicionais)\n"
            "Formato: roll-up 80x200cm ou bandeiras 60x90cm\n"
            "Material: tecido ou lona — decidir com producao\n"
            "Conteudo: icone oficial ODS + numero + nome\n"
            "Fonte: icones ODS disponíveis no site da ONU (domínio publico)"
        ),
        "Na edicao 2019 a pasta 'BANNER CODS_ PRE ACAO' tinha banners dos ODS para uso nas tendas e na praca. Total de 17 ODS representados.",
        "11h31i0vnClKYLxMaABXuj9L2xeiZWxB0",
        (
            "Definir quais ODS serao trabalhados em Manaus (ODS 3 principal + outros)\n"
            "Verificar se e preciso redesenhar os banners ou usar os icones ODS padrao\n"
            "Adaptar para o espaco disponivel na Praia de Ponta Negra"
        ),
    ),
    (
        "Banners Parceiros / Patrocinadores",
        "B. Sinalizacao do Container",
        "Banners de sinalizacao com logos dos parceiros institucionais e patrocinadores, posicionados na entrada e nas principais areas do evento.",
        (
            "Formato: roll-up 80x200cm\n"
            "Quantidade: 1 por patrocinador/parceiro principal (estimativa: 4-6 unidades)\n"
            "Conteudo: logos Vibra Energia, NTICS Projetos, parceiros institucionais Manaus\n"
            "Arquivo fonte: .ai por parceiro"
        ),
        "Na edicao 2019 havia pasta 'BANNERS MIDIAS PARTNER' com variantes de banners para parceiros de midia (veiculos de imprensa) e parceiros institucionais.",
        "1vX1aqRW3vp8YfTgHaVg8X-d85uFAz-mb",
        (
            "Atualizar lista de parceiros para Manaus 2026\n"
            "Aguardar confirmacao de parceiros institucionais locais (prefeitura, SEMED, universidades)\n"
            "Incluir regras de proporcao da marca Vibra conforme manual"
        ),
    ),
    (
        "Lona Area de Atividade (tema Ecoarte)",
        "B. Sinalizacao do Container",
        "Lona de delimitacao e identificacao visual para a area de atividade tematica Ecoarte (arte com materiais reutilizados), criando um espaco imersivo na praca.",
        (
            "Dimensoes: conforme planta do espaco (estimar ~6m x 4m)\n"
            "Material: lona colorida\n"
            "Conteudo: identidade visual Ecoarte + elementos de atividade (cores, texturas, ODS 3)\n"
            "Arquivo fonte: .ai"
        ),
        "Na edicao 2019 havia pasta 'LONA CULINARIA SUSTENTAVEL' para a zona de culinaria sustentavel. Em 2026 o equivalente e a area de atividade Ecoarte.",
        "1kiEAVczWEL0NsrDtzVe1HpPCQgJRIATf",
        (
            "Redesenhar para tema Ecoarte: arte com materiais reutilizados\n"
            "Incorporar ODS 3 e elementos visuais de saude/bem-estar\n"
            "Definir tamanho exato com equipe de producao"
        ),
    ),

    # ── C. IMPRESSOS DO EVENTO ────────────────────────────────────────────────
    (
        "Cartaz do Evento",
        "C. Impressos do Evento",
        "Cartaz oficial do evento Ecoarte Manaus 2026, para distribuicao em escolas publicas, pontos de cultura, secretarias e pontos de grande circulacao em Manaus.",
        (
            "Formato: A2 (420x594mm) e A3 (297x420mm)\n"
            "Impressao: couche 150g 4x0 (frente colorida, verso branco)\n"
            "Tiragem: 200 unidades A2 + 300 unidades A3 (confirmar com producao)\n"
            "Arquivo fonte: .ai com sangria de 3mm\n"
            "Conteudo obrigatorio: nome do evento, data (14/06/2026), local (Praia de Ponta Negra), logos, hashtag, URL/Instagram"
        ),
        "Na edicao 2019 o cartaz foi criado como 'cartaz_caminhao-ods.ai' (.ai 2.2MB + .pdf). Design de Bruna Seibel.",
        "13akTex84PIrf1IZHAaTbHIf0T1u8_VRc",
        (
            "Trocar nome do evento para Ecoarte\n"
            "Atualizar data, local e cidade\n"
            "Substituir visual Whirlpool → Vibra Energia\n"
            "Incluir ODS 3 como tema central\n"
            "Adaptar distribuicao para rede de escolas parceiras em Manaus"
        ),
    ),
    (
        "Folder / Programacao do Dia",
        "C. Impressos do Evento",
        "Material impresso com a programacao completa do dia 14/06/2026, para distribuir ao publico na entrada do evento. Serve como guia de atividades.",
        (
            "Formato: A4 dobrado (fechado A5) ou A5\n"
            "Impressao: couche 120g 4x4 (frente e verso coloridos)\n"
            "Tiragem: 1.000 unidades\n"
            "Conteudo: grade horaria por turno (manha/tarde/noite), descricao de atividades, mapa do espaco, logos\n"
            "Arquivo fonte: .ai com sangria 3mm"
        ),
        "Na edicao 2019 havia pasta 'FOLDER_ programacao joinville' com folder de programacao do dia.",
        "12iSCvcRwT3E5FjC78L9WH2d_yOIRUAJ8",
        (
            "Aguardar programacao completa do dia 14/06 (Angelo confirma)\n"
            "Incluir 3 turnos conforme plano: manha regenerativa, tarde escolar, noite MPB + influenciadores\n"
            "Incluir mapa simplificado do espaco na Praia de Ponta Negra\n"
            "Adaptar linguagem para publico geral de Manaus"
        ),
    ),
    (
        "Mapa do Evento / Layout do Espaco",
        "C. Impressos do Evento",
        "Mapa impresso e/ou em banner com o layout do espaco do evento, indicando zonas de atividades, palco, banheiros, entrada, saida e pontos de referencia.",
        (
            "Formato impresso: A3 ou A4 (para distribuicao)\n"
            "Formato banner: 80x120cm\n"
            "Conteudo: planta do espaco com zonas numeradas + legenda\n"
            "Arquivo fonte: .ai"
        ),
        "Na edicao 2019 havia 'MAPA DO EVENTO GERAL JOINVILLE' com versao impressa e 'MAPA VERSAO A4' dentro da pasta do Backdrop.",
        "1ulavfp7JM3Wfju6GjlG0Uj9pQKArRRKJ",
        (
            "Adaptar planta para a Praia de Ponta Negra (espaco ao ar livre, diferente de praca interna)\n"
            "Coordenar com equipe de producao para confirmar layout antes de criar a arte\n"
            "Criar versao digital para compartilhar em WhatsApp e Instagram Stories"
        ),
    ),
    (
        "Certificado de Participacao",
        "C. Impressos do Evento",
        "Certificado para escolas participantes, educadores e voluntarios que participaram do evento Ecoarte Manaus 2026.",
        (
            "Formato: A4 horizontal (297x210mm)\n"
            "Impressao: papel sulfite 90g ou couche 150g 1x0 (impressao laser local)\n"
            "Campos variaveis: nome do participante, carga horaria, data\n"
            "Arquivo fonte: .ai (template base) + versao editavel para preenchimento\n"
            "Assinaturas: Diretor NTICS + representante Vibra ou Secretaria de Educacao"
        ),
        "Na edicao 2019 havia pasta 'CERTIFICADO' com template de certificado para participantes. Usado em oficinas e talks.",
        "1TkPKbCwAEvw8PM-DAXWt_f1TTk",
        (
            "Incluir referencias ao Ecoarte e ODS 3\n"
            "Substituir assinaturas conforme parceiros confirmados em Manaus\n"
            "Verificar se ha necessidade de certificados para alunos (escolas) e para educadores separadamente\n"
            "Criar versao digital (PDF) para envio por e-mail apos o evento"
        ),
    ),
    (
        "Imantado / Brinde Lembranca",
        "C. Impressos do Evento",
        "Imantado personalizado do projeto para distribuicao ao publico como brinde de lembranca do evento Ecoarte Manaus 2026.",
        (
            "Formato: 9x6cm ou 10x7cm\n"
            "Material: papel fotografico com adesivo magnetico\n"
            "Tiragem: 500-1.000 unidades\n"
            "Conteudo: logomarca Ecoarte + ODS 3 + hashtag + Instagram\n"
            "Arquivo fonte: .ai"
        ),
        "Na edicao 2019 havia pasta 'IMANTADO' com arte de imantado personalizado do projeto Caminhao ODS para distribuicao ao publico.",
        "1THMqcDtuGmPNqeOrnB2ef4BemKgJdfEI",
        (
            "Adaptar arte para Ecoarte 2026 e ODS 3\n"
            "Verificar orcamento de producao (Abilio aprova)\n"
            "Confirmar tiragem com base na estimativa de publico (6.000 pessoas — % de distribuicao)"
        ),
    ),

    # ── D. VESTUARIO E UNIFORMES ──────────────────────────────────────────────
    (
        "Camisetas da Equipe",
        "D. Vestuario e Uniformes",
        "Camisetas personalizadas para identificacao da equipe NTICS e voluntarios durante o evento Ecoarte Manaus 2026.",
        (
            "Tecido: malha PV (67% poliester / 33% viscose) ou algodao 30.1\n"
            "Cores disponiveis: branca ou preta (definir com identidade visual do evento)\n"
            "Estampa: serigrafia ou sublimacao frontal — logo Ecoarte + 'EQUIPE'\n"
            "Tamanhos: P, M, G, GG (levantar tamanhos com todos os integrantes)\n"
            "Quantidade: equipe NTICS (~10) + voluntarios locais (~20) = ~30 unidades\n"
            "Fornecedor: grafica local Manaus ou enviar de SP"
        ),
        "Na edicao 2019 havia pasta 'CAMISETAS_ engajamento' com arte de camiseta para equipe e voluntarios. Serigrafia frontal com logomarca e verso com ODS.",
        "1p39yoI5XIe13fYQPfndCnDVikhCSaYba",
        (
            "Atualizar estampa para Ecoarte 2026\n"
            "Verificar regras de uso da marca Vibra em vestuario\n"
            "Levantar tamanhos da equipe com antecedencia (minimo 30 dias antes)\n"
            "Confirmar cor da camiseta com identidade visual aprovada"
        ),
    ),
    (
        "Coletes de Identificacao",
        "D. Vestuario e Uniformes",
        "Coletes para identificacao de coordenadores e membros de equipe com funcao de apoio ao visitante durante o evento.",
        (
            "Tipo: colete de pano com bolso ou colete refletivo (depende do contexto)\n"
            "Quantidade: 10-15 unidades\n"
            "Identificacao: bordado ou patch com logo Ecoarte + cargo (COORDENACAO / APOIO / VOLUNTARIO)\n"
            "Cores: diferenciar cargos por cor se possivel"
        ),
        "Na edicao 2019 havia pasta 'COLETES' com arte de colete para equipe de coordenacao. Diferenciava cargos por cor.",
        "1diPSiBIhqQZf_rvSL6xAQrJSHRyU7FiD",
        (
            "Confirmar quantidade por funcao com Abilio/Angelo\n"
            "Verificar se fornecedor de camisetas tambem faz coletes\n"
            "Definir sistema de cores para diferenciar: coordenadores, monitores, voluntarios"
        ),
    ),

    # ── E. MATERIAIS EDUCACIONAIS ─────────────────────────────────────────────
    (
        "Kit Pedagogico / Material do Professor",
        "E. Materiais Educacionais",
        "Material de apoio pedagogico enviado as escolas publicas antes do evento, para que professores possam preparar os alunos para a visita ao Ecoarte.",
        (
            "Componentes: (a) Guia do Educador (PDF 4-8 pag), (b) Material do Aluno (folha A4 frente/verso), (c) Atividade pre-evento (enquete ou atividade de reflexao)\n"
            "Distribuicao: envio digital para SEMED + impressao nas escolas parceiras\n"
            "Prazo: material disponivel 30 dias antes do evento (14/05/2026)\n"
            "Arquivo fonte: .ai + .pdf editavel"
        ),
        "Na edicao 2019 havia pasta 'MATERIAIS EDUCACIONAIS _ PED' com subpastas: Oficinas, Material do Aluno, Workshops, Guia do Educador. Material enviado as escolas 1 mes antes.",
        "1yOboTs-axkTh4jk1AFLkc5n0iRW1gkYz",
        (
            "Adaptar tema do ODS 3 / 'Meu Corpo, Minhas Regras' para linguagem escolar\n"
            "Incluir atividade sobre saude e bem-estar alinhada a BNCC\n"
            "Coordenar com SEMED Manaus para validacao pedagogica\n"
            "Criar versao para ensino fundamental I e II separadamente"
        ),
    ),
    (
        "Jogo Conhecendo os ODS (adaptado para Ecoarte)",
        "E. Materiais Educacionais",
        "Jogo educativo adaptado da versao 2019 para o tema Ecoarte, utilizando os ODS como base para atividade ludica durante o evento nas escolas e na praca.",
        (
            "Tipo: jogo de cartas ou tabuleiro simplificado\n"
            "Tiragem: 50-100 kits (para uso no evento e nas escolas parceiras)\n"
            "Componentes: cards, tabuleiro impresso, instrucoes\n"
            "Producao: designer NTICS + parceria editorial ou grafica\n"
            "Arquivo fonte: .ai"
        ),
        "Na edicao 2019 havia pasta 'JOGO CONHECENDO OS ODS' com o jogo original criado para o projeto. Era um jogo de cartas/tabuleiro sobre os 17 ODS.",
        "17N0qY-ig2CxuG5XXHNXANxFjXguk92xW",
        (
            "Verificar se o jogo original pode ser reaproveitado com ajustes minimos\n"
            "Adaptar para dar destaque ao ODS 3 (Saude)\n"
            "Considerar producao de versao digital (app ou Kahoot) para escolas sem recurso de impressao"
        ),
    ),
    (
        "Jogo Ecoarte / Atividade Interativa",
        "E. Materiais Educacionais",
        "Atividade interativa especifica do Ecoarte — criacao artistica com materiais reutilizados — que conecta expressao artistica a temas de saude e sustentabilidade.",
        (
            "Formato: instrucoes em banner A2 ou em cards\n"
            "Materiais necessarios: definir com equipe de producao (papelao, tesoura, cola etc)\n"
            "Publico: criancas e adolescentes de escolas publicas\n"
            "Tempo de atividade: 20-30 minutos\n"
            "Producao do kit de atividade: Abilio orcar"
        ),
        "Na edicao 2019 havia pasta 'JOGO ECOGAME DA RECICLAGEM' com atividade interativa de reciclagem para criancas.",
        "1XQVFnkO9ykS6JcWmRXEc",
        (
            "Repensar a atividade para o tema Ecoarte: arte com materiais reutilizados + ODS 3\n"
            "Conectar ao tema 'Meu Corpo, Minhas Regras' de forma ludica\n"
            "Definir quem facilita a atividade (monitor treinado)"
        ),
    ),
    (
        "Rota dos ODS / Trilha Tematica do Container",
        "E. Materiais Educacionais",
        "Roteiro de visita guiada dentro e ao redor do container, com sinalizacao que orienta o visitante a seguir uma trilha tematica pelos diferentes ODS.",
        (
            "Formato: sinalizacao no chao (adesivos) + cards de parede numerados\n"
            "Numero de estacoes: 5-8 (conforme layout do espaco)\n"
            "Producao: adesivos de piso + placas\n"
            "Arquivo fonte: .ai (mapa da rota)"
        ),
        "Na edicao 2019 havia pasta 'ROTA DOS ODS' com a trilha tematica guiando visitantes pelas atividades dos 17 ODS no espaco do evento.",
        "1ndBAj1LVm95XYBO1X7y2UiexbQVNRlo5",
        (
            "Adaptar rota para o espaco da Praia de Ponta Negra\n"
            "Focar no ODS 3 como estacao principal, com estacoes complementares\n"
            "Criar versao impressa para distribuir como mapa-roteiro"
        ),
    ),

    # ── F. BRINDES ────────────────────────────────────────────────────────────
    (
        "Copo / Brinde do Evento",
        "F. Brindes",
        "Copo personalizado Ecoarte como brinde para participantes selecionados (escolas, imprensa, parceiros). Reforca identidade do projeto e sua mensagem de sustentabilidade.",
        (
            "Material: copo de plastico reusavel ou caneca de ceramica\n"
            "Quantidade: 200-500 unidades\n"
            "Personalizacao: logo Ecoarte + ODS 3 + hashtag\n"
            "Orcamento: Abilio aprova\n"
            "Fornecedor: grafica de brindes SP ou Manaus"
        ),
        "Na edicao 2019 havia pasta 'COPO' com arte de copo personalizado do projeto Caminhao ODS. Era um item de brinde para publico selecionado.",
        "1niGvs5xqrQblNY6F1n6Wgqu4uClJ7uWG",
        (
            "Verificar alinhamento com patrocinador Vibra (marca no copo?)\n"
            "Considerar copo ecologico (aluminio ou bambu) para reforcar tema sustentabilidade\n"
            "Confirmar tiragem com base em publico-alvo (imprensa + escolas + autoridades)"
        ),
    ),

    # ── G. INSTITUCIONAL ──────────────────────────────────────────────────────
    (
        "Apresentacao Institucional do Projeto",
        "G. Institucional",
        "Deck de apresentacao do Ecoarte Manaus 2026 para reunioes com secretarias, parceiros institucionais, imprensa e autoridades locais antes do evento.",
        (
            "Formato: Google Slides ou PowerPoint\n"
            "Extensao: 15-20 slides\n"
            "Publico: secretarias de educacao, parceiros, imprensa\n"
            "Conteudo: contexto NTICS, historico do projeto, proposta Manaus 2026, ODS 3, patrocinio Vibra, impacto esperado (6.000 pessoas, 400+ alunos), proximos passos\n"
            "Referencia de estrutura: apresentacao 2019 com Whirlpool (PDF 1.3MB)"
        ),
        "Na edicao 2019 havia apresentacao 'APRESENTACAO CONHECENDO OS ODS _ WHIRLPOOL.pdf' (1.3MB) e versao PROGRAMACAO_TALKS para imprensa. Estrutura: conceito, engajamento, atividades, plano de comunicacao, legado.",
        "1g3TobtJwgynYYFf2TiqeRc-LtjZ4w-0r",
        (
            "Atualizar todo o conteudo para Ecoarte 2026 e Vibra Energia\n"
            "Incluir dados de Manaus (parceiros locais, escolas, numero de alunos esperados)\n"
            "Focar no ODS 3 como tema central\n"
            "Incluir resultados de edicoes anteriores como prova de impacto\n"
            "Validar com Abilio antes de usar em reunioes externas"
        ),
    ),
    (
        "Convite Oficial para Secretarias de Educacao",
        "G. Institucional",
        "Documento formal de convite enviado pela NTICS para a Secretaria Municipal de Educacao de Manaus (SEMED) e demais secretarias parceiras.",
        (
            "Formato: carta em papel timbrado NTICS (PDF)\n"
            "Conteudo: apresentacao breve do projeto, proposta de parceria, data e local do evento, solicitacao de mobilizacao de escolas\n"
            "Assinatura: Abilio Martins ou representante legal NTICS\n"
            "Prazo de envio: ate 01/05/2026 (ja em andamento)"
        ),
        "Na edicao 2019 havia pasta 'CONVITE SECRETARIA' com carta-convite para secretarias de educacao das cidades do roteiro.",
        "1QwpBkDaGRr2jfaFEonjwZS4CM3KPHUTo",
        (
            "Personalizar para Secretaria Municipal de Educacao de Manaus (SEMED)\n"
            "Incluir informacoes sobre o ODS 3 e o tema do evento\n"
            "Mencionar numero estimado de alunos a atender (400+)\n"
            "Verificar se ha outros orgaos a convidar formalmente (Secretaria de Saude, UFAM)"
        ),
    ),
    (
        "Talks / Agenda de Palestras e Paineis",
        "G. Institucional",
        "Material de apresentacao e divulgacao da programacao de Talks que acontece no dia anterior ao evento (12/06/2026) em universidade parceira.",
        (
            "Formato: PDF de programacao (A4) + arte para divulgacao digital\n"
            "Conteudo: tema do Talk, palestrantes confirmados, universidade anfitria, data (12/06/2026), horario\n"
            "Distribuicao: redes sociais + e-mail para contatos academicos\n"
            "Arte digital: feed Instagram + story"
        ),
        "Na edicao 2019 havia pasta 'TALKS' com material para os talks realizados no dia anterior ao evento em cada cidade. Cafe da manha + apresentacao para imprensa e parceiros.",
        "1sm1VrsiZZc7H5vwO4nCyngy9GGAzAlBN",
        (
            "Confirmar universidade parceira em Manaus (Angelo / Abilio)\n"
            "Confirmar palestrantes e tema do Talk de 12/06\n"
            "Criar programacao visual alinhada com identidade Ecoarte\n"
            "Definir canal de transmissao (presencial / online / hibrido)"
        ),
    ),
    (
        "Relatorio de Impacto do Evento",
        "G. Institucional",
        "Documento final de prestacao de contas e impacto do evento Ecoarte Manaus 2026, entregue a Vibra Energia e publicado como legado do projeto.",
        (
            "Formato: PDF 20-30 paginas + versao executiva 4-6 pag\n"
            "Conteudo: numeros do evento (publico, escolas, alunos), cobertura de midia, fotos, depoimentos, ODS impactados, legado\n"
            "Prazo: rascunho 30 dias apos o evento\n"
            "Aprovacao: Abilio + Vibra antes de publicacao\n"
            "Arquivo fonte: InDesign ou Slides"
        ),
        "Na edicao 2019 havia pasta 'RELATORIOS' com relatorio de impacto das 3 cidades. Incluia dados de publico, cobertura de imprensa, fotos e ODS trabalhados.",
        "15D2khnHu1Bs1MO_BBJhofWOi0F-gtCnP",
        (
            "Criar template antes do evento para facilitar preenchimento pos-evento\n"
            "Incluir pagina de resultados por cidade (Manaus separado de RJ)\n"
            "Incluir section de midia (clipping + mencoes em redes)\n"
            "Alinhar com Vibra quais KPIs sao prioritarios para o relatorio"
        ),
    ),
    (
        "Plano de Midia",
        "G. Institucional",
        "Documento estrategico de plano de midia paga e espontanea para o evento Ecoarte Manaus 2026, incluindo canais, orcamento e cronograma.",
        (
            "Formato: Google Slides ou PDF\n"
            "Conteudo: canais organicos (Instagram, LinkedIn, WhatsApp), assessoria de imprensa, parceiros de midia, impulsionamento pago (se houver), cronograma de publicacoes por fase\n"
            "Responsavel: Lucas (estrategia) + Angelo (imprensa local)\n"
            "Prazo: versao inicial ate 15/05/2026"
        ),
        "Na edicao 2019 havia pasta 'PLANO DE MIDIA' com documento estrategico de comunicacao para as 3 cidades.",
        "1VM0IIgle-RDmLm-Dj9j-TS4qzb26dSE1",
        (
            "Adaptar para Manaus 2026 (apenas 1 cidade nesta fase)\n"
            "Incluir assessoria de imprensa com releases e mailing Manaus\n"
            "Definir se ha orcamento para midia paga (Instagram Ads)\n"
            "Integrar com plano de comunicacao digital ja criado"
        ),
    ),

    # ── H. ELEMENTOS DE PRODUCAO (sem ref 2019) ───────────────────────────────
    (
        "Apresentacao / Deck Executivo do Projeto",
        "H. Elementos de Producao",
        "Deck resumido do projeto para uso em reunioes rapidas de prospecao de parceiros, autoridades e patrocinadores para futuras edicoes.",
        (
            "Formato: Google Slides (maximo 10 slides)\n"
            "Publico: executivos, decisores\n"
            "Conteudo: problema, solucao, impacto 2019-2025, proposta 2026, patrocinio\n"
            "Responsavel: Lucas (conteudo) + designer NTICS (arte)"
        ),
        "Nao ha referencia direta de 2019 para este item especifico.",
        "",
        (
            "Criar do zero com base na apresentacao institucional mais completa\n"
            "Foco em dados de impacto e proposta de valor para novos patrocinadores\n"
            "Incluir resultados esperados de Manaus + RJ 2026"
        ),
    ),
    (
        "Video de Abertura (para telas no container)",
        "H. Elementos de Producao",
        "Video institucional de 2-4 minutos exibido continuamente nas telas internas do container, introduzindo os ODS e o projeto Ecoarte aos visitantes.",
        (
            "Duracao: 2-4 minutos (loop)\n"
            "Formato: MP4 1080p ou 4K\n"
            "Conteudo: o que sao os ODS, o que e o Ecoarte, ODS 3, mensagem do projeto\n"
            "Producao: video maker NTICS ou terceirizado\n"
            "Trilha: licenciada ou criada especialmente"
        ),
        "Nao ha referencia especifica de 2019, mas o container tinha telas com videos sobre os ODS.",
        "",
        (
            "Definir se sera producao propria ou reaproveitamento de conteudo existente\n"
            "Verificar se Vibra tem video institucional para incluir\n"
            "Testar resolucao nas telas especificas do container antes do evento"
        ),
    ),
    (
        "Kit de Onboarding da Equipe / Voluntarios",
        "H. Elementos de Producao",
        "Material de boas-vindas e instrucoes para todos os membros da equipe e voluntarios, garantindo alinhamento antes do evento.",
        (
            "Formato: Google Doc ou PDF + apresentacao rapida (slides)\n"
            "Conteudo: missao do evento, calendario, fluxograma de responsabilidades, contatos chave, FAQ para perguntas do publico\n"
            "Distribuicao: grupo WhatsApp da equipe + pasta Drive\n"
            "Prazo: 1 semana antes do evento (07/06/2026)"
        ),
        "Nao ha referencia direta de 2019.",
        "",
        (
            "Criar template adaptavel para cada evento do roteiro\n"
            "Incluir mapa do espaco e posicoes de cada membro\n"
            "Incluir script de resposta para perguntas frequentes do publico sobre ODS 3"
        ),
    ),
    (
        "PPT de Capacitacao da Equipe",
        "H. Elementos de Producao",
        "Apresentacao de treinamento para monitores e voluntarios, cobrindo o conteudo do evento (ODS 3, Ecoarte, dinamicas) e as funcoes de cada um.",
        (
            "Formato: Google Slides\n"
            "Extensao: 20-30 slides\n"
            "Conteudo: o que sao os ODS, ODS 3 em detalhes, sobre o Ecoarte, como facilitar cada atividade, duvidas frequentes\n"
            "Treinamento: presencial ou online com toda a equipe\n"
            "Prazo: pronto ate 07/06/2026"
        ),
        "Nao ha referencia direta de 2019.",
        "",
        (
            "Basear no conteudo da apresentacao institucional e no kit pedagogico\n"
            "Incluir exercicios praticos para fixacao\n"
            "Preparar com linguagem acessivel para voluntarios sem formacao em sustentabilidade"
        ),
    ),
    (
        "Programacao Completa do Evento (doc oficial)",
        "H. Elementos de Producao",
        "Documento de referencia interno com a grade horaria completa do dia 14/06/2026 — usado para coordenacao da producao e base para o folder impresso.",
        (
            "Formato: Google Doc ou Planilha\n"
            "Conteudo: horarios por turno, responsaveis por atividade, palco, nome do artista/palestrante\n"
            "Responsavel: Angelo (programacao) + Abilio (producao)\n"
            "Prazo: versao final ate 31/05/2026"
        ),
        "Nao ha referencia direta de 2019.",
        "",
        (
            "Usar como base o plano de 3 turnos do ClickUp doc 8cje8p1-46031\n"
            "Sincronizar com Angelo para confirmar artistas MPB da noite\n"
            "Confirmar faixas horarias com producao local"
        ),
    ),
    (
        "Registro Fotografico Profissional",
        "H. Elementos de Producao",
        "Cobertura fotografica do evento 14/06/2026 por fotografo profissional, para uso em relatorio de impacto, comunicacao pos-evento e portfolio NTICS.",
        (
            "Formato de entrega: RAW + JPEG 300dpi\n"
            "Quantidade minima: 200-300 fotos editadas\n"
            "Cobertura: setup, abertura, atividades, publico, palco, equipe, autoridades\n"
            "Fornecedor: fotografo profissional de Manaus (contratar localmente)\n"
            "Prazo entrega: 5 dias uteis apos o evento"
        ),
        "Nao ha referencia de briefing especifico de 2019, mas o projeto tinha cobertura fotografica em todas as edicoes.",
        "",
        (
            "Contatar fotografos locais de Manaus com antecedencia\n"
            "Passar briefing visual: fotos com pessoas, emocao, diversidade, ODS visiveis\n"
            "Garantir autorizacao de uso de imagem (foco em menores de idade)"
        ),
    ),
    (
        "Registro em Video / Filmagem do Evento",
        "H. Elementos de Producao",
        "Captacao de video do evento para producao de aftermovie e conteudo pos-evento, incluindo depoimentos de participantes.",
        (
            "Formato de entrega: MP4 1080p\n"
            "Duracao do aftermovie: 2-3 minutos\n"
            "Material bruto: 2-4 horas de captacao\n"
            "Depoimentos: 5-10 entrevistas curtas (participantes, professores, autoridades)\n"
            "Fornecedor: videomaker NTICS ou terceirizado local"
        ),
        "Nao ha referencia de briefing especifico de 2019.",
        "",
        (
            "Verificar se o video maker do projeto (briefing na pasta tools/media) cobre este evento\n"
            "Preparar roteiro de entrevistas e perguntas\n"
            "Garantir autorizacao de imagem para todos os entrevistados"
        ),
    ),
    (
        "Clipping de Midia (monitoramento de mencoes)",
        "H. Elementos de Producao",
        "Compilacao sistematica de todas as publicacoes, mencoes e coberturas do evento na imprensa e nas redes sociais.",
        (
            "Periodo de monitoramento: 01/06 a 30/06/2026\n"
            "Canais monitorados: G1 Amazonas, portais regionais, CBN Amazonas, Instagram (mencoes e reposts)\n"
            "Entregavel: planilha com links + prints das publicacoes + metricas de alcance\n"
            "Responsavel: Angelo (imprensa local) + Lucas (redes sociais)"
        ),
        "Nao ha referencia de briefing especifico de 2019.",
        "",
        (
            "Configurar Google Alerts para 'Ecoarte Manaus', 'Caminhao ODS Manaus', 'Vibra Energia Manaus'\n"
            "Usar planilha de mailing Manaus (aba Assessoria + Midia Kit) para acompanhar retorno de cada veiculo\n"
            "Incluir mencoes organicas em Instagram no monitoramento"
        ),
    ),
    (
        "Relatorio Parcial (para Vibra — durante evento)",
        "H. Elementos de Producao",
        "Relatorio intermediario enviado a Vibra Energia durante ou logo apos o evento com primeiros numeros e registros fotograficos.",
        (
            "Formato: PDF 2-4 paginas\n"
            "Conteudo: publico estimado, fotos do evento, destaques da programacao, primeiras mencoes de imprensa\n"
            "Prazo: ate 48h apos o evento (16/06/2026)\n"
            "Responsavel: Lucas (redacao) + Abilio (aprovacao)"
        ),
        "Nao ha referencia direta de 2019.",
        "",
        (
            "Criar template antes do evento para agilizar preenchimento\n"
            "Definir com Vibra quais KPIs sao prioritarios no relatorio parcial\n"
            "Incluir fotos selecionadas pelo fotografo ainda sem edicao completa"
        ),
    ),
    (
        "Relatorio Final de Impacto (com fotos e dados)",
        "H. Elementos de Producao",
        "Documento completo de prestacao de contas consolidando os dois eventos (Manaus + RJ) para a Vibra Energia, referente a Cota 2 do patrocinio.",
        (
            "Formato: PDF 20-30 paginas + versao executiva 4-6 pag\n"
            "Conteudo: resultados quantitativos (publico total, escolas, alunos, mencoes de midia), fotos profissionais, depoimentos, ODS impactados, legado\n"
            "Prazo: rascunho 30 dias apos o evento RJ (28/09/2026)\n"
            "Aprovacao: Abilio + Vibra"
        ),
        "Nao ha referencia direta de 2019.",
        "",
        (
            "Criar template unificado que consolide dados de Manaus e RJ\n"
            "Reservar secao para carta de agradecimento da NTICS a Vibra\n"
            "Incluir proposta de continuidade / edicoes futuras se relevante"
        ),
    ),
]

assert len(PECAS) == 39, f"Esperado 39 pecas, encontradas {len(PECAS)}"


def build_doc_text(peca_data):
    nome, secao, objetivo, specs, ref_desc, ref_id, adaptacoes = peca_data
    ref_url = (REF_BASE + ref_id) if ref_id else "Nao ha referencia direta de 2019."
    linhas = [
        f"BRIEFING — {nome.upper()}",
        "",
        f"Projeto: {EVENTO}",
        f"Cidade: {CIDADE}",
        f"Secao: {secao}",
        "",
        "=" * 60,
        "",
        "1. OBJETIVO DA PECA",
        objetivo,
        "",
        "=" * 60,
        "",
        "2. ESPECIFICACOES TECNICAS",
        specs,
        "",
        "=" * 60,
        "",
        "3. REFERENCIA 2019",
        ref_desc,
        "",
        f"Pasta de referencia 2019: {ref_url}",
        "",
        "=" * 60,
        "",
        "4. ADAPTACOES PARA 2026 (Ecoarte Vibra Manaus)",
        adaptacoes,
        "",
        "=" * 60,
        "",
        "5. FLUXO DE APROVACAO",
        "Producao: Designer NTICS",
        "Revisao de conteudo: Lucas Rotta",
        "Aprovacao interna: Bruna Seibel",
        "Aprovacao patrocinador: Vibra Energia (via Angelo)",
        "",
        "Status inicial: A briefar",
        f"Data limite: a definir",
        "",
    ]
    return "\n".join(linhas)


def main():
    creds = get_credentials()
    drive_svc = build("drive", "v3", credentials=creds)
    sheets_svc = build("sheets", "v4", credentials=creds)

    print(f"Criando {len(PECAS)} briefings na pasta {FOLDER_ID}...\n")

    # Mapeamento: row_sheet (1-based) → doc_url
    # Precisamos saber em qual linha de planilha cada item esta
    # Ler sheet para obter posicoes
    result = sheets_svc.spreadsheets().values().get(
        spreadsheetId=SS_ID,
        range=f"'{TAB_PECAS}'!A:A"
    ).execute()
    sheet_names = [r[0] if r else "" for r in result.get("values", [])]

    # Mapear nome → row index (0-based)
    name_to_row = {}
    for i, v in enumerate(sheet_names):
        name_to_row[v.strip()] = i

    doc_updates = []   # (row_0based, url)
    created = []

    for idx, peca in enumerate(PECAS):
        nome = peca[0]
        doc_text = build_doc_text(peca)
        doc_title = f"BRIEFING — {nome}"

        # Criar doc no Drive
        meta = {
            "name": doc_title,
            "mimeType": "application/vnd.google-apps.document",
            "parents": [FOLDER_ID],
        }
        doc_file = drive_svc.files().create(
            body=meta,
            fields="id"
        ).execute()
        doc_id = doc_file["id"]

        # Adicionar conteudo via Docs API
        docs_svc = build("docs", "v1", credentials=creds)
        docs_svc.documents().batchUpdate(
            documentId=doc_id,
            body={"requests": [{"insertText": {"location": {"index": 1}, "text": doc_text}}]}
        ).execute()

        doc_url = f"https://docs.google.com/document/d/{doc_id}/edit"

        # Encontrar a linha correspondente na planilha
        row_0 = name_to_row.get(nome.strip())
        if row_0 is not None:
            doc_updates.append((row_0, doc_url))

        created.append((nome, doc_id))
        print(f"  [{idx+1:02d}/39] {nome[:55]} OK")
        time.sleep(0.3)   # evitar rate limit

    print(f"\nTotal criados: {len(created)}")

    # Adicionar cabecalho da coluna L se nao existir
    sheets_svc.spreadsheets().values().update(
        spreadsheetId=SS_ID,
        range=f"'{TAB_PECAS}'!L1",
        valueInputOption="USER_ENTERED",
        body={"values": [["Link Briefing"]]}
    ).execute()

    # Escrever os links na coluna L
    value_data = []
    for row_0, url in doc_updates:
        sheet_row = row_0 + 1   # 1-based
        value_data.append({
            "range": f"'{TAB_PECAS}'!L{sheet_row}",
            "values": [[url]]
        })

    if value_data:
        sheets_svc.spreadsheets().values().batchUpdate(
            spreadsheetId=SS_ID,
            body={"valueInputOption": "USER_ENTERED", "data": value_data}
        ).execute()
        print(f"{len(value_data)} links escritos na coluna L.")

    print(f"\nURL Planilha: https://docs.google.com/spreadsheets/d/{SS_ID}/edit")
    print(f"URL Pasta Briefings: https://drive.google.com/drive/folders/{FOLDER_ID}")

    print("\n--- IDs dos docs criados ---")
    for nome, doc_id in created:
        print(f"{doc_id}  {nome}")


if __name__ == "__main__":
    main()
