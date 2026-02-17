# Semantic Page-Level PDF Retrieval

This repository implements a semantic, page-level PDF retrieval system: each PDF page is treated as a document, pages are embedded with SentenceTransformers, and queries return the most relevant page and an extracted answer.

Quick start (Windows PowerShell):

1. Clone:

   git clone <your-fork-url>
   cd "E:\VS code\IR_Project"

2. Create and activate a virtual environment (Windows PowerShell):

```powershell
python -m venv .venv
& ".venv\Scripts\Activate.ps1"
```

3. Install dependencies:

```powershell
& ".venv\Scripts\python.exe" -m pip install -r requirements.txt
```

4. Add your PDFs:

 - Place PDF files under `data/pdfs/` (create the folder if missing).

5. Generate embeddings:

```powershell
& ".venv\Scripts\python.exe" scripts\generate_embeddings.py
```

6. Run the app:

```powershell
& ".venv\Scripts\python.exe" main.py
```

Notes:
- The repository intentionally ignores `data/` and `embeddings/` (see `.gitignore`). Do not commit large PDFs or embedding files.
- If you want to share sample data with collaborators, consider adding a very small sample PDF or publishing embeddings as a release / external storage location.

If you want, I can add a tiny sample PDF (under a `sample/` folder) so the repo runs out-of-the-box — tell me if you want that and I'll add it.
