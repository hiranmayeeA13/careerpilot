import unittest
from app.models.schemas import CandidateProfile, SkillEvidence
from app.services.portfolio_service import generate_portfolio_project_recommendation


class TestPortfolioProjectGenerator(unittest.TestCase):
    def setUp(self):
        # Exact fixture profile weak in Linux + Networking for DevOps Engineer target role
        self.fixture_profile = CandidateProfile(
            id="cand_fixture_weak_linux_net",
            name="Jordan Lee",
            target_role="DevOps Engineer",
            skills={
                "Linux": 30,         # Weak
                "Networking": 25,    # Weak
                "Docker": 75,        # Stronger
                "CI/CD": 70          # Stronger
            },
            skill_evidence={
                "Linux": SkillEvidence(resume_claimed=True, resume_supported=False, status="Unverified", confidence="Low"),
                "Networking": SkillEvidence(resume_claimed=True, resume_supported=False, status="Unverified", confidence="Low"),
                "Docker": SkillEvidence(resume_claimed=True, resume_supported=True, status="Resume-supported", confidence="Moderate"),
                "CI/CD": SkillEvidence(resume_claimed=True, resume_supported=True, status="Resume-supported", confidence="Moderate"),
            },
            goals=["Transition into DevOps"],
            learning_preferences={},
            completed_projects=[],
            interview_history=[],
            prior_roadmaps=[],
            twin_summary="Jordan is building DevOps skills."
        )

    def test_linux_networking_fixture_never_recommends_generic_website(self):
        """
        Acceptance test: given a profile weak in Linux+networking,
        output must not be a generic 'build a portfolio website'.
        """
        project = generate_portfolio_project_recommendation(self.fixture_profile)

        # 1. Assert title and problem statement do NOT mention generic portfolio website
        generic_terms = [
            "portfolio website",
            "personal website",
            "blog website",
            "resume website",
            "landing page"
        ]
        for term in generic_terms:
            self.assertNotIn(term, project.title.lower())
            self.assertNotIn(term, project.problem_statement.lower())

        # 2. Assert skills demonstrated explicitly target Linux and Networking
        self.assertIn("Linux", project.skills_demonstrated)
        self.assertIn("Networking", project.skills_demonstrated)

        # 3. Assert required tools include Linux and Networking utilities
        tool_str = " ".join(project.required_tools).lower()
        self.assertTrue("linux" in tool_str or "nftables" in tool_str or "tcpdump" in tool_str or "bash" in tool_str)

        # 4. Assert impact clarifies evidence transition
        self.assertIn("Project-demonstrated", project.evidence_profile_impact)
        self.assertIn("Linux", project.evidence_profile_impact)

        # 5. Assert milestones and rubric are populated
        self.assertTrue(len(project.milestones) >= 2)
        self.assertTrue(len(project.evaluation_rubric) >= 2)
        self.assertTrue(len(project.expected_deliverables) >= 2)


if __name__ == "__main__":
    unittest.main()
