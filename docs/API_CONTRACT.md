# CAREERPILOT AI — API CONTRACT

This document serves as the formal frontend-backend API integration contract for CareerPilot AI.
Every endpoint, schema, parameter, error format, and data type listed below was verified directly against the FastAPI backend codebase (`app/main.py`, `app/models/schemas.py`, `app/routers/`, `app/database.py`).

---

## 1. Global Specifications

- **Default Base URL**: `http://127.0.0.1:8008` (Configurable via `VITE_API_BASE_URL`)
- **Authentication**: None required.
- **CORS Policy**: Configured in FastAPI middleware with `allow_origins=["*"]`, `allow_credentials=True`, `allow_methods=["*"]`, `allow_headers=["*"]`.
- **Standard Error Response Format**:
  ```json
  {
    "detail": "Descriptive error message",
    "error_code": "NOT_FOUND | BAD_REQUEST | INTERNAL_ERROR"
  }
  ```
- **Seeded Candidates in Database**:
  - `cand_devops_001`: Alex Rivera (Target Role: `DevOps Engineer`)
  - `cand_backend_001`: Priya Sharma (Target Role: `Backend Engineer`)

---

## 2. Endpoints Specification

### 2.1 Backend Health Check
- **Path**: `GET /health`
- **Status**: **CONFIRMED**
- **Description**: Verifies backend server availability and health status.
- **Request Parameters / Body**: None.
- **Response (200 OK)**:
  ```json
  {
    "status": "healthy",
    "service": "CareerPilot AI Backend"
  }
  ```
- **Error Response**: 500 `{"detail": "string", "error_code": "INTERNAL_ERROR"}`

---

### 2.2 Career Readiness Score
- **Path**: `GET /api/readiness/{candidate_id}`
- **Status**: **CONFIRMED**
- **Description**: Computes deterministic readiness score (0-100), categorization, 4 pillar sub-scores, top positive & negative factors, and recommended next action.
- **Path Parameters**:
  - `candidate_id` (string, required): Unique identifier for candidate (e.g. `cand_devops_001`).
- **Request Body**: None.
- **Response (200 OK)**:
  ```json
  {
    "overall_score": 49,
    "category": "Beginner",
    "breakdown": {
      "skills": 52.75,
      "interview": 68.0,
      "portfolio": 40.0,
      "evidence": 18.5
    },
    "top_positive_factors": [
      "Strong mastery in Docker (75/100)",
      "Project-demonstrated verification for Docker",
      "Strong mastery in CI/CD (65/100)"
    ],
    "top_negative_factors": [
      "Low foundational mastery in Linux (40/100)",
      "Unverified evidence status for critical skill Linux",
      "Low foundational mastery in Networking (35/100)"
    ],
    "recommended_next_action": "Build foundational proficiency in Linux to meet the baseline requirement for DevOps Engineer."
  }
  ```
- **Field Constraints & Types**:
  - `overall_score`: integer [0, 100]
  - `category`: `"Beginner"` | `"Developing"` | `"Job-Ready"`
  - `breakdown.skills`: float [0.0, 100.0]
  - `breakdown.interview`: float [0.0, 100.0]
  - `breakdown.portfolio`: float [0.0, 100.0]
  - `breakdown.evidence`: float [0.0, 100.0]
  - `top_positive_factors`: array of strings (max 3 items)
  - `top_negative_factors`: array of strings (max 3 items)
  - `recommended_next_action`: string
- **Error Response (404 Not Found)**:
  ```json
  {
    "detail": "Candidate with ID 'xxx' not found",
    "error_code": "NOT_FOUND"
  }
  ```

---

### 2.3 What-If Career Simulator
- **Path**: `POST /api/career/simulate`
- **Status**: **CONFIRMED** (with critical naming correction)
- **Description**: Evaluates readiness impact of hypothetical skill improvements in-memory on deep copies. Underlying candidate record in SQLite is never modified.
- **Request Headers**: `Content-Type: application/json`
- **Request Body**:
  ```json
  {
    "candidate_id": "cand_devops_001",
    "hypothetical_skills": {
      "Linux": 85,
      "Networking": 80
    }
  }
  ```
  *(CRITICAL: Field is named `hypothetical_skills`, not `hypothetical_skill_mastery_delta`. Values are absolute target mastery [0, 100], not relative delta).*
