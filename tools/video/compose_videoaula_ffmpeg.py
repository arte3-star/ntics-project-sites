"""Compoe videoaula faceless a partir de cenas.json + slides PNG + clipes MP4 + audios MP3.

Para cada cena:
- Se eh slide: cria video estatico (imagem + audio) com duracao do audio
- Se eh clipe: usa o clipe (loop ou trim) com audio por cima

Depois concatena tudo via FFmpeg concat demuxer.

Uso:
    python compose_videoaula_ffmpeg.py

Espera estrutura:
    output/workshops/videoaula/
        cenas.json
        slides/slide-NNN.png
        clips/*.mp4
        audio/cena-NN.mp3
        out/  (sera criado)
"""
import json, subprocess, sys
from pathlib import Path

ROOT = Path("g:/O meu disco/AUTOMAÇÕES/output/workshops/videoaula")
PADDING = 0.4  # segundos de respiro depois do audio
WIDTH, HEIGHT = 1920, 1080
FPS = 30


def run(cmd, **kw):
    r = subprocess.run(cmd, capture_output=True, text=True, **kw)
    if r.returncode != 0:
        print("STDERR:", r.stderr[-500:])
        raise RuntimeError(f"Comando falhou: {' '.join(map(str,cmd))}")
    return r


def compose_slide_scene(slide_path, audio_path, dur, out_path):
    """Slide estatico com audio."""
    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-i", str(slide_path),
        "-i", str(audio_path),
        "-t", f"{dur:.2f}",
        "-vf", f"scale={WIDTH}:{HEIGHT}:force_original_aspect_ratio=decrease,"
                f"pad={WIDTH}:{HEIGHT}:(ow-iw)/2:(oh-ih)/2:color=black,fps={FPS}",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "veryfast", "-crf", "23",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest",
        str(out_path)
    ]
    run(cmd)


def compose_clip_scene(clip_path, audio_path, dur, out_path):
    """Clipe de video (loop se necessario) com audio por cima."""
    cmd = [
        "ffmpeg", "-y",
        "-stream_loop", "-1", "-i", str(clip_path),  # loop infinito
        "-i", str(audio_path),
        "-t", f"{dur:.2f}",
        "-vf", f"scale={WIDTH}:{HEIGHT}:force_original_aspect_ratio=decrease,"
                f"pad={WIDTH}:{HEIGHT}:(ow-iw)/2:(oh-ih)/2:color=black,fps={FPS}",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "veryfast", "-crf", "23",
        "-c:a", "aac", "-b:a", "192k",
        "-map", "0:v", "-map", "1:a",  # video do clipe, audio da narracao
        "-shortest",
        str(out_path)
    ]
    run(cmd)


def main():
    cenas = json.loads((ROOT / "cenas.json").read_text(encoding="utf-8"))
    out_dir = ROOT / "out"
    out_dir.mkdir(parents=True, exist_ok=True)
    cenas_dir = out_dir / "cenas-mp4"
    cenas_dir.mkdir(exist_ok=True)

    for c in cenas:
        n = c['n']
        out_cena = cenas_dir / f"cena-{n:02d}.mp4"
        if out_cena.exists():
            print(f"Cena {n:2d}: pulando (ja existe)")
            continue

        audio = ROOT / c['audio_path']
        dur = c['audio_duration'] + PADDING

        if c['tipo'] == 'slide':
            slide = ROOT / "slides" / c['media']
            compose_slide_scene(slide, audio, dur, out_cena)
            print(f"Cena {n:2d} [slide] {c['media']:38s} {dur:5.2f}s OK")
        else:
            clip = ROOT / "clips" / c['media']
            compose_clip_scene(clip, audio, dur, out_cena)
            print(f"Cena {n:2d} [clipe] {c['media']:38s} {dur:5.2f}s OK")

    # Concatena
    print("\nConcatenando 29 cenas...")
    list_file = out_dir / "concat-list.txt"
    list_file.write_text(
        "\n".join(f"file 'cenas-mp4/cena-{c['n']:02d}.mp4'" for c in cenas),
        encoding="utf-8"
    )

    final = out_dir / "videoaula-RAW.mp4"
    cmd = [
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", str(list_file),
        "-c", "copy",
        str(final)
    ]
    run(cmd)

    # Mede duracao final
    r = subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","default=noprint_wrappers=1:nokey=1",str(final)],
                      capture_output=True, text=True)
    dur = float(r.stdout.strip())
    size_mb = final.stat().st_size / 1024 / 1024
    print(f"\n=== FINAL ===")
    print(f"Arquivo: {final}")
    print(f"Duracao: {dur:.1f}s = {int(dur//60)}min {int(dur%60)}s")
    print(f"Tamanho: {size_mb:.1f} MB")


if __name__ == "__main__":
    main()
