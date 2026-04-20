"""
Reformata todas as 8 aulas do modulo Empreendedorismo (Trilha Itapoa)
com paleta da plataforma (#3c5a76 + #d12743) + icones SVG inline.

Estilo: Opcao A aprovada pelo usuario.

Uso:
    python tools/publishing/reformat_empreendedorismo.py            # gera HTML
    python tools/publishing/reformat_empreendedorismo.py --publish  # publica via Tutor LMS API
    python tools/publishing/reformat_empreendedorismo.py --verify   # so verifica
"""
import sys, json, argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools' / 'publishing'))
from negocio_cultural import _tutor_request

PRIMARY = '#3c5a76'
PRIMARY_DARK = '#2c4459'
PRIMARY_LIGHT_BG = '#eef2f6'
PRIMARY_LIGHT_BORDER = '#c8d4df'
RED = '#d12743'
RED_DARK = '#a01f36'
RED_BG = '#fdeef0'
RED_BORDER = '#f8c8d1'
TEXT = '#374151'
MUTED = '#6b7280'

COURSE_BASE = 'https://negociocultural.com.br/courses/trilha-do-conhecimento-2-2/lessons'

# ==== Icon library (Tutor LMS native font icons - survive wp_kses) ============
# Map semantic names to tutor-icon-* CSS classes (loaded by tutor-icon.min.css)
ICONS = {
    'flowchart': 'clipboard-list',
    'megaphone': 'bullhorn',
    'monitor': 'desktop',
    'users': 'user-group',
    'trending-up': 'rocket',
    'heart': 'heart-bold',
    'tag': 'tag',
    'scissors': 'badge-percent',
    'wallet': 'wallet',
    'map': 'map-pin',
    'globe': 'earth',
    'star': 'star-bold',
    'check-circle': 'circle-mark',
    'file-text': 'document-text',
    'play-circle': 'play-line',
    'external-link': 'external-link',
    'award': 'trophy',
    'flag': 'flag',
    'shield': 'privacy',
    'briefcase': 'instructor',
    'thumbs-up': 'grade',
    'graduation-cap': 'mortarboard',
}

def svg(name, size=40, color='#fff', stroke=2):
    """Render Tutor LMS font-icon. Param 'size' becomes font-size. 'stroke' ignored."""
    cls = ICONS.get(name, ICONS['star'])
    return (f'<i class="tutor-icon-{cls}" style="font-size:{size}px;color:{color};'
            f'line-height:1;display:inline-block;vertical-align:middle;"></i>')

# ==== Building blocks =========================================================
def hero(eyebrow, title, subtitle=None, gradient=(PRIMARY_DARK, PRIMARY)):
    sub = f'<p style="font-size:17px;line-height:1.55;margin:0 auto;max-width:580px;color:rgba(255,255,255,0.92);">{subtitle}</p>' if subtitle else ''
    return f'''<div style="background:linear-gradient(135deg,{gradient[0]} 0%,{gradient[1]} 100%);color:#fff;padding:48px 32px;text-align:center;border-radius:12px 12px 0 0;">
  <span style="display:inline-block;background:rgba(255,255,255,0.18);padding:6px 14px;border-radius:999px;font-size:13px;letter-spacing:0.04em;text-transform:uppercase;margin-bottom:18px;font-weight:600;color:#fff;">{eyebrow}</span>
  <h2 style="font-size:32px;font-weight:700;line-height:1.2;margin:0 0 14px;color:#fff;">{title}</h2>
  {sub}
</div>'''

def section_open(eyebrow=None):
    eb = f'<p style="text-align:center;font-size:14px;font-weight:700;letter-spacing:0.12em;text-transform:uppercase;color:{PRIMARY};margin:0 0 28px;">{eyebrow}</p>' if eyebrow else ''
    return f'<div style="background:#fff;padding:40px 32px;border-radius:0 0 12px 12px;border:1px solid #e5e7eb;border-top:none;">{eb}'

def section_close():
    return '</div>'

