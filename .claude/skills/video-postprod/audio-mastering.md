# Skill: Audio Mastering (FFmpeg)

Masteriza áudio de vídeo para padrão broadcast. Highpass, EQ de presença,
compressão e normalização de loudness.

## Quando usar
- Qualquer vídeo antes de publicar
- Depoimentos gravados com microfone de celular
- Vídeos com volume inconsistente
- Antes de adicionar trilha sonora

## Pipeline de áudio (ordem importa)

```bash
ffmpeg -i INPUT.mp4 \
  -af "highpass=f=80, \
       equalizer=f=3000:t=q:w=1.5:g=3, \
       acompressor=threshold=-20dB:ratio=4:attack=5:release=50, \
       loudnorm=I=-16:TP=-1.5:LRA=11" \
  -c:v copy \
  OUTPUT.mp4
```

## Explicação de cada filtro

| Filtro | O que faz | Parâmetros |
|--------|-----------|------------|
| `highpass=f=80` | Remove rumble/grave indesejado | f=80Hz (corta tudo abaixo) |
| `equalizer=f=3000:g=3` | Boost de presença vocal | 3kHz +3dB (clareza da voz) |
| `acompressor` | Compressão dinâmica | -20dB threshold, ratio 4:1 |
| `loudnorm` | Normalização loudness | -16 LUFS (padrão YouTube/Instagram) |

## Padrões de loudness por plataforma

| Plataforma | LUFS | TP (True Peak) |
|-----------|------|----------------|
| YouTube | -14 | -1.0 dB |
| Instagram/TikTok | -16 | -1.5 dB |
| Podcast | -16 | -1.0 dB |
| Broadcast TV | -24 | -2.0 dB |

## Para adicionar trilha de fundo

```bash
# Trilha a -17dB (audível sem cobrir a voz)
ffmpeg -i INPUT.mp4 -i TRILHA.mp3 \
  -filter_complex "[1:a]volume=-17dB[bg];[0:a][bg]amix=inputs=2:duration=first[aout]" \
  -map 0:v -map "[aout]" \
  -c:v copy -c:a aac -b:a 192k \
  OUTPUT.mp4
```

## Dicas
- Sempre comparar antes/depois ouvindo com fones
- Se a voz ficar "metálica", reduza o EQ de presença (g=2 ou g=1)
- Para ambientes muito ruidosos, adicione `anlmdn` (denoiser) antes do highpass
- Loudnorm funciona melhor em two-pass (mede primeiro, aplica depois)
