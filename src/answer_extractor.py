import re
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

model = SentenceTransformer('all-MiniLM-L6-v2')

def extract_answer(page_text, query):
    # Split using . ? !
    sentences = re.split(r'[?.!]', page_text)

    # Remove very short sentences (headings)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 40]

    if not sentences:
        return "Answer not found clearly on this page."

    sentence_vecs = model.encode(sentences)
    query_vec = model.encode([query])

    scores = cosine_similarity(query_vec, sentence_vecs)[0]
    best_sentence = sentences[scores.argmax()]

    return best_sentence
