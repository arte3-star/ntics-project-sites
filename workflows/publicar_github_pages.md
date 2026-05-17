# Workflow: Publicar HTML no GitHub Pages

## Objetivo

Publicar qualquer arquivo HTML gerado em `output/` no repositório `arte3-star/ntics-project-sites` e obter a URL pública compartilhável.

## Quando Executar

Sempre que um HTML for gerado e precisar ser compartilhado (briefings, relatorios, landing pages de projeto). Este workflow faz parte do passo final de qualquer producao HTML.

## Fluxo Padrao

```
Gerar HTML em output/  -->  publish_html.py  -->  GitHub Pages  -->  URL compartilhavel
```

### Passo 1 - Gerar o HTML

O HTML deve estar salvo em `output/{area}/{tipo}/{data}/index.html`.

Exemplos de caminhos:
- `output/marketing/briefings-videomaker/2026-05-04/index.html`
- `output/relatorios/pmo-diario/2026-05-04.html`

### Passo 2 - Publicar

Rodar o comando (o destino no GitHub Pages e derivado automaticamente do caminho `output/`):

```bash
python tools/publish/publish_html.py --src output/marketing/briefings-videomaker/2026-05-04/index.html
```

O script:
1. Atualiza o clone local de `arte3-star/ntics-project-sites`
2. Copia o HTML para a pasta equivalente dentro do repo
3. Faz commit + push
4. Retorna a URL publica

### Passo 3 - Compartilhar a URL

A URL segue a estrutura:
```
https://arte3-star.github.io/ntics-project-sites/{caminho-sem-output}/
```

Exemplos:
- `output/marketing/briefings-videomaker/2026-05-04/index.html`
  -> `https://arte3-star.github.io/ntics-project-sites/marketing/briefings-videomaker/2026-05-04/`

GitHub Pages leva ~1-2 minutos para propagar apos o push.

## Regras

- O HTML gerado NUNCA deve conter links hardcoded para o proprio GitHub Pages
- Arquivos nomeados `index.html` geram URL limpa (sem o nome do arquivo)
- Outros arquivos (ex: `relatorio.html`) geram URL com o nome: `.../relatorio.html`
- Se o arquivo ja foi publicado e nao mudou, o script detecta e nao faz novo commit

## Dest Explicito (quando necessario)

Se o destino automatico nao for adequado, usar `--dest`:

```bash
python tools/publish/publish_html.py \
  --src output/marketing/briefings-videomaker/2026-05-04/index.html \
  --dest briefings/videomaker/2026-05-04
```

## Integracao com outros workflows

Workflows que geram HTML devem incluir este passo no seu Output Esperado:

```
Apos gerar o HTML em output/, rodar:
  python tools/publish/publish_html.py --src {caminho-do-html}
URL retornada e o link compartilhavel.
```

Workflows que ja incluem este passo:
- `/briefing-video` (briefing de captacao videomaker)
- Relatorio PMO (em avaliacao)

## Requisitos

- `gh` CLI autenticado (`gh auth login`)
- `git` configurado com nome e e-mail
- Acesso ao repositorio `arte3-star/ntics-project-sites`
