import uuid
from typing import Any, Dict, List, Tuple
from app.database import save_job_posting, get_job_postings_for_role, get_role_requirements
from app.models.schemas import (
    CandidateProfile,
    JobPostingIngestRequest,
    JobPostingIngestResponse,
    SkillGapMapResponse,
    SkillGapRoleRequirement,
)
from app.services.skill_taxonomy import extract_skill_counts

FOUNDATION_SKILLS = {
    "Linux", "Networking", "Data Structures & Algorithms", "Python", "SQL & Databases",
    "Cloud Architecture", "Security & IAM",
}


def aggregate_requirements(postings: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """
    Deterministically turn N real job postings into a requirement map:
    a skill's weight is how many postings mention it (demand), and required_mastery
    scales with how consistently it appears across postings.
    """
    n = len(postings)
    if n == 0:
        return {}

    doc_freq: Dict[str, int] = {}
    for p in postings:
        for skill in p["extracted_skills"].keys():
            doc_freq[skill] = doc_freq.get(skill, 0) + 1

    total_mentions = sum(doc_freq.values()) or 1
    requirements: Dict[str, Dict[str, Any]] = {}
    for skill, freq in doc_freq.items():
        demand_pct = freq / n
        weight = round(freq / total_mentions, 3)
        # Appears in most postings => treat as a baseline/foundation expectation
        is_foundation = demand_pct >= 0.6 or skill in FOUNDATION_SKILLS
        required_mastery = 75 if demand_pct >= 0.75 else 70 if demand_pct >= 0.4 else 60
        requirements[skill] = {
            "weight": weight,
            "is_foundation": is_foundation,
            "required_mastery": required_mastery,
            "demand_pct": round(demand_pct * 100, 1),
        }
    return requirements


def ingest_job_posting(request: JobPostingIngestRequest) -> JobPostingIngestResponse:
    extracted = extract_skill_counts(request.raw_text)
    posting_id = f"job_{uuid.uuid4().hex[:10]}"
    save_job_posting(posting_id, request.role, request.company, request.raw_text, extracted)

    postings = get_job_postings_for_role(request.role)
    aggregated = aggregate_requirements(postings)

    return JobPostingIngestResponse(
        role=request.role,
        company=request.company,
        postings_analyzed=len(postings),
        extracted_skills=extracted,
        aggregated_requirements=aggregated,
    )


def get_effective_requirements(role: str) -> Tuple[Dict[str, Dict[str, Any]], str, int]:
    """Real ingested postings win when available; otherwise fall back to the static defaults."""
    postings = get_job_postings_for_role(role)
    if postings:
        return aggregate_requirements(postings), "real_job_postings", len(postings)
    return get_role_requirements(role), "fallback_defaults", 0


def build_skill_gap_map(candidate: CandidateProfile, target_role: str | None = None) -> SkillGapMapResponse:
    role = target_role or candidate.target_role
    requirements, source, postings_analyzed = get_effective_requirements(role)

    items: List[SkillGapRoleRequirement] = []
    missing: List[str] = []
    for skill, req in sorted(requirements.items(), key=lambda kv: -kv[1].get("weight", 0)):
        current = candidate.skills.get(skill, 0)
        required = req.get("required_mastery", 70)
        is_met = current >= required
        items.append(
            SkillGapRoleRequirement(
                skill=skill,
                demand_pct=req.get("demand_pct", round(req.get("weight", 0) * 100, 1)),
                required_mastery=required,
                current_mastery=current,
                is_met=is_met,
                is_foundation=req.get("is_foundation", False),
            )
        )
        if not is_met:
            missing.append(skill)

    return SkillGapMapResponse(
        target_role=role,
        source=source,
        postings_analyzed=postings_analyzed,
        requirements=items,
        missing_skills=missing,
    )
