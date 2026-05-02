import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.search import search_top_k
from src.answer_extractor import extract_answer

app = FastAPI(
    title="Semantic IR API",
    description="Semantic Page-Level PDF & PPT Retrieval System",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1)(:\d+)?$",
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


class RankedResult(BaseModel):
    file: str
    page: int
    score: float


class SearchResponse(BaseModel):
    answer: str
    results: list[RankedResult]


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/")
def root():
    return {"message": "Semantic IR API running"}


@app.post("/search", response_model=SearchResponse)
def search(request: SearchRequest) -> SearchResponse:
    """
    Retrieve Top-3 ranked pages/slides for *query* from pre-built embeddings.
    Ranking is based strictly on cosine similarity (descending).
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

    # Run Top-K cosine-similarity search over all page embeddings
    try:
        ranked_results = search_top_k(request.query, embedding_file, k=3)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))

    if not ranked_results:
        raise HTTPException(status_code=404, detail="No ranked results found for this query.")

    # Retrieval-only answer: choose the best matching sentence from top-ranked page text
    top_page = ranked_results[0]["page"]
    answer = extract_answer(top_page["text"], request.query)

    response_results = [
        RankedResult(
            file=os.path.basename(str(result["page"].get("pdf", "Unknown"))),
            page=int(result["page"].get("page", 0)),
            score=round(float(result["score"]), 4),
        )
        for result in ranked_results
    ]

    return SearchResponse(
        answer=answer,
        results=response_results,
    )
