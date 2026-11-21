from fastapi import APIRouter, HTTPException, status
from app.database import get_candidate
from app.models.schemas import ErrorResponse, ReadinessResponse
from app.services.readiness_service import calculate_readiness_score

router = APIRouter(prefix="/api/readiness", tags=["Readiness"])


@router.get(
    "/{candidate_id}",
    response_model=ReadinessResponse,
    responses={
        404: {"model": ErrorResponse, "description": "Candidate not found"}
    }
)
def get_candidate_readiness(candidate_id: str):
    """
    Computes deterministic Career Readiness Score for the candidate based on
    skill mastery, role weights, verified interview performance, portfolio
    completion, and skill evidence status.
    """
    candidate = get_candidate(candidate_id)
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Candidate with ID '{candidate_id}' not found",
        )

    return calculate_readiness_score(candidate)