def numbered_card(num, icon_name, title, body_html, color='primary'):
    """Standard numbered card with icon."""
    is_red = (color == 'red')
    accent = RED if is_red else PRIMARY
    bg = RED_BG if is_red else PRIMARY_LIGHT_BG
    title_color = RED if is_red else PRIMARY
    return f'''<table role="presentation" cellpadding="0" cellspacing="0" border="0" style="width:100%;background:{bg};border-left:6px solid {accent};border-radius:8px;margin:0 0 18px;">
  <tr>
    <td style="padding:24px;width:96px;vertical-align:middle;text-align:center;">
      <div style="background:{accent};width:72px;height:72px;border-radius:16px;display:inline-block;line-height:72px;">{svg(icon_name, 40)}</div>
      <div style="color:{accent};font-weight:800;font-size:14px;margin-top:8px;letter-spacing:0.1em;">{num:02d}</div>
    </td>
    <td style="padding:24px 24px 24px 0;vertical-align:middle;">
      <h3 style="margin:0 0 8px;color:{title_color};font-size:20px;font-weight:700;">{title}</h3>
      <div style="margin:0;color:{TEXT};font-size:15px;line-height:1.55;">{body_html}</div>
    </td>
  </tr>
</table>'''

def big_quote_card(num, text):
    """Big destaque para frases-impacto."""
    return f'''<table role="presentation" cellpadding="0" cellspacing="0" border="0" style="width:100%;background:linear-gradient(135deg,{PRIMARY_LIGHT_BG} 0%,#fff 100%);border:2px solid {PRIMARY_LIGHT_BORDER};border-radius:12px;margin:0 0 18px;">
  <tr>
    <td style="padding:32px;text-align:center;">
      <div style="display:inline-block;background:{PRIMARY};color:#fff;width:44px;height:44px;border-radius:50%;line-height:44px;font-weight:800;font-size:18px;margin-bottom:16px;">{num}</div>
      <p style="font-size:18px;line-height:1.5;color:{PRIMARY_DARK};font-weight:600;margin:0;font-style:italic;">"{text}"</p>
    </td>
  </tr>
</table>'''

def link_card(title, url, hint=None, icon='external-link'):
    h = f'<p style="margin:4px 0 0;color:{MUTED};font-size:13px;">{hint}</p>' if hint else ''
    return f'''<table role="presentation" cellpadding="0" cellspacing="0" border="0" style="width:100%;background:#fff;border:1px solid #e5e7eb;border-radius:10px;margin:0 0 12px;">
  <tr>
    <td style="padding:20px;width:64px;vertical-align:middle;text-align:center;">
      <div style="background:{PRIMARY};width:48px;height:48px;border-radius:10px;display:inline-block;line-height:48px;">{svg(icon, 24)}</div>
    </td>
    <td style="padding:20px 16px 20px 0;vertical-align:middle;">
      <a href="{url}" target="_blank" rel="noopener" style="color:{PRIMARY};text-decoration:none;font-weight:700;font-size:16px;">{title}</a>{h}
      <p style="margin:6px 0 0;font-size:12px;color:{MUTED};word-break:break-all;">{url}</p>
    </td>
  </tr>
</table>'''

def cta(text, next_slug, btn_label='Próxima aula'):
    url = f'{COURSE_BASE}/{next_slug}/' if not next_slug.startswith('http') else next_slug
    return f'''<table role="presentation" cellpadding="0" cellspacing="0" border="0" style="width:100%;background:linear-gradient(135deg,{PRIMARY_DARK} 0%,{PRIMARY} 100%);border-radius:12px;margin-top:32px;">
  <tr>
    <td style="padding:28px 32px;color:#fff;font-size:17px;font-weight:500;vertical-align:middle;">{text}</td>
    <td style="padding:28px 32px 28px 0;text-align:right;vertical-align:middle;white-space:nowrap;">
      <a href="{url}" style="background:{RED};color:#fff;padding:12px 22px;border-radius:8px;text-decoration:none;font-weight:700;font-size:15px;display:inline-block;">{btn_label}</a>
    </td>
  </tr>
</table>'''

