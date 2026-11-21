import uuid
from datetime import datetime
from app.database import create_candidate
from app.models.schemas import CandidateProfile, SkillEvidence, ResumeIntakeRequest, ResumeIntakeResponse
from app.services.skill_taxonomy import extract_skill_counts, mastery_from_resume_count


def run_resume_intake(request: ResumeIntakeRequest) -> ResumeIntakeResponse:
    counts = extract_skill_counts(request.resume_text)

    skills = {}
    skill_evidence = {}
    for skill, count in counts.items():
        mastery = mastery_from_resume_count(count)
        skills[skill] = mastery
        skill_evidence[skill] = SkillEvidence(
            resume_claimed=True,
            resume_supported=count >= 2,
            interview_demonstrated=False,
            portfolio_demonstrated=False,
            confidence="Moderate" if count >= 2 else "Low",
            status="Resume-supported" if count >= 2 else "Unverified",
        )

    candidate_id = f"cand_{uuid.uuid4().hex[:10]}"
    candidate = CandidateProfile(
        id=candidate_id,
        name=request.name,
        target_role=request.target_role,
        skills=skills,
        skill_evidence=skill_evidence,
        goals=[
            f"Reach Job-Ready readiness for {request.target_role}",
            "Complete first verified hands-on capstone project",
            "Demonstrate core architecture mastery in technical mock interview",
        ],
        learning_preferences={"preferred_format": "hands-on projects", "weekly_hours": request.weekly_hours or 10},
        completed_projects=[],
        interview_history=[],
        prior_roadmaps=[],
        twin_summary=(
            f"{request.name} is preparing toward {request.target_role}. "
            f"Resume intake identified {len(skills)} skill signal(s). Complete mock interviews and portfolio projects to strengthen verification status."
        ),
        updated_at=datetime.now().strftime("%Y-%m-%d"),
    )

    should_persist = getattr(request, "save_to_database", True)
    if should_persist is None:
        should_persist = True

    create_candidate(candidate, persist=should_persist)

    return ResumeIntakeResponse(
        candidate_id=candidate_id,
        name=request.name,
        target_role=request.target_role,
        extracted_skills=skills,
        skills_detected=len(skills),
        message=(
            f"Candidate profile initialized {'and saved to persistent database' if should_persist else 'in temporary session'}. "
            f"Detected {len(skills)} skills ready for exploration across Career Twin, Simulator, and Mock Interviews."
        ),
    )
