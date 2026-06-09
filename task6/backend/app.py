# backend/app.py
# FastAPI application that communicates with Google Gemini API
# and serves the tokenization and chatbot frontend.

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse
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

# Import our custom tokenizer
from backend.tokenizer import tokenize_text

# Load environment variables from .env
# Look first in the local directory, then fall back to Task2 chatbot directory
load_dotenv()
gemini_api_key = os.getenv("GEMINI_API_KEY")

if not gemini_api_key:
    try:
        # Fallback to Task 2 chatbot .env file if key is empty locally
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
    title="Gemini Tokenized Chatbot",
    description="A chatbot that visualizes tokens, token limits, and stats in real time.",
    version="1.0.0"
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

# Define Pydantic Models for requests
class Message(BaseModel):
    role: str # "user" or "assistant"
    content: str

class ChatRequest(BaseModel):
    message: str
    history: List[Message] = []
    model: str = "gemini-2.5-flash"
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_output_tokens: Optional[int] = Field(default=None, ge=1)
    top_p: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    top_k: Optional[int] = Field(default=None, ge=1)

class TokenizeRequest(BaseModel):
    text: str

@app.post("/api/tokenize")
async def tokenize_endpoint(req: TokenizeRequest):
    """Tokenizes text offline and returns the detailed token objects."""
    tokens = tokenize_text(req.text)
    return {
        "tokens": tokens,
        "count": len(tokens)
    }

async def event_generator(req: ChatRequest):
    """
    Asynchronous event generator that calls the Gemini API, 
    streams text chunks, and sends a final token analysis payload.
    """
    if not client:
        # Mock Response Generator if API Key is missing
        yield f"data: {json.dumps({'type': 'chunk', 'text': '[Mock Mode] API key is missing. Here is a simulated response. '})}\n\n"
        await asyncio.sleep(0.5)
        mock_response = (
            "This is a mocked response because no GEMINI_API_KEY was found in the environment. "
            "To resolve this, please add GEMINI_API_KEY=your_key in the backend/.env file."
        )
        for word in mock_response.split(" "):
            yield f"data: {json.dumps({'type': 'chunk', 'text': word + ' '})}\n\n"
            await asyncio.sleep(0.08)
        
        tokens_list = tokenize_text("[Mock Mode] API key is missing. Here is a simulated response. " + mock_response)
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

    # Build Gemini contents structure
    contents = []
    for msg in req.history:
        role = "user" if msg.role == "user" else "model"
        contents.append(
            types.Content(
                role=role,
                parts=[types.Part.from_text(text=msg.content)]
            )
        )
    # Append current message
    contents.append(
        types.Content(
            role="user",
            parts=[types.Part.from_text(text=req.message)]
        )
    )

    # Set up config options
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
        # Request async stream from Gemini API
        response_stream = await client.aio.models.generate_content_stream(
            model=req.model,
            contents=contents,
            config=config
        )

        async for chunk in response_stream:
            chunk_text = chunk.text
            if chunk_text:
                accumulated_text += chunk_text
                # Send text chunk to client
                yield f"data: {json.dumps({'type': 'chunk', 'text': chunk_text})}\n\n"

            # Capture finish reason
            if chunk.candidates and len(chunk.candidates) > 0:
                fr = chunk.candidates[0].finish_reason
                if fr:
                    finish_reason = str(fr).split(".")[-1]

            # Capture token usage metadata
            if chunk.usage_metadata:
                prompt_tokens = chunk.usage_metadata.prompt_token_count or prompt_tokens
                completion_tokens = chunk.usage_metadata.candidates_token_count or completion_tokens
                total_tokens = chunk.usage_metadata.total_token_count or total_tokens

        # Fallback to local tokenizer if metadata was not returned in stream chunks
        tokens_list = tokenize_text(accumulated_text)
        if completion_tokens == 0:
            completion_tokens = len(tokens_list)
        if prompt_tokens == 0:
            prompt_flat = " ".join([c.parts[0].text for c in contents if c.parts])
            prompt_tokens = len(tokenize_text(prompt_flat))
        if total_tokens == 0:
            total_tokens = prompt_tokens + completion_tokens

        # Send terminal SSE event containing final text, token analysis list, and metadata
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

# Mount frontend files (served at root)
# frontend directory is relative to this file: ../frontend
frontend_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend")
if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")
    print(f"[INFO] Static files mounted from: {frontend_path}")
else:
    print(f"[WARN] Static frontend folder not found at: {frontend_path}")
