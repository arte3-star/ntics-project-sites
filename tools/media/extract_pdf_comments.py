"""
extract_pdf_comments.py — Extrai comentarios/anotacoes de um PDF revisado.

Le todas as annotations de um PDF e gera um JSON com as edicoes de texto
identificadas. Suporta os tipos mais comuns de marcacao de revisao:

  - Highlight + comentario: texto destacado com instrucao de alteracao
  - StrikeOut: texto riscado (para remover)
  - StrikeOut + comentario: texto riscado com substituto no comentario
  - Caret/Insert: ponto de insercao com texto a adicionar
  - Text Note (sticky): comentario posicional com instrucao
  - FreeText: anotacao de texto livre
  - Underline/Squiggly + comentario: texto marcado com instrucao

Usage:
  python tools/extract_pdf_comments.py --pdf "C:/revisao/apresentacao_revisada.pdf"
  python tools/extract_pdf_comments.py --pdf "C:/revisao/apresentacao_revisada.pdf" --output .tmp/edits.json
  python tools/extract_pdf_comments.py --pdf "C:/revisao/apresentacao_revisada.pdf" --page 3

Output JSON schema:
  {
    "source_pdf": "path",
    "total_annotations": 12,
    "edits": [
      {
        "page": 1,
        "type": "replace",           // replace | delete | insert | note
        "original_text": "texto original",
        "new_text": "texto corrigido",
        "comment": "comentario do revisor",
        "annotation_type": "Highlight",
        "confidence": "high",         // high | medium | low
        "rect": [x0, y0, x1, y1]
      }
    ],
    "notes": [
      {
        "page": 2,
        "comment": "Verificar dados",
        "annotation_type": "Text",
        "rect": [x0, y0, x1, y1]
      }
    ]
  }

Environment:
  Requires PyMuPDF: pip install PyMuPDF
"""

import argparse
import json
import re
import sys
from pathlib import Path

# Fix Windows console encoding
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

try:
    import fitz  # PyMuPDF
except ImportError:
    print("[ERROR] PyMuPDF not installed. Run: pip install PyMuPDF")
    sys.exit(1)


# -- Annotation type constants ------------------------------------------------

# Markup annotations that select text
MARKUP_TYPES = {
    fitz.PDF_ANNOT_HIGHLIGHT,
    fitz.PDF_ANNOT_STRIKE_OUT,
    fitz.PDF_ANNOT_UNDERLINE,
    fitz.PDF_ANNOT_SQUIGGLY,
}

# Text insertion annotations
INSERT_TYPES = {
    fitz.PDF_ANNOT_CARET,
}

# Note/comment annotations
NOTE_TYPES = {
    fitz.PDF_ANNOT_TEXT,  # Sticky note
    fitz.PDF_ANNOT_FREE_TEXT,
}


# -- Helper functions ----------------------------------------------------------

def clean_text(text):
    """Normalize whitespace in extracted text."""
    if not text:
        return ""
    # Collapse multiple whitespace into single space, strip
    return re.sub(r"\s+", " ", text).strip()


def get_marked_text(page, annot):
    """Extract the text covered by a markup annotation (highlight, strikeout, etc)."""
    try:
        # Get quads (quadrilaterals) that define the marked area
        quads = annot.vertices
        if not quads:
            # Fallback: use the annotation rect
            return clean_text(page.get_textbox(annot.rect))

        # Vertices come in groups of 4 (quad points)
        text_parts = []
        for i in range(0, len(quads), 4):
            quad = fitz.Quad(quads[i: i + 4])
            text_parts.append(page.get_textbox(quad.rect))

        return clean_text(" ".join(text_parts))
    except Exception:
        # Fallback to rect-based extraction
        try:
            return clean_text(page.get_textbox(annot.rect))
        except Exception:
            return ""


