"""
readiness_service.py — Deterministic Career Readiness Scoring Engine

Scoring Formula Documentation:
------------------------------
Overall Readiness Score (0-100, int) is a deterministic weighted linear combination
of four normalized pillar scores:

  overall_score = round(
      0.40 * score_skills +
      0.25 * score_interview +
      0.20 * score_portfolio +
      0.15 * score_evidence
  )

Where:
  1. score_skills (0-100, float):
     Weighted average of candidate's mastery in target role requirements:
       sum(mastery_s * weight_s for s in role_skills) / sum(weight_s)
     (Defaults to 0 if no skills present).

  2. score_interview (0-100, float):
     Average performance score across candidate's verified interview records.
     (Defaults to 0.0 if no interviews have been completed).

  3. score_portfolio (0-100, float):
     Portfolio completion metric:
       min(1.0, len(completed_projects) / 2.0) * avg_project_evaluation_score
     (Defaults to 0.0 if no completed projects).

  4. score_evidence (0-100, float):
     Weighted verification status score for required skills:
       Strongly-supported     -> 100.0
       Project-demonstrated   -> 75.0
       Interview-demonstrated -> 65.0
       Resume-supported       -> 35.0
       Unverified             -> 0.0
     Aggregated by role skill importance weights.

Category Thresholds:
  - 0  .. 49 : "Beginner"
  - 50 .. 74 : "Developing"
  - 75 .. 100: "Job-Ready"
"""

from typing import Dict, List, Tuple
from app.database import get_role_requirements
from app.models.schemas import (
    CandidateProfile,
    ReadinessBreakdown,
    ReadinessCategory,
    ReadinessResponse,
    SkillEvidence,
)
from app.services.evidence_service import evaluate_skill_evidence, get_status_weight


def calculate_readiness_score(candidate: CandidateProfile) -> ReadinessResponse:
    """
    Computes candidate readiness deterministically without LLM calls.
    Returns identical results on repeated calls with unchanged data.
    """
    role_reqs = get_role_requirements(candidate.target_role, candidate.skills)

    # 1. Skill Mastery Sub-score (Weight: 40%)
    total_skill_weight = 0.0
    weighted_mastery_sum = 0.0
    for skill_name, req_info in role_reqs.items():
        weight = req_info.get("weight", 1.0)
        total_skill_weight += weight
        mastery = candidate.skills.get(skill_name, 0)
        weighted_mastery_sum += mastery * weight

    score_skills = (
        (weighted_mastery_sum / total_skill_weight)
        if total_skill_weight > 0
        else 0.0
    )

    # 2. Verified Interview Performance Sub-score (Weight: 25%)
    if candidate.interview_history:
        score_interview = sum(
            i.performance_score for i in candidate.interview_history
        ) / len(candidate.interview_history)
    else:
        score_interview = 0.0

    # 3. Portfolio Completion Sub-score (Weight: 20%)
    if candidate.completed_projects:
        qty_factor = min(1.0, len(candidate.completed_projects) / 2.0)
        avg_eval = sum(
            (p.evaluation_score or 80) for p in candidate.completed_projects
        ) / len(candidate.completed_projects)
        score_portfolio = qty_factor * avg_eval
    else:
        score_portfolio = 0.0

    # 4. Evidence Verification Sub-score (Weight: 15%)
    total_ev_weight = 0.0
    weighted_ev_sum = 0.0
    for skill_name, req_info in role_reqs.items():
        weight = req_info.get("weight", 1.0)
        total_ev_weight += weight

        ev = candidate.skill_evidence.get(skill_name)
        if not ev:
            ev = evaluate_skill_evidence(
                resume_claimed=skill_name in candidate.skills,
                resume_supported=False,
                interview_demonstrated=False,
                portfolio_demonstrated=False,
            )
        weighted_ev_sum += (get_status_weight(ev.status) * 100.0) * weight

    score_evidence = (
        (weighted_ev_sum / total_ev_weight)
        if total_ev_weight > 0
        else 0.0
    )

    # Composite Overall Score (0-100)
    raw_overall = (
        0.40 * score_skills +
        0.25 * score_interview +
        0.20 * score_portfolio +
        0.15 * score_evidence
    )
    overall_score = max(0, min(100, int(round(raw_overall))))

    # Category Assignment
    if overall_score >= 75:
        category: ReadinessCategory = "Job-Ready"
    elif overall_score >= 50:
        category = "Developing"
    else:
        category = "Beginner"

    # Deterministic Positive & Negative Factors
    positive_factors, negative_factors = _extract_factors(
        candidate, role_reqs, score_interview, score_portfolio
    )

    # Deterministic Recommended Next Action Template
    recommended_action = _generate_recommended_action(
        candidate, role_reqs, score_interview, score_portfolio
    )

    return ReadinessResponse(
        overall_score=overall_score,
        category=category,
        breakdown=ReadinessBreakdown(
            skills=round(score_skills, 2),
            interview=round(score_interview, 2),
            portfolio=round(score_portfolio, 2),
            evidence=round(score_evidence, 2),
        ),
        top_positive_factors=positive_factors[:3],
        top_negative_factors=negative_factors[:3],
        recommended_next_action=recommended_action,
    )


