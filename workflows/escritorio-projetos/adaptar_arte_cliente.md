# Workflow: Adaptar Arte com Identidade Visual do Cliente

## Objetivo
Adaptar materiais visuais (artes de projeto) com a identidade visual do patrocinador/cliente — trocando cores, posicionando logo e substituindo fontes — e exportar PDF vetorial para impressão e/ou SVG para uso digital.

## Quando Executar
Após aprovação do Termo de Abertura, quando o projeto tiver materiais gráficos que precisam receber a marca do patrocinador.

## Inputs Necessários
| Input | Fonte | Obrigatório |
|-------|-------|-------------|
| Arquivo de arte base (.ai, .eps, .svg, .pdf) | Drive do projeto | Sim |
| Logo do cliente (vetor .ai, .eps, .svg) | Cliente/patrocinador | Sim |
| Cores do cliente (CMYK) | Manual de marca do cliente | Sim |
| Fontes do cliente | Manual de marca do cliente | Não |
| Formato de saída (PDF e/ou SVG) | Agente pergunta | Sim |

## Regras Críticas
- **Nunca sobrescrever o arquivo original** — sempre exportar para `.tmp/adapted/`
- Cores devem ser informadas em CMYK (C, M, Y, K — valores de 0 a 100)
- Se o manual de marca do cliente não estiver disponível, perguntar as cores diretamente
- O Illustrator precisa estar instalado no PC (execução via COM/scripting)

## Passo a Passo

### Fase 1 — Coleta de informações
Perguntar ao usuário:
1. Qual arquivo de arte? (caminho completo)
2. Qual o logo do cliente? (caminho do arquivo vetor)
3. Quais cores trocar? (formato: CMYK original → CMYK do cliente)
4. Quais fontes trocar? (opcional)
5. Onde posicionar o logo? (top-left, top-right, bottom-left, bottom-right, center)
6. Formato de saída: PDF, SVG ou ambos?
7. Nome do cliente (para nomear os arquivos)

### Fase 2 — Preparação
1. Validar que todos os arquivos existem
2. Criar diretório de saída: `.tmp/adapted/{nome_cliente}/`
3. Montar config JSON ou usar flags inline

### Fase 3 — Execução
Executar o tool:

**Via config JSON:**
```bash
python tools/adapt_artwork_illustrator.py \
  --artwork "caminho/arte.ai" \
  --config .tmp/adapt_config.json \
  --output-dir .tmp/adapted/cliente
```

**Via flags inline:**
```bash
python tools/adapt_artwork_illustrator.py \
  --artwork "caminho/arte.ai" \
  --client-name "Empresa X" \
  --colors "64,0,69,33>100,50,0,0" "100,17,0,55>0,80,95,0" \
  --logo "caminho/logo_cliente.ai" \
  --logo-position top-right \
  --fonts "Montserrat-Bold>HelveticaNeue-Bold" \
  --output-dir .tmp/adapted/empresa_x \
  --export pdf svg
```

### Fase 4 — Verificação e entrega
1. Ler o resultado (manifest.json) do tool
2. Reportar ao usuário:
   - Quantas cores foram trocadas
   - Se o logo foi posicionado
   - Quantas fontes foram alteradas
   - Caminho dos arquivos gerados
3. Se houver warnings (fonte não instalada, etc.), informar
4. Perguntar se deseja ajustes

## Output Esperado
- PDF vetorial (PDF/X-4, CMYK, com sangria de 3mm, marcas de corte) — pronto para gráfica
- SVG (fontes em outlines, imagens embeddadas) — pronto para digital

## Tool Utilizado
`tools/adapt_artwork_illustrator.py` → `tools/jsx/adapt_artwork.jsx`

## Checklist de Qualidade
- [ ] Cores do cliente aplicadas (nenhuma cor original restante nas áreas mapeadas)
- [ ] Logo do cliente posicionado corretamente
- [ ] PDF exportado em PDF/X-4 com bleed
- [ ] SVG com fontes convertidas em outlines
- [ ] Arquivo original NÃO foi sobrescrito
- [ ] Manifest.json gerado com status de sucesso

## Erros Comuns
| Erro | Causa | Solução |
|------|-------|---------|
| COM dispatch falha | Illustrator não instalado ou licença expirada | Verificar instalação |
| Timeout na conexão | Illustrator demorando para abrir | Aumentar --timeout para 120 |
| Fonte não encontrada | Fonte do cliente não instalada no PC | Instalar a fonte ou converter em outlines |
| Cor não substituída | Tolerância CMYK muito baixa | Aumentar --color-tolerance para 10 |
| Logo não posicionado | Layer "Logo" não existe no arquivo | Usar --logo-layer com nome correto |
| Arquivo já aberto | Arte aberta em outra sessão do Illustrator | O script reutiliza o documento aberto |
