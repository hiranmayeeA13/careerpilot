import json
import os
import tempfile
import unittest
from app.database import get_candidate, init_db, save_candidate
from app.models.schemas import CandidateProfile, SkillEvidence
from app.services.simulator_service import run_what_if_simulation


class TestCareerSimulator(unittest.TestCase):
    def setUp(self):
        self.temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.db_path = self.temp_db.name
        self.temp_db.close()
        init_db(self.db_path)

        self.candidate = CandidateProfile(
            id="cand_sim_001",
            name="Diana Prince",
            target_role="DevOps Engineer",
            skills={"Linux": 40, "Networking": 50, "Docker": 30},
            skill_evidence={
                "Linux": SkillEvidence(resume_claimed=True, status="Unverified", confidence="Low"),
                "Networking": SkillEvidence(resume_claimed=True, status="Unverified", confidence="Low"),
                "Docker": SkillEvidence(resume_claimed=True, status="Unverified", confidence="Low"),
            },
            goals=["Become DevOps Engineer"],
            learning_preferences={"format": "hands-on"},
            completed_projects=[],
            interview_history=[],
            prior_roadmaps=[],
            twin_summary="Diana is working towards DevOps fundamentals."
        )
        save_candidate(self.candidate, db_path=self.db_path)

    def tearDown(self):
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_simulation_profile_byte_identical_before_and_after(self):
        """
        Acceptance (critical): test calls simulate, then re-fetches the candidate's
        real profile, and asserts it is byte-identical to before the call.
        """
        # Fetch candidate before simulation and serialize to bytes
        profile_before = get_candidate("cand_sim_001", db_path=self.db_path)
        self.assertIsNotNone(profile_before)
        bytes_before = json.dumps(profile_before.model_dump(), sort_keys=True).encode("utf-8")

        # Run what-if simulation with significant skill delta
        hypothetical = {"Linux": 85, "Docker": 80, "Kubernetes": 75}
        result = run_what_if_simulation(profile_before, hypothetical)

        # Assert simulation outputs correct delta
        self.assertGreater(result.simulated_score, result.current_score)
        self.assertGreater(result.delta, 0)
        self.assertIn("Linux", result.newly_improved_skills)
        self.assertIn("Docker", result.newly_improved_skills)

        # Re-fetch candidate from DB after simulation
        profile_after = get_candidate("cand_sim_001", db_path=self.db_path)
        self.assertIsNotNone(profile_after)
        bytes_after = json.dumps(profile_after.model_dump(), sort_keys=True).encode("utf-8")

        # Assert byte-for-byte identical
        self.assertEqual(
            bytes_before,
            bytes_after,
            "Critical failure: candidate profile was mutated by simulation call!"
        )


if __name__ == "__main__":
    unittest.main()
