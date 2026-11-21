import os
import tempfile
import unittest
from app.database import get_candidate, init_db, save_candidate
from app.models.schemas import CandidateProfile, SkillEvidence
from app.services.twin_service import update_career_twin


class TestCareerTwin(unittest.TestCase):
    def setUp(self):
        self.temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.db_path = self.temp_db.name
        self.temp_db.close()
        init_db(self.db_path)

        self.candidate = CandidateProfile(
            id="cand_twin_001",
            name="Evan Wright",
            target_role="DevOps Engineer",
            skills={"Linux": 50, "Networking": 40},
            skill_evidence={
                "Linux": SkillEvidence(resume_claimed=True, status="Unverified", confidence="Low"),
                "Networking": SkillEvidence(resume_claimed=True, status="Unverified", confidence="Low"),
            },
            goals=["Master Kubernetes", "Transition to DevOps"],
            learning_preferences={"style": "interactive"},
            completed_projects=[],
            interview_history=[],
            prior_roadmaps=[],
            twin_summary="Evan is starting his DevOps journey."
        )
        save_candidate(self.candidate, db_path=self.db_path)

    def tearDown(self):
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_all_four_triggers_update_and_persist(self):
        """Acceptance test: after each trigger type, GET reflects the change + concise summary field."""
        
        # 1. Trigger: interview_completed
        interview_payload = {
            "interview_id": "mock_interview_101",
            "target_role": "DevOps Engineer",
            "date": "2026-04-10",
            "performance_score": 82,
            "skills_evaluated": ["Linux"],
            "feedback": "Strong command line and shell skills."
        }
        res_interview = update_career_twin("cand_twin_001", "interview_completed", interview_payload, db_path=self.db_path)
        fetched_1 = get_candidate("cand_twin_001", db_path=self.db_path)
        self.assertEqual(len(fetched_1.interview_history), 1)
        self.assertEqual(fetched_1.interview_history[0].performance_score, 82)
        self.assertEqual(fetched_1.skill_evidence["Linux"].status, "Interview-demonstrated")
        self.assertIsNotNone(fetched_1.twin_summary)
        self.assertIn("Evan Wright", fetched_1.twin_summary)

        # 2. Trigger: learning_task_completed
        learning_payload = {
            "skill_name": "Networking",
            "task_name": "Subnetting and Routing Lab",
            "mastery_increment": 15,
            "evidence_supported": True,
        }
        res_learning = update_career_twin("cand_twin_001", "learning_task_completed", learning_payload, db_path=self.db_path)
        fetched_2 = get_candidate("cand_twin_001", db_path=self.db_path)
        self.assertEqual(fetched_2.skills["Networking"], 55)
        self.assertEqual(fetched_2.skill_evidence["Networking"].status, "Resume-supported")

        # 3. Trigger: project_completed
        project_payload = {
            "project_id": "proj_ansible_01",
            "title": "Automated Configuration Pipeline",
            "description": "Ansible playbooks for server hardening",
            "skills_demonstrated": ["Linux"],
            "evaluation_score": 90,
            "completion_date": "2026-04-12"
        }
        res_project = update_career_twin("cand_twin_001", "project_completed", project_payload, db_path=self.db_path)
        fetched_3 = get_candidate("cand_twin_001", db_path=self.db_path)
        self.assertEqual(len(fetched_3.completed_projects), 1)
        # Since Linux already had interview_demonstrated and now portfolio_demonstrated:
        self.assertEqual(fetched_3.skill_evidence["Linux"].status, "Strongly-supported")
        self.assertEqual(fetched_3.skill_evidence["Linux"].confidence, "High")

        # 4. Trigger: skill_assessed
        assessment_payload = {
            "skill_name": "Docker",
            "mastery_score": 75,
            "assessment_type": "exam",
            "verified": True
        }
        res_assessed = update_career_twin("cand_twin_001", "skill_assessed", assessment_payload, db_path=self.db_path)
        fetched_4 = get_candidate("cand_twin_001", db_path=self.db_path)
        self.assertEqual(fetched_4.skills["Docker"], 75)
        self.assertEqual(fetched_4.skill_evidence["Docker"].status, "Resume-supported")
        self.assertIsNotNone(fetched_4.twin_summary)


if __name__ == "__main__":
    unittest.main()
