import { useEffect, useState } from 'react';
import { FlaskConical, Sparkles, Loader2, RotateCcw, Plus, ArrowRight } from 'lucide-react';
import { useCandidate } from '../state/CandidateContext';
import { useApi } from '../lib/useApi';
import { api, ApiError } from '../lib/api';
import { Spinner, ErrorBanner, SectionTitle, Badge } from '../components/Primitives';
import { scoreColor } from '../lib/utils';
import type { SimulationResponse } from '../types/api';

const STANDARD_ROLE_SKILLS: Record<string, string[]> = {
  'DevOps Engineer': ['Linux', 'Networking', 'Docker', 'Kubernetes', 'CI/CD', 'Cloud/AWS'],
  'Backend Engineer': ['Python', 'Data Structures & Algorithms', 'SQL & Databases', 'API Design & REST', 'System Design'],
  'Frontend Engineer': ['React', 'TypeScript', 'JavaScript', 'HTML/CSS', 'Web Performance & Testing'],
  'Full Stack Developer': ['React', 'TypeScript', 'Node.js', 'SQL & Databases', 'REST APIs', 'Docker'],
  'Cloud Solutions Architect': ['Cloud Architecture', 'Networking', 'Security & IAM', 'DevOps & IaC', 'Cost Optimization'],
  'Data Engineer': ['Python', 'SQL & Databases', 'Data Pipelines', 'Big Data & Spark', 'Cloud Warehousing'],
  'Machine Learning Engineer': ['Python', 'Machine Learning', 'Data Structures & Algorithms', 'MLOps & Deployment', 'Deep Learning'],
  'Site Reliability Engineer': ['Linux', 'Networking', 'Kubernetes', 'Monitoring & Observability', 'Incident Management'],
  'Security Engineer': ['Security & IAM', 'Networking', 'Application Security', 'Vulnerability Assessment', 'Cryptography'],
  'Software Engineer': ['Data Structures & Algorithms', 'System Design', 'Testing & CI/CD', 'API Design & REST', 'SQL & Databases'],
};

