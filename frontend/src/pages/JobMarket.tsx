import { useState } from 'react';
import { Briefcase, Sparkles, Loader2, CheckCircle2, XCircle, TrendingUp, DollarSign, Layers } from 'lucide-react';
import { useCandidate } from '../state/CandidateContext';
import { useApi } from '../lib/useApi';
import { api, ApiError } from '../lib/api';
import { Spinner, ErrorBanner, SectionTitle, Badge } from '../components/Primitives';

const SAMPLE_POSTINGS = [
  {
    company: 'Stripe',
    role: 'DevOps Engineer',
    salary: '$150,000 - $185,000',
    demand: 'Very High (+24% YoY)',
    text: `Stripe is looking for a DevOps Engineer to scale our core payment infrastructure.
Key Requirements:
- Strong Linux systems administration and performance profiling (top, vmstat, systemd)
- High proficiency in Docker containerization and Kubernetes cluster orchestration
- Deep understanding of Networking fundamentals (TCP/IP, DNS, TLS certificates, routing)
- Experience designing automated CI/CD pipelines with GitHub Actions or GitLab
- Cloud experience with AWS (VPC, IAM, ECS/EKS)`,
  },
  {
    company: 'Netflix',
    role: 'Full Stack Developer',
    salary: '$160,000 - $210,000',
    demand: 'High (+18% YoY)',
    text: `Netflix is seeking a Full Stack Developer to build next-generation studio applications.
Key Requirements:
- Deep expertise in React, TypeScript, and modern state management patterns
- Production experience with Node.js backend services and high-throughput REST APIs
- Solid knowledge of SQL & Databases (PostgreSQL, schema design, query optimization)
- Experience packaging microservices using Docker
- Familiarity with CI/CD and automated end-to-end testing`,
  },
  {
    company: 'AWS',
    role: 'Cloud Solutions Architect',
    salary: '$165,000 - $205,000',
    demand: 'Very High (+28% YoY)',
    text: `Amazon Web Services is hiring a Cloud Solutions Architect to guide enterprise migrations.
Key Requirements:
- Deep expertise in Cloud Architecture, multi-tier systems, and high availability design
- Solid Networking mastery (VPCs, CIDR subnetting, Direct Connect, Route 53)
- Thorough understanding of Security & IAM least-privilege policies and compliance
- Experience automating deployments via DevOps & IaC (Terraform, CloudFormation)
- Cost Optimization and capacity planning for distributed enterprise workloads`,
  },
  {
    company: 'Shopify',
    role: 'Backend Engineer',
    salary: '$140,000 - $180,000',
    demand: 'High (+20% YoY)',
    text: `Shopify is seeking a Backend Engineer to build resilient merchant checkout pipelines.
Key Requirements:
- Strong proficiency in Python or Ruby for building high-concurrency microservices
- Deep understanding of Data Structures & Algorithms and algorithmic time complexity
- Mastery of SQL & Databases (PostgreSQL/MySQL, ACID transactions, index optimization)
- Experience designing clean, idempotent RESTful APIs and distributed workflows
- Familiarity with System Design principles and caching with Redis`,
  },
];

