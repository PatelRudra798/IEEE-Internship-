import logging
from typing import List
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

class EmbeddingService:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initializes the EmbeddingService and loads the SentenceTransformer model.
        This runs once during service startup.
        """
        logger.info(f"Loading SentenceTransformer embedding model: {model_name}...")
        try:
            self.model = SentenceTransformer(model_name)
            logger.info("Embedding model loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}", exc_info=True)
            raise e

    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generates dense vector embeddings for a list of text chunks.
        
        Args:
            texts: List of text strings to embed.
            
        Returns:
            A list of vector embeddings, where each embedding is a list of floats.
        """
        if not texts:
            return []
            
        logger.info(f"Generating embeddings for {len(texts)} text chunks.")
        try:
            # sentence-transformers returns numpy arrays; we convert them to lists of floats
            embeddings = self.model.encode(texts, convert_to_numpy=True)
            return [vector.tolist() for vector in embeddings]
        except Exception as e:
            logger.error(f"Failed to generate embeddings: {e}", exc_info=True)
            raise e

    def generate_query_embedding(self, question: str) -> List[float]:
        """
        Generates a dense vector embedding for a single query.
        
        Args:
            question: Query text to embed.
            
        Returns:
            Vector embedding as a list of floats.
        """
        logger.info("Generating embedding for search query.")
        try:
            embedding = self.model.encode(question, convert_to_numpy=True)
            # Check if it's 1D, since we passed a single string
            if len(embedding.shape) == 1:
                return embedding.tolist()
            else:
                return embedding[0].tolist()
        except Exception as e:
            logger.error(f"Failed to generate query embedding: {e}", exc_info=True)
            raise e
