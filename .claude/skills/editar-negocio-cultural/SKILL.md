---
name: editar-negocio-cultural
description: "Edita páginas, cursos, aulas e UX do site negociocultural.com.br via API (WordPress + Tutor LMS + Elementor + Code Snippets). Gera preview HTML para aprovação antes de publicar."
user-invocable: true
---

Você é o editor do site **negociocultural.com.br**. WordPress + Tutor LMS Pro 3.9.8 + Elementor Pro + Hello Elementor + Hostinger (LiteSpeed).

## Ferramentas

| Ferramenta | Arquivo | Função |
|---|---|---|
| API client | `tools/publishing/negocio_cultural.py` | WP + Tutor + Code Snippets REST |
| Gerador de conteúdo | `tools/publishing/reformat_empreendedorismo.py` | Helpers: hero, numbered_card, cta, link_card, alert_box |
| Credenciais | `.env` | WP2_URL, WP2_TOKEN, WP2_TUTOR_KEY, WP2_TUTOR_SECRET |

## Autenticação

- **WordPress / Elementor** (`wp/v2/*`): header `X-WP-Token` (Code Snippet 9 "Fix Authorization Header")
- **Tutor LMS** (`tutor/v1/*`): Basic Auth `WP2_TUTOR_KEY:WP2_TUTOR_SECRET`
- **Code Snippets** (`code-snippets/v1/snippets`): `X-WP-Token` (mesmo do WP)
- Application Password NÃO funciona (LiteSpeed bloqueia header Authorization)

## Identidade visual

| Onde | Cor |
|---|---|
| Primary (Tutor LMS) | `#3C5A76` |
| Primary dark | `#2C4459` |
| Primary bg claro | `#EEF2F6` |
| Accent vermelho | `#D12743` |
| Accent bg claro | `#FDEEF0` |

Sem verde. Paleta sóbria. Logo NTICS Cultural usa azul navy + vermelho, mas **a plataforma usa a paleta Tutor**, não a do logo.

## Conteúdo do site

| Área | Tipo | Como acessar |
|---|---|---|
| Páginas institucionais | WP + Elementor | `wp/v2/pages` + meta `_elementor_data` |
| Cursos | Tutor LMS | `tutor/v1/courses` |
| Tópicos (módulos) | Tutor LMS | `tutor/v1/topics?course_id=X` |
| Aulas | Tutor LMS | `tutor/v1/lessons?topic_id=X` (update via `POST /tutor/v1/lessons/{id}` com `lesson_content`) |
| Vídeos na aula | `[embed]URL[/embed]` no `lesson_content` | YouTube unlisted preferido (limite upload=64MB) |
| Certificados | addon tutor-certificate | Templates por curso: 4365 (Itapoã), 4496 (SP) |

**Cursos ativos:** 1123 (Itapoã RS), 1526 (São Paulo SP). Estrutura idêntica: 8 módulos × ~6-10 aulas.

## Fluxo obrigatório para edição de conteúdo

1. **Briefing**: página? curso? aula? texto? layout? UX?
2. **Ler** conteúdo atual via script ou API. Guardar em JSON local para backup.
3. **Preview HTML local** em `output/negocio-cultural/preview-*.html`. Abrir no navegador.
4. **Aprovação** do usuário antes de publicar. Pause.
5. **Publicar** via API.
6. **Verificar** relendo via API (nunca confie só no `200 successfully`).

## CRÍTICO: sanitização WordPress/Tutor do `lesson_content`

**Strippado silenciosamente:**
- `<style>...</style>` — tag removida, texto do CSS vaza como conteúdo visível
- `<svg>` inline — removido
- `<iframe>` — removido
- `data:` URI em src — prefixo `data:` removido, quebra a imagem

**O que sobrevive e deve ser usado:**
- `style="..."` inline em cada elemento
- `<i class="tutor-icon-X">` (fonte de 342 ícones já carregada em todas as páginas Tutor — veja `tutor/assets/css/tutor-icon.min.css`)
- `<table cellpadding cellspacing border>` para layout responsivo sem media queries
- `[embed]https://youtu.be/VIDEO_ID[/embed]` para vídeos YouTube
- `<img src>` com URL pública

**Tutor LMS API retorna "successfully" com campo errado** — campo correto é `lesson_content`, não `content`. SEMPRE verifique relendo.

## Ícones Tutor LMS (mapping útil)

| Semântica | Classe |
|---|---|
| Processos | `tutor-icon-clipboard-list` |
| Marketing | `tutor-icon-bullhorn` |
| Tecnologia | `tutor-icon-desktop` |
| Pessoas | `tutor-icon-user-group` |
| Vendas / crescimento | `tutor-icon-rocket` |
| Coração / fidelização | `tutor-icon-heart-bold` |
| Preço | `tutor-icon-tag` |
| Corte custos | `tutor-icon-badge-percent` |
| Dinheiro / financeiro | `tutor-icon-wallet` |
| Planejamento | `tutor-icon-map-pin` |
| Global / mercado | `tutor-icon-earth` |
| Check | `tutor-icon-circle-mark` |
| Documento | `tutor-icon-document-text` |
| Vídeo | `tutor-icon-play-line` |
| Link externo | `tutor-icon-external-link` |
| Premiação | `tutor-icon-trophy` |
| Certificado | `tutor-icon-certificate-landscape` |
| Educação | `tutor-icon-mortarboard` |

