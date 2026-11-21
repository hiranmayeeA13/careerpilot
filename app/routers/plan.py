from fastapi import APIRouter, HTTPException, status
from app.database import get_candidate
from app.models.schemas import ErrorResponse, LearningPlanResponse
from app.services.plan_service import generate_learning_plan, get_or_generate_plan

router = APIRouter(prefix="/api/plan", tags=["Week-by-Week Learning Plan"])


@router.get(
    "/{candidate_id}",
    response_model=LearningPlanResponse,
    responses={404: {"model": ErrorResponse, "description": "Candidate not found"}},
)
def get_plan(candidate_id: str):
    """Returns the candidate's current week-by-week plan, generating one if none exists yet."""
    candidate = get_candidate(candidate_id)
    if not candidate:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Candidate with ID '{candidate_id}' not found")
    return get_or_generate_plan(candidate)


@router.post(
    "/{candidate_id}/regenerate",
    response_model=LearningPlanResponse,
    responses={404: {"model": ErrorResponse, "description": "Candidate not found"}},
)
def regenerate_plan(candidate_id: str):
    """Force-regenerates the plan from the candidate's current skill gaps."""
    candidate = get_candidate(candidate_id)
    if not candidate:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Candidate with ID '{candidate_id}' not found")
    return generate_learning_plan(candidate, adjustment_note="Manually regenerated.")
