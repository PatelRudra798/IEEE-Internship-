# app/main.py
# FastAPI application entry point.
# Provides the /chat REST API endpoint.

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from fastapi.middleware.cors import CORSMiddleware

from app.config import config
from app.chatbot import SecureChatbot

# Initialize FastAPI app
app = FastAPI(
    title=config.APP_TITLE,
    version=config.APP_VERSION,
    description="A secure AI chatbot API with strict guardrails and JSON output."
)

# Add CORS middleware to allow frontend clients to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the chatbot engine
chatbot = SecureChatbot()


# Request/Response Data Models
class ChatRequest(BaseModel):
    message: str = Field(..., max_length=config.MAX_INPUT_LENGTH, description="The user's message to the chatbot.")

class ChatResponse(BaseModel):
    intent: str
    risk_level: str
    response: str


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "ok", "app": config.APP_TITLE, "version": config.APP_VERSION}


@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Main chat endpoint.
    Receives user message, passes it through the SecureChatbot pipeline,
    and returns a structured JSON response.
    """
    try:
        # Process the message through the secure pipeline
        result = await chatbot.process_message(request.message)
        
        # The result is guaranteed to be a dict matching ChatResponse by our JSONParser
        return result
        
    except Exception as e:
        # Catch unexpected server errors
        print(f"[CRITICAL ERROR] Error in /chat endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal server error while processing the request.")