- **Response (200 OK)**:
  ```json
  {
    "current_score": 49,
    "simulated_score": 57,
    "delta": 8,
    "newly_improved_skills": [
      "Linux",
      "Networking"
    ],
    "remaining_weaknesses": [
      "Kubernetes",
      "Cloud/AWS"
    ],
    "recommended_next_skill": "Kubernetes"
  }
  ```
- **Field Constraints & Types**:
  - `current_score`: integer [0, 100]
  - `simulated_score`: integer [0, 100]
  - `delta`: integer (can be positive, zero, or negative)
  - `newly_improved_skills`: array of strings
  - `remaining_weaknesses`: array of strings
  - `recommended_next_skill`: string
- **Error Response (404 Not Found)**:
  ```json
  {
    "detail": "Candidate with ID 'xxx' not found",
    "error_code": "NOT_FOUND"
  }
  ```

---

### 2.4 Persistent Career Twin Profile
- **Path**: `GET /api/career-twin/{candidate_id}`
- **Status**: **CONFIRMED**
- **Description**: Returns candidate twin profile, including target career, skills dictionary, full skill evidence status & confidence, goals, learning preferences, completed projects, interview history, prior roadmaps, and twin summary.
- **Path Parameters**:
  - `candidate_id` (string, required): e.g. `cand_devops_001`
- **Request Body**: None.
- **Response (200 OK)**:
  ```json
  {
    "id": "cand_devops_001",
    "name": "Alex Rivera",
    "target_role": "DevOps Engineer",
    "skills": {
      "Linux": 40,
      "Networking": 35,
      "Docker": 75,
      "Kubernetes": 55,
      "CI/CD": 65,
      "Cloud/AWS": 60
    },
    "skill_evidence": {
      "Linux": {
        "resume_claimed": true,
        "resume_supported": false,
        "interview_demonstrated": false,
        "portfolio_demonstrated": false,
        "confidence": "Low",
        "status": "Unverified"
      },
      "Docker": {
        "resume_claimed": true,
        "resume_supported": true,
        "interview_demonstrated": false,
        "portfolio_demonstrated": true,
        "confidence": "Moderate",
        "status": "Project-demonstrated"
      }
    },
    "goals": [
      "Advance to DevOps Engineer role",
      "Master Linux kernel performance and container orchestration"
    ],
    "learning_preferences": {
      "preferred_format": "hands-on projects",
      "weekly_hours": 12
    },
    "completed_projects": [
      {
        "id": "proj_docker_01",
        "title": "Microservices Dockerization Lab",
        "description": "Containerized sample 3-tier web app using Docker Compose",
        "skills_demonstrated": ["Docker"],
        "completion_date": "2026-02-15",
        "evaluation_score": 80
      }
    ],
    "interview_history": [
      {
        "id": "int_001",
        "target_role": "DevOps Engineer",
        "date": "2026-03-01",
        "performance_score": 68,
        "skills_evaluated": ["Docker", "CI/CD"],
        "feedback": "Good understanding of build pipelines, needs deeper core networking and Linux internals."
      }
    ],
    "prior_roadmaps": [
      {
        "version": 1,
        "created_at": "2026-01-10",
        "target_role": "DevOps Engineer",
        "milestones": [
          "Learn Docker Basics",
          "Setup GitHub Actions Pipeline"
        ]
      }
    ],
    "twin_summary": "Alex Rivera is building technical readiness for DevOps, with demonstrated container skills and ongoing foundational work in Linux.",
    "updated_at": "2026-11-21 14:14:00"
  }
  ```
