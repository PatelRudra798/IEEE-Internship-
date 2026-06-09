# Task7 – Gemini RAG Studio

## Overview

This project implements a **Retrieval‑Augmented Generation (RAG) chatbot** using Gemini models. It extends the functionality of `task6` by adding a Knowledge Base, document ingestion, vector store indexing (FAISS), and context retrieval. The UI features three tabs:

1. **Chat Studio** – Streamed chat with optional RAG context.
2. **Live Tokenizer** – Visualize tokenization of arbitrary text.
3. **Knowledge Base** – Upload files or paste text, view indexed documents, and test retrieval.

The backend is a FastAPI server exposing endpoints for chat, tokenization, ingestion, RAG status, clear, and query. The frontend is vanilla HTML/JS/CSS with modern dark‑mode styling, glassmorphism, micro‑animations, and a polished user experience.

## Project Structure

```
task7/
├─ backend/
│   ├─ app.py          # FastAPI server with RAG endpoints
│   ├─ rag.py          # Chunking, embedding, FAISS index
│   ├─ tokenizer.py    # BPE‑style tokenizer (copied from task6)
│   ├─ .env            # Environment variables (e.g., GEMINI_API_KEY)
│   └─ requirements.txt
└─ frontend/
    ├─ index.html      # Main UI with three tabs
    ├─ app.js          # Frontend logic (RAG toggle, file upload, etc.)
    └─ styles.css      # Rich, premium styling
```

## Quick Start

```bash
# Install dependencies (run in task7 folder)
python -m pip install -r backend/requirements.txt

# Start the server (will listen on http://127.0.0.1:8002)
python -m uvicorn backend.app:app --host 127.0.0.1 --port 8002
```

Open `frontend/index.html` in a browser (served via any static server or directly from the file system) and start chatting!

---

*Feel free to customize the UI, model parameters, or swap the embedding model for a larger one.*