def _extract_factors(
    candidate: CandidateProfile,
    role_reqs: Dict,
    score_interview: float,
    score_portfolio: float,
) -> Tuple[List[str], List[str]]:
    positives = []
    negatives = []

    # Check skills & evidence
    for skill_name, req_info in role_reqs.items():
        mastery = candidate.skills.get(skill_name, 0)
        req_mastery = req_info.get("required_mastery", 70)
        ev = candidate.skill_evidence.get(skill_name)
        ev_status = ev.status if ev else "Unverified"

        if mastery >= req_mastery:
            positives.append(f"Strong mastery in {skill_name} ({mastery}/100)")
        elif mastery < 50:
            negatives.append(f"Low foundational mastery in {skill_name} ({mastery}/100)")

        if ev_status in ["Strongly-supported", "Project-demonstrated"]:
            positives.append(f"{ev_status} verification for {skill_name}")
        elif ev_status == "Unverified" and req_info.get("is_foundation", False):
            negatives.append(f"Unverified evidence status for critical skill {skill_name}")

    # Check interview
    if score_interview >= 75:
        positives.append(f"Demonstrated technical interview proficiency ({int(score_interview)}/100)")
    elif score_interview == 0:
        negatives.append("No verified technical interview performance on record")
    elif score_interview < 60:
        negatives.append(f"Developing interview performance ({int(score_interview)}/100)")

    # Check portfolio
    if score_portfolio >= 70:
        positives.append(f"Solid portfolio backing with {len(candidate.completed_projects)} completed project(s)")
    elif score_portfolio == 0:
        negatives.append("Zero completed portfolio projects demonstrated")
    elif score_portfolio < 50:
        negatives.append("Portfolio project depth below target role expectations")

    if not positives:
        positives.append(f"Baseline technical profile established for {candidate.target_role}")
    if not negatives:
        negatives.append("No critical skill or evidence deficiencies detected")

    return positives, negatives


def _generate_recommended_action(
    candidate: CandidateProfile,
    role_reqs: Dict,
    score_interview: float,
    score_portfolio: float,
) -> str:
    """Generate one-sentence deterministic template action."""
    # Priority 1: Missing foundational skills
    for skill_name, req_info in role_reqs.items():
        if req_info.get("is_foundation") and candidate.skills.get(skill_name, 0) < req_info.get("required_mastery", 70):
            return (
                f"Build foundational proficiency in {skill_name} to meet the baseline requirement "
                f"for {candidate.target_role}."
            )

    # Priority 2: Unverified evidence on key skills
    for skill_name in role_reqs.keys():
        ev = candidate.skill_evidence.get(skill_name)
        if not ev or ev.status in ["Unverified", "Resume-supported"]:
            return (
                f"Complete a hands-on project demonstrating {skill_name} to elevate your skill evidence "
                f"to Project-demonstrated."
            )

    # Priority 3: Portfolio completion
    if len(candidate.completed_projects) < 2:
        return (
            f"Develop a complete portfolio project demonstrating {candidate.target_role} architecture."
        )

    # Priority 4: Interview readiness
    if score_interview < 70:
        return (
            f"Participate in a structured technical assessment interview for {candidate.target_role}."
        )

    return (
        f"Maintain job-ready status by refining advanced distributed systems and reviewing modern {candidate.target_role} practices."
    )