def alert_box(text, title=None, color='primary'):
    is_red = (color == 'red')
    accent = RED if is_red else PRIMARY
    bg = RED_BG if is_red else PRIMARY_LIGHT_BG
    t = f'<p style="margin:0 0 8px;color:{accent};font-size:14px;font-weight:700;letter-spacing:0.04em;text-transform:uppercase;">{title}</p>' if title else ''
    return f'<div style="background:{bg};border-left:6px solid {accent};border-radius:8px;padding:20px 24px;margin:24px 0;">{t}<p style="margin:0;color:{TEXT};font-size:15px;line-height:1.55;">{text}</p></div>'

def wrap(content):
    return f'<div style="font-family:-apple-system,\'Segoe UI\',Roboto,sans-serif;color:{TEXT};max-width:760px;margin:0 auto;">{content}</div>'

def section_heading(text):
    return f'<h3 style="font-size:22px;font-weight:700;color:{PRIMARY_DARK};margin:32px 0 16px;text-align:center;">{text}</h3>'

# ==== AULAS ===================================================================

def aula_1127_vender_mais():
    return wrap(
        hero('Empreendedorismo · Aula 2', 'Vender mais',
             '<strong style="color:#fff;">Um dos maiores desejos do empreendedor é vender mais.</strong> Por isso, elencamos alguns pilares importantes que podem te auxiliar.')
        + section_open('5 pilares para vender mais')
        + numbered_card(1, 'flowchart', 'Processos', '<p style="margin:0;">Padronize os processos de vendas e marketing digital, para gerir as vendas e os fornecedores de Marketing.</p>')
        + numbered_card(2, 'megaphone', 'Marketing Digital', '<p style="margin:0;">Planeje qual a melhor "rota" na internet para você seguir criando o seu Plano de Marketing e vendas com objetivo de atrair pela internet novas pessoas interessadas no que você vende (leads).</p>')
        + numbered_card(3, 'monitor', 'Tecnologias', '<p style="margin:0;">Se possível, implemente softwares, que são tecnologias que te ajudam a gerar indicadores de gestão para monitorar em que fase estão as oportunidades (leads) para tomar ações que gerem mais vendas. Se não for possível, conte com uma planilha excel para alimentar todas as informações que você possui.</p>')
        + numbered_card(4, 'users', 'Pessoas', '<p style="margin:0;">Se você tiver uma equipe de marketing e vendas, mesmo que pequena, treine-a para usarem os processos para atrair e transformar as oportunidades geradas (leads) em mais vendas.</p>')
        + numbered_card(5, 'trending-up', 'Vendas',
            f'<p style="margin:0 0 8px;color:{RED_DARK};font-weight:500;">Coloque o motor pra rodar:</p>'
            f'<p style="margin:0 0 6px;"><span style="color:{RED};font-weight:700;margin-right:6px;">→</span>Defina as metas do mês (Marketing e Vendas).</p>'
            f'<p style="margin:0 0 6px;"><span style="color:{RED};font-weight:700;margin-right:6px;">→</span>Audite o funil de vendas e as atividades do time (CRM). <em style="color:{MUTED};">Você vai aprender mais sobre funil de vendas no módulo de Marketing.</em></p>'
            f'<p style="margin:0 0 6px;"><span style="color:{RED};font-weight:700;margin-right:6px;">→</span>Dê feedback para o time agir e corrigir as falhas.</p>'
            f'<p style="margin:0;"><span style="color:{RED};font-weight:700;margin-right:6px;">→</span>Meça os resultados e crie novas ações de vendas e pós-vendas.</p>',
            color='red')
        + cta('Continue na próxima aula e descubra como transformar essas vendas em lucro.', '3-lucrar-2')
        + section_close()
    )