- **Field Constraints & Types**:
  - `skills`: `Record<string, number>` (0-100)
  - `skill_evidence`: `Record<string, SkillEvidence>`
    - `resume_claimed`: boolean
    - `resume_supported`: boolean
    - `interview_demonstrated`: boolean
    - `portfolio_demonstrated`: boolean
    - `confidence`: `"Low"` | `"Moderate"` | `"High"`
    - `status`: `"Unverified"` | `"Resume-supported"` | `"Interview-demonstrated"` | `"Project-demonstrated"` | `"Strongly-supported"`
- **Error Response (404 Not Found)**:
  ```json
  {
    "detail": "Candidate with ID 'xxx' not found",
    "error_code": "NOT_FOUND"
  }
  ```

---

### 2.5 Career Twin Lifecycle Update
- **Path**: `POST /api/career-twin/update`
- **Status**: **CONFIRMED**
- **Description**: Updates candidate career twin on lifecycle events (`interview_completed`, `learning_task_completed`, `project_completed`, `skill_assessed`).
- **Request Body**:
  ```json
  {
    "candidate_id": "cand_devops_001",
    "trigger_type": "learning_task_completed",
    "payload": {
      "skill_name": "Linux",
      "task_name": "Linux Core Hardening",
      "mastery_increment": 20,
      "evidence_supported": true
    }
  }
  ```
- **Response (200 OK)**: Full updated `CandidateProfile`.

---

