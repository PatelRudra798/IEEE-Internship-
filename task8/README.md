# Document QA System (RAG) – Portfolio Demo

**A production‑grade Retrieval‑Augmented Generation (RAG) application** that lets users upload PDF documents, index them, and ask questions about their contents. The system is built with:

- **FastAPI** – backend REST API
- **Streamlit** – modern chat‑style UI
- **ChromaDB** – persistent vector database
- **Sentence‑Transformers** (`all‑MiniLM‑L6‑v2`) – embeddings
- **LLM provider abstraction** – Ollama (default), with optional OpenAI or Gemini support
- **Docker & Docker‑Compose** – one‑click containerised deployment

---

## Table of Contents

1. [Project Structure](#project-structure)
2. [Prerequisites](#prerequisites)
3. [Setup & Installation](#setup--installation)
4. [Running the Application](#running-the-application)
5. [API Overview](#api-overview)
6. [Frontend UI Overview](#frontend-ui-overview)
7. [Testing the RAG Pipeline](#testing-the-rag-pipeline)
8. [Configuration (`.env`)](#configuration-env)
9. [Extending the LLM Provider](#extending-the-llm-provider)
10. [Known Issues & Windows Tips](#known-issues--windows-tips)
11. [License](#license)

---

## Project Structure

```
document-qa/               # Root of the project (this folder)
├── backend/               # FastAPI service
│   ├── api/               # Route definitions (health, upload, chat)
│   ├── config/            # Pydantic settings loader
│   ├── models/            # Request/response schemas (Pydantic)
│   ├── services/          # Core services (pdf, chunk, embedding, vector, rag, llm)
│   ├── requirements.txt   # Backend dependencies
│   ├── Dockerfile         # Backend Docker image
│   └── main.py            # FastAPI entry point
│
├── frontend/              # Streamlit UI
│   ├── api_client.py      # Thin HTTP wrapper for the backend
│   ├── app.py             # Streamlit app – chat UI, uploader, document list
│   ├── requirements.txt   # Frontend dependencies (streamlit, httpx)
│   └── Dockerfile         # Frontend Docker image
│
├── uploads/               # Uploaded PDFs (mounted as a Docker volume)
├── chroma_db/             # Persistent ChromaDB store (Docker volume)
├── test_rag_pipeline.py   # Small integration test script (see walkthrough)
├── docker-compose.yml     # Orchestrates backend + frontend containers
├── .env.example           # Template for environment variables
├── .env                   # Active configuration (copy from .env.example)
├── requirements.txt       # Root‑level combined deps (optional for local dev)
└── README.md              # ← **this file**
```

---

## Prerequisites

| Tool | Minimum version |
|------|-----------------|
| **Docker Desktop** | 4.30+ (includes Docker Engine & Compose) |
| **Python** | 3.10 (the Docker images use `python:3.10-slim`) |
| **Git** | optional – useful for cloning the repo |
| **Ollama** | required only if you intend to use the default LLM provider (Llama 3). Install from <https://ollama.com> and run `ollama serve`.

> **Windows tip** – Docker Desktop installs a Linux VM under the hood. The `host.docker.internal` hostname is used inside containers to reach services on the host (e.g., Ollama).

---

## Setup & Installation

### 1. Clone the repository (or copy the `task8` folder)
```bash
git clone <repo‑url>  # if you have a remote repo
# otherwise the folder already exists at
# C:\Users\rudra\IEEE(Internship)\task8
```

### 2. Create a virtual environment for local development (optional)
```bash
cd C:\Users\rudra\IEEE(Internship)\task8
python -m venv venv
.\venv\Scripts\activate  # PowerShell / CMD
pip install -r requirements.txt
```

### 3. Copy the example environment file and edit values
```bash
copy .env.example .env
```
Edit `.env` with a text editor. Important keys:
- `LLM_PROVIDER` – `ollama` (default), `openai`, or `gemini`
- `OLLAMA_HOST` – keep as `http://host.docker.internal:11434` when running inside Docker
- `OPENAI_API_KEY` / `GEMINI_API_KEY` – fill only if you switch providers
- `EMBEDDING_MODEL` – keep `all-MiniLM-L6-v2`
- `CHROMA_DB_PATH` – default `./chroma_db`
- `UPLOADS_PATH` – default `./uploads`

---

## Running the Application

### Using Docker Compose (recommended for a clean, reproducible environment)
```bash
docker compose up --build
```
- Backend will be reachable at **http://localhost:8000**
- Streamlit UI will be reachable at **http://localhost:8501**
- Volumes `rag_chroma_db` and `rag_uploads` persist across container restarts.

### Without Docker (local dev only)
```bash
# Activate venv first
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
# In another terminal, run the UI
streamlit run frontend/app.py --server.port=8501 --server.address=0.0.0.0
```
Make sure the `BACKEND_URL` environment variable in the UI points to `http://localhost:8000` (the default).

---

## API Overview

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | `GET` | Simple health check (`{"status":"healthy"}`) |
| `/upload` | `POST` (multipart) | Accepts a PDF, extracts text, chunks, embeds, and stores in ChromaDB. Returns `chunks_processed`.
| `/documents` | `GET` | Lists indexed PDF files with their chunk counts.
| `/documents/{filename}` | `DELETE` | Removes a document from the DB **and** deletes the uploaded file.
| `/ask` | `POST` (`{"question":"..."}`) | Runs the RAG pipeline and returns `answer` plus a list of source citations.

All routes return JSON and follow the Pydantic models defined in `backend/models/response_models.py`.

---

## Frontend UI Overview (Streamlit)

The Streamlit UI mimics a ChatGPT‑style conversation:
1. **Sidebar** – Upload PDFs, view indexed documents, delete files, and see backend connection status.
2. **Main area** – Chat history displayed with `st.chat_message`. Assistant responses include an expandable *Sources* panel showing the document name, page number, similarity score, and a snippet of the retrieved chunk.
3. **Styling** – Uses the modern *Outfit* Google Font, gradient titles, dark‑mode‑friendly cards, and subtle hover effects for a premium look.

---

## Testing the RAG Pipeline

A minimal integration script lives at `test_rag_pipeline.py`. It:
- Generates a temporary PDF (via `reportlab`).
- Runs the PDF extraction, chunking, embedding, and ChromaDB storage.
- Performs a similarity search.
- Cleans up after itself (Windows‑aware file‑lock handling).

Run it with:
```bash
python test_rag_pipeline.py
```
The script should finish with:
```
Cleanup complete. All RAG components verified successfully!
```
If you see errors, ensure that no other process holds the `test_chroma_db` folder (e.g., a stray Python REPL).

---

## Configuration (`.env`)

Below is a snippet of the most common settings. All of them are already present in `.env.example`.
```dotenv
# Server
PORT=8000
HOST=0.0.0.0

# LLM Provider (ollama | openai | gemini)
LLM_PROVIDER=ollama
OLLAMA_HOST=http://host.docker.internal:11434
OLLAMA_MODEL=llama3

# Optional API keys for non‑ollama providers
OPENAI_API_KEY=
GEMINI_API_KEY=

# Embedding & Vector DB
EMBEDDING_MODEL=all-MiniLM-L6-v2
CHROMA_DB_PATH=./chroma_db
UPLOADS_PATH=./uploads
TOP_K=5
```

---

## Extending the LLM Provider

The abstraction lives in `backend/services/llm_service.py`. To add a new provider:
1. Subclass `BaseLLMProvider` and implement `generate_answer(self, context, question)`.
2. Add the initialization logic (e.g., API client) inside the new class.
3. Extend `get_llm_provider()` to recognise a new `LLM_PROVIDER` value and return the new class.
4. Update the Dockerfile (if extra system packages are needed) and add any required pip packages to `backend/requirements.txt`.

---

## Known Issues & Windows Tips

- **Symlink warning from `sentence‑transformers`** – Windows does not allow the library to use symlinks for caching. This only increases disk usage; the models still load correctly.
- **ChromaDB folder lock on cleanup** – The test script now explicitly deletes the client (`del vector_service`) and forces garbage collection before removing the `test_chroma_db` directory.
- **Ollama connectivity** – Inside Docker the backend reaches the host Ollama instance via `host.docker.internal`. If you run Ollama *inside* a container, change `OLLAMA_HOST` accordingly (e.g., `http://ollama:11434`).
- **Future deprecation** – The `google.generativeai` package is deprecated. Switch to `google.genai` when you decide to use Gemini.

---

## License

This demo project is released under the **MIT License** – feel free to copy, modify, and use it in your portfolio or personal projects.

---

*Happy hacking! 🎉*
