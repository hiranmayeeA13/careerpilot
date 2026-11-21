from __future__ import annotations
from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field


# ─── Evidence & Verification (Feature 2) ─────────────────────────────────────

ConfidenceLevel = Literal["Low", "Moderate", "High"]
EvidenceStatus = Literal[
    "Unverified",
    "Resume-supported",
    "Interview-demonstrated",
    "Project-demonstrated",
    "Strongly-supported"
]

class SkillEvidence(BaseModel):
    resume_claimed: bool = False
    resume_supported: bool = False
    interview_demonstrated: bool = False
    portfolio_demonstrated: bool = False
    confidence: ConfidenceLevel = "Low"
    status: EvidenceStatus = "Unverified"


# ─── Candidate & Career Twin Core Models (Feature 4) ─────────────────────────

class ProjectRecord(BaseModel):
    id: str
    title: str
    description: Optional[str] = ""
    skills_demonstrated: List[str] = Field(default_factory=list)
    completion_date: Optional[str] = None
    evaluation_score: Optional[int] = 80  # 0-100

class InterviewRecord(BaseModel):
    id: str
    target_role: str
    date: str
    performance_score: int = Field(ge=0, le=100)
    skills_evaluated: List[str] = Field(default_factory=list)
    feedback: Optional[str] = ""

class RoadmapRecord(BaseModel):
    version: int
    created_at: str
    target_role: str
    milestones: List[str] = Field(default_factory=list)

class CandidateProfile(BaseModel):
    id: str
    name: str
    target_role: str
    skills: Dict[str, int] = Field(default_factory=dict)  # skill_name -> mastery (0-100)
    skill_evidence: Dict[str, SkillEvidence] = Field(default_factory=dict)
    goals: List[str] = Field(default_factory=list)
    learning_preferences: Dict[str, Any] = Field(default_factory=dict)
    completed_projects: List[ProjectRecord] = Field(default_factory=list)
    interview_history: List[InterviewRecord] = Field(default_factory=list)
    prior_roadmaps: List[RoadmapRecord] = Field(default_factory=list)
    twin_summary: Optional[str] = None
    updated_at: Optional[str] = None


# ─── Feature 1: Readiness Score ──────────────────────────────────────────────

ReadinessCategory = Literal["Beginner", "Developing", "Job-Ready"]

class ReadinessBreakdown(BaseModel):
    skills: float = Field(ge=0, le=100, description="Weighted skill mastery score")
    interview: float = Field(ge=0, le=100, description="Verified interview performance score")
    portfolio: float = Field(ge=0, le=100, description="Portfolio completion score")
    evidence: float = Field(ge=0, le=100, description="Skill evidence verification score")

class ReadinessResponse(BaseModel):
    overall_score: int = Field(ge=0, le=100)
    category: ReadinessCategory
    breakdown: ReadinessBreakdown
    top_positive_factors: List[str] = Field(max_length=3)
    top_negative_factors: List[str] = Field(max_length=3)
    recommended_next_action: str


# ─── Feature 3: What-If Career Simulator ─────────────────────────────────────

class SimulationRequest(BaseModel):
    candidate_id: str
    hypothetical_skills: Dict[str, int] = Field(
        ...,
        description="Hypothetical delta skill mastery values (e.g. {'Linux': 80})"
    )

class SimulationResponse(BaseModel):
    current_score: int
    simulated_score: int
    delta: int
    newly_improved_skills: List[str]
    remaining_weaknesses: List[str]
    recommended_next_skill: str


# ─── Feature 4: Career Twin Update Trigger ───────────────────────────────────

TriggerType = Literal[
    "interview_completed",
    "learning_task_completed",
    "project_completed",
    "skill_assessed"
]

class CareerTwinUpdateRequest(BaseModel):
    candidate_id: str
    trigger_type: TriggerType
    payload: Dict[str, Any]


# ─── Feature 5: Career Reality Check ─────────────────────────────────────────

class RealityCheckRequest(BaseModel):
    candidate_id: str
    target_role: Optional[str] = None
    hypothetical_skills: Optional[Dict[str, int]] = None

class PrerequisiteItem(BaseModel):
    skill: str
    importance_weight: float
    required_mastery: int
    current_mastery: int
    evidence_status: EvidenceStatus
    is_met: bool
    why_it_matters: str

class RealityCheckResponse(BaseModel):
    target_role: str
    current_level: str
    major_prerequisites: List[PrerequisiteItem]
    missing_foundations: List[str]
    preparation_sequence: List[str]
    next_milestone: str


# ─── Feature 6: Smart Portfolio Project Generator ───────────────────────────

class PortfolioRecommendRequest(BaseModel):
    candidate_id: str
    variation_index: Optional[int] = 0

