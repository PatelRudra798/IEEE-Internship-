# backend/app.py
# FastAPI application for the RAG-enhanced Gemini Tokenized Chatbot.
# Adds document ingestion, retrieval, and augmented generation on top of Task 6.

from fastapi import FastAPI, HTTPException, Request, UploadFile, File, Form
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import os
import json
import asyncio
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

# Import Google GenAI SDK
from google import genai
from google.genai import types

# Import our custom tokenizer and RAG module
from backend.tokenizer import tokenize_text
from backend import rag

# Load environment variables from .env
load_dotenv()
gemini_api_key = os.getenv("GEMINI_API_KEY")

if not gemini_api_key:
    try:
        parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        task2_env = os.path.join(parent_dir, "..", "Task2", "secure-ai-chatbot", ".env")
        if os.path.exists(task2_env):
            with open(task2_env, "r") as f:
                for line in f:
                    if line.strip().startswith("GEMINI_API_KEY="):
                        gemini_api_key = line.split("=")[1].strip()
                        os.environ["GEMINI_API_KEY"] = gemini_api_key
                        break
    except Exception as e:
        print(f"[WARN] Failed to read fallback .env from Task2: {e}")

# Initialize FastAPI app
app = FastAPI(
    title="Gemini RAG Chatbot",
    description="A RAG-enhanced chatbot that retrieves relevant documents before generating responses.",
    version="2.0.0"
)

# Enable CORS for local testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Gemini Client if API key is present
client = None
if gemini_api_key:
    client = genai.Client(api_key=gemini_api_key)
    print("[INFO] Google GenAI Client initialized successfully.")
else:
    print("[ERROR] GEMINI_API_KEY not found. Server will run in Mock Mode.")


# ─── Pydantic Models ────────────────────────────────────────────────────────

class Message(BaseModel):
    role: str  # "user" or "assistant"
    content: str

class ChatRequest(BaseModel):
    message: str
    history: List[Message] = []
    model: str = "gemini-2.5-flash"
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_output_tokens: Optional[int] = Field(default=None, ge=1)
    top_p: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    top_k: Optional[int] = Field(default=None, ge=1)
    use_rag: bool = False
    rag_top_k: int = Field(default=5, ge=1, le=20)

class TokenizeRequest(BaseModel):
    text: str


# ─── Tokenize Endpoint ──────────────────────────────────────────────────────

@app.post("/api/tokenize")
async def tokenize_endpoint(req: TokenizeRequest):
    """Tokenizes text offline and returns the detailed token objects."""
    tokens = tokenize_text(req.text)
    return {
        "tokens": tokens,
        "count": len(tokens)
    }


# ─── RAG Endpoints ──────────────────────────────────────────────────────────

@app.post("/api/ingest/text")
async def ingest_text_endpoint(req: Request):
    """Ingest raw text content into the RAG knowledge base."""
    body = await req.json()
    text = body.get("text", "")
    source = body.get("source", "pasted-text")
    if not text.strip():
        raise HTTPException(status_code=400, detail="No text provided.")
    result = rag.ingest_text(text, source_name=source)
    return result


@app.post("/api/ingest/file")
async def ingest_file_endpoint(file: UploadFile = File(...)):
    """Upload and ingest a file into the RAG knowledge base."""
    contents = await file.read()
    text = contents.decode("utf-8", errors="replace")
    if not text.strip():
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")
    result = rag.ingest_text(text, source_name=file.filename or "upload")
    return result


@app.post("/api/ingest/folder")
async def ingest_folder_endpoint(req: Request):
    """Ingest all supported files from a folder path on the server."""
    body = await req.json()
    folder = body.get("folder", "")
    if not folder or not os.path.isdir(folder):
        raise HTTPException(status_code=400, detail=f"Invalid folder path: {folder}")
    results = rag.ingest_folder(folder)
    return {"results": results}


@app.get("/api/rag/status")
async def rag_status():
    """Get current RAG index status."""
    return rag.get_status()


@app.post("/api/rag/clear")
async def rag_clear():
    """Clear the entire RAG index."""
    return rag.clear_index()


@app.post("/api/rag/query")
async def rag_query(req: Request):
    """Test retrieval without calling the LLM – returns matching chunks."""
    body = await req.json()
    query = body.get("query", "")
    top_k = body.get("top_k", 5)
    if not query:
        raise HTTPException(status_code=400, detail="No query provided.")
    hits = rag.retrieve(query, top_k=top_k)
    return {"query": query, "results": hits}


# ─── Chat / Streaming ───────────────────────────────────────────────────────

