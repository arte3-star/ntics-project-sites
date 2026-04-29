# Tools — Registro de Scripts

Todos os scripts Python determinísticos da NTICS, organizados por função.

> 📚 **Leonardo AI:** Os scripts em `media/` e `content-gen/` que usam Leonardo AI têm sua lógica validada. Se surgir erro, dúvida sobre payload ou resultado visual inesperado, consulte `workflows/marketing/referencia/leonardo_ai_core.md` — base de conhecimento complementar com modos, erros conhecidos e exemplos por caso de uso.

## Estrutura

```
tools/
├── content-gen/    # Geração de carrosséis, cards e conteúdo visual
├── media/          # Geração e busca de imagens (Leonardo AI, Unsplash, PDF)
├── adobe/          # Automação Adobe Illustrator, After Effects e JSX
├── integrations/   # Conectores externos (ClickUp, Drive, Gmail, Pipedrive, Sembly)
├── research/       # Pesquisa de dados (Perplexity, CSR news, SALIC)
├── publishing/     # Newsletter, sites institucionais (NTICS) e Negócio Cultural (_nc_*)
├── migration/      # Pipeline Lovable → ntics.com.br (build → photos → refine → upload)
├── reports/        # Relatórios PMO diário e semanal (ClickUp → HTML → Gmail)
├── sync/           # Sincronização ClickUp/Drive ↔ projects/*/state.yaml
├── meetings/       # Processamento de reuniões e atas
├── video/          # remotion-video (Node.js) + video_analysis (Python)
└── _tests/         # Scripts experimentais e de teste
```

---

## content-gen/

| Script | Workflow(s) | APIs | Status |
|---|---|---|---|
| gerar_carrossel_noticias_v2.py | [carrossel_noticias.md](../workflows/marketing/producao/carrosseis/carrossel_noticias.md), [agente_criador_semanal.md](../workflows/marketing/agentes/agente_criador_semanal.md) | Leonardo AI, Perplexity, Serper | Ativo |
| gerar_carrossel_educativo.py | [carrossel_educativo.md](../workflows/marketing/producao/carrosseis/carrossel_educativo.md) | Leonardo AI, Pillow (só logo CTA) | Ativo |
| gerar_carrosseis_3semanas.py | [agente_criador_semanal.md](../workflows/marketing/agentes/agente_criador_semanal.md) | Leonardo AI | Ativo |
| gerar_educativos_3semanas.py | [agente_criador_semanal.md](../workflows/marketing/agentes/agente_criador_semanal.md) | Leonardo AI | Ativo |
| gerar_artigo_site.py | [artigo_site.md](../workflows/marketing/producao/artigo_site.md) | Leonardo AI | Ativo |
| gerar_textos_pdf_carrossel.py | [carrossel_case_projeto.md](../workflows/marketing/producao/carrosseis/carrossel_case_projeto.md) | fpdf2 | Ativo |
| selecao_fotos.py | — | Google Drive | Utilitário |
| gamma_create.py | [gamma_api.md](../workflows/marketing/referencia/gamma_api.md) | Gamma API v1.0 | Ativo |
| capa_video_pie.py | [capa_video.md](../workflows/marketing/producao/videos/capa_video.md) | Leonardo AI, Pillow | Por-projeto (PIE) |
| capa_video_culinaria125.py | [capa_video.md](../workflows/marketing/producao/videos/capa_video.md) | Leonardo AI, Pillow | Por-projeto (Samarco Culinária 125) |
| capa_video_negocio_cultural_120.py | [capa_video.md](../workflows/marketing/producao/videos/capa_video.md) | Leonardo AI, Pillow | Por-projeto (Negócio Cultural 120) |
| carrossel_pie_v2.py | [carrossel_projeto_ativo_cliente.md](../workflows/marketing/producao/carrosseis/carrossel_projeto_ativo_cliente.md) | Leonardo AI | Por-projeto (PIE) — `_v1` deprecated |
| carrossel_negocio_cultural_120.py | [carrossel_projeto_ativo_cliente.md](../workflows/marketing/producao/carrosseis/carrossel_projeto_ativo_cliente.md) | Leonardo AI | Por-projeto (Negócio Cultural) |
| carrossel_quem_somos.py | — | Pillow | One-shot institucional |
| stories_v21_pipeline.py / stories_v21_leonardo.py | — | Leonardo AI | Stories — pipeline + gerador (v21 ativo, v4v5 legacy) |
| story3_compose.py / story3_html.py / story3_leonardo.py | — | Leonardo AI, Pillow | Story 3-card pipeline |
| _crop_logos_120.py | — | Pillow | Utilitário (one-shot, recorte logos) |

