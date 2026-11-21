import math
from datetime import datetime
from typing import List
from app.database import save_learning_plan, get_learning_plan
from app.models.schemas import CandidateProfile, LearningPlanResponse, WeekPlanItem
from app.services.job_market_service import build_skill_gap_map

MAX_WEEKS = 16
HOURS_PER_MASTERY_POINT = 1.2  # heuristic: ~1.2 learning-hours per point of mastery gap


def _tasks_for_skill(skill: str, gap: int) -> List[str]:
    if gap >= 30:
        return [f"Foundational course/tutorial on {skill}", f"Daily hands-on drills in {skill}", f"Build a small isolated exercise using {skill}"]
    if gap >= 15:
        return [f"Targeted practice problems in {skill}", f"Apply {skill} inside an existing project"]
    return [f"Polish {skill} with an advanced exercise or mock review"]


def generate_learning_plan(candidate: CandidateProfile, adjustment_note: str = "") -> LearningPlanResponse:
    gap_map = build_skill_gap_map(candidate)
    weekly_hours = max(3, int(candidate.learning_preferences.get("weekly_hours", 10) or 10))

    # Foundations first, biggest gap first within tier
    gaps = [
        (r.skill, max(0, r.required_mastery - r.current_mastery), r.is_foundation)
        for r in gap_map.requirements
        if r.required_mastery > r.current_mastery
    ]
    gaps.sort(key=lambda t: (not t[2], -t[1]))

    weeks: List[WeekPlanItem] = []
    week_num = 1
    for skill, gap, _is_foundation in gaps:
        if week_num > MAX_WEEKS:
            break
        hours_needed = gap * HOURS_PER_MASTERY_POINT
        weeks_needed = max(1, math.ceil(hours_needed / weekly_hours))
        for _ in range(weeks_needed):
            if week_num > MAX_WEEKS:
                break
            weeks.append(
                WeekPlanItem(
                    week=week_num,
                    focus_skills=[skill],
                    tasks=_tasks_for_skill(skill, gap),
                    hours_allocated=weekly_hours,
                    status="planned",
                )
            )
            week_num += 1

    if not weeks:
        weeks.append(
            WeekPlanItem(
                week=1,
                focus_skills=["Interview & portfolio polish"],
                tasks=["All tracked requirements are met — focus on mock interviews and a capstone project."],
                hours_allocated=weekly_hours,
                status="planned",
            )
        )

    # Final week is always an integration/interview-prep week
    weeks.append(
        WeekPlanItem(
            week=week_num,
            focus_skills=["Interview readiness"],
            tasks=["Run a mock interview on this week's weakest skills", "Update portfolio with newest project"],
            hours_allocated=weekly_hours,
            status="planned",
        )
    )

    note = adjustment_note or (
        f"Generated from {gap_map.source.replace('_', ' ')} "
        f"({gap_map.postings_analyzed} posting(s) analyzed)." if gap_map.source == "real_job_postings"
        else "Generated from built-in role defaults — ingest real job postings for a sharper plan."
    )

    plan_dicts = [w.model_dump() for w in weeks]
    save_learning_plan(candidate.id, gap_map.target_role, plan_dicts, gap_map.source, note)

    return LearningPlanResponse(
        candidate_id=candidate.id,
        target_role=gap_map.target_role,
        source=gap_map.source,
        total_weeks=len(weeks),
        weeks=weeks,
        adjustment_note=note,
        generated_at=datetime.now().strftime("%Y-%m-%d %H:%M"),
    )


def get_or_generate_plan(candidate: CandidateProfile) -> LearningPlanResponse:
    stored = get_learning_plan(candidate.id)
    if stored:
        return LearningPlanResponse(
            candidate_id=candidate.id,
            target_role=stored["target_role"],
            source=stored["source"],
            total_weeks=len(stored["weeks"]),
            weeks=[WeekPlanItem(**w) for w in stored["weeks"]],
            adjustment_note=stored["adjustment_note"] or "",
            generated_at=stored["generated_at"],
        )
    return generate_learning_plan(candidate)


def regenerate_plan_after_progress(candidate: CandidateProfile, trigger_type: str) -> None:
    """Called by the Career Twin update hook — progress tracking that actually adjusts the plan."""
    note = f"Plan auto-adjusted after '{trigger_type}' update on {datetime.now().strftime('%Y-%m-%d')}."
    generate_learning_plan(candidate, adjustment_note=note)
