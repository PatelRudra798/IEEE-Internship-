import os
import shutil
import logging
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status, Request

from backend.config.settings import settings
from backend.models.response_models import UploadResponse, DocumentListResponse, DocumentInfo, DeleteResponse
from backend.services.pdf_service import extract_text
from backend.services.chunk_service import ChunkService
from backend.services.embedding_service import EmbeddingService
from backend.services.vector_service import VectorService

router = APIRouter()
logger = logging.getLogger(__name__)

# FastAPI state-based Dependency injection helpers
def get_chunk_service(request: Request) -> ChunkService:
    return request.app.state.chunk_service

def get_embedding_service(request: Request) -> EmbeddingService:
    return request.app.state.embedding_service

def get_vector_service(request: Request) -> VectorService:
    return request.app.state.vector_service


@router.post("/upload", response_model=UploadResponse, tags=["Documents"])
def upload_document(
    file: UploadFile = File(...),
    chunk_service: ChunkService = Depends(get_chunk_service),
    embedding_service: EmbeddingService = Depends(get_embedding_service),
    vector_service: VectorService = Depends(get_vector_service)
) -> UploadResponse:
    """
    Upload a PDF document, parse its text page-by-page, chunk it, embed it,
    and save it inside the ChromaDB vector database.
    """
    filename = file.filename
    if not filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file has no filename."
        )
        
    if not filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported file extension. Only PDF documents are accepted."
        )

    file_path = os.path.join(settings.uploads_path, filename)
    logger.info(f"Received upload request for '{filename}'. Storing at '{file_path}'")

    try:
        # 1. Write PDF payload to disk
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # 2. Extract text page-by-page
        pages_data = extract_text(file_path)

        # 3. Chunk the document
        chunks = chunk_service.chunk_document(pages_data, filename)
        if not chunks:
            # If no chunks were created, delete file and raise error
            if os.path.exists(file_path):
                os.remove(file_path)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Successfully parsed PDF, but no text content could be extracted for chunking."
            )

        # 4. Generate text embeddings
        chunk_texts = [c["text"] for c in chunks]
        embeddings = embedding_service.generate_embeddings(chunk_texts)

        # 5. Push to ChromaDB
        vector_service.add_documents(chunks, embeddings)

        logger.info(f"Upload and processing complete for '{filename}'. {len(chunks)} chunks cached.")
        return UploadResponse(
            success=True,
            filename=filename,
            chunks_processed=len(chunks)
        )

    except ValueError as e:
        logger.warning(f"Failed to process document content: {e}")
        # Clean up files on user validation failure
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except FileNotFoundError as e:
        logger.error(f"File saving operation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server disk writing failure occurred."
        )
    except Exception as e:
        logger.error(f"Unexpected error during PDF processing of '{filename}': {e}", exc_info=True)
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while indexing document: {str(e)}"
        )


@router.get("/documents", response_model=DocumentListResponse, tags=["Documents"])
def get_documents(
    vector_service: VectorService = Depends(get_vector_service)
) -> DocumentListResponse:
    """
    Retrieves all unique PDF files currently indexed in the vector database.
    """
    try:
        docs = vector_service.list_documents()
        doc_infos = [
            DocumentInfo(filename=d["filename"], chunks_count=d["chunks_count"])
            for d in docs
        ]
        return DocumentListResponse(documents=doc_infos)
    except Exception as e:
        logger.error(f"Failed to list documents: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to query indexed documents list: {str(e)}"
        )


@router.delete("/documents/{filename}", response_model=DeleteResponse, tags=["Documents"])
def delete_document(
    filename: str,
    vector_service: VectorService = Depends(get_vector_service)
) -> DeleteResponse:
    """
    Deletes an indexed PDF file: removes all its vector chunks from ChromaDB,
    and removes the file from local uploads storage.
    """
    file_path = os.path.join(settings.uploads_path, filename)
    
    in_db = False
    in_disk = os.path.exists(file_path)

    try:
        # Check if registered in ChromaDB
        docs = vector_service.list_documents()
        in_db = any(d["filename"] == filename for d in docs)

        if not in_db and not in_disk:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document '{filename}' is not indexed or found on disk."
            )

        # Remove database entries
        if in_db:
            vector_service.delete_document(filename)

        # Remove physical file
        if in_disk:
            os.remove(file_path)

        # Compile detailed message
        if in_db and in_disk:
            msg = f"Document '{filename}' deleted from database and disk storage."
        elif in_db and not in_disk:
            msg = f"Document '{filename}' deleted from database; file was not found on disk."
        else:
            msg = f"Document '{filename}' file deleted from disk; no database records found."

        logger.info(msg)
        return DeleteResponse(
            success=True,
            filename=filename,
            message=msg
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete document '{filename}': {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete document: {str(e)}"
        )
