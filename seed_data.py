from app.config import DB_PATH
from app.database import init_db, save_candidate
from app.models.schemas import (
    CandidateProfile,
    InterviewRecord,
    ProjectRecord,
    RoadmapRecord,
    SkillEvidence,
)
from app.services.evidence_service import evaluate_skill_evidence


def seed():
    init_db(DB_PATH)

    # 1. DevOps Candidate with foundational deficits (weak in Linux & Networking)
    devops_cand = CandidateProfile(
        id="cand_devops_001",
        name="Alex Rivera",
        target_role="DevOps Engineer",
        skills={
            "Linux": 40,
            "Networking": 35,
            "Docker": 75,
            "Kubernetes": 55,
            "CI/CD": 65,
            "Cloud/AWS": 60,
        },
        skill_evidence={
            "Linux": evaluate_skill_evidence(resume_claimed=True, resume_supported=False),
            "Networking": evaluate_skill_evidence(resume_claimed=True, resume_supported=False),
            "Docker": evaluate_skill_evidence(resume_claimed=True, resume_supported=True, portfolio_demonstrated=True),
            "Kubernetes": evaluate_skill_evidence(resume_claimed=True, resume_supported=False),
            "CI/CD": evaluate_skill_evidence(resume_claimed=True, resume_supported=True),
            "Cloud/AWS": evaluate_skill_evidence(resume_claimed=True, resume_supported=False),
        },
        goals=["Advance to DevOps Engineer role", "Master Linux kernel performance and container orchestration"],
        learning_preferences={"preferred_format": "hands-on projects", "weekly_hours": 12},
        completed_projects=[
            ProjectRecord(
                id="proj_docker_01",
                title="Microservices Dockerization Lab",
                description="Containerized sample 3-tier web app using Docker Compose",
                skills_demonstrated=["Docker"],
                completion_date="2026-02-15",
                evaluation_score=80,
            )
        ],
        interview_history=[
            InterviewRecord(
                id="int_001",
                target_role="DevOps Engineer",
                date="2026-03-01",
                performance_score=68,
                skills_evaluated=["Docker", "CI/CD"],
                feedback="Good understanding of build pipelines, needs deeper core networking and Linux internals."
            )
        ],
        prior_roadmaps=[
            RoadmapRecord(
                version=1,
                created_at="2026-01-10",
                target_role="DevOps Engineer",
                milestones=["Learn Docker Basics", "Setup GitHub Actions Pipeline"]
            )
        ],
        twin_summary="Alex Rivera is building technical readiness for DevOps, with demonstrated container skills and ongoing foundational work in Linux."
    )
    save_candidate(devops_cand, DB_PATH)

    # 2. Backend Candidate
    backend_cand = CandidateProfile(
        id="cand_backend_001",
        name="Priya Sharma",
        target_role="Backend Engineer",
        skills={
            "Data Structures & Algorithms": 80,
            "Python": 85,
            "SQL & Databases": 75,
            "API Design & REST": 80,
            "System Design": 60,
        },
        skill_evidence={
            "Data Structures & Algorithms": evaluate_skill_evidence(resume_claimed=True, resume_supported=True, interview_demonstrated=True),
            "Python": evaluate_skill_evidence(resume_claimed=True, resume_supported=True, portfolio_demonstrated=True),
            "SQL & Databases": evaluate_skill_evidence(resume_claimed=True, resume_supported=True),
            "API Design & REST": evaluate_skill_evidence(resume_claimed=True, portfolio_demonstrated=True),
            "System Design": evaluate_skill_evidence(resume_claimed=True),
        },
        goals=["Senior Backend Architect", "Scale high-throughput APIs"],
        learning_preferences={"preferred_format": "code deep-dives", "weekly_hours": 15},
        completed_projects=[
            ProjectRecord(
                id="proj_fastapi_01",
                title="High-Speed Async Order Processing API",
                description="FastAPI service with PostgreSQL connection pooling and Redis caching",
                skills_demonstrated=["Python", "API Design & REST"],
                completion_date="2026-02-28",
                evaluation_score=90,
            )
        ],
        interview_history=[
            InterviewRecord(
                id="int_002",
                target_role="Backend Engineer",
                date="2026-03-05",
                performance_score=85,
                skills_evaluated=["Data Structures & Algorithms", "Python"],
                feedback="Excellent algorithmic problem-solving and clean asynchronous Python design."
            )
        ],
        prior_roadmaps=[],
        twin_summary="Priya Sharma exhibits strong backend application engineering readiness with robust Python and API design competencies."
    )
    save_candidate(backend_cand, DB_PATH)

    print("Successfully seeded candidate profiles into database at:", DB_PATH)


if __name__ == "__main__":
    seed()