### 2.6 Career Reality Check
- **Path**: `POST /api/career/reality-check`
- **Status**: **CONFIRMED**
- **Description**: Evaluates candidate skills against prerequisites for a target role. Identifies missing foundations and builds an ordered preparation sequence. Prohibits hiring probability or guaranteed job promises.
- **Request Headers**: `Content-Type: application/json`
- **Request Body**:
  ```json
  {
    "candidate_id": "cand_devops_001",
    "target_role": "DevOps Engineer"
  }
  ```
  *(Note: `target_role` is optional; if omitted, backend defaults to candidate's stored `target_role`).*
- **Response (200 OK)**:
  ```json
  {
    "target_role": "DevOps Engineer",
    "current_level": "Beginner",
    "major_prerequisites": [
      {
        "skill": "Linux",
        "importance_weight": 0.25,
        "required_mastery": 75,
        "current_mastery": 40,
        "evidence_status": "Unverified",
        "is_met": false,
        "why_it_matters": "Linux provides the essential operating system runtime and command-line automation baseline for DevOps Engineer."
      },
      {
        "skill": "Networking",
        "importance_weight": 0.2,
        "required_mastery": 70,
        "current_mastery": 35,
        "evidence_status": "Unverified",
        "is_met": false,
        "why_it_matters": "Networking fundamentals govern secure system communication and reliable distributed architecture."
      },
      {
        "skill": "Docker",
        "importance_weight": 0.2,
        "required_mastery": 70,
        "current_mastery": 75,
        "evidence_status": "Project-demonstrated",
        "is_met": true,
        "why_it_matters": "Containerization underpins reproducible deployments and microservice isolation."
      }
    ],
    "missing_foundations": [
      "Linux",
      "Networking"
    ],
    "preparation_sequence": [
      "Step 1: Master core foundations — Linux, Networking with verified hands-on labs.",
      "Step 2: Develop intermediate tooling & workflows — Kubernetes.",
      "Step 3: Advanced systems & scalability — Cloud/AWS."
    ],
    "next_milestone": "Attain verified proficiency in foundational Linux."
  }
  ```
- **Error Response (404 Not Found)**:
  ```json
  {
    "detail": "Candidate with ID 'xxx' not found",
    "error_code": "NOT_FOUND"
  }
  ```

---

### 2.7 Smart Portfolio Project Generator
- **Path**: `POST /api/portfolio/recommend`
- **Status**: **CONFIRMED**
- **Description**: Recommends a targeted, hands-on portfolio project tailored specifically to candidate's verified-missing skills.
- **Request Headers**: `Content-Type: application/json`
- **Request Body**:
  ```json
  {
    "candidate_id": "cand_devops_001"
  }
  ```
- **Response (200 OK)**:
  ```json
  {
    "title": "Hardened Linux Gateway & Automated Network Packet Inspector",
    "problem_statement": "Modern infrastructure environments require automated edge gateways capable of filtering, routing, and inspecting high-throughput network packets while maintaining strict Linux kernel security baselines and systemd daemon management.",
    "why_recommended": "Your Career Twin profile identifies Networking, Linux as primary verification deficits for DevOps Engineer. Delivering this project produces tangible technical evidence addressing these specific gaps.",
    "skills_demonstrated": [
      "Linux",
      "Networking",
      "Docker"
    ],
    "difficulty": "Intermediate-Advanced",
    "required_tools": [
      "Linux (Ubuntu/Debian)",
      "Bash",
      "nftables/iptables",
      "Wireshark/tcpdump",
      "systemd",
      "Python"
    ],
    "milestones": [
      {
        "step": 1,
        "name": "Linux Kernel & Network Namespace Configuration",
        "deliverable": "Configured isolated Linux network namespaces, virtual veth pairs, and routing tables."
      },
      {
        "step": 2,
        "name": "Firewall Rule Engine & Traffic Filtering",
        "deliverable": "nftables script enforcing stateful packet inspection, NAT masquerading, and port knocking."
      },
      {
        "step": 3,
        "name": "Observability & Health Daemon",
        "deliverable": "Automated Python/Bash service logging packet metrics as a managed systemd background daemon."
      }
    ],
    "expected_deliverables": [
      "GitHub repository with systemd unit files and kernel sysctl hardening presets",
      "Automated setup script deploying isolated network namespaces and firewall rules",
      "Network benchmark report demonstrating packet filtering throughput and latency analysis",
      "Comprehensive architectural documentation and packet-flow diagram"
    ],
    "evaluation_rubric": [
      {
        "criterion": "Linux System Administration",
        "target_standard": "Proper use of systemd services, security capabilities, and sysctl network tuning."
      },
      {
        "criterion": "Network Architecture & Routing",
        "target_standard": "Correct CIDR subnetting, stateful firewall rules, and verified packet flow inspection."
      },
      {
        "criterion": "Documentation & Reproducibility",
        "target_standard": "Single-command reproducible lab environment with clear verification commands."
      }
    ],
    "evidence_profile_impact": "Completing and publishing this project directly updates your Career Twin skill evidence for Linux, Networking, Docker from their current unverified/provisional status to Project-demonstrated, increasing your portfolio readiness sub-score."
  }
  ```
- **Error Response (404 Not Found)**:
  ```json
  {
    "detail": "Candidate with ID 'xxx' not found",
    "error_code": "NOT_FOUND"
  }
  ```

---

## 3. Summary of Differences from Prompt Hypotheses

| Feature | Prompt Hypothesis | Actual Backend Implementation | Impact / Action |
| :--- | :--- | :--- | :--- |
| **Simulator Request Field** | `hypothetical_skill_mastery_delta` | `hypothetical_skills` | **Corrected**: Request payload must send `{"hypothetical_skills": {"Skill": 85}}`. |
| **Simulator Values** | Delta increment (e.g. `+20`) | Absolute target mastery (e.g. `80`) | **Corrected**: Slider sets target mastery (0-100) or computes target = current + slider delta. |
| **Candidate List Endpoint** | Assumed `GET /api/candidates` | **Missing / None** | **Handled**: Pre-populate candidate selector with seeded IDs (`cand_devops_001`, `cand_backend_001`) and allow custom candidate ID entry. |
| **Skill Intelligence Endpoint** | Assumed separate `/api/skills` | Sourced from `GET /api/career-twin/{id}` | **Confirmed**: Twin endpoint exposes complete `skills` map and `skill_evidence` with all 6 verification properties. |
| **Health Check** | Assumed | `GET /health` returns `{"status": "healthy"}` | **Integrated**: Used in Top Bar for real-time backend connection status. |