---

## media/

| Script | Workflow(s) | APIs | Status |
|---|---|---|---|
| generate_images_leonardo.py | Vários carrosséis | Leonardo AI | Ativo |
| generate_icons_leonardo.py | [kv_derivar_projeto.md](../workflows/escritorio-projetos/kv_derivar_projeto.md) | Leonardo AI (flux/lightning/phoenix) | **Ativo** — gera biblioteca de ícones flat/linear/gradient coerente |
| fetch_images_unsplash.py | [carrossel_noticias.md](../workflows/marketing/producao/carrosseis/carrossel_noticias.md) | Unsplash | Fallback |
| fetch_images_google.py | [carrossel_noticias.md](../workflows/marketing/producao/carrosseis/carrossel_noticias.md) | Google Custom Search JSON API | Ativo |
| vectorize_image_illustrator.py | [vetorizar.md](../workflows/marketing/producao/vetorizar_imagem.md) | Adobe Illustrator | Ativo |
| extract_pdf_comments.py | [aplicar_revisao_pdf_illustrator.md](../workflows/escritorio-projetos/aplicar_revisao_pdf_illustrator.md) | PyMuPDF | Ativo |

---

## adobe/

| Script | Workflow(s) | Runtime | Status |
|---|---|---|---|
| adapt_artwork_illustrator.py | [adaptar-arte/SKILL.md](../.claude/skills/adaptar-arte/SKILL.md) | Adobe Illustrator | Ativo |
| adapt_motion_aftereffects.py | [motion-projeto/SKILL.md](../.claude/skills/motion-projeto/SKILL.md) | Adobe After Effects | Ativo |
| apply_text_edits_illustrator.py | [aplicar_revisao_pdf_illustrator.md](../workflows/escritorio-projetos/aplicar_revisao_pdf_illustrator.md) | Adobe Illustrator | Ativo |
| arte_impressao.py | [arte_impressao_cmyk.md](../workflows/escritorio-projetos/arte_impressao_cmyk.md) | Adobe Illustrator | **Stub** — assinatura pronta, pipeline COM+JSX a implementar |
| kv_derivar.py | [kv_derivar_projeto.md](../workflows/escritorio-projetos/kv_derivar_projeto.md) | Illustrator + Leonardo AI | **Stub** — orquestração pronta, funções a implementar |
| estampa_textil.py | [estampa_textil.md](../workflows/escritorio-projetos/estampa_textil.md) | Adobe Illustrator | **Stub** — validação de legibilidade pronta, geração JSX a implementar |
| revisao_arte_pdf.py | [revisao_arte_impressao.md](../workflows/marketing/revisao/revisao_arte_impressao.md) | PyMuPDF (fitz) | **Stub** — esqueleto de checks pronto, validações específicas a completar |
| jsx/adapt_artwork.jsx | Invocado por adapt_artwork_illustrator.py | Illustrator | Ativo |
| jsx/adapt_motion.jsx | Invocado por adapt_motion_aftereffects.py | After Effects | Ativo |
| jsx/apply_text_edits.jsx | Invocado por apply_text_edits_illustrator.py | Illustrator | Ativo |
| jsx/vectorize_image.jsx | Invocado por vectorize_image_illustrator.py | Illustrator | Ativo |
| jsx/read_document_colors.jsx | Utilitário de leitura de cores | Illustrator | Utilitário |
| jsx/arte_impressao.jsx | (a criar) invocado por arte_impressao.py | Illustrator | **Pendente** |
| jsx/kv_logo_projeto.jsx | (a criar) invocado por kv_derivar.py | Illustrator | **Pendente** |
| jsx/estampa_textil.jsx | (a criar) invocado por estampa_textil.py | Illustrator | **Pendente** |