def parse_replacement_comment(comment):
    """Try to extract a replacement text from a comment.

    Common patterns reviewers use:
      - "trocar por: texto novo"
      - "alterar para: texto novo"
      - "substituir por texto novo"
      - "corrigir: texto novo"
      - "-> texto novo"
      - "=> texto novo"
      - Just the replacement text directly
    """
    if not comment:
        return None, "low"

    comment = comment.strip()

    # Pattern: explicit replacement markers (Portuguese + English)
    patterns = [
        r"(?:trocar|alterar|mudar|substituir|corrigir|replace|change)\s*(?:por|para|to|with|:)\s*[:\-]?\s*(.+)",
        r"(?:deve ser|should be|deveria ser)\s*[:\-]?\s*(.+)",
        r"^[:\-\u2192\u2794\u27A1]>\s*(.+)",       # -> or => or arrow
        r"^\u2192\s*(.+)",                           # Unicode arrow
        r'^"(.+)"$',                                 # Quoted text = replacement
        r"^'(.+)'$",                                 # Single-quoted
    ]

    for pattern in patterns:
        match = re.match(pattern, comment, re.IGNORECASE | re.DOTALL)
        if match:
            return clean_text(match.group(1)), "high"

    # If the comment is short (< 100 chars) and doesn't look like an instruction,
    # it might be the replacement text itself
    if len(comment) < 100 and not re.search(r"[?!]$|verificar|checar|revisar|check|review|avaliar", comment, re.IGNORECASE):
        return comment, "medium"

    return None, "low"


def classify_annotation(annot_type, marked_text, comment):
    """Classify an annotation into an edit type."""
    has_text = bool(marked_text)
    has_comment = bool(comment and comment.strip())

    # StrikeOut without replacement comment = delete
    if annot_type == fitz.PDF_ANNOT_STRIKE_OUT:
        if has_comment:
            replacement, confidence = parse_replacement_comment(comment)
            if replacement:
                return "replace", replacement, confidence
        return "delete", "", "high"

    # Caret = insert
    if annot_type == fitz.PDF_ANNOT_CARET:
        if has_comment:
            return "insert", comment.strip(), "high"
        return "insert", "", "low"

    # Highlight/Underline/Squiggly with comment = likely replacement
    if annot_type in MARKUP_TYPES and has_comment:
        replacement, confidence = parse_replacement_comment(comment)
        if replacement:
            return "replace", replacement, confidence
        return "note", None, "low"

    # Markup without comment = just flagged, no clear action
    if annot_type in MARKUP_TYPES and not has_comment:
        return "note", None, "low"

    return "note", None, "low"


# -- Main extraction -----------------------------------------------------------

def extract_comments(pdf_path, target_page=None):
    """Extract all annotations from a PDF and classify them as edits."""
    doc = fitz.open(pdf_path)

    edits = []
    notes = []

    for page_num in range(doc.page_count):
        if target_page is not None and page_num + 1 != target_page:
            continue

        page = doc[page_num]

        for annot in page.annots() or []:
            annot_type = annot.type[0]
            annot_type_name = annot.type[1]
            comment = clean_text(annot.info.get("content", ""))
            rect = list(annot.rect)

            # Markup annotations (highlight, strikeout, underline, squiggly)
            if annot_type in MARKUP_TYPES:
                marked_text = get_marked_text(page, annot)
                edit_type, new_text, confidence = classify_annotation(annot_type, marked_text, comment)

                if edit_type == "note":
                    notes.append({
                        "page": page_num + 1,
                        "comment": comment or f"[{annot_type_name}] {marked_text}",
                        "marked_text": marked_text,
                        "annotation_type": annot_type_name,
                        "rect": rect,
                    })
                else:
                    edits.append({
                        "page": page_num + 1,
                        "type": edit_type,
                        "original_text": marked_text,
                        "new_text": new_text or "",
                        "comment": comment,
                        "annotation_type": annot_type_name,
                        "confidence": confidence,
                        "rect": rect,
                    })

            # Caret (insert) annotations
            elif annot_type in INSERT_TYPES:
                edit_type, new_text, confidence = classify_annotation(annot_type, "", comment)
                # Try to get surrounding text for context
                context_text = ""
                try:
                    expanded_rect = fitz.Rect(rect[0] - 50, rect[1] - 5, rect[2] + 50, rect[3] + 5)
                    context_text = clean_text(page.get_textbox(expanded_rect))
                except Exception:
                    pass

                edits.append({
                    "page": page_num + 1,
                    "type": edit_type,
                    "original_text": context_text,
                    "new_text": new_text or "",
                    "comment": comment,
                    "annotation_type": annot_type_name,
                    "confidence": confidence,
                    "rect": rect,
                })

            # Sticky notes and free text
            elif annot_type in NOTE_TYPES:
                # Check if the note contains replacement instructions
                replacement, confidence = parse_replacement_comment(comment)

                # Try to get text near the note
                nearby_text = ""
                try:
                    expanded_rect = fitz.Rect(rect[0] - 20, rect[1] - 10, rect[2] + 200, rect[3] + 10)
                    nearby_text = clean_text(page.get_textbox(expanded_rect))
                except Exception:
                    pass

                if replacement:
                    edits.append({
                        "page": page_num + 1,
                        "type": "replace",
                        "original_text": nearby_text,
                        "new_text": replacement,
                        "comment": comment,
                        "annotation_type": annot_type_name,
                        "confidence": "medium" if nearby_text else "low",
                        "rect": rect,
                    })
                else:
                    notes.append({
                        "page": page_num + 1,
                        "comment": comment,
                        "nearby_text": nearby_text,
                        "annotation_type": annot_type_name,
                        "rect": rect,
                    })

            # Redact annotations (explicit replacement)
            elif annot_type == fitz.PDF_ANNOT_REDACT:
                marked_text = get_marked_text(page, annot)
                edits.append({
                    "page": page_num + 1,
                    "type": "delete" if not comment else "replace",
                    "original_text": marked_text,
                    "new_text": comment or "",
                    "comment": comment,
                    "annotation_type": annot_type_name,
                    "confidence": "high",
                    "rect": rect,
                })

    doc.close()

    return {
        "source_pdf": str(Path(pdf_path).resolve()),
        "total_annotations": len(edits) + len(notes),
        "total_edits": len(edits),
        "total_notes": len(notes),
        "edits": edits,
        "notes": notes,
    }


