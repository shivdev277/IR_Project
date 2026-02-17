from sentence_transformers import SentenceTransformer
import pickle

model = SentenceTransformer('all-MiniLM-L6-v2')

def create_embeddings(pages, save_path):
    texts = [p["text"] for p in pages]
    embeddings = model.encode(texts)

    for i in range(len(pages)):
        pages[i]["vector"] = embeddings[i]

    with open(save_path, "wb") as f:
        pickle.dump(pages, f)
