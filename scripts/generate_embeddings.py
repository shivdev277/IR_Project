#!/usr/bin/env python
"""
Generate embeddings from PDFs and save them to the embeddings folder.

Usage (PowerShell):
  cd "E:\VS code\IR_Project"
  & ".venv\Scripts\python.exe" scripts\generate_embeddings.py

"""
import os
import argparse

from src.pdf_reader import extract_pages
from src.text_cleaner import clean_text
from src.embedder import create_embeddings


def main():
    parser = argparse.ArgumentParser(description="Generate embeddings from PDFs")
    parser.add_argument("--pdf-folder", default="data/pdfs", help="Folder containing PDF files")
    parser.add_argument("--out", default="embeddings/page_vectors.pkl", help="Output pickle path")
    args = parser.parse_args()

    if not os.path.isdir(args.pdf_folder):
        print(f"No PDF folder found at {args.pdf_folder}. Place PDFs there and run again.")
        return

    pages = []
    for fname in os.listdir(args.pdf_folder):
        if not fname.lower().endswith('.pdf'):
            continue
        path = os.path.join(args.pdf_folder, fname)
        ps = extract_pages(path)
        for p in ps:
            p["text"] = clean_text(p["text"])
        pages.extend(ps)

    if not pages:
        print("No pages were extracted from PDFs. Ensure your PDFs are not empty and retry.")
        return

    out_dir = os.path.dirname(args.out)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    print(f"Creating embeddings for {len(pages)} pages...")
    create_embeddings(pages, args.out)
    print(f"Saved embeddings to {args.out}")


if __name__ == '__main__':
    main()
