from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import pickle
import numpy as np

model = SentenceTransformer('all-MiniLM-L6-v2')

def search_query(query, embedding_file):
    with open(embedding_file, "rb") as f:
        pages = pickle.load(f)

    query_vec = model.encode([query])
    page_vecs = np.array([p["vector"] for p in pages])

    scores = cosine_similarity(query_vec, page_vecs)[0]

    best_index = scores.argmax()
    return pages[best_index]