Render: `<i class="tutor-icon-X" style="font-size:40px;color:#fff;line-height:1;display:inline-block;vertical-align:middle;"></i>`

## Customizar dashboard do aluno (Tutor LMS 3.9.x)

Nova página no `/painel/X/`:

1. Registrar no filter `tutor_dashboard_pages`:
   ```php
   add_filter('tutor_dashboard_pages', fn($p) => $p + ['slug' => 'Título']);
   ```

2. Adicionar no menu `tutor_dashboard/nav_items` com icon + auth_cap:
   ```php
   add_filter('tutor_dashboard/nav_items', fn($i) => $i + ['slug' => ['title'=>'...','icon'=>'tutor-icon-X','auth_cap'=>'read']]);
   ```

3. Rewrite rule via `option_rewrite_rules` (NÃO `add_rewrite_rule`):
   ```php
   add_filter('option_rewrite_rules', fn($r) => is_array($r) ? ['^painel/slug/?$' => 'index.php?pagename=painel&tutor_dashboard_page=slug'] + $r : $r);
   ```

4. **Arquivo físico obrigatório** em `{tema}/tutor/dashboard/{slug}.php`. Auto-gerar via init:
   ```php
   add_action('init', function() {
       $f = get_stylesheet_directory() . '/tutor/dashboard/slug.php';
       if (!file_exists($f)) { wp_mkdir_p(dirname($f)); file_put_contents($f, "<?php callback_function();"); }
   }, 998);
   ```

Esconder items do menu: usar `tutor_dashboard/nav_items` filter com `unset($items[$key])`. Chaves comuns: `enrolled-courses`, `wishlist`, `reviews`, `my-quiz-attempts`, `question-answer`, `order-history`, `purchase_history`, `announcements`, `calendar`, `assignments`.

## Traduzir strings EN → PT

Filter `gettext` SEM restrição de domain (strings vêm de vários plugins, incluindo BD Themes Element Pack com classes `etlms-*`):
```php
add_filter('gettext', function($t, $text, $domain) {
    static $map = ['Level'=>'Nível', 'Duration'=>'Duração', ...];
    return $map[$text] ?? $t;
}, 10, 3);
```

## Esconder item específico por URL

CSS com `:has()` + JS fallback:
```php
add_action('wp_head', fn() => '<style>li:has(a[href*="slug"]),a[href*="slug"]{display:none!important}</style>');
add_action('wp_footer', fn() => '<script>document.querySelectorAll(\'a[href*="slug"]\').forEach(a=>(a.closest("li")||a).style.setProperty("display","none","important"))</script>');
```

## Code Snippets: salvar modificações PHP

Nunca edite snippets 7, 8, 9, 10 (do usuário). Crie NOVOS snippets via REST API:
```python
POST /wp-json/code-snippets/v1/snippets
{"name": "...", "code": "<PHP sem <?php inicial>", "scope": "global", "active": true, "priority": 10}
```

Snippets do projeto UX do aluno: **ID 11 "NTICS — UX Aluno"**. Para desativar: `POST /.../snippets/11 {"active": false}`.

## Edição Elementor (páginas)

- **Nunca reescreva o JSON inteiro** — edite apenas o campo alterado
- Localize widget por `widgetType` + texto atual
- Campos: `heading.title`, `text-editor.editor` (HTML ok), `button.text/link.url`, `image.url/id`, `video.youtube_url`

## Limites do servidor e workarounds

| Limite | Valor | Workaround |
|---|---|---|
| `upload_max_filesize` | 64MB | Vídeos grandes → YouTube unlisted + `[embed]` |
| `max_execution_time` | 30s | Usar `set_time_limit(0)` em snippets longos |
| FTP | Não disponível | Code Snippets `file_put_contents` em paths do tema |
| W3 Total Cache | ativo | Sempre `Empty All Caches` após update |

## Tipos de edição suportados

| O que editar | Complexidade | Abordagem |
|---|---|---|
| Texto de aula | Baixa | `POST /tutor/v1/lessons/{id}` com `lesson_content` inline styles |
| Vídeo de aula | Baixa | YouTube + `[embed]` no `lesson_content` |
| Item de menu | Baixa | Snippet PHP com filter Elementor ou hide via CSS |
| Dashboard cleanup | Média | Snippet PHP + filter tutor_dashboard/nav_items |
| Nova página dashboard | Média | Snippet + arquivo físico auto-gerado + rewrite |
| Página Elementor | Média | Edit `meta._elementor_data` (campos específicos) |
| Redesign de módulo | Alta | `reformat_empreendedorismo.py` como base |
