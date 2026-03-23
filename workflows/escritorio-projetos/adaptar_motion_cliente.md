# Workflow: Adaptar Motion Graphics com Dados do Cliente

## Objetivo
Adaptar templates de motion graphics (.aep) com os dados do projeto/cliente — textos, logos, imagens, cores — e renderizar o vídeo final automaticamente via After Effects.

## Quando Executar
Quando o projeto tiver template de vídeo/motion que precisa ser personalizado com a marca do patrocinador ou dados específicos do projeto.

## Inputs Necessários
| Input | Fonte | Obrigatório |
|-------|-------|-------------|
| Projeto template (.aep) | Drive do projeto | Sim |
| Textos para substituir (nome, patrocinador, datas) | Termo de Abertura / usuário | Sim |
| Logo do cliente (PNG/AI/EPS) | Cliente/patrocinador | Não |
| Imagens/vídeos de substituição | Drive do projeto | Não |
| Cores do cliente (RGB) | Manual de marca | Não |
| Formato de saída (MP4, MOV, etc.) | Agente pergunta | Sim |

## Regras Críticas
- **Nunca sobrescrever o projeto original** — usar `--save-as` para salvar cópia adaptada
- Textos são identificados pelo **nome da layer** no After Effects (ex: "Titulo", "Patrocinador")
- O usuário precisa informar os nomes das layers ou o agente deve listar as layers do template primeiro
- Cores são em RGB (0-255), diferente do Illustrator que usa CMYK

## Passo a Passo

### Fase 1 — Coleta de informações
Perguntar ao usuário:
1. Qual o projeto .aep template? (caminho completo)
2. Qual composição usar? (nome da comp, ou usar a principal)
3. Quais textos trocar? (nome da layer → novo texto)
4. Quais imagens/logos substituir? (nome da layer/item → novo arquivo)
5. Quais cores trocar? (RGB original → RGB do cliente)
6. Formato de saída: MP4, MOV, GIF?
7. Nome do cliente (para nomear os arquivos)

### Fase 2 — Preparação
1. Validar que o projeto .aep existe
2. Validar que os arquivos de footage/logo existem
3. Criar diretório de saída: `.tmp/rendered/{nome_cliente}/`
4. Montar config JSON ou usar flags inline

### Fase 3 — Execução

**Modo 1: Adaptar + Renderizar (completo)**
```bash
python tools/adapt_motion_aftereffects.py \
  --project "C:/projetos/template.aep" \
  --comp "Main Comp" \
  --texts "Titulo>Projeto Statkraft" "Patrocinador>Statkraft Energias" "Data>Março 2026" \
  --footage "Logo>C:/logos/statkraft.png" \
  --colors "255,0,0>0,100,200" \
  --output .tmp/rendered/statkraft/video.mp4 \
  --save-as .tmp/rendered/statkraft/projeto_adaptado.aep
```

**Modo 2: Adaptar sem renderizar (só preparar)**
```bash
python tools/adapt_motion_aftereffects.py \
  --project "C:/projetos/template.aep" \
  --config .tmp/motion_config.json \
  --no-render \
  --save-as .tmp/rendered/projeto_adaptado.aep
```

**Modo 3: Só renderizar (sem alterar)**
```bash
python tools/adapt_motion_aftereffects.py \
  --project "C:/projetos/projeto.aep" \
  --comp "Final" \
  --output .tmp/rendered/video.mp4 \
  --render-only
```

**Modo 4: Renderizar com aerender (mais rápido, sem GUI)**
```bash
python tools/adapt_motion_aftereffects.py \
  --project "C:/projetos/template.aep" \
  --config .tmp/motion_config.json \
  --output .tmp/rendered/video.mp4 \
  --use-aerender
```

### Fase 4 — Verificação e entrega
1. Ler o resultado (manifest.json)
2. Reportar ao usuário:
   - Quantos textos foram trocados
   - Quantos footages substituídos
   - Quantas cores alteradas
   - Se o render foi concluído
   - Caminho do vídeo final
3. Se houver warnings, informar
4. Perguntar se deseja ajustes

## Config JSON Completo (referência)
```json
{
  "comp_name": "Main Comp",
  "text_map": [
    {"layer_name": "Titulo", "new_text": "Projeto X", "font": "Arial-Bold", "font_size": 48},
    {"find": "EMPRESA", "replace": "Statkraft"}
  ],
  "footage_map": [
    {"layer_name": "Logo", "new_file": "C:/logos/logo.png"},
    {"item_name": "background.jpg", "new_file": "C:/imgs/bg.jpg"}
  ],
  "color_map": [
    {"from_rgb": [255, 0, 0], "to_rgb": [0, 100, 200]}
  ],
  "color_tolerance": 0.05,
  "render": {
    "output_path": "C:/output/video.mp4",
    "output_template": "H.264 - Match Render Settings - 15 Mbps",
    "render_template": "Best Settings"
  },
  "save_as": "C:/projetos/projeto_adaptado.aep"
}
```

## Output Esperado
- Vídeo renderizado (MP4/MOV) pronto para uso
- Projeto .aep adaptado (cópia, original intocado)
- manifest.json com detalhes da operação

## Tools Utilizados
- `tools/adapt_motion_aftereffects.py` → `tools/jsx/adapt_motion.jsx`
- `aerender.exe` (render headless)

## Checklist de Qualidade
- [ ] Textos do cliente visíveis e corretos no vídeo
- [ ] Logo do cliente posicionado corretamente
- [ ] Cores adaptadas para a paleta do cliente
- [ ] Vídeo renderizado sem artefatos
- [ ] Projeto original NÃO foi sobrescrito
- [ ] Manifest.json gerado com status de sucesso

## Erros Comuns
| Erro | Causa | Solução |
|------|-------|---------|
| COM dispatch falha | After Effects não instalado | Verificar instalação |
| Timeout na conexão | AE demora para abrir (projeto pesado) | Aumentar --timeout para 120+ |
| Layer não encontrada | Nome da layer diferente do esperado | Listar layers do template primeiro |
| Footage missing | Arquivo de substituição não existe | Validar caminhos antes de executar |
| Render falha | Output Module template não existe | Usar template padrão ou verificar nome |
| aerender error | Codec não disponível | Verificar Media Encoder instalado |
