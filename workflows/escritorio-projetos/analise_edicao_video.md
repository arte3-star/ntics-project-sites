# Workflow: Análise de Vídeo + Edição Automática com Motion Graphics

## Objetivo
Pipeline completo para: (1) analisar vídeos brutos de eventos/B-roll, (2) catalogar momentos-chave por tags/temas, (3) gerar narração TTS, e (4) montar vídeo temático com cortes + motion graphics via Remotion.

## Quando Executar
- Recebeu vídeos brutos de um evento/projeto e precisa catalogá-los
- Precisa montar um vídeo de 1min sobre um tema específico a partir de footage existente
- Quer reaproveitar footage de múltiplos eventos para conteúdo de marketing

## Setup (primeira vez)

### Dependências do sistema
```bash
# Mac
brew install ffmpeg

# Ubuntu/Debian
sudo apt install ffmpeg

# Verificar
ffmpeg -version && ffprobe -version
```

### Dependências Python
```bash
pip install anthropic ffmpeg-python Pillow faster-whisper edge-tts elevenlabs
```

### Dependências Node.js (Remotion)
```bash
# Windows: usar junction C:\ntics-remotion (path com espaços/acentos quebra npm)
cd /c/ntics-remotion && npm install
# Ou: cd tools/remotion-video && npm install (se path não tem espaços)
```

### Variáveis de ambiente (.env)
```
ANTHROPIC_API_KEY=sk-...      # Obrigatória (análise visual)
ELEVENLABS_API_KEY=...         # Opcional (narração premium)
```

## Inputs Necessários

| Input | Fonte | Obrigatório |
|-------|-------|-------------|
| Pasta com vídeos brutos (.mp4/.mov) | Equipe de produção / Google Drive | Sim |
| Tema do vídeo | Usuário define | Sim (para montagem) |
| Nome do projeto | TA / briefing | Recomendado |
| Nome do patrocinador | TA / briefing | Recomendado |

## Regras Críticas

- **Claude NÃO vê o vídeo** — cada render precisa de revisão humana
- **Manter motion graphics simples** — lower thirds, fades, cartelas. Não tentar animações complexas
- **Nunca re-encode clips fonte** — usar transport stream (.ts) para concatenação
- **Sessões curtas** — context rot é real após ~20% da janela. 1 vídeo por sessão
- **Antes de chamar API paga** (Claude Vision, ElevenLabs) — confirmar com o usuário

## Passo a Passo

### CAMADA 1: Biblioteca de Footage (análise + catálogo)

#### Passo 1 — Ingestão dos vídeos
```bash
python tools/video_analysis/ingest_videos.py \
  --input-dir .tmp/videos-brutos/ \
  --output-dir .tmp/video-analysis/ \
  --interval 5
```
- Escaneia pasta recursivamente
- Para cada vídeo: extrai metadados + frames a cada 5s + áudio
- Output: `.tmp/video-analysis/{video_name}/` com metadata.json, frames/, audio.wav

#### Passo 2 — Análise visual (⚠️ consome API)
```bash
python tools/video_analysis/analyze_frames.py \
  --video-dir .tmp/video-analysis/{video_name}/ \
  --batch-size 8 \
  --transcribe
```
- Envia frames para Claude Vision API em batches
- Opcionalmente transcreve áudio com faster-whisper
- Output: `analysis.json` com segmentos, tags, scores, descrições

**🔴 CHECKPOINT:** Revise o analysis.json — tags fazem sentido? Scores razoáveis?

#### Passo 3 — Catálogo consolidado
```bash
python tools/video_analysis/build_catalog.py \
  --analysis-dir .tmp/video-analysis/ \
  --min-score 5
```
- Consolida todos os analysis.json num índice unificado
- Output: `catalog.json` pesquisável por tags/tipo/score

### CAMADA 2: Roteiro + Narração

#### Passo 4 — Gerar roteiro
O agente (Claude) escreve o roteiro seguindo a estrutura de 5 fases NTICS:
1. Abertura (0:00–0:12) — gancho visual forte
2. Propósito (0:12–0:25) — por que o projeto existe
3. Como acontece (0:25–0:42) — atividades, números
4. Convite (0:42–0:52) — CTA
5. Fechamento (0:52–final) — cartela

Consultar `workflows/marketing/roteiro_video.md` para a estrutura detalhada.

#### Passo 5 — Gerar narração TTS
```bash
# Edge TTS (gratuito)
python tools/video_analysis/generate_narration.py \
  --text-file .tmp/roteiro.txt \
  --output .tmp/video-assembly/narration.mp3 \
  --engine edge-tts \
  --voice "pt-BR-AntonioNeural"

# ElevenLabs (premium)
python tools/video_analysis/generate_narration.py \
  --text-file .tmp/roteiro.txt \
  --output .tmp/video-assembly/narration.mp3 \
  --engine elevenlabs \
  --voice "nome-da-voz"
```
- Gera .mp3 + .srt (legendas sincronizadas)