def aula_1128_lucrar():
    return wrap(
        hero('Empreendedorismo · Aula 3', 'Lucrar',
             'Além de vender mais, <strong style="color:#fff;">o empreendedor também quer lucrar.</strong> Veja três ações que aumentam a margem da sua empresa.')
        + section_open('3 ações para obter mais lucro')
        + numbered_card(1, 'heart', 'Implemente estratégias de fidelização',
            '<p style="margin:0;">Você sabia que tem maiores chances de vender novamente para quem já comprou do que de conquistar um novo cliente? Claro que o novo cliente também é extremamente importante, porém a fidelização traz resultados bastante positivos, pois além de eles voltarem, eles podem te indicar para novos clientes.</p>')
        + numbered_card(2, 'tag', 'Saiba fazer a precificação',
            '<p style="margin:0;">Atribuir o valor errado ao seu produto pode reduzir a margem de lucro da sua empresa. <strong>No módulo Financeiro</strong> você aprenderá como precificar corretamente o seu produto ou serviço.</p>')
        + numbered_card(3, 'scissors', 'Corte custos desnecessários',
            '<p style="margin:0;">É a matemática básica! Para calcular o seu lucro, subtraímos o que você gasta (custo total) do que você ganha (receita total). Então, se o custo for menor, o lucro será maior.</p>',
            color='red')
        + cta('Agora que você sabe vender e lucrar, é hora de pensar em crescer.', '4-expandir-sua-empresa')
        + section_close()
    )

def aula_1129_expandir():
    return wrap(
        hero('Empreendedorismo · Aula 4', 'Expandir sua empresa',
             '<strong style="color:#fff;">Já parou para pensar no que impede uma empresa de crescer?</strong> Conheça os 2 maiores obstáculos e os 4 aceleradores que destravam o crescimento.')
        + section_open('O que impede o crescimento')
        + numbered_card(1, 'wallet', 'Falta de controle financeiro',
            '<p style="margin:0 0 8px;">"O controle financeiro empresarial é definido pelo conjunto de ações de análise, avaliações e controle de dados financeiros de um negócio para entender suas condições financeiras." Exemplos: análise do fluxo de caixa e controle de entradas e saídas (que você aprenderá no módulo Financeiro).</p>'
            '<p style="margin:0;">Ou seja, ter o controle financeiro é fundamental para que seu negócio fique saudável e possa expandir. Fique atento a isso no seu negócio!</p>',
            color='red')
        + numbered_card(2, 'map', 'Falta de planejamento',
            '<p style="margin:0;">Um plano de negócio é um documento que descreve por escrito os objetivos de um negócio e quais passos devem ser dados para que esses objetivos sejam alcançados. Exemplos: proposta de valor, análise da concorrência e jornada do cliente.</p>',
            color='red')
        + section_heading('O que acelera o crescimento')
        + numbered_card(1, 'globe', 'Entender o mercado',
            '<p style="margin:0;">Conhecer o cenário do seu ramo e analisar os fatores externos, observar quais são os rumos da concorrência e as tendências do seu mercado.</p>')
        + numbered_card(2, 'users', 'Entender os interesses do seu cliente',
            '<p style="margin:0;">Quais seus medos, dores, desejos e sonhos?</p>')
        + numbered_card(3, 'megaphone', 'Investir em marketing',
            '<p style="margin:0;">Seja em mídias convencionais como outdoor, rádio, panfletos ou em mídias sociais como campanhas no Facebook, Instagram, Google e até influenciadores digitais da sua região.</p>')
        + numbered_card(4, 'trending-up', 'Ter processo de vendas bem definido',
            '<p style="margin:0;">Quais as etapas que seu cliente passa até fechar uma venda? Você e sua equipe têm isso bem alinhado? Se não, vale a pena separar um tempo na sua agenda para criar este processo de vendas, que vai facilitar bastante a sua vida e a vida da sua equipe.</p>')
        + cta('Antes de seguir, confira 3 fatos que todo empreendedor precisa saber.', '5-fatos-relevantes-sobre-empreendedorismo')
        + section_close()
    )

def aula_1130_fatos():
    return wrap(
        hero('Empreendedorismo · Aula 5', 'Fatos relevantes', 'Depois de saber como vender, lucrar e crescer, chegou a hora de saber 3 fatos sobre empreendedorismo que são relevantes para você.')
        + section_open('3 fatos que mudam o jeito de empreender')
        + big_quote_card(1, 'Quem cresce não é a empresa, e sim as pessoas que fazem parte dela.')
        + big_quote_card(2, 'O resultado não está somente na sua visão, mas sim na visão do cliente.')
        + big_quote_card(3, 'Todas as pessoas são capazes de gerar resultados extraordinários — desde que saibam o que fazer e paguem o preço do sucesso.')
        + cta('Hora de transformar tudo isso em prática: legalize sua empresa.', '6-como-legalizar-sua-empresa')
        + section_close()
    )

