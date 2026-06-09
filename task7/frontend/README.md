# Frontend – Gemini RAG Studio (task7)

The `frontend` folder holds the static web UI for the RAG chatbot. It consists of three main parts:

- **`index.html`** – The main page with a dark‑mode, glass‑morphism layout and three tabs:
  1. **Chat Studio** – Interactive chat with streaming responses, token usage tracker, and a RAG toggle.
  2. **Live Tokenizer** – Real‑time tokenization visualizer with token‑by‑token colors.
  3. **Knowledge Base** – Drag‑and‑drop file upload, paste‑to‑ingest, status overview, and a test‑retrieval panel.
- **`app.js`** – Vanilla JavaScript handling UI interactions, streaming, file uploads, and rendering of RAG source badges.
- **`styles.css`** – Premium CSS using custom design tokens, smooth gradients, micro‑animations, and responsive layout.

The UI follows the same visual language as `task6` but adds RAG‑specific controls (toggle switch, top‑k slider, source badges) and a knowledge‑base dashboard.

### Development

Open `index.html` directly in a browser or serve it via any static‑file server (e.g., `python -m http.server`). The UI talks to the backend at `http://127.0.0.1:8002`.

---

**Customization** – Adjust colors in `styles.css` (CSS variables at the top) to match your branding. The JavaScript is modular; you can replace the RAG‑specific parts with your own retrieval logic.
