# Semantic Page-Level PDF & PPT Retrieval System

This project is an Information Retrieval (IR) system for semantic search over course documents.

Core pipeline:
- Sentence-BERT embeddings (`all-MiniLM-L6-v2`)
- Cosine similarity ranking
- Top-3 retrieval results
- FastAPI backend + React (Vite) frontend

## Project Structure

- `api.py`: FastAPI backend API (`/search`)
- `src/search.py`: embedding loading + cosine similarity ranking
- `src/answer_extractor.py`: retrieval-only sentence selection from top document
- `scripts/generate_embeddings.py`: embedding generation from PDF/PPT files
- `scripts/evaluate_precision_at_1.py`: IR evaluation script
- `evaluation/test_queries.json`: manual test set for Precision@1
- `frontend/`: React (Vite) UI

## Run the Project (Windows PowerShell)

### 1. Backend setup

```powershell
cd "E:\VS code\IR_Project"
python -m venv venv
& ".\venv\Scripts\Activate.ps1"
python -m pip install -r requirements.txt
```

### 2. Generate embeddings (first time or after document updates)

```powershell
python scripts\generate_embeddings.py
```

### 3. Start backend API

```powershell
python -m uvicorn api:app --reload
```

Backend will run at: `http://127.0.0.1:8000`

### 4. Start frontend (new terminal)

```powershell
cd "E:\VS code\IR_Project\frontend"
npm install
npm run dev -- --host 127.0.0.1 --port 5173
```

Frontend will run at the URL shown by Vite (typically `http://127.0.0.1:5173`).

## Search API Response Format

`POST /search`

```json
{
   "answer": "...",
   "results": [
      {
         "file": "file1.pdf",
         "page": 3,
         "score": 0.89
      },
      {
         "file": "file2.pptx",
         "page": 5,
         "score": 0.76
      },
      {
         "file": "file3.pdf",
         "page": 7,
         "score": 0.65
      }
   ]
}
```

Notes:
- `results` are sorted by cosine similarity in descending order.
- This is retrieval-only behavior (no generative model output).

## IR Evaluation (Precision@1)

Manual test set is defined in:
- `evaluation/test_queries.json`

Run evaluation:

```powershell
python scripts\evaluate_precision_at_1.py
```

Output includes:
- Query-wise Top-1 file prediction
- Relevance flag (`True` / `False`)
- Final `Precision@1`

Formula:

`Precision@1 = Correct Top-1 Results / Total Queries`

## Notes

- Keep `data/` and `embeddings/` out of git commits for large files.
- If your frontend uses a port other than 5173, backend CORS already allows localhost/127.0.0.1 with any port.
