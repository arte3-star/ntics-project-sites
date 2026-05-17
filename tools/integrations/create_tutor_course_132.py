#!/usr/bin/env python3
"""
Cria o curso Estação Samarco no TutorLMS via REST API.
Estrutura: 1 curso → 8 tópicos (D1-D8) → lições por tópico.

Uso:
  python tools/integrations/create_tutor_course_132.py
"""
import base64
import io
import json
import ssl
import sys
import urllib.request
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = Path(__file__).resolve().parents[2]

env = dict(
    l.split('=', 1) for l in (ROOT / '.env').read_text(encoding='utf-8').splitlines()
    if '=' in l and not l.startswith('#')
)

WP_URL = env['WP_URL'].rstrip('/')
creds = base64.b64encode(f"{env['WP_USER']}:{env['WP_APP_PASSWORD']}".encode()).decode()
AUTH = f"Basic {creds}"

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE


def api(method: str, path: str, data: dict = None) -> dict:
    url = f"{WP_URL}/wp-json/{path}"
    body = json.dumps(data).encode('utf-8') if data else None
    req = urllib.request.Request(
        url,
        data=body,
        headers={
            'Authorization': AUTH,
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        },
        method=method,
    )
    try:
        r = urllib.request.urlopen(req, context=ctx, timeout=30)
        return json.loads(r.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8', errors='replace')
        return {'error': f'HTTP {e.code}: {body[:400]}'}
    except Exception as e:
        return {'error': str(e)}


# ── Estrutura do curso ─────────────────────────────────────────────────────────

COURSE = {
    'post_title': 'Estação Samarco – Formação Digital',
    'post_content': (
        'Formação digital do Programa Estação Samarco | Territórios do Futuro. '
        '8 módulos online que complementam a formação presencial de Culinária ou Beleza, '
        'totalizando 22h e habilitando para o certificado de 50h. '
        'Conteúdo 100% prático: empreendedorismo, IA aplicada, redes sociais, gestão do negócio e geração de renda local.'
    ),
    'post_status': 'publish',
    'meta_input': {
        '_tutor_course_duration': '20:00:00',    # 20h digitais (D6 novo = 4h)
        '_tutor_course_level': 'beginner',
        '_tutor_enable_qa': 'no',
    },
}

# Cada item: (título do tópico, carga_horária, [lista de lições])
MODULOS = [
    (
        'D1 – Boas-vindas, plataforma e regulamento',
        '01:00:00',
        [
            'O que é a NTICS Projetos e o programa (vídeo 8 min)',
            'Como navegar a plataforma (vídeo 7 min)',
            'Como funciona a parte digital do curso (vídeo 6 min)',
            'Regulamento e critérios para certificação (vídeo 8 min)',
            'Termos e proteção de dados – LGPD (vídeo 6 min)',
            'Quiz inicial do módulo',
            'Aceite do regulamento',
            'Aceite do termo de tratamento de dados',
            'Cadastro complementar',
        ],
    ),
    (
        'D2 – Postura profissional e atendimento ao cliente',
        '02:00:00',
        [
            'Por que a postura define o negócio (vídeo)',
            'Apresentação pessoal e higiene profissional (vídeo)',
            'Como receber e atender o cliente (vídeo)',
            'Comunicação clara: falar, escutar, confirmar (vídeo)',
            'Como lidar com reclamações e clientes difíceis (vídeo)',
            'Atividade: autoavaliação de postura profissional',
            'Atividade: simulação de atendimento (texto + foto)',
            'Quiz final do módulo',
        ],
    ),
    (
        'D3 – Empreendedorismo: precificação, fluxo de caixa e organização',
        '03:00:00',
        [
            'O que é ser empreendedora (vídeo)',
            'Custo, preço e lucro: a diferença que salva o negócio (vídeo)',
            'Como calcular o preço certo (vídeo + planilha)',
            'Fluxo de caixa: o que entra, o que sai, o que sobra (vídeo)',
            'Organização básica do negócio (vídeo)',
            'Atividade: precifique 3 produtos ou serviços seus',
            'Atividade: preencha o fluxo de caixa de 1 semana',
            'Quiz final do módulo',
        ],
    ),
    (
        'D4 – IA aplicada a vendas e divulgação',
        '03:00:00',
        [
            'O que é inteligência artificial e por que te importa (vídeo)',
            'ChatGPT e ferramentas gratuitas para o dia a dia (vídeo)',
            'Como criar textos para divulgação com IA (vídeo)',
            'Como criar imagens para redes sociais com IA (vídeo)',
            'Automações simples com WhatsApp Business (vídeo)',
            'Atividade: crie um texto de divulgação com IA',
            'Atividade: crie uma imagem de produto com IA',
            'Quiz final do módulo',
        ],
    ),
    (
        'D5 – WhatsApp Business e redes sociais',
        '03:00:00',
        [
            'WhatsApp Business: configuração e recursos essenciais (vídeo)',
            'Como responder rápido e parecer profissional (vídeo)',
            'Instagram para negócios locais: o básico que funciona (vídeo)',
            'Como tirar fotos boas com o celular (vídeo)',
            'Frequência de posts e o que postar cada semana (vídeo)',
            'Atividade: configure o WhatsApp Business completo',
            'Atividade: publique um post e envie o link',
            'Quiz final do módulo',
        ],
    ),
    (
        'D6 – Gestão do Seu Negócio',
        '04:00:00',
        [
            'Controle financeiro simples: caixa diário (vídeo)',
            'MEI e formalização: quando vale e como fazer (vídeo)',
            'Fidelização: como fazer o cliente voltar sempre (vídeo)',
            'Organização da agenda e do tempo (vídeo)',
            'Crescendo com estrutura: do informal ao organizado (vídeo)',
            'Atividade: preencha o caixa dos últimos 7 dias',
            'Atividade: crie sua lista de 10 clientes',
            'Atividade: escreva uma mensagem de retorno para WhatsApp',
            'Quiz final do módulo',
        ],
    ),
    (
        'D7 – Geração de renda local e oportunidades no território',
        '02:00:00',
        [
            'Mercado local: olhar para a cidade com olhos de empreendedora (vídeo)',
            'Onde estão os clientes – mapeamento do território (vídeo)',
            'Parcerias locais: do salão ao mercado, da igreja ao posto de saúde (vídeo)',
            'Eventos e datas comemorativas como oportunidades de renda (vídeo)',
            'Como atender empresas locais (vídeo)',
            'Cooperação entre participantes do programa (vídeo)',
            'Histórias de quem começou e cresceu (vídeo)',
            'Atividade: mapa de oportunidades da sua cidade',
            'Quiz final do módulo',
        ],
    ),
    (
        'D8 – Projeto de aplicação prática e preparação para certificação',
        '02:00:00',
        [
            'Revisão geral: o que você aprendeu nos 8 módulos (vídeo)',
            'Seu plano dos próximos 30 dias (vídeo + template)',
            'Como funciona o certificado e o e-certificado.com (vídeo)',
            'Projeto final: preencha seu plano de 30 dias',
            'Atividade: reflita sobre o que vai mudar a partir de amanhã',
            'Quiz de certificação (nota mínima 70%)',
            'Aceite de conclusão e pedido de certificado',
        ],
    ),
]


def create_course() -> int | None:
    print("[tutor] Criando curso...")
    result = api('POST', 'tutor/v1/courses', COURSE)
    if 'error' in result:
        print(f"  ERRO ao criar curso: {result['error']}")
        return None
    course_id = result.get('ID') or result.get('id') or result.get('post_id')
    print(f"  Curso criado: ID={course_id}")
    return course_id


def create_topic(course_id: int, title: str, summary: str = '') -> int | None:
    data = {
        'topic_course_id': course_id,
        'topic_title': title,
        'topic_summary': summary,
    }
    result = api('POST', 'tutor/v1/topics', data)
    if 'error' in result:
        print(f"    ERRO ao criar tópico '{title}': {result['error']}")
        return None
    topic_id = result.get('topic_id') or result.get('id') or result.get('ID')
    print(f"    Tópico criado: '{title}' (ID={topic_id})")
    return topic_id


def create_lesson(topic_id: int, course_id: int, title: str) -> int | None:
    data = {
        'topic_id': topic_id,
        'course_id': course_id,
        'post_title': title,
        'post_status': 'publish',
    }
    result = api('POST', 'tutor/v1/lessons', data)
    if 'error' in result:
        print(f"      ERRO ao criar lição '{title}': {result['error']}")
        return None
    lesson_id = result.get('ID') or result.get('id') or result.get('lesson_id')
    print(f"      + {title} (ID={lesson_id})")
    return lesson_id


def main():
    course_id = create_course()
    if not course_id:
        print("[tutor] Abortando: não foi possível criar o curso.")
        sys.exit(1)

    for (title, duration, lessons) in MODULOS:
        print(f"\n[tutor] Módulo: {title}")
        topic_id = create_topic(course_id, title, f'Carga horária: {duration}')
        if not topic_id:
            continue
        for lesson_title in lessons:
            create_lesson(topic_id, course_id, lesson_title)

    print(f"\n[tutor] Concluído! Curso ID={course_id}")
    print(f"[tutor] Acesse: {WP_URL}/wp-admin/post.php?post={course_id}&action=edit")


if __name__ == '__main__':
    main()
