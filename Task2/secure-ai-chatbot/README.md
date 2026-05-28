# Secure AI Chatbot

A production-ready, highly secure backend AI chatbot API built with FastAPI and Python. This project enforces strict safety guardrails, blocks prompt injections, and guarantees responses in a structured JSON format.

## Features
- **FastAPI Backend**: Asynchronous, fast, and documented API.
- **Strict Guardrails**: Prevents hacking, malware, phishing, and prompt injections using regex and keyword filtering.
- **Intent Detection**: Classifies user messages (e.g., technical support, billing) before processing.
- **Structured JSON Output**: Guarantees output formats utilizing custom parsers to strip markdown and extract JSON from LLM responses.
- **Multi-Provider Support**: Supports both Google Gemini (free tier) and OpenAI.

## Project Structure
```
secure-ai-chatbot/
├── app/
│   ├── main.py        # FastAPI entry point
│   ├── chatbot.py     # Core ReAct workflow logic
│   ├── safety.py      # Keyword and injection filtering
│   ├── intent.py      # User intent categorization
│   └── config.py      # Environment variables and settings
├── prompts/           # Text files containing system instructions
├── parsers/           # JSON extraction logic
├── docs/              # PRD and FRD documents
├── .env               # Your API keys (create this)
└── requirements.txt   # Python dependencies
```

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up your environment:**
   Create a `.env` file in the root directory and add your API key:
   ```env
   PROVIDER=gemini
   GEMINI_API_KEY=your_google_ai_studio_key_here
   ```
   *(You can get a free Gemini API key from [Google AI Studio](https://aistudio.google.com/app/apikey))*

3. **Run the server:**
   ```bash
   uvicorn app.main:app --reload
   ```

4. **Test the API:**
   You can interact with the API using `curl` or by visiting `http://localhost:8000/docs` in your browser.
   
   ```bash
   curl -X POST http://localhost:8000/chat \
        -H "Content-Type: application/json" \
        -d '{"message": "Hello, how can you help me today?"}'
   ```
