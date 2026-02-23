import os
import sys
import pickle
from sentence_transformers import SentenceTransformer

# -------------------------------------------------
# Fix Python path so that src/ can be imported
# -------------------------------------------------
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.pdf_reader import extract_pages
from src.ppt_reader import extract_slides
from src.text_cleaner import clean_text

# -------------------------------------------------
# Load Sentence-BERT model
# -------------------------------------------------
model = SentenceTransformer("all-MiniLM-L6-v2")

# -------------------------------------------------
# Paths
# -------------------------------------------------
BASE_DATA_PATH = "data/courses"
OUTPUT_EMBED_PATH = "embeddings"

os.makedirs(OUTPUT_EMBED_PATH, exist_ok=True)

# -------------------------------------------------
# Process each course
# -------------------------------------------------
for course in os.listdir(BASE_DATA_PATH):
    course_path = os.path.join(BASE_DATA_PATH, course)

    if not os.path.isdir(course_path):
        continue

    print(f"\nProcessing course: {course}")
    all_pages = []

    # -------------------------------------------------
    # Read PDFs and PPTX files
    # -------------------------------------------------
    for file in os.listdir(course_path):
        file_path = os.path.join(course_path, file)

        try:
            if file.lower().endswith(".pdf"):
                pages = extract_pages(file_path)

            elif file.lower().endswith(".pptx"):
                pages = extract_slides(file_path)

            else:
                continue

            for p in pages:
                p["text"] = clean_text(p["text"])
                all_pages.append(p)

        except Exception as e:
            print(f"Failed to process {file}: {e}")

    # -------------------------------------------------
    # If no content found
    # -------------------------------------------------
    if not all_pages:
        print(f"No readable PDF/PPTX content found for {course}")
        continue

    # -------------------------------------------------
    # Create embeddings
    # -------------------------------------------------
    texts = [p["text"] for p in all_pages]
    vectors = model.encode(texts, show_progress_bar=True)

    for i in range(len(all_pages)):
        all_pages[i]["vector"] = vectors[i]

    # -------------------------------------------------
    # Save embeddings
    # -------------------------------------------------
    output_file = os.path.join(OUTPUT_EMBED_PATH, f"{course}.pkl")

    with open(output_file, "wb") as f:
        pickle.dump(all_pages, f)

    print(f"Saved embeddings → {output_file}")

print("\n✅ Embedding generation completed successfully.")