export function JobMarket() {
  const { candidateId, candidate } = useCandidate();
  const [company, setCompany] = useState('');
  const [rawText, setRawText] = useState('');
  const [ingesting, setIngesting] = useState(false);
  const [ingestError, setIngestError] = useState<string | null>(null);
  const [ingestMsg, setIngestMsg] = useState<string | null>(null);
  const [selectedPreset, setSelectedPreset] = useState<number | null>(null);

  const gapMap = useApi(() => api.getSkillGapMap(candidateId), [candidateId]);

  function loadSample(idx: number) {
    const p = SAMPLE_POSTINGS[idx];
    setSelectedPreset(idx);
    setCompany(p.company);
    setRawText(p.text);
  }

  async function ingest() {
    if (!rawText.trim()) {
      setIngestError('Select a sample or paste a job description first.');
      return;
    }
    setIngesting(true);
    setIngestError(null);
    setIngestMsg(null);
    try {
      const res = await api.ingestJobPosting({ role: candidate.role, company: company || undefined, raw_text: rawText });
      setIngestMsg(`✓ Ingested and analyzed ${res.postings_analyzed} posting(s) for ${res.role}.`);
      gapMap.refetch();
    } catch (e) {
      setIngestError(e instanceof ApiError ? e.message : 'Ingestion failed.');
    } finally {
      setIngesting(false);
    }
  }

  const activePreset = selectedPreset !== null ? SAMPLE_POSTINGS[selectedPreset] : null;

  return (
    <div className="fade-up space-y-6">
      <SectionTitle
        icon={<Briefcase size={20} />}
        title="Job Market & Gap Analysis"
        subtitle={`Real-world market requirements and skill-gap map for ${candidate.name} (${candidate.role})`}
      />

      {/* 1-Click Sample Postings */}
      <div className="card p-5 space-y-3">
        <p className="text-xs uppercase tracking-wider text-white/50 font-semibold">1-Click Sample Job Postings</p>
        <div className="grid sm:grid-cols-2 md:grid-cols-4 gap-3">
          {SAMPLE_POSTINGS.map((p, idx) => (
            <button
              key={p.company}
              onClick={() => loadSample(idx)}
              className={`p-3 rounded-xl border text-left transition-all ${
                selectedPreset === idx
                  ? 'bg-accent/15 border-accent text-white'
                  : 'bg-white/[0.02] border-white/5 hover:border-white/15 text-white/75'
              }`}
            >
              <div className="flex items-center justify-between">
                <span className="font-bold text-sm text-white">{p.company}</span>
                <span className="text-[10px] text-accent2 font-semibold">Sample</span>
              </div>
              <p className="text-xs text-white/50 mt-1">{p.role}</p>
            </button>
          ))}
        </div>
      </div>

      {/* Market Benchmark KPIs */}
      {activePreset && (
        <div className="grid sm:grid-cols-2 gap-4">
          <div className="card p-4 flex items-center gap-3 bg-gradient-to-r from-accent2/10 to-transparent border-accent2/20">
            <DollarSign size={20} className="text-accent2 shrink-0" />
            <div>
              <p className="text-[10px] uppercase text-white/40">Market Compensation Range</p>
              <p className="text-base font-bold text-white mt-0.5">{activePreset.salary}</p>
            </div>
          </div>
          <div className="card p-4 flex items-center gap-3 bg-gradient-to-r from-accent/10 to-transparent border-accent/20">
            <TrendingUp size={20} className="text-accent shrink-0" />
            <div>
              <p className="text-[10px] uppercase text-white/40">Market Demand Index</p>
              <p className="text-base font-bold text-white mt-0.5">{activePreset.demand}</p>
            </div>
          </div>
        </div>
      )}

      {/* Ingestion Box */}
      <div className="card p-5 space-y-3">
        <div className="grid md:grid-cols-[1fr_200px] gap-3">
          <div>
            <label className="text-xs text-white/50 mb-1.5 block">Target Role</label>
            <input
              value={candidate.role}
              disabled
              className="w-full bg-white/5 border border-white/10 rounded-xl px-3 py-2 text-sm text-white/50"
            />
          </div>
          <div>
            <label className="text-xs text-white/50 mb-1.5 block">Company Name</label>
            <input
              value={company}
              onChange={(e) => setCompany(e.target.value)}
              placeholder="e.g. Stripe, AWS"
              className="w-full bg-white/5 border border-white/10 rounded-xl px-3 py-2 text-sm text-white focus:outline-none focus:border-accent"
            />
          </div>
        </div>

        <div>
          <label className="text-xs text-white/50 mb-1.5 block">Job Description Text</label>
          <textarea
            value={rawText}
            onChange={(e) => setRawText(e.target.value)}
            rows={5}
            placeholder="Paste a job description or select one of the presets above..."
            className="w-full bg-white/5 border border-white/10 rounded-xl px-3 py-2.5 text-sm text-white placeholder:text-white/25 focus:outline-none focus:border-accent font-sans"
          />
        </div>

        {ingestError && <p className="text-xs text-danger">{ingestError}</p>}
        {ingestMsg && <p className="text-xs text-accent2">{ingestMsg}</p>}

        <button
          onClick={ingest}
          disabled={ingesting}
          className="flex items-center gap-2 bg-accent hover:bg-accent/90 disabled:opacity-60 text-ink font-semibold text-sm px-4 py-2 rounded-xl transition-colors shadow-glow"
        >
          {ingesting ? <Loader2 size={16} className="animate-spin" /> : <Sparkles size={16} />}
          Ingest & Refresh Gap Analysis
        </button>
      </div>

      {/* Gap Analysis Display */}
      {gapMap.loading ? (
        <Spinner label="Analyzing skill gaps..." />
      ) : gapMap.error ? (
        <ErrorBanner message={gapMap.error} onRetry={gapMap.refetch} />
      ) : gapMap.data ? (
        <div className="space-y-4">
          <div className="card p-5 flex items-center justify-between flex-wrap gap-4">
            <div>
              <p className="text-xs uppercase tracking-wider text-white/40">Market Readiness Gap</p>
              <h4 className="text-lg font-bold text-white mt-1">
                {gapMap.data.target_role} ({gapMap.data.source === 'real_job_postings' ? `${gapMap.data.postings_analyzed} Real Postings Analyzed` : 'Role Benchmark'})
              </h4>
            </div>
            <div className="flex items-center gap-2">
              <Badge className={gapMap.data.source === 'real_job_postings' ? 'bg-accent2/15 text-accent2 border-accent2/25' : 'bg-white/5 text-white/50 border-white/10'}>
                {gapMap.data.source === 'real_job_postings' ? 'Live Market Feed' : 'Standard Benchmark'}
              </Badge>
            </div>
          </div>

          <div className="grid md:grid-cols-2 gap-4">
            {gapMap.data.requirements.map((r) => (
              <div key={r.skill} className="card p-4 space-y-2 border-white/5">
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-2">
                    {r.is_met ? (
                      <CheckCircle2 size={18} className="text-accent2 shrink-0" />
                    ) : (
                      <XCircle size={18} className="text-danger shrink-0" />
                    )}
                    <div>
                      <p className="text-sm font-semibold text-white">{r.skill}</p>
                      <p className="text-xs text-white/40">
                        {r.current_mastery} / {r.required_mastery} Mastery · Demand {r.demand_pct}%
                      </p>
                    </div>
                  </div>
                  <Badge className={r.is_met ? 'bg-accent2/10 text-accent2 border-accent2/20' : 'bg-danger/10 text-danger border-danger/20'}>
                    {r.is_met ? 'Target Met' : 'Gap Detected'}
                  </Badge>
                </div>
                {/* Progress bar */}
                <div className="h-1.5 bg-white/5 rounded-full overflow-hidden mt-1">
                  <div
                    className={`h-full ${r.is_met ? 'bg-accent2' : 'bg-warn'}`}
                    style={{ width: `${Math.min(100, (r.current_mastery / r.required_mastery) * 100)}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      ) : null}
    </div>
  );
}
