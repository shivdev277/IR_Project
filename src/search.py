from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import pickle
import numpy as np
import os

model = SentenceTransformer('all-MiniLM-L6-v2')


def search_query(query, embedding_file):
    if not os.path.exists(embedding_file):
        raise FileNotFoundError(
            f"Embeddings file not found: {embedding_file}.\n"
            "Generate embeddings first using `scripts/generate_embeddings.py` or run the app which can create them.")

    try:
        with open(embedding_file, "rb") as f:
            pages = pickle.load(f)
    except EOFError:
        raise RuntimeError(
            f"Embeddings file appears empty or corrupted: {embedding_file}.\n"
            "Recreate it by running `scripts/generate_embeddings.py`.")
    except Exception as e:
        raise RuntimeError(f"Failed to read embeddings from {embedding_file}: {e}")

    if not pages:
        raise RuntimeError(f"Embeddings file {embedding_file} contains no pages.")

    # Ensure vectors exist
    try:
        page_vecs = np.array([p["vector"] for p in pages])
    except Exception:
        raise RuntimeError(
            "Embeddings file does not contain page vectors. Recreate embeddings by running `scripts/generate_embeddings.py`.")

    query_vec = model.encode([query])

    scores = cosine_similarity(query_vec, page_vecs)[0]

    best_index = scores.argmax()
    return pages[best_index]
