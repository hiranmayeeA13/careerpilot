from app.models.schemas import ConfidenceLevel, EvidenceStatus, SkillEvidence


def evaluate_skill_evidence(
    resume_claimed: bool = False,
    resume_supported: bool = False,
    interview_demonstrated: bool = False,
    portfolio_demonstrated: bool = False
) -> SkillEvidence:
    """
    Deterministically computes evidence status and confidence level for a skill.
    
    Status Hierarchy:
    Unverified -> Resume-supported -> Interview-demonstrated -> Project-demonstrated -> Strongly-supported
    
    Rule:
    A skill with resume_claimed=True and nothing else must NEVER return
    'verified' or 'strongly-supported'; its status is strictly 'Unverified' with 'Low' confidence.
    """
    # 1. Determine Status
    if interview_demonstrated and portfolio_demonstrated:
        status: EvidenceStatus = "Strongly-supported"
    elif portfolio_demonstrated:
        status = "Project-demonstrated"
    elif interview_demonstrated:
        status = "Interview-demonstrated"
    elif resume_supported:
        status = "Resume-supported"
    else:
        status = "Unverified"

    # 2. Determine Confidence Level
    if interview_demonstrated and portfolio_demonstrated:
        confidence: ConfidenceLevel = "High"
    elif resume_supported or interview_demonstrated or portfolio_demonstrated:
        confidence = "Moderate"
    else:
        confidence = "Low"

    return SkillEvidence(
        resume_claimed=bool(resume_claimed),
        resume_supported=bool(resume_supported),
        interview_demonstrated=bool(interview_demonstrated),
        portfolio_demonstrated=bool(portfolio_demonstrated),
        confidence=confidence,
        status=status,
    )


def get_status_weight(status: EvidenceStatus) -> float:
    """Deterministic numeric weight for evidence status used in readiness scoring."""
    weights = {
        "Strongly-supported": 1.0,
        "Project-demonstrated": 0.75,
        "Interview-demonstrated": 0.65,
        "Resume-supported": 0.35,
        "Unverified": 0.0,
    }
    return weights.get(status, 0.0)
