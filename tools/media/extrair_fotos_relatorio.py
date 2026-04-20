"""
extrair_fotos_relatorio.py — Extrai fotos contextuais de um relatorio PDF.

Le o texto de cada pagina do PDF, identifica quais paginas sao relevantes
para cada card do carrossel, e extrai apenas as imagens dessas paginas.

Estrutura dos 8 cards NTICS (embutida, sem necessidade de configuracao externa):
  01 capa        — apresentacao geral do projeto e patrocinador
  02 o_projeto   — objetivo, descricao, publico-alvo
  03 metodologia — atividades, oficinas, como funciona
  04 alcance     — numeros, cidades, beneficiarios
  05 a_empresa   — patrocinador, ESG, sustentabilidade
  06 resultados  — resultados, satisfacao, engajamento
  07 impacto     — impacto, legado, ODS, Agenda 2030
  08 cta         — (sem foto, apenas logos)

Para cada card, extrai as top-N melhores fotos (fallback automatico):
  - rank 1 = foto principal (usada na geracao automaticamente)
  - rank 2 e 3 = fallbacks (usadas se a principal nao ficar boa)

Filtros aplicados automaticamente:
  - Infograficos/slides: imagens com >65% de pixels claros (fundo branco)
    sao marcadas como 'graphic' e movidas para o final da fila de fallbacks
  - Deduplicacao cross-card: fotos visualmente identicas entre cards distintos
    sao removidas do card de menor prioridade (mantidas no card mais relevante)

Usage:
  python tools/media/extrair_fotos_relatorio.py \\
    --pdf ".tmp/marketing/carrosseis/meu-projeto/relatorio.pdf" \\
    --output ".tmp/marketing/carrosseis/meu-projeto/fotos-contextuais" \\
    --min-size 1000 \\
    --top-n 3

Output:
  {output}/card01_capa_p{pag}_img{n}.jpeg   — foto extraida
  {output}/card01_capa_p{pag}_PAGE.jpg      — screenshot da pagina de origem (para revisao visual)
  {output}/manifest.json                     — mapeamento completo card→fotos + page_screenshot por imagem

Environment:
  Requires pdfplumber, PyMuPDF, Pillow: pip install pdfplumber PyMuPDF Pillow
"""

import argparse
import json
import sys
import unicodedata
from datetime import date
from pathlib import Path

# Fix Windows console encoding
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


# ── Definicao dos 8 cards NTICS ──────────────────────────────────────────────

