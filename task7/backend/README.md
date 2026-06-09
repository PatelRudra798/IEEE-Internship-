# Backend – Gemini RAG Studio (task7)

This directory contains the server‑side components for the **Retrieval‑Augmented Generation (RAG) chatbot**.

## Files

- **`app.py`** – FastAPI entry point exposing the following endpoints:
  - `POST /api/chat` – Normal Gemini chat with optional RAG context.
  - `POST /api/tokenize` – Tokenizer service used by the Live Tokenizer tab.
  - `POST /api/ingest/file` – Upload a document (PDF, txt, etc.) → chunk → embed → FAISS.
  - `POST /api/ingest/text` – Ingest raw text with a custom source label.
  - `GET  /api/rag/status` – Current KB stats (documents, chunks, index size).
  - `POST /api/rag/clear` – Reset the knowledge base.
  - `POST /api/rag/query` – Test retrieval – returns top‑k similar chunks.
- **`rag.py`** – Core RAG utilities:
  - Sentence‑level chunking (via NLTK).
  - Embedding generation using `sentence‑transformers` (`all‑MiniLM‑L6‑v2`).
  - FAISS `IndexFlatL2` for fast vector similarity search.
  - Helper functions for ingestion, clearing, status, and querying.
- **`tokenizer.py`** – BPE‑style tokenizer (ported from `task6`).
- **`.env`** – Environment config (e.g., `GEMINI_API_KEY`).
- **`requirements.txt`** – Python dependencies needed to run the backend.

## Development

```bash
# Install deps (run from the task7 folder)
python -m pip install -r backend/requirements.txt

# Run the development server
python -m uvicorn backend.app:app --reload
```

The server runs on `http://127.0.0.1:8002`.

---

**Contributing** – Follow the standard GitHub workflow: fork, create a feature branch, open a pull request, and ensure the README stays up‑to‑date.
