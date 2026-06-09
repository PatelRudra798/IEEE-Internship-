import uuid
import logging
from typing import List, Dict, Any
import chromadb

logger = logging.getLogger(__name__)

class VectorService:
    def __init__(self, db_path: str, collection_name: str = "document_chunks"):
        """
        Initializes the ChromaDB persistent client and collection.
        """
        logger.info(f"Connecting to ChromaDB at storage path: {db_path}")
        try:
            self.client = chromadb.PersistentClient(path=db_path)
            # Use cosine distance (distance = 1 - cosine_similarity)
            self.collection = self.client.get_or_create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            logger.info(f"Connected to collection '{collection_name}' successfully.")
        except Exception as e:
            logger.error(f"Failed to connect to ChromaDB: {e}", exc_info=True)
            raise e

    def add_documents(self, chunks: List[Dict[str, Any]], embeddings: List[List[float]]) -> None:
        """
        Adds text chunks, their embeddings, and metadata to ChromaDB.
        
        Args:
            chunks: List of chunk dicts [{"text": "...", "metadata": {"page": 1, "source": "doc.pdf"}}]
            embeddings: List of embedding vectors matching the index of chunks.
        """
        if not chunks:
            logger.warning("No chunks provided to store in ChromaDB.")
            return

        if len(chunks) != len(embeddings):
            raise ValueError("The number of text chunks must match the number of embeddings.")

        logger.info(f"Upserting {len(chunks)} chunks into ChromaDB.")
        try:
            ids = [str(uuid.uuid4()) for _ in range(len(chunks))]
            documents = [chunk["text"] for chunk in chunks]
            metadatas = [chunk["metadata"] for chunk in chunks]

            self.collection.add(
                ids=ids,
                embeddings=embeddings,
                metadatas=metadatas,
                documents=documents
            )
            logger.info("Successfully added all chunks to ChromaDB.")
        except Exception as e:
            logger.error(f"Failed to write chunks to ChromaDB: {e}", exc_info=True)
            raise e

    def search_documents(self, query_embedding: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Searches the collection for chunks similar to the query embedding.
        
        Args:
            query_embedding: The vector embedding of the user's question.
            top_k: The number of closest matches to return.
            
        Returns:
            List of matching chunks with similarity score and metadata.
            Example:
            [
                {
                    "text": "chunk text content",
                    "source": "filename.pdf",
                    "page": 4,
                    "score": 0.85  # similarity score (1 - distance)
                }
            ]
        """
        logger.info(f"Querying ChromaDB for top_k={top_k} nearest neighbors.")
        try:
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k
            )

            formatted_results: List[Dict[str, Any]] = []
            if not results or not results["documents"] or len(results["documents"]) == 0:
                return formatted_results

            # Extraction maps the single queried item
            documents = results["documents"][0]
            metadatas = results["metadatas"][0]
            distances = results["distances"][0] if results.get("distances") else [0.0] * len(documents)

            for doc, meta, dist in zip(documents, metadatas, distances):
                # Chroma HNWS cosine space distance is 1.0 - cosine_similarity.
                # Therefore, similarity_score = 1.0 - distance.
                similarity_score = 1.0 - float(dist)
                
                formatted_results.append({
                    "text": doc,
                    "source": meta.get("source", "unknown"),
                    "page": meta.get("page", 0),
                    "score": similarity_score
                })

            return formatted_results
        except Exception as e:
            logger.error(f"Failed to query ChromaDB: {e}", exc_info=True)
            raise e

    def delete_document(self, filename: str) -> None:
        """
        Deletes all chunks stored for a specific PDF file.
        
        Args:
            filename: The source filename metadata to delete.
        """
        logger.info(f"Deleting all vector database records for source: {filename}")
        try:
            self.collection.delete(where={"source": filename})
            logger.info(f"Database deletion completed for {filename}.")
        except Exception as e:
            logger.error(f"Failed to delete records for {filename}: {e}", exc_info=True)
            raise e

    def list_documents(self) -> List[Dict[str, Any]]:
        """
        Aggregates stored chunks to list unique document sources and their chunk count.
        
        Returns:
            List of document info dictionaries: [{"filename": "...", "chunks_count": 10}]
        """
        logger.info("Listing all indexed documents.")
        try:
            # Query only the metadata of all items
            data = self.collection.get(include=["metadatas"])
            metadatas = data.get("metadatas", [])
            
            counts: Dict[str, int] = {}
            for meta in metadatas:
                source = meta.get("source")
                if source:
                    counts[source] = counts.get(source, 0) + 1
                    
            docs_list = [
                {"filename": k, "chunks_count": v}
                for k, v in counts.items()
            ]
            return docs_list
        except Exception as e:
            logger.error(f"Failed to list documents from ChromaDB: {e}", exc_info=True)
            raise e
