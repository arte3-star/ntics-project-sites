"""
assemble_timeline.py — Monta timeline temática a partir do catálogo + narração.

Dado um tema, consulta o catálogo de segmentos, seleciona os melhores clips
para cada fase do roteiro NTICS (5 fases) e gera um timeline.json.

Usage:
  python tools/video_analysis/assemble_timeline.py \
    --catalog .tmp/video-analysis/catalog.json \
    --theme "impacto social" \
    --duration 60 \
    --output .tmp/video-assembly/impacto-social/timeline.json

  # Com narração (sincroniza B-roll com áudio)
  python tools/video_analysis/assemble_timeline.py \
    --catalog .tmp/video-analysis/catalog.json \
    --narration .tmp/video-assembly/narration.mp3 \
    --srt .tmp/video-assembly/narration.srt \
    --theme "impacto social" \
    --output .tmp/video-assembly/impacto-social/timeline.json

Output:
  timeline.json — pronto para render_video.py processar
"""

import argparse
import json
import os
import sys


# Estrutura de 5 fases do roteiro NTICS (do workflow roteiro_edicao_video.md)
FASES_ROTEIRO = [
    {
        "id": "abertura",
        "nome": "Abertura",
        "tempo_inicio": 0,
        "tempo_fim": 12,
        "descricao": "Apresentar projeto + gancho visual forte",
        "tags_preferidas": ["evento", "abertura", "paisagem", "fachada", "plateia"],
        "tipos_preferidos": ["b-roll", "paisagem", "plateia"],
        "transicao_entrada": "fade_in",
    },
    {
        "id": "proposito",
        "nome": "Propósito",
        "tempo_inicio": 12,
        "tempo_fim": 25,
        "descricao": "Por que o projeto existe",
        "tags_preferidas": ["depoimento", "impacto", "comunidade", "necessidade"],
        "tipos_preferidos": ["depoimento", "b-roll", "atividade"],
        "transicao_entrada": "crossfade",
    },
    {
        "id": "como",
        "nome": "Como vai acontecer",
        "tempo_inicio": 25,
        "tempo_fim": 42,
        "descricao": "Frentes, oficinas, números, atividades",
        "tags_preferidas": ["atividade", "oficina", "sala-de-aula", "workshop", "ação"],
        "tipos_preferidos": ["atividade", "b-roll", "bastidores"],
        "transicao_entrada": "crossfade",
    },
    {
        "id": "convite",
        "nome": "Convite/Chamada",
        "tempo_inicio": 42,
        "tempo_fim": 52,
        "descricao": "CTA — inscrição, abertura, acompanhar",
        "tags_preferidas": ["pessoas", "sorriso", "grupo", "interação"],
        "tipos_preferidos": ["b-roll", "plateia", "atividade"],
        "transicao_entrada": "crossfade",
    },
    {
        "id": "fechamento",
        "nome": "Fechamento",
        "tempo_inicio": 52,
        "tempo_fim": 60,
        "descricao": "Visão positiva + cartela final",
        "tags_preferidas": ["grupo", "encerramento", "aplausos", "celebração"],
        "tipos_preferidos": ["b-roll", "plateia"],
        "transicao_entrada": "crossfade",
    },
]


def scale_phases(fases: list, target_duration: int) -> list:
    """Escala as fases proporcionalmente para a duração alvo."""
    original_duration = fases[-1]["tempo_fim"]
    ratio = target_duration / original_duration

    scaled = []
    for fase in fases:
        f = dict(fase)
        f["tempo_inicio"] = round(fase["tempo_inicio"] * ratio, 1)
        f["tempo_fim"] = round(fase["tempo_fim"] * ratio, 1)
        scaled.append(f)

    return scaled


def score_segment_for_phase(segment: dict, fase: dict, theme: str) -> float:
    """Calcula score de compatibilidade entre segmento e fase."""
    score = segment.get("score", 5)

    # Bonus por tag match
    seg_tags = {t.lower() for t in segment.get("tags", [])}
    preferred_tags = {t.lower() for t in fase.get("tags_preferidas", [])}
    tag_overlap = len(seg_tags & preferred_tags)
    score += tag_overlap * 2

    # Bonus por tipo match
    tipo = segment.get("tipo", "outro").lower()
    if tipo in [t.lower() for t in fase.get("tipos_preferidos", [])]:
        score += 3

    # Bonus por tema no texto
    theme_words = theme.lower().split()
    desc = (segment.get("descricao_visual", "") + " " + " ".join(segment.get("tags", []))).lower()
    for word in theme_words:
        if word in desc:
            score += 1

    return score


