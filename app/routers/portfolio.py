from fastapi import APIRouter, HTTPException, status
from app.database import get_candidate
from app.models.schemas import (
    ErrorResponse,
    PortfolioProjectResponse,
    PortfolioRecommendRequest,
)
from app.services.portfolio_service import generate_portfolio_project_recommendation

router = APIRouter(prefix="/api/portfolio", tags=["Smart Portfolio Generator"])


@router.post(
    "/recommend",
    response_model=PortfolioProjectResponse,
    responses={
        404: {"model": ErrorResponse, "description": "Candidate not found"}
    }
)
def recommend_portfolio_project(request: PortfolioRecommendRequest):
    """
    Recommends a targeted, hands-on portfolio project tailored to the candidate's
    actual weakest verified-missing skills derived from Feature 2 evidence data.
    """
    candidate = get_candidate(request.candidate_id)
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Candidate with ID '{request.candidate_id}' not found",
        )

    return generate_portfolio_project_recommendation(candidate, variation_index=request.variation_index or 0)
