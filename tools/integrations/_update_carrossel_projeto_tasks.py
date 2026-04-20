"""Script one-time: atualiza nome das tasks Carrossel Projeto S02-S24 com numero do projeto."""

import requests, os, time
from dotenv import load_dotenv

load_dotenv()
token = os.getenv("CLICKUP_API_KEY") or os.getenv("CLICKUP_TOKEN")
headers = {"Authorization": token, "Content-Type": "application/json"}
BASE_URL = "https://api.clickup.com/api/v2"

# task_id, semana, num_projeto, nome_projeto, patrocinador, atendidos, relatorio, fotos, video
MAPPING = [
    ("868j1upu7", "S02", 50,  "Festival Cinegastroarte", "—", 53262,
     "https://drive.google.com/drive/folders/1MZCXGw5voeLoQTGSXtpS2g1xpLHOD28C",
     "https://drive.google.com/drive/folders/144ZJc0NoF-tWqlnJx2vzsb10SiELcJEX",
     "https://youtu.be/4YNknU0eDqo"),
    ("868j1upwu", "S03", 111, "Caminhao ODS", "Rabobank", 24063,
     "https://drive.google.com/file/d/1ux-JrC6pIkVbZiGXu8olYRPxhkvbQFvb/view",
     "https://drive.google.com/drive/folders/1yQvGP-kfvsFBRM4e0_KvBfYpcWF46EQ0",
     "https://drive.google.com/file/d/1dUUXvDgRc1eCQTORJ_srwXizZnwAw1d7/view"),
    ("868j1upv0", "S04", 60,  "Circo no Brasil & Festival de Circo", "—", 20930,
     "https://drive.google.com/file/d/1lkYuHqCfB-jNLAeH7SShz_0nlzKmxMNh/view",
     "https://drive.google.com/drive/folders/1uyXL8ufX4_MrIYEYgaGZm9_q1mqUlaYk",
     "https://youtu.be/iENALeCLQnM"),
    ("868j1upv4", "S05", 88,  "Festival ODS Pocket", "Whirlpool", 17646,
     "https://drive.google.com/file/d/1Iy24N-ubvgiT4wWFcE10ZXAZHRUKwRpb/view",
     "https://drive.google.com/drive/folders/1mBxJnYXaheOPdwhgb_z12fN2EaNBy50a",
     "https://youtu.be/2kMu-chR2qA"),
    ("868j1upv7", "S06", 92,  "Cultura na Comunidade", "Rabobank", 9107,
     "https://drive.google.com/file/d/1Vu3Y05JEirBOjFjPx0HAf1-EoaqTEgWP/view",
     "https://drive.google.com/drive/u/0/folders/1CJ72V5btu7J0hMfP2ntg-AI1k20xoRpS",
     "https://youtu.be/H1ouuOtrNIE"),
    ("868j1upx2", "S07", 90,  "Teatro dos ODS", "Repsol", 7210,
     "https://drive.google.com/file/d/1Qsq1S8kGFLjjOTDhAiT1pC-pW5qEB7kV/view",
     "https://drive.google.com/drive/u/0/folders/1iBTzkAqZIuHPMsLu2WkKgu8PBGL9HXha",
     "https://youtu.be/n6fN5kb6f5s"),
    ("868j1upx6", "S08", 108, "ODS Cultural nas Escolas", "Repsol", 7045,
     "https://drive.google.com/file/d/1cP_QrcL8q1VUKk_rvsvAViTfduyVzChn/view",
     "https://drive.google.com/drive/folders/1oR7HDoQnoLV5Nzc1J7PfSWO4eGk4ZrPl",
     "https://drive.google.com/file/d/1BzVxrjQGssC5dUjkJkrdr2lUi3VbaQ_o/view"),
    ("868j1upzv", "S09", 98,  "Conhecendo os ODS", "Wilson & Sons", 7045,
     "https://drive.google.com/drive/folders/1gobYgEMhZy-p_0oXrfIo0rlN679zLeWq",
     "https://drive.google.com/drive/folders/1EQ3gaiiz8AprsQ7KHGomC10wo3_DFRiL",
     "https://drive.google.com/drive/folders/1zkJ_ra1jvThc_zeAEe46bocPcYCjV5lX"),
    ("868j1uq30", "S10", 97,  "Conhecendo os ODS", "Moove", 6032,
     "https://drive.google.com/file/d/1w-Ux_k8Z8kR12l4NeOCtinVNs4RTQK0u/view",
     "https://drive.google.com/drive/folders/1IyEpcr3RH4cNy5SJ3KLTddwf36k1iG1i",
     "https://youtu.be/kVt4KwdlUKQ"),
    ("868j1uq39", "S11", 107, "Teatro e Oficina Robotica 3aEd", "Whirlpool", 5893,
     "https://drive.google.com/file/d/1xazMwdum_Ew_6YeiYBJKgMCBTH9iF3n9/view",
     "https://drive.google.com/drive/folders/1KNjZOGwEesCfF0y8l7IsC-jYZbcHlWw_",
     "https://drive.google.com/file/d/1WWo9UWyeTVIxr027jO3lDHxFmUw2dEPU/view"),
    ("868j1uq44", "S12", "93a", "Caminhao ODS Artistico", "TCP", 5741,
     "https://drive.google.com/file/d/1kSsIBVfWoVR4Znjq75s4ug_oRLxE8qs0/view",
     "https://drive.google.com/drive/u/0/folders/1BFIn0vsQ8YkXVjzZCE3k4f_M1bCqhXVT",
     "https://youtu.be/wxT0gyL3SRA"),
    ("868j1uq4f", "S13", "93b", "Caminhao ODS Artistico", "Moove", 5568,
     "https://drive.google.com/file/d/1kzwvyk_YOwvnop-fkpI-ssXwkTXuNkYF/view",
     "https://drive.google.com/drive/u/0/folders/1YqDhyGk5BYFsNjGb5IxGlDv4aTBuHzTt",
     "https://youtu.be/Ix4aErTsbqE"),
    ("868j1uq4t", "S14", 91,  "Caminhao Energia", "CTG", 5532,
     "https://drive.google.com/file/d/1hSe74SrRckXFx674ev3g4hWA8Bojov7/view",
     "https://drive.google.com/drive/u/0/folders/13bkWbsdXZFywC_OB5-k4roRmH0sdZezW",
     "https://youtu.be/5oOZyQy_9FE"),
    ("868j1uq53", "S15", 103, "Gastronomia Tambem e Arte", "Whirlpool", 4414,
     "https://drive.google.com/file/d/19Enw68ah6iKcJQVsaTPgW2bc5R7_1IdV/view",
     "https://drive.google.com/drive/folders/1uRpRKc8AoQJon7P9drMHSdwTCT7O6Ktc",
     "https://youtu.be/7IByvjNUegA"),
    ("868j1uq5g", "S16", 87,  "Culinaria Sustentavel", "Enercan", 4173,
     "https://drive.google.com/file/d/1WgI3Fm4marQcdbQ1P3jivkj3v2ayvW4V/view",
     "https://drive.google.com/drive/folders/1c3WZux8KOSuLM7EBumpAo44lt2T7GGot",
     "https://youtu.be/fkeCjDIHmno"),
    ("868j1uq4e", "S17", 89,  "Oficina Teatro Sustentavel", "Ferroport", 4157,
     "https://drive.google.com/file/d/1AUsccvkp5GaAXScbhZuTOY3h_bxJe5ul/view",
     "https://drive.google.com/drive/folders/136QiLGdqGhBNC93QLjU0cvU13AlJpP0P",
     "https://youtu.be/XZoUilKuTUw"),
    ("868j1uq5h", "S18", 86,  "Teatro Bons Habitos", "Ferroporte", 4080,
     "https://drive.google.com/file/d/1CEJvI0mYBw9JtzVC7k4H7Xb5AUxFZqdB/view",
     "https://drive.google.com/drive/folders/12-qi422ADABQwchqltnv_ZK9h5z4JxoF",
     "https://youtu.be/HjOhoGgKZXY"),
    ("868j1uq7j", "S19", 109, "Educacao Cultural", "Statkraft", 3356,
     "https://drive.google.com/file/d/1btI4lsFwRxbmozcn3JUjrAtRloahyU0f/view",
     "https://drive.google.com/drive/folders/15AEtyTCdH8UszEon00Bbg1FeSRqKvzkT",
     "https://drive.google.com/file/d/1bbxcNQ1EjrpiapEuZv-i5Ap9oMZAM2pn/view"),
    ("868j1uq8c", "S20", 110, "Caminhao da Cultura", "Jaepel", 3317,
     "https://drive.google.com/file/d/1enG2PAOibudA7W1pMmhQq6-cVmyFksTB6/view",
     "https://drive.google.com/drive/folders/1SQY61xbxIqXnVu9G7_SWEzzLZqDlNamD",
     "https://drive.google.com/file/d/1Bln0BByuxaF_Rim5GkRjt7KFt_1oKeRY/view"),
    ("868j1uqe9", "S21", 85,  "Meus Habitos 2aEd", "Imetame", 3187,
     "https://drive.google.com/file/d/1bPs2ibE5QkZFBl1j-hiyZEqectb1rjne/view",
     "https://drive.google.com/drive/folders/1qa5N3IHb596N8vI4gDETc7O6Ktc",
     "https://youtu.be/BD7bU-aytVk"),
    ("868j1uqjy", "S22", 50,  "Festival Cinegastroarte", "—", 53262,
     "https://drive.google.com/drive/folders/1MZCXGw5voeLoQTGSXtpS2g1xpLHOD28C",
     "https://drive.google.com/drive/folders/144ZJc0NoF-tWqlnJx2vzsb10SiELcJEX",
     "https://youtu.be/4YNknU0eDqo"),
    ("868j1uqpd", "S23", 111, "Caminhao ODS", "Rabobank", 24063,
     "https://drive.google.com/file/d/1ux-JrC6pIkVbZiGXu8olYRPxhkvbQFvb/view",
     "https://drive.google.com/drive/folders/1yQvGP-kfvsFBRM4e0_KvBfYpcWF46EQ0",
     "https://drive.google.com/file/d/1dUUXvDgRc1eCQTORJ_srwXizZnwAw1d7/view"),
    ("868j1uqqk", "S24", 60,  "Circo no Brasil", "—", 20930,
     "https://drive.google.com/file/d/1lkYuHqCfB-jNLAeH7SShz_0nlzKmxMNh/view",
     "https://drive.google.com/drive/folders/1uyXL8ufX4_MrIYEYgaGZm9_q1mqUlaYk",
     "https://youtu.be/iENALeCLQnM"),
]