def aula_1131_legalizar():
    body = wrap(
        hero('Empreendedorismo · Aula 6', 'Como legalizar sua empresa',
             'Por fim, mas não menos importante: a <strong style="color:#fff;">importância da legalização do seu negócio.</strong>')
        + section_open()
        + alert_box(
            'A formalização e o registro da empresa geram oportunidades e ganhos para o negócio. Seu empreendimento tem mais chances de fechar parcerias, acessar linhas de crédito, exportar e receber subsídios do governo.',
            'Por que se formalizar')
        + section_heading('O que é MEI')
        + f'<p style="font-size:15px;line-height:1.65;color:{TEXT};margin:0 0 14px;">O <strong>MEI (Microempreendedor Individual)</strong> é a forma mais utilizada para se empreender no Brasil. Este regime tributário permite que pessoas que trabalham por conta própria possam abrir uma empresa para formalizar suas atividades de maneira simples e sem aquele excesso de burocracias.</p>'
        + f'<p style="font-size:15px;line-height:1.65;color:{TEXT};margin:0 0 14px;">O Microempreendedor Individual também possui uma carga tributária mais baixa perante outros regimes, e ainda tem acesso à Previdência Social. Com isso, o MEI tem direito a benefícios como auxílio-doença, licença maternidade, pensão por morte e muitos outros.</p>'
        + f'<p style="font-size:15px;line-height:1.65;color:{TEXT};margin:0 0 14px;">Como a simplicidade e a facilidade são características do MEI, a categoria faz parte do <a href="https://blog.vhsys.com.br/o-simples-nacional-e-simples-mesmo/" target="_blank" rel="noopener" style="color:{PRIMARY};font-weight:600;">Simples Nacional</a> (Sistema de Tributação Simplificada). Com essa participação no Simples, o MEI pode pagar seus impostos em apenas uma guia, trazendo mais facilidade na hora de cumprir com suas obrigações.</p>'
        + section_heading('Requisitos para ser MEI')
        + numbered_card(1, 'briefcase', 'Posição',
            '<p style="margin:0;">A pessoa empreendedora não pode ser sócia, administradora ou titular de outra empresa. Se você tem certeza sobre o seu novo negócio como MEI, é preciso encerrar as atividades da outra empresa ou sair da empresa que você ainda possui vínculo.</p>')
        + numbered_card(2, 'users', 'Empregados',
            '<p style="margin:0;">A pessoa MEI pode ter, no máximo, um empregado que receba um salário mínimo ou o piso da categoria. Essa limitação é <a href="https://blog.vhsys.com.br/regras-para-o-mei-contratar-um-funcionario/" target="_blank" rel="noopener" style="color:' + PRIMARY + ';font-weight:600;">uma das regras para a contratação sendo MEI</a>, justificada pelo seu limite de faturamento.</p>')
        + numbered_card(3, 'check-circle', 'Idade',
            '<p style="margin:0;">Ser maior de 18 anos ou menor legalmente emancipado.</p>')
        + numbered_card(4, 'wallet', 'Faturamento',
            f'<p style="margin:0;">Não ultrapassar o limite de <strong style="color:{PRIMARY_DARK};">R$ 81 mil por ano</strong>.</p>')
        + numbered_card(5, 'tag', 'Ocupação',
            '<p style="margin:0;">Sua ocupação deve estar na lista das áreas aceitas para se cadastrar como MEI, conforme a <a href="https://blog.vhsys.com.br/saiba-como-encontrar-a-cnae-de-sua-empresa/" target="_blank" rel="noopener" style="color:' + PRIMARY + ';font-weight:600;">Classificação Nacional de Atividades Econômicas (CNAE)</a>.</p>')
        + section_heading('Como abrir uma empresa MEI')
        + alert_box('Antes de tudo, é necessário fazer um Cadastro no Portal de Serviços do Governo Federal — passo obrigatório antes de começar o cadastro do MEI no Portal do Empreendedor. Esse primeiro cadastro permite ao cidadão acesso a serviços públicos digitais.', 'Pré-requisito')
        + section_heading('Documentos necessários')
        + numbered_card(1, 'file-text', 'CPF', '<p style="margin:0;">Número do CPF.</p>')
        + numbered_card(2, 'file-text', 'Título de eleitor ou IRPF',
            '<p style="margin:0;">Título de eleitor ou recibo da última declaração de imposto de renda (IRPF).</p>')
        + numbered_card(3, 'file-text', 'CEP',
            '<p style="margin:0;">CEP da residência ou local onde a empresa vai operar (verifique se a prefeitura permite que a atividade seja desempenhada em tal lugar).</p>')
        + numbered_card(4, 'file-text', 'Celular',
            '<p style="margin:0;">Número de celular ativo.</p>')
        + alert_box(
            'Com a documentação em mãos é só entrar no <strong>Portal do Empreendedor</strong> e clicar em <strong>Formalize-se</strong> para efetuar o cadastro. Após isso, será gerado um login de acesso e uma senha para acessar o portal e solicitar serviços como guias de pagamento de impostos, obrigações fiscais e cancelamento do MEI.',
            'Próximo passo')
        + f'<p style="font-size:12px;color:{MUTED};margin:24px 0 0;text-align:center;">Fonte: <a href="https://blog.vhsys.com.br/como-abrir-mei/" target="_blank" rel="noopener" style="color:{MUTED};">blog.vhsys.com.br/como-abrir-mei</a></p>'
        + cta('Hora de colocar a mão na massa: vamos fazer a atividade do MEI.', '7-atividade-mei')
        + section_close()
    )
    return body

