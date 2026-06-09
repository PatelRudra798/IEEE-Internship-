import os
from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings

def find_env_file() -> str:
    """Recursively search up for a .env file."""
    current = Path(__file__).resolve().parent
    for _ in range(5):
        env_path = current / ".env"
        if env_path.exists():
            return str(env_path)
        current = current.parent
    return ".env"

class Settings(BaseSettings):
    port: int = Field(default=8000, validation_alias="PORT")
    host: str = Field(default="0.0.0.0", validation_alias="HOST")
    
    # LLM Settings
    llm_provider: str = Field(default="ollama", validation_alias="LLM_PROVIDER")
    ollama_host: str = Field(default="http://host.docker.internal:11434", validation_alias="OLLAMA_HOST")
    ollama_model: str = Field(default="llama3", validation_alias="OLLAMA_MODEL")
    openai_api_key: str = Field(default="", validation_alias="OPENAI_API_KEY")
    gemini_api_key: str = Field(default="", validation_alias="GEMINI_API_KEY")
    
    # RAG Settings
    embedding_model: str = Field(default="all-MiniLM-L6-v2", validation_alias="EMBEDDING_MODEL")
    chroma_db_path: str = Field(default="./chroma_db", validation_alias="CHROMA_DB_PATH")
    uploads_path: str = Field(default="./uploads", validation_alias="UPLOADS_PATH")
    top_k: int = Field(default=5, validation_alias="TOP_K")

    model_config = {
        "env_file": find_env_file(),
        "env_file_encoding": "utf-8",
        "extra": "ignore"
    }

settings = Settings()

# Ensure uploads and chroma directories exist
os.makedirs(settings.uploads_path, exist_ok=True)
os.makedirs(settings.chroma_db_path, exist_ok=True)
