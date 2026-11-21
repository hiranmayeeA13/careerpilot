import json
import socket
import sys
import threading
import time
import urllib.request
import uvicorn
from app.main import app
from seed_data import seed

PORT = 8008

def run_server():
    config = uvicorn.Config(app, host="127.0.0.1", port=PORT, log_level="warning")
    server = uvicorn.Server(config)
    server.run()

def http_get(path):
    url = f"http://127.0.0.1:{PORT}{path}"
    req = urllib.request.Request(url, method="GET")
    with urllib.request.urlopen(req, timeout=5) as response:
        return response.status, json.loads(response.read().decode("utf-8"))

def http_post(path, data):
    url = f"http://127.0.0.1:{PORT}{path}"
    body = json.dumps(data).encode("utf-8")
    req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=5) as response:
        return response.status, json.loads(response.read().decode("utf-8"))

def main():
    print("Seeding database...")
    seed()

    print(f"Starting live FastAPI backend on 127.0.0.1:{PORT}...")
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()

    # Wait for server to come up
    for _ in range(20):
        try:
            with socket.create_connection(("127.0.0.1", PORT), timeout=0.5):
                break
        except OSError:
            time.sleep(0.2)
    else:
        print("Error: Server failed to start in time.")
        sys.exit(1)

    print("Backend server is live! Exercising complete workflow end to end...\n")
    candidate_id = "cand_devops_001"

    # 1. Health
    st, res = http_get("/health")
    print(f"[1] GET /health -> Status: {st}")
    print(json.dumps(res, indent=2))

    # 2. Career Twin Profile
    st, res = http_get(f"/api/career-twin/{candidate_id}")
    print(f"\n[2] GET /api/career-twin/{candidate_id} -> Status: {st}")
    print(json.dumps(res, indent=2))

    # 3. Career Readiness Score
    st, res = http_get(f"/api/readiness/{candidate_id}")
    print(f"\n[3] GET /api/readiness/{candidate_id} -> Status: {st}")
    print(json.dumps(res, indent=2))

    # 4. What-If Simulator
    sim_payload = {
        "candidate_id": candidate_id,
        "hypothetical_skills": {"Linux": 85, "Networking": 80}
    }
    st, res = http_post("/api/career/simulate", sim_payload)
    print(f"\n[4] POST /api/career/simulate -> Status: {st}")
    print(json.dumps(res, indent=2))

    # 5. Career Twin Update Trigger
    twin_payload = {
        "candidate_id": candidate_id,
        "trigger_type": "learning_task_completed",
        "payload": {
            "skill_name": "Linux",
            "task_name": "Linux Core Hardening",
            "mastery_increment": 20,
            "evidence_supported": True
        }
    }
    st, res = http_post("/api/career-twin/update", twin_payload)
    print(f"\n[5] POST /api/career-twin/update -> Status: {st}")
    print(json.dumps(res, indent=2))

    # 6. Career Reality Check
    rc_payload = {
        "candidate_id": candidate_id,
        "target_role": "DevOps Engineer"
    }
    st, res = http_post("/api/career/reality-check", rc_payload)
    print(f"\n[6] POST /api/career/reality-check -> Status: {st}")
    print(json.dumps(res, indent=2))

    # 7. Smart Portfolio Project Recommendation
    port_payload = {"candidate_id": candidate_id}
    st, res = http_post("/api/portfolio/recommend", port_payload)
    print(f"\n[7] POST /api/portfolio/recommend -> Status: {st}")
    print(json.dumps(res, indent=2))

    print("\nEnd-to-End Live Workflow Exercise Completed Successfully!")

if __name__ == "__main__":
    main()
