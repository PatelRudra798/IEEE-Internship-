from fastapi import APIRouter
from backend.models.response_models import HealthResponse

router = APIRouter()

@router.get("/health", response_model=HealthResponse, tags=["Health"])
async def get_health() -> HealthResponse:
    """
    Check the health of the FastAPI backend.
    """
    return HealthResponse(status="healthy")
