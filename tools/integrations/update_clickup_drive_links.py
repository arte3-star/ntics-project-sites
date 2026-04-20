"""
update_clickup_drive_links.py
Lê .tmp/drive_upload_results.json (gerado por upload_to_drive.py)
e atualiza a DESCRIÇÃO de cada task do ClickUp com o link do Drive.

Uso: python tools/update_clickup_drive_links.py
"""
import os
import json
import sys
from pathlib import Path
import requests
from dotenv import load_dotenv

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

load_dotenv()
CLICKUP_TOKEN = os.getenv("CLICKUP_API_KEY") or os.getenv("CLICKUP_TOKEN")

BASE_URL = "https://api.clickup.com/api/v2"

CLICKUP_MAP = {
    "carrosseis/noticias/S03": ("868hrghtq", "Carrossel Notícias ESG — Semana S03"),
    "carrosseis/noticias/S04": ("868hrghtr", "Carrossel Notícias ESG — Semana S04"),
    "carrosseis/noticias/S05": ("868j1upxc", "Carrossel Notícias ESG — Semana S05"),
    "carrosseis/educativo/S03": ("868hrghrg", "Carrossel Educativo — Semana S03"),
    "carrosseis/educativo/S04": ("868hrghrq", "Carrossel Educativo — Semana S04"),
    "carrosseis/educativo/S05": ("868hrght1", "Carrossel Educativo — Semana S05"),
    "videos/semana-03": ("868hrghrj", "Roteiro Vídeo — Semana S03"),
    "videos/semana-04": ("868hrghru", "Roteiro Vídeo — Semana S04"),
    "videos/semana-05": ("868hrght2", "Roteiro Vídeo — Semana S05"),
}


def update_task_description(task_id, new_description):
    headers = {
        "Authorization": CLICKUP_TOKEN,
        "Content-Type": "application/json",
    }
    payload = {"description": new_description}
    r = requests.put(
        f"{BASE_URL}/task/{task_id}",
        headers=headers,
        json=payload,
        timeout=30,
    )
    if not r.ok:
        raise RuntimeError(f"{r.status_code}: {r.text[:300]}")
    return r.json()


def main():
    results_path = Path(__file__).parent.parent / ".tmp" / "drive_upload_results.json"
    if not results_path.exists():
        print("ERRO: .tmp/drive_upload_results.json não encontrado.")
        print("Execute primeiro: python tools/upload_to_drive.py")
        sys.exit(1)

    with open(results_path, encoding="utf-8") as f:
        results = json.load(f)

    for folder_key, data in results.items():
        if folder_key not in CLICKUP_MAP:
            continue

        task_id, label = CLICKUP_MAP[folder_key]
        link = data["link"]

        description = (
            f"**{label}**\n\n"
            f"📁 Google Drive: {link}\n\n"
            f"Pasta com todos os cards gerados (JPGs + descricao.txt). "
            f"Revisar visualmente antes de publicar."
        )

        print(f">> Atualizando task {task_id} ({label})...", end=" ", flush=True)
        try:
            update_task_description(task_id, description)
            print("✓")
        except Exception as e:
            print(f"ERRO: {e}")

    print("\nConcluído!")


if __name__ == "__main__":
    main()
