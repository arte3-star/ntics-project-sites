"""
drive_transcribe.py — Baixa video do Google Drive e transcreve com faster-whisper.

Usage:
  python tools/integrations/drive_transcribe.py --url "https://drive.google.com/file/d/FILE_ID/view"
  python tools/integrations/drive_transcribe.py --id FILE_ID
  python tools/integrations/drive_transcribe.py --id FILE_ID --lang pt --model medium

Saida:
  tmp/transcricoes/{nome_do_arquivo}.txt   (texto limpo)
  tmp/transcricoes/{nome_do_arquivo}.srt   (com timestamps)

PRE-REQUISITO:
  pip install faster-whisper
  credentials.json em tools/gws/ (mesmo OAuth usado pelos outros scripts Drive)
"""

import argparse
import io
import re
import sys
from pathlib import Path

from googleapiclient.http import MediaIoBaseDownload

sys.path.insert(0, str(Path(__file__).parent))
from upload_to_drive import get_drive_service  # noqa: E402

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

TRANSCRICOES_DIR = Path(__file__).parent.parent.parent / "tmp" / "transcricoes"
DOWNLOAD_DIR = Path(__file__).parent.parent.parent / "tmp" / "drive_videos"

VIDEO_MIMES = {
    "video/mp4", "video/quicktime", "video/x-msvideo",
    "video/x-matroska", "video/webm", "video/mpeg",
}


def extract_file_id(url_or_id: str) -> str:
    """Extrai file ID de URL do Drive ou retorna o ID direto."""
    match = re.search(r"/d/([a-zA-Z0-9_-]{25,})", url_or_id)
    if match:
        return match.group(1)
    match = re.search(r"id=([a-zA-Z0-9_-]{25,})", url_or_id)
    if match:
        return match.group(1)
    return url_or_id.strip()


def download_video(service, file_id: str) -> Path:
    """Baixa o arquivo do Drive para tmp/drive_videos/ e retorna o Path local."""
    meta = service.files().get(fileId=file_id, fields="name,mimeType,size").execute()
    name = meta["name"]
    mime = meta.get("mimeType", "")
    size_mb = int(meta.get("size", 0)) / 1_048_576

    print(f"Arquivo: {name}")
    print(f"Tipo:    {mime}")
    print(f"Tamanho: {size_mb:.1f} MB")

    if mime not in VIDEO_MIMES:
        print(f"AVISO: MIME '{mime}' nao e video reconhecido. Tentando mesmo assim.")

    DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
    dest = DOWNLOAD_DIR / name

    if dest.exists():
        print(f"Ja existe em cache: {dest}")
        return dest

    print("Baixando...", end=" ", flush=True)
    request = service.files().get_media(fileId=file_id)
    buf = io.BytesIO()
    downloader = MediaIoBaseDownload(buf, request, chunksize=8 * 1024 * 1024)
    done = False
    while not done:
        status, done = downloader.next_chunk()
        if status:
            print(f"{int(status.progress() * 100)}%", end=" ", flush=True)
    print("OK")

    dest.write_bytes(buf.getvalue())
    print(f"Salvo em: {dest}")
    return dest


def format_srt_time(seconds: float) -> str:
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds % 1) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def transcribe(video_path: Path, lang: str, model_size: str) -> tuple[str, str]:
    """Transcreve com faster-whisper. Retorna (texto_limpo, conteudo_srt)."""
    from faster_whisper import WhisperModel

    print(f"\nCarregando modelo Whisper '{model_size}'...")
    model = WhisperModel(model_size, device="cpu", compute_type="int8")

    print(f"Transcrevendo em '{lang}'...")
    segments, info = model.transcribe(str(video_path), language=lang, beam_size=5)

    print(f"Idioma detectado: {info.language} (prob {info.language_probability:.0%})")

    texto_lines = []
    srt_lines = []
    for i, seg in enumerate(segments, 1):
        texto_lines.append(seg.text.strip())
        srt_lines.append(str(i))
        srt_lines.append(f"{format_srt_time(seg.start)} --> {format_srt_time(seg.end)}")
        srt_lines.append(seg.text.strip())
        srt_lines.append("")

    return "\n".join(texto_lines), "\n".join(srt_lines)


def main():
    parser = argparse.ArgumentParser(description="Transcreve video do Google Drive")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--url", help="URL completa do Google Drive")
    group.add_argument("--id", help="File ID do Google Drive")
    parser.add_argument("--lang", default="pt", help="Idioma (padrao: pt)")
    parser.add_argument(
        "--model",
        default="base",
        choices=["tiny", "base", "small", "medium", "large-v2", "large-v3"],
        help="Tamanho do modelo Whisper (padrao: base)",
    )
    args = parser.parse_args()

    file_id = extract_file_id(args.url if args.url else args.id)
    print(f"File ID: {file_id}")

    service = get_drive_service()
    video_path = download_video(service, file_id)

    texto, srt = transcribe(video_path, args.lang, args.model)

    TRANSCRICOES_DIR.mkdir(parents=True, exist_ok=True)
    stem = video_path.stem
    txt_path = TRANSCRICOES_DIR / f"{stem}.txt"
    srt_path = TRANSCRICOES_DIR / f"{stem}.srt"

    txt_path.write_text(texto, encoding="utf-8")
    srt_path.write_text(srt, encoding="utf-8")

    print(f"\n{'='*60}")
    print(f"Transcricao salva em:")
    print(f"  Texto: {txt_path}")
    print(f"  SRT:   {srt_path}")
    print(f"{'='*60}")
    print("\nPREVIA (primeiros 500 caracteres):")
    print(texto[:500])


if __name__ == "__main__":
    main()
