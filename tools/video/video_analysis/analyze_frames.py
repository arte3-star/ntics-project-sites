"""
analyze_frames.py — Análise visual de vídeo via Claude Vision API.

Envia frames extraídos para Claude Vision em batches, recebe descrições visuais,
e gera um analysis.json com segmentos catalogados por tags, score e tipo.

Usage:
  python tools/video_analysis/analyze_frames.py \
    --video-dir .tmp/video-analysis/video_001/ \
    --batch-size 8

  # Com transcrição (se existir audio.wav)
  python tools/video_analysis/analyze_frames.py \
    --video-dir .tmp/video-analysis/video_001/ \
    --transcribe

Output:
  .tmp/video-analysis/video_001/analysis.json

ATENÇÃO: Consome tokens da API Claude. Cada batch de 8 frames ≈ 1 chamada API.
Para 100 vídeos de 5min cada (60 frames/vídeo), são ~750 chamadas.
"""

import argparse
import base64
import json
import os
import sys
from pathlib import Path

try:
    import anthropic
except ImportError:
    print("[ERRO] Instale: pip install anthropic", file=sys.stderr)
    sys.exit(1)


ANALYSIS_PROMPT = """Analise estas {n_frames} frames extraídas de um vídeo de evento/projeto social.
Cada frame representa uma cena distinta com timestamps reais indicados abaixo.

{transcription_context}

Para cada frame/cena, forneça um segmento com:
- **in/out**: use os timestamps reais fornecidos no contexto (formato "MM:SS.s")
- **descricao_visual**: o que está acontecendo visualmente (1-2 frases)
- **tags**: lista de tags descritivas (ex: "evento", "sala-de-aula", "depoimento", "atividade", "plateia", "bastidores", "paisagem", "close-up")
- **score**: 1-10 (qualidade visual: iluminação, enquadramento, foco, estabilidade, interesse visual)
- **tipo**: um de [b-roll, depoimento, atividade, plateia, bastidores, paisagem, cartela, outro]
- **qualidade_tecnica**: breve nota sobre iluminação, foco, estabilidade
- **uso_sugerido**: onde esse trecho seria útil num vídeo (abertura, contexto, prova social, CTA, etc.)

Responda APENAS em JSON válido, sem markdown:
{{
  "segmentos": [
    {{
      "id": "seg01",
      "in": "00:00.0",
      "out": "00:15.0",
      "descricao_visual": "...",
      "tags": ["..."],
      "score": 8,
      "tipo": "b-roll",
      "qualidade_tecnica": "...",
      "uso_sugerido": "..."
    }}
  ],
  "resumo": "Resumo geral do conteúdo do vídeo em 2-3 frases."
}}"""


def load_frames(frames_dir: str, max_frames: int = 60) -> list:
    """Carrega frames como base64 para envio à API."""
    frames = sorted([
        f for f in os.listdir(frames_dir)
        if f.endswith((".jpg", ".png"))
    ])

    if len(frames) > max_frames:
        step = len(frames) / max_frames
        frames = [frames[int(i * step)] for i in range(max_frames)]

    loaded = []
    for frame_name in frames:
        frame_path = os.path.join(frames_dir, frame_name)
        with open(frame_path, "rb") as f:
            data = base64.standard_b64encode(f.read()).decode("utf-8")
        loaded.append({
            "name": frame_name,
            "path": frame_path,
            "base64": data,
            "media_type": "image/jpeg"
        })
    return loaded


def transcribe_audio(video_dir: str) -> str:
    """Transcreve áudio com WhisperX (word-level, PT-BR). Fallback para faster-whisper."""
    audio_path = os.path.join(video_dir, "audio.wav")
    if not os.path.exists(audio_path):
        return ""

    # Tentativa 1: WhisperX (word-level timestamps)
    try:
        import whisperx
        print("  Transcrevendo com WhisperX (word-level)...")
        model = whisperx.load_model("base", device="cpu", language="pt", compute_type="int8")
        result = model.transcribe(audio_path)
        align_model, align_meta = whisperx.load_align_model("pt", device="cpu")
        result = whisperx.align(result["segments"], align_model, align_meta, audio_path, "cpu")

        # Salvar word-level JSON
        words_path = os.path.join(video_dir, "transcription_words.json")
        with open(words_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        # Formatar como texto com timestamps para o prompt
        lines = []
        for seg in result.get("segments", []):
            start = seg.get("start", 0)
            end = seg.get("end", 0)
            text = seg.get("text", "").strip()
            start_fmt = f"{int(start//60):02d}:{start%60:05.2f}"
            end_fmt = f"{int(end//60):02d}:{end%60:05.2f}"
            lines.append(f"[{start_fmt} → {end_fmt}] {text}")

        transcription = "\n".join(lines)
        txt_path = os.path.join(video_dir, "transcription.txt")
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(transcription)
        return transcription

    except ImportError:
        pass  # WhisperX não instalado, tentar fallback

    # Fallback: faster-whisper (segmento-level)
    try:
        from faster_whisper import WhisperModel
        print("  Transcrevendo com faster-whisper (fallback)...")
        fw_model = WhisperModel("base", device="cpu", compute_type="int8")
        segments, _ = fw_model.transcribe(audio_path, language="pt")

        lines = []
        for seg in segments:
            start_fmt = f"{int(seg.start//60):02d}:{seg.start%60:05.2f}"
            end_fmt = f"{int(seg.end//60):02d}:{seg.end%60:05.2f}"
            lines.append(f"[{start_fmt} → {end_fmt}] {seg.text.strip()}")

        transcription = "\n".join(lines)
        txt_path = os.path.join(video_dir, "transcription.txt")
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(transcription)
        return transcription

    except ImportError:
        print("[AVISO] whisperx e faster-whisper não disponíveis. Pulando transcrição.", file=sys.stderr)
        return ""


def analyze_batch(client: anthropic.Anthropic, frames: list, interval: int,
                  batch_idx: int, transcription: str = "", scenes: list = None) -> dict:
    """Envia um batch de frames para Claude Vision e retorna análise."""
    content = []

    for frame in frames:
        content.append({
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": frame["media_type"],
                "data": frame["base64"]
            }
        })

    transcription_context = ""

    # Timestamps reais das cenas (PySceneDetect)
    if scenes:
        frame_names = [f["name"] for f in frames]
        scene_lines = []
        for s in scenes:
            if s["frame"] in frame_names:
                in_fmt = f"{int(s['in_seconds']//60):02d}:{s['in_seconds']%60:05.2f}"
                out_fmt = f"{int(s['out_seconds']//60):02d}:{s['out_seconds']%60:05.2f}"
                scene_lines.append(f"  {s['frame']}: cena {in_fmt} → {out_fmt} ({s['duracao']:.1f}s)")
        if scene_lines:
            transcription_context += "Timestamps reais de cada cena (use exatamente esses valores para in/out):\n"
            transcription_context += "\n".join(scene_lines) + "\n\n"

    if transcription:
        transcription_context += f"Transcrição do áudio (para contexto):\n{transcription[:2000]}\n"

    content.append({
        "type": "text",
        "text": ANALYSIS_PROMPT.format(
            n_frames=len(frames),
            interval=interval,
            transcription_context=transcription_context
        )
    })

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        messages=[{"role": "user", "content": content}]
    )

    response_text = response.content[0].text.strip()
    if response_text.startswith("```"):
        response_text = response_text.split("\n", 1)[1].rsplit("```", 1)[0]

    try:
        return json.loads(response_text)
    except json.JSONDecodeError:
        print(f"  [AVISO] Batch {batch_idx}: resposta não é JSON válido", file=sys.stderr)
        return {"segmentos": [], "resumo": "Erro na análise"}


