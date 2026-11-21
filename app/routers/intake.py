from fastapi import APIRouter, HTTPException
from app.models.schemas import ResumeIntakeRequest, ResumeIntakeResponse
from app.services.intake_service import run_resume_intake
from app.database import save_intake_candidate

router = APIRouter(prefix="/api/intake", tags=["Resume & Role Intake"])


@router.post("/resume", response_model=ResumeIntakeResponse)
def intake_resume(request: ResumeIntakeRequest):
    """
    Creates a brand-new candidate from pasted resume text + a target role.
    Skills are extracted deterministically via keyword matching (never an LLM),
    and start as Unverified/Resume-supported until backed by interview or project evidence.
    """
    return run_resume_intake(request)



@router.post("/resume/{candidate_id}/save")
def save_resume_candidate(candidate_id: str):
    """Persist a resume-intake candidate only after the user selects Save profile."""
    candidate = save_intake_candidate(candidate_id)
    if candidate is None:
        raise HTTPException(status_code=404, detail="Temporary candidate not found or already expired.")
    return {"candidate_id": candidate.id, "saved": True, "message": "Profile saved to the persistent roster."}