CARD_DEFINITIONS = [
    {
        "card_num": 1,
        "card_name": "capa",
        "needs_photo": True,
        "keywords": [
            "projeto", "nome", "apresenta", "titulo", "capa", "introducao",
            "iniciativa", "bem-vindo", "lancamento", "abertura", "realizado por",
            "patrocinado", "apoio", "sponsorship", "overview",
        ],
    },
    {
        "card_num": 2,
        "card_name": "o_projeto",
        "needs_photo": True,
        "keywords": [
            "objetivo", "proposta", "descricao", "publico-alvo", "publico alvo",
            "o que e", "o que eh", "meta", "finalidade", "justificativa",
            "sobre o projeto", "apresentacao do projeto", "o projeto visa",
            "tem como objetivo", "busca", "pretende",
            # projetos itinerantes (caminhao, onibus, unidade movel)
            "caminhao", "itinerante", "unidade movel", "modulo itinerante",
            "fachada", "exterior", "estrutura", "espaco interativo",
        ],
    },
    {
        "card_num": 3,
        "card_name": "metodologia",
        "needs_photo": True,
        "keywords": [
            "metodologia", "atividade", "oficina", "circuito", "steam",
            "como funciona", "abordagem", "dinamica", "formato", "programacao",
            "agenda", "etapas", "modulos", "pedagogia",
            "educacional", "aprendizagem", "vivencia", "experiencia",
        ],
    },
    {
        "card_num": 4,
        "card_name": "alcance",
        "needs_photo": True,
        "keywords": [
            "alcance", "cidade", "municipio", "escola", "aluno", "beneficiario",
            "numero", "atendido", "quantidade", "participante", "turma",
            "regiao", "estado", "abrangencia", "cobertura", "territorios",
            "locais atendidos", "cidades atendidas", "escolas atendidas",
        ],
    },
    {
        "card_num": 5,
        "card_name": "a_empresa",
        "needs_photo": True,
        "keywords": [
            "empresa", "patrocinador", "parceiro", "esg", "sustentabilidade",
            "corporativo", "responsabilidade social", "lei rouanet", "incentivo fiscal",
            "quem somos", "sobre nos", "nossa missao", "investimento social",
            "agenda 2030", "compromisso", "relatorio de sustentabilidade",
            "patrocinio", "apoiador", "realizacao",
        ],
    },
    {
        "card_num": 6,
        "card_name": "resultados",
        "needs_photo": True,
        "keywords": [
            "resultado", "avaliacao", "satisfacao", "engajamento", "midia",
            "feedback", "nota", "avaliado", "indice", "pesquisa",
            "retorno", "impacto imediato", "alcancado", "conquistado",
            "superado", "entregue", "realizado", "concluido",
            "o que foi alcancado", "numeros finais",
        ],
    },
    {
        "card_num": 7,
        "card_name": "impacto",
        "needs_photo": True,
        "keywords": [
            "impacto", "transformacao", "legado", "longo prazo", "ods",
            "agenda 2030", "indireto", "comunidade", "mudanca", "futuro",
            "visao", "inspiracao", "desenvolvimento sustentavel",
            "objetivos de desenvolvimento sustentavel", "carbono",
            "neutro", "meio ambiente", "social", "economico",
        ],
    },
    {
        "card_num": 8,
        "card_name": "cta",
        "needs_photo": False,
        "keywords": [],
    },
]


# ── Utilitarios de texto ─────────────────────────────────────────────────────

def normalize(text: str) -> str:
    """Normaliza texto: lowercase, remove acentos, remove pontuacao extra."""
    text = text.lower()
    nfd = unicodedata.normalize("NFD", text)
    text = "".join(c for c in nfd if unicodedata.category(c) != "Mn")
    return text


def score_page(page_text_norm: str, keywords: list) -> float:
    """Calcula score de relevancia de uma pagina para um card."""
    if not keywords or not page_text_norm:
        return 0.0

    score = 0.0
    matched = []

    for kw in keywords:
        kw_norm = normalize(kw)
        if kw_norm in page_text_norm:
            weight = 1.0 + 0.1 * (len(kw_norm.split()) - 1)
            freq = page_text_norm.count(kw_norm)
            score += weight * (1.0 + 0.2 * min(freq - 1, 3))
            matched.append(kw)

    if len(matched) >= 2:
        score += 0.3 * (len(matched) - 1)

    return round(score, 3)


# ── Filtros de qualidade visual ──────────────────────────────────────────────

def is_graphic_or_infographic(image_path: Path, white_threshold: float = 0.65) -> bool:
    """
    Retorna True se a imagem for provavelmente um infografico, slide ou layout
    com fundo predominantemente branco.

    Criterio: se >65% dos pixels tiverem luminancia > 220 (muito claros),
    a imagem e tratada como grafico, nao como fotografia.
    """
    try:
        from PIL import Image as PILImage
        import struct

        img = PILImage.open(str(image_path)).convert("RGB")
        # Reduzir para amostra 100x100 para performance
        img = img.resize((100, 100), PILImage.LANCZOS)
        pixels = list(img.getdata())  # type: ignore[arg-type]
        total = len(pixels)
        if total == 0:
            return False
        # Contar pixels com todos os canais > 220 (muito claros / quase branco)
        light_count = sum(1 for r, g, b in pixels if r > 220 and g > 220 and b > 220)
        ratio = light_count / total
        return ratio > white_threshold
    except Exception:
        return False


