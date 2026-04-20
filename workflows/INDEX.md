# Workflows Index

## Escritório de Projetos (`workflows/escritorio-projetos/`)

SOPs de planejamento, estruturação e gestão de projetos NTICS.

| Workflow | Arquivo | Quando usar |
|----------|---------|-------------|
| Termo de Abertura | `termo_abertura.md` | Novo projeto precisa de estruturação formal (TA) |
| Perfil Estratégico | `perfil_estrategico.md` | Analisar empresa antes de proposta/TA |
| Plano de Divulgação | `plano_divulgacao.md` | Criar comunicação + releases (requer TA + PEP) |
| Roteiro Edição Vídeo | `roteiro_edicao_video.md` | Criar script de vídeo pré-projeto (legado) |
| Roteiro Vídeo Completo | `roteiro_video_completo.md` | Roteiro de vídeo para 5 tipos: pré/durante/case/venda1/venda2 |
| Briefing Website | `briefing_website.md` | Montar conteúdo para site do projeto |
| Engenhoca Prestação Contas | `engenhoca_prestacao_contas.md` | Automação de prestação de contas Rouanet |
| Processamento de Reuniões | `process_meeting_transcript.md` | Transcrição → classificação → tasks no ClickUp |
| Criar Site do Projeto | `criar_site_projeto.md` | Site institucional no Lovable (briefing ClickUp + assets Drive + GitHub + Jinja2/Tailwind) |
| Form de Indicadores | `form_indicadores_projeto.md` | Gera Google Form de coleta de indicadores a partir da seção 6 do TAP (KPIs NTICS + Quantitativos + Específicos + ODS) |
| Email Calendário Social | `email_calendario_social.md` | Gera email para o cliente com calendário de postagens (carrosséis/reels/case) a partir de TAP + Plano + Releases + tasks ClickUp |
| **KV Derivar Projeto** | `kv_derivar_projeto.md` | `/kv-derivar` — gera KV do projeto a partir do manual do cliente + biblioteca de 12 ícones via Leonardo AI |
| **Arte Impressão CMYK** | `arte_impressao_cmyk.md` | `/arte-impressao-cmyk` — gera .AI + .PDF CMYK + .PNG para rollup, pantojet, wind banner, saia bancada, placa fotos, moldura espelho |
| **Estampa Têxtil** | `estampa_textil.md` | `/estampa-textil` — gera arte para avental, dolma, camiseta, jaleco, capa corte cabelo com cores Pantone e mockup visual |

**Cadeia de dependências típica:**
```
Perfil Patrocinador ──┐
                      ├──> Termo de Abertura ──> Plano Divulgação ──> /briefing-video (Roteiro + Carrossel)
                      │                                              └──> Briefing Website ──> Criar Site (Lovable)
```

## Inscrição de Projetos (`workflows/inscricao-projetos/`)

SOPs para estruturação e submissão de projetos a leis de incentivo.

| Workflow | Arquivo | Quando usar |
|----------|---------|-------------|
| Estruturador Lei Rouanet | `estruturador_rouanet.md` | Estruturar projeto para inscrição MinC |
| Conselheiro SALIC | `conselheiro_salic.md` | Preencher campos SALIC campo-a-campo |
| Conselheiro Lei Reciclagem | `conselheiro_reciclagem.md` | Execução/diligências/PC Lei Reciclagem |

## Marketing (`workflows/marketing/`)

Organizado em 4 subpastas: `producao/`, `producao/carrosseis/`, `agentes/`, `referencia/`.

### Produção (`producao/`)

| Workflow | Arquivo | Comando | Quando usar |
|----------|---------|---------|-------------|
| Plano Mensal | `producao/plano_mensal.md` | `/plano-mensal` | Planejamento editorial do mês (arco ABT + hooks) + tasks ClickUp |
| Roteiro Vídeo | `producao/roteiro_video.md` | `/roteiro-video` | Script de 1 min para NotebookLM |
| Artigo Mensal | `producao/artigo_mensal.md` | `/artigo-mensal` | Compila 4 roteiros em artigo integrado |
| Newsletter | `producao/newsletter.md` | `/newsletter` | HTML completo + draft Gmail ou Brevo (semanal ou mensal) |
| Artigo Site (mensal) | `producao/artigo_site.md` | `/artigo-site` | Corpo HTML do artigo mensal para ntics.com.br |
| Artigo Notícias Site | `producao/artigo_noticias_site.md` | — | Fase 5 do carrossel de notícias: artigo semanal aprofundando as 7 notícias ESG |
| Vetorizar | `producao/vetorizar_imagem.md` | — | Raster → vetor via Illustrator |
| Post Instagram | `producao/posts/post-instagram.md` | `/post-instagram` | Capa 4:5 para post único feed Instagram (Leonardo + image_reference, padrão case) |
| **Google Slides Template** | `producao/google_slides_template.md` | `/google-slides-template` | Template Google Slides editável com placeholders `{CIDADE}`, `{TRILHA}`, `{DATA}` (convite cidade, card QR, certificado) |
| **Revisão Arte Impressão** | `revisao/revisao_arte_impressao.md` | `/revisao-arte-impressao` | Auditoria técnica PDF/AI antes da gráfica: CMYK, DPI, sangria, fontes, logo hierarquia |

