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
# Request / Response models
# ---------------------------------------------------------------------------

class SearchRequest(BaseModel):
    course: str
    query: str


class SearchResponse(BaseModel):
    answer: str
    file: str
    page: int
    # Cosine similarity score of the best matching page (0.0 – 1.0)
    score: float


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/")
def root():
    return {"message": "Semantic IR API running"}


@app.post("/search", response_model=SearchResponse)
def search(request: SearchRequest) -> SearchResponse:
    """
    Retrieve the most relevant page for *query* from the pre-built embeddings
    of the requested *course* using cosine-similarity ranking (pure IR, no LLM).
    """
    # Build the path to the course's pre-computed embedding file
    embedding_file = os.path.join("embeddings", f"{request.course}.pkl")

    if not os.path.exists(embedding_file):
        raise HTTPException(
            status_code=404,
            detail=(
                f"Embeddings for course '{request.course}' not found. "
                "Generate them first using scripts/generate_embeddings.py."
            ),
        )

    # Run cosine-similarity search over all page embeddings
    try:
        best_page, score = search_query(request.query, embedding_file)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))

    # Extract the most relevant snippet from the best-matching page text
    answer = extract_answer(best_page["text"], request.query)

    return SearchResponse(
        answer=answer,
        file=best_page["pdf"],
        page=best_page["page"],
        # Round to 4 decimal places for a clean, readable score
        score=round(score, 4),
    )
