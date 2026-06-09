# Backend – Gemini Chat Studio (task6)

The `backend` folder contains the FastAPI server that powers the original Gemini chat UI.

## Endpoints

- **`POST /api/chat`** – Streams Gemini responses. Accepts model, temperature, top‑p, top‑k, max‑output‑tokens, and the conversation history.
- **`POST /api/tokenize`** – Tokenizes a given string using the custom BPE tokenizer (`tokenizer.py`). Returns token list, counts, and visual metadata.

## Files

- **`app.py`** – FastAPI app with streaming logic and endpoint definitions.
- **`tokenizer.py`** – BPE‑style tokenizer implementation (ported from the Gemini‑LLM example).
- **`.env`** – Environment variables (e.g., `GEMINI_API_KEY`).
- **`requirements.txt`** – Python dependencies required for the backend (`fastapi`, `uvicorn`, `python‑multipart`, etc.).

## Development

```bash
# Install dependencies (run from task6 folder)
python -m pip install -r backend/requirements.txt

# Run the server (default port 8001)
python -m uvicorn backend.app:app --host 127.0.0.1 --port 8001
```

The server will be reachable at `http://127.0.0.1:8001` and the frontend will call the API endpoints directly.
