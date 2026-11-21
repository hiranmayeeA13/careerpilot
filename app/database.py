import json
import sqlite3
from typing import Any, Dict, List, Optional
from app.config import DB_PATH
from app.models.schemas import CandidateProfile, SkillEvidence, ProjectRecord, InterviewRecord, RoadmapRecord

# Resume-intake profiles remain in process memory until explicitly saved.
_TEMP_CANDIDATES: Dict[str, CandidateProfile] = {}


ROLE_REQUIREMENTS: Dict[str, Dict[str, Dict[str, Any]]] = {
    "DevOps Engineer": {
        "Linux": {"weight": 0.25, "is_foundation": True, "required_mastery": 75},
        "Networking": {"weight": 0.20, "is_foundation": True, "required_mastery": 70},
        "Docker": {"weight": 0.20, "is_foundation": False, "required_mastery": 70},
        "Kubernetes": {"weight": 0.15, "is_foundation": False, "required_mastery": 65},
        "CI/CD": {"weight": 0.10, "is_foundation": False, "required_mastery": 65},
        "Cloud/AWS": {"weight": 0.10, "is_foundation": False, "required_mastery": 65},
    },
    "Backend Engineer": {
        "Python": {"weight": 0.25, "is_foundation": True, "required_mastery": 75},
        "Data Structures & Algorithms": {"weight": 0.25, "is_foundation": True, "required_mastery": 75},
        "SQL & Databases": {"weight": 0.20, "is_foundation": True, "required_mastery": 70},
        "API Design & REST": {"weight": 0.15, "is_foundation": False, "required_mastery": 70},
        "System Design": {"weight": 0.15, "is_foundation": False, "required_mastery": 65},
    },
    "Frontend Engineer": {
        "React": {"weight": 0.25, "is_foundation": True, "required_mastery": 75},
        "TypeScript": {"weight": 0.25, "is_foundation": True, "required_mastery": 75},
        "JavaScript": {"weight": 0.20, "is_foundation": True, "required_mastery": 70},
        "HTML/CSS": {"weight": 0.15, "is_foundation": False, "required_mastery": 70},
        "Web Performance & Testing": {"weight": 0.15, "is_foundation": False, "required_mastery": 65},
    },
    "Full Stack Developer": {
        "React": {"weight": 0.20, "is_foundation": True, "required_mastery": 75},
        "TypeScript": {"weight": 0.20, "is_foundation": True, "required_mastery": 75},
        "Node.js": {"weight": 0.20, "is_foundation": True, "required_mastery": 70},
        "SQL & Databases": {"weight": 0.15, "is_foundation": False, "required_mastery": 70},
        "REST APIs": {"weight": 0.15, "is_foundation": False, "required_mastery": 65},
        "Docker": {"weight": 0.10, "is_foundation": False, "required_mastery": 65},
    },
    "Cloud Solutions Architect": {
        "Cloud Architecture": {"weight": 0.30, "is_foundation": True, "required_mastery": 80},
        "Networking": {"weight": 0.20, "is_foundation": True, "required_mastery": 75},
        "Security & IAM": {"weight": 0.20, "is_foundation": True, "required_mastery": 75},
        "DevOps & IaC": {"weight": 0.15, "is_foundation": False, "required_mastery": 70},
        "Cost Optimization": {"weight": 0.15, "is_foundation": False, "required_mastery": 65},
    },
    "Data Engineer": {
        "Python": {"weight": 0.25, "is_foundation": True, "required_mastery": 75},
        "SQL & Databases": {"weight": 0.25, "is_foundation": True, "required_mastery": 75},
        "Data Pipelines": {"weight": 0.20, "is_foundation": True, "required_mastery": 70},
        "Big Data & Spark": {"weight": 0.15, "is_foundation": False, "required_mastery": 65},
        "Cloud Warehousing": {"weight": 0.15, "is_foundation": False, "required_mastery": 65},
    },
    "Machine Learning Engineer": {
        "Python": {"weight": 0.25, "is_foundation": True, "required_mastery": 75},
        "Machine Learning": {"weight": 0.25, "is_foundation": True, "required_mastery": 75},
        "Data Structures & Algorithms": {"weight": 0.20, "is_foundation": True, "required_mastery": 70},
        "MLOps & Deployment": {"weight": 0.15, "is_foundation": False, "required_mastery": 65},
        "Deep Learning": {"weight": 0.15, "is_foundation": False, "required_mastery": 65},
    },
    "Site Reliability Engineer": {
        "Linux": {"weight": 0.25, "is_foundation": True, "required_mastery": 75},
        "Networking": {"weight": 0.20, "is_foundation": True, "required_mastery": 75},
        "Kubernetes": {"weight": 0.20, "is_foundation": False, "required_mastery": 70},
        "Monitoring & Observability": {"weight": 0.20, "is_foundation": False, "required_mastery": 70},
        "Incident Management": {"weight": 0.15, "is_foundation": False, "required_mastery": 65},
    },
    "Security Engineer": {
        "Security & IAM": {"weight": 0.25, "is_foundation": True, "required_mastery": 75},
        "Networking": {"weight": 0.25, "is_foundation": True, "required_mastery": 75},
        "Application Security": {"weight": 0.20, "is_foundation": False, "required_mastery": 70},
        "Vulnerability Assessment": {"weight": 0.15, "is_foundation": False, "required_mastery": 65},
        "Cryptography": {"weight": 0.15, "is_foundation": False, "required_mastery": 65},
    },
    "Software Engineer": {
        "Data Structures & Algorithms": {"weight": 0.25, "is_foundation": True, "required_mastery": 75},
        "System Design": {"weight": 0.20, "is_foundation": True, "required_mastery": 70},
        "Testing & CI/CD": {"weight": 0.20, "is_foundation": False, "required_mastery": 70},
        "API Design & REST": {"weight": 0.20, "is_foundation": False, "required_mastery": 65},
        "SQL & Databases": {"weight": 0.15, "is_foundation": False, "required_mastery": 65},
    },
}


