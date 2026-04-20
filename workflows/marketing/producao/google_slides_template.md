# Workflow: Google Slides Template

## Objetivo
Criar templates editáveis no Google Slides com placeholders nomeados para a equipe (ou cliente) preencher com dados variáveis (cidade, data, trilha, nome do participante, código e-certificado, etc.). Exportar PNG de exemplo preenchido para validação. Entregar o link do Slides na pasta Drive do projeto.

## Quando Executar
- Convite por cidade (feed, WhatsApp, story)
- Card de inscrição com QR
- Certificado digital (trilha inicial, profissionalizante)
- Qualquer peça que vai ser preenchida N vezes com dados diferentes

## Inputs Necessários

| Input | Fonte | Obrigatório |
|---|---|---|
| Tipo de peça | `convite-cidade` · `card-qr` · `certificado-a5` · `custom` | Sim |
| Dimensões do slide (em px ou mm) | Brief da peça | Sim |
| Paleta (hex) | KV do projeto (pasta Drive) | Sim |
| Tipografia (Google Fonts name) | KV do projeto | Sim |
| Logos (PNG/SVG) | Drive do projeto | Sim |
| Placeholders | Lista `{CIDADE}`, `{DATA}`, `{TRILHA}` etc. com limite de caracteres | Sim |
| Conteúdo fixo | Headlines, subheads, textos não editáveis | Sim |
| Exemplo preenchido | Valores de exemplo (ex: "Santa Rita Durão", "15 de maio de 2026") | Sim |
| Pasta Drive destino | Folder ID onde salvar | Sim |
| Nome do arquivo | String (LETRAS MAIÚSCULAS COM ESPAÇO) | Sim |

## Passo a Passo

### Fase 1 — Coleta
Perguntar ao usuário:
1. Tipo de peça?
2. Dimensões (px ou mm)?
3. Onde está o KV do projeto (pasta Drive)?
4. Quais placeholders? (nome + limite caracteres + exemplo)
5. Qual pasta destino?
6. Nome do arquivo (padrão MAIÚSCULAS)?

### Fase 2 — Preparação
1. Baixar logos/ícones do KV (via MCP Drive).
2. Validar paleta hex → converter para RGB para Slides API.
3. Montar JSON de config:
```json
{
  "type": "convite-cidade",
  "size": { "width_px": 1080, "height_px": 1350 },
  "palette": {
    "primary": "#003A70",
    "accent": "#F5A623",
    "dark": "#001F3F",
    "light": "#FFFFFF"
  },
  "font_family": "Montserrat",
  "logos": {
    "soberana": "path/to/logo_estacao_samarco.png",
    "realizacao": "path/to/logo_ntics.png"
  },
  "placeholders": [
    { "name": "CIDADE", "max_chars": 25, "example": "Santa Rita Durão" },
    { "name": "DATA", "max_chars": 30, "example": "A partir de 15 de maio de 2026" }
  ],
  "fixed_content": {
    "headline": "Estação Samarco em {CIDADE}",
    "subhead": "Inscrições abertas"
  },
  "drive_folder_id": "1wDNy7rve_uK-cBZa3aP529q9GHtL0cf6",
  "file_name": "CONVITE POST CIDADE"
}
```

### Fase 3 — Execução
```bash
python tools/gws/slides_template_create.py --config .tmp/slides_config.json
```

O tool:
1. Autentica via OAuth (reusa `tools/gws/auth.py`).
2. Cria apresentação nova via Slides API.
3. Ajusta tamanho do slide para as dimensões pedidas.
4. Aplica paleta e tipografia.
5. Insere logos nas posições corretas.
6. Cria os placeholders como text boxes com `{CAMPO}` e estilo visual do campo.
7. Preenche uma cópia (segundo slide) com os valores de exemplo e exporta como PNG.
8. Move a apresentação para a pasta Drive do projeto.
9. Retorna: `slides_url`, `png_preview_path`, `file_id`.

### Fase 4 — Verificação e entrega
1. Confirmar que o Slides abriu na pasta destino (MCP Drive `get_file_metadata`).
2. Validar PNG de preview (resolução, cores, legibilidade).
3. Reportar ao usuário:
   - Link do Google Slides (clicável)
   - Caminho do PNG de preview
   - Lista dos placeholders que aparecem no arquivo
4. Se integrado com ClickUp: postar comentário na subtask com os 2 links.

## Output Esperado
- 1 Google Slides editável na pasta Drive do projeto, com placeholders `{CAMPO}` funcionais
- 1 PNG preview exportado (exemplo preenchido) — 300 dpi
- Link do Slides + caminho do PNG reportados

## Tool Utilizado
`tools/gws/slides_template_create.py`

## Integração com outras skills
- Usa `/design-briefing` como gate antes de criar (confirmar cores/fontes)
- Pode ser chamada pelo `/time-design` em produção em lote
- Após criar, pode chamar `/verificar` para confirmar o arquivo está acessível na pasta

## Regras NTICS
- Nome do arquivo em **LETRAS MAIÚSCULAS COM ESPAÇO** (ex: `CONVITE POST CIDADE`, não `convite-post-cidade`)
- Usar tipografia do KV do projeto (Open Sans/Montserrat é o padrão Samarco)
- Placeholders em caixa alta entre chaves: `{CIDADE}`, não `[CIDADE]`
- Sempre escrever **inteligência artificial** por extenso (não usar sigla "IA") em qualquer texto fixo
