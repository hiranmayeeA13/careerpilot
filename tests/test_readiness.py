import unittest
from app.models.schemas import (
    CandidateProfile,
    InterviewRecord,
    ProjectRecord,
    SkillEvidence,
)
from app.services.readiness_service import calculate_readiness_score


class TestReadinessScore(unittest.TestCase):
    def setUp(self):
        self.candidate = CandidateProfile(
            id="cand_test_001",
            name="Alice Smith",
            target_role="DevOps Engineer",
            skills={"Linux": 85, "Networking": 75, "Docker": 80, "Kubernetes": 60},
            skill_evidence={
                "Linux": SkillEvidence(
                    resume_claimed=True,
                    resume_supported=True,
                    interview_demonstrated=True,
                    portfolio_demonstrated=True,
                    confidence="High",
                    status="Strongly-supported"
                ),
                "Networking": SkillEvidence(
                    resume_claimed=True,
                    resume_supported=True,
                    interview_demonstrated=True,
                    portfolio_demonstrated=False,
                    confidence="Moderate",
                    status="Interview-demonstrated"
                ),
                "Docker": SkillEvidence(
                    resume_claimed=True,
                    resume_supported=False,
                    interview_demonstrated=False,
                    portfolio_demonstrated=True,
                    confidence="Moderate",
                    status="Project-demonstrated"
                )
            },
            completed_projects=[
                ProjectRecord(
                    id="proj_1",
                    title="Containerized Microservices on AWS",
                    skills_demonstrated=["Docker", "Linux"],
                    evaluation_score=85
                )
            ],
            interview_history=[
                InterviewRecord(
                    id="int_1",
                    target_role="DevOps Engineer",
                    date="2026-03-01",
                    performance_score=78,
                    skills_evaluated=["Linux", "Networking"]
                )
            ]
        )

    def test_determinism_identical_score_on_consecutive_calls(self):
        """Acceptance test: calling calculation twice with unchanged data returns identical score."""
        res1 = calculate_readiness_score(self.candidate)
        res2 = calculate_readiness_score(self.candidate)

        self.assertEqual(res1.overall_score, res2.overall_score)
        self.assertEqual(res1.category, res2.category)
        self.assertEqual(res1.breakdown.model_dump(), res2.breakdown.model_dump())
        self.assertEqual(res1.top_positive_factors, res2.top_positive_factors)
        self.assertEqual(res1.top_negative_factors, res2.top_negative_factors)
        self.assertEqual(res1.recommended_next_action, res2.recommended_next_action)

    def test_beginner_candidate(self):
        beginner = CandidateProfile(
            id="cand_beginner",
            name="Bob Novice",
            target_role="DevOps Engineer",
            skills={"Linux": 20},
            skill_evidence={},
            completed_projects=[],
            interview_history=[]
        )
        res = calculate_readiness_score(beginner)
        self.assertLess(res.overall_score, 50)
        self.assertEqual(res.category, "Beginner")
        self.assertEqual(res.breakdown.interview, 0.0)
        self.assertEqual(res.breakdown.portfolio, 0.0)

    def test_job_ready_candidate(self):
        job_ready = CandidateProfile(
            id="cand_ready",
            name="Charlie Pro",
            target_role="DevOps Engineer",
            skills={
                "Linux": 95,
                "Networking": 90,
                "Docker": 90,
                "Kubernetes": 85,
                "CI/CD": 85,
                "Cloud/AWS": 85,
            },
            skill_evidence={
                skill: SkillEvidence(
                    resume_claimed=True,
                    resume_supported=True,
                    interview_demonstrated=True,
                    portfolio_demonstrated=True,
                    confidence="High",
                    status="Strongly-supported"
                )
                for skill in ["Linux", "Networking", "Docker", "Kubernetes", "CI/CD", "Cloud/AWS"]
            },
            completed_projects=[
                ProjectRecord(id="p1", title="Cluster Setup", skills_demonstrated=["Kubernetes"], evaluation_score=90),
                ProjectRecord(id="p2", title="CI/CD Pipeline", skills_demonstrated=["CI/CD"], evaluation_score=92),
            ],
            interview_history=[
                InterviewRecord(id="i1", target_role="DevOps Engineer", date="2026-03-01", performance_score=90)
            ]
        )
        res = calculate_readiness_score(job_ready)
        self.assertGreaterEqual(res.overall_score, 75)
        self.assertEqual(res.category, "Job-Ready")


if __name__ == "__main__":
    unittest.main()
