"""
generate_icons_leonardo.py — Gera biblioteca de ícones temáticos via Leonardo AI.

Otimizado para produzir ícones flat vetoriais coerentes (estilo uniforme, cor única,
fundo limpo) para biblioteca de KV de projetos NTICS.

📚 Ref: workflows/marketing/referencia/leonardo_ai_core.md — erros conhecidos e payloads

Uso:
    # A partir de um JSON com lista de temas + config
    python tools/media/generate_icons_leonardo.py \
        --config .tmp/icones_estacao_samarco.json \
        --output-dir .tmp/icones/

    # Ícone único
    python tools/media/generate_icons_leonardo.py \
        --theme "empreendedorismo" \
        --color "#F5A623" \
        --output-dir .tmp/icones/

Config JSON (recomendado):
    {
      "projeto": "Estação Samarco Empreendedorismo",
      "cor_destaque": "#F5A623",
      "estilo": "flat",        # flat · linear · gradient
      "modelo": "flux",        # lightning (rápido) · flux (qualidade) · phoenix
      "icones": [
        { "nome": "empreendedorismo", "descricao": "lightbulb com gráfico de crescimento subindo" },
        { "nome": "inteligencia_artificial", "descricao": "chip de processador com conexões neurais" },
        { "nome": "culinaria_sustentavel", "descricao": "panela com folha verde saindo" },
        { "nome": "beleza_estetica", "descricao": "espelho redondo com pincel de maquiagem" },
        { "nome": "atendimento_cliente", "descricao": "headset com chat bubble" },
        { "nome": "marketing_digital", "descricao": "megafone com símbolo de rede social" },
        ...
      ]
    }

Output:
    {output_dir}/empreendedorismo.png
    {output_dir}/inteligencia_artificial.png
    ...
    {output_dir}/manifest.json  (lista completa com generation_ids e prompts)

Após gerar, vetorize com:
    python tools/media/vectorize_image_illustrator.py --input .tmp/icones/ --output-dir .tmp/icones/svg/

Dependências: requests, python-dotenv. LEONARDO_API_KEY no .env.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

import requests
from dotenv import load_dotenv

# Windows Unicode
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

load_dotenv()

BASE_URL_V1 = "https://cloud.leonardo.ai/api/rest/v1"

# Modelos recomendados para ícones (não usar nano-banana-2 que é foto-realista)
MODELS = {
    "flux":      "b2614463-296c-462a-9586-aafdb8f00e36",  # Flux Dev — ótimo para ícones limpos
    "lightning": "b24e16ff-06e3-43eb-8d33-4416c2d75876",  # Lightning XL — rápido
    "phoenix":   "de7d3faf-762f-48e0-b3b7-9d0ac3a3fcf3",  # Phoenix 1.0 — flagship (mais caro)
}
DEFAULT_MODEL = "flux"


PROMPT_TEMPLATES = {
    "flat": (
        "flat vector icon of {theme}, single solid color {color}, "
        "minimalist geometric design, centered composition, "
        "isolated on pure white background, clean bold outline, "
        "uniform thick strokes, modern icon, simple shape, "
        "no text, no letters, no numbers, no people, no faces, "
        "no shadows, no gradients, no 3D, no photorealism"
    ),
    "linear": (
        "linear outline icon of {theme}, monochromatic stroke color {color}, "
        "minimalist line art, centered, isolated on pure white background, "
        "uniform 3px stroke weight, rounded line caps, no fill, "
        "modern icon design, thin geometric style, "
        "no text, no people, no shadows, no photorealism"
    ),
    "gradient": (
        "flat icon of {theme} with subtle gradient in {color} tones, "
        "minimalist modern design, centered, isolated on pure white background, "
        "clean geometric shapes, soft gradient fill, "
        "no text, no people, no shadows, no photorealism"
    ),
}

NEGATIVE_PROMPT = (
    "photorealistic, photograph, realistic, 3D render, shadow, reflection, "
    "text, letter, number, watermark, logo, signature, brand, "
    "multiple icons, icon grid, busy composition, detailed background, "
    "people, faces, human figures, hands with details, cluttered"
)


def build_prompt(theme: str, description: str, color_hex: str, style: str = "flat") -> str:
    """Monta prompt específico para um ícone."""
    template = PROMPT_TEMPLATES.get(style, PROMPT_TEMPLATES["flat"])
    # Detalha o tema com a descrição curta
    full_theme = f"{theme} — {description}" if description else theme
    return template.format(theme=full_theme, color=color_hex)


def start_generation(api_key: str, prompt: str, model_key: str = DEFAULT_MODEL,
                     width: int = 1024, height: int = 1024) -> str:
    """Inicia geração. Retorna generation_id."""
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": f"Bearer {api_key}",
    }
    payload = {
        "prompt": prompt,
        "negative_prompt": NEGATIVE_PROMPT,
        "modelId": MODELS[model_key],
        "width": width,
        "height": height,
        "num_images": 1,
        "public": False,
        "alchemy": False,       # ícone não precisa de alchemy
        "guidance_scale": 7,    # maior fidelidade ao prompt
    }
    resp = requests.post(f"{BASE_URL_V1}/generations", headers=headers, json=payload, timeout=30)
    resp.raise_for_status()
    return resp.json()["sdGenerationJob"]["generationId"]


def poll_generation(api_key: str, generation_id: str, max_wait: int = 120) -> str:
    """Aguarda conclusão. Retorna URL da imagem."""
    headers = {"accept": "application/json", "authorization": f"Bearer {api_key}"}
    url = f"{BASE_URL_V1}/generations/{generation_id}"
    waited, interval = 0, 3

    while waited < max_wait:
        resp = requests.get(url, headers=headers, timeout=30)
        resp.raise_for_status()
        job = resp.json().get("generations_by_pk", {})
        status = job.get("status", "")
        if status == "COMPLETE":
            imgs = job.get("generated_images", [])
            if imgs:
                return imgs[0]["url"]
            raise RuntimeError("Geração completa mas sem imagens")
        if status == "FAILED":
            raise RuntimeError(f"Geração falhou: {job}")
        time.sleep(interval)
        waited += interval
        print(f"    ⏳ Aguardando... ({waited}s)")
    raise TimeoutError(f"Timeout após {max_wait}s")


def download(url: str, output_path: Path) -> Path:
    """Baixa imagem."""
    resp = requests.get(url, timeout=60)
    resp.raise_for_status()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "wb") as f:
        f.write(resp.content)
    return output_path


def generate_one_icon(api_key: str, theme: str, description: str, color_hex: str,
                      style: str, model_key: str, output_path: Path) -> dict:
    """Gera um ícone único."""
    prompt = build_prompt(theme, description, color_hex, style)
    print(f"\n🎨 Gerando ícone: {theme}")
    print(f"   Prompt: {prompt[:100]}...")

    gen_id = start_generation(api_key, prompt, model_key)
    print(f"   Generation ID: {gen_id}")

    image_url = poll_generation(api_key, gen_id)
    print(f"   ✓ Pronto: {image_url[:70]}...")

    download(image_url, output_path)
    print(f"   ✓ Salvo: {output_path}")

    return {
        "tema": theme,
        "descricao": description,
        "generation_id": gen_id,
        "image_url": image_url,
        "local_path": str(output_path),
        "prompt": prompt,
        "color": color_hex,
        "style": style,
        "model": model_key,
    }


def generate_library(config: dict, api_key: str, output_dir: Path) -> list[dict]:
    """Gera biblioteca completa a partir de config."""
    cor = config.get("cor_destaque", "#000000")
    estilo = config.get("estilo", "flat")
    modelo = config.get("modelo", DEFAULT_MODEL)
    icones = config.get("icones", [])

    if modelo not in MODELS:
        print(f"[AVISO] Modelo '{modelo}' desconhecido, usando '{DEFAULT_MODEL}'")
        modelo = DEFAULT_MODEL

    print(f"\n📦 Projeto: {config.get('projeto', 'sem nome')}")
    print(f"   Cor destaque: {cor}")
    print(f"   Estilo: {estilo}")
    print(f"   Modelo Leonardo: {modelo}")
    print(f"   Total de ícones: {len(icones)}")

    output_dir.mkdir(parents=True, exist_ok=True)
    results = []

    for i, icone in enumerate(icones, 1):
        nome = icone["nome"]
        descricao = icone.get("descricao", "")
        output_path = output_dir / f"{nome}.png"

        print(f"\n[{i}/{len(icones)}] {nome}")

        try:
            result = generate_one_icon(
                api_key, nome, descricao, cor, estilo, modelo, output_path
            )
            results.append(result)
        except Exception as e:
            print(f"   ❌ Erro: {e}")
            results.append({
                "tema": nome,
                "erro": str(e),
            })

    # Salva manifest
    manifest_path = output_dir / "manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump({
            "projeto": config.get("projeto"),
            "cor_destaque": cor,
            "estilo": estilo,
            "modelo": modelo,
            "total_solicitado": len(icones),
            "total_gerado": sum(1 for r in results if "local_path" in r),
            "icones": results,
        }, f, indent=2, ensure_ascii=False)
    print(f"\n📄 Manifest: {manifest_path}")

    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="Gera biblioteca de ícones via Leonardo AI.")
    parser.add_argument("--config", help="Caminho JSON de config (lista de ícones)")
    parser.add_argument("--theme", help="Tema único (sem config)")
    parser.add_argument("--description", default="", help="Descrição visual curta do ícone")
    parser.add_argument("--color", default="#000000", help="Cor hex (padrão: preto)")
    parser.add_argument("--style", default="flat", choices=["flat", "linear", "gradient"])
    parser.add_argument("--model", default=DEFAULT_MODEL, choices=list(MODELS.keys()))
    parser.add_argument("--output-dir", default=".tmp/icones", help="Pasta de saída")
    args = parser.parse_args()

    api_key = os.getenv("LEONARDO_API_KEY")
    if not api_key:
        print("[ERRO] LEONARDO_API_KEY não configurada no .env")
        print("Obter chave: https://app.leonardo.ai/settings/api-keys")
        sys.exit(1)

    output_dir = Path(args.output_dir)

    if args.config:
        config_path = Path(args.config)
        if not config_path.exists():
            print(f"[ERRO] Config não encontrado: {config_path}")
            sys.exit(1)
        with config_path.open("r", encoding="utf-8") as f:
            config = json.load(f)
        results = generate_library(config, api_key, output_dir)
        ok = sum(1 for r in results if "local_path" in r)
        total = len(results)
        print(f"\n{'='*60}\n✅ Concluído: {ok}/{total} ícones gerados")
        print(f"📁 Output: {output_dir}")
        print(f"💡 Próximo passo: vetorize com")
        print(f"   python tools/media/vectorize_image_illustrator.py --input {output_dir} --output-dir {output_dir}/svg")

    elif args.theme:
        safe_name = args.theme.lower().replace(" ", "_")
        output_path = output_dir / f"{safe_name}.png"
        result = generate_one_icon(
            api_key, args.theme, args.description, args.color, args.style, args.model, output_path
        )
        print(f"\n✅ Ícone gerado: {output_path}")
        print(json.dumps(result, indent=2, ensure_ascii=False))

    else:
        parser.error("Informe --config OU --theme")


if __name__ == "__main__":
    main()