def aula_1132_atividade_mei():
    return wrap(
        hero('Empreendedorismo · Atividade', 'Mão na massa: MEI', 'Depois de todas as dicas recebidas, queremos saber: você já possui MEI? Se não, chegou a hora de dar o primeiro passo.')
        + section_open()
        + f'<p style="font-size:18px;text-align:center;color:{PRIMARY_DARK};font-weight:600;margin:0 0 28px;">Vamos nessa?</p>'
        + section_heading('Passo 1 — Assista ao vídeo do SEBRAE')
        + link_card('Vídeo SEBRAE — Como abrir um MEI', 'https://www.youtube.com/watch?v=wMUS4gGklgY', 'Dicas práticas para começar', icon='play-circle')
        + section_heading('Passo 2 — Acesse e cadastre-se')
        + link_card('Portal do Governo — Registrar como MEI', 'https://www.gov.br/pt-br/servicos/realizar-registro-como-microempreendedor-individual-mei', 'Cadastro oficial gratuito', icon='external-link')
        + alert_box('Reserve cerca de 30 minutos. Tenha em mãos seu CPF, título de eleitor (ou recibo do IRPF) e celular ativo. O processo é rápido e simples.', 'Tempo estimado', color='red')
        + cta('Avance para conteúdos complementares e aprofunde os temas do módulo.', 'conteudo-complementar-2')
        + section_close()
    )

def aula_1133_complementar():
    return wrap(
        hero('Empreendedorismo · Complementar', 'Conteúdo complementar', 'Materiais selecionados para você se aprofundar nos temas deste módulo.')
        + section_open('Leituras recomendadas')
        + link_card('Entenda o motivo do sucesso e do fracasso das empresas',
                    'https://www.sebrae.com.br/sites/PortalSebrae/ufs/sp/bis/entenda-o-motivo-do-sucesso-e-do-fracasso-das-empresas,b1d31ebfe6f5f510VgnVCM1000004c00210aRCRD',
                    'SEBRAE-SP', icon='file-text')
        + link_card('4 erros que impedem sua empresa de crescer',
                    'https://administradores.com.br/noticias/4-erros-que-impedem-sua-empresa-de-crescer',
                    'Portal Administradores', icon='file-text')
        + link_card('Controle financeiro empresarial: o que é, importância e dicas',
                    'https://elevesuasvendas.com.br/blog/financeiro/controle-financeiro-empresarial',
                    'Eleve Suas Vendas', icon='file-text')
        + cta('Pronto para encerrar este módulo e seguir adiante?', 'mensagem-final-8', 'Mensagem final')
        + section_close()
    )