def select_segments(catalog: dict, fases: list, theme: str, max_clip_duration: float = 5.0) -> list:
    """Seleciona multiplos clips curtos por fase para montagem dinamica.

    Em vez de 1 clip longo por fase, preenche cada fase com 2-4 clips de
    3-5s cada, priorizando variedade visual e qualidade tecnica.
    """
    segments = catalog.get("segmentos", [])
    used_ids = set()
    timeline_entries = []

    for fase in fases:
        fase_duration = fase["tempo_fim"] - fase["tempo_inicio"]
        current_time = fase["tempo_inicio"]

        # Calcular score de cada segmento para esta fase
        candidates = []
        for seg in segments:
            if seg["id"] in used_ids:
                continue
            compatibility = score_segment_for_phase(seg, fase, theme)
            candidates.append((compatibility, seg))

        # Ordenar por score de compatibilidade (maior primeiro)
        candidates.sort(key=lambda x: x[0], reverse=True)

        clip_index = 0
        while current_time < fase["tempo_fim"] and candidates:
            # Pegar proximo melhor candidato
            if clip_index >= len(candidates):
                break
            best_score, best_seg = candidates[clip_index]
            clip_index += 1
            used_ids.add(best_seg["id"])

            # Calcular duracao do clip (3-5s, maximo ate fim da fase)
            remaining = fase["tempo_fim"] - current_time
            clip_dur = min(max_clip_duration, remaining)
            if clip_dur < 2.0:
                break

            # Determinar in/out dentro do segmento original
            seg_in = best_seg.get("in", "00:00.0")
            seg_out = best_seg.get("out", "00:15.0")

            # Usar inicio do segmento + clip_dur (pegar o melhor trecho)
            from_time = parse_ts(seg_in)
            to_time = min(from_time + clip_dur, parse_ts(seg_out))
            actual_dur = to_time - from_time
            if actual_dur < 1.5:
                continue

            entry = {
                "fase": fase["id"],
                "fase_nome": fase["nome"],
                "tempo_inicio": round(current_time, 1),
                "tempo_fim": round(current_time + actual_dur, 1),
                "source_video": best_seg.get("caminho_origem", ""),
                "source_arquivo": best_seg.get("arquivo_origem", ""),
                "segment_id": best_seg["id"],
                "segment_in": format_ts(from_time),
                "segment_out": format_ts(to_time),
                "descricao": best_seg.get("descricao_visual", ""),
                "transicao": "crossfade" if current_time > fase["tempo_inicio"] else fase.get("transicao_entrada", "cut"),
                "score_compatibilidade": best_score,
            }
            timeline_entries.append(entry)
            current_time += actual_dur

        if not any(e["fase"] == fase["id"] for e in timeline_entries):
            timeline_entries.append({
                "fase": fase["id"],
                "fase_nome": fase["nome"],
                "tempo_inicio": fase["tempo_inicio"],
                "tempo_fim": fase["tempo_fim"],
                "source_video": "[PREENCHER]",
                "segment_id": None,
                "descricao": f"Sem segmento encontrado para: {fase['descricao']}",
                "transicao": fase.get("transicao_entrada", "cut"),
            })

    return timeline_entries


def parse_ts(ts: str) -> float:
    """Converte timestamp MM:SS.ms para segundos."""
    parts = ts.replace(",", ".").split(":")
    if len(parts) == 2:
        return float(parts[0]) * 60 + float(parts[1])
    elif len(parts) == 3:
        return float(parts[0]) * 3600 + float(parts[1]) * 60 + float(parts[2])
    return float(ts)


def format_ts(seconds: float) -> str:
    """Converte segundos para MM:SS.s"""
    m = int(seconds // 60)
    s = seconds % 60
    return f"{m:02d}:{s:04.1f}"


def main():
    parser = argparse.ArgumentParser(description="Monta timeline temática a partir do catálogo")
    parser.add_argument("--catalog", required=True, help="Caminho do catalog.json")
    parser.add_argument("--theme", required=True, help="Tema do vídeo (ex: 'impacto social')")
    parser.add_argument("--duration", type=int, default=60, help="Duração alvo em segundos (default: 60)")
    parser.add_argument("--narration", default=None, help="Caminho do áudio de narração (.mp3)")
    parser.add_argument("--srt", default=None, help="Caminho das legendas (.srt)")
    parser.add_argument("--output", required=True, help="Caminho do timeline.json")
    parser.add_argument("--projeto", default="", help="Nome do projeto (para motion graphics)")
    parser.add_argument("--patrocinador", default="", help="Nome do patrocinador (para cartela)")
    args = parser.parse_args()

    # Carregar catálogo
    with open(args.catalog, "r", encoding="utf-8") as f:
        catalog = json.load(f)

    print(f"Catálogo: {catalog['total_segmentos']} segmentos de {catalog['total_videos']} vídeos")

    # Escalar fases para duração alvo
    fases = scale_phases(FASES_ROTEIRO, args.duration)

    # Selecionar segmentos
    print(f"Selecionando segmentos para tema '{args.theme}'...")
    timeline_entries = select_segments(catalog, fases, args.theme)

    # Montar timeline completo
    timeline = {
        "tema": args.theme,
        "duracao_alvo": args.duration,
        "formato": "9:16",
        "timeline": timeline_entries,
        "narration": {
            "audio_path": args.narration,
            "srt_path": args.srt,
        } if args.narration else None,
        "motion_graphics": {
            "titulo_card": {
                "projeto": args.projeto or args.theme,
                "patrocinador": args.patrocinador,
            },
            "end_card": {
                "realizacao": "NTICS Projetos",
                "redes": "@nticsprojetos",
            },
            "lower_thirds": [],
        },
    }

    # Criar diretório de saída
    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(timeline, f, ensure_ascii=False, indent=2)

    # Resumo
    filled = sum(1 for e in timeline_entries if e.get("segment_id"))
    total = len(timeline_entries)
    print(f"\n[OK] Timeline montada: {filled}/{total} fases preenchidas")

    if filled < total:
        missing = [e["fase_nome"] for e in timeline_entries if not e.get("segment_id")]
        print(f"  [AVISO] Fases sem clip: {', '.join(missing)}")

    print(f"  Output: {args.output}")
    print(f"\n[CHECKPOINT] Revise a timeline antes de renderizar!")

    json.dump({"status": "ok", "fases_preenchidas": filled, "total_fases": total, "output": args.output}, sys.stdout)


if __name__ == "__main__":
    main()
