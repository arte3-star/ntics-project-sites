# Skill: Burn Subtitles (FFmpeg)

Queima legendas word-by-word sobre o vídeo. Usa arquivo SRT gerado pelo TTS
ou pelo Whisper.

## Quando usar
- Vídeos para Instagram/TikTok (maioria assiste sem som)
- Depoimentos com narração
- Qualquer vídeo com fala que vai para redes sociais

## Comando básico

```bash
# Legendas simples (brancas, centralizadas embaixo)
ffmpeg -i INPUT.mp4 \
  -vf "subtitles=LEGENDAS.srt:force_style='FontSize=24,FontName=Arial,PrimaryColour=&HFFFFFF,OutlineColour=&H000000,Outline=2,Alignment=2,MarginV=60'" \
  -c:a copy \
  OUTPUT.mp4
```

## Estilos prontos

### Estilo 1: Clean (fundo escuro, texto branco)
```
force_style='FontSize=22,FontName=Arial,PrimaryColour=&HFFFFFF,BackColour=&H80000000,BorderStyle=4,Outline=0,Shadow=0,MarginV=50,Alignment=2'
```

### Estilo 2: Bold (outline forte, impactante)
```
force_style='FontSize=26,FontName=Arial Bold,PrimaryColour=&HFFFFFF,OutlineColour=&H000000,Outline=3,Shadow=2,MarginV=50,Alignment=2'
```

### Estilo 3: Destaque (palavra atual em amarelo)
Requer SRT com marcação word-level (gerado pelo Edge TTS ou Whisper).

## Gerar SRT a partir de vídeo

```bash
# Via Whisper (se já tem audio.wav)
# O tool analyze_frames.py com --transcribe gera transcription.txt
# Converter para SRT:
python -c "
from faster_whisper import WhisperModel
model = WhisperModel('base', device='cpu', compute_type='int8')
segs, _ = model.transcribe('audio.wav', language='pt', word_timestamps=True)
# ... gerar SRT com timestamps word-level
"
```

## Posicionamento por formato

| Formato | MarginV | Alignment | Posição |
|---------|---------|-----------|---------|
| 9:16 (Reels) | 80 | 2 (centro-baixo) | Terço inferior |
| 16:9 (YouTube) | 40 | 2 | Embaixo |
| 1:1 (Feed) | 60 | 2 | Embaixo |

## Dicas
- Para 9:16, FontSize entre 22-28 (mais que isso fica muito grande)
- Sempre usar Outline ≥ 2 para legibilidade sobre qualquer fundo
- Testar em celular antes de publicar (o que parece bom no desktop pode ser pequeno no mobile)
- Edge TTS gera SRT com word boundaries automaticamente
- Legendas word-by-word (karaokê) performam melhor em Reels/TikTok
