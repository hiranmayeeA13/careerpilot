import json
import os
import socket
import subprocess
import sys
import threading
import time
import urllib.request

BACKEND_DIR = r"C:\Users\INDIA\.gemini\antigravity\scratch\careerpilot"
FRONTEND_DIR = r"C:\Users\INDIA\Downloads\careerpilot\frontend"
BACKEND_PORT = 8008
FRONTEND_PORT = 5173

sys.path.insert(0, BACKEND_DIR)

def wait_for_port(port, timeout=15):
    start = time.time()
    while time.time() - start < timeout:
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=0.5):
                return True
        except OSError:
            time.sleep(0.3)
    return False

def http_get(url):
    req = urllib.request.Request(url, method="GET")
    with urllib.request.urlopen(req, timeout=5) as resp:
        return resp.status, resp.read().decode("utf-8")

def http_post(url, data):
    body = json.dumps(data).encode("utf-8")
    req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=5) as resp:
        return resp.status, json.loads(resp.read().decode("utf-8"))

def main():
    print("==================================================")
    print("CAREERPILOT AI — FULL-STACK VERIFICATION TEST")
    print("==================================================")

    # 1. Start Backend in thread
    print(f"\n[1/4] Starting Backend on http://127.0.0.1:{BACKEND_PORT}...")
    from app.main import app
    import uvicorn
    from seed_data import seed
    seed()

    def run_backend():
        config = uvicorn.Config(app, host="127.0.0.1", port=BACKEND_PORT, log_level="warning")
        server = uvicorn.Server(config)
        server.run()

    backend_thread = threading.Thread(target=run_backend, daemon=True)
    backend_thread.start()

    if not wait_for_port(BACKEND_PORT):
        print("ERROR: Backend server failed to start.")
        sys.exit(1)
    print("✓ Backend is up and listening on port", BACKEND_PORT)

    # 2. Start Frontend Dev Server via Bun
    print(f"\n[2/4] Starting Frontend Dev Server on http://127.0.0.1:{FRONTEND_PORT}...")
    frontend_proc = subprocess.Popen(
        ["bun", "run", "dev", "--port", str(FRONTEND_PORT), "--host", "127.0.0.1"],
        cwd=FRONTEND_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    try:
        if not wait_for_port(FRONTEND_PORT, timeout=20):
            print("ERROR: Frontend dev server failed to start.")
            sys.exit(1)
        print("✓ Frontend dev server is up and listening on port", FRONTEND_PORT)

        # 3. Hit Frontend UI HTML
        print("\n[3/4] Testing Frontend HTTP response...")
        status, html = http_get(f"http://127.0.0.1:{FRONTEND_PORT}")
        assert status == 200, f"Expected 200, got {status}"
        assert "CareerPilot AI" in html or "root" in html, "HTML missing expected root element"
        print("✓ Frontend serves index.html with Vite root container successfully (Status 200)")

        # 4. Exercise Full User Flow Endpoints in UI Trigger Sequence
        print("\n[4/4] Exercising UI data-fetch and action flow...")
        candidate_id = "cand_devops_001"

        # A. Health Check
        st, body = http_get(f"http://127.0.0.1:{BACKEND_PORT}/health")
        h_data = json.loads(body)
        print(f"  A. Health Check: {h_data['status']} ({h_data['service']})")
        assert h_data["status"] == "healthy"

        # B. Career Twin Profile
        st, body = http_get(f"http://127.0.0.1:{BACKEND_PORT}/api/career-twin/{candidate_id}")
        profile = json.loads(body)
        print(f"  B. Career Twin: Name='{profile['name']}', Role='{profile['target_role']}'")
        assert profile["name"] == "Alex Rivera"
        assert len(profile["skills"]) >= 5
        assert "Linux" in profile["skill_evidence"]

        # C. Readiness Score
        st, body = http_get(f"http://127.0.0.1:{BACKEND_PORT}/api/readiness/{candidate_id}")
        readiness = json.loads(body)
        print(f"  C. Readiness Score: {readiness['overall_score']}/100, Category='{readiness['category']}'")
        assert readiness["overall_score"] >= 0
        assert "skills" in readiness["breakdown"]

        # D. Reality Check
        st, rc = http_post(f"http://127.0.0.1:{BACKEND_PORT}/api/career/reality-check", {
            "candidate_id": candidate_id,
            "target_role": "DevOps Engineer"
        })
        print(f"  D. Reality Check: Current Level='{rc['current_level']}', Missing Foundations={rc['missing_foundations']}")
        assert len(rc["major_prerequisites"]) > 0
        assert len(rc["preparation_sequence"]) > 0

        # E. Portfolio Recommendation
        st, port = http_post(f"http://127.0.0.1:{BACKEND_PORT}/api/portfolio/recommend", {
            "candidate_id": candidate_id
        })
        print(f"  E. Portfolio Recommend: Title='{port['title']}', Difficulty='{port['difficulty']}'")
        assert "Linux" in port["skills_demonstrated"]
        assert len(port["milestones"]) >= 2

        # F. What-If Simulator Action
        st, sim = http_post(f"http://127.0.0.1:{BACKEND_PORT}/api/career/simulate", {
            "candidate_id": candidate_id,
            "hypothetical_skills": {"Linux": 85, "Networking": 80}
        })
        print(f"  F. Simulator Delta: Current={sim['current_score']} -> Simulated={sim['simulated_score']} (Delta: +{sim['delta']})")
        assert sim["delta"] > 0
        assert "Linux" in sim["newly_improved_skills"]

        print("\n==================================================")
        print("ALL VERIFICATIONS PASSED: 100% SUCCESS")
        print("==================================================")

    finally:
        print("\nShutting down frontend dev server process...")
        frontend_proc.terminate()
        try:
            frontend_proc.wait(timeout=3)
        except subprocess.TimeoutExpired:
            frontend_proc.kill()
        print("Frontend process terminated cleanly.")

if __name__ == "__main__":
    main()
