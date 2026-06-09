import logging
from typing import Dict, Any, List
from backend.services.embedding_service import EmbeddingService
from backend.services.vector_service import VectorService
from backend.services.llm_service import BaseLLMProvider
from backend.config.settings import settings

logger = logging.getLogger(__name__)

class RAGService:
    def __init__(
        self,
        embedding_service: EmbeddingService,
        vector_service: VectorService,
        llm_provider: BaseLLMProvider
    ):
        """
        Initializes the RAGService with required helper services.
        """
        self.embedding_service = embedding_service
        self.vector_service = vector_service
        self.llm_provider = llm_provider
        logger.info("RAGService initialized.")

    def answer_question(self, question: str) -> Dict[str, Any]:
        """
        Executes the full RAG pipeline to answer the user's question.
        
        Args:
            question: The question query string.
            
        Returns:
            Dict containing 'answer' and a list of 'sources'.
            Example:
            {
                "answer": "Generated answer here...",
                "sources": [{"document": "file.pdf", "page": 1, "text": "...", "score": 0.85}]
            }
        """
        logger.info(f"RAG workflow started for query: '{question}'")
        
        # 1. Convert question to dense embedding vector
        query_embedding = self.embedding_service.generate_query_embedding(question)
        
        # 2. Query vector database for top-k matching chunks
        top_k = settings.top_k
        retrieved_chunks = self.vector_service.search_documents(
            query_embedding=query_embedding,
            top_k=top_k
        )
        
        # 3. If there is no context in the vector database, return grounding answer immediately
        if not retrieved_chunks:
            logger.info("Zero context chunks retrieved from vector database.")
            return {
                "answer": "I could not find this information in the uploaded documents.",
                "sources": []
            }
            
        # 4. Formulate the strict prompt context string from retrieved chunks
        context_blocks = []
        for idx, chunk in enumerate(retrieved_chunks):
            source_info = f"[Doc: {chunk['source']}, Page: {chunk['page']}, Index: {idx+1}]"
            context_blocks.append(f"{source_info}\n{chunk['text']}")
            
        context_str = "\n\n---\n\n".join(context_blocks)
        
        # 5. Call LLM provider to construct the response
        try:
            answer = self.llm_provider.generate_answer(
                context=context_str,
                question=question
            )
        except Exception as e:
            logger.error(f"Failed to generate answer from LLM: {e}", exc_info=True)
            raise e
            
        # 6. Format the source citations for the output model
        sources = [
            {
                "document": chunk["source"],
                "page": chunk["page"],
                "text": chunk["text"],
                "score": chunk["score"]
            }
            for chunk in retrieved_chunks
        ]
        
        logger.info("RAG workflow completed successfully.")
        return {
            "answer": answer,
            "sources": sources
        }
