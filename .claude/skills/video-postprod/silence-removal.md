# Skill: Silence Removal (FFmpeg)

Remove pausas/silêncio excessivo de vídeos. Mantém pausas de 0.3s para naturalidade.

## Quando usar
- Vídeos de depoimentos com muitas pausas
- Talking-head videos antes de publicar
- Qualquer clip com silêncio indesejado

## Comando FFmpeg

```bash
# Detectar silêncio (lista timestamps)
ffmpeg -i INPUT.mp4 -af silencedetect=noise=-30dB:d=0.5 -f null - 2>&1 | grep "silence_"

# Remover silêncio (via filtro)
# Passo 1: Detectar e gerar segmentos de não-silêncio
ffmpeg -i INPUT.mp4 -af silencedetect=noise=-30dB:d=0.5 -f null - 2>&1 | \
  grep "silence_end" | \
  awk '{print $5 - 0.3, $5}' > segments.txt

# Passo 2: Cortar e concatenar segmentos (manter 0.3s de pausa)
# O agente deve gerar os comandos de corte baseado nos timestamps
```

## Parâmetros ajustáveis

| Parâmetro | Default | Descrição |
|-----------|---------|-----------|
| `noise` | `-30dB` | Threshold de silêncio (mais negativo = mais sensível) |
| `d` | `0.5` | Duração mínima para considerar silêncio (segundos) |
| `pausa_natural` | `0.3` | Pausa mantida entre cortes para naturalidade |

## Dicas
- Para ambientes barulhentos, use `-25dB`
- Para estúdio limpo, use `-35dB`
- Sempre revise o resultado — cortes automáticos podem cortar respirações/ênfases
- Usar transport stream (.ts) para concatenação sem re-encode
