import logging
from fastapi import APIRouter, Depends, HTTPException, Request, status

from backend.models.request_models import AskRequest
from backend.models.response_models import AskResponse, SourceModel
from backend.services.rag_service import RAGService

router = APIRouter()
logger = logging.getLogger(__name__)

def get_rag_service(request: Request) -> RAGService:
    return request.app.state.rag_service


@router.post("/ask", response_model=AskResponse, tags=["Chat"])
def ask_question(
    payload: AskRequest,
    rag_service: RAGService = Depends(get_rag_service)
) -> AskResponse:
    """
    Ask a question about the contents of indexed PDF documents. The response
    is strictly grounded in the document context.
    """
    try:
        logger.info(f"Received question query request: '{payload.question}'")
        
        result = rag_service.answer_question(payload.question)
        
        # Map output to Pydantic SourceModel list
        sources = [
            SourceModel(
                document=s["document"],
                page=s["page"],
                text=s["text"],
                score=s["score"]
            )
            for s in result.get("sources", [])
        ]
        
        return AskResponse(
            answer=result["answer"],
            sources=sources
        )
    except Exception as e:
        logger.error(f"RAG query generation failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while answering your question: {str(e)}"
        )
