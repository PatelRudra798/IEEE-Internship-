# Frontend – Gemini Chat Studio (task6)

The `frontend` folder provides the static web interface for the original Gemini chat UI.

## Components

- **`index.html`** – Main page containing two tabs:
  1. **Chat Studio** – Interactive chat with streaming responses, token usage tracker, and model parameter controls.
  2. **Live Tokenizer** – Text area that sends input to `/api/tokenize` and visualizes the token stream with color‑coded spans and a token table.
- **`app.js`** – Vanilla JavaScript handling:
  - Form submission and streaming of Gemini responses.
  - Typewriter animation and token usage tracking.
  - Slider and dropdown UI controls.
  - Live tokenizer debounce logic and rendering.
- **`styles.css`** – Premium dark‑mode styling using CSS variables, glass‑morphism effects, smooth gradients, and micro‑animations. Includes responsive layout for mobile devices.

## Development

The UI is purely static; you can open `index.html` directly in a browser or serve it with any static file server (e.g., `python -m http.server`). The code expects the backend API to be reachable at the same origin (default `http://127.0.0.1:8001`).

## Customization

- **Design** – All colors, fonts, and spacing are defined at the top of `styles.css` as CSS variables. Adjust them to match your branding.
- **Functionality** – Extend `app.js` to add new tabs or integrate additional APIs. The code is organized into clear sections with comments.

---

> This folder serves as the baseline UI that `task7` builds upon, adding a third Knowledge Base tab and RAG‑specific controls.