def image_histogram_similarity(path_a: Path, path_b: Path) -> float:
    """
    Calcula similaridade de histograma entre duas imagens (0.0 a 1.0).
    Usa correlacao de histograma RGB normalizado — rapido e sem dependencias extras.
    Retorna 1.0 para imagens identicas, ~0.0 para completamente diferentes.
    """
    try:
        from PIL import Image as PILImage

        def get_hist(path):
            img = PILImage.open(str(path)).convert("RGB").resize((64, 64), PILImage.LANCZOS)
            hist = img.histogram()  # 768 valores: R(256) + G(256) + B(256)
            total = sum(hist) or 1
            return [v / total for v in hist]

        ha = get_hist(path_a)
        hb = get_hist(path_b)

        # Correlacao de Pearson simplificada
        n = len(ha)
        mean_a = sum(ha) / n
        mean_b = sum(hb) / n
        num = sum((ha[i] - mean_a) * (hb[i] - mean_b) for i in range(n))
        den_a = sum((ha[i] - mean_a) ** 2 for i in range(n)) ** 0.5
        den_b = sum((hb[i] - mean_b) ** 2 for i in range(n)) ** 0.5
        if den_a < 1e-10 or den_b < 1e-10:
            return 0.0
        return max(0.0, min(1.0, num / (den_a * den_b)))
    except Exception:
        return 0.0


def deduplicate_cross_card(manifest_cards: list, output_dir: Path, similarity_threshold: float = 0.97):
    """
    Remove duplicatas visuais entre cards diferentes.

    Para cada par de imagens de cards distintos, calcula similaridade de histograma.
    Se similarity >= threshold, remove do card de MENOR numero (menor prioridade narrativa),
    pois o card de maior numero geralmente ja passou o contexto visual.

    Na pratica: mantém a imagem no card que aparece PRIMEIRO na narrativa.
    """
    # Coletar todas as imagens com referencia ao card
    all_images = []
    for card in manifest_cards:
        for img in card.get("images", []):
            path = output_dir / img["filename"]
            if path.exists():
                all_images.append({
                    "card_num": card["card_num"],
                    "filename": img["filename"],
                    "path": path,
                    "rank": img["rank"],
                })

    removed = set()
    pairs_checked = 0

    for i in range(len(all_images)):
        if all_images[i]["filename"] in removed:
            continue
        for j in range(i + 1, len(all_images)):
            if all_images[j]["filename"] in removed:
                continue
            if all_images[i]["card_num"] == all_images[j]["card_num"]:
                continue  # mesmo card — nao deduplica

            pairs_checked += 1
            sim = image_histogram_similarity(all_images[i]["path"], all_images[j]["path"])
            if sim >= similarity_threshold:
                # Manter no card de menor numero (aparece primeiro na narrativa)
                keep = all_images[i] if all_images[i]["card_num"] <= all_images[j]["card_num"] else all_images[j]
                drop = all_images[j] if keep == all_images[i] else all_images[i]
                removed.add(drop["filename"])
                print(f"    [dedup] {drop['filename']} (card {drop['card_num']}) "
                      f"duplicata de {keep['filename']} (card {keep['card_num']}) "
                      f"sim={sim:.3f} — removida")

    if not removed:
        return manifest_cards, 0

    # Remover dos manifests
    for card in manifest_cards:
        original_count = len(card.get("images", []))
        card["images"] = [img for img in card.get("images", []) if img["filename"] not in removed]
        # Renumerar ranks
        for rank_idx, img in enumerate(card["images"]):
            img["rank"] = rank_idx + 1
            img["status"] = "primary" if rank_idx == 0 else "fallback"

    # Deletar arquivos removidos
    for fname in removed:
        p = output_dir / fname
        if p.exists():
            p.unlink()

    return manifest_cards, len(removed)


# ── Extracao de imagens via PyMuPDF ─────────────────────────────────────────