async def event_generator(req: ChatRequest):
    """
    Asynchronous event generator that optionally performs RAG retrieval,
    then calls the Gemini API and streams text chunks plus a final token analysis.
    """
    rag_context = ""
    retrieved_chunks = []

    # ── RAG retrieval ────────────────────────────────────────────────────
    if req.use_rag:
        try:
            retrieved_chunks = rag.retrieve(req.message, top_k=req.rag_top_k)
            rag_context = rag.build_rag_context(req.message, top_k=req.rag_top_k)
            # Send RAG metadata event so the UI can display sources
            rag_event = {
                "type": "rag_context",
                "chunks": retrieved_chunks,
                "chunk_count": len(retrieved_chunks),
            }
            yield f"data: {json.dumps(rag_event)}\n\n"
        except Exception as e:
            print(f"[WARN] RAG retrieval failed: {e}")
            # Continue without RAG if retrieval fails

    # ── Mock mode ────────────────────────────────────────────────────────
    if not client:
        yield f"data: {json.dumps({'type': 'chunk', 'text': '[Mock Mode] API key is missing. Here is a simulated response. '})}\n\n"
        await asyncio.sleep(0.5)
        mock_response = (
            "This is a mocked response because no GEMINI_API_KEY was found in the environment. "
            "To resolve this, please add GEMINI_API_KEY=your_key in the backend/.env file."
        )
        if rag_context:
            mock_response += " [RAG context was provided but ignored in mock mode.]"

        for word in mock_response.split(" "):
            yield f"data: {json.dumps({'type': 'chunk', 'text': word + ' '})}\n\n"
            await asyncio.sleep(0.08)

        tokens_list = tokenize_text("[Mock Mode] " + mock_response)
        payload = {
            "type": "done",
            "text": mock_response,
            "tokens": tokens_list,
            "finish_reason": "STOP",
            "usage": {
                "prompt_tokens": len(tokenize_text(req.message)),
                "completion_tokens": len(tokens_list),
                "total_tokens": len(tokenize_text(req.message)) + len(tokens_list)
            }
        }
        yield f"data: {json.dumps(payload)}\n\n"
        return

    # ── Build Gemini contents ────────────────────────────────────────────
    contents = []
    for msg in req.history:
        role = "user" if msg.role == "user" else "model"
        contents.append(
            types.Content(
                role=role,
                parts=[types.Part.from_text(text=msg.content)]
            )
        )

    # Build the augmented user message
    if rag_context:
        augmented_message = rag_context + "User question: " + req.message
    else:
        augmented_message = req.message

    contents.append(
        types.Content(
            role="user",
            parts=[types.Part.from_text(text=augmented_message)]
        )
    )

    # Set up config
    config_args = {}
    if req.temperature is not None:
        config_args["temperature"] = req.temperature
    if req.max_output_tokens is not None:
        config_args["max_output_tokens"] = req.max_output_tokens
    if req.top_p is not None:
        config_args["top_p"] = req.top_p
    if req.top_k is not None:
        config_args["top_k"] = req.top_k

    config = types.GenerateContentConfig(**config_args)

    accumulated_text = ""
    finish_reason = "STOP"
    prompt_tokens = 0
    completion_tokens = 0
    total_tokens = 0

    try:
        response_stream = await client.aio.models.generate_content_stream(
            model=req.model,
            contents=contents,
            config=config
        )

        async for chunk in response_stream:
            chunk_text = chunk.text
            if chunk_text:
                accumulated_text += chunk_text
                yield f"data: {json.dumps({'type': 'chunk', 'text': chunk_text})}\n\n"

            if chunk.candidates and len(chunk.candidates) > 0:
                fr = chunk.candidates[0].finish_reason
                if fr:
                    finish_reason = str(fr).split(".")[-1]

            if chunk.usage_metadata:
                prompt_tokens = chunk.usage_metadata.prompt_token_count or prompt_tokens
                completion_tokens = chunk.usage_metadata.candidates_token_count or completion_tokens
                total_tokens = chunk.usage_metadata.total_token_count or total_tokens

        tokens_list = tokenize_text(accumulated_text)
        if completion_tokens == 0:
            completion_tokens = len(tokens_list)
        if prompt_tokens == 0:
            prompt_flat = " ".join([c.parts[0].text for c in contents if c.parts])
            prompt_tokens = len(tokenize_text(prompt_flat))
        if total_tokens == 0:
            total_tokens = prompt_tokens + completion_tokens

        payload = {
            "type": "done",
            "text": accumulated_text,
            "tokens": tokens_list,
            "finish_reason": finish_reason,
            "usage": {
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": total_tokens
            }
        }
        yield f"data: {json.dumps(payload)}\n\n"

    except Exception as e:
        print(f"[ERROR] Stream error: {e}")
        yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"


@app.post("/api/chat")
async def chat_endpoint(req: ChatRequest):
    """Streams chat completions as Server-Sent Events (SSE)."""
    return StreamingResponse(
        event_generator(req),
        media_type="text/event-stream"
    )


# ─── Static files (frontend) ────────────────────────────────────────────────

frontend_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend")
if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")
    print(f"[INFO] Static files mounted from: {frontend_path}")
else:
    print(f"[WARN] Static frontend folder not found at: {frontend_path}")
