import copy
from typing import Dict, List
from app.database import get_role_requirements
from app.models.schemas import CandidateProfile, SimulationResponse
from app.services.readiness_service import calculate_readiness_score


def run_what_if_simulation(
    candidate: CandidateProfile,
    hypothetical_skills: Dict[str, int]
) -> SimulationResponse:
    """
    Simulates readiness score changes in-memory without modifying the candidate profile.
    Guarantees zero database or in-place mutations.
    """
    # 1. Base readiness calculation
    current_res = calculate_readiness_score(candidate)
    current_score = current_res.overall_score

    # 2. In-memory clone (guaranteed isolated copy)
    simulated_candidate = copy.deepcopy(candidate)

    newly_improved = []
    from app.models.schemas import SkillEvidence, ProjectRecord
    for skill_name, target_mastery in hypothetical_skills.items():
        original_mastery = candidate.skills.get(skill_name, 0)
        target_clamped = max(0, min(100, int(target_mastery)))
        simulated_candidate.skills[skill_name] = target_clamped

        if target_clamped > original_mastery:
            newly_improved.append(skill_name)
            if target_clamped >= 60:
                simulated_candidate.skill_evidence[skill_name] = SkillEvidence(
                    resume_claimed=True,
                    resume_supported=True,
                    interview_demonstrated=target_clamped >= 80,
                    portfolio_demonstrated=target_clamped >= 70,
                    confidence="High" if target_clamped >= 80 else "Moderate",
                    status="Strongly-supported" if target_clamped >= 80 else "Project-demonstrated",
                )

    if newly_improved and not simulated_candidate.completed_projects:
        simulated_candidate.completed_projects = [
            ProjectRecord(
                id="sim_proj",
                title="Simulated Capstone Implementation",
                description="Practical project demonstrating improved technical skills",
                skills_demonstrated=newly_improved[:3],
                evaluation_score=85,
            )
        ]

    # 3. Simulated readiness calculation
    sim_res = calculate_readiness_score(simulated_candidate)
    simulated_score = sim_res.overall_score
    delta = simulated_score - current_score

    # 4. Identify remaining weaknesses
    role_reqs = get_role_requirements(candidate.target_role, candidate.skills)
    remaining_weaknesses = []
    for skill_name, req_info in role_reqs.items():
        req_mastery = req_info.get("required_mastery", 70)
        current_or_sim = simulated_candidate.skills.get(skill_name, 0)
        if current_or_sim < req_mastery:
            remaining_weaknesses.append(skill_name)

    # 5. Deterministic recommendation for next best skill
    # Evaluate marginal gain for each remaining weakness
    recommended_next_skill = ""
    max_marginal_gain = -1

    for weak_skill in remaining_weaknesses:
        test_candidate = copy.deepcopy(simulated_candidate)
        test_req_mastery = role_reqs.get(weak_skill, {}).get("required_mastery", 75)
        test_candidate.skills[weak_skill] = test_req_mastery
        test_score = calculate_readiness_score(test_candidate).overall_score
        gain = test_score - simulated_score
        if gain > max_marginal_gain:
            max_marginal_gain = gain
            recommended_next_skill = weak_skill

    if not recommended_next_skill and remaining_weaknesses:
        recommended_next_skill = remaining_weaknesses[0]
    elif not recommended_next_skill:
        recommended_next_skill = "All role prerequisite skills meet target standards"

    return SimulationResponse(
        current_score=current_score,
        simulated_score=simulated_score,
        delta=delta,
        newly_improved_skills=newly_improved,
        remaining_weaknesses=remaining_weaknesses,
        recommended_next_skill=recommended_next_skill,
    )
