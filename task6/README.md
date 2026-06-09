# Task6 – Gemini Chat Studio (Baseline)

**A sleek, modern web UI** that showcases Gemini model generation with **live token visualization**, **streaming responses**, and **parameter controls**. This lightweight project is the foundation for the later RAG‑enabled `task7` version.

---

## ✨ Features

- **Streaming chat** with token‑by‑token typewriter animation.
- **Live token visualizer** (color‑coded sub‑word tokens, token table, usage metrics).
- **Dynamic parameter panel** – model selection, temperature, top‑p, top‑k, max‑output‑tokens.
- **Session token accounting** with progress bar and warnings when limits are hit.
- **Responsive dark‑mode UI** using glass‑morphism, gradients, and micro‑animations.
- **Extensible architecture** – clean separation of backend (FastAPI) and vanilla JavaScript frontend.

---

## 🛠️ Technologies

- **Frontend**: HTML5, CSS3 (custom design system, no framework), vanilla JavaScript (ES2022).
- **Backend**: Python 3.13, FastAPI, Uvicorn.
- **Tokenizer**: Custom BPE‑style tokenizer (ported from Gemini examples).
- **Styling**: CSS variables, glass‑morphism, gradient palettes, smooth transitions.
- **Deployment**: Simple `uvicorn` command; can be containerized with Docker if desired.

---

## 🎯 Use Cases

- **Model prototyping** – quickly test Gemini prompts, temperature, and top‑p settings.
- **Educational demos** – visualize how tokenization works in real time.
- **UI/UX reference** – serves as a high‑quality example for building interactive LLM front‑ends.
- **Base for extensions** – easy to add RAG, tool‑calling, or multimodal capabilities (see `task7`).

---

## 📂 Project Layout

```
task6/
├─ backend/
│   ├─ app.py          # FastAPI server exposing /api/chat and /api/tokenize
│   ├─ tokenizer.py    # BPE‑style tokenizer used by the Live Tokenizer tab
│   └─ .env            # Environment variables (e.g., GEMINI_API_KEY)
└─ frontend/
    ├─ index.html      # UI with two tabs: Chat Studio & Live Tokenizer
    ├─ app.js          # Frontend logic (streaming, token view, controls)
    └─ styles.css      # Dark‑mode, glass‑morphism design
```

---

## 🚀 Quick Start

```bash
# 1️⃣ Install backend dependencies (run from the task6 folder)
python -m pip install -r backend/requirements.txt  # create this file if missing

# 2️⃣ Launch the FastAPI server (default port 8001)
python -m uvicorn backend.app:app --host 127.0.0.1 --port 8001
```

```bash
# 3️⃣ Open the UI (any static server works) – e.g.:
python -m http.server 8080 --directory frontend
# Then visit http://localhost:8080 in your browser.
```

---

## 📖 Documentation

- **Backend** – see `backend/README.md` for API details.
- **Frontend** – see `frontend/README.md` for UI component explanations and customization tips.

---

## 🤝 Contributing

Fork the repository, create a feature branch, and open a pull request. Keep the design system consistent and update the README sections when adding new features.

---

*Enjoy building with Gemini!*
