import unittest
from fastapi import HTTPException
from app.models.schemas import (
    CareerTwinUpdateRequest,
    PortfolioRecommendRequest,
    RealityCheckRequest,
    SimulationRequest,
)
from app.routers.career import career_reality_check, simulate_career_impact
from app.routers.portfolio import recommend_portfolio_project
from app.routers.readiness import get_candidate_readiness
from app.routers.twin import get_career_twin, update_career_twin_trigger
from seed_data import seed


class TestCareerPilotE2EWorkflow(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        seed()

    def test_complete_end_to_end_workflow(self):
        """
        Exercises the complete CareerPilot workflow:
        profile -> readiness -> simulate -> twin update -> reality-check -> portfolio recommend
        """
        candidate_id = "cand_devops_001"

        # 1. Profile retrieval (Career Twin)
        twin = get_career_twin(candidate_id)
        self.assertEqual(twin.name, "Alex Rivera")
        self.assertEqual(twin.target_role, "DevOps Engineer")
        self.assertIsNotNone(twin.twin_summary)
        self.assertIn("Alex Rivera", twin.twin_summary)

        # 2. Career Readiness Score
        readiness_1 = get_candidate_readiness(candidate_id)
        self.assertGreater(readiness_1.overall_score, 0)
        self.assertIn(readiness_1.category, ["Beginner", "Developing", "Job-Ready"])
        self.assertIsNotNone(readiness_1.breakdown)
        self.assertTrue(len(readiness_1.top_positive_factors) <= 3)
        self.assertTrue(len(readiness_1.top_negative_factors) <= 3)
        self.assertTrue(len(readiness_1.recommended_next_action) > 10)

        # Assert determinism: repeated call returns identical score
        readiness_2 = get_candidate_readiness(candidate_id)
        self.assertEqual(readiness_1.overall_score, readiness_2.overall_score)
        self.assertEqual(readiness_1.category, readiness_2.category)
        self.assertEqual(readiness_1.breakdown.model_dump(), readiness_2.breakdown.model_dump())

        # 3. What-If Career Simulator
        sim_request = SimulationRequest(
            candidate_id=candidate_id,
            hypothetical_skills={"Linux": 85, "Networking": 80}
        )
        sim_res = simulate_career_impact(sim_request)
        self.assertGreater(sim_res.simulated_score, sim_res.current_score)
        self.assertEqual(sim_res.delta, sim_res.simulated_score - sim_res.current_score)
        self.assertIn("Linux", sim_res.newly_improved_skills)
        self.assertIn("Networking", sim_res.newly_improved_skills)

        # Assert profile was NOT mutated by simulate call
        twin_after_sim = get_career_twin(candidate_id)
        self.assertEqual(twin_after_sim.skills["Linux"], 40)

        # 4. Career Twin Trigger Update (learning_task_completed)
        update_request = CareerTwinUpdateRequest(
            candidate_id=candidate_id,
            trigger_type="learning_task_completed",
            payload={
                "skill_name": "Linux",
                "task_name": "Linux Kernel & Sysfs Deep Dive",
                "mastery_increment": 25,
                "evidence_supported": True
            }
        )
        updated_twin = update_career_twin_trigger(update_request)
        self.assertEqual(updated_twin.skills["Linux"], 65)
        self.assertEqual(updated_twin.skill_evidence["Linux"].status, "Resume-supported")
        self.assertIsNotNone(updated_twin.twin_summary)

        # 5. Career Reality Check
        rc_request = RealityCheckRequest(
            candidate_id=candidate_id,
            target_role="DevOps Engineer"
        )
        rc_res = career_reality_check(rc_request)
        self.assertEqual(rc_res.target_role, "DevOps Engineer")
        self.assertTrue(len(rc_res.major_prerequisites) > 0)
        self.assertTrue(len(rc_res.preparation_sequence) >= 3)
        self.assertIsNotNone(rc_res.next_milestone)
        for prereq in rc_res.major_prerequisites:
            self.assertTrue(len(prereq.why_it_matters) > 5)

        # 6. Smart Portfolio Project Generator
        port_request = PortfolioRecommendRequest(candidate_id=candidate_id)
        port_res = recommend_portfolio_project(port_request)
        self.assertTrue(len(port_res.title) > 5)
        self.assertTrue(len(port_res.problem_statement) > 20)
        self.assertTrue(len(port_res.milestones) >= 2)
        self.assertTrue(len(port_res.evaluation_rubric) >= 2)
        self.assertIn("Project-demonstrated", port_res.evidence_profile_impact)
        # Verify it targeted the candidate's weak skills and is NOT a generic website
        self.assertNotIn("portfolio website", port_res.title.lower())

        # 7. Missing Candidate Graceful Handling (404)
        with self.assertRaises(HTTPException) as ctx:
            get_candidate_readiness("non_existent_candidate_xyz")
        self.assertEqual(ctx.exception.status_code, 404)


if __name__ == "__main__":
    unittest.main()