def extract_images_from_pages(
    pdf_path,
    pages,
    card_num,
    card_name,
    output_dir,
    min_size,
    seen_xrefs,
):
    """
    Extrai imagens das paginas indicadas.
    Retorna lista de dicts com info de cada imagem extraida.
    """
    try:
        import fitz  # PyMuPDF
    except ImportError:
        print("ERRO: PyMuPDF nao instalado. Execute: pip install PyMuPDF")
        sys.exit(1)

    output_dir.mkdir(parents=True, exist_ok=True)
    extracted = []

    doc = fitz.open(str(pdf_path))
    page_screenshots: dict[int, str] = {}  # page_0 -> filename do screenshot

    for page_0 in pages:
        if page_0 >= len(doc):
            continue
        page = doc[page_0]
        page_num = page_0 + 1  # 1-based para output
        image_list = page.get_images(full=True)

        # Renderizar screenshot da pagina uma vez (antes de extrair imagens)
        if page_0 not in page_screenshots:
            label = f"card{card_num:02d}_{card_name}"
            screenshot_name = render_page_screenshot(doc, page_0, output_dir, label)
            if screenshot_name:
                page_screenshots[page_0] = screenshot_name

        img_idx = 0
        for img_info in image_list:
            xref = img_info[0]

            # Deduplicar: mesma imagem em multiplas paginas
            if xref in seen_xrefs:
                continue

            width_raw = img_info[2]
            height_raw = img_info[3]

            if max(width_raw, height_raw) < min_size:
                continue

            if width_raw < 200 or height_raw < 200:
                continue

            # Aspect ratio > 3.0 indica banner, rodape ou infografico horizontal
            # (ex: foto de equipe 1182x367 = 3.22, barras decorativas > 5.0)
            aspect = max(width_raw, height_raw) / max(min(width_raw, height_raw), 1)
            if aspect > 3.0:
                continue

            try:
                pix = fitz.Pixmap(doc, xref)

                if pix.n > 4:
                    pix = fitz.Pixmap(fitz.csRGB, pix)
                elif pix.n == 2:
                    pix = fitz.Pixmap(fitz.csRGB, pix)

                if max(pix.width, pix.height) < min_size:
                    continue

                img_idx += 1
                filename = f"card{card_num:02d}_{card_name}_p{page_num:02d}_img{img_idx}.jpeg"
                out_path = output_dir / filename

                pix.save(str(out_path))

                size_kb = out_path.stat().st_size / 1024
                if size_kb < 50:
                    out_path.unlink()
                    continue

                # Filtro de infografico: imagens com fundo predominantemente branco
                is_graphic = is_graphic_or_infographic(out_path)
                if is_graphic:
                    print(f"    [grafico] {filename} — fundo branco dominante, movido para fallback")

                seen_xrefs.add(xref)
                extracted.append({
                    "filename": filename,
                    "page": page_num,
                    "dimensions": f"{pix.width}x{pix.height}",
                    "size_kb": round(size_kb, 1),
                    "xref": xref,
                    "is_graphic": is_graphic,
                    "page_screenshot": page_screenshots.get(page_0),
                })
                print(f"    Extraida: {filename} ({pix.width}x{pix.height}, {size_kb:.0f}KB)")

            except Exception as e:
                print(f"    AVISO: xref {xref} pagina {page_num}: {e}")
                continue

    doc.close()
    return extracted


def get_adjacent_pages(page_nums, total_pages, radius=2):
    """Retorna paginas adjacentes (+/-radius) nao incluidas na lista original."""
    original_set = set(page_nums)
    adjacent = set()
    for p in page_nums:
        for d in range(1, radius + 1):
            if p - d >= 0:
                adjacent.add(p - d)
            if p + d < total_pages:
                adjacent.add(p + d)
    return sorted(adjacent - original_set)


