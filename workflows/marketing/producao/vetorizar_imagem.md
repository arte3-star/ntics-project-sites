# Workflow: Vetorizar Imagens (Leonardo AI → Illustrator)

## Objetivo
Converter imagens raster (geradas pelo Leonardo AI ou qualquer outra fonte) em vetores editáveis usando o Image Trace do Adobe Illustrator, exportando em SVG, AI, EPS ou PDF vetorial.

## Quando Executar
- Após gerar imagens no Leonardo AI que precisam ser vetorizadas
- Quando o projeto precisa de artes em formato vetorial para impressão, recorte ou aplicação em materiais
- Para converter logos, ícones ou ilustrações de raster para vetor

## Inputs Necessários
| Input | Fonte | Obrigatório |
|-------|-------|-------------|
| Imagem(ns) raster (PNG, JPG, TIFF, PSD, BMP) | Leonardo AI / Drive / usuário | Sim |
| Preset de vetorização | Agente sugere conforme tipo | Não (default: High Fidelity Photo) |
| Formato(s) de saída | Agente pergunta | Não (default: SVG) |

## Guia de Presets

Escolha o preset baseado no tipo de imagem:

| Tipo de imagem | Preset recomendado | Resultado |
|----------------|-------------------|-----------|
| **Foto do Leonardo AI** | High Fidelity Photo | Máxima fidelidade, muitas cores |
| **Ilustração colorida** | 16 Colors ou 6 Colors | Paleta reduzida, limpo |
| **Logo simples** | Black and White Logo | P&B, contornos nítidos |
| **Logo colorido** | 3 Colors ou 6 Colors | Poucas cores, bordas limpas |
| **Ícone/silhueta** | Silhouettes | Formas sólidas |
| **Desenho a traço** | Line Art | Só contornos |
| **Sketch/rascunho** | Sketched Art | Preserva estilo sketch |
| **Arte estilizada** | Low Fidelity Photo | Menos detalhes, mais artístico |
| **Desenho técnico** | Technical Drawing | Linhas precisas |

## Passo a Passo

### Fase 1 — Identificar imagens
Perguntar ao usuário:
1. Qual(is) imagem(ns)? (caminho ou pasta)
2. Qual o tipo de imagem? (foto, logo, ícone, ilustração)
3. Qual formato de saída? (SVG, AI, EPS, PDF, ou vários)
4. Precisa ignorar fundo branco? (--ignore-white)

### Fase 2 — Executar vetorização

**Imagem única:**
```bash
python tools/media/vectorize_image_illustrator.py \
  --images .tmp/images/logo_leonardo.png \
  --preset "High Fidelity Photo" \
  --formats svg ai \
  --output-dir .tmp/vectorized
```

**Batch (pasta inteira):**
```bash
python tools/media/vectorize_image_illustrator.py \
  --input-dir .tmp/images/2026-03-20 \
  --preset "16 Colors" \
  --formats svg \
  --output-dir .tmp/vectorized
```

**Logo com fundo branco:**
```bash
python tools/media/vectorize_image_illustrator.py \
  --images .tmp/images/logo.png \
  --preset "Black and White Logo" \
  --ignore-white \
  --formats svg eps pdf \
  --output-dir .tmp/vectorized
```

**Listar presets disponíveis:**
```bash
python tools/media/vectorize_image_illustrator.py --list-presets
```

### Fase 3 — Pipeline Leonardo AI → Vetor

Para o fluxo completo de geração + vetorização:

```bash
# 1. Gerar imagem no Leonardo AI
python tools/media/generate_images_leonardo.py \
  --prompt "Logo minimalista de sustentabilidade" \
  --output-dir .tmp/images

# 2. Vetorizar o resultado
python tools/media/vectorize_image_illustrator.py \
  --input-dir .tmp/images \
  --preset "6 Colors" \
  --ignore-white \
  --formats svg ai \
  --output-dir .tmp/vectorized
```

### Fase 4 — Entrega
1. Verificar resultado (manifest.json)
2. Informar arquivos gerados e presets usados
3. Perguntar se quer ajustar (outro preset, mais/menos cores, ignorar branco)

## Output Esperado
- Arquivo(s) vetorial(is) (SVG, AI, EPS e/ou PDF) no diretório de saída
- Manifest.json com detalhes da operação

## Tool Utilizado
`tools/media/vectorize_image_illustrator.py` → `tools/adobe/jsx/vectorize_image.jsx`

## Checklist de Qualidade
- [ ] Imagem vetorizada sem perda significativa de detalhes
- [ ] Formato de saída correto (SVG/AI/EPS/PDF)
- [ ] Fundo branco removido (se solicitado)
- [ ] Arquivo editável (paths, não imagem embutida)
- [ ] Manifest.json gerado com status de sucesso

## Erros Comuns
| Erro | Causa | Solução |
|------|-------|---------|
| Vetor muito pesado (MB) | Preset "High Fidelity" em foto complexa | Usar "Low Fidelity" ou "16 Colors" |
| Bordas serrilhadas | Imagem fonte de baixa resolução | Usar imagem 1024px+ do Leonardo |
| Cores estranhas | Preset inadequado para o tipo de imagem | Trocar preset (ver tabela acima) |
| Fundo branco incluso | Esqueceu --ignore-white | Rodar novamente com --ignore-white |
| Muitos paths | Foto muito detalhada | Usar preset com menos cores ou Low Fidelity |
