from typing import List, Optional
from app.database import get_role_requirements
from app.models.schemas import (
    CandidateProfile,
    PrerequisiteItem,
    RealityCheckResponse,
)
from app.services.gemini_service import (
    generate_prerequisite_explanation,
    sanitize_gemini_text,
)


def run_career_reality_check(
    candidate: CandidateProfile,
    target_role: Optional[str] = None,
    hypothetical_skills: Optional[dict] = None,
) -> RealityCheckResponse:
    """
    Performs deterministic gap analysis of candidate profile against target role prerequisites.
    Generates structured preparation sequence prioritizing foundational skills before advanced tools.
    Strictly prohibits hiring probability or guaranteed job timeline claims.
    """
    import copy
    candidate_eff = copy.deepcopy(candidate)
    if hypothetical_skills:
        for sk, val in hypothetical_skills.items():
            candidate_eff.skills[sk] = int(val)
            if int(val) >= 60 and sk in candidate_eff.skill_evidence:
                candidate_eff.skill_evidence[sk].status = "Project-demonstrated"
            elif int(val) >= 60:
                from app.models.schemas import SkillEvidence
                candidate_eff.skill_evidence[sk] = SkillEvidence(
                    resume_claimed=True,
                    resume_supported=True,
                    interview_demonstrated=False,
                    portfolio_demonstrated=True,
                    confidence="Moderate",
                    status="Project-demonstrated",
                )

    role = target_role or candidate_eff.target_role
    role_reqs = get_role_requirements(role, candidate_eff.skills)

    major_prerequisites: List[PrerequisiteItem] = []
    missing_foundations: List[str] = []
    missing_intermediate: List[str] = []
    missing_advanced: List[str] = []

    # Sort role requirements so foundations come first
    sorted_reqs = sorted(
        role_reqs.items(),
        key=lambda item: (not item[1].get("is_foundation", False), -item[1].get("weight", 0.0))
    )

    for skill_name, req in sorted_reqs:
        weight = req.get("weight", 1.0)
        req_mastery = req.get("required_mastery", 70)
        curr_mastery = candidate_eff.skills.get(skill_name, 0)
        is_foundation = req.get("is_foundation", False)

        ev = candidate_eff.skill_evidence.get(skill_name)
        ev_status = ev.status if ev else "Unverified"

        # A prerequisite is met if mastery is achieved and evidence is at least resume-supported
        is_met = (curr_mastery >= req_mastery) and (ev_status not in ["Unverified"])

        why_it_matters = sanitize_gemini_text(
            generate_prerequisite_explanation(skill_name, role)
        )

        item = PrerequisiteItem(
            skill=skill_name,
            importance_weight=round(weight, 2),
            required_mastery=req_mastery,
            current_mastery=curr_mastery,
            evidence_status=ev_status,
            is_met=is_met,
            why_it_matters=why_it_matters,
        )
        major_prerequisites.append(item)

        if not is_met:
            if is_foundation:
                missing_foundations.append(skill_name)
            elif weight >= 0.15:
                missing_intermediate.append(skill_name)
            else:
                missing_advanced.append(skill_name)

    # Determine current level
    if missing_foundations:
        current_level = "Beginner"
    elif missing_intermediate or missing_advanced:
        current_level = "Intermediate"
    else:
        current_level = "Advanced"

    # Deterministic preparation sequence: foundations always precede advanced
    prep_sequence: List[str] = []
    step_num = 1
    if missing_foundations:
        prep_sequence.append(
            f"Step {step_num}: Master core foundations — {', '.join(missing_foundations)} with verified hands-on labs."
        )
        step_num += 1

    if missing_intermediate:
        prep_sequence.append(
            f"Step {step_num}: Develop intermediate tooling & workflows — {', '.join(missing_intermediate)}."
        )
        step_num += 1

    if missing_advanced:
        prep_sequence.append(
            f"Step {step_num}: Advanced systems & scalability — {', '.join(missing_advanced)}."
        )
        step_num += 1

    prep_sequence.append(
        f"Step {step_num}: Build multi-component capstone project validating full-stack {role} competency."
    )
    step_num += 1
    prep_sequence.append(
        f"Step {step_num}: Conduct structured technical interview simulations to benchmark readiness."
    )

    # Next milestone
    if missing_foundations:
        next_milestone = f"Attain verified proficiency in foundational {missing_foundations[0]}."
    elif missing_intermediate:
        next_milestone = f"Complete practical implementation and verification for {missing_intermediate[0]}."
    elif missing_advanced:
        next_milestone = f"Build advanced architectural implementation for {missing_advanced[0]}."
    else:
        next_milestone = f"Complete capstone technical demonstration for {role}."

    return RealityCheckResponse(
        target_role=role,
        current_level=current_level,
        major_prerequisites=major_prerequisites,
        missing_foundations=missing_foundations,
        preparation_sequence=prep_sequence,
        next_milestone=next_milestone,
    )
