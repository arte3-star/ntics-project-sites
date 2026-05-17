"""
HeyGen Video Creator — Programa Estação Samarco
Cria vídeos de avatar + slides automaticamente via HeyGen API v2.

Pré-requisitos no .env:
    HEYGEN_API_KEY     = sua chave da API HeyGen (Settings > API)
    HEYGEN_AVATAR_ID   = ID do avatar (HeyGen > Avatars > clica no avatar > copiar ID)
    HEYGEN_VOICE_ID    = ID da voz PT-BR (HeyGen > Voices > copiar ID)

Uso:
    # Criar vídeo V1 com slides na pasta slides/v1/
    python tools/publishing/heygen_create_video.py --video 1 --slides slides/v1/

    # Criar todos os 6 vídeos (precisa das pastas slides/v1/ a slides/v6/)
    python tools/publishing/heygen_create_video.py --todos --slides slides/

    # Verificar status de um vídeo em processamento
    python tools/publishing/heygen_create_video.py --status VIDEO_ID

    # Listar avatares disponíveis na conta
    python tools/publishing/heygen_create_video.py --listar-avatares

    # Listar vozes PT-BR disponíveis
    python tools/publishing/heygen_create_video.py --listar-vozes

Formato das pastas de slides:
    slides/v1/slide_01.png
    slides/v1/slide_02.png
    ... (uma imagem por slide, nomeadas em ordem)

Como exportar slides do Gamma como PNG:
    1. Abra a apresentação no Gamma
    2. Clique em Export > PNG (baixa um ZIP com um PNG por slide)
    3. Descompacte na pasta slides/vN/ correspondente
    4. Renomeie para slide_01.png, slide_02.png, etc.

Formato dos scripts:
    Scripts em SecondBrain/projetos/132-estacao-samarco/content/cursos/digital/scripts-heygen/
    O parser busca blocos [SLIDE N — Título | X min] e extrai o texto de fala.
"""

import os
import re
import sys
import json
import time
import argparse
import urllib.request
import urllib.error
import urllib.parse
from pathlib import Path

# ── Config ────────────────────────────────────────────────────────────────────

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = ROOT / "SecondBrain/projetos/132-estacao-samarco/content/cursos/digital/scripts-heygen"

SCRIPT_FILES = {
    1: "v1-postura-profissional.md",
    2: "v2-custo-preco-lucro.md",
    3: "v3-ia-vender-divulgar.md",
    4: "v4-whatsapp-instagram.md",
    5: "v5-territorio-negocio.md",
    6: "v6-plano-30-dias.md",
}

HEYGEN_API_BASE = "https://api.heygen.com"

# ── Env ───────────────────────────────────────────────────────────────────────

def load_env():
    env_path = ROOT / ".env"
    env = {}
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, _, v = line.partition("=")
                env[k.strip()] = v.strip().strip('"').strip("'")
    env.update(os.environ)
    return env


def get_credentials():
    env = load_env()
    api_key = env.get("HEYGEN_API_KEY", "")
    avatar_id = env.get("HEYGEN_AVATAR_ID", "")
    voice_id = env.get("HEYGEN_VOICE_ID", "")
    if not api_key:
        print("ERRO: HEYGEN_API_KEY não encontrado no .env")
        print("Adicione ao .env: HEYGEN_API_KEY=sua_chave_aqui")
        sys.exit(1)
    return api_key, avatar_id, voice_id


# ── HeyGen API ────────────────────────────────────────────────────────────────

