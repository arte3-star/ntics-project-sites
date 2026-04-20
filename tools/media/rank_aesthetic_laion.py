"""Rankeia fotos por qualidade estética usando LAION Aesthetic Predictor v2.

Implementacao direta do predictor oficial (Schuhmann/LAION):
  https://github.com/christophschuhmann/improved-aesthetic-predictor

Arquitetura: CLIP ViT-L/14 embedding (768d) -> MLP 5 camadas -> score 1-10
Modelo treinado em ~400k fotos com ratings humanos (SAC + LOGOs + AVA1 combinados).

Uso:
    python rank_aesthetic_laion.py --folder "path/to/photos" --output "scores.csv"
    python rank_aesthetic_laion.py --folder "path/to/photos" --rename

Score interpretation:
  >=7.0  excelente (publicavel)
  5.5-7  mediano
  <5.5   descartavel
"""
from __future__ import annotations

import argparse
import csv
import re
import urllib.request
from pathlib import Path

import torch
import torch.nn as nn
from PIL import Image
from transformers import CLIPModel, CLIPProcessor

CLIP_MODEL_ID = "openai/clip-vit-large-patch14"
WEIGHTS_URL = "https://github.com/christophschuhmann/improved-aesthetic-predictor/raw/main/sac%2Blogos%2Bava1-l14-linearMSE.pth"
WEIGHTS_NAME = "sac+logos+ava1-l14-linearMSE.pth"
EXTS = {".jpg", ".jpeg", ".png", ".webp"}


class MLP(nn.Module):
    """Arquitetura MLP do LAION Aesthetic Predictor v2."""

    def __init__(self, input_size: int = 768):
        super().__init__()
        self.layers = nn.Sequential(
            nn.Linear(input_size, 1024),
            nn.Dropout(0.2),
            nn.Linear(1024, 128),
            nn.Dropout(0.2),
            nn.Linear(128, 64),
            nn.Dropout(0.1),
            nn.Linear(64, 16),
            nn.Linear(16, 1),
        )

    def forward(self, x):
        return self.layers(x)


def get_weights_path() -> Path:
    cache = Path.home() / ".cache" / "laion-aesthetic"
    cache.mkdir(parents=True, exist_ok=True)
    target = cache / WEIGHTS_NAME
    if not target.exists():
        print(f"[LAION] Baixando pesos MLP ({WEIGHTS_URL})...")
        urllib.request.urlretrieve(WEIGHTS_URL, target)
        print(f"[LAION] Pesos salvos em {target}")
    return target


def load_model():
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"[LAION] Device: {device}")

    print(f"[LAION] Carregando CLIP {CLIP_MODEL_ID}...")
    clip_model = CLIPModel.from_pretrained(CLIP_MODEL_ID).to(device)
    clip_model.eval()
    processor = CLIPProcessor.from_pretrained(CLIP_MODEL_ID)

    print("[LAION] Carregando MLP head...")
    mlp = MLP(768).to(device)
    state = torch.load(get_weights_path(), map_location=device, weights_only=True)
    mlp.load_state_dict(state)
    mlp.eval()

    return clip_model, processor, mlp, device


@torch.no_grad()
def score_image(clip_model, processor, mlp, device, path: Path) -> float:
    img = Image.open(path).convert("RGB")
    inputs = processor(images=img, return_tensors="pt").to(device)
    vision_out = clip_model.vision_model(pixel_values=inputs["pixel_values"])
    pooled = vision_out.pooler_output  # [1, 1024]
    features = clip_model.visual_projection(pooled)  # [1, 768]
    features = features / features.norm(dim=-1, keepdim=True)  # L2 normalize
    score = mlp(features)
    return float(score.item())


def iter_images(folder: Path):
    for p in sorted(folder.iterdir()):
        if p.is_file() and p.suffix.lower() in EXTS:
            yield p


def rename_with_rank(folder: Path, results: list[tuple[Path, float]]):
    """Renomeia arquivos com prefixo NN_ baseado no score (maior score = 01)."""
    results_sorted = sorted(results, key=lambda x: -x[1])
    width = max(2, len(str(len(results_sorted))))

    # Passo 1: temp
    for idx, (path, _) in enumerate(results_sorted, 1):
        body = re.sub(r"^\d+_", "", path.name)
        path.rename(path.with_name(f".tmp_{idx:04d}_{body}"))

    # Passo 2: final
    for p in sorted(folder.iterdir()):
        if p.name.startswith(".tmp_"):
            m = re.match(r"\.tmp_(\d+)_(.+)", p.name)
            if m:
                final = f"{int(m.group(1)):0{width}d}_{m.group(2)}"
                p.rename(folder / final)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--folder", required=True, type=Path)
    ap.add_argument("--output", type=Path, help="Caminho do CSV com scores")
    ap.add_argument("--rename", action="store_true", help="Renomear arquivos com prefixo de rank")
    args = ap.parse_args()

    folder = args.folder.expanduser().resolve()
    if not folder.is_dir():
        raise SystemExit(f"Pasta nao existe: {folder}")

    clip_model, processor, mlp, device = load_model()

    images = list(iter_images(folder))
    print(f"[LAION] {len(images)} imagens a pontuar em {folder}")

    results: list[tuple[Path, float]] = []
    for i, p in enumerate(images, 1):
        try:
            s = score_image(clip_model, processor, mlp, device, p)
        except Exception as e:
            print(f"  ERRO {p.name}: {e}")
            continue
        results.append((p, s))
        print(f"  [{i:>3}/{len(images)}] {s:5.2f}  {p.name}")

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("w", encoding="utf-8", newline="") as f:
            w = csv.writer(f)
            w.writerow(["rank", "score", "filename"])
            for rank, (p, s) in enumerate(sorted(results, key=lambda x: -x[1]), 1):
                w.writerow([rank, f"{s:.3f}", p.name])
        print(f"\n[LAION] CSV: {args.output}")

    if args.rename:
        rename_with_rank(folder, results)
        print(f"[LAION] Arquivos renomeados com prefixo de rank")

    if results:
        scores = [s for _, s in results]
        print(f"\n[LAION] Stats: min={min(scores):.2f}  max={max(scores):.2f}  avg={sum(scores)/len(scores):.2f}")


if __name__ == "__main__":
    main()
