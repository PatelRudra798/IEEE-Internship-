# backend/rag.py
# Retrieval-Augmented Generation module.
# Handles document loading, chunking, embedding, FAISS indexing, and retrieval.

import os
import re
import json
import hashlib
import numpy as np
from typing import List, Dict, Any, Optional
from .pdf_parser import extract_text_from_pdf
from .pptx_parser import extract_text_from_pptx
from .docx_parser import extract_text_from_docx
from pathlib import Path

# We lazy-import heavy libs so the server starts fast even if they aren't installed yet
_faiss = None
_model = None

CHUNK_SIZE = 500       # characters per chunk (approx)
CHUNK_OVERLAP = 80     # overlap between consecutive chunks
EMBEDDING_DIM = 384    # all-MiniLM-L6-v2 output dimension

# In-memory store ----------------------------------------------------------
_index = None                        # FAISS index object
_chunks: List[Dict[str, Any]] = []   # parallel list of chunk metadata
_documents: List[Dict[str, Any]] = []  # list of ingested document metadata


def _ensure_model():
    """Lazy-load the sentence-transformers model on first use."""
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer("all-MiniLM-L6-v2")
        print("[RAG] Sentence-transformers model loaded: all-MiniLM-L6-v2")
    return _model


def _ensure_index():
    """Create or return the FAISS index."""
    global _faiss, _index
    if _faiss is None:
        import faiss as _faiss_module
        _faiss = _faiss_module
    if _index is None:
        _index = _faiss.IndexFlatL2(EMBEDDING_DIM)
        print("[RAG] FAISS index created (dim=%d)" % EMBEDDING_DIM)
    return _index


# ---------- Chunking -------------------------------------------------------

def _chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[str]:
    """
    Split text into overlapping chunks.
    Tries to break on sentence boundaries for cleaner context.
    """
    # Split into sentences first
    sentences = re.split(r'(?<=[.!?])\s+', text)
    
    chunks = []
    current_chunk = ""

    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue

        if len(current_chunk) + len(sentence) + 1 <= chunk_size:
            current_chunk = (current_chunk + " " + sentence).strip()
        else:
            if current_chunk:
                chunks.append(current_chunk)
            # Start new chunk, keeping overlap from previous
            if overlap > 0 and current_chunk:
                tail = current_chunk[-overlap:]
                current_chunk = tail + " " + sentence
            else:
                current_chunk = sentence

    if current_chunk.strip():
        chunks.append(current_chunk.strip())

    # If no sentence splitting happened (e.g. no punctuation), fall back to
    # fixed-window chunking so very long texts still get split.
    if len(chunks) <= 1 and len(text) > chunk_size:
        chunks = []
        for i in range(0, len(text), chunk_size - overlap):
            chunks.append(text[i:i + chunk_size])

    return chunks


# ---------- Ingestion -------------------------------------------------------

def ingest_text(text: str, source_name: str = "upload") -> Dict[str, Any]:
    """
    Ingest a single document (raw text string).
    Returns metadata about the ingested document.
    """
    global _chunks

    model = _ensure_model()
    index = _ensure_index()

    chunks = _chunk_text(text)
    if not chunks:
        return {"status": "empty", "chunks": 0, "source": source_name}

    # Embed all chunks
    embeddings = model.encode(chunks, show_progress_bar=False)
    embeddings = np.array(embeddings, dtype="float32")

    # Record chunk metadata
    start_id = len(_chunks)
    for i, chunk_text in enumerate(chunks):
        _chunks.append({
            "id": start_id + i,
            "text": chunk_text,
            "source": source_name,
            "doc_index": len(_documents),
        })

    # Add to FAISS
    index.add(embeddings)

    # Track document
    doc_meta = {
        "id": len(_documents),
        "source": source_name,
        "char_count": len(text),
        "chunk_count": len(chunks),
        "chunk_ids": list(range(start_id, start_id + len(chunks))),
    }
    _documents.append(doc_meta)

    print(f"[RAG] Ingested '{source_name}': {len(chunks)} chunks, {len(text)} chars")
    return {
        "status": "ok",
        "source": source_name,
        "chunks": len(chunks),
        "total_chunks_in_index": len(_chunks),
    }


