from fastapi import APIRouter, HTTPException, status
from app.database import get_candidate
from app.models.schemas import (
    ErrorResponse,
    RealityCheckRequest,
    RealityCheckResponse,
    SimulationRequest,
    SimulationResponse,
)
from app.services.reality_check_service import run_career_reality_check
from app.services.simulator_service import run_what_if_simulation

router = APIRouter(prefix="/api/career", tags=["Career Simulation & Insights"])


@router.post(
    "/simulate",
    response_model=SimulationResponse,
    responses={
        404: {"model": ErrorResponse, "description": "Candidate not found"}
    }
)
def simulate_career_impact(request: SimulationRequest):
    """
    Simulates readiness score changes in-memory based on hypothetical skill mastery improvements.
    Guarantees that the underlying candidate profile is never modified.
    """
    candidate = get_candidate(request.candidate_id)
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Candidate with ID '{request.candidate_id}' not found",
        )

    return run_what_if_simulation(candidate, request.hypothetical_skills)


@router.post(
    "/reality-check",
    response_model=RealityCheckResponse,
    responses={
        404: {"model": ErrorResponse, "description": "Candidate not found"}
    }
)
def career_reality_check(request: RealityCheckRequest):
    """
    Evaluates prerequisites, identifies missing foundations, and constructs
    an ordered preparation sequence. Prohibits hiring probability or guaranteed timeline claims.
    """
    candidate = get_candidate(request.candidate_id)
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Candidate with ID '{request.candidate_id}' not found",
        )

    return run_career_reality_check(candidate, request.target_role, request.hypothetical_skills)