def aula_1134_mensagem_final():
    return wrap(
        hero('Empreendedorismo · Encerramento', 'Você chegou ao fim do módulo!',
             'Parabéns por concluir o primeiro grande passo da sua trilha. Agora vamos para o próximo módulo: <strong style="color:#fff;">Plano de Negócios</strong>.')
        + section_open()
        + f'''<table role="presentation" cellpadding="0" cellspacing="0" border="0" style="width:100%;background:linear-gradient(135deg,{PRIMARY_LIGHT_BG} 0%,#fff 100%);border:2px solid {PRIMARY_LIGHT_BORDER};border-radius:12px;margin:0 0 24px;">
  <tr>
    <td style="padding:40px 32px;text-align:center;">
      <div style="background:{PRIMARY};width:88px;height:88px;border-radius:50%;display:inline-block;line-height:88px;margin-bottom:20px;">{svg('award', 48)}</div>
      <p style="font-size:20px;font-weight:700;color:{PRIMARY_DARK};margin:0 0 12px;">O empreendedorismo é uma jornada</p>
      <p style="font-size:16px;line-height:1.55;color:{TEXT};margin:0;max-width:480px;display:inline-block;">Você acabou de fortalecer a base. No próximo módulo, vamos transformar essa base em um plano concreto para o seu negócio.</p>
    </td>
  </tr>
</table>'''
        + cta('Vamos começar o módulo de Plano de Negócios?', 'video-introdutorio-3', 'Próximo módulo')
        + section_close()
    )

# ==== Pipeline ================================================================
LESSONS = {
    1127: ('2. Vender mais', aula_1127_vender_mais),
    1128: ('3. Lucrar', aula_1128_lucrar),
    1129: ('4. Expandir sua empresa', aula_1129_expandir),
    1130: ('5. Fatos relevantes', aula_1130_fatos),
    1131: ('6. Como legalizar', aula_1131_legalizar),
    1132: ('7. Atividade MEI', aula_1132_atividade_mei),
    1133: ('Conteúdo complementar', aula_1133_complementar),
    1134: ('Mensagem final', aula_1134_mensagem_final),
}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--publish', action='store_true', help='Publish to Tutor LMS API')
    parser.add_argument('--verify', action='store_true', help='Only verify')
    parser.add_argument('--lesson', type=int, help='Single lesson ID')
    args = parser.parse_args()

    out_dir = ROOT / 'output' / 'negocio-cultural' / 'reformuladas'
    out_dir.mkdir(parents=True, exist_ok=True)

    target = [args.lesson] if args.lesson else list(LESSONS.keys())

    for lid in target:
        title, fn = LESSONS[lid]
        html = fn()
        path = out_dir / f'aula-{lid}-{title.replace(" ", "-").replace(".", "").lower()}.html'
        path.write_text(html, encoding='utf-8')
        print(f'[GEN] {lid} {title} ({len(html)} chars) -> {path.name}')
        if args.publish:
            r = _tutor_request(f'tutor/v1/lessons/{lid}', method='POST', data={'lesson_content': html})
            print(f'  [PUB] {r.get("message","?")}')

    if args.verify or args.publish:
        print('\n=== VERIFICATION ===')
        r = _tutor_request('tutor/v1/course-contents/1123')
        data = r['data'] if isinstance(r, dict) and 'data' in r else r
        for t in data:
            for c in t.get('contents', []):
                if c.get('ID') in target:
                    ct = c.get('post_content','')
                    has_3c5a76 = '#3c5a76' in ct
                    has_data_sheets = 'data-sheets-' in ct
                    print(f'  {c["ID"]:>5} | {c["post_title"][:40]:40} | len={len(ct):>6} | palette OK={has_3c5a76} | clean={not has_data_sheets}')

if __name__ == '__main__':
    main()
