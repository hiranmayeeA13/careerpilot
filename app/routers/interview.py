from fastapi import APIRouter, HTTPException, status
from app.database import get_candidate
from app.models.schemas import (
    ErrorResponse, InterviewStartResponse, InterviewSubmitRequest, InterviewSubmitResponse,
)
from app.services.interview_service import generate_mock_interview, submit_mock_interview

router = APIRouter(prefix="/api/interview", tags=["Mock Interviews"])


@router.post(
    "/start/{candidate_id}",
    response_model=InterviewStartResponse,
    responses={404: {"model": ErrorResponse, "description": "Candidate not found"}},
)
def start_interview(candidate_id: str, variant: int = 0):
    """Generates a mock interview targeting the candidate's weakest skill-gap areas."""
    candidate = get_candidate(candidate_id)
    if not candidate:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Candidate with ID '{candidate_id}' not found")
    return generate_mock_interview(candidate, variant=variant)


@router.post("/submit", response_model=InterviewSubmitResponse)
def submit_interview(request: InterviewSubmitRequest):
    """
    Scores each answer deterministically against its rubric's keyword criteria,
    then feeds the result back into the Career Twin (updating evidence + readiness + the plan).
    """
    try:
        return submit_mock_interview(request)
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(ve))