# -- CLI -----------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Extrai comentarios/anotacoes de revisao de um PDF."
    )
    parser.add_argument("--pdf", required=True, help="Caminho do PDF revisado")
    parser.add_argument("--output", help="Caminho do JSON de saida (default: .tmp/pdf_edits.json)")
    parser.add_argument("--page", type=int, help="Extrair apenas de uma pagina especifica")
    parser.add_argument("--show", action="store_true", help="Exibir resultado no terminal")

    args = parser.parse_args()

    pdf_path = Path(args.pdf).resolve()
    if not pdf_path.exists():
        print(f"[ERROR] PDF not found: {pdf_path}")
        sys.exit(1)

    print(f"[...] Extraindo anotacoes de: {pdf_path.name}")
    result = extract_comments(str(pdf_path), target_page=args.page)

    # Output path
    output_path = Path(args.output) if args.output else Path(".tmp/pdf_edits.json")
    output_path = output_path.resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    # Report
    print(f"\n{'=' * 60}")
    print(f"RESULTADO DA EXTRACAO")
    print(f"{'=' * 60}")
    print(f"  PDF:            {pdf_path.name}")
    print(f"  Total anotacoes: {result['total_annotations']}")
    print(f"  Edicoes claras:  {result['total_edits']}")
    print(f"  Notas/avisos:    {result['total_notes']}")

    if result["edits"]:
        print(f"\n  EDICOES IDENTIFICADAS:")
        for i, edit in enumerate(result["edits"], 1):
            conf_icon = {"high": "+", "medium": "~", "low": "?"}.get(edit["confidence"], "?")
            print(f"    [{conf_icon}] p.{edit['page']} {edit['type'].upper()}: ", end="")
            if edit["type"] == "replace":
                orig = edit["original_text"][:50] + ("..." if len(edit["original_text"]) > 50 else "")
                new = edit["new_text"][:50] + ("..." if len(edit["new_text"]) > 50 else "")
                print(f'"{orig}" -> "{new}"')
            elif edit["type"] == "delete":
                orig = edit["original_text"][:60] + ("..." if len(edit["original_text"]) > 60 else "")
                print(f'REMOVER "{orig}"')
            elif edit["type"] == "insert":
                new = edit["new_text"][:60] + ("..." if len(edit["new_text"]) > 60 else "")
                print(f'INSERIR "{new}"')

    if result["notes"]:
        print(f"\n  NOTAS (requerem interpretacao manual):")
        for note in result["notes"]:
            comment = note["comment"][:70] + ("..." if len(note["comment"]) > 70 else "")
            print(f"    p.{note['page']}: {comment}")

    print(f"\n  JSON salvo em: {output_path}")
    print(f"{'=' * 60}")

    if args.show:
        print(f"\n{json.dumps(result, ensure_ascii=False, indent=2)}")


if __name__ == "__main__":
    main()