def ingest_file(filepath: str) -> Dict[str, Any]:
    """Ingest a file (PDF, PPTX, DOCX, or plain text) from disk."""
    path = Path(filepath)
    if not path.is_file():
        return {"status": "error", "message": f"File not found: {filepath}"}

    ext = path.suffix.lower()
    if ext == ".pdf":
        text = extract_text_from_pdf(str(path))
    elif ext == ".pptx":
        text = extract_text_from_pptx(str(path))
    elif ext == ".docx":
        text = extract_text_from_docx(str(path))
    else:
        # default to plain text read
        text = path.read_text(encoding="utf-8", errors="replace")
    return ingest_text(text, source_name=path.name)


def ingest_folder(folder_path: str) -> List[Dict[str, Any]]:
    """Ingest all .txt / .md / .csv files from a folder."""
    folder = Path(folder_path)
    if not folder.is_dir():
        return [{"status": "error", "message": f"Not a directory: {folder_path}"}]

    results = []
    for f in sorted(folder.iterdir()):
        if f.is_file() and f.suffix.lower() in {".txt", ".md", ".csv", ".log", ".json", ".py", ".html", ".css", ".js"}:
            results.append(ingest_file(str(f)))
    return results


# ---------- Retrieval -------------------------------------------------------

def retrieve(query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """
    Retrieve the top-k most relevant chunks for a given query.
    Returns list of dicts: {text, source, score, id}.
    """
    if not _chunks or _index is None or _index.ntotal == 0:
        return []

    model = _ensure_model()
    query_vec = model.encode([query], show_progress_bar=False)
    query_vec = np.array(query_vec, dtype="float32")

    k = min(top_k, _index.ntotal)
    distances, indices = _index.search(query_vec, k)

    results = []
    for dist, idx in zip(distances[0], indices[0]):
        if idx < 0 or idx >= len(_chunks):
            continue
        chunk = _chunks[idx]
        results.append({
            "id": chunk["id"],
            "text": chunk["text"],
            "source": chunk["source"],
            "score": float(dist),
        })

    return results


# ---------- Context builder -------------------------------------------------

def build_rag_context(query: str, top_k: int = 5) -> str:
    """
    Build a RAG context string from retrieved chunks.
    This gets prepended to the user message before sending to the LLM.
    """
    hits = retrieve(query, top_k=top_k)
    if not hits:
        return ""

    context_parts = []
    for i, hit in enumerate(hits, 1):
        context_parts.append(
            f"[Source: {hit['source']}]\n{hit['text']}"
        )

    context = "\n\n---\n\n".join(context_parts)
    return (
        "Use the following retrieved documents to help answer the user's question. "
        "If the documents don't contain relevant information, say so and answer "
        "based on your own knowledge.\n\n"
        "--- RETRIEVED DOCUMENTS ---\n\n"
        f"{context}\n\n"
        "--- END OF DOCUMENTS ---\n\n"
    )


# ---------- Status / Reset --------------------------------------------------

def get_status() -> Dict[str, Any]:
    """Return current RAG index status."""
    return {
        "total_chunks": len(_chunks),
        "total_documents": len(_documents),
        "index_size": _index.ntotal if _index else 0,
        "documents": [
            {"source": d["source"], "chunks": d["chunk_count"], "chars": d["char_count"]}
            for d in _documents
        ],
    }


def clear_index():
    """Reset the entire RAG index."""
    global _index, _chunks, _documents
    _index = None
    _chunks = []
    _documents = []
    _ensure_index()  # recreate empty index
    print("[RAG] Index cleared.")
    return {"status": "cleared"}
