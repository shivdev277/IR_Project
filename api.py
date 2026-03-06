import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.search import search_query
from src.answer_extractor import extract_answer

app = FastAPI(
    title="Semantic IR API",
    description="Semantic Page-Level PDF & PPT Retrieval System",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Request model
# ---------------------------------------------------------------------------

class SearchRequest(BaseModel):
    course: str
    query: str


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/")
def root():
    return {"message": "Semantic IR API running"}


@app.post("/search")
def search(request: SearchRequest):
    embedding_file = os.path.join("embeddings", f"{request.course}.pkl")

    if not os.path.exists(embedding_file):
        raise HTTPException(
            status_code=404,
            detail=f"Embeddings for course '{request.course}' not found. "
                   "Generate them first using scripts/generate_embeddings.py.",
        )

    try:
        best_page = search_query(request.query, embedding_file)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))

    answer = extract_answer(best_page["text"], request.query)

    return {
        "answer": answer,
        "file": best_page["pdf"],
        "page": best_page["page"],
    }
