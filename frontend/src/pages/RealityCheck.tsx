import { useState, useEffect } from 'react';
import { Compass, CheckCircle2, XCircle, Flag, ListChecks, ToggleLeft, ToggleRight, Clock, AlertTriangle } from 'lucide-react';
import { useCandidate } from '../state/CandidateContext';
import { api, ApiError } from '../lib/api';
import { Spinner, ErrorBanner, SectionTitle, Badge } from '../components/Primitives';
import type { RealityCheckResponse } from '../types/api';

const TARGET_ROLE_OPTIONS = [
  'DevOps Engineer',
  'Backend Engineer',
  'Frontend Engineer',
  'Full Stack Developer',
  'Cloud Solutions Architect',
  'Data Engineer',
  'Machine Learning Engineer',
  'Site Reliability Engineer',
  'Security Engineer',
  'Software Engineer',
];

export function RealityCheck() {
  const { candidateId, candidate } = useCandidate();
  const [selectedRole, setSelectedRole] = useState(candidate.role);
  const [applySimulator, setApplySimulator] = useState(false);
  const [data, setData] = useState<RealityCheckResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Check if session has what-if simulator skills
  const [simulatedSkills, setSimulatedSkills] = useState<Record<string, number> | null>(null);

  useEffect(() => {
    try {
      const stored = sessionStorage.getItem(`what_if_${candidateId}`);
      if (stored) {
        setSimulatedSkills(JSON.parse(stored));
      }
    } catch {
      // ignore
    }
  }, [candidateId]);

  async function fetchRealityCheck() {
    setLoading(true);
    setError(null);
    try {
      const hypSkills = applySimulator && simulatedSkills ? simulatedSkills : undefined;
      const res = await api.realityCheck(candidateId, selectedRole, hypSkills);
      setData(res);
    } catch (e) {
      setError(e instanceof ApiError ? e.message : 'Could not run reality check.');
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    fetchRealityCheck();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [candidateId, selectedRole, applySimulator]);

  const metCount = data ? data.major_prerequisites.filter((p) => p.is_met).length : 0;
  const missingCount = data ? data.missing_foundations.length : 0;
  // Estimate time to readiness: ~3-4 weeks per missing foundation at 10 hrs/week
  const estimatedWeeks = Math.max(2, missingCount * 3 + (data && data.current_level === 'Beginner' ? 4 : 0));

  return (
    <div className="fade-up space-y-6">
      <div className="flex items-start justify-between flex-wrap gap-3">
        <SectionTitle
          icon={<Compass size={20} />}
          title="Career Reality Check"
          subtitle={`${candidate.name} vs. ${selectedRole} — honest prerequisite analysis and preparation sequence`}
        />

        {/* What-If Simulator Skills Toggle */}
        {simulatedSkills && Object.keys(simulatedSkills).length > 0 && (
          <button
            onClick={() => setApplySimulator(!applySimulator)}
            className={`flex items-center gap-2 text-xs font-semibold px-3 py-1.5 rounded-lg border transition-all ${
              applySimulator
                ? 'bg-accent2/20 text-accent2 border-accent2/40'
                : 'bg-white/5 text-white/60 border-white/10 hover:border-white/20'
            }`}
          >
            {applySimulator ? <ToggleRight size={18} className="text-accent2" /> : <ToggleLeft size={18} />}
            Apply What-If Simulator Skills ({Object.keys(simulatedSkills).length} skills)
          </button>
        )}
      </div>

      {/* Role Switcher Toolbar */}
      <div className="card p-4 flex items-center justify-between flex-wrap gap-3 border-accent/20">
        <div className="flex items-center gap-2">
          <label className="text-xs text-white/50 font-medium">Evaluate Against Role:</label>
          <select
            value={selectedRole}
            onChange={(e) => setSelectedRole(e.target.value)}
            className="bg-white/5 border border-white/10 rounded-lg px-3 py-1.5 text-xs text-white focus:outline-none focus:border-accent"
          >
            {TARGET_ROLE_OPTIONS.map((r) => (
              <option key={r} value={r} className="bg-[#121833] text-white">
                {r}
              </option>
            ))}
          </select>
        </div>

        {applySimulator && (
          <Badge className="bg-accent2/15 text-accent2 border-accent2/30 text-xs">
            ✓ Incorporating What-If Simulator Skills
          </Badge>
        )}
      </div>

      {loading && <Spinner label="Evaluating career prerequisites and foundation gaps…" />}
      {error && <ErrorBanner message={error} onRetry={fetchRealityCheck} />}

      {!loading && data && (
        <>
          {/* Top KPI Summary */}
          <div className="grid sm:grid-cols-3 gap-4">
            <div className="card p-5">
              <p className="text-[10px] uppercase tracking-wider text-white/40 font-semibold">Current Assessment Level</p>
              <p className="text-xl font-bold text-white mt-1">{data.current_level}</p>
              <p className="text-xs text-white/45 mt-1">Based on verified foundational mastery</p>
            </div>

            <div className="card p-5">
              <p className="text-[10px] uppercase tracking-wider text-white/40 font-semibold">Prerequisites Satisfied</p>
              <p className="text-xl font-bold text-white mt-1">
                <span className="text-accent2">{metCount}</span>{' '}
                <span className="text-white/40 text-sm font-normal">/ {data.major_prerequisites.length} required</span>
              </p>
              <p className="text-xs text-white/45 mt-1">
                {missingCount === 0 ? 'All foundational prerequisites met!' : `${missingCount} critical gap(s) remaining`}
              </p>
            </div>

            <div className="card p-5 bg-gradient-to-br from-accent/10 to-transparent border-accent/20">
              <p className="text-[10px] uppercase tracking-wider text-accent font-semibold flex items-center gap-1">
                <Clock size={12} /> Estimated Time-to-Readiness
              </p>
              <p className="text-xl font-bold text-white mt-1">~{estimatedWeeks} Weeks</p>
              <p className="text-xs text-white/50 mt-1">At 10 hours/week structured study</p>
            </div>
          </div>

          {/* Missing Foundations Warning Banner */}
          {data.missing_foundations.length > 0 && (
            <div className="card p-4 flex items-start gap-3 bg-warn/10 border-warn/30">
              <AlertTriangle size={18} className="text-warn shrink-0 mt-0.5" />
              <div>
                <p className="text-xs font-bold text-warn uppercase tracking-wider">Critical Foundational Deficits</p>
                <p className="text-xs text-white/75 mt-0.5 leading-relaxed">
                  Before applying for {data.target_role}, the following foundational competencies must be verified:
                </p>
                <div className="flex flex-wrap gap-1.5 mt-2">
                  {data.missing_foundations.map((f) => (
                    <Badge key={f} className="bg-warn/15 text-warn border-warn/30 text-xs">
                      {f}
                    </Badge>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Major Prerequisites Table */}
          <div className="card p-5">
            <h4 className="text-sm font-semibold text-white/80 mb-3">Prerequisites & Evidence Breakdown</h4>
            <div className="space-y-3">
              {data.major_prerequisites.map((p) => (
                <div key={p.skill} className="border border-white/5 rounded-xl p-3.5 bg-white/[0.01]">
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex items-center gap-2.5">
                      {p.is_met ? (
                        <CheckCircle2 size={18} className="text-accent2 shrink-0" />
                      ) : (
                        <XCircle size={18} className="text-danger shrink-0" />
                      )}
                      <div>
                        <p className="text-sm font-semibold text-white">{p.skill}</p>
                        <p className="text-xs text-white/45 mt-0.5">
                          Current Mastery: <strong className="text-white/70">{p.current_mastery}</strong> / {p.required_mastery} required · Weight {p.importance_weight}
                        </p>
                      </div>
                    </div>
                    <Badge className={p.is_met ? 'bg-accent2/10 text-accent2 border-accent2/20' : 'bg-danger/10 text-danger border-danger/20'}>
                      {p.is_met ? 'Satisfied' : 'Deficit'}
                    </Badge>
                  </div>
                  <p className="text-xs text-white/60 mt-2 pl-7 leading-relaxed">{p.why_it_matters}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Ordered Preparation Sequence */}
          <div className="card p-5 space-y-3">
            <h4 className="text-sm font-semibold text-white/80 flex items-center gap-2">
              <ListChecks size={16} className="text-accent" />
              Recommended Preparation Sequence
            </h4>
            <p className="text-xs text-white/50">
              Address foundational skills before attempting advanced orchestration to build verified readiness systematically:
            </p>
            <div className="grid sm:grid-cols-2 gap-3 pt-1">
              {data.preparation_sequence.map((step, idx) => (
                <div key={idx} className="p-3 rounded-xl bg-white/[0.02] border border-white/5 flex items-start gap-2.5">
                  <span className="w-5 h-5 rounded-full bg-accent/20 text-accent text-xs font-bold flex items-center justify-center shrink-0">
                    {idx + 1}
                  </span>
                  <span className="text-xs text-white/80 font-medium leading-relaxed">{step}</span>
                </div>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  );
}
