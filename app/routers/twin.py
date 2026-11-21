from fastapi import APIRouter, HTTPException, status
from typing import List
from app.database import get_candidate, list_all_candidates, save_candidate, delete_candidate
from app.models.schemas import (
    CandidateProfile,
    CareerTwinUpdateRequest,
    ErrorResponse,
)
from app.services.twin_service import update_career_twin

router = APIRouter(prefix="/api/career-twin", tags=["Career Twin"])


@router.get("/roster/all", response_model=List[CandidateProfile])
def get_all_roster_candidates():
    """Returns all candidates currently in the system (persistent + in-memory)."""
    return list_all_candidates()


@router.post("/save-profile", response_model=CandidateProfile)
def save_candidate_profile(profile: CandidateProfile):
    """Saves or updates a candidate profile into persistent SQLite database."""
    save_candidate(profile, force_persist=True)
    return profile


@router.delete("/{candidate_id}")
def remove_candidate(candidate_id: str):
    """Deletes a candidate by ID."""
    success = delete_candidate(candidate_id)
    return {"candidate_id": candidate_id, "deleted": success}


@router.get(
    "/{candidate_id}",
    response_model=CandidateProfile,
    responses={
        404: {"model": ErrorResponse, "description": "Candidate not found"}
    }
)
def get_career_twin(candidate_id: str):
    """
    Retrieves the persistent Career Twin profile, including target career,
    skills, mastery, goals, learning preferences, completed projects,
    interview history, skill evidence, prior roadmaps, and twin summary.
    """
    candidate = get_candidate(candidate_id)
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Candidate with ID '{candidate_id}' not found",
        )
    return candidate


@router.post(
    "/update",
    response_model=CandidateProfile,
    responses={
        404: {"model": ErrorResponse, "description": "Candidate not found"},
        400: {"model": ErrorResponse, "description": "Invalid trigger or payload"}
    }
)
def update_career_twin_trigger(request: CareerTwinUpdateRequest):
    """
    Updates the persistent Career Twin upon lifecycle triggers:
      - interview_completed
      - learning_task_completed
      - project_completed
      - skill_assessed
    """
    try:
        updated_profile = update_career_twin(
            candidate_id=request.candidate_id,
            trigger_type=request.trigger_type,
            payload=request.payload,
        )
        return updated_profile
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(ve),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to update career twin: {str(e)}",
        )
