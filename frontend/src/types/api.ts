/**
 * CAREERPILOT AI — TypeScript Type Definitions
 * Directly mirrored from backend Pydantic schemas in `app/models/schemas.py`
 */

// ─── Evidence & Verification (Feature 2) ─────────────────────────────────────

export type ConfidenceLevel = 'Low' | 'Moderate' | 'High';

export type EvidenceStatus =
  | 'Unverified'
  | 'Resume-supported'
  | 'Interview-demonstrated'
  | 'Project-demonstrated'
  | 'Strongly-supported';

export interface SkillEvidence {
  resume_claimed: boolean;
  resume_supported: boolean;
  interview_demonstrated: boolean;
  portfolio_demonstrated: boolean;
  confidence: ConfidenceLevel;
  status: EvidenceStatus;
}

// ─── Candidate & Career Twin Core Models (Feature 4) ─────────────────────────

export interface ProjectRecord {
  id: string;
  title: string;
  description?: string;
  skills_demonstrated: string[];
  completion_date?: string | null;
  evaluation_score?: number | null; // 0-100
}

export interface InterviewRecord {
  id: string;
  target_role: string;
  date: string;
  performance_score: number; // 0-100
  skills_evaluated: string[];
  feedback?: string;
}

export interface RoadmapRecord {
  version: number;
  created_at: string;
  target_role: string;
  milestones: string[];
}

export interface CandidateProfile {
  id: string;
  name: string;
  target_role: string;
  skills: Record<string, number>; // skill_name -> mastery (0-100)
  skill_evidence: Record<string, SkillEvidence>;
  goals: string[];
  learning_preferences: {
    preferred_format?: string;
    weekly_hours?: number;
    [key: string]: unknown;
  };
  completed_projects: ProjectRecord[];
  interview_history: InterviewRecord[];
  prior_roadmaps: RoadmapRecord[];
  twin_summary?: string | null;
  updated_at?: string | null;
}

// ─── Feature 1: Readiness Score ──────────────────────────────────────────────

export type ReadinessCategory = 'Beginner' | 'Developing' | 'Job-Ready';

export interface ReadinessBreakdown {
  skills: number; // 0-100
  interview: number; // 0-100
  portfolio: number; // 0-100
  evidence: number; // 0-100
}

export interface ReadinessResponse {
  overall_score: number; // 0-100
  category: ReadinessCategory;
  breakdown: ReadinessBreakdown;
  top_positive_factors: string[];
  top_negative_factors: string[];
  recommended_next_action: string;
}

// ─── Feature 3: What-If Career Simulator ─────────────────────────────────────

export interface SimulationRequest {
  candidate_id: string;
  hypothetical_skills: Record<string, number>; // Skill name -> target mastery (0-100)
}

export interface SimulationResponse {
  current_score: number;
  simulated_score: number;
  delta: number;
  newly_improved_skills: string[];
  remaining_weaknesses: string[];
  recommended_next_skill: string;
}

// ─── Feature 4: Career Twin Update Trigger ───────────────────────────────────

export type TriggerType =
  | 'interview_completed'
  | 'learning_task_completed'
  | 'project_completed'
  | 'skill_assessed';

export interface CareerTwinUpdateRequest {
  candidate_id: string;
  trigger_type: TriggerType;
  payload: Record<string, unknown>;
}

// ─── Feature 5: Career Reality Check ─────────────────────────────────────────

export interface RealityCheckRequest {
  candidate_id: string;
  target_role?: string | null;
  hypothetical_skills?: Record<string, number> | null;
}

export interface PrerequisiteItem {
  skill: string;
  importance_weight: number;
  required_mastery: number;
  current_mastery: number;
  evidence_status: EvidenceStatus;
  is_met: boolean;
  why_it_matters: string;
}

export type RealityCheckLevel = 'Beginner' | 'Intermediate' | 'Advanced';

export interface RealityCheckResponse {
  target_role: string;
  current_level: RealityCheckLevel | string;
  major_prerequisites: PrerequisiteItem[];
  missing_foundations: string[];
  preparation_sequence: string[];
  next_milestone: string;
}

// ─── Feature 6: Smart Portfolio Project Generator ───────────────────────────

export interface PortfolioRecommendRequest {
  candidate_id: string;
  variation_index?: number;
}

export interface ProjectMilestone {
  step: number;
  name: string;
  deliverable: string;
}

