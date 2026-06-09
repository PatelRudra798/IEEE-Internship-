import logging
from typing import List, Dict, Any
from langchain_text_splitters import RecursiveCharacterTextSplitter

logger = logging.getLogger(__name__)

class ChunkService:
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 100):
        """
        Initializes the ChunkService with specified size and overlap.
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len
        )
        logger.info(
            f"Initialized ChunkService with chunk_size={chunk_size}, chunk_overlap={chunk_overlap}"
        )

    def chunk_document(self, pages_data: List[Dict[str, Any]], filename: str) -> List[Dict[str, Any]]:
        """
        Chunks structured pages of text from a PDF, preserving metadata.
        
        Args:
            pages_data: Output of PDF processing service [{"page": 1, "text": "..."}].
            filename: The original PDF filename.
            
        Returns:
            List of dictionaries containing the chunk text and metadata.
            Example:
            [
                {
                    "text": "...",
                    "metadata": {
                        "page": 1,
                        "source": "document.pdf"
                    }
                }
            ]
        """
        logger.info(f"Starting chunking for {filename} ({len(pages_data)} pages)")
        chunks: List[Dict[str, Any]] = []
        
        for item in pages_data:
            page_num = item["page"]
            text_content = item["text"]
            
            if not text_content:
                continue
                
            # Split the text of this specific page to keep page number metadata accurate
            page_chunks = self.splitter.split_text(text_content)
            
            for chunk_text in page_chunks:
                clean_chunk = chunk_text.strip()
                if not clean_chunk:
                    continue
                    
                chunks.append({
                    "text": clean_chunk,
                    "metadata": {
                        "page": page_num,
                        "source": filename
                    }
                })
                
        logger.info(f"Successfully chunked {filename} into {len(chunks)} chunks.")
        return chunks
