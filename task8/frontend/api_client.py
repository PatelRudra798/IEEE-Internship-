import os
import logging
from typing import Dict, Any, List, Optional
import httpx

logger = logging.getLogger(__name__)

class APIClient:
    def __init__(self, base_url: Optional[str] = None):
        """
        Initializes the API Client. Retrieves base URL from environment or defaults to localhost.
        """
        if not base_url:
            base_url = os.getenv("BACKEND_URL", "http://localhost:8000")
        self.base_url = base_url.rstrip("/")
        logger.info(f"API Client configured to point to backend: {self.base_url}")

    def check_health(self) -> bool:
        """
        Pings the backend health endpoint. Returns True if healthy.
        """
        url = f"{self.base_url}/health"
        try:
            with httpx.Client(timeout=3.0) as client:
                response = client.get(url)
                if response.status_code == 200:
                    return response.json().get("status") == "healthy"
                return False
        except Exception:
            return False

    def upload_pdf(self, file_bytes: bytes, filename: str) -> Dict[str, Any]:
        """
        Uploads a PDF file to the backend vector store database.
        """
        url = f"{self.base_url}/upload"
        files = {"file": (filename, file_bytes, "application/pdf")}
        try:
            # We set a generous timeout because parsing, chunking, embedding,
            # and database storage can take time for large documents.
            with httpx.Client(timeout=180.0) as client:
                response = client.post(url, files=files)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            error_detail = e.response.json().get("detail", "Error processing upload.")
            logger.error(f"Document upload HTTP failure: {error_detail}")
            raise RuntimeError(error_detail)
        except Exception as e:
            logger.error(f"Failed connecting to server for PDF upload: {e}")
            raise RuntimeError(f"Connection failed: {str(e)}")

    def ask_question(self, question: str) -> Dict[str, Any]:
        """
        Queries the backend RAG pipeline.
        """
        url = f"{self.base_url}/ask"
        payload = {"question": question}
        try:
            # Timout allows for vector db search and LLM inference time
            with httpx.Client(timeout=120.0) as client:
                response = client.post(url, json=payload)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            error_detail = e.response.json().get("detail", "Error generating answer.")
            logger.error(f"RAG query HTTP failure: {error_detail}")
            raise RuntimeError(error_detail)
        except Exception as e:
            logger.error(f"Failed connecting to server for query: {e}")
            raise RuntimeError(f"Connection failed: {str(e)}")

    def list_documents(self) -> List[Dict[str, Any]]:
        """
        Retrieves list of all indexed files from vector DB.
        """
        url = f"{self.base_url}/documents"
        try:
            with httpx.Client(timeout=5.0) as client:
                response = client.get(url)
                response.raise_for_status()
                return response.json().get("documents", [])
        except Exception as e:
            logger.error(f"Failed to fetch document list: {e}")
            return []

    def delete_document(self, filename: str) -> Dict[str, Any]:
        """
        Deletes a document from the vector store and server storage.
        """
        url = f"{self.base_url}/documents/{filename}"
        try:
            with httpx.Client(timeout=15.0) as client:
                response = client.delete(url)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            error_detail = e.response.json().get("detail", "Error deleting document.")
            logger.error(f"Document deletion HTTP failure: {error_detail}")
            raise RuntimeError(error_detail)
        except Exception as e:
            logger.error(f"Failed connecting to server for deletion: {e}")
            raise RuntimeError(f"Connection failed: {str(e)}")