def task_name(semana, num, projeto, patrocinador):
    pat = f" ({patrocinador})" if patrocinador != "—" else ""
    return f"Carrossel Projeto {semana} — #{num} {projeto}{pat}"


def build_description(semana, num, projeto, patrocinador, atendidos, relatorio, fotos, video):
    pat_line = f"**Patrocinador:** {patrocinador}  \n" if patrocinador != "—" else ""
    return (
        f"## Briefing\n\n"
        f"**Tipo:** Carrossel Projeto Ativo  \n"
        f"**Semana:** {semana}  \n"
        f"**Projeto:** #{num} — {projeto}  \n"
        f"{pat_line}"
        f"**Pessoas atendidas (diretas):** {atendidos:,}\n\n"
        f"---\n\n"
        f"## Fontes\n\n"
        f"- **Relatorio:** {relatorio}\n"
        f"- **Fotos:** {fotos}\n"
        f"- **Video:** {video}\n\n"
        f"---\n\n"
        f"**Workflow:** `workflows/marketing/producao/carrosseis/carrossel_case_projeto.md`\n"
    )


def update_task(task_id, name, description):
    r = requests.put(
        f"{BASE_URL}/task/{task_id}",
        headers=headers,
        json={"name": name, "markdown_description": description},
        timeout=30,
    )
    if not r.ok:
        print(f"  ERRO {task_id}: {r.status_code} {r.text[:200]}")
        return False
    return True


for entry in MAPPING:
    task_id, semana, num, projeto, patrocinador, atendidos, relatorio, fotos, video = entry
    name = task_name(semana, num, projeto, patrocinador)
    desc = build_description(semana, num, projeto, patrocinador, atendidos, relatorio, fotos, video)
    ok = update_task(task_id, name, desc)
    status = "OK" if ok else "ERRO"
    print(f"  [{status}] {semana}: {name}")
    time.sleep(0.3)

print(f"\nConcluido. {len(MAPPING)} tasks atualizadas.")
