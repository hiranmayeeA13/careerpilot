import uuid
from datetime import datetime
from typing import List
from app.database import save_application, get_applications, update_application_status
from app.models.schemas import (
    ApplicationLogRequest,
    ApplicationRecord,
    ApplicationInsightsResponse,
    CategoryInsight,
)

RESPONDED_STATUSES = {"Interviewing", "Offer", "Rejected"}  # any of these means the company DID respond


def classify_role_category(role_title: str) -> str:
    t = role_title.lower()
    if any(k in t for k in ["senior", "sr.", "staff", "lead", "principal"]):
        return "Senior"
    if any(k in t for k in ["junior", "jr.", "entry", "intern", "graduate", "associate"]):
        return "Junior/Entry"
    return "Mid-level"


def log_application(request: ApplicationLogRequest) -> ApplicationRecord:
    app_id = f"app_{uuid.uuid4().hex[:10]}"
    category = classify_role_category(request.role_title)
    date_applied = request.date_applied or datetime.now().strftime("%Y-%m-%d")
    responded = request.status in RESPONDED_STATUSES

    save_application(
        app_id, request.candidate_id, request.company, request.role_title,
        category, date_applied, request.status, responded,
    )

    return ApplicationRecord(
        id=app_id, candidate_id=request.candidate_id, company=request.company,
        role_title=request.role_title, role_category=category, date_applied=date_applied,
        status=request.status, responded=responded,
    )


def update_status(app_id: str, status: str) -> bool:
    responded = status in RESPONDED_STATUSES
    return update_application_status(app_id, status, responded)


def list_applications(candidate_id: str) -> List[ApplicationRecord]:
    rows = get_applications(candidate_id)
    return [
        ApplicationRecord(
            id=r["id"], candidate_id=r["candidate_id"], company=r["company"],
            role_title=r["role_title"], role_category=r["role_category"],
            date_applied=r["date_applied"], status=r["status"],
            responded=bool(r["responded"]), updated_at=r["updated_at"],
        )
        for r in rows
    ]


def compute_insights(candidate_id: str) -> ApplicationInsightsResponse:
    apps = list_applications(candidate_id)
    total = len(apps)
    total_responded = sum(1 for a in apps if a.responded)
    overall_rate = round(100 * total_responded / total, 1) if total else 0.0

    by_category: dict = {}
    for a in apps:
        bucket = by_category.setdefault(a.role_category, {"applied": 0, "responded": 0})
        bucket["applied"] += 1
        bucket["responded"] += int(a.responded)

    category_insights: List[CategoryInsight] = [
        CategoryInsight(
            category=cat, applied=v["applied"], responded=v["responded"],
            response_rate=round(100 * v["responded"] / v["applied"], 1) if v["applied"] else 0.0,
        )
        for cat, v in by_category.items()
    ]
    category_insights.sort(key=lambda c: -c.response_rate)

    if total == 0:
        recommendation = "Log a few applications to start surfacing which role types respond best."
    elif len(category_insights) >= 2 and category_insights[0].response_rate > category_insights[-1].response_rate:
        best, worst = category_insights[0], category_insights[-1]
        recommendation = (
            f"{best.category} roles are responding at {best.response_rate}% vs {worst.response_rate}% for "
            f"{worst.category} — lean into {best.category} applications and tailor your resume toward that band."
        )
    else:
        recommendation = f"Overall response rate is {overall_rate}% — log more applications across role levels to sharpen this pattern."

    return ApplicationInsightsResponse(
        candidate_id=candidate_id,
        total_applications=total,
        overall_response_rate=overall_rate,
        by_role_category=category_insights,
        recommendation=recommendation,
    )