def main():
    parser = argparse.ArgumentParser(description="Análise visual de vídeo via Claude Vision")
    parser.add_argument("--video-dir", required=True, help="Pasta do vídeo (com frames/ e metadata.json)")
    parser.add_argument("--batch-size", type=int, default=8, help="Frames por chamada API (default: 8)")
    parser.add_argument("--transcribe", action="store_true", help="Transcrever áudio antes da análise")
    parser.add_argument("--max-frames", type=int, default=60, help="Máximo de frames a analisar (default: 60)")
    args = parser.parse_args()

    video_dir = os.path.abspath(args.video_dir)
    frames_dir = os.path.join(video_dir, "frames")

    if not os.path.isdir(frames_dir):
        print(f"[ERRO] Pasta de frames não encontrada: {frames_dir}", file=sys.stderr)
        sys.exit(1)

    # Carregar metadados
    metadata_path = os.path.join(video_dir, "metadata.json")
    metadata = {}
    if os.path.exists(metadata_path):
        with open(metadata_path, "r") as f:
            metadata = json.load(f)

    interval = metadata.get("intervalo_frames", 5) or 5
    scenes = metadata.get("scenes", [])

    # Transcrição opcional
    transcription = ""
    if args.transcribe:
        transcription = transcribe_audio(video_dir)
        if transcription:
            print(f"  Transcrição: {len(transcription)} caracteres")

    # Carregar frames
    print(f"Carregando frames de {frames_dir}...")
    frames = load_frames(frames_dir, args.max_frames)
    if not frames:
        print("[ERRO] Nenhum frame encontrado", file=sys.stderr)
        sys.exit(1)
    print(f"  {len(frames)} frames carregados")

    # Carregar .env se existir
    try:
        from dotenv import load_dotenv
        env_path = Path(__file__).resolve().parent.parent.parent.parent / ".env"
        if env_path.exists():
            load_dotenv(env_path)
    except ImportError:
        pass

    # Inicializar cliente Anthropic
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("[ERRO] ANTHROPIC_API_KEY nao definida", file=sys.stderr)
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)

    # Processar em batches
    all_segments = []
    resumo = ""
    batches = [frames[i:i + args.batch_size] for i in range(0, len(frames), args.batch_size)]

    print(f"Analisando {len(frames)} frames em {len(batches)} batches...")
    for i, batch in enumerate(batches):
        print(f"  Batch {i+1}/{len(batches)} ({len(batch)} frames)...")
        result = analyze_batch(client, batch, interval, i, transcription, scenes)
        all_segments.extend(result.get("segmentos", []))
        if result.get("resumo"):
            resumo = result["resumo"]

    # Renumerar IDs dos segmentos
    video_name = Path(video_dir).stem
    for j, seg in enumerate(all_segments):
        seg["id"] = f"{video_name}_seg{j+1:02d}"

    # Montar analysis.json
    analysis = {
        "arquivo": metadata.get("arquivo", Path(video_dir).stem),
        "duracao": metadata.get("duracao_formatada", "?"),
        "duracao_segundos": metadata.get("duracao_segundos", 0),
        "resolucao": metadata.get("resolucao", "?"),
        "fps": metadata.get("fps", 0),
        "resumo": resumo,
        "total_segmentos": len(all_segments),
        "segmentos": all_segments,
        "transcricao_disponivel": bool(transcription),
    }

    output_path = os.path.join(video_dir, "analysis.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(analysis, f, ensure_ascii=False, indent=2)

    print(f"\n[OK] Analise completa: {len(all_segments)} segmentos identificados")
    print(f"  Output: {output_path}")

    json.dump({"status": "ok", "segmentos": len(all_segments), "output": output_path}, sys.stdout)


if __name__ == "__main__":
    main()
