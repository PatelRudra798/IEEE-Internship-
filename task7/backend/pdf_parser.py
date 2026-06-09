# pdf_parser.py
"""Utility to extract plain text from PDF files using PyMuPDF (fitz)."""

import fitz  # PyMuPDF
from pathlib import Path

def extract_text_from_pdf(file_path: str) -> str:
    """Return the concatenated text of all pages in the PDF.

    Args:
        file_path: Path to the PDF file.
    Returns:
        Plain text extracted from the PDF.
    """
    path = Path(file_path)
    if not path.is_file():
        raise FileNotFoundError(f"PDF not found: {file_path}")
    doc = fitz.open(str(path))
    texts = []
    for page in doc:
        texts.append(page.get_text())
    return "\n".join(texts)
