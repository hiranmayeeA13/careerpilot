from fastapi import APIRouter, HTTPException, status
from app.database import get_candidate
from app.models.schemas import (
    ErrorResponse, JobPostingIngestRequest, JobPostingIngestResponse, SkillGapMapResponse,
)
from app.services.job_market_service import ingest_job_posting, build_skill_gap_map

router = APIRouter(prefix="/api/jobs", tags=["Job Market & Skill Gap"])


@router.post("/ingest", response_model=JobPostingIngestResponse)
def ingest_posting(request: JobPostingIngestRequest):
    """
    Paste a real job description; it's parsed for skill keywords and folded into that
    role's requirement map (weighted by how many postings mention each skill).
    """
    return ingest_job_posting(request)


@router.get(
    "/skill-gap/{candidate_id}",
    response_model=SkillGapMapResponse,
    responses={404: {"model": ErrorResponse, "description": "Candidate not found"}},
)
def skill_gap_map(candidate_id: str, target_role: str | None = None):
    """
    Skill-gap map for a candidate. Uses real ingested job postings for the role when any
    exist; otherwise falls back to the built-in role defaults (and says so in `source`).
    """
    candidate = get_candidate(candidate_id)
    if not candidate:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Candidate with ID '{candidate_id}' not found")
    return build_skill_gap_map(candidate, target_role)
