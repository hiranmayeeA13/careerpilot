import unittest
from app.services.evidence_service import evaluate_skill_evidence


class TestSkillEvidence(unittest.TestCase):
    def test_resume_claimed_only_never_verified_or_strongly_supported(self):
        """Acceptance test: resume_claimed=True with nothing else must NEVER return verified or strongly-supported."""
        evidence = evaluate_skill_evidence(
            resume_claimed=True,
            resume_supported=False,
            interview_demonstrated=False,
            portfolio_demonstrated=False
        )
        self.assertEqual(evidence.status, "Unverified")
        self.assertEqual(evidence.confidence, "Low")
        self.assertNotEqual(evidence.status.lower(), "verified")
        self.assertNotEqual(evidence.status, "Strongly-supported")

    def test_no_claims_unverified(self):
        evidence = evaluate_skill_evidence(False, False, False, False)
        self.assertEqual(evidence.status, "Unverified")
        self.assertEqual(evidence.confidence, "Low")

    def test_resume_supported_status(self):
        evidence = evaluate_skill_evidence(
            resume_claimed=True,
            resume_supported=True,
            interview_demonstrated=False,
            portfolio_demonstrated=False
        )
        self.assertEqual(evidence.status, "Resume-supported")
        self.assertEqual(evidence.confidence, "Moderate")

    def test_interview_demonstrated_status(self):
        evidence = evaluate_skill_evidence(
            resume_claimed=True,
            resume_supported=False,
            interview_demonstrated=True,
            portfolio_demonstrated=False
        )
        self.assertEqual(evidence.status, "Interview-demonstrated")
        self.assertEqual(evidence.confidence, "Moderate")

    def test_project_demonstrated_status(self):
        evidence = evaluate_skill_evidence(
            resume_claimed=True,
            resume_supported=False,
            interview_demonstrated=False,
            portfolio_demonstrated=True
        )
        self.assertEqual(evidence.status, "Project-demonstrated")
        self.assertEqual(evidence.confidence, "Moderate")

    def test_strongly_supported_status(self):
        evidence = evaluate_skill_evidence(
            resume_claimed=True,
            resume_supported=True,
            interview_demonstrated=True,
            portfolio_demonstrated=True
        )
        self.assertEqual(evidence.status, "Strongly-supported")
        self.assertEqual(evidence.confidence, "High")


if __name__ == "__main__":
    unittest.main()
