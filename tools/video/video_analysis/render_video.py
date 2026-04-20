"""
render_video.py — Corta segmentos com FFmpeg e prepara para render Remotion.

Lê um timeline.json, corta os segmentos dos vídeos originais usando FFmpeg
(sem re-encoding via transport stream), e gera o input props para Remotion renderizar
a composição final com motion graphics.

Usage:
  # Só cortar segmentos (sem Remotion)
  python tools/video_analysis/render_video.py \
    --timeline .tmp/video-assembly/timeline.json \
    --output-dir .tmp/video-assembly/cuts/ \
    --cuts-only

  # Pipeline completo (cortes + Remotion render)
  python tools/video_analysis/render_video.py \
    --timeline .tmp/video-assembly/timeline.json \
    --output-dir .tmp/video-assembly/ \
    --remotion-dir tools/remotion-video/

  # Concatenar cortes sem motion graphics (FFmpeg only)
  python tools/video_analysis/render_video.py \
    --timeline .tmp/video-assembly/timeline.json \
    --output-dir .tmp/video-assembly/ \
    --concat-only

IMPORTANTE: Cada render precisa de revisão humana. Claude NÃO vê o output visual.
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


def parse_timestamp(ts: str) -> float:
    """Converte timestamp 'MM:SS.ms' ou 'HH:MM:SS.ms' para segundos."""
    parts = ts.replace(",", ".").split(":")
    if len(parts) == 2:
        return float(parts[0]) * 60 + float(parts[1])
    elif len(parts) == 3:
        return float(parts[0]) * 3600 + float(parts[1]) * 60 + float(parts[2])
    return float(ts)


def cut_segment(source: str, seg_in: str, seg_out: str, output: str) -> bool:
    """Corta segmento do vídeo sem re-encoding (transport stream)."""
    start = parse_timestamp(seg_in)
    end = parse_timestamp(seg_out)
    duration = end - start

    if duration <= 0:
        print(f"  [AVISO] Duração inválida: {seg_in} → {seg_out}", file=sys.stderr)
        return False

    cmd = [
        "ffmpeg", "-y",
        "-ss", str(start),
        "-i", source,
        "-t", str(duration),
        "-c", "copy",
        "-avoid_negative_ts", "make_zero",
        output,
        "-loglevel", "warning"
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        # Fallback: re-encode se copy falhar
        print(f"  [AVISO] Copy falhou, re-encodando...", file=sys.stderr)
        cmd_reencode = [
            "ffmpeg", "-y",
            "-ss", str(start),
            "-i", source,
            "-t", str(duration),
            "-c:v", "libx264", "-preset", "fast", "-crf", "18",
            "-c:a", "aac", "-b:a", "128k",
            output,
            "-loglevel", "warning"
        ]
        result = subprocess.run(cmd_reencode, capture_output=True, text=True)

    return result.returncode == 0


def concat_segments_ts(cuts: list, output: str, narration: str = None) -> bool:
    """Concatena segmentos via transport stream (sem re-encode)."""
    # Converter para .ts
    ts_files = []
    for i, cut_path in enumerate(cuts):
        ts_path = cut_path.rsplit(".", 1)[0] + ".ts"
        cmd = [
            "ffmpeg", "-y", "-i", cut_path,
            "-c", "copy", "-bsf:v", "h264_mp4toannexb",
            "-f", "mpegts", ts_path,
            "-loglevel", "warning"
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            ts_files.append(ts_path)

    if not ts_files:
        return False

    # Concatenar
    concat_input = "|".join(ts_files)
    cmd = [
        "ffmpeg", "-y",
        "-i", f"concat:{concat_input}",
        "-c", "copy",
        output,
        "-loglevel", "warning"
    ]

    # Se tem narração, mixar
    if narration and os.path.exists(narration):
        # Precisa re-encode para mixar áudio
        cmd = [
            "ffmpeg", "-y",
            "-i", f"concat:{concat_input}",
            "-i", narration,
            "-c:v", "copy",
            "-c:a", "aac", "-b:a", "128k",
            "-map", "0:v:0", "-map", "1:a:0",
            "-shortest",
            output,
            "-loglevel", "warning"
        ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    # Limpar .ts temporários
    for ts in ts_files:
        try:
            os.remove(ts)
        except OSError:
            pass

    return result.returncode == 0


def generate_remotion_props(timeline: dict, cuts_dir: str, remotion_dir: str = None) -> dict:
    """Gera props JSON para o Remotion VideoAssembly.

    Se remotion_dir for fornecido, copia os arquivos de corte e narração
    para public/ do Remotion e usa paths relativos (compatível com staticFile()).
    """
    # Se temos remotion_dir, copiar arquivos para public/
    public_dir = None
    if remotion_dir:
        public_dir = os.path.join(remotion_dir, "public")
        public_cuts = os.path.join(public_dir, "cuts")
        os.makedirs(public_cuts, exist_ok=True)

    clips = []
    # Encontrar todos os arquivos de corte existentes em cuts_dir
    existing_cuts = set()
    if os.path.isdir(cuts_dir):
        existing_cuts = {f for f in os.listdir(cuts_dir) if f.endswith(".mp4")}

    fase_counter = {}
    for entry in timeline.get("timeline", []):
        fase_id = entry.get("fase", "unknown")
        fase_counter[fase_id] = fase_counter.get(fase_id, 0) + 1
        clip_name = f"{fase_id}_{fase_counter[fase_id]:02d}.mp4"
        cut_path = os.path.join(cuts_dir, clip_name)

        if not os.path.exists(cut_path):
            # Fallback: tenta nome antigo (sem _01)
            old_name = f"{fase_id}.mp4"
            old_path = os.path.join(cuts_dir, old_name)
            if os.path.exists(old_path):
                cut_path = old_path
                clip_name = old_name

        if public_dir and os.path.exists(cut_path):
            dest = os.path.join(public_dir, "cuts", clip_name)
            shutil.copy2(cut_path, dest)
            src_ref = f"cuts/{clip_name}"
        else:
            src_ref = os.path.abspath(cut_path) if os.path.exists(cut_path) else ""

        clips.append({
            "id": f"{fase_id}_{fase_counter[fase_id]:02d}",
            "src": src_ref,
            "durationInSeconds": entry.get("tempo_fim", 0) - entry.get("tempo_inicio", 0),
            "transition": entry.get("transicao", "cut"),
            "label": entry.get("fase_nome", ""),
        })

    # Copiar narração para public/
    narration_ref = None
    narration_path = (timeline.get("narration") or {}).get("audio_path")
    if narration_path and os.path.exists(narration_path):
        if public_dir:
            dest = os.path.join(public_dir, "narration.mp3")
            shutil.copy2(narration_path, dest)
            narration_ref = "narration.mp3"
        else:
            narration_ref = narration_path

    mg = timeline.get("motion_graphics", {})

    props = {
        "clips": clips,
        "narration": narration_ref,
        "titleCard": mg.get("titulo_card", {}),
        "endCard": mg.get("end_card", {}),
        "lowerThirds": mg.get("lower_thirds", []),
        "totalDurationInSeconds": timeline.get("duracao_alvo", 60),
        "format": timeline.get("formato", "9:16"),
    }

    return props


def main():
    parser = argparse.ArgumentParser(description="Corta segmentos e prepara render Remotion")
    parser.add_argument("--timeline", required=True, help="Caminho do timeline.json")
    parser.add_argument("--output-dir", required=True, help="Pasta de saída")
    parser.add_argument("--remotion-dir", default=None,
                        help="Pasta do projeto Remotion (default: auto-detecta C:/ntics-remotion ou relativo)")
    parser.add_argument("--cuts-only", action="store_true", help="Só cortar, sem concatenar/render")
    parser.add_argument("--concat-only", action="store_true", help="Cortar + concatenar via FFmpeg (sem Remotion)")
    args = parser.parse_args()

    # Auto-detectar remotion-dir se não fornecido
    if not args.remotion_dir and not args.concat_only and not args.cuts_only:
        # Tentar junction path (Windows com espaços no path)
        junction = Path("C:/ntics-remotion")
        relative = Path(__file__).resolve().parent.parent / "remotion-video"
        if junction.exists() and (junction / "package.json").exists():
            args.remotion_dir = str(junction)
        elif relative.exists() and (relative / "package.json").exists():
            args.remotion_dir = str(relative)

    # Carregar timeline
    with open(args.timeline, "r", encoding="utf-8") as f:
        timeline = json.load(f)

    cuts_dir = os.path.join(os.path.abspath(args.output_dir), "cuts")
    os.makedirs(cuts_dir, exist_ok=True)

    # 1. Cortar segmentos
    print("Cortando segmentos dos videos originais...")
    cut_paths = []
    fase_counter = {}
    for entry in timeline.get("timeline", []):
        source = entry.get("source_video", "")
        if not source or source == "[PREENCHER]" or not os.path.exists(source):
            print(f"  [AVISO] Fase '{entry['fase']}': video fonte nao encontrado ({source})")
            continue

        # Naming unico: fase_01.mp4, fase_02.mp4, etc.
        fase_id = entry['fase']
        fase_counter[fase_id] = fase_counter.get(fase_id, 0) + 1
        clip_name = f"{fase_id}_{fase_counter[fase_id]:02d}"
        output_path = os.path.join(cuts_dir, f"{clip_name}.mp4")
        print(f"  Cortando: {clip_name} ({entry.get('segment_in')} -> {entry.get('segment_out')})")

        success = cut_segment(
            source, entry.get("segment_in", "00:00.0"),
            entry.get("segment_out", "00:15.0"), output_path
        )

        if success:
            cut_paths.append(output_path)
            print(f"    [OK] {output_path}")
        else:
            print(f"    [FALHA] ao cortar")

    if not cut_paths:
        print("[ERRO] Nenhum segmento cortado com sucesso", file=sys.stderr)
        sys.exit(1)

    print(f"\n[OK] {len(cut_paths)} segmentos cortados")

    if args.cuts_only:
        json.dump({"status": "ok", "cuts": len(cut_paths), "cuts_dir": cuts_dir}, sys.stdout)
        return

    # 2. Concatenar via FFmpeg (simples) ou gerar props Remotion
    if args.concat_only or not args.remotion_dir:
        print("\nConcatenando segmentos via transport stream...")
        output_video = os.path.join(args.output_dir, "draft.mp4")
        narration = None
        if timeline.get("narration"):
            narration = timeline["narration"].get("audio_path")

        success = concat_segments_ts(cut_paths, output_video, narration)
        if success:
            print(f"\n[OK] Draft concatenado: {output_video}")
            print(f"\n[CHECKPOINT] Assista o draft e valide antes de finalizar!")
        else:
            print("[ERRO] Concatenação falhou", file=sys.stderr)
            sys.exit(1)

        json.dump({"status": "ok", "draft": output_video}, sys.stdout)
    else:
        # 3. Gerar props para Remotion (copia arquivos para public/)
        print("\nGerando props para Remotion...")
        remotion_abs = os.path.abspath(args.remotion_dir)
        props = generate_remotion_props(timeline, cuts_dir, remotion_abs)
        props_path = os.path.join(args.output_dir, "remotion-props.json")
        with open(props_path, "w", encoding="utf-8") as f:
            json.dump(props, f, ensure_ascii=False, indent=2)

        print(f"[OK] Props Remotion gerados: {props_path}")

        # 4. Renderizar via Remotion
        output_video = os.path.join(args.output_dir, "final.mp4")
        print(f"\nRenderizando via Remotion...")
        render_cmd = [
            "npx", "remotion", "render", "VideoAssembly",
            "--props", os.path.abspath(props_path),
            output_video,
        ]
        result = subprocess.run(render_cmd, cwd=remotion_abs, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"\n[OK] Video final renderizado: {output_video}")
            print(f"\n[CHECKPOINT] Assista o video final e valide!")
            json.dump({"status": "ok", "video": output_video, "remotion_props": props_path}, sys.stdout)
        else:
            print(f"[AVISO] Remotion render falhou, verifique manualmente:", file=sys.stderr)
            print(result.stderr, file=sys.stderr)
            print(f"\nRender manual:")
            print(f"  cd {args.remotion_dir}")
            print(f"  npx remotion render VideoAssembly --props {os.path.abspath(props_path)} out.mp4")
            json.dump({"status": "partial", "remotion_props": props_path, "cuts_dir": cuts_dir}, sys.stdout)


if __name__ == "__main__":
    main()
