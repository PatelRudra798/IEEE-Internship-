# docx_parser.py
"""Utility to extract plain text from Microsoft Word (.docx) files using python-docx."""

from pathlib import Path
from docx import Document

def extract_text_from_docx(file_path: str) -> str:
    """Return concatenated text from a DOCX file.

    Args:
        file_path: Path to the DOCX file.
    Returns:
        Plain text extracted from all paragraphs.
    """
    path = Path(file_path)
    if not path.is_file():
        raise FileNotFoundError(f"DOCX not found: {file_path}")
    doc = Document(str(path))
    paragraphs = [p.text for p in doc.paragraphs if p.text]
    return "\n".join(paragraphs)
