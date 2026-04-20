"""
ingest_videos.py — Ingestão de vídeos brutos para análise.

Escaneia uma pasta de vídeos, extrai metadados (FFprobe), frames a cada N segundos
(FFmpeg) e áudio (para transcrição futura). Prepara tudo para análise visual.

Usage:
  python tools/video_analysis/ingest_videos.py \
    --input-dir .tmp/videos-brutos/ \
    --output-dir .tmp/video-analysis/ \
    --interval 5

  # Só metadados (sem frames/áudio)
  python tools/video_analysis/ingest_videos.py \
    --input-dir .tmp/videos-brutos/ \
    --metadata-only

Output por vídeo:
  .tmp/video-analysis/{video_name}/
    ├── metadata.json     # Duração, resolução, fps, codec
    ├── frames/           # frame_00000.jpg, frame_00005.jpg, ...
    └── audio.wav         # Áudio extraído para transcrição
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

VIDEO_EXTENSIONS = {".mp4", ".mov", ".avi", ".mkv", ".webm", ".m4v", ".mts"}


def get_video_metadata(video_path: str) -> dict:
    """Extrai metadados do vídeo via FFprobe."""
    cmd = [
        "ffprobe", "-v", "quiet",
        "-print_format", "json",
        "-show_format", "-show_streams",
        str(video_path)
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"[ERRO] FFprobe falhou para {video_path}: {result.stderr}", file=sys.stderr)
        return {}

    probe = json.loads(result.stdout)
    video_stream = next(
        (s for s in probe.get("streams", []) if s.get("codec_type") == "video"),
        {}
    )
    audio_stream = next(
        (s for s in probe.get("streams", []) if s.get("codec_type") == "audio"),
        {}
    )
    fmt = probe.get("format", {})

    duration = float(fmt.get("duration", 0))
    minutes = int(duration // 60)
    seconds = int(duration % 60)

    return {
        "arquivo": os.path.basename(video_path),
        "caminho": str(video_path),
        "duracao_segundos": duration,
        "duracao_formatada": f"{minutes:02d}:{seconds:02d}",
        "resolucao": f"{video_stream.get('width', '?')}x{video_stream.get('height', '?')}",
        "width": video_stream.get("width"),
        "height": video_stream.get("height"),
        "fps": eval(video_stream.get("r_frame_rate", "0/1")) if video_stream.get("r_frame_rate") else 0,
        "codec_video": video_stream.get("codec_name", "?"),
        "codec_audio": audio_stream.get("codec_name", "?"),
        "tamanho_mb": round(float(fmt.get("size", 0)) / (1024 * 1024), 2),
        "bitrate_kbps": round(float(fmt.get("bit_rate", 0)) / 1000, 0),
    }


def detect_scenes(video_path: str, output_dir: str, threshold: float = 0.3) -> list:
    """Detecta cenas via FFmpeg scene filter e extrai 1 frame por cena.

    Usa `select='gt(scene,threshold)'` do FFmpeg — rápido, sem dependências extras.
    Escreve stderr em arquivo temporário para evitar deadlock no Windows com vídeos grandes.
    Retorna lista de cenas com in/out reais. Retorna [] se nenhum corte detectado.
    """
    import re
    import tempfile

    frames_dir = os.path.join(output_dir, "frames")
    os.makedirs(frames_dir, exist_ok=True)

    # Obter duração total
    probe_cmd = [
        "ffprobe", "-v", "quiet", "-show_format", "-of", "json", str(video_path)
    ]
    probe = subprocess.run(probe_cmd, capture_output=True, text=True, timeout=30)
    try:
        duration = float(json.loads(probe.stdout)["format"]["duration"])
    except (KeyError, ValueError, json.JSONDecodeError):
        return []

    # Detectar cenas — escrever stderr em temp file para evitar deadlock no Windows
    # -hwaccel auto: usa GPU quando disponível (13x mais rápido em Windows)
    frames_pattern = os.path.join(frames_dir, "scene_%03d.jpg")
    detect_cmd = [
        "ffmpeg", "-hwaccel", "auto",
        "-i", str(video_path),
        "-vf", f"select='gt(scene,{threshold})',showinfo",
        "-vsync", "vfr", "-q:v", "2",
        frames_pattern,
        "-y", "-loglevel", "warning"
    ]

    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as tf:
        tmp_path = tf.name

    try:
        with open(tmp_path, "w", encoding="utf-8", errors="replace") as err_file:
            proc = subprocess.Popen(
                detect_cmd,
                stdout=subprocess.DEVNULL,
                stderr=err_file
            )
            proc.wait(timeout=int(duration * 3 + 30))  # 3x duração + 30s margem

        with open(tmp_path, "r", encoding="utf-8", errors="replace") as f:
            stderr_output = f.read()
    except subprocess.TimeoutExpired:
        proc.kill()
        print(f"[AVISO] detect_scenes timeout para {os.path.basename(str(video_path))}", file=sys.stderr)
        return []
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass

    # Parsear timestamps de corte do output showinfo
    cut_times = [0.0]
    for line in stderr_output.split("\n"):
        if "pts_time" in line and "showinfo" in line:
            m = re.search(r"pts_time:([\d.]+)", line)
            if m:
                t = float(m.group(1))
                if t > 0.5:  # ignorar near-start
                    cut_times.append(round(t, 3))

    cut_times.append(round(duration, 3))
    cut_times = sorted(set(cut_times))

    if len(cut_times) <= 2:
        # Sem cortes intermediários — vídeo contínuo
        return []

    # Montar lista de cenas
    frame_files = sorted([
        f for f in os.listdir(frames_dir) if f.startswith("scene_") and f.endswith(".jpg")
    ])

    scenes = []
    for i in range(len(cut_times) - 1):
        frame_name = frame_files[i] if i < len(frame_files) else ""
        scenes.append({
            "id": i + 1,
            "in_seconds": cut_times[i],
            "out_seconds": cut_times[i + 1],
            "duracao": round(cut_times[i + 1] - cut_times[i], 3),
            "frame": frame_name
        })

    return scenes


def extract_frames(video_path: str, output_dir: str, interval: int = 5) -> int:
    """Extrai frames a cada N segundos via FFmpeg (fallback quando sem cortes detectáveis)."""
    frames_dir = os.path.join(output_dir, "frames")
    os.makedirs(frames_dir, exist_ok=True)

    cmd = [
        "ffmpeg", "-i", str(video_path),
        "-vf", f"fps=1/{interval}",
        "-q:v", "2",
        "-vsync", "vfr",
        os.path.join(frames_dir, "frame_%05d.jpg"),
        "-y", "-loglevel", "warning"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"[ERRO] Extração de frames falhou: {result.stderr}", file=sys.stderr)
        return 0

    frame_count = len([f for f in os.listdir(frames_dir) if f.endswith(".jpg")])
    return frame_count


def extract_audio(video_path: str, output_dir: str) -> str:
    """Extrai áudio do vídeo como WAV mono 16kHz (ideal para Whisper)."""
    audio_path = os.path.join(output_dir, "audio.wav")

    cmd = [
        "ffmpeg", "-i", str(video_path),
        "-vn", "-acodec", "pcm_s16le",
        "-ar", "16000", "-ac", "1",
        audio_path,
        "-y", "-loglevel", "warning"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"[ERRO] Extração de áudio falhou: {result.stderr}", file=sys.stderr)
        return ""

    return audio_path


def find_videos(input_dir: str) -> list:
    """Encontra todos os vídeos na pasta (recursivo)."""
    videos = []
    for root, _, files in os.walk(input_dir):
        for f in files:
            if Path(f).suffix.lower() in VIDEO_EXTENSIONS:
                videos.append(os.path.join(root, f))
    return sorted(videos)


def ingest_video(video_path: str, output_dir: str, interval: int, metadata_only: bool) -> dict:
    """Processa um único vídeo: metadados + frames + áudio."""
    video_name = Path(video_path).stem
    video_out_dir = os.path.join(output_dir, video_name)
    os.makedirs(video_out_dir, exist_ok=True)

    # 1. Metadados
    print(f"  [1/3] Extraindo metadados...")
    metadata = get_video_metadata(video_path)
    if not metadata:
        return {"erro": f"Falha ao extrair metadados de {video_path}"}

    if metadata_only:
        metadata_path = os.path.join(video_out_dir, "metadata.json")
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        return metadata

    # 2. Detecção de cenas
    print(f"  [2/3] Detectando cenas com PySceneDetect...")
    scenes = detect_scenes(video_path, video_out_dir)

    if scenes:
        metadata["frames_extraidos"] = len(scenes)
        metadata["intervalo_frames"] = None
        metadata["scenes"] = scenes
    else:
        # Fallback: frames fixos a cada N segundos
        print(f"  [2/3] Sem cortes detectados — fallback: frames a cada {interval}s...")
        frame_count = extract_frames(video_path, video_out_dir, interval)
        metadata["frames_extraidos"] = frame_count
        metadata["intervalo_frames"] = interval
        metadata["scenes"] = []

    # 3. Áudio
    print(f"  [3/3] Extraindo áudio...")
    audio_path = extract_audio(video_path, video_out_dir)
    metadata["audio_extraido"] = bool(audio_path)

    # Salvar metadados
    metadata_path = os.path.join(video_out_dir, "metadata.json")
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

    return metadata


def main():
    parser = argparse.ArgumentParser(
        description="Ingestão de vídeos brutos para análise"
    )
    parser.add_argument("--input-dir", required=True, help="Pasta com vídeos brutos")
    parser.add_argument("--output-dir", default=".tmp/video-analysis/", help="Pasta de saída")
    parser.add_argument("--interval", type=int, default=5, help="Intervalo entre frames em segundos (default: 5)")
    parser.add_argument("--metadata-only", action="store_true", help="Só extrair metadados, sem frames/áudio")
    args = parser.parse_args()

    input_dir = os.path.abspath(args.input_dir)
    output_dir = os.path.abspath(args.output_dir)

    if not os.path.isdir(input_dir):
        print(f"[ERRO] Pasta não encontrada: {input_dir}", file=sys.stderr)
        sys.exit(1)

    videos = find_videos(input_dir)
    if not videos:
        print(f"[ERRO] Nenhum vídeo encontrado em {input_dir}", file=sys.stderr)
        sys.exit(1)

    print(f"Encontrados {len(videos)} vídeos em {input_dir}")
    os.makedirs(output_dir, exist_ok=True)

    results = []
    for i, video_path in enumerate(videos, 1):
        print(f"\n[{i}/{len(videos)}] Processando: {os.path.basename(video_path)}")
        result = ingest_video(video_path, output_dir, args.interval, args.metadata_only)
        results.append(result)

    # Salvar manifesto geral
    manifest_path = os.path.join(output_dir, "ingest_manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump({
            "total_videos": len(results),
            "input_dir": input_dir,
            "output_dir": output_dir,
            "intervalo_frames": args.interval,
            "videos": results
        }, f, ensure_ascii=False, indent=2)

    print(f"\n[OK] Ingestao completa. {len(results)} videos processados.")
    print(f"  Manifesto: {manifest_path}")

    # Output JSON para stdout (para orquestração)
    json.dump({"status": "ok", "total": len(results), "manifest": manifest_path}, sys.stdout)


if __name__ == "__main__":
    main()