export interface RubricCriterion {
  criterion: string;
  target_standard: string;
}

export interface PortfolioProjectResponse {
  title: string;
  problem_statement: string;
  why_recommended: string;
  skills_demonstrated: string[];
  difficulty: string;
  required_tools: string[];
  milestones: ProjectMilestone[];
  expected_deliverables: string[];
  evaluation_rubric: RubricCriterion[];
  evidence_profile_impact: string;
}

// ─── System Health & Error Shapes ───────────────────────────────────────────

export interface BackendHealthResponse {
  status: string;
  service: string;
}

export interface ApiErrorDetail {
  detail: string;
  error_code: string;
}

// ─── Feature 7: Resume & Target-Role Intake ──────────────────────────────────

export interface ResumeIntakeRequest {
  name: string;
  target_role: string;
  resume_text: string;
  weekly_hours?: number;
  save_to_database?: boolean;
}

export interface ResumeIntakeResponse {
  candidate_id: string;
  name: string;
  target_role: string;
  extracted_skills: Record<string, number>;
  skills_detected: number;
  message: string;
}

// ─── Feature 8: Skill-Gap Map from Real Job Descriptions ─────────────────────

export interface JobPostingIngestRequest {
  role: string;
  company?: string;
  raw_text: string;
}

export interface JobPostingIngestResponse {
  role: string;
  company?: string;
  postings_analyzed: number;
  extracted_skills: Record<string, number>;
  aggregated_requirements: Record<string, { weight: number; is_foundation: boolean; required_mastery: number; demand_pct: number }>;
}

export interface SkillGapRoleRequirement {
  skill: string;
  demand_pct: number;
  required_mastery: number;
  current_mastery: number;
  is_met: boolean;
  is_foundation: boolean;
}

export interface SkillGapMapResponse {
  target_role: string;
  source: 'real_job_postings' | 'fallback_defaults';
  postings_analyzed: number;
  requirements: SkillGapRoleRequirement[];
  missing_skills: string[];
}

// ─── Feature 9: Week-by-Week Learning Plan ───────────────────────────────────

export interface WeekPlanItem {
  week: number;
  focus_skills: string[];
  tasks: string[];
  hours_allocated: number;
  status: 'planned' | 'in_progress' | 'completed';
}

export interface LearningPlanResponse {
  candidate_id: string;
  target_role: string;
  source: 'real_job_postings' | 'fallback_defaults';
  total_weeks: number;
  weeks: WeekPlanItem[];
  adjustment_note: string;
  generated_at?: string;
}

// ─── Feature 10: Mock Interviews Scored Against a Rubric ────────────────────

export interface InterviewQuestion {
  question_id: string;
  skill: string;
  question: string;
  rubric: string[];
}

export interface InterviewStartResponse {
  session_id: string;
  candidate_id: string;
  questions: InterviewQuestion[];
}

export interface InterviewAnswer {
  question_id: string;
  answer_text: string;
}

export interface InterviewSubmitRequest {
  candidate_id: string;
  session_id: string;
  answers: InterviewAnswer[];
}

export interface QuestionScore {
  question_id: string;
  skill: string;
  score: number;
  rubric_hits: string[];
  rubric_misses: string[];
  feedback: string;
}

export interface InterviewSubmitResponse {
  overall_score: number;
  per_question: QuestionScore[];
  recorded_to_career_twin: boolean;
  plan_adjusted: boolean;
}

// ─── Feature 11: Application Tracker That Learns From Responses ─────────────

export type ApplicationStatus = 'Applied' | 'Interviewing' | 'Rejected' | 'Offer' | 'No Response';

export interface ApplicationLogRequest {
  candidate_id: string;
  company: string;
  role_title: string;
  date_applied?: string;
  status?: ApplicationStatus;
}

export interface ApplicationRecord {
  id: string;
  candidate_id: string;
  company: string;
  role_title: string;
  role_category: string;
  date_applied: string;
  status: ApplicationStatus;
  responded: boolean;
  updated_at?: string | null;
}

export interface CategoryInsight {
  category: string;
  applied: number;
  responded: number;
  response_rate: number;
}

export interface ApplicationInsightsResponse {
  candidate_id: string;
  total_applications: number;
  overall_response_rate: number;
  by_role_category: CategoryInsight[];
  recommendation: string;
}
