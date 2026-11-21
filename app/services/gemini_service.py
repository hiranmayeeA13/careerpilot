import logging
import asyncio
from typing import Optional
from app.config import GEMINI_API_KEY, GEMINI_MODEL, GEMINI_TIMEOUT_SECONDS

logger = logging.getLogger(__name__)

# Banned terms filter to guarantee policy compliance even if LLM generates them
BANNED_PHRASES = [
    "hireability",
    "will get you hired",
    "guaranteed job",
    "guaranteed timeline",
    "hiring probability",
    "chance of being hired",
    "guarantee you a job",
    "get hired in",
    "job guarantee",
]

def sanitize_gemini_text(text: str) -> str:
    cleaned = text
    for phrase in BANNED_PHRASES:
        cleaned = cleaned.replace(phrase, "readiness development")
        cleaned = cleaned.replace(phrase.capitalize(), "Readiness development")
        cleaned = cleaned.replace(phrase.title(), "Readiness Development")
    return cleaned


def generate_career_twin_summary(
    name: str,
    target_role: str,
    top_skills: list[str],
    completed_projects_count: int,
    verified_interviews_count: int,
) -> str:
    """Generate 1-2 sentence career twin summary with graceful fallback."""
    fallback = (
        f"{name} is actively advancing technical readiness for the {target_role} path, "
        f"with demonstrated competencies in {', '.join(top_skills[:3]) or 'foundational domains'} "
        f"and {completed_projects_count} verified practical project milestone(s)."
    )

    if not GEMINI_API_KEY:
        return fallback

    prompt = (
        f"Provide a concise, professional 1-2 sentence career profile summary for {name}, "
        f"who is preparing for the role of {target_role}. "
        f"Current strengths include: {', '.join(top_skills[:3]) or 'foundational tools'}. "
        f"Completed projects: {completed_projects_count}, completed interviews: {verified_interviews_count}. "
        f"STRICT CONSTRAINT: Do NOT state or imply any hiring outcome, hiring probability, "
        f"guaranteed job, or timeline to get hired. Focus strictly on skill readiness."
    )

    try:
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel(GEMINI_MODEL)
        response = model.generate_content(prompt)
        if response and response.text:
            return sanitize_gemini_text(response.text.strip())
    except Exception as e:
        logger.warning("Gemini API call failed, using deterministic fallback: %s", e)

    return fallback


def generate_prerequisite_explanation(skill: str, target_role: str) -> str:
    """Generate a one-line explanation of why a foundational prerequisite matters."""
    fallbacks = {
        "Linux": f"Linux provides the essential operating system runtime and command-line automation baseline for {target_role}.",
        "Networking": f"Networking fundamentals (TCP/IP, DNS, routing) govern secure system communication and reliable distributed architecture in {target_role}.",
        "Docker": f"Containerization underpins reproducible deployments, microservice isolation, and modern cloud deployment pipelines.",
        "Kubernetes": f"Kubernetes orchestration coordinates scalable container lifecycles, service discovery, and resilient cluster state.",
        "CI/CD": f"Continuous integration and delivery enables verified code promotion and automated validation gates.",
        "Cloud/AWS": f"Cloud infrastructure services provide the scalable compute, storage, and networking primitives required in {target_role}.",
        "Data Structures & Algorithms": f"Core data structures determine algorithmic efficiency, resource constraints, and backend system scaling.",
        "Python": f"Python serves as the primary implementation language for backend application logic, automation, and tooling.",
        "SQL & Databases": f"Relational database design and query optimization ensure data integrity, indexing efficiency, and persistent storage reliability.",
        "API Design & REST": f"Clear API contracts and HTTP RESTful standards ensure decoupled, maintainable client-service communication.",
        "System Design": f"High-level system design ensures fault tolerance, load distribution, and scalability under high concurrency.",
        "Cloud Architecture": f"Architectural blueprints ensure multi-region resilience, scalability, and secure service topology in {target_role}.",
        "Security & IAM": f"Identity and access management enforces least privilege, zero-trust boundaries, and compliance protection.",
        "DevOps & IaC": f"Infrastructure as Code codifies repeatable, version-controlled cloud infrastructure deployment.",
        "Cost Optimization": f"Resource right-sizing and lifecycle management minimize compute expenditure while preserving performance."
    }

    if skill in fallbacks:
        return fallbacks[skill]

    fallback = f"{skill} establishes the technical foundation and operational competency required for {target_role} workflows."

    if not GEMINI_API_KEY:
        return fallback

    prompt = (
        f"Provide exactly one concise sentence explaining why the skill '{skill}' is a critical prerequisite "
        f"for a '{target_role}'. Do not mention hiring, job guarantees, or hiring probability."
    )

    try:
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel(GEMINI_MODEL)
        response = model.generate_content(prompt)
        if response and response.text:
            line = response.text.strip().split("\n")[0]
            return sanitize_gemini_text(line)
    except Exception as e:
        logger.warning("Gemini API call failed for prerequisite explanation: %s", e)

    return fallback
