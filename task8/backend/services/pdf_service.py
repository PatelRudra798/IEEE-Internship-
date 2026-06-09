import logging
from typing import List, Dict, Any
from pypdf import PdfReader

logger = logging.getLogger(__name__)

def extract_text(pdf_path: str) -> List[Dict[str, Any]]:
    """
    Extracts text page-by-page from a PDF file.
    
    Args:
        pdf_path: Path to the PDF file on disk.
        
    Returns:
        List of dictionaries with page numbers (1-indexed) and extracted text.
        Example: [{"page": 1, "text": "..."}]
        
    Raises:
        ValueError: If the PDF is empty, unreadable, or has no extractable text.
        FileNotFoundError: If the PDF file does not exist.
        Exception: General PDF parsing exceptions.
    """
    logger.info(f"Starting text extraction for PDF: {pdf_path}")
    
    pages_data = []
    try:
        reader = PdfReader(pdf_path)
        num_pages = len(reader.pages)
        
        if num_pages == 0:
            logger.error(f"Failed parsing {pdf_path}: PDF has 0 pages.")
            raise ValueError("The PDF file is empty and contains no pages.")
            
        for idx in range(num_pages):
            page = reader.pages[idx]
            page_num = idx + 1
            
            # Extract text (or empty string if extract_text returns None)
            extracted_text = page.extract_text()
            text_content = (extracted_text or "").strip()
            
            pages_data.append({
                "page": page_num,
                "text": text_content
            })
            
        # Validate that we actually extracted some text (i.e. not a purely scanned image PDF without OCR)
        total_text_length = sum(len(p["text"]) for p in pages_data)
        if total_text_length == 0:
            logger.error(f"No text extracted from {pdf_path}. The file may be image-only or encrypted.")
            raise ValueError(
                "No extractable text found. The PDF might be scanned, image-only, or password-protected."
            )
            
        logger.info(f"Extracted {num_pages} pages from {pdf_path}. Total characters: {total_text_length}")
        return pages_data
        
    except FileNotFoundError:
        logger.error(f"File not found: {pdf_path}")
        raise FileNotFoundError(f"PDF file not found at path: {pdf_path}")
    except Exception as e:
        if not isinstance(e, ValueError):
            logger.error(f"Failed to parse PDF {pdf_path} due to unexpected error: {e}", exc_info=True)
        raise e
