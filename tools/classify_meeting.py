#!/usr/bin/env python3
"""
tools/classify_meeting.py
Classifies a meeting transcript and extracts tasks using Claude API.
Output: .tmp/meeting_result.json
"""

import os, sys, json, argparse
from pathlib import Path
import anthropic

def load_transcript(text: str | None, tmp_path: Path) -> str:
    if text and len(text) > 100:
        return text
    transcript_file = tmp_path / "transcript.txt"
    if transcript_file.exists():
        return transcript_file.read_text(encoding="utf-8")
    return text or ""

SYSTEM_PROMPT = """You are the NTICS Projetos meeting intelligence agent.

Analyze the meeting transcript and return ONLY valid JSON, no extra text.

NTICS TEAM (Name → ClickUp ID):
Ana Carolina Xavier=81460584, Abilio Martins=81470291, Bruna Seibel=81461902,
Raíza Araújo=81460587, Jessica Lora=81477520, Mayara Ferreira=81460588,
Lucas Rotta=81513300, Vera Carvalho=126152139, Cristina Ygiro=81502630,
Fernando Clark=81460585, Luiz Felipe Deffune=81460586, Ariadne Canaver=81545764,
Angelo Miguel=81549824, Luisa Moreira=87399549

ASSIGNMENT RULES:
- produção/campo → 81460587 or 81477520
- financeiro/NF/pagamento/reembolso → 126152139
- jurídico/contrato/compliance → 81460586
- vendas/proposta/captação → 81470291 or 81502630
- comunicação/IA/site/post/automação → 81513300
- inscrição/MINC/prestação de contas → 81460588
- coordenação/prazo/PMO → 81461902
- assessoria/release/clipping → 81549824
- design/carrossel/visual → 87399549

ACTIVE PROJECTS 2026:
115=Peróxidos/Tupy/BTG, 116=Éster(list:901113068470),
117=Whirlpool(list:901113013525), 118=Wilson Sons, 119=Sylvamo/PEC(list:901113051700),
120=Statkraft/Porto Itapoá, 121=TAG, 122=Repsol, 123=TCP/Circo,
124=Compagas/Gastronomia(list:901113142041), 125=GRU Gastronomia, 127=GRU/Sotreq
DEFAULT_LIST=901113425673

CLASSIFICATION:
- INTERNAL: only NTICS team, operational → ClickUp only, NO Pipedrive
- SALES: external client/sponsor present → ClickUp + Pipedrive
- STRATEGIC: leadership + OKRs/direction → ClickUp only, NO Pipedrive

Return this exact JSON structure:
{
  "meeting_type": "INTERNAL|SALES|STRATEGIC",
  "confidence": 0-100,
  "title": "meeting title",
  "project_number": "115-127 or null",
  "list_id": "ClickUp list ID — use known IDs above or 901113425673",
  "external_participants": ["name1"],
  "tasks": [
    {
      "title": "action in infinitive form",
      "assignee_id": "numeric ID or null",
      "due_date": "YYYY-MM-DD or null",
      "priority": "urgent|high|normal|low",
      "city": "city name or null",
      "phase": "phase name or null",
      "context": "transcript excerpt that originated this task"
    }
  ],
  "pipedrive_summary": "CRM summary if SALES, null otherwise",
  "learning": "new organizational knowledge discovered, null if none"
}"""

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--text", default="")
    parser.add_argument("--url", default="")
    parser.add_argument("--name", default="Ata")
    args = parser.parse_args()

    root = Path(__file__).parent.parent
    tmp  = root / ".tmp"
    tmp.mkdir(exist_ok=True)

    transcript = load_transcript(args.text, tmp)

    if len(transcript) < 50:
        print("ERROR: Transcript too short or empty", file=sys.stderr)
        sys.exit(1)

    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    prompt = f"""FILE: {args.name}
URL: {args.url}

TRANSCRIPT:
{transcript[:12000]}"""

    print(f"🤖 Classifying: {args.name[:60]}...")

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}]
    )

    raw = response.content[0].text.strip()

    # Strip markdown fences if present
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    result = json.loads(raw)

    # Apply low-confidence fallback
    if result.get("confidence", 0) < 80:
        print(f"⚠️  Low confidence ({result['confidence']}%) — routing to triage list")
        result["list_id"] = "901113425673"
        result["triage"] = True

    output = tmp / "meeting_result.json"
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"✅ Type: {result['meeting_type']} ({result['confidence']}%)")
    print(f"   Project: {result.get('project_number', 'none')} → list {result['list_id']}")
    print(f"   Tasks found: {len(result.get('tasks', []))}")
    print(f"   Output: {output}")

if __name__ == "__main__":
    main()
