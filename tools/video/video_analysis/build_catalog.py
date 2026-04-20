"""
build_catalog.py — Consolida análises individuais num catálogo pesquisável.

Lê todos os analysis.json de uma pasta e gera um catalog.json unificado,
indexado por tags, tipo de cena e score de qualidade.

Usage:
  python tools/video_analysis/build_catalog.py \
    --analysis-dir .tmp/video-analysis/ \
    --output .tmp/video-analysis/catalog.json

  # Filtrar por score mínimo
  python tools/video_analysis/build_catalog.py \
    --analysis-dir .tmp/video-analysis/ \
    --min-score 6

Output:
  catalog.json com todos os segmentos + índices de busca
"""

import argparse
import json
import os
import sys
from collections import defaultdict
from pathlib import Path


def find_analysis_files(analysis_dir: str) -> list:
    """Encontra todos os analysis.json na pasta."""
    files = []
    for entry in os.scandir(analysis_dir):
        if entry.is_dir():
            analysis_path = os.path.join(entry.path, "analysis.json")
            if os.path.exists(analysis_path):
                files.append(analysis_path)
    return sorted(files)


def build_catalog(analysis_files: list, min_score: int = 0) -> dict:
    """Consolida análises num catálogo unificado."""
    all_segments = []
    videos = []
    tag_index = defaultdict(list)
    type_index = defaultdict(list)

    for filepath in analysis_files:
        with open(filepath, "r", encoding="utf-8") as f:
            analysis = json.load(f)

        video_info = {
            "arquivo": analysis.get("arquivo", "?"),
            "duracao": analysis.get("duracao", "?"),
            "resolucao": analysis.get("resolucao", "?"),
            "resumo": analysis.get("resumo", ""),
            "total_segmentos": analysis.get("total_segmentos", 0),
            "caminho_analysis": filepath,
        }
        videos.append(video_info)

        # Carregar metadados para pegar caminho original
        metadata_path = os.path.join(os.path.dirname(filepath), "metadata.json")
        caminho_original = ""
        if os.path.exists(metadata_path):
            with open(metadata_path, "r") as mf:
                meta = json.load(mf)
                caminho_original = meta.get("caminho", "")

        for seg in analysis.get("segmentos", []):
            score = seg.get("score", 0)
            if score < min_score:
                continue

            seg["arquivo_origem"] = analysis.get("arquivo", "?")
            seg["caminho_origem"] = caminho_original

            all_segments.append(seg)

            # Indexar por tag
            for tag in seg.get("tags", []):
                tag_lower = tag.lower().strip()
                tag_index[tag_lower].append(seg["id"])

            # Indexar por tipo
            tipo = seg.get("tipo", "outro").lower()
            type_index[tipo].append(seg["id"])

    # Ordenar segmentos por score (maior primeiro)
    all_segments.sort(key=lambda s: s.get("score", 0), reverse=True)

    catalog = {
        "total_videos": len(videos),
        "total_segmentos": len(all_segments),
        "videos": videos,
        "segmentos": all_segments,
        "indice_tags": dict(tag_index),
        "indice_tipos": dict(type_index),
        "tags_disponiveis": sorted(tag_index.keys()),
        "tipos_disponiveis": sorted(type_index.keys()),
    }

    return catalog


def search_catalog(catalog: dict, tags: list = None, tipo: str = None,
                   min_score: int = 0, limit: int = 20) -> list:
    """Busca segmentos no catálogo por critérios."""
    results = []

    for seg in catalog.get("segmentos", []):
        if seg.get("score", 0) < min_score:
            continue

        if tipo and seg.get("tipo", "").lower() != tipo.lower():
            continue

        if tags:
            seg_tags = {t.lower() for t in seg.get("tags", [])}
            if not any(t.lower() in seg_tags for t in tags):
                continue

        results.append(seg)

        if len(results) >= limit:
            break

    return results


def main():
    parser = argparse.ArgumentParser(description="Consolida análises num catálogo pesquisável")
    parser.add_argument("--analysis-dir", required=True, help="Pasta com subpastas de análise")
    parser.add_argument("--output", default=None, help="Caminho do catalog.json")
    parser.add_argument("--min-score", type=int, default=0, help="Score mínimo para incluir (default: 0)")
    args = parser.parse_args()

    analysis_dir = os.path.abspath(args.analysis_dir)
    output_path = args.output or os.path.join(analysis_dir, "catalog.json")

    analysis_files = find_analysis_files(analysis_dir)
    if not analysis_files:
        print(f"[ERRO] Nenhum analysis.json encontrado em {analysis_dir}", file=sys.stderr)
        sys.exit(1)

    print(f"Consolidando {len(analysis_files)} análises...")
    catalog = build_catalog(analysis_files, args.min_score)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(catalog, f, ensure_ascii=False, indent=2)

    print(f"\n[OK] Catalogo gerado com {catalog['total_segmentos']} segmentos de {catalog['total_videos']} videos")
    print(f"  Tags disponíveis: {', '.join(catalog['tags_disponiveis'][:15])}...")
    print(f"  Tipos: {', '.join(catalog['tipos_disponiveis'])}")
    print(f"  Output: {output_path}")

    json.dump({
        "status": "ok",
        "total_videos": catalog["total_videos"],
        "total_segmentos": catalog["total_segmentos"],
        "output": output_path
    }, sys.stdout)


if __name__ == "__main__":
    main()
