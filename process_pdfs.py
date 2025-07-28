#!/usr/bin/env python3
import json
import re
import statistics
from collections import Counter
from pathlib import Path
import fitz  # PyMuPDF


def extract_text_blocks(doc, page_limit=None):
    """Extracts all text blocks with metadata from a PDF document."""
    blocks_data = []
    pages = range(len(doc)) if page_limit is None else range(min(len(doc), page_limit))

    for page_num in pages:
        page = doc[page_num]
        blocks = page.get_text("dict", flags=11)["blocks"]
        for b in blocks:
            for line in b.get("lines", []):
                for span in line.get("spans", []):
                    text = span.get("text", "").strip()
                    if not text:
                        continue
                    blocks_data.append({
                        "text": text,
                        "font_size": span.get("size"),
                        "font_name": span.get("font"),
                        "page": page_num + 1,
                        "y_pos": span.get("bbox")[1]
                    })
    return blocks_data


def get_body_text_style(blocks):
    """Determines the most frequent (mode) font size for body text."""
    if not blocks:
        return 12, ""
    sizes = [b["font_size"] for b in blocks if b["font_size"] < 20]
    sizes = sizes or [b["font_size"] for b in blocks]
    try:
        body_size = statistics.mode(sizes)
    except statistics.StatisticsError:
        body_size = sorted(Counter(sizes).items(), key=lambda x: x[1], reverse=True)[0][0]
    return body_size, ""


def identify_and_classify_headings(blocks, body_size):
    """Scores text blocks to detect headings and assign H1/H2/H3 levels."""
    headings = []
    title_info = None
    # Title: first page largest font
    first_blocks = [b for b in blocks if b["page"] == 1]
    if first_blocks:
        max_font = max(b["font_size"] for b in first_blocks)
        for b in first_blocks:
            if b["font_size"] == max_font:
                title_info = {"text": b["text"], "page": 1}
                break

    # pattern for numbering
    heading_pattern = re.compile(r"^\s*(\d+(?:\.\d+)*\.?|[A-Z]\.)\s+")
    candidates = []

    for b in blocks:
        text = b["text"]
        fs = b["font_size"]
        fname = b["font_name"].lower()
        # skip title itself
        if title_info and b["page"] == 1 and text == title_info["text"]:
            continue
        score = 0
        if fs > body_size + 1:
            score += 2
        if "bold" in fname:
            score += 1
        if heading_pattern.match(text):
            score += 5
        if len(text.split()) < 15:
            score += 1
        if text.isupper() and len(text) > 2:
            score += 1
        if score >= 4:
            candidates.append(b)

    if not candidates:
        return [], title_info

    # Map font sizes to H1/H2/H3 by descending size
    sizes = sorted({c["font_size"] for c in candidates}, reverse=True)
    style_map = {size: f"H{i+1}" for i, size in enumerate(sizes[:3])}

    for b in candidates:
        lvl = style_map.get(b["font_size"])
        if lvl:
            headings.append({
                "level": lvl,
                "text": b["text"],
                "page": b["page"],
                "y_pos": b["y_pos"]
            })

    # sort by page and position
    headings = sorted(headings, key=lambda h: (h["page"], h["y_pos"]))
    return headings, title_info


def group_text_into_sections(blocks, headings):
    """Groups raw text blocks under the most recent heading."""
    sections = []
    if not headings:
        return []

    for i, heading in enumerate(headings):
        start_page = heading['page']
        start_y = heading['y_pos']
        # Determine the boundary of the section
        end_page = headings[i+1]['page'] if i + 1 < len(headings) else float('inf')
        end_y = headings[i+1]['y_pos'] if i + 1 < len(headings) else float('inf')

        content = []
        for block in blocks:
            after_start = (block['page'] > start_page) or \
                          (block['page'] == start_page and block['y_pos'] > start_y)
            before_end = (block['page'] < end_page) or \
                         (block['page'] == end_page and block['y_pos'] < end_y)
            # skip block if it's one of the headings
            is_heading = any(h['text'] == block['text'] and h['page'] == block['page'] for h in headings)
            if after_start and before_end and not is_heading:
                content.append(block['text'])
        sections.append({
            'heading_text': heading['text'],
            'heading_level': heading['level'],
            'page': heading['page'],
            'content': "\n".join(content)
        })
    return sections


def generate_outline_from_pdf(pdf_path: Path) -> dict:
    """Opens a PDF and returns a dict with title, outline list, and sections."""
    try:
        doc = fitz.open(str(pdf_path))
    except Exception as e:
        return {"error": f"Could not open PDF: {e}"}

    blocks = extract_text_blocks(doc)
    doc.close()

    if not blocks:
        return {"title": "", "outline": [], "sections": []}

    body_size, _ = get_body_text_style(blocks)
    headings, title_info = identify_and_classify_headings(blocks, body_size)
    title = title_info.get("text", "Untitled") if title_info else "Untitled"

    outline = [{"level": h["level"], "text": h["text"], "page": h["page"]} for h in headings]
    sections = group_text_into_sections(blocks, headings)

    return {"title": title, "outline": outline, "sections": sections}


def process_pdfs():
    input_dir = Path("/app/input")
    output_dir = Path("/app/output")
    
    # Debug: Check directory and glob pattern
    print(f"Input directory: {input_dir}")
    print(f"Input directory exists: {input_dir.exists()}")
    print(f"Input directory is_dir: {input_dir.is_dir()}")
    
    # Check what glob finds
    pdf_files = list(input_dir.glob("*.pdf"))
    print(f"PDF files found by glob: {pdf_files}")
    print(f"Number of PDF files: {len(pdf_files)}")
    
    # Also try different patterns
    all_files = list(input_dir.glob("*"))
    print(f"All files in directory: {all_files}")
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    if not pdf_files:
        print(f"[!] No PDFs found in {input_dir}")
        return
    
    for pdf_file in pdf_files:
        result = generate_outline_from_pdf(pdf_file)
        output_file = output_dir / f"{pdf_file.stem}.json"
        output_file.write_text(
            json.dumps(result, indent=2, ensure_ascii=False), 
            encoding="utf-8"
        )
        print(f"[✓] {pdf_file.name} → {output_file.name}")


if __name__ == "__main__":
    print("Starting PDF processing…")
    process_pdfs()
    print("Completed PDF processing.")