def heygen_request(method: str, path: str, api_key: str, body: dict = None) -> dict:
    url = f"{HEYGEN_API_BASE}{path}"
    data = json.dumps(body).encode("utf-8") if body else None
    req = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={
            "X-Api-Key": api_key,
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body_text = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HeyGen API erro {e.code}: {body_text}") from e


def upload_image_to_heygen(image_path: Path, api_key: str) -> str:
    """Faz upload de uma imagem PNG para o HeyGen e retorna a URL pública."""
    # HeyGen aceita upload via asset endpoint
    url = f"{HEYGEN_API_BASE}/v1/asset"
    with open(image_path, "rb") as f:
        image_data = f.read()

    import base64
    b64 = base64.b64encode(image_data).decode("utf-8")

    payload = {
        "name": image_path.name,
        "data": b64,
        "type": "image",
    }
    result = heygen_request("POST", "/v1/asset", api_key, payload)
    asset_url = result.get("data", {}).get("url") or result.get("url", "")
    if not asset_url:
        raise RuntimeError(f"Upload falhou para {image_path.name}: {result}")
    return asset_url


def list_avatars(api_key: str) -> list:
    result = heygen_request("GET", "/v2/avatars", api_key)
    return result.get("data", {}).get("avatars", [])


def list_voices(api_key: str, language: str = "Portuguese") -> list:
    result = heygen_request("GET", "/v2/voices", api_key)
    voices = result.get("data", {}).get("voices", [])
    if language:
        voices = [v for v in voices if language.lower() in v.get("language", "").lower()]
    return voices


def get_video_status(video_id: str, api_key: str) -> dict:
    return heygen_request("GET", f"/v1/video_status.get?video_id={video_id}", api_key)


def create_video(scenes: list, title: str, api_key: str) -> str:
    """
    Cria um vídeo no HeyGen com múltiplas cenas (uma por slide).
    Retorna o video_id.
    """
    payload = {
        "video_inputs": scenes,
        "test": False,
        "caption": False,
        "title": title,
        "dimension": {"width": 1920, "height": 1080},
    }
    result = heygen_request("POST", "/v2/video/generate", api_key, payload)
    video_id = result.get("data", {}).get("video_id", "")
    if not video_id:
        raise RuntimeError(f"Criação do vídeo falhou: {result}")
    return video_id


# ── Script Parser ─────────────────────────────────────────────────────────────

def parse_script(script_path: Path) -> list[dict]:
    """
    Lê o arquivo .md do script e extrai blocos por slide.
    Retorna lista de dicts: [{"slide": N, "titulo": "...", "texto": "..."}]

    Formato esperado nos arquivos:
        ## [SLIDE 1 — Título | 60 seg]
        Texto do avatar...

        ## [SLIDE 2 — Título | 3 min]
        Texto do avatar...
    """
    content = script_path.read_text(encoding="utf-8")
    # Separa no padrão ## [SLIDE N — ...]
    pattern = r"##\s*\[SLIDE\s+(\d+)[^\]]*\]\s*"
    parts = re.split(pattern, content)

    slides = []
    # parts[0] é o cabeçalho, depois alterna: número, texto, número, texto...
    i = 1
    while i + 1 < len(parts):
        slide_num = int(parts[i])
        raw_text = parts[i + 1].strip()
        # Remove linhas de separação ---
        raw_text = re.sub(r"\n---+\n?", "\n", raw_text)
        # Remove markdown bold/italic
        raw_text = re.sub(r"\*\*([^*]+)\*\*", r"\1", raw_text)
        raw_text = re.sub(r"\*([^*]+)\*", r"\1", raw_text)
        # Remove linhas de cabeçalho (##)
        raw_text = re.sub(r"^##.*$", "", raw_text, flags=re.MULTILINE)
        # Limpa espaços extras
        raw_text = re.sub(r"\n{3,}", "\n\n", raw_text).strip()
        slides.append({"slide": slide_num, "texto": raw_text})
        i += 2

    return slides


# ── Build Scenes ──────────────────────────────────────────────────────────────

def build_scenes(slides_data: list[dict], slide_images: list[str],
                 avatar_id: str, voice_id: str) -> list[dict]:
    """
    Constrói o array de cenas para o HeyGen API.
    slides_data: lista de {slide, texto} do parser
    slide_images: lista de URLs das imagens já uploaded (em ordem)
    """
    scenes = []
    for i, slide in enumerate(slides_data):
        bg_url = slide_images[i] if i < len(slide_images) else None
        texto = slide["texto"]
        if not texto:
            continue

        scene = {
            "character": {
                "type": "avatar",
                "avatar_id": avatar_id,
                "avatar_style": "normal",
                "scale": 0.35,        # avatar ocupa ~35% da altura
                "offset": {
                    "x": -0.38,       # posicionado na esquerda
                    "y": 0.35,        # ancorado na parte inferior
                },
            },
            "voice": {
                "type": "text",
                "input_text": texto,
                "voice_id": voice_id,
                "speed": 1.0,
            },
        }

        if bg_url:
            scene["background"] = {
                "type": "image",
                "url": bg_url,
                "fit": "cover",
            }
        else:
            # fallback: fundo azul escuro do programa
            scene["background"] = {
                "type": "color",
                "value": "#2C4459",
            }

        scenes.append(scene)

    return scenes


# ── Main Flows ────────────────────────────────────────────────────────────────

def cmd_listar_avatares(args):
    api_key, _, _ = get_credentials()
    avatares = list_avatars(api_key)
    print(f"\n{len(avatares)} avatares encontrados:\n")
    for a in avatares:
        print(f"  ID: {a.get('avatar_id')} | Nome: {a.get('avatar_name')} | Tipo: {a.get('avatar_type')}")
    print("\nColoque o ID desejado em HEYGEN_AVATAR_ID no .env")


def cmd_listar_vozes(args):
    api_key, _, _ = get_credentials()
    vozes = list_voices(api_key, language="Portuguese")
    print(f"\n{len(vozes)} vozes em português encontradas:\n")
    for v in vozes:
        print(f"  ID: {v.get('voice_id')} | Nome: {v.get('name')} | Gênero: {v.get('gender')} | Locale: {v.get('language')}")
    print("\nColoque o ID desejado em HEYGEN_VOICE_ID no .env")


def cmd_status(args):
    api_key, _, _ = get_credentials()
    result = get_video_status(args.status, api_key)
    data = result.get("data", {})
    status = data.get("status", "desconhecido")
    url = data.get("video_url", "")
    print(f"\nVídeo: {args.status}")
    print(f"Status: {status}")
    if url:
        print(f"URL: {url}")
    else:
        print("Ainda processando...")


def cmd_criar_video(video_num: int, slides_base: Path, api_key: str, avatar_id: str, voice_id: str):
    script_file = SCRIPTS_DIR / SCRIPT_FILES[video_num]
    slides_dir = slides_base / f"v{video_num}"

    print(f"\n{'='*60}")
    print(f"Criando Vídeo V{video_num}: {SCRIPT_FILES[video_num]}")
    print(f"{'='*60}")

    # 1. Parsear script
    if not script_file.exists():
        print(f"ERRO: Script não encontrado: {script_file}")
        return None

    print(f"  Parseando script...")
    slides_data = parse_script(script_file)
    print(f"  {len(slides_data)} slides encontrados no script")

    # 2. Coletar imagens dos slides
    slide_images_urls = []
    if slides_dir.exists():
        image_files = sorted(
            [f for f in slides_dir.iterdir() if f.suffix.lower() in (".png", ".jpg", ".jpeg")],
            key=lambda f: f.name,
        )
        print(f"  {len(image_files)} imagens de slides encontradas em {slides_dir}")

        if len(image_files) != len(slides_data):
            print(f"  AVISO: {len(image_files)} imagens para {len(slides_data)} blocos de script.")
            print(f"  Slides sem imagem usarão fundo colorido.")

        # Upload das imagens
        print(f"  Fazendo upload das imagens para o HeyGen...")
        for i, img_path in enumerate(image_files):
            print(f"    Upload {i+1}/{len(image_files)}: {img_path.name}...", end=" ", flush=True)
            try:
                url = upload_image_to_heygen(img_path, api_key)
                slide_images_urls.append(url)
                print("OK")
            except Exception as e:
                print(f"FALHOU: {e}")
                slide_images_urls.append(None)
    else:
        print(f"  AVISO: Pasta de slides não encontrada: {slides_dir}")
        print(f"  Vídeo será criado com fundo colorido (sem slides visuais)")

    # 3. Construir cenas
    print(f"  Construindo {len(slides_data)} cenas...")
    scenes = build_scenes(slides_data, slide_images_urls, avatar_id, voice_id)

    # 4. Criar vídeo
    video_titles = {
        1: "V1 - Postura Profissional e Atendimento - Estação Samarco",
        2: "V2 - Custo, Preço e Lucro - Estação Samarco",
        3: "V3 - IA para Vender e Divulgar - Estação Samarco",
        4: "V4 - WhatsApp e Instagram - Estação Samarco",
        5: "V5 - Seu Território é um Negócio - Estação Samarco",
        6: "V6 - Plano dos Próximos 30 Dias - Estação Samarco",
    }

    print(f"  Enviando para o HeyGen...")
    video_id = create_video(scenes, video_titles[video_num], api_key)
    print(f"  Vídeo em processamento!")
    print(f"  Video ID: {video_id}")
    print(f"  Acompanhe o status:")
    print(f"    python tools/publishing/heygen_create_video.py --status {video_id}")

    return video_id


def cmd_criar(args):
    api_key, avatar_id, voice_id = get_credentials()

    if not avatar_id:
        print("ERRO: HEYGEN_AVATAR_ID não definido no .env")
        print("Execute: python tools/publishing/heygen_create_video.py --listar-avatares")
        sys.exit(1)
    if not voice_id:
        print("ERRO: HEYGEN_VOICE_ID não definido no .env")
        print("Execute: python tools/publishing/heygen_create_video.py --listar-vozes")
        sys.exit(1)

    slides_base = Path(args.slides) if args.slides else ROOT / "output" / "slides"

    if args.todos:
        video_ids = {}
        for num in range(1, 7):
            vid = cmd_criar_video(num, slides_base, api_key, avatar_id, voice_id)
            if vid:
                video_ids[num] = vid
            time.sleep(2)  # intervalo entre criações

        print(f"\n{'='*60}")
        print(f"Todos os vídeos enviados para processamento:")
        for num, vid in video_ids.items():
            print(f"  V{num}: {vid}")
        print(f"\nVerifique o status no HeyGen Studio ou via --status VIDEO_ID")

    elif args.video:
        cmd_criar_video(args.video, slides_base, api_key, avatar_id, voice_id)


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Cria vídeos HeyGen para o Programa Estação Samarco"
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--video", type=int, choices=range(1, 7),
                       help="Número do vídeo a criar (1 a 6)")
    group.add_argument("--todos", action="store_true",
                       help="Criar todos os 6 vídeos")
    group.add_argument("--status", metavar="VIDEO_ID",
                       help="Verificar status de um vídeo")
    group.add_argument("--listar-avatares", action="store_true",
                       help="Listar avatares disponíveis na conta HeyGen")
    group.add_argument("--listar-vozes", action="store_true",
                       help="Listar vozes em português disponíveis")

    parser.add_argument("--slides", metavar="PASTA",
                        help="Pasta base com subpastas v1/ a v6/ contendo os PNGs dos slides")

    args = parser.parse_args()

    if args.listar_avatares:
        cmd_listar_avatares(args)
    elif args.listar_vozes:
        cmd_listar_vozes(args)
    elif args.status:
        cmd_status(args)
    else:
        cmd_criar(args)


if __name__ == "__main__":
    main()
