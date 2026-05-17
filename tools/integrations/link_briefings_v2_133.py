#!/usr/bin/env python3
"""
link_briefings_v2_133.py
Popula a coluna "Link Briefing" (col N, idx 13) na aba "Comunicacao Digital"
da planilha v2 do Projeto 133 com os links dos Google Docs criados.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "gws"))
from gws_auth import get_credentials
from googleapiclient.discovery import build

SS_ID = "1fccNKRv-OVwlk9Y4OyUNI3TzXN32GRqCC-qj-cgQ8c0"
TAB   = "Comunicacao Digital"

DOC_BASE = "https://docs.google.com/document/d/{}/edit"

# Mapeamento: fragmento do nome (lowercase) → doc_id
# O fragmento deve ser suficientemente único para match na col B
BRIEFINGS = [
    # EMAIL
    ("1 semana antes",           "1w8CVBgFly_dqWBMFYfFeDZT8ug1vCf13XT8G_BlSQiw"),
    ("amanha comeca",            "1KIbJYvNaqnrLxGe76-5G3FOJVOA46omKnk37ZjfAqDs"),
    # WHATSAPP — "card" prefix distingue de Redes
    ("card convite escolas",     "1GH1YsJm1wkUePFnnazVrrBDo87MMkUSKlZHouPZMMUI"),
    ("card convite comunidade",  "1nc0OJwhvDvS3f4l2XSoozw-mOMatwp8NsO7v-gyo7yE"),
    ("card programacao",         "1-QwUVflekOHEtUde-FQUAvmDkXJ-AeM1lmV-oJhuw8s"),
    ("agradecimento",            "15dBLknGTAkZA_he5Dv5zBf7etN1I5w0mCWdTx_f1TTk"),
    # REDES SOCIAIS — mais especificos primeiro para evitar match errado
    ("contagem regressiva",      "1Q9UOEQMVwBHQzKPCfgpCbIF1uzDqMfqLRjZyC8FE22I"),
    ("faltam 15",                "16J0oSqd-RSYWEMNAFMm0yWOFRYzO2-gCgXlN1BC8nG8"),
    ("faltam 7",                 "1q_Z9xzVjz9UrKE8zokyIi5mHDg9u-ZTSTHGZpS15920"),
    ("vem ai! ecoarte em manaus (1)", "1DQRWmAxh0ciFZhqNzJV2jCSWMgmRLdN5OCX0EWfdarw"),
    ("linkedin",                 "1-SKKoh1TdWxmY4TPyRMMS2l_VEogcdUkMAA7IokOmm8"),
    ("comeca hoje",              "1RthwluZDywfsyjCZsSK-_NIYGzGL9GmXoIyNnspH140"),
    ("programacao do dia d",     "1aX3hVR1ciWlSO3_CIPFOZqASA3ubMEg1WfxocNX5qVs"),
    ("cobertura ao vivo",        "1930sR2yd_RC2oSzzHr5MkgN4_43WCqZ-iMV7tejahXg"),
    ("melhores momentos manaus", "1sXuDL3-ahKT_YE8BgsCHcPiHDfpz9-GZNyCzRRQioFo"),
    ("melhores momentos",        "1sGQW0DldZf5LKQdvG-7vL3_xIAqFIazRMwuPVYU_HbQ"),
    ("numeralha",                "1ziQ_nuUwWVU6wMFRyD3aU3bTFdYf_siLTHbwdPaOqO8"),
]


def find_doc_id(cell_value: str) -> str | None:
    v = cell_value.lower()
    for frag, doc_id in BRIEFINGS:
        if frag in v:
            return doc_id
    return None


def main():
    creds = get_credentials()
    svc = build("sheets", "v4", credentials=creds)

    # Ler toda a aba para encontrar posicoes dos itens
    result = svc.spreadsheets().values().get(
        spreadsheetId=SS_ID,
        range=f"'{TAB}'!A:P"
    ).execute()
    rows = result.get("values", [])

    print(f"Total de linhas na aba: {len(rows)}")

    updates = []   # (row_idx_0based, url)
    matched = []

    for i, row in enumerate(rows):
        if len(row) < 2:
            continue
        nome = row[1] if len(row) > 1 else ""
        doc_id = find_doc_id(nome)
        if doc_id:
            url = DOC_BASE.format(doc_id)
            updates.append((i, url))
            matched.append((i+1, nome, url))  # 1-based para exibir

    print(f"\nItens com briefing encontrado: {len(matched)}")
    for row_num, nome, url in matched:
        print(f"  Linha {row_num}: {nome[:60]} | {url[:60]}...")

    if not updates:
        print("\nNenhum item encontrado. Verifique os nomes na planilha.")
        return

    # Escrever um a um usando a notacao A1 de cada celula N
    value_requests = []
    for row_0, url in updates:
        sheet_row = row_0 + 1   # 1-based para A1
        value_requests.append({
            "range": f"'{TAB}'!N{sheet_row}",
            "values": [[url]]
        })

    svc.spreadsheets().values().batchUpdate(
        spreadsheetId=SS_ID,
        body={
            "valueInputOption": "USER_ENTERED",
            "data": value_requests
        }
    ).execute()

    print(f"\n{len(updates)} links escritos na coluna N.")
    print(f"\nURL: https://docs.google.com/spreadsheets/d/{SS_ID}/edit")


if __name__ == "__main__":
    main()