**🔴 CHECKPOINT:** Ouça a narração — tom natural? Pronúncias corretas?

### CAMADA 3: Montagem (seleção + timeline)

#### Passo 6 — Montar timeline temática
```bash
python tools/video_analysis/assemble_timeline.py \
  --catalog .tmp/video-analysis/catalog.json \
  --narration .tmp/video-assembly/narration.mp3 \
  --srt .tmp/video-assembly/narration.srt \
  --theme "impacto social" \
  --duration 60 \
  --projeto "Projeto Aurora" \
  --patrocinador "Empresa X" \
  --output .tmp/video-assembly/timeline.json
```
- Seleciona melhores segmentos do catálogo para cada fase
- Sincroniza com narração

**🔴 CHECKPOINT:** Revise timeline.json — B-roll combina com cada fase?

### CAMADA 4: Render (corte + motion + exportação)

#### Passo 7a — Render simples (só FFmpeg, sem motion)
```bash
python tools/video_analysis/render_video.py \
  --timeline .tmp/video-assembly/timeline.json \
  --output-dir .tmp/video-assembly/ \
  --concat-only
```
- Corta segmentos + concatena via transport stream
- Output: `draft.mp4`

#### Passo 7b — Render com motion graphics (Remotion)
```bash
python tools/video_analysis/render_video.py \
  --timeline .tmp/video-assembly/timeline.json \
  --output-dir .tmp/video-assembly/ \
  --remotion-dir tools/remotion-video/

# Depois, no Remotion:
cd tools/remotion-video
npx remotion studio   # Preview ao vivo
npx remotion render VideoAssembly --props ../../.tmp/video-assembly/remotion-props.json out/video.mp4
```

**🔴 CHECKPOINT FINAL:** Assista o vídeo completo — timing ok? Motion graphics posicionados? Cortes suaves?

### Pós-produção opcional (Skills FFmpeg)

| Skill | Quando usar |
|-------|-------------|
| `.claude/skills/video-postprod/silence-removal.md` | Remover pausas de depoimentos |
| `.claude/skills/video-postprod/smart-zoom.md` | Dinamizar talking-head com zoom |
| `.claude/skills/video-postprod/audio-mastering.md` | Masterizar áudio para broadcast |
| `.claude/skills/video-postprod/burn-subtitles.md` | Queimar legendas word-by-word |

## Output Esperado

| Artefato | Caminho |
|----------|---------|
| Catálogo de footage | `.tmp/video-analysis/catalog.json` |
| Análise por vídeo | `.tmp/video-analysis/{video}/analysis.json` |
| Narração (.mp3 + .srt) | `.tmp/video-assembly/narration.mp3` |
| Timeline | `.tmp/video-assembly/timeline.json` |
| Cortes individuais | `.tmp/video-assembly/cuts/{fase}.mp4` |
| Draft (só FFmpeg) | `.tmp/video-assembly/draft.mp4` |
| Vídeo final (Remotion) | `tools/remotion-video/out/video.mp4` |

## Checklist de Qualidade

- [ ] Todos os vídeos brutos foram processados pela ingestão
- [ ] Analysis.json revisado — tags e scores fazem sentido
- [ ] Roteiro segue estrutura 5 fases NTICS
- [ ] Narração revisada — tom natural, pronúncias corretas
- [ ] Timeline revisada — B-roll combina com narração
- [ ] Motion graphics simples (lower thirds, fades, cartelas apenas)
- [ ] Áudio masterizado (loudnorm -16 LUFS para Instagram)
- [ ] Legendas queimadas (se para Reels/TikTok)
- [ ] Vídeo final revisado por humano antes de publicar
- [ ] Cartela final com patrocinador + NTICS Projetos

## Limitações conhecidas

| Limitação | Impacto | Mitigação |
|-----------|---------|-----------|
| Claude não vê output visual | Não detecta texto desalinhado, timing errado | Revisão humana obrigatória |
| Animações complexas quebram | Positioning off, timing weird | Manter componentes simples |
| Context rot em sessões longas | Qualidade das decisões cai | Sessões curtas, 1 vídeo por sessão |
| Rate limits | Sessão pode ser interrompida | Trabalhar em batches pequenas |

## Variações Permitidas

- **Só análise** (sem montagem): Passo 1-3 apenas, gera catálogo
- **Só cortes FFmpeg** (sem motion): Passo 7a, draft simples
- **Com motion graphics**: Passo 7b, render via Remotion
- **Vídeo institucional**: Usar cartela com logo do patrocinador
- **Highlight reel**: Selecionar top 10 segmentos por score, montar sequência

## Referências

- Remotion + Claude Code: remotion.dev/docs/ai/claude-code
- Chris Lema — Skills FFmpeg: chrislema.com
- Karen Spinner — Transport stream lesson: wonderingaboutai.substack.com
- Deborah Folloni — Workflow PT-BR: dfolloni.substack.com
