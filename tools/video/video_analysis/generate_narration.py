"""
generate_narration.py — Gera narração (TTS) a partir de texto de roteiro.

Suporta dois engines:
  - edge-tts (padrão): Gratuito, vozes PT-BR nativas da Microsoft
  - elevenlabs (premium): Vozes ultra-naturais, requer API key

Gera áudio .mp3 + legendas .srt sincronizadas.

Usage:
  # Edge TTS (gratuito)
  python tools/video_analysis/generate_narration.py \
    --text "O Projeto Aurora transformou a realidade de 200 crianças..." \
    --output .tmp/video-assembly/narration.mp3 \
    --engine edge-tts \
    --voice "pt-BR-AntonioNeural"

  # A partir de arquivo de roteiro
  python tools/video_analysis/generate_narration.py \
    --text-file .tmp/roteiro.txt \
    --output .tmp/narration.mp3

  # ElevenLabs (premium)
  python tools/video_analysis/generate_narration.py \
    --text "..." \
    --output .tmp/narration.mp3 \
    --engine elevenlabs \
    --voice "nome-da-voz"

Vozes PT-BR disponíveis (Edge TTS):
  - pt-BR-AntonioNeural  (masculina, narração — recomendada)
  - pt-BR-FranciscaNeural (feminina, narração)
  - pt-BR-ThalitaNeural   (feminina, jovem)
"""

import argparse
import asyncio
import json
import os
import sys
from pathlib import Path


EDGE_VOICES = {
    "antonio": "pt-BR-AntonioNeural",
    "francisca": "pt-BR-FranciscaNeural",
    "thalita": "pt-BR-ThalitaNeural",
}

DEFAULT_VOICE = "pt-BR-AntonioNeural"


async def generate_edge_tts(text: str, output_path: str, voice: str) -> dict:
    """Gera áudio + legendas via Edge TTS (gratuito)."""
    try:
        import edge_tts
    except ImportError:
        print("[ERRO] Instale: pip install edge-tts", file=sys.stderr)
        sys.exit(1)

    # Resolver nome curto para nome completo
    voice = EDGE_VOICES.get(voice.lower(), voice)

    communicate = edge_tts.Communicate(text, voice)

    # Gerar áudio
    print(f"  Gerando áudio com Edge TTS (voz: {voice})...")
    await communicate.save(output_path)

    # Gerar SRT a partir dos word/sentence boundaries
    srt_path = str(Path(output_path).with_suffix(".srt"))
    submaker = edge_tts.SubMaker()
    boundary_type = None
    async for chunk in edge_tts.Communicate(text, voice).stream():
        if chunk["type"] in ("WordBoundary", "SentenceBoundary"):
            if boundary_type is None:
                boundary_type = chunk["type"]
            if chunk["type"] == boundary_type:
                submaker.feed(chunk)

    srt_content = submaker.get_srt()
    with open(srt_path, "w", encoding="utf-8") as f:
        f.write(srt_content)

    return {
        "engine": "edge-tts",
        "voice": voice,
        "audio_path": output_path,
        "srt_path": srt_path,
        "text_length": len(text),
    }


def generate_elevenlabs(text: str, output_path: str, voice: str) -> dict:
    """Gera áudio via ElevenLabs (premium)."""
    try:
        from elevenlabs.client import ElevenLabs
    except ImportError:
        print("[ERRO] Instale: pip install elevenlabs", file=sys.stderr)
        sys.exit(1)

    api_key = os.environ.get("ELEVENLABS_API_KEY")
    if not api_key:
        print("[ERRO] ELEVENLABS_API_KEY não definida", file=sys.stderr)
        sys.exit(1)

    client = ElevenLabs(api_key=api_key)

    print(f"  Gerando áudio com ElevenLabs (voz: {voice})...")
    audio = client.text_to_speech.convert(
        text=text,
        voice_id=voice,
        model_id="eleven_multilingual_v2",
        output_format="mp3_44100_128",
    )

    with open(output_path, "wb") as f:
        for chunk in audio:
            f.write(chunk)

    return {
        "engine": "elevenlabs",
        "voice": voice,
        "audio_path": output_path,
        "srt_path": None,
        "text_length": len(text),
    }


def estimate_duration(text: str, words_per_minute: int = 150) -> float:
    """Estima duração da narração em segundos."""
    word_count = len(text.split())
    return (word_count / words_per_minute) * 60


def main():
    parser = argparse.ArgumentParser(description="Gera narração TTS a partir de texto")
    parser.add_argument("--text", default=None, help="Texto para narrar")
    parser.add_argument("--text-file", default=None, help="Arquivo com texto para narrar")
    parser.add_argument("--output", required=True, help="Caminho do arquivo de áudio (.mp3)")
    parser.add_argument("--engine", default="edge-tts", choices=["edge-tts", "elevenlabs"],
                        help="Engine TTS (default: edge-tts)")
    parser.add_argument("--voice", default=DEFAULT_VOICE,
                        help="Nome da voz (default: pt-BR-AntonioNeural)")
    args = parser.parse_args()

    # Obter texto
    if args.text:
        text = args.text
    elif args.text_file:
        with open(args.text_file, "r", encoding="utf-8") as f:
            text = f.read().strip()
    else:
        print("[ERRO] Forneça --text ou --text-file", file=sys.stderr)
        sys.exit(1)

    if not text:
        print("[ERRO] Texto vazio", file=sys.stderr)
        sys.exit(1)

    # Criar diretório de saída
    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)

    # Estimar duração
    est_duration = estimate_duration(text)
    print(f"Texto: {len(text.split())} palavras (~{est_duration:.0f}s estimados)")

    # Gerar narração
    if args.engine == "edge-tts":
        result = asyncio.run(generate_edge_tts(text, args.output, args.voice))
    elif args.engine == "elevenlabs":
        result = generate_elevenlabs(text, args.output, args.voice)

    result["duracao_estimada_segundos"] = est_duration

    print(f"\n[OK] Narracao gerada: {result['audio_path']}")
    if result.get("srt_path"):
        print(f"  Legendas: {result['srt_path']}")

    json.dump({"status": "ok", **result}, sys.stdout)


if __name__ == "__main__":
    main()
