"""
Cria Google Form a partir de YAML ou JSON.

Uso:
  python forms_create.py --config briefing.yaml
  python forms_create.py --config briefing.yaml --link-sheet

Formato do YAML:
  title: "Briefing de Projeto"
  description: "Preencha antes de iniciar."
  collect_email: true          # opcional
  items:
    - title: "Nome do projeto"
      type: text               # text | paragraph | radio | checkbox | dropdown | scale | date | time
      required: true
    - title: "Descreva o objetivo"
      type: paragraph
    - title: "Categoria"
      type: radio
      options: [Educação, Cultura, Sustentabilidade]
      required: true
    - title: "Públicos atendidos"
      type: checkbox
      options: [Crianças, Jovens, Adultos, Idosos]
    - title: "Prioridade"
      type: scale
      low: 1
      high: 5
      low_label: Baixa
      high_label: Alta
    - title: "Data prevista"
      type: date
"""
import argparse
import json
import sys
from pathlib import Path

import yaml
from googleapiclient.discovery import build
from gws_auth import get_credentials


def _question_item(entry: dict) -> dict:
    qtype = entry.get("type", "text").lower()
    required = bool(entry.get("required", False))
    question: dict = {"required": required}

    if qtype == "text":
        question["textQuestion"] = {"paragraph": False}
    elif qtype == "paragraph":
        question["textQuestion"] = {"paragraph": True}
    elif qtype in ("radio", "checkbox", "dropdown"):
        type_map = {"radio": "RADIO", "checkbox": "CHECKBOX", "dropdown": "DROP_DOWN"}
        opts = entry.get("options") or []
        if not opts:
            raise ValueError(f"'{entry.get('title')}': tipo {qtype} exige 'options'")
        question["choiceQuestion"] = {
            "type": type_map[qtype],
            "options": [{"value": str(o)} for o in opts],
            "shuffle": bool(entry.get("shuffle", False)),
        }
    elif qtype == "scale":
        question["scaleQuestion"] = {
            "low": int(entry.get("low", 1)),
            "high": int(entry.get("high", 5)),
            "lowLabel": entry.get("low_label", ""),
            "highLabel": entry.get("high_label", ""),
        }
    elif qtype == "date":
        question["dateQuestion"] = {
            "includeTime": bool(entry.get("include_time", False)),
            "includeYear": bool(entry.get("include_year", True)),
        }
    elif qtype == "time":
        question["timeQuestion"] = {"duration": bool(entry.get("duration", False))}
    else:
        raise ValueError(f"Tipo desconhecido: {qtype}")

    item: dict = {
        "title": entry["title"],
        "questionItem": {"question": question},
    }
    if entry.get("description"):
        item["description"] = entry["description"]
    return item


def load_config(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() in (".yaml", ".yml"):
        return yaml.safe_load(text)
    return json.loads(text)


def create_form(config: dict) -> dict:
    service = build("forms", "v1", credentials=get_credentials())

    # Passo 1: criar shell (só title é aceito aqui)
    form = service.forms().create(body={"info": {"title": config["title"]}}).execute()
    form_id = form["formId"]

    # Passo 2: batchUpdate com description, settings e items
    requests: list[dict] = []

    info_update: dict = {}
    if config.get("description"):
        info_update["description"] = config["description"]
    if config.get("document_title"):
        info_update["documentTitle"] = config["document_title"]
    if info_update:
        requests.append({
            "updateFormInfo": {
                "info": info_update,
                "updateMask": ",".join(info_update.keys()),
            }
        })

    if config.get("collect_email"):
        requests.append({
            "updateSettings": {
                "settings": {"emailCollectionType": "VERIFIED"},
                "updateMask": "emailCollectionType",
            }
        })

    for idx, entry in enumerate(config.get("items", [])):
        requests.append({
            "createItem": {
                "item": _question_item(entry),
                "location": {"index": idx},
            }
        })

    if requests:
        service.forms().batchUpdate(
            formId=form_id, body={"requests": requests}
        ).execute()

    return service.forms().get(formId=form_id).execute()


def main():
    parser = argparse.ArgumentParser(description="Cria Google Form a partir de YAML/JSON")
    parser.add_argument("--config", required=True, help="Caminho do YAML ou JSON")
    args = parser.parse_args()

    path = Path(args.config)
    if not path.exists():
        print(f"ERRO: config nao encontrado: {path}", file=sys.stderr)
        sys.exit(1)

    config = load_config(path)
    form = create_form(config)

    print(f"Form criado: {form['info']['title']}")
    print(f"ID:         {form['formId']}")
    print(f"Editar:     https://docs.google.com/forms/d/{form['formId']}/edit")
    print(f"Responder:  {form.get('responderUri', '')}")


if __name__ == "__main__":
    main()