def get_db_connection(db_path: str = DB_PATH) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: str = DB_PATH) -> None:
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS candidates (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            target_role TEXT NOT NULL,
            skills_json TEXT NOT NULL,
            skill_evidence_json TEXT NOT NULL,
            goals_json TEXT NOT NULL,
            learning_preferences_json TEXT NOT NULL,
            completed_projects_json TEXT NOT NULL,
            interview_history_json TEXT NOT NULL,
            prior_roadmaps_json TEXT NOT NULL,
            twin_summary TEXT,
            updated_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def save_candidate(candidate: CandidateProfile, db_path: str = DB_PATH, force_persist: bool = False) -> None:
    if candidate.id in _TEMP_CANDIDATES and not force_persist:
        _TEMP_CANDIDATES[candidate.id] = candidate
        return
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    
    # Serialize sub-models to JSON
    evidence_dict = {
        k: (v.model_dump() if isinstance(v, SkillEvidence) else v)
        for k, v in candidate.skill_evidence.items()
    }
    projects_list = [
        (p.model_dump() if isinstance(p, ProjectRecord) else p)
        for p in candidate.completed_projects
    ]
    interviews_list = [
        (i.model_dump() if isinstance(i, InterviewRecord) else i)
        for i in candidate.interview_history
    ]
    roadmaps_list = [
        (r.model_dump() if isinstance(r, RoadmapRecord) else r)
        for r in candidate.prior_roadmaps
    ]

    cursor.execute("""
        INSERT OR REPLACE INTO candidates (
            id, name, target_role, skills_json, skill_evidence_json,
            goals_json, learning_preferences_json, completed_projects_json,
            interview_history_json, prior_roadmaps_json, twin_summary, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
    """, (
        candidate.id,
        candidate.name,
        candidate.target_role,
        json.dumps(candidate.skills),
        json.dumps(evidence_dict),
        json.dumps(candidate.goals),
        json.dumps(candidate.learning_preferences),
        json.dumps(projects_list),
        json.dumps(interviews_list),
        json.dumps(roadmaps_list),
        candidate.twin_summary,
    ))
    conn.commit()
    conn.close()


def get_candidate(candidate_id: str, db_path: str = DB_PATH) -> Optional[CandidateProfile]:
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM candidates WHERE id = ?", (candidate_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        # Temporary intake profiles are usable by all analysis endpoints but never
        # written to the persistent SQLite roster unless explicitly saved.
        return _TEMP_CANDIDATES.get(candidate_id)

    skills = json.loads(row["skills_json"])
    evidence_raw = json.loads(row["skill_evidence_json"])
    skill_evidence = {
        k: SkillEvidence(**v) for k, v in evidence_raw.items()
    }
    goals = json.loads(row["goals_json"])
    learning_preferences = json.loads(row["learning_preferences_json"])
    completed_projects = [ProjectRecord(**p) for p in json.loads(row["completed_projects_json"])]
    interview_history = [InterviewRecord(**i) for i in json.loads(row["interview_history_json"])]
    prior_roadmaps = [RoadmapRecord(**r) for r in json.loads(row["prior_roadmaps_json"])]

    return CandidateProfile(
        id=row["id"],
        name=row["name"],
        target_role=row["target_role"],
        skills=skills,
        skill_evidence=skill_evidence,
        goals=goals,
        learning_preferences=learning_preferences,
        completed_projects=completed_projects,
        interview_history=interview_history,
        prior_roadmaps=prior_roadmaps,
        twin_summary=row["twin_summary"],
        updated_at=row["updated_at"]
    )


def get_role_requirements(role_name: str, candidate_skills: Optional[Dict[str, int]] = None) -> Dict[str, Dict[str, Any]]:
    """Return requirement map for the given role, or fallback defaults."""
    if not role_name:
        role_name = "Software Engineer"
    if role_name in ROLE_REQUIREMENTS:
        return ROLE_REQUIREMENTS[role_name]
    
    role_lower = role_name.lower()
    if "devops" in role_lower:
        return ROLE_REQUIREMENTS["DevOps Engineer"]
    elif "full" in role_lower or "stack" in role_lower:
        return ROLE_REQUIREMENTS["Full Stack Developer"]
    elif "front" in role_lower or "ui" in role_lower or "react" in role_lower:
        return ROLE_REQUIREMENTS["Frontend Engineer"]
    elif "cloud" in role_lower or "architect" in role_lower:
        return ROLE_REQUIREMENTS["Cloud Solutions Architect"]
    elif "data" in role_lower:
        return ROLE_REQUIREMENTS["Data Engineer"]
    elif "ml" in role_lower or "machine" in role_lower or "ai" in role_lower:
        return ROLE_REQUIREMENTS["Machine Learning Engineer"]
    elif "sre" in role_lower or "reliability" in role_lower:
        return ROLE_REQUIREMENTS["Site Reliability Engineer"]
    elif "sec" in role_lower or "cyber" in role_lower:
        return ROLE_REQUIREMENTS["Security Engineer"]
    elif "back" in role_lower:
        return ROLE_REQUIREMENTS["Backend Engineer"]

    if candidate_skills and len(candidate_skills) > 0:
        reqs: Dict[str, Dict[str, Any]] = {}
        top_skills = list(candidate_skills.keys())[:5]
        weight_per_skill = round(1.0 / len(top_skills), 2)
        for i, sk in enumerate(top_skills):
            reqs[sk] = {
                "weight": weight_per_skill,
                "is_foundation": i < 2,
                "required_mastery": 70,
            }
        return reqs

    return ROLE_REQUIREMENTS["Software Engineer"]


def list_all_candidates(db_path: str = DB_PATH) -> List[CandidateProfile]:
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM candidates")
    rows = cursor.fetchall()
    conn.close()

    candidates: List[CandidateProfile] = []
    seen_ids = set()
    for row in rows:
        c = get_candidate(row["id"], db_path)
        if c:
            candidates.append(c)
            seen_ids.add(c.id)

    return candidates


def delete_candidate(candidate_id: str, db_path: str = DB_PATH) -> bool:
    _TEMP_CANDIDATES.pop(candidate_id, None)
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM candidates WHERE id = ?", (candidate_id,))
    cursor.execute("DELETE FROM applications WHERE candidate_id = ?", (candidate_id,))
    cursor.execute("DELETE FROM learning_plans WHERE candidate_id = ?", (candidate_id,))
    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return deleted


# ─────────────────────────────────────────────────────────────────────────────
# Spotlight Round 2 — extra tables: job postings, learning plans, applications
# ─────────────────────────────────────────────────────────────────────────────

def init_extra_tables(db_path: str = DB_PATH) -> None:
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS job_postings (
            id TEXT PRIMARY KEY,
            role TEXT NOT NULL,
            company TEXT,
            raw_text TEXT NOT NULL,
            extracted_skills_json TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS learning_plans (
            candidate_id TEXT PRIMARY KEY,
            target_role TEXT NOT NULL,
            plan_json TEXT NOT NULL,
            source TEXT NOT NULL,
            adjustment_note TEXT,
            generated_at TEXT NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS applications (
            id TEXT PRIMARY KEY,
            candidate_id TEXT NOT NULL,
            company TEXT NOT NULL,
            role_title TEXT NOT NULL,
            role_category TEXT NOT NULL,
            date_applied TEXT NOT NULL,
            status TEXT NOT NULL,
            responded INTEGER NOT NULL DEFAULT 0,
            updated_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def create_candidate(candidate: "CandidateProfile", db_path: str = DB_PATH, persist: bool = False) -> None:
    """Register a candidate in memory by default; persist only on explicit choice."""
    if persist:
        save_candidate(candidate, db_path=db_path)
        _TEMP_CANDIDATES.pop(candidate.id, None)
    else:
        # Keep only the current active unsaved session candidate so previous discarded names don't linger
        _TEMP_CANDIDATES.clear()
        _TEMP_CANDIDATES[candidate.id] = candidate


def save_intake_candidate(candidate_id: str, db_path: str = DB_PATH) -> Optional[CandidateProfile]:
    """Promote an in-memory intake candidate to the persistent SQLite roster."""
    candidate = _TEMP_CANDIDATES.get(candidate_id)
    if candidate is None:
        # Already saved or not an intake candidate.
        return get_candidate(candidate_id, db_path=db_path)
    save_candidate(candidate, db_path=db_path, force_persist=True)
    _TEMP_CANDIDATES.pop(candidate_id, None)
    return candidate


def save_job_posting(posting_id: str, role: str, company: Optional[str], raw_text: str,
                      extracted_skills: Dict[str, int], db_path: str = DB_PATH) -> None:
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO job_postings (id, role, company, raw_text, extracted_skills_json, created_at)
        VALUES (?, ?, ?, ?, ?, datetime('now'))
    """, (posting_id, role, company, raw_text, json.dumps(extracted_skills)))
    conn.commit()
    conn.close()


def get_job_postings_for_role(role: str, db_path: str = DB_PATH) -> List[Dict[str, Any]]:
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM job_postings WHERE role = ? ORDER BY created_at DESC", (role,))
    rows = cursor.fetchall()
    conn.close()
    return [
        {
            "id": r["id"],
            "role": r["role"],
            "company": r["company"],
            "raw_text": r["raw_text"],
            "extracted_skills": json.loads(r["extracted_skills_json"]),
            "created_at": r["created_at"],
        }
        for r in rows
    ]


def save_learning_plan(candidate_id: str, target_role: str, plan: List[Dict[str, Any]],
                        source: str, adjustment_note: str, db_path: str = DB_PATH) -> None:
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO learning_plans (candidate_id, target_role, plan_json, source, adjustment_note, generated_at)
        VALUES (?, ?, ?, ?, ?, datetime('now'))
    """, (candidate_id, target_role, json.dumps(plan), source, adjustment_note))
    conn.commit()
    conn.close()


def get_learning_plan(candidate_id: str, db_path: str = DB_PATH) -> Optional[Dict[str, Any]]:
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM learning_plans WHERE candidate_id = ?", (candidate_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    return {
        "candidate_id": candidate_id,
        "target_role": row["target_role"],
        "weeks": json.loads(row["plan_json"]),
        "source": row["source"],
        "adjustment_note": row["adjustment_note"],
        "generated_at": row["generated_at"],
    }


def save_application(app_id: str, candidate_id: str, company: str, role_title: str,
                      role_category: str, date_applied: str, status: str, responded: bool,
                      db_path: str = DB_PATH) -> None:
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO applications
            (id, candidate_id, company, role_title, role_category, date_applied, status, responded, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
    """, (app_id, candidate_id, company, role_title, role_category, date_applied, status, int(responded)))
    conn.commit()
    conn.close()


def get_applications(candidate_id: str, db_path: str = DB_PATH) -> List[Dict[str, Any]]:
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM applications WHERE candidate_id = ? ORDER BY date_applied DESC", (candidate_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def update_application_status(app_id: str, status: str, responded: bool, db_path: str = DB_PATH) -> bool:
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE applications SET status = ?, responded = ?, updated_at = datetime('now') WHERE id = ?",
        (status, int(responded), app_id),
    )
    changed = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return changed