---

## integrations/

| Script | Workflow(s) | APIs | Status |
|---|---|---|---|
| create_clickup_tasks.py | [process_meeting_transcript.md](../workflows/escritorio-projetos/process_meeting_transcript.md), vários | ClickUp API | Ativo |
| create_social_media_tasks.py | [agente_criador_semanal.md](../workflows/marketing/agentes/agente_criador_semanal.md) | ClickUp API | Ativo |
| update_clickup_drive_links.py | [agente_criador_semanal.md](../workflows/marketing/agentes/agente_criador_semanal.md) | ClickUp, Google Drive | Ativo |
| upload_to_drive.py | Vários workflows de output | Google Drive API | Ativo |
| publicar_drive.py | [publicar_drive.md](../workflows/marketing/publicar_drive.md) | Google Drive API | Ativo |
| drive_2026_discover.py | [publicar_drive.md](../workflows/marketing/publicar_drive.md) | Google Drive API | Ativo |
| drive_2026_scaffold.py | [publicar_drive.md](../workflows/marketing/publicar_drive.md) | Google Drive API | Ativo |
| drive_2026_reorg.py | [publicar_drive.md](../workflows/marketing/publicar_drive.md) | Google Drive API | One-shot (executado 2026-04-23) |
| drive_import_designer_assets.py | — | Google Drive API | Ativo — baixa peças gráficas de projetos ativos p/ `assets/projetos/*/identidade-visual/` |
| read_google_doc.py | Vários | Google Docs API | Ativo |
| update_learning_registry.py | — | Google Sheets | Ativo |
| create_pipedrive_note.py | [process_meeting_transcript.md](../workflows/escritorio-projetos/process_meeting_transcript.md), [sembly_to_pipedrive.md](../workflows/escritorio-projetos/sembly_to_pipedrive.md) | Pipedrive API | Ativo — aceita `--deal-id` para pular lookup |
| pipedrive_match_deal.py | [sembly_to_pipedrive.md](../workflows/escritorio-projetos/sembly_to_pipedrive.md) | Pipedrive API | Ativo — match deal por email do participante (fallback domínio da org) |
| sembly_pull_meetings.py | [sembly_to_pipedrive.md](../workflows/escritorio-projetos/sembly_to_pipedrive.md) | Sembly API v1 | Ativo — list/detail/transcript de meetings |
| sembly_to_pipedrive.py | [sembly_to_pipedrive.md](../workflows/escritorio-projetos/sembly_to_pipedrive.md) | Sembly + Pipedrive + Anthropic | Ativo — orquestrador, scheduled 4x/dia |
| clickup_pull_projetos_ntics.py | [relatorio_diario_pmo.md](../workflows/escritorio-projetos/relatorio_diario_pmo.md) | ClickUp API | Ativo — pull pasta Projetos Ativos |
| clickup_pull_sprint.py | [relatorio_diario_pmo.md](../workflows/escritorio-projetos/relatorio_diario_pmo.md) | ClickUp API | Ativo — pull lista Sprint da semana |
| clickup_pull_overdue_comments.py | [relatorio_diario_pmo.md](../workflows/escritorio-projetos/relatorio_diario_pmo.md) | ClickUp API | Ativo — comentários em tasks atrasadas |
| clickup_remove_list_dependencies.py | — | ClickUp API | Utilitário |
| drive_find_cronograma.py | [criar_site_projeto.md](../workflows/escritorio-projetos/criar_site_projeto.md) | Google Drive API | Ativo — busca planilha de cronograma do projeto |
| parse_cronograma.py | [criar_site_projeto.md](../workflows/escritorio-projetos/criar_site_projeto.md) | openpyxl | Ativo — extrai datas/marcos do XLSX |
| update_lps_2026.py | [criar_landing_ntics.md](../workflows/marketing/referencia/criar_landing_ntics.md) | WordPress (Code Snippets) | Ativo — atualização em massa de LPs 2026 |
| webhook_server.py | n8n integrations | HTTP | Ativo |
| gws/forms_create.py | [form_indicadores_projeto.md](../workflows/escritorio-projetos/form_indicadores_projeto.md) | Google Forms API v1 | Ativo |
| gws/gws_cli.py | Vários (Gmail/Calendar/Drive CLI) | Google Workspace APIs | Ativo |
| gws/slides_template_create.py | [google_slides_template.md](../workflows/marketing/producao/google_slides_template.md) | Google Slides + Drive API | **Stub** — criação da presentation pronta, placeholders/cores/logos/preview a completar |

