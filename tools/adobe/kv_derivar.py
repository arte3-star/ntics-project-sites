"""
KV Derivar Projeto (Subbrand)

A partir do manual oficial de marca do cliente, deriva um KV próprio para o
sub-programa/projeto: gera logo, variações, biblioteca de ícones temáticos
(via Leonardo AI) e manual PDF de aplicação visual.

Workflow: workflows/escritorio-projetos/kv_derivar_projeto.md
Skill:    .claude/skills/kv-derivar/SKILL.md

Uso:
    python tools/adobe/kv_derivar.py --config path/config.json

Config JSON (exemplo):
    {
      "projeto": {
        "nome": "Estação Samarco",
        "codigo_ntics": 132,
        "sem_regua_minc": true
      },
      "manual_cliente_pdf": "path/manual_samarco.pdf",
      "icones": {
        "quantidade": 12,
        "estilo": "flat",
        "cor_destaque": "#F5A623",
        "temas": [
          "empreendedorismo",
          "inteligência artificial",
          "culinária sustentável",
          "beleza e estética",
          "marketing digital",
          "atendimento ao cliente",
          ...
        ]
      },
      "hierarquia_marcas": {
        "soberana": "Estação Samarco",
        "apresenta": "Samarco corporativa",
        "realizacao": "NTICS"
      },
      "output_dir": "KV ESTACAO SAMARCO EMPREENDEDORISMO/",
      "drive_folder_id": "1JwiIVdOKFc2znnRqkPuOJOj2AvtfvED5"
    }

Output:
    {output_dir}/logos/*.ai, *.png
    {output_dir}/icones/*.svg, *.png
    {output_dir}/manual.pdf

Status: STUB — implementação base a fazer.
Depende de: Leonardo AI, Adobe Illustrator, tools/media/vectorize_image_illustrator.py
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def extract_manual_cliente(pdf_path: Path) -> dict:
    """
    Extrai paleta, tipografia e regras do manual PDF.

    TODO:
      1. PyMuPDF (fitz) para extrair texto e imagens
      2. OCR se necessário (pytesseract ou via Claude Vision API)
      3. Regex/heurística para capturar:
         - Cores CMYK (padrão "C 100 M 65 Y 0 K 45" ou hex)
         - Tipografia (nomes de família)
         - Área de proteção do logo
      4. Retornar dict estruturado
    """
    raise NotImplementedError("extract_manual_cliente — implementar extração do manual cliente.")


def generate_logo_projeto(config: dict, cliente_data: dict) -> dict:
    """
    Gera logo do projeto em Illustrator derivando do cliente.

    TODO: criar jsx/kv_logo_projeto.jsx
    """
    raise NotImplementedError("generate_logo_projeto — implementar geração de logo via Illustrator.")


def generate_icone_library(config: dict, cliente_data: dict | None = None) -> list:
    """
    Gera biblioteca de ícones via Leonardo AI.

    Implementação: delega para tools/media/generate_icons_leonardo.py

    Após gerar os PNGs, o caller deve chamar vectorize_image_illustrator.py
    para converter PNG → SVG.
    """
    import subprocess
    import sys as _sys

    icones_cfg = config.get("icones", {})
    projeto = config.get("projeto", {}).get("nome", "sem-nome")
    output_dir = Path(config.get("output_dir", ".tmp/kv")) / "icones"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Montar config para o tool específico
    leonardo_config = {
        "projeto": projeto,
        "cor_destaque": icones_cfg.get("cor_destaque", "#000000"),
        "estilo": icones_cfg.get("estilo", "flat"),
        "modelo": icones_cfg.get("modelo", "flux"),
        "icones": icones_cfg.get("temas", []),
    }

    # Salva config temporário e chama o tool
    tmp_config = output_dir / "_leonardo_config.json"
    with tmp_config.open("w", encoding="utf-8") as f:
        json.dump(leonardo_config, f, indent=2, ensure_ascii=False)

    script = Path(__file__).parent.parent / "media" / "generate_icons_leonardo.py"
    cmd = [
        _sys.executable, str(script),
        "--config", str(tmp_config),
        "--output-dir", str(output_dir),
    ]
    print(f"[kv-derivar] Chamando: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)

    # Ler manifest gerado
    manifest_path = output_dir / "manifest.json"
    with manifest_path.open("r", encoding="utf-8") as f:
        manifest = json.load(f)

    return manifest.get("icones", [])


def build_manual_pdf(config: dict, logo_paths: dict, icones: list) -> Path:
    """Monta o manual PDF A4 horizontal com todas as seções."""
    raise NotImplementedError("build_manual_pdf — implementar via Illustrator ou ReportLab.")


def derive_kv(config: dict) -> dict:
    """Orquestra a geração completa do KV."""
    manual_path = Path(config["manual_cliente_pdf"])
    cliente_data = extract_manual_cliente(manual_path)
    logo_paths = generate_logo_projeto(config, cliente_data)
    icones = generate_icone_library(config, cliente_data)
    manual_pdf = build_manual_pdf(config, logo_paths, icones)
    return {
        "logos": logo_paths,
        "icones": icones,
        "manual": str(manual_pdf),
        "drive_folder": config.get("drive_folder_id"),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Deriva KV do projeto a partir do manual cliente.")
    parser.add_argument("--config", required=True, help="Caminho JSON de config.")
    args = parser.parse_args()

    config_path = Path(args.config)
    if not config_path.exists():
        print(f"[ERRO] Config não encontrado: {config_path}")
        sys.exit(1)

    with config_path.open("r", encoding="utf-8") as f:
        config = json.load(f)

    result = derive_kv(config)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
