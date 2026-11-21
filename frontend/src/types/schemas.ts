import { z } from 'zod';

export const ConfidenceLevelSchema = z.enum(['Low', 'Moderate', 'High']);

export const EvidenceStatusSchema = z.enum([
  'Unverified',
  'Resume-supported',
  'Interview-demonstrated',
  'Project-demonstrated',
  'Strongly-supported',
]);

export const SkillEvidenceSchema = z.object({
  resume_claimed: z.boolean().default(false),
  resume_supported: z.boolean().default(false),
  interview_demonstrated: z.boolean().default(false),
  portfolio_demonstrated: z.boolean().default(false),
  confidence: ConfidenceLevelSchema.default('Low'),
  status: EvidenceStatusSchema.default('Unverified'),
});

export const ProjectRecordSchema = z.object({
  id: z.string(),
  title: z.string(),
  description: z.string().optional().nullable().default(''),
  skills_demonstrated: z.array(z.string()).default([]),
  completion_date: z.string().optional().nullable(),
  evaluation_score: z.number().nullable().optional().default(80),
});

export const InterviewRecordSchema = z.object({
  id: z.string(),
  target_role: z.string(),
  date: z.string(),
  performance_score: z.number().min(0).max(100),
  skills_evaluated: z.array(z.string()).default([]),
  feedback: z.string().optional().nullable().default(''),
});

export const RoadmapRecordSchema = z.object({
  version: z.number(),
  created_at: z.string(),
  target_role: z.string(),
  milestones: z.array(z.string()).default([]),
});

export const CandidateProfileSchema = z.object({
  id: z.string(),
  name: z.string(),
  target_role: z.string(),
  skills: z.record(z.number()),
  skill_evidence: z.record(SkillEvidenceSchema).default({}),
  goals: z.array(z.string()).default([]),
  learning_preferences: z.record(z.any()).default({}),
  completed_projects: z.array(ProjectRecordSchema).default([]),
  interview_history: z.array(InterviewRecordSchema).default([]),
  prior_roadmaps: z.array(RoadmapRecordSchema).default([]),
  twin_summary: z.string().nullable().optional(),
  updated_at: z.string().nullable().optional(),
});

export const ReadinessBreakdownSchema = z.object({
  skills: z.number().min(0).max(100),
  interview: z.number().min(0).max(100),
  portfolio: z.number().min(0).max(100),
  evidence: z.number().min(0).max(100),
});

export const ReadinessResponseSchema = z.object({
  overall_score: z.number().min(0).max(100),
  category: z.enum(['Beginner', 'Developing', 'Job-Ready']),
  breakdown: ReadinessBreakdownSchema,
  top_positive_factors: z.array(z.string()).default([]),
  top_negative_factors: z.array(z.string()).default([]),
  recommended_next_action: z.string(),
});

export const SimulationResponseSchema = z.object({
  current_score: z.number(),
  simulated_score: z.number(),
  delta: z.number(),
  newly_improved_skills: z.array(z.string()).default([]),
  remaining_weaknesses: z.array(z.string()).default([]),
  recommended_next_skill: z.string(),
});

export const PrerequisiteItemSchema = z.object({
  skill: z.string(),
  importance_weight: z.number(),
  required_mastery: z.number(),
  current_mastery: z.number(),
  evidence_status: EvidenceStatusSchema,
  is_met: z.boolean(),
  why_it_matters: z.string(),
});

export const RealityCheckResponseSchema = z.object({
  target_role: z.string(),
  current_level: z.string(),
  major_prerequisites: z.array(PrerequisiteItemSchema).default([]),
  missing_foundations: z.array(z.string()).default([]),
  preparation_sequence: z.array(z.string()).default([]),
  next_milestone: z.string(),
});

export const ProjectMilestoneSchema = z.object({
  step: z.number(),
  name: z.string(),
  deliverable: z.string(),
});

export const RubricCriterionSchema = z.object({
  criterion: z.string(),
  target_standard: z.string(),
});

export const PortfolioProjectResponseSchema = z.object({
  title: z.string(),
  problem_statement: z.string(),
  why_recommended: z.string(),
  skills_demonstrated: z.array(z.string()).default([]),
  difficulty: z.string(),
  required_tools: z.array(z.string()).default([]),
  milestones: z.array(ProjectMilestoneSchema).default([]),
  expected_deliverables: z.array(z.string()).default([]),
  evaluation_rubric: z.array(RubricCriterionSchema).default([]),
  evidence_profile_impact: z.string(),
});

export const BackendHealthResponseSchema = z.object({
  status: z.string(),
  service: z.string(),
});