---

## research/

| Script | Workflow(s) | APIs | Status |
|---|---|---|---|
| search_perplexity.py | [carrossel_noticias.md](../workflows/marketing/producao/carrosseis/carrossel_noticias.md) | Perplexity API | Ativo |
| research_csr_news.py | [carrossel_noticias.md](../workflows/marketing/producao/carrosseis/carrossel_noticias.md) | Perplexity API | Ativo |
| parse_salic_excel.py | [conselheiro_salic.md](../workflows/inscricao-projetos/conselheiro_salic.md) | — (local) | Ativo |

---

## publishing/

| Script | Workflow(s) | APIs | Status |
|---|---|---|---|
| build_newsletter.py | [newsletter.md](../workflows/marketing/producao/newsletter.md) | Jinja2 | Ativo |
| send_newsletter.py | [newsletter.md](../workflows/marketing/producao/newsletter.md) | Gmail API | Ativo |
| publish_to_brevo.py | [newsletter.md](../workflows/marketing/producao/newsletter.md) | Brevo API (sib-api-v3-sdk) | Ativo |
| generate_project_site.py | [criar_site_projeto.md](../workflows/escritorio-projetos/criar_site_projeto.md) | Jinja2, Lovable | Ativo |
| templates/newsletter.html | build_newsletter.py | — | Template |
| templates/newsletter-corporate.html | build_newsletter.py | — | Template alternativo (corporate) |
| templates/project_site.html | generate_project_site.py | — | Template |

### Negócio Cultural — automação WordPress/Tutor LMS (`_nc_*.py`)

Suite de scripts dedicados ao site `negociocultural.com.br` (WordPress + Tutor LMS + Elementor + Code Snippets API). Naming convention: prefixo `_nc_` indica scripts deste cliente. Workflow base: skill `editar-negocio-cultural`.

| Script | Propósito | Status |
|---|---|---|
| _nc_inspect_home.py / _nc_inspect_itapoa.py / _nc_inspect_subpages.py | Inspeção de páginas via Chrome CDP | Ativo |
| _nc_audit_chrome.py | Auditoria UX automatizada | Ativo |
| _nc_create_remaining.py / _nc_create_statkraft_pages.py | Criação em massa de páginas/cidades | Ativo |
| _nc_duplicate_trilha.py / _nc_duplicate_lessons_only.py | Clonagem de trilha+aulas para nova cidade | Ativo |
| _nc_edicoes_add_sp.py / _nc_edicoes_add_sp_v2.py | Adição de São Paulo às edições | One-shot |
| _nc_elementor_regen.py | Regenerar caches Elementor | Ativo |
| _nc_find_sections.py / _nc_fix_city_headers.py | Manutenção de seções/cabeçalhos | Ativo |
| _nc_flush_caches.py | Limpar caches WP/Elementor após edição | Ativo |
| _nc_footer_trilhas.py / _nc_trim_footer.py / _nc_remove_ctas.py | Ajustes de footer/CTAs | Ativo |
| _nc_publish_drafts.py | Publicar drafts em batch | Ativo |
| _nc_rebuild_home.py | Reconstrução da home | Ativo |
| _nc_test_one_page.py | Sandbox para testar mudanças em 1 página | Ativo |
| _nc_trilha_and_band.py | Banner + trilha por cidade | Ativo |
| _nc_update_form3_cidades.py / _nc_update_form3_via_snippet.py / _nc_update_itapoa.py | Atualização de form/cidades | Ativo |
| _nc_upload_statkraft_assets.py | Upload de assets Statkraft (patrocinador) | One-shot |
| _nc_*.json | Snapshots/mappings de páginas (statkraft_media, statkraft_pages, trilha_mapping, src_trilha_snapshot) | Dados |

---

## migration/

