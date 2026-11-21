from datetime import datetime
from typing import Any, Dict
from app.config import DB_PATH
from app.database import get_candidate, save_candidate
from app.models.schemas import (
    CandidateProfile,
    InterviewRecord,
    ProjectRecord,
    TriggerType,
)
from app.services.evidence_service import evaluate_skill_evidence
from app.services.gemini_service import generate_career_twin_summary
from app.services.plan_service import regenerate_plan_after_progress


def update_career_twin(
    candidate_id: str,
    trigger_type: TriggerType,
    payload: Dict[str, Any],
    db_path: str = DB_PATH,
) -> CandidateProfile:
    """
    Plain service layer function that updates the persistent Career Twin
    across the four lifecycle triggers:
      - interview_completed
      - learning_task_completed
      - project_completed
      - skill_assessed
    """
    candidate = get_candidate(candidate_id, db_path=db_path)
    if not candidate:
        raise ValueError(f"Candidate '{candidate_id}' not found")

    # 1. Trigger: interview_completed
    if trigger_type == "interview_completed":
        interview_id = payload.get("interview_id", f"int_{int(datetime.now().timestamp())}")
        target_role = payload.get("target_role", candidate.target_role)
        date_str = payload.get("date", datetime.now().strftime("%Y-%m-%d"))
        perf_score = max(0, min(100, int(payload.get("performance_score", 70))))
        skills_eval = payload.get("skills_evaluated", [])
        feedback = payload.get("feedback", "")

        record = InterviewRecord(
            id=interview_id,
            target_role=target_role,
            date=date_str,
            performance_score=perf_score,
            skills_evaluated=skills_eval,
            feedback=feedback,
        )
        candidate.interview_history.append(record)

        # Update evidence for evaluated skills
        for skill in skills_eval:
            current_ev = candidate.skill_evidence.get(skill)
            resume_claimed = current_ev.resume_claimed if current_ev else (skill in candidate.skills)
            resume_supported = current_ev.resume_supported if current_ev else False
            portfolio_demo = current_ev.portfolio_demonstrated if current_ev else False
            
            # If interview passed (>= 60), mark interview_demonstrated
            interview_demo = (perf_score >= 60) or (current_ev.interview_demonstrated if current_ev else False)
            candidate.skill_evidence[skill] = evaluate_skill_evidence(
                resume_claimed=resume_claimed,
                resume_supported=resume_supported,
                interview_demonstrated=interview_demo,
                portfolio_demonstrated=portfolio_demo,
            )

    # 2. Trigger: learning_task_completed
    elif trigger_type == "learning_task_completed":
        skill_name = payload["skill_name"]
        increment = int(payload.get("mastery_increment", 5))
        current_mastery = candidate.skills.get(skill_name, 0)
        candidate.skills[skill_name] = max(0, min(100, current_mastery + increment))

        if payload.get("evidence_supported", False):
            current_ev = candidate.skill_evidence.get(skill_name)
            candidate.skill_evidence[skill_name] = evaluate_skill_evidence(
                resume_claimed=True,
                resume_supported=True,
                interview_demonstrated=current_ev.interview_demonstrated if current_ev else False,
                portfolio_demonstrated=current_ev.portfolio_demonstrated if current_ev else False,
            )

    # 3. Trigger: project_completed
    elif trigger_type == "project_completed":
        proj_id = payload.get("project_id", f"proj_{int(datetime.now().timestamp())}")
        title = payload.get("title", "Applied Technical Project")
        desc = payload.get("description", "")
        skills_demo = payload.get("skills_demonstrated", [])
        eval_score = max(0, min(100, int(payload.get("evaluation_score", 85))))
        comp_date = payload.get("completion_date", datetime.now().strftime("%Y-%m-%d"))

        proj_record = ProjectRecord(
            id=proj_id,
            title=title,
            description=desc,
            skills_demonstrated=skills_demo,
            completion_date=comp_date,
            evaluation_score=eval_score,
        )
        candidate.completed_projects.append(proj_record)

        # Update evidence for demonstrated skills
        for skill in skills_demo:
            current_ev = candidate.skill_evidence.get(skill)
            resume_claimed = current_ev.resume_claimed if current_ev else (skill in candidate.skills)
            resume_supported = current_ev.resume_supported if current_ev else False
            interview_demo = current_ev.interview_demonstrated if current_ev else False

            candidate.skill_evidence[skill] = evaluate_skill_evidence(
                resume_claimed=resume_claimed,
                resume_supported=resume_supported,
                interview_demonstrated=interview_demo,
                portfolio_demonstrated=True,
            )
            # Uplift mastery if evaluation score is higher
            if eval_score > candidate.skills.get(skill, 0):
                candidate.skills[skill] = eval_score

    # 4. Trigger: skill_assessed
    elif trigger_type == "skill_assessed":
        skill_name = payload["skill_name"]
        score = max(0, min(100, int(payload.get("mastery_score", 50))))
        verified = bool(payload.get("verified", False))

        candidate.skills[skill_name] = score

        current_ev = candidate.skill_evidence.get(skill_name)
        resume_claimed = True
        resume_supported = verified or (current_ev.resume_supported if current_ev else False)
        interview_demo = current_ev.interview_demonstrated if current_ev else False
        portfolio_demo = current_ev.portfolio_demonstrated if current_ev else False

        candidate.skill_evidence[skill_name] = evaluate_skill_evidence(
            resume_claimed=resume_claimed,
            resume_supported=resume_supported,
            interview_demonstrated=interview_demo,
            portfolio_demonstrated=portfolio_demo,
        )

    # 5. Refresh concise 1-2 sentence twin summary (via Gemini or deterministic fallback)
    top_skills = sorted(
        candidate.skills.keys(),
        key=lambda s: candidate.skills[s],
        reverse=True,
    )
    candidate.twin_summary = generate_career_twin_summary(
        name=candidate.name,
        target_role=candidate.target_role,
        top_skills=top_skills,
        completed_projects_count=len(candidate.completed_projects),
        verified_interviews_count=len(candidate.interview_history),
    )

    # Persist updated Career Twin
    save_candidate(candidate, db_path=db_path)

    # Progress tracking that adjusts the plan: regenerate the week-by-week
    # learning plan whenever real progress changes the candidate's skill gaps.
    try:
        regenerate_plan_after_progress(candidate, trigger_type)
    except Exception:
        pass  # plan regeneration is best-effort; never block the twin update itself

    return candidate