class ProjectMilestone(BaseModel):
    step: int
    name: str
    deliverable: str

class RubricCriterion(BaseModel):
    criterion: str
    target_standard: str

class PortfolioProjectResponse(BaseModel):
    title: str
    problem_statement: str
    why_recommended: str
    skills_demonstrated: List[str]
    difficulty: str
    required_tools: List[str]
    milestones: List[ProjectMilestone]
    expected_deliverables: List[str]
    evaluation_rubric: List[RubricCriterion]
    evidence_profile_impact: str


# ─── Standard Error Response ─────────────────────────────────────────────────

class ErrorResponse(BaseModel):
    detail: str
    error_code: str


# ─── Feature 7: Resume & Target-Role Intake ──────────────────────────────────

class ResumeIntakeRequest(BaseModel):
    name: str
    target_role: str
    resume_text: str = Field(..., description="Plain-text resume content pasted by the candidate")
    weekly_hours: Optional[int] = Field(default=10, ge=1, le=60)
    save_to_database: Optional[bool] = True

class ResumeIntakeResponse(BaseModel):
    candidate_id: str
    name: str
    target_role: str
    extracted_skills: Dict[str, int] = Field(description="skill -> starting mastery (0-100), derived from resume text")
    skills_detected: int
    message: str


# ─── Feature 8: Skill-Gap Map from Real Job Descriptions ─────────────────────

class JobPostingIngestRequest(BaseModel):
    role: str
    company: Optional[str] = None
    raw_text: str

class JobPostingIngestResponse(BaseModel):
    role: str
    company: Optional[str] = None
    postings_analyzed: int
    extracted_skills: Dict[str, int]
    aggregated_requirements: Dict[str, Dict[str, Any]]

class SkillGapRoleRequirement(BaseModel):
    skill: str
    demand_pct: float = Field(description="Percent of ingested postings mentioning this skill")
    required_mastery: int
    current_mastery: int
    is_met: bool
    is_foundation: bool

class SkillGapMapResponse(BaseModel):
    target_role: str
    source: Literal["real_job_postings", "fallback_defaults"]
    postings_analyzed: int
    requirements: List[SkillGapRoleRequirement]
    missing_skills: List[str]


# ─── Feature 9: Week-by-Week Learning Plan ───────────────────────────────────

class WeekPlanItem(BaseModel):
    week: int
    focus_skills: List[str]
    tasks: List[str]
    hours_allocated: int
    status: Literal["planned", "in_progress", "completed"] = "planned"

class LearningPlanResponse(BaseModel):
    candidate_id: str
    target_role: str
    source: Literal["real_job_postings", "fallback_defaults"]
    total_weeks: int
    weeks: List[WeekPlanItem]
    adjustment_note: str
    generated_at: Optional[str] = None


# ─── Feature 10: Mock Interviews Scored Against a Rubric ─────────────────────

class InterviewQuestion(BaseModel):
    question_id: str
    skill: str
    question: str
    rubric: List[str] = Field(description="The criteria an answer is scored against")

class InterviewStartResponse(BaseModel):
    session_id: str
    candidate_id: str
    questions: List[InterviewQuestion]

class InterviewAnswer(BaseModel):
    question_id: str
    answer_text: str

class InterviewSubmitRequest(BaseModel):
    candidate_id: str
    session_id: str
    answers: List[InterviewAnswer]

class QuestionScore(BaseModel):
    question_id: str
    skill: str
    score: int = Field(ge=0, le=100)
    rubric_hits: List[str]
    rubric_misses: List[str]
    feedback: str

class InterviewSubmitResponse(BaseModel):
    overall_score: int
    per_question: List[QuestionScore]
    recorded_to_career_twin: bool
    plan_adjusted: bool


# ─── Feature 11: Application Tracker That Learns From Responses ─────────────

ApplicationStatus = Literal["Applied", "Interviewing", "Rejected", "Offer", "No Response"]

class ApplicationLogRequest(BaseModel):
    candidate_id: str
    company: str
    role_title: str
    date_applied: Optional[str] = None
    status: ApplicationStatus = "Applied"

class ApplicationRecord(BaseModel):
    id: str
    candidate_id: str
    company: str
    role_title: str
    role_category: str
    date_applied: str
    status: ApplicationStatus
    responded: bool
    updated_at: Optional[str] = None

class ApplicationStatusUpdateRequest(BaseModel):
    status: ApplicationStatus

class CategoryInsight(BaseModel):
    category: str
    applied: int
    responded: int
    response_rate: float

class ApplicationInsightsResponse(BaseModel):
    candidate_id: str
    total_applications: int
    overall_response_rate: float
    by_role_category: List[CategoryInsight]
    recommendation: str