### Carrosseis (`producao/carrosseis/`) — 4 Tipos

| Tipo | Arquivo | Comando | Identidade | Quando usar |
|------|---------|---------|------------|-------------|
| Notícias ESG | `carrossel_noticias.md` | `/carrossel-noticias` | NTICS | 8 cards ESG news (Perplexity + Leonardo) — semanal |
| Educativo ESG | `carrossel_educativo.md` | `/carrossel-educativo` | NTICS | 8 cards educativos (Pillow + capa Leonardo) — semanal |
| Case Projeto | `carrossel_case_projeto.md` | `/carrossel-case` | NTICS | 8 cards case pós-projeto (Leonardo + image_reference) |
| Projeto Ativo Cliente | `carrossel_projeto_ativo_cliente.md` | `/carrossel-cliente` | **DO CLIENTE** | 8 cards com identidade do patrocinador (pré/durante/pós) |
| Briefing Carrossel+Vídeo | `briefing_carrossel_video.md` | `/briefing-video` | DO CLIENTE | Companion: briefing carrossel + roteiro vídeo |

### Agentes Autônomos (`agentes/`)

| Agente | Arquivo | Trigger | O que faz |
|--------|---------|---------|-----------|
| Criador Semanal | `agente_criador_semanal.md` | Domingo 20h | Produz 4 peças semanais (educativo + notícias + vídeo + case) |
| Revisor Semanal | `agente_revisor_semanal.md` | Segunda 8h | Revisa qualidade das peças produzidas |
| Ajustes Tempo Real | `agente_ajustes_tempo_real.md` | Comentário ClickUp | Corrige conteúdo quando Lucas comenta |
| Publicador | `agente_publicador.md` | Status "aprovado" no ClickUp (webhook n8n) | Publica no LinkedIn (auto) + notifica Instagram manual, muda status para "publicado" |

### Referência (`referencia/`)

| Doc | Arquivo | Propósito |
|-----|---------|-----------|
| **Leonardo AI Core** | `leonardo_ai_core.md` | Referência rápida: modos, endpoints, payload mínimo, dimensões, checklist visual (porta de entrada) |
| **Leonardo AI Cookbook** | `leonardo_ai_cookbook.md` | Detalhes, erros conhecidos, exemplos completos, FAQ (consulta sob demanda) |
| LinkedIn Strategy | `linkedin_strategy.md` | Pilares, formatos, tom e cadência |
| Uso de Squads | `uso_squads_marketing.md` | Como rotear para os 10 squads |
| Time Mídias Sociais | `team_midias_sociais.md` | Agent Team (lead + writer + publisher) |
| Time Design Conteúdo | `team_design_conteudo.md` | Agent Team de design visual |

**Cadeia editorial típica:**
```
/plano-mensal (gera plano + cria tasks ClickUp)
  ├→ Agente criador semanal (domingo 20h, automático)
  │   ├→ /carrossel-educativo (segunda)
  │   ├→ Perplexity pesquisa 7 notícias ESG
  │   │   ├→ artigo_noticias_site (publica PRIMEIRO no site)
  │   │   └→ /carrossel-noticias (publica DEPOIS, com link pro artigo) (terça)
  │   ├→ /roteiro-video (quarta)
  │   └→ /carrossel-case (quinta)
  │
  ├→ Lucas aprova via ClickUp (muda status para "aprovado")
  │   ├→ Agente ajustes em tempo real (se necessário antes de aprovar)
  │   └→ Lucas agenda manualmente no Instagram + LinkedIn
  │       (captions prontas nos campos customizados da task)
  │
  └→ /artigo-mensal (fim do mês)
       ├→ /artigo-site (corpo HTML para ntics.com.br)
       └→ /newsletter (consolida tudo + Gmail draft)
/carrossel-cliente (por projeto ativo — pré/durante/pós)
```

**Knowledge files** (referência compartilhada): `workflows/knowledge/`

## APIs de Conteúdo

APIs usadas pelos workflows de marketing (chaves em `.env`):

| API | Uso | Variável |
|-----|-----|----------|
| Leonardo AI | Geração de imagens (nano-banana-2, 4:5 Instagram) | `LEONARDO_API_KEY` |
| Perplexity | Busca de notícias ESG/CSR (sonar, filtro semanal) | `PERPLEXITY_API_KEY` |
| Unsplash | Imagens stock (fallback) | `UNSPLASH_API_KEY` |
| Gmail | Criação de drafts de newsletter (via MCP) | Google OAuth |
| Brevo | Campanhas de email marketing (newsletter em massa) | `BREVO_API_KEY` |
| Serper | Busca de imagens reais via Google Images (newsletter) | `SERPER_API_KEY` |