def render_page_screenshot(doc, page_0: int, output_dir: Path, label: str) -> str | None:
    """
    Renderiza uma pagina do PDF como JPEG thumbnail (~800px de largura).
    Salva em output_dir com nome {label}_p{page_num}_PAGE.jpg.
    Retorna o filename ou None se falhar.

    Usado para comparacao visual: ver o que esta na pagina vs o que foi extraido.
    """
    try:
        import fitz

        page = doc[page_0]
        page_num = page_0 + 1

        # Calcular escala para ~800px de largura
        target_w = 800
        scale = target_w / page.rect.width
        mat = fitz.Matrix(scale, scale)
        pix = page.get_pixmap(matrix=mat, alpha=False)

        filename = f"{label}_p{page_num:02d}_PAGE.jpg"
        out_path = output_dir / filename
        pix.save(str(out_path), output="jpeg", jpg_quality=75)
        return filename
    except Exception as e:
        print(f"    AVISO: nao foi possivel renderizar pagina {page_0 + 1}: {e}")
        return None


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Extrai fotos contextuais de relatorio PDF para carrossel NTICS"
    )
    parser.add_argument(
        "--pdf", required=True,
        help="Caminho para o PDF do relatorio"
    )
    parser.add_argument(
        "--output", required=True,
        help="Pasta de saida para as fotos extraidas"
    )
    parser.add_argument(
        "--min-size", type=int, default=1000,
        help="Tamanho minimo em pixels (lado maior). Padrao: 1000"
    )
    parser.add_argument(
        "--top-n", type=int, default=3,
        help="Numero de opcoes de foto por card (inclui fallbacks). Padrao: 3"
    )
    args = parser.parse_args()

    pdf_path = Path(args.pdf)
    output_dir = Path(args.output)

    if not pdf_path.exists():
        print(f"ERRO: PDF nao encontrado: {pdf_path}")
        sys.exit(1)

    try:
        import pdfplumber
    except ImportError:
        print("ERRO: pdfplumber nao instalado. Execute: pip install pdfplumber")
        sys.exit(1)

    print(f"\n{'='*60}")
    print("EXTRACAO CONTEXTUAL DE FOTOS DE RELATORIO PDF")
    print(f"PDF: {pdf_path.name}")
    print(f"Output: {output_dir}")
    print(f"Min size: {args.min_size}px | Top-N: {args.top_n} opcoes/card")
    print(f"{'='*60}\n")

    # ── Fase 1: Indexar texto por pagina ────────────────────────────────────
    print(">> Fase 1: Lendo texto das paginas...")
    page_texts = {}
    total_pages = 0

    with pdfplumber.open(str(pdf_path)) as pdf:
        total_pages = len(pdf.pages)
        print(f"   Total de paginas: {total_pages}")
        for i, page in enumerate(pdf.pages):
            text = page.extract_text() or ""
            page_texts[i] = normalize(text)
            if (i + 1) % 10 == 0:
                print(f"   Lidas: {i+1}/{total_pages}")

    print(f"   Indexacao concluida: {total_pages} paginas\n")

    # ── Fase 2: Pontuar paginas por card ────────────────────────────────────
    print(">> Fase 2: Pontuando paginas por relevancia de card...")

    card_page_scores = {}

    for card in CARD_DEFINITIONS:
        if not card["needs_photo"]:
            continue

        card_num = card["card_num"]
        keywords = card["keywords"]
        scores = {}

        for page_0, text_norm in page_texts.items():
            s = score_page(text_norm, keywords)
            if s > 0:
                scores[page_0] = s

        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        card_page_scores[card_num] = ranked

        top_display = ranked[:args.top_n]
        pages_str = ", ".join(f"p{p+1}({s})" for p, s in top_display)
        print(f"   Card {card_num:02d} {card['card_name']}: {pages_str or '(sem match)'}")

    print()

    # ── Fase 3: Extrair imagens das top-N paginas por card ──────────────────
    print(">> Fase 3: Extraindo imagens das paginas relevantes...")

    seen_xrefs: set = set()
    manifest_cards = []

    cards_needing_photo = [c for c in CARD_DEFINITIONS if c["needs_photo"]]

    for card in cards_needing_photo:
        card_num = card["card_num"]
        card_name = card["card_name"]

        ranked = card_page_scores.get(card_num, [])
        top_pages_0 = [p for p, _ in ranked[:args.top_n]]
        top_scores = {p: s for p, s in ranked[:args.top_n]}

        print(f"\n   Card {card_num:02d} {card_name} — paginas candidatas: {[p+1 for p in top_pages_0]}")

        extracted = extract_images_from_pages(
            pdf_path, top_pages_0, card_num, card_name,
            output_dir, args.min_size, seen_xrefs
        )

        # Se nao extraiu nada, tenta paginas adjacentes como fallback
        if not extracted and top_pages_0:
            adj_pages = get_adjacent_pages(top_pages_0, total_pages, radius=2)
            print(f"    Sem imagens nas paginas principais. Tentando adjacentes: {[p+1 for p in adj_pages]}")
            extracted = extract_images_from_pages(
                pdf_path, adj_pages, card_num, card_name,
                output_dir, args.min_size, seen_xrefs
            )

        # Ordenar: fotos reais primeiro, infograficos no final (fallback de ultimo recurso)
        extracted.sort(key=lambda x: (1 if x.get("is_graphic") else 0))

        images_manifest = []
        for rank_idx, img in enumerate(extracted):
            page_0 = img["page"] - 1
            relevance_score = top_scores.get(page_0, 0.0)
            text_raw = page_texts.get(page_0, "")[:150]

            status = "primary" if rank_idx == 0 else "fallback"
            images_manifest.append({
                "filename": img["filename"],
                "page_screenshot": img.get("page_screenshot"),
                "rank": rank_idx + 1,
                "page": img["page"],
                "dimensions": img["dimensions"],
                "size_kb": img["size_kb"],
                "relevance_score": relevance_score,
                "status": status,
                "is_graphic": img.get("is_graphic", False),
                "page_text_snippet": text_raw,
            })

        if not images_manifest:
            print(f"    AVISO: Nenhuma imagem extraida para card {card_num}")

        page_scores_out = {str(p + 1): s for p, s in ranked[:args.top_n]}
        manifest_cards.append({
            "card_num": card_num,
            "card_name": card_name,
            "relevant_pages": [p + 1 for p in top_pages_0],
            "page_scores": page_scores_out,
            "images": images_manifest,
        })

    # Card CTA
    manifest_cards.append({
        "card_num": 8,
        "card_name": "cta",
        "relevant_pages": [],
        "page_scores": {},
        "images": [],
        "note": "CTA card nao precisa de foto — usa logos via Pillow pos-processamento",
    })

    manifest_cards.sort(key=lambda c: c["card_num"])

    # ── Fase 3b: Deduplicacao cross-card ────────────────────────────────────
    print("\n>> Fase 3b: Verificando duplicatas visuais entre cards...")
    manifest_cards, n_removed = deduplicate_cross_card(manifest_cards, output_dir)
    if n_removed == 0:
        print("   Nenhuma duplicata encontrada.")
    else:
        print(f"   {n_removed} imagem(ns) duplicada(s) removida(s).")

    # ── Fase 4: Gerar manifesto ─────────────────────────────────────────────
    print("\n>> Fase 4: Gerando manifesto...")

    total_extracted = sum(len(c["images"]) for c in manifest_cards)

    manifest = {
        "source_pdf": pdf_path.name,
        "extraction_date": str(date.today()),
        "parameters": {
            "min_size_px": args.min_size,
            "top_n_per_card": args.top_n,
        },
        "stats": {
            "total_pages": total_pages,
            "images_extracted": total_extracted,
        },
        "cards": manifest_cards,
    }

    manifest_path = output_dir / "manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    print(f"   Manifesto salvo: {manifest_path}")

    # ── Resumo ──────────────────────────────────────────────────────────────
    print(f"\n{'='*60}")
    print(f"RESULTADO: {total_extracted} fotos extraidas para {len(cards_needing_photo)} cards")
    for c in manifest_cards:
        if not c["images"]:
            status_str = "SEM FOTOS" if c["card_num"] != 8 else "OK (sem foto)"
        else:
            primary = c["images"][0]["filename"]
            fallbacks = len(c["images"]) - 1
            status_str = f"{primary} + {fallbacks} fallback(s)"
        print(f"  Card {c['card_num']:02d} {c['card_name']}: {status_str}")
    print(f"\nOutput: {output_dir}")
    print(f"Manifesto: {manifest_path}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
