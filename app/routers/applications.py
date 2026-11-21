from fastapi import APIRouter, HTTPException, status
from app.models.schemas import (
    ApplicationLogRequest, ApplicationRecord, ApplicationStatusUpdateRequest,
    ApplicationInsightsResponse,
)
from app.services.application_service import log_application, update_status, list_applications, compute_insights

router = APIRouter(prefix="/api/applications", tags=["Application Tracker"])


@router.post("/log", response_model=ApplicationRecord)
def log_app(request: ApplicationLogRequest):
    """Logs a job application. role_category is derived automatically (Senior/Mid-level/Junior)."""
    return log_application(request)


@router.get("/{candidate_id}", response_model=list[ApplicationRecord])
def get_apps(candidate_id: str):
    return list_applications(candidate_id)


@router.patch("/{app_id}/status", response_model=dict)
def patch_status(app_id: str, request: ApplicationStatusUpdateRequest):
    changed = update_status(app_id, request.status)
    if not changed:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Application '{app_id}' not found")
    return {"id": app_id, "status": request.status, "updated": True}


@router.get("/{candidate_id}/insights", response_model=ApplicationInsightsResponse)
def get_insights(candidate_id: str):
    """
    Learns which kinds of roles respond: aggregates response rate by role category
    (Senior / Mid-level / Junior-Entry) from the candidate's logged application history.
    """
    return compute_insights(candidate_id)
