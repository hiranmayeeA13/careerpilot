import type {
  ReadinessResponse,
  SimulationResponse,
  CandidateProfile,
  RealityCheckResponse,
  PortfolioProjectResponse,
  BackendHealthResponse,
  ApiErrorDetail,
  ResumeIntakeRequest,
  ResumeIntakeResponse,
  JobPostingIngestRequest,
  JobPostingIngestResponse,
  SkillGapMapResponse,
  LearningPlanResponse,
  InterviewStartResponse,
  InterviewSubmitRequest,
  InterviewSubmitResponse,
  ApplicationLogRequest,
  ApplicationRecord,
  ApplicationStatus,
  ApplicationInsightsResponse,
} from '../types/api';

const BASE_URL = (import.meta as any).env?.VITE_API_BASE_URL || 'http://127.0.0.1:8008';

export class ApiError extends Error {
  error_code: string;
  status: number;
  constructor(detail: string, error_code: string, status: number) {
    super(detail);
    this.error_code = error_code;
    this.status = status;
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let res: Response;
  try {
    res = await fetch(`${BASE_URL}${path}`, {
      headers: { 'Content-Type': 'application/json' },
      ...init,
    });
  } catch (e) {
    throw new ApiError(
      'Could not reach the CareerPilot backend. Make sure the FastAPI server is running on ' + BASE_URL,
      'NETWORK_ERROR',
      0
    );
  }
  if (!res.ok) {
    let body: ApiErrorDetail | null = null;
    try {
      body = await res.json();
    } catch {
      /* noop */
    }
    throw new ApiError(body?.detail || `Request failed (${res.status})`, body?.error_code || 'ERROR', res.status);
  }
  return res.json() as Promise<T>;
}

export const api = {
  health: () => request<BackendHealthResponse>('/health'),

  getReadiness: (candidateId: string) => request<ReadinessResponse>(`/api/readiness/${encodeURIComponent(candidateId)}`),

  simulate: (candidateId: string, hypotheticalSkills: Record<string, number>) =>
    request<SimulationResponse>('/api/career/simulate', {
      method: 'POST',
      body: JSON.stringify({ candidate_id: candidateId, hypothetical_skills: hypotheticalSkills }),
    }),

  getCareerTwin: (candidateId: string) => request<CandidateProfile>(`/api/career-twin/${encodeURIComponent(candidateId)}`),

  updateCareerTwin: (candidateId: string, triggerType: string, payload: Record<string, unknown>) =>
    request<CandidateProfile>('/api/career-twin/update', {
      method: 'POST',
      body: JSON.stringify({ candidate_id: candidateId, trigger_type: triggerType, payload }),
    }),

  realityCheck: (candidateId: string, targetRole?: string, hypotheticalSkills?: Record<string, number> | null) =>
    request<RealityCheckResponse>('/api/career/reality-check', {
      method: 'POST',
      body: JSON.stringify({ candidate_id: candidateId, target_role: targetRole ?? null, hypothetical_skills: hypotheticalSkills ?? null }),
    }),

  recommendPortfolio: (candidateId: string, variationIndex: number = 0) =>
    request<PortfolioProjectResponse>('/api/portfolio/recommend', {
      method: 'POST',
      body: JSON.stringify({ candidate_id: candidateId, variation_index: variationIndex }),
    }),

  // Feature 7 — Resume & target-role intake
  intakeResume: (payload: ResumeIntakeRequest) =>
    request<ResumeIntakeResponse>('/api/intake/resume', { method: 'POST', body: JSON.stringify(payload) }),
  saveIntakeCandidate: (candidateId: string) =>
    request<{ candidate_id: string; saved: boolean; message: string }>(`/api/intake/resume/${encodeURIComponent(candidateId)}/save`, { method: 'POST' }),

  // Feature 8 — Real job description ingestion + skill-gap map
  ingestJobPosting: (payload: JobPostingIngestRequest) =>
    request<JobPostingIngestResponse>('/api/jobs/ingest', { method: 'POST', body: JSON.stringify(payload) }),
  getSkillGapMap: (candidateId: string, targetRole?: string) =>
    request<SkillGapMapResponse>(
      `/api/jobs/skill-gap/${encodeURIComponent(candidateId)}${targetRole ? `?target_role=${encodeURIComponent(targetRole)}` : ''}`
    ),

  // Feature 9 — Week-by-week learning plan
  getLearningPlan: (candidateId: string) => request<LearningPlanResponse>(`/api/plan/${encodeURIComponent(candidateId)}`),
  regenerateLearningPlan: (candidateId: string) =>
    request<LearningPlanResponse>(`/api/plan/${encodeURIComponent(candidateId)}/regenerate`, { method: 'POST' }),

  // Feature 10 — Mock interviews scored against a rubric
  startInterview: (candidateId: string, variant: number = 0) =>
    request<InterviewStartResponse>(`/api/interview/start/${encodeURIComponent(candidateId)}?variant=${variant}`, { method: 'POST' }),
  submitInterview: (payload: InterviewSubmitRequest) =>
    request<InterviewSubmitResponse>('/api/interview/submit', { method: 'POST', body: JSON.stringify(payload) }),

  getRosterCandidates: () => request<CandidateProfile[]>('/api/career-twin/roster/all'),
  saveCandidateProfile: (profile: CandidateProfile) =>
    request<CandidateProfile>('/api/career-twin/save-profile', { method: 'POST', body: JSON.stringify(profile) }),
  deleteCandidate: (candidateId: string) =>
    request<{ candidate_id: string; deleted: boolean }>(`/api/career-twin/${encodeURIComponent(candidateId)}`, { method: 'DELETE' }),

  // Feature 11 — Application tracker that learns from responses
  logApplication: (payload: ApplicationLogRequest) =>
    request<ApplicationRecord>('/api/applications/log', { method: 'POST', body: JSON.stringify(payload) }),
  listApplications: (candidateId: string) => request<ApplicationRecord[]>(`/api/applications/${encodeURIComponent(candidateId)}`),
  updateApplicationStatus: (appId: string, status: ApplicationStatus) =>
    request<{ id: string; status: string; updated: boolean }>(`/api/applications/${encodeURIComponent(appId)}/status`, {
      method: 'PATCH',
      body: JSON.stringify({ status }),
    }),
  getApplicationInsights: (candidateId: string) =>
    request<ApplicationInsightsResponse>(`/api/applications/${encodeURIComponent(candidateId)}/insights`),
};
