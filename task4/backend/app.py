from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os
from langchain_community.chat_models import ChatOpenAI
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()

# Initialize FastAPI app
app = FastAPI()

# Serve frontend static files
app.mount("/", StaticFiles(directory="../frontend", html=True), name="frontend")

# Define request schema
class ChatRequest(BaseModel):
    message: str

# System prompt to restrict to DSA topics
SYSTEM_PROMPT = (
    "You are a helpful assistant that only answers questions related to Data Structures and Algorithms. "
    "If the user asks about anything outside this domain, respond with "
    "'I can only help with DSA topics.'"
)

# Initialize LLM (OpenAI GPT-3.5 Turbo via LangChain)
# The OpenAI API key should be set in the environment variable OPENAI_API_KEY.
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise RuntimeError("OPENAI_API_KEY not set in environment. Please add it to .env file.")

llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.0)

@app.post("/api/chat")
async def chat_endpoint(req: ChatRequest):
    user_msg = req.message.strip()
    if not user_msg:
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    # Construct prompt with system instruction
    prompt = f"{SYSTEM_PROMPT}\n\nUser: {user_msg}\nAssistant:" 
    try:
        response = llm.invoke(prompt)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {"response": response.strip()}