Pipeline de migração de landing pages Lovable → ntics.com.br. Workflow: [criar_landing_ntics.md](../workflows/marketing/referencia/criar_landing_ntics.md).

| Script | Propósito | Status |
|---|---|---|
| lovable_to_ntics.py | Orquestrador principal Lovable → NTICS | Ativo |
| build_site_model.py / build_all_models.py | Constrói modelo da página a partir do scrape | Ativo |
| build_photo_assignment.py | Atribui fotos do banco a cada seção (LAION + Sonnet) | Ativo |
| inject_photos.py | Injeta fotos no template HTML | Ativo |
| editorial_rewrite.py | Reescreve copy em tom NTICS | Ativo |
| refine_sites.py / adjust_sites.py | Ajustes pós-build | Ativo |
| upload_ntics.py / upload_new_sites.py | Upload final via Code Snippets API | Ativo |
| refresh_landing_preprojeto.py | Refresh de landing pré-projeto | Ativo |
| _review_live.py | Auditoria pós-publicação | Utilitário |
| generate_all_final.py | Pipeline end-to-end (build → photos → refine → upload) | Ativo |

---

## reports/

Geradores de relatório PMO automatizados. Workflows: [relatorio_diario_pmo.md](../workflows/escritorio-projetos/relatorio_diario_pmo.md), [relatorio_semanal_pmo.md](../workflows/escritorio-projetos/relatorio_semanal_pmo.md).

| Script | Propósito | Status |
|---|---|---|
| run_pmo_daily.py | Entrypoint diário (cron 8h) — pull → aggregate → render → email | Ativo |
| run_pmo_weekly.py | Entrypoint semanal (sexta 16h) | Ativo |
| aggregate_pmo_metrics.py | Agrega saúde por coordenador, atrasos, marcos, bloqueios | Ativo |
| aggregate_pmo_weekly.py | Agrega janela semanal (entregue na semana / planejado próxima) | Ativo |
| generate_pmo_summary.py / generate_weekly_summary.py | Resumo executivo via Claude Haiku | Ativo |
| render_pmo_html.py / render_pmo_weekly.py | Render Jinja2 → HTML | Ativo |
| send_pmo_email.py | Envio Gmail (Lucas/Bruna/Abilio) | Ativo |
| templates/pmo_diario.html.j2 / pmo_semanal.html.j2 | Templates de email | Template |
| config/pmo_diario.yaml | Config: lista IDs ClickUp, destinatários, thresholds | Config |
| _common.py | Helpers compartilhados | — |

---

## sync/

Sincronização ClickUp/Drive ↔ workspace local `projects/`. Skill: `/projeto-sync`.

| Script | Propósito | Status |
|---|---|---|
| projeto_sync.py | Sync state.yaml ↔ ClickUp + Gmail (cron + SessionStart) | Ativo |
| read_drive_xlsx.py | Lê XLSX do Drive direto (sem download) | Utilitário |
| _form_extract.py / _form_fill_132.py / _form_read_api.py | Extração/preenchimento de formulários (projeto 132 Samarco) | Por-projeto |
| register_cron_windows.ps1 | Registra schedule task Windows para projeto_sync | Setup |

---

## meetings/

| Script | Workflow(s) | APIs | Status |
|---|---|---|---|
| classify_meeting.py | [process_meeting_transcript.md](../workflows/escritorio-projetos/process_meeting_transcript.md) | Claude API | Ativo |

---

## video/

| Módulo | Workflow(s) | Runtime | Status |
|---|---|---|---|
| remotion-video/ | [analise_edicao_video.md](../workflows/escritorio-projetos/analise_edicao_video.md) | Node.js / Remotion | Ativo |
| video_analysis/ | [analise_edicao_video.md](../workflows/escritorio-projetos/analise_edicao_video.md) | Python | Ativo |

---

## _tests/

Scripts experimentais — não invocar em produção.

| Script | Propósito |
|---|---|
| teste_estilo_mindset.py | Teste de estilos de imagem para carrosséis Mindset |
| teste_og_image.py | Teste de geração de Open Graph images |
| teste_perplexity_imagens.py | Teste de busca de imagens via Perplexity |
| teste_unsplash_noticias.py | Teste de busca de imagens Unsplash para notícias |
