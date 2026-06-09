import logging
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from backend.config.settings import settings
from backend.services.embedding_service import EmbeddingService
from backend.services.vector_service import VectorService
from backend.services.chunk_service import ChunkService
from backend.services.rag_service import RAGService
from backend.services.llm_service import get_llm_provider
from backend.api import health, upload, chat

# Configure application-wide logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("backend")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan event handler for FastAPI startup and shutdown routines.
    Loads models and initializes db clients once.
    """
    logger.info("Starting FastAPI application...")
    logger.info(f"Configuration: LLM Provider = '{settings.llm_provider}', Embedding Model = '{settings.embedding_model}'")
    
    try:
        # 1. Instantiate the heavy Embedding Model (loads once)
        embedding_service = EmbeddingService(model_name=settings.embedding_model)
        
        # 2. Instantiate the persistent Vector DB client
        vector_service = VectorService(db_path=settings.chroma_db_path)
        
        # 3. Instantiate chunk service (no heavy startup cost)
        chunk_service = ChunkService()
        
        # 4. Resolve the configured LLM provider
        llm_provider = get_llm_provider()
        
        # 5. Instantiate RAG coordinator
        rag_service = RAGService(
            embedding_service=embedding_service,
            vector_service=vector_service,
            llm_provider=llm_provider
        )
        
        # Cache services inside the application state for dependency retrieval
        app.state.embedding_service = embedding_service
        app.state.vector_service = vector_service
        app.state.chunk_service = chunk_service
        app.state.rag_service = rag_service
        
        logger.info("All backend services initialized successfully. Ready to handle client requests.")
    except Exception as e:
        logger.critical(f"Startup initialization failed: {e}", exc_info=True)
        raise e
        
    yield
    logger.info("FastAPI application is shutting down...")


app = FastAPI(
    title="Document QA RAG Backend",
    description="Production-quality FastAPI backend for Retrieval-Augmented Generation.",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS for communication from local or dockerized Streamlit UI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Broad CORS settings for development/docker-compose environment
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Attach routes
app.include_router(health.router)
app.include_router(upload.router)
app.include_router(chat.router)


if __name__ == "__main__":
    logger.info(f"Starting server locally on http://{settings.host}:{settings.port}")
    uvicorn.run("backend.main:app", host=settings.host, port=settings.port, reload=True)
