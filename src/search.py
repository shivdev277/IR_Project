import pickle
import os

import numpy as np
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

model = SentenceTransformer('all-MiniLM-L6-v2')


def _load_pages(embedding_file):
    """Load and validate page-level embeddings from disk."""
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

    return pages


def search_top_k(query, embedding_file, k=3):
    """
    Return the Top-K ranked pages/slides using cosine similarity.

    Returns a list of dictionaries with:
    - page: raw page object
    - score: cosine similarity score as float
    """
    pages = _load_pages(embedding_file)

    # Ensure vectors exist
    try:
        page_vecs = np.array([p["vector"] for p in pages])
    except Exception:
        raise RuntimeError(
            "Embeddings file does not contain page vectors. Recreate embeddings by running `scripts/generate_embeddings.py`.")

    if k <= 0:
        raise ValueError("k must be greater than 0.")

    query_vec = model.encode([query])
    scores = cosine_similarity(query_vec, page_vecs)[0]

    top_indices = np.argsort(scores)[::-1][:k]

    ranked_results = []
    for index in top_indices:
        ranked_results.append({
            "page": pages[int(index)],
            "score": float(scores[int(index)]),
        })

    return ranked_results


def _normalize_scores(raw_scores):
    if not raw_scores:
        return []

    min_score = float(min(raw_scores))
    max_score = float(max(raw_scores))
    if max_score == min_score:
        return [0.0 for _ in raw_scores]

    return [(float(score) - min_score) / (max_score - min_score) for score in raw_scores]


def _tokenize(text):
    return (text or "").lower().split()


def search_hybrid_top_k(query, embedding_file, k=3):
    """
    Return the Top-K ranked pages/slides using hybrid retrieval.

    final_score = (0.5 * normalized_bm25) + (0.5 * cosine_similarity)

    Returns a list of dictionaries with:
    - page: raw page object
    - score: final hybrid score
    - bm25: normalized BM25 score
    - cosine: cosine similarity score
    """
    pages = _load_pages(embedding_file)

    if k <= 0:
        raise ValueError("k must be greater than 0.")

    try:
        page_vecs = np.array([p["vector"] for p in pages])
    except Exception:
        raise RuntimeError(
            "Embeddings file does not contain page vectors. Recreate embeddings by running `scripts/generate_embeddings.py`.")

    # Build BM25 index for the document texts
    tokenized_docs = [_tokenize(p.get("text", "")) for p in pages]
    bm25 = BM25Okapi(tokenized_docs)
    query_tokens = _tokenize(query)
    bm25_scores = bm25.get_scores(query_tokens)
    bm25_normalized = _normalize_scores(list(bm25_scores))

    # Cosine similarity for semantic match
    query_vec = model.encode([query])
    cosine_scores = cosine_similarity(query_vec, page_vecs)[0]

    combined_scores = [
        (0.5 * bm25_normalized[idx]) + (0.5 * float(cosine_scores[idx]))
        for idx in range(len(pages))
    ]

    top_indices = np.argsort(combined_scores)[::-1][:k]

    ranked_results = []
    for index in top_indices:
        ranked_results.append({
            "page": pages[int(index)],
            "score": float(combined_scores[int(index)]),
            "bm25": float(bm25_normalized[int(index)]),
            "cosine": float(cosine_scores[int(index)]),
        })

    return ranked_results


def search_query(query, embedding_file):
    """Backward-compatible helper that returns only the best result."""
    ranked_results = search_top_k(query=query, embedding_file=embedding_file, k=1)
    if not ranked_results:
        raise RuntimeError("No ranked results were found for the given query.")

    top_result = ranked_results[0]
    return top_result["page"], top_result["score"]
