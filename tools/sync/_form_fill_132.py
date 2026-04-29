"""Preenche o form Kickoff Patrocinador via Chrome CDP (porta 9222).
Não submete — para no final pra usuário revisar e enviar.
"""
import asyncio
from playwright.async_api import async_playwright

FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLScjvoZC279K_QQns7lZRMBCL6Ov6qF9BdsUceu6cUyg--gAiA/viewform"

# Respostas indexadas pela ordem das itemId no form (mesma ordem visual)
ANSWERS = [
    # 1. Nome da Empresa
    "Samarco Mineracao S.A.",
    # 2. Projetos Patrocinados
    ("Estacao Samarco — Territorios do Futuro. Programa de empregabilidade, empreendedorismo "
     "e capacitacao profissionalizante em 12 comunidades prioritarias (7 em MG: Camargos, "
     "Antonio Pereira, Bento Rodrigues, Paracatu de Baixo, Santa Rita Durao, Brumal e Catas "
     "Altas; 5 no ES: Meaipe, Mae-Ba, Parati, Ubu e Recanto do Sol). Estrutura em tres trilhas "
     "formativas: Trilha Inicial (Empreendedorismo & IA), Estacao Sabores (Culinaria Sustentavel) "
     "e Estacao Beleza & Estetica. Evolucao do Culinaria Sustentavel 2025, agora unificado MG+ES "
     "com certificacao rastreavel."),
    # 3. Relacionamento na cidade
    ("A Samarco mantem relacionamento institucional consolidado nos territorios de atuacao em "
     "Minas Gerais (regiao de Mariana e Catas Altas) e no Espirito Santo (Anchieta e Guarapari). "
     "A articulacao local em ES e coordenada por Roberta (Samarco), responsavel pela abertura "
     "de territorio e mapeamento de instituicoes nas cidades de Meaipe, Mae-Ba, Parati, Ubu e "
     "Recanto do Sol. [VERIFICAR — listagem especifica de Entidade/Contato/Telefone/E-mail por "
     "cidade ainda pendente; Roberta deve consolidar o mapeamento.]"),
    # 4. Ponto focal
    ("Cintia — Gestao do Contrato e mediacao institucional Samarco. Coordena cronograma, "
     "compliance e articulacao MG+ES. [VERIFICAR — incluir e-mail e telefone direto.]"),
    # 5. Visita Tecnica
    ("A antecedencia de 3 meses e adequada e esta alinhada com a experiencia das edicoes "
     "anteriores. Reforcamos a importancia de incluir na VT: (i) confirmacao dos equipamentos "
     "disponiveis em cada local (fornos, bancadas, pias — ja validados em parte por Ricardo "
     "no kickoff de 17/04 quanto ao restaurante interno), (ii) alinhamento previo com as "
     "secretarias municipais e (iii) mapeamento das instituicoes parceiras locais. Sem objecoes "
     "ao prazo proposto."),
    # 6. Assessoria de imprensa
    ("Sim. A comunicacao corporativa Samarco e operada pela TransmeService, equipe ampliada "
     "que atua diretamente com Samarco Comunicacao. Ponto focal: Amanda (Comunicacao "
     "Corporativa). Time: Camila, Josiandra, Ari e Luiz Felipe. [VERIFICAR — telefones e "
     "e-mails da equipe TransmeService.]"),
    # 7. Contato aprovacao materiais
    ("Amanda (Samarco / TransmeService) — Comunicacao Corporativa, aprovacao de pecas e "
     "aplicacao de marca. Aprovacao dupla com Rayane (Comunicacao ES — assume durante ferias "
     "da Amanda). Questoes contratuais escalonadas para Cintia. [VERIFICAR — e-mail e telefone "
     "diretos de Amanda e Rayane.]"),
    # 8. Comunicacao institucional
    ("Todo envio e troca de arquivos do projeto ocorre obrigatoriamente via Microsoft Teams / "
     "SharePoint Samarco (canal corporativo oficial). WhatsApp nao e canal autorizado para "
     "arquivos do projeto. Aprovacao dupla obrigatoria: Amanda (corporativa MG+ES) + Rayane "
     "(ES). Acessos e credenciamento operados por Tatiane (Tatiana Martins Alves) — "
     "Credenciamento/Acessos Samarco."),
    # 9. RADIO — tempo aprovacao pecas
    ("RADIO", "3 dias"),
    # 10. RADIO — tempo aprovacao release
    ("RADIO", "3 dias"),
    # 11. UPLOAD — pular
    ("SKIP_UPLOAD", None),
    # 12. Problema ambiental/social
    ("A Samarco atua em territorios diretamente impactados pelo rompimento da barragem de "
     "Fundao (2015), notadamente Bento Rodrigues, Paracatu de Baixo e Santa Rita Durao. "
     "Pedimos atencao editorial maxima da equipe NTICS nessas comunidades: tom positivo "
     "voltado ao presente e ao futuro, sem revitimizacao e sem linguagem assistencialista "
     "ou triunfalista. O projeto e instrumento de reconstrucao territorial — o foco editorial "
     "deve estar no que cada participante esta construindo agora. [VERIFICAR fraseado com "
     "Cintia/Amanda.]"),
    # 13. Outras infos / voluntariado
    ("A equipe de sensibilizacao Samarco — Thiago, Glenda e Vanessa (Joia) — e responsavel "
     "por captacao de inscricoes e mobilizacao local nos territorios. Inscricoes nao sao "
     "responsabilidade NTICS. [VERIFICAR — informacoes sobre programa de voluntariado "
     "corporativo Samarco, se aplicavel.]"),
    # 14. Sobre a empresa
    "[VERIFICAR — solicitar a Amanda boilerplate corporativo Samarco aprovado para uso em pecas.]",
    # 15. RADIO — voluntariado sim/nao
    ("SKIP_RADIO", None),
    # 16. Se sim, como envolver
    "[Condicional a Q15. Preencher apos definicao sobre voluntariado.]",
]


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp("http://localhost:9222", timeout=15000)
        context = browser.contexts[0]

        # Procura aba do form (caso usuario ja tenha aberto) ou abre nova
        page = None
        for pg in context.pages:
            if "docs.google.com/forms" in pg.url:
                page = pg
                break
        if not page:
            page = await context.new_page()
            await page.goto(FORM_URL, wait_until="domcontentloaded", timeout=60000)

        await page.wait_for_timeout(3000)
        print(f"URL: {page.url}")
        print(f"Title: {await page.title()}")

        # Cada pergunta esta dentro de um div[role="listitem"]
        items = await page.locator('div[role="listitem"]').all()
        print(f"Found {len(items)} list items")

        for idx, ans in enumerate(ANSWERS):
            if idx >= len(items):
                print(f"!! item {idx+1} nao encontrado (apenas {len(items)})")
                break
            item = items[idx]
            try:
                heading = await item.locator('div[role="heading"]').first.inner_text(timeout=2000)
            except Exception:
                heading = "(sem titulo)"
            heading_short = heading[:70].replace("\n", " ")
            print(f"\n[{idx+1}] {heading_short}")

            if isinstance(ans, tuple):
                tag = ans[0]
                if tag == "RADIO":
                    target = ans[1]
                    radios = await item.locator('div[role="radio"]').all()
                    clicked = False
                    for r in radios:
                        label = await r.get_attribute("aria-label") or ""
                        if target.lower() in label.lower():
                            await r.click()
                            print(f"   -> radio: {label}")
                            clicked = True
                            break
                    if not clicked:
                        print(f"   !! radio '{target}' nao achado")
                elif tag == "SKIP_UPLOAD":
                    print("   -> upload (skip — usuario envia logo via SharePoint)")
                elif tag == "SKIP_RADIO":
                    print("   -> radio voluntariado (skip — pendencia aberta)")
                continue

            # Texto: tenta input[type=text] ou textarea
            text_field = item.locator('textarea, input[type="text"]').first
            try:
                await text_field.click(timeout=2000)
                await text_field.fill(ans)
                preview = ans[:60].replace("\n", " ")
                print(f"   -> texto: {preview}...")
            except Exception as e:
                print(f"   !! falhou ao preencher: {e}")

        print("\n=== PREENCHIDO. NAO submetido. Revise e clique 'Enviar' manualmente. ===")


asyncio.run(main())
