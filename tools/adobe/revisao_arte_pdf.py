"""
Revisão de Arte para Impressão (PDF)

Auditoria técnica de arte antes do envio à gráfica. Valida CMYK, DPI,
sangria, fontes em outline, logos vetoriais, hierarquia de marcas e
regras específicas do projeto.

Workflow: workflows/marketing/revisao/revisao_arte_impressao.md
Skill:    .claude/skills/revisao-arte-impressao/SKILL.md

Uso:
    python tools/adobe/revisao_arte_pdf.py --file arte.pdf [--project 132] [--type rollup]

Output:
    Relatório markdown + JSON com checklist e decisão (🟢/🟡/🔴).

Dependências: PyMuPDF (fitz), pikepdf (opcional para metadados mais detalhados)

Status: STUB — implementação base a fazer.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Literal

try:
    import fitz  # PyMuPDF
except ImportError:
    print("[ERRO] PyMuPDF não instalado. pip install PyMuPDF")
    sys.exit(1)


Status = Literal["pass", "warning", "fail"]


# Sangria mínima por tipo de peça (cm)
SANGRIA_MIN_CM = {
    "rollup": 3.0,
    "pantojet": 5.0,
    "backdrop": 5.0,
    "wind-banner": 3.0,
    "saia-bancada": 3.0,
    "placa-fotos": 2.0,
    "camiseta": 0.3,  # área de estampa, sangria é conceitual
    "default": 0.3,   # 3 mm universal
}


def validar_cor_cmyk(doc: fitz.Document) -> tuple[Status, str]:
    """Verifica se o PDF está em CMYK."""
    # TODO: inspecionar ColorSpace de cada página e imagem
    # Resumidamente: iterar doc, checar /ColorSpace nos objetos
    return "pass", "Implementação pendente — a fazer"


def validar_dpi(doc: fitz.Document, min_dpi: int = 300) -> tuple[Status, list]:
    """Verifica DPI das imagens raster embedadas."""
    problemas = []
    for page_num, page in enumerate(doc):
        for img in page.get_images(full=True):
            # img = (xref, smask, width, height, bpc, colorspace, alt_cs, name, filter, referencer)
            xref, _, width_px, height_px, *_ = img
            rect = page.rect
            # cálculo aproximado de DPI — precisa da escala de colocação
            # TODO: melhorar cálculo usando matriz de transformação
            dpi_estimado = width_px / (rect.width / 72)  # rough
            if dpi_estimado < min_dpi:
                problemas.append({
                    "page": page_num + 1,
                    "image": img[7],
                    "dpi_estimado": round(dpi_estimado, 1),
                })
    if problemas:
        return "fail", problemas
    return "pass", []


def validar_sangria(doc: fitz.Document, tipo_peca: str) -> tuple[Status, str]:
    """Verifica se o PDF tem sangria (/BleedBox > /TrimBox)."""
    # TODO: ler MediaBox, BleedBox, TrimBox e calcular diferença
    min_cm = SANGRIA_MIN_CM.get(tipo_peca, SANGRIA_MIN_CM["default"])
    return "pass", f"Implementação pendente — mínimo esperado: {min_cm} cm"


def validar_fontes_outline(doc: fitz.Document) -> tuple[Status, list]:
    """Verifica se as fontes estão em outline (convertidas em curvas)."""
    # TODO: iterar doc.get_page_fonts(page_num) — se retornar fontes embedadas, não está 100% outline
    return "warning", ["Implementação pendente — checar doc.get_page_fonts"]


def validar_logos_vetoriais(doc: fitz.Document) -> tuple[Status, str]:
    """Sinaliza se há logos aplicados como imagem raster (PNG/JPG)."""
    # TODO: heurística — imagens pequenas (< 200×200 px) no layout são candidatas a logo raster
    return "warning", "Implementação pendente — inspeção heurística"


def revisar_pdf(file_path: Path, tipo_peca: str = "default", project_code: str | None = None) -> dict:
    """Executa toda a bateria de validações e retorna checklist + decisão."""
    doc = fitz.open(file_path)

    checks = {
        "cmyk":           validar_cor_cmyk(doc),
        "dpi":            validar_dpi(doc),
        "sangria":        validar_sangria(doc, tipo_peca),
        "fontes_outline": validar_fontes_outline(doc),
        "logos_vetor":    validar_logos_vetoriais(doc),
    }

    # TODO: se project_code fornecido, ler SecondBrain/projetos/{codigo}/tap.md
    # e validar hierarquia de marca + régua MinC / ausência de régua.

    # Consolidar decisão
    tem_fail    = any(status == "fail"    for status, _ in checks.values())
    tem_warning = any(status == "warning" for status, _ in checks.values())
    if tem_fail:
        decisao = "🔴 BLOQUEADO"
    elif tem_warning:
        decisao = "🟡 COM RESSALVAS"
    else:
        decisao = "🟢 APROVADO"

    doc.close()

    return {
        "arquivo": str(file_path),
        "tipo_peca": tipo_peca,
        "project_code": project_code,
        "checks": {k: {"status": s, "details": d} for k, (s, d) in checks.items()},
        "decisao": decisao,
    }


def formatar_relatorio_markdown(resultado: dict) -> str:
    """Gera relatório markdown estruturado a partir do dict de resultado."""
    emoji = {"pass": "🟢 Pass", "warning": "🟡 Warning", "fail": "🔴 Fail"}
    lines = [
        f"# Revisão de arte — {Path(resultado['arquivo']).name}",
        f"**Tipo:** {resultado['tipo_peca']}",
        f"**Projeto:** {resultado.get('project_code') or '—'}",
        "",
        f"## Resultado: {resultado['decisao']}",
        "",
        "## Checklist",
        "| Item | Status | Observação |",
        "|---|---|---|",
    ]
    labels = {
        "cmyk":           "Espaço de cor CMYK",
        "dpi":            "DPI ≥ 300 nas imagens",
        "sangria":        "Sangria mínima",
        "fontes_outline": "Fontes em outline",
        "logos_vetor":    "Logos vetoriais",
    }
    for key, check in resultado["checks"].items():
        status = emoji.get(check["status"], check["status"])
        details = check["details"] if isinstance(check["details"], str) else json.dumps(check["details"], ensure_ascii=False)
        lines.append(f"| {labels.get(key, key)} | {status} | {details} |")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Revisão técnica de arte para impressão.")
    parser.add_argument("--file", required=True, help="Caminho do PDF a revisar.")
    parser.add_argument("--type", default="default", help="Tipo de peça (rollup, pantojet, etc.)")
    parser.add_argument("--project", help="Código NTICS do projeto (ex: 132)")
    parser.add_argument("--output", choices=["md", "json"], default="md", help="Formato do output")
    args = parser.parse_args()

    file_path = Path(args.file)
    if not file_path.exists():
        print(f"[ERRO] Arquivo não encontrado: {file_path}")
        sys.exit(1)

    resultado = revisar_pdf(file_path, tipo_peca=args.type, project_code=args.project)

    if args.output == "json":
        print(json.dumps(resultado, indent=2, ensure_ascii=False))
    else:
        print(formatar_relatorio_markdown(resultado))

    # Exit code: 0 se aprovado ou warning, 1 se bloqueado
    sys.exit(0 if "🟢" in resultado["decisao"] or "🟡" in resultado["decisao"] else 1)


if __name__ == "__main__":
    main()
