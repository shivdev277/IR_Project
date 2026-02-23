import os
import fitz  # PyMuPDF

def extract_pages(pdf_path):
    doc = fitz.open(pdf_path)
    pages = []

    for page_num, page in enumerate(doc):
        text = page.get_text().strip()
        if len(text) > 50:  # ignore empty pages
            pages.append({
                "pdf": os.path.basename(pdf_path),
                "page": page_num + 1,
                "text": text
            })
    return pages
