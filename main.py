import os
from src.pdf_reader import extract_pages
from src.text_cleaner import clean_text
from src.embedder import create_embeddings
from src.search import search_query
from src.answer_extractor import extract_answer

PDF_FOLDER = "data/pdfs"
EMBED_FILE = "embeddings/page_vectors.pkl"

# Step 1: Read PDFs
all_pages = []
for pdf in os.listdir(PDF_FOLDER):
    pages = extract_pages(os.path.join(PDF_FOLDER, pdf))
    for p in pages:
        p["text"] = clean_text(p["text"])
    all_pages.extend(pages)

# Step 2: Create embeddings (run once)
if not os.path.exists(EMBED_FILE):
    create_embeddings(all_pages, EMBED_FILE)

# Step 3: Ask query
query = input("Ask a question: ")

best_page = search_query(query, EMBED_FILE)
answer = extract_answer(best_page["text"], query)

print("\nAnswer:", answer)
print("Source PDF:", best_page["pdf"])
print("Page Number:", best_page["page"])
