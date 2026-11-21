import {
  BackendHealthResponse,
  CandidateProfile,
  CareerTwinUpdateRequest,
  PortfolioProjectResponse,
  PortfolioRecommendRequest,
  ReadinessResponse,
  RealityCheckRequest,
  RealityCheckResponse,
  SimulationRequest,
  SimulationResponse,
} from '../types/api';

const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8008';

async function request<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const url = `${BASE_URL}${endpoint}`;
  const response = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  });

  if (!response.ok) {
    let errorDetail = `Request failed with status ${response.status}`;
    try {
      const errorJson = await response.json();
      errorDetail = errorJson.detail || errorDetail;
    } catch {
      // ignore json parse error
    }
    throw new Error(errorDetail);
  }

  return response.json();
}

export const api = {
  getHealth(): Promise<BackendHealthResponse> {
    return request<BackendHealthResponse>('/health');
  },

  getCareerTwin(candidateId: string): Promise<CandidateProfile> {
    return request<CandidateProfile>(`/api/career-twin/${candidateId}`);
  },

  updateCareerTwin(data: CareerTwinUpdateRequest): Promise<CandidateProfile> {
    return request<CandidateProfile>('/api/career-twin/update', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  getReadiness(candidateId: string): Promise<ReadinessResponse> {
    return request<ReadinessResponse>(`/api/readiness/${candidateId}`);
  },

  simulateCareer(data: SimulationRequest): Promise<SimulationResponse> {
    return request<SimulationResponse>('/api/career/simulate', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  realityCheck(data: RealityCheckRequest): Promise<RealityCheckResponse> {
    return request<RealityCheckResponse>('/api/career/reality-check', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  recommendPortfolio(data: PortfolioRecommendRequest): Promise<PortfolioProjectResponse> {
    return request<PortfolioProjectResponse>('/api/portfolio/recommend', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },
};
