import json
import os
import sys
import threading
import time
import urllib.request
import socket

ROOT_DIR = r"C:\Users\INDIA\Downloads\careerpilot"
sys.path.insert(0, ROOT_DIR)

from app.main import app
import uvicorn
from seed_data import seed

PORT = 8010

def http_get(url):
    req = urllib.request.Request(url, method="GET")
    with urllib.request.urlopen(req, timeout=5) as resp:
        return resp.status, json.loads(resp.read().decode("utf-8"))

def http_post(url, data):
    body = json.dumps(data).encode("utf-8")
    req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=5) as resp:
        return resp.status, json.loads(resp.read().decode("utf-8"))

def wait_for_port(port, timeout=10):
    start = time.time()
    while time.time() - start < timeout:
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=0.5):
                return True
        except OSError:
            time.sleep(0.2)
    return False

def test_all():
    print("--- 1. Seeding base data ---")
    seed()

    print(f"--- 2. Starting test server on port {PORT} ---")
    def run_server():
        config = uvicorn.Config(app, host="127.0.0.1", port=PORT, log_level="error")
        server = uvicorn.Server(config)
        server.run()

    t = threading.Thread(target=run_server, daemon=True)
    t.start()
    assert wait_for_port(PORT), "Server failed to start"
    print("✓ Test server up!")

    # Req 1 & 11: Resume intake without saving vs with saving
    print("\n--- Testing Req 1 & 11: Resume Intake (Unsaved vs Saved) ---")
    resume_text = """
    Jordan Lee
    Email: jordan.lee@example.com
    Target: Full Stack Developer
    Summary: Full stack developer with 3 years building web apps using React, Node.js, TypeScript, PostgreSQL, and Docker.
    Skills: React, Node.js, TypeScript, PostgreSQL, Docker, Git, REST APIs
    Experience: Built scalable microservices with Node.js and PostgreSQL. Designed responsive UI with React and TypeScript.
    """
    # Unsaved intake
    st, unsaved = http_post(f"http://127.0.0.1:{PORT}/api/intake/resume", {
        "name": "Jordan Lee",
        "resume_text": resume_text,
        "target_role": "Full Stack Developer",
        "save_to_database": False
    })
    assert st == 200
    assert unsaved["name"] == "Jordan Lee"
    print(f"✓ Unsaved intake parsed candidate '{unsaved['name']}' with {len(unsaved['extracted_skills'])} skills, save_to_database=False")

    # Saved intake
    st, saved = http_post(f"http://127.0.0.1:{PORT}/api/intake/resume", {
        "name": "Jordan Lee",
        "resume_text": resume_text,
        "target_role": "Full Stack Developer",
        "save_to_database": True
    })
    assert st == 200
    new_cand_id = saved["candidate_id"]
    print(f"✓ Saved intake persisted candidate '{saved['name']}' with ID: {new_cand_id}")

    # Req 1: Career Readiness Score for new candidate
    print("\n--- Testing Req 1: Career Readiness Score for new candidate ---")
    st, readiness = http_get(f"http://127.0.0.1:{PORT}/api/readiness/{new_cand_id}")
    assert st == 200
    print(f"✓ Career Readiness overall_score: {readiness['overall_score']}/100, category: '{readiness['category']}'")
    assert readiness["overall_score"] > 0, "Score should not be 0 for qualified candidate"
    assert "skills" in readiness["breakdown"]

    # Req 2: What-If Simulator for new candidate
    print("\n--- Testing Req 2: What-If Simulator Uplift ---")
    st, sim = http_post(f"http://127.0.0.1:{PORT}/api/career/simulate", {
        "candidate_id": new_cand_id,
        "hypothetical_skills": {"TypeScript": 95, "Docker": 90, "React": 95}
    })
    assert st == 200
    print(f"✓ What-If Simulator: Current {sim['current_score']} -> Simulated {sim['simulated_score']} (Delta: +{sim['delta']})")
    assert sim["delta"] > 0, "Delta must be strictly positive when upgrading skills"

    # Req 3 & 12: Career Twin & About Me for new candidate
    print("\n--- Testing Req 3 & 12: Career Twin & About Me Profile ---")
    st, twin = http_get(f"http://127.0.0.1:{PORT}/api/career-twin/{new_cand_id}")
    assert st == 200
    print(f"✓ Career Twin fetched for '{twin['name']}'. Skills count: {len(twin['skills'])}, Goals: {twin['goals']}")
    assert len(twin["skills"]) >= 3, "Skills should be populated"
    assert len(twin["goals"]) > 0, "Starter goals should be populated for new candidate"

    # Req 4: Job Market and Gap Analysis
    print("\n--- Testing Req 4: Job Market & Gap Analysis ---")
    st, job_res = http_post(f"http://127.0.0.1:{PORT}/api/jobs/ingest", {
        "role": "Full Stack Developer",
        "company": "Stripe",
        "raw_text": "We are seeking a Full Stack Developer with React, TypeScript, Node.js, Docker, and SQL experience."
    })
    assert st == 200
    st, gap_res = http_get(f"http://127.0.0.1:{PORT}/api/jobs/skill-gap/{new_cand_id}?target_role=Full+Stack+Developer")
    assert st == 200
    print(f"✓ Job Market Gap: Target Role='{gap_res['target_role']}', Requirements count={len(gap_res['requirements'])}, Source='{gap_res['source']}'")
    assert len(gap_res["requirements"]) > 0

    # Req 5: Learning Plan for candidate
    print("\n--- Testing Req 5: Learning Plan Generation ---")
    st, plan_res = http_get(f"http://127.0.0.1:{PORT}/api/plan/{new_cand_id}")
    assert st == 200
    print(f"✓ Learning Plan: Total Weeks={plan_res['total_weeks']}, First Week Focus={plan_res['weeks'][0]['focus_skills']}")
    assert plan_res["total_weeks"] > 0
    assert len(plan_res["weeks"][0]["tasks"]) > 0

    # Req 6: Reality Check receiving properties & hypothetical skills
    print("\n--- Testing Req 6: Reality Check with Hypothetical Skills ---")
    st, rc = http_post(f"http://127.0.0.1:{PORT}/api/career/reality-check", {
        "candidate_id": new_cand_id,
        "target_role": "Full Stack Developer",
        "hypothetical_skills": {"React": 90, "TypeScript": 90, "Node.js": 85}
    })
    assert st == 200
    print(f"✓ Reality Check: Current Level='{rc['current_level']}', Missing Foundations={rc['missing_foundations']}")
    assert len(rc["preparation_sequence"]) > 0

    # Req 7: Portfolio Generator different suggestions
    print("\n--- Testing Req 7: Portfolio Generator Suggestions Variation ---")
    st, port0 = http_post(f"http://127.0.0.1:{PORT}/api/portfolio/recommend", {
        "candidate_id": new_cand_id,
        "variation_index": 0
    })
    st, port1 = http_post(f"http://127.0.0.1:{PORT}/api/portfolio/recommend", {
        "candidate_id": new_cand_id,
        "variation_index": 1
    })
    print(f"✓ Variant 0: '{port0['title']}'")
    print(f"✓ Variant 1: '{port1['title']}'")
    assert port0["title"] != port1["title"], "Portfolio suggestion should vary with variation_index"
    assert len(port0["milestones"]) >= 3

    # Req 8: Mock Interview questions variation and thorough answer evaluation
    print("\n--- Testing Req 8: Mock Interview Question Sets & Answer Evaluation ---")
    st, session0 = http_post(f"http://127.0.0.1:{PORT}/api/interview/start/{new_cand_id}?variant=0", {})
    st, session1 = http_post(f"http://127.0.0.1:{PORT}/api/interview/start/{new_cand_id}?variant=1", {})
    q0 = session0['questions'][0]['question']
    q1 = session1['questions'][0]['question']
    print(f"✓ Interview Set 0 Question 1: '{q0}'")
    print(f"✓ Interview Set 1 Question 1: '{q1}'")
    assert q0 != q1, "Different variants should produce different questions"

    # Submit thorough technical answer
    q = session0["questions"][0]
    st, eval_res = http_post(f"http://127.0.0.1:{PORT}/api/interview/submit", {
        "candidate_id": new_cand_id,
        "session_id": session0["session_id"],
        "answers": [
            {
                "question_id": q["question_id"],
                "answer_text": "To reduce Docker image size and build times, we implemented multi-stage builds using a minimal alpine base image. We leveraged layer caching by copying package manifests before source code, and added a .dockerignore to prune build artifacts and clean caches."
            }
        ]
    })
    assert st == 200
    scored_q = eval_res["per_question"][0]
    print(f"✓ Answer Evaluation: Score={scored_q['score']}/100, Hits={scored_q['rubric_hits']}, Misses={scored_q['rubric_misses']}")
    assert scored_q["score"] >= 65, "A detailed technical answer hitting keywords must receive a high score"
    assert len(scored_q["rubric_hits"]) > 0, "Keywords hit should be detected"
    print(f"✓ Feedback: {scored_q['feedback']}")

    # Req 9: Applications tracker test
    print("\n--- Testing Req 9: Applications Tracker & Status ---")
    st, app_log = http_post(f"http://127.0.0.1:{PORT}/api/applications/log", {
        "candidate_id": new_cand_id,
        "company": "Stripe",
        "role_title": "Full Stack Developer",
        "status": "Interviewing"
    })
    assert st == 200
    print(f"✓ Application logged for {app_log['company']} ({app_log['role_title']}) with status {app_log['status']}")

    # Req 10: Compare Candidates & Roster All includes new candidate
    print("\n--- Testing Req 10: Roster List includes newly added candidate ---")
    st, roster = http_get(f"http://127.0.0.1:{PORT}/api/career-twin/roster/all")
    assert st == 200
    roster_ids = [c["id"] for c in roster]
    print(f"✓ Roster contains {len(roster)} candidates: {roster_ids}")
    assert new_cand_id in roster_ids, "Newly added candidate must be present in roster"

    print("\n=======================================================")
    print("ALL 12 REQUIREMENTS TESTED AND PASSED SUCCESSFULLY! (100%)")
    print("=======================================================")

if __name__ == "__main__":
    test_all()
