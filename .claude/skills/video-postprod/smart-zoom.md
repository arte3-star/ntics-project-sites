# Skill: Smart Zoom (FFmpeg)

Aplica zoom inteligente em vídeos talking-head. Zoom suave em momentos de ênfase.

## Quando usar
- Talking-head videos para dar dinamismo
- Depoimentos longos que precisam de variação visual
- Destaque de momentos-chave

## Níveis de zoom

| Tipo | Zoom | Quando usar |
|------|------|-------------|
| Normal | 1.0x (sem zoom) | Conteúdo regular, contexto |
| Ênfase | 1.25x | Pontos importantes, dados, nomes |
| Crítico | 1.6x | Momento emocional, frase-chave, CTA |

## Comando FFmpeg

```bash
# Zoom estático 1.25x centralizado no rosto
ffmpeg -i INPUT.mp4 \
  -vf "scale=2*iw:-1,crop=iw/1.25:ih/1.25" \
  -c:a copy \
  OUTPUT.mp4

# Zoom animado (Ken Burns) — de 1.0x para 1.25x em 3 segundos
ffmpeg -i INPUT.mp4 \
  -vf "zoompan=z='min(zoom+0.0015,1.25)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=90:s=1920x1080:fps=30" \
  -c:a copy \
  OUTPUT.mp4

# Zoom em trecho específico (0:15 a 0:25)
ffmpeg -i INPUT.mp4 \
  -vf "crop=in_w/1.25:in_h/1.25:(in_w-in_w/1.25)/2:(in_h-in_h/1.25)/2:enable='between(t,15,25)'" \
  -c:a copy \
  OUTPUT.mp4
```

## Workflow recomendado
1. O agente analisa a transcrição e identifica momentos de ênfase
2. Gera lista de timestamps com nível de zoom para cada trecho
3. Aplica zoom via FFmpeg filtergraph
4. **Humano revisa** — zoom automático pode cortar o rosto

## Dicas
- Sempre centralizar no rosto (usar detecção facial se possível)
- Transições de zoom devem durar 0.3-0.5s para parecer natural
- Não usar zoom > 1.6x — perde qualidade
- Testar em resolução alta (1080p+) para manter nitidez após crop
