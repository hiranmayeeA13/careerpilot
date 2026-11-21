import json
import unittest
from app.models.schemas import CandidateProfile, SkillEvidence
from app.services.reality_check_service import run_career_reality_check


class TestCareerRealityCheck(unittest.TestCase):
    def setUp(self):
        self.candidate = CandidateProfile(
            id="cand_rc_001",
            name="Grace Hopper",
            target_role="DevOps Engineer",
            skills={"Docker": 75, "CI/CD": 70},  # Has intermediate tools, but missing foundational Linux & Networking!
            skill_evidence={
                "Docker": SkillEvidence(resume_claimed=True, resume_supported=True, status="Resume-supported", confidence="Moderate"),
                "CI/CD": SkillEvidence(resume_claimed=True, resume_supported=True, status="Resume-supported", confidence="Moderate"),
            },
            goals=["Transition into DevOps"],
            learning_preferences={},
            completed_projects=[],
            interview_history=[],
            prior_roadmaps=[],
            twin_summary="Grace has container knowledge but needs core systems foundation."
        )

    def test_reality_check_identifies_missing_foundations(self):
        res = run_career_reality_check(self.candidate)
        self.assertEqual(res.target_role, "DevOps Engineer")
        self.assertEqual(res.current_level, "Beginner")
        self.assertIn("Linux", res.missing_foundations)
        self.assertIn("Networking", res.missing_foundations)

        # Check preparation sequence orders foundations first
        self.assertTrue(len(res.preparation_sequence) >= 3)
        self.assertIn("foundations", res.preparation_sequence[0].lower())
        self.assertIn("Linux", res.preparation_sequence[0])

        # Check each prerequisite has why_it_matters
        for prereq in res.major_prerequisites:
            self.assertTrue(len(prereq.why_it_matters) > 10)
            self.assertFalse(prereq.why_it_matters.isspace())

    def test_banned_phrases_grep_check(self):
        """
        Acceptance test: no output field contains hiring probability,
        guaranteed timeline, or 'will get you hired' language.
        """
        banned_phrases = [
            "will get you hired",
            "guaranteed job",
            "guaranteed timeline",
            "hiring probability",
            "chance of being hired",
            "guarantee you a job",
            "get hired in",
            "job guarantee",
            "hireability"
        ]

        res = run_career_reality_check(self.candidate)
        serialized_json = json.dumps(res.model_dump()).lower()

        for phrase in banned_phrases:
            self.assertNotIn(
                phrase.lower(),
                serialized_json,
                f"Banned phrase '{phrase}' detected in reality-check output!"
            )


if __name__ == "__main__":
    unittest.main()