export function Simulator() {
  const { candidateId, candidate } = useCandidate();
  const twin = useApi(() => api.getCareerTwin(candidateId), [candidateId]);

  const [sliderValues, setSliderValues] = useState<Record<string, number>>({});
  const [newSkillName, setNewSkillName] = useState('');
  const [result, setResult] = useState<SimulationResponse | null>(null);
  const [simLoading, setSimLoading] = useState(false);
  const [simError, setSimError] = useState<string | null>(null);

  useEffect(() => {
    if (twin.data) {
      const initial: Record<string, number> = { ...twin.data.skills };
      // Include any standard skills for target role that candidate doesn't have yet, starting at 0
      const roleSkills = STANDARD_ROLE_SKILLS[twin.data.target_role] || STANDARD_ROLE_SKILLS['Full Stack Developer'];
      roleSkills.forEach((sk) => {
        if (!(sk in initial)) {
          initial[sk] = 0;
        }
      });
      setSliderValues(initial);
      setResult(null);
    }
  }, [twin.data]);

  if (twin.loading) return <Spinner label="Loading candidate skill profile…" />;
  if (twin.error) return <ErrorBanner message={twin.error} onRetry={twin.refetch} />;
  if (!twin.data) return null;

  const baseline = twin.data.skills;
  const changedSkills = Object.entries(sliderValues).filter(([skill, val]) => val !== (baseline[skill] ?? 0));

  async function runSimulation() {
    setSimLoading(true);
    setSimError(null);
    try {
      const hypothetical = Object.fromEntries(changedSkills);
      // Pass changed skills or slider values
      const payload = Object.keys(hypothetical).length > 0 ? hypothetical : sliderValues;
      const res = await api.simulate(candidateId, payload);
      setResult(res);

      // Save to sessionStorage for Reality Check tab integration
      try {
        sessionStorage.setItem(`what_if_${candidateId}`, JSON.stringify(sliderValues));
      } catch {
        // ignore
      }
    } catch (e) {
      setSimError(e instanceof ApiError ? e.message : 'Simulation failed.');
    } finally {
      setSimLoading(false);
    }
  }

  function reset() {
    if (twin.data) {
      const initial: Record<string, number> = { ...twin.data.skills };
      const roleSkills = STANDARD_ROLE_SKILLS[twin.data.target_role] || STANDARD_ROLE_SKILLS['Full Stack Developer'];
      roleSkills.forEach((sk) => {
        if (!(sk in initial)) {
          initial[sk] = 0;
        }
      });
      setSliderValues(initial);
      setResult(null);
      try {
        sessionStorage.removeItem(`what_if_${candidateId}`);
      } catch {
        // ignore
      }
    }
  }

  function addCustomSkill() {
    if (!newSkillName.trim()) return;
    setSliderValues({ ...sliderValues, [newSkillName.trim()]: 50 });
    setNewSkillName('');
  }

  return (
    <div className="fade-up space-y-6">
      <div className="flex items-start justify-between flex-wrap gap-3">
        <SectionTitle
          icon={<FlaskConical size={20} />}
          title="What-If Career Simulator"
          subtitle={`Simulate skill upgrades and see immediate impact on readiness score for ${candidate.name} without mutating the database`}
        />
        <button
          onClick={reset}
          className="flex items-center gap-1.5 text-xs font-medium px-3 py-1.5 rounded-lg bg-white/5 hover:bg-white/10 transition-colors text-white/60"
        >
          <RotateCcw size={13} /> Reset to baseline
        </button>
      </div>

      {/* Delta Banner if simulation executed */}
      {result && (
        <div className="card p-6 bg-gradient-to-br from-accent/10 to-accent2/10 border-accent/30 fade-up">
          <div className="flex items-center justify-between flex-wrap gap-4">
            <div>
              <p className="text-xs uppercase tracking-wider text-accent font-semibold">Simulated Readiness Uplift</p>
              <div className="flex items-baseline gap-3 mt-1">
                <span className="text-4xl font-extrabold text-white">{result.simulated_score}/100</span>
                <span className="text-lg font-bold text-accent2">+{result.delta} points</span>
                <span className="text-xs text-white/40">from baseline {result.current_score}</span>
              </div>
              <p className="text-xs text-white/60 mt-1">
                Upgrading {result.newly_improved_skills.length} skill(s) bridges foundational deficits toward {candidate.role}.
              </p>
            </div>
            {result.recommended_next_skill && (
              <div className="bg-white/[0.03] border border-white/10 rounded-xl p-3.5">
                <p className="text-[10px] uppercase text-white/40 font-semibold">Recommended Next High-Impact Skill</p>
                <p className="text-sm font-bold text-accent mt-0.5">{result.recommended_next_skill}</p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Sliders Grid */}
      <div className="card p-6 space-y-5">
        <div className="flex items-center justify-between flex-wrap gap-2">
          <h3 className="text-sm font-semibold text-white/90">
            Hypothetical Skill Sliders ({Object.keys(sliderValues).length} Available)
          </h3>
          <span className="text-xs text-accent font-medium">
            {changedSkills.length} modified from baseline
          </span>
        </div>

        <div className="grid md:grid-cols-2 gap-5">
          {Object.entries(sliderValues).map(([skill, val]) => {
            const baseVal = baseline[skill] ?? 0;
            const diff = val - baseVal;
            return (
              <div key={skill} className="p-3.5 rounded-xl bg-white/[0.02] border border-white/5 space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium text-white">{skill}</span>
                  <div className="flex items-center gap-2">
                    <span className="text-xs text-white/40">Baseline: {baseVal}</span>
                    <span className={`text-sm font-bold ${scoreColor(val)}`}>{val}</span>
                    {diff !== 0 && (
                      <span className={`text-xs font-semibold ${diff > 0 ? 'text-accent2' : 'text-danger'}`}>
                        {diff > 0 ? `+${diff}` : diff}
                      </span>
                    )}
                  </div>
                </div>
                <input
                  type="range"
                  min={0}
                  max={100}
                  value={val}
                  onChange={(e) => setSliderValues({ ...sliderValues, [skill]: Number(e.target.value) })}
                  className="w-full accent-accent cursor-pointer"
                />
              </div>
            );
          })}
        </div>

        {/* Add custom skill input */}
        <div className="pt-3 border-t border-white/5 flex items-center gap-3">
          <input
            value={newSkillName}
            onChange={(e) => setNewSkillName(e.target.value)}
            placeholder="Add another skill to simulate (e.g. Terraform, GraphQL)..."
            className="flex-1 bg-white/5 border border-white/10 rounded-xl px-3 py-2 text-xs text-white placeholder:text-white/25 focus:outline-none focus:border-accent"
          />
          <button
            onClick={addCustomSkill}
            className="flex items-center gap-1.5 text-xs font-semibold px-3 py-2 rounded-xl bg-white/10 hover:bg-white/15 text-white transition-colors"
          >
            <Plus size={14} /> Add Slider
          </button>
        </div>

        {simError && <p className="text-xs text-danger">{simError}</p>}

        <div className="pt-2 flex justify-end">
          <button
            onClick={runSimulation}
            disabled={simLoading}
            className="flex items-center gap-2 bg-accent hover:bg-accent/90 disabled:opacity-60 text-ink font-semibold text-sm px-6 py-2.5 rounded-xl transition-colors shadow-glow"
          >
            {simLoading ? <Loader2 size={16} className="animate-spin" /> : <Sparkles size={16} />}
            Simulate Career Readiness Impact
          </button>
        </div>
      </div>
    </div>
  );
}
