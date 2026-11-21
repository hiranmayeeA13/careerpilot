import { useState, useEffect } from 'react';
import { FolderGit2, Wrench, ListChecks, Sparkles, RefreshCw, CheckCircle2, Copy, Check } from 'lucide-react';
import { useCandidate } from '../state/CandidateContext';
import { api, ApiError } from '../lib/api';
import { Spinner, ErrorBanner, SectionTitle, Badge } from '../components/Primitives';
import type { PortfolioProjectResponse } from '../types/api';

export function Portfolio() {
  const { candidateId, candidate } = useCandidate();
  const [data, setData] = useState<PortfolioProjectResponse | null>(null);
  const [variationIndex, setVariationIndex] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Interactive milestone check-off state
  const [checkedMilestones, setCheckedMilestones] = useState<Record<number, boolean>>({});
  const [recording, setRecording] = useState(false);
  const [recordSuccess, setRecordSuccess] = useState(false);
  const [copied, setCopied] = useState(false);

  async function load(indexToLoad: number = variationIndex) {
    setLoading(true);
    setError(null);
    setRecordSuccess(false);
    setCheckedMilestones({});
    try {
      const res = await api.recommendPortfolio(candidateId, indexToLoad);
      setData(res);
    } catch (e) {
      setError(e instanceof ApiError ? e.message : 'Could not generate a recommendation.');
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load(0);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [candidateId]);

  function handleNextSuggestion() {
    const nextIdx = variationIndex + 1;
    setVariationIndex(nextIdx);
    load(nextIdx);
  }

  function toggleMilestone(step: number) {
    setCheckedMilestones((prev) => ({ ...prev, [step]: !prev[step] }));
  }

  async function handleRecordToTwin() {
    if (!data) return;
    setRecording(true);
    try {
      await api.updateCareerTwin(candidateId, 'project_completed', {
        title: data.title,
        description: data.problem_statement,
        skills_demonstrated: data.skills_demonstrated,
        evaluation_score: 88,
      });
      setRecordSuccess(true);
    } catch (e: any) {
      setError(e?.message || 'Could not record project to Career Twin.');
    } finally {
      setRecording(false);
    }
  }

  function copyBrief() {
    if (!data) return;
    const text = `${data.title}\n\nProblem:\n${data.problem_statement}\n\nRequired Tools:\n${data.required_tools.join(', ')}\n\nMilestones:\n${data.milestones.map((m) => `${m.step}. ${m.name}: ${m.deliverable}`).join('\n')}`;
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }

  if (loading) return <Spinner label="Generating targeted portfolio project..." />;
  if (error) return <ErrorBanner message={error} onRetry={() => load(variationIndex)} />;
  if (!data) return null;

  const totalSteps = data.milestones.length;
  const completedSteps = Object.values(checkedMilestones).filter(Boolean).length;
  const progressPct = totalSteps > 0 ? Math.round((completedSteps / totalSteps) * 100) : 0;

  return (
    <div className="fade-up space-y-6 max-w-5xl">
      <div className="flex items-start justify-between flex-wrap gap-3">
        <SectionTitle
          icon={<FolderGit2 size={20} />}
          title="Portfolio Generator"
          subtitle={`Interactive project briefs targeting verified skill gaps for ${candidate.name}`}
        />
        <div className="flex items-center gap-2">
          <button
            onClick={copyBrief}
            className="flex items-center gap-1.5 text-xs font-medium px-3 py-1.5 rounded-xl border border-white/10 bg-white/5 hover:bg-white/10 transition-colors text-white/80"
          >
            {copied ? <Check size={13} className="text-accent2" /> : <Copy size={13} />}
            {copied ? 'Copied' : 'Copy Brief'}
          </button>
          <button
            onClick={handleNextSuggestion}
            className="flex items-center gap-1.5 text-xs font-semibold px-3 py-1.5 rounded-xl bg-accent text-ink hover:bg-accent/90 transition-colors shadow-glow"
          >
            <RefreshCw size={13} />
            New Suggestion
          </button>
        </div>
      </div>

      {/* Main Project Card */}
      <div className="card p-6 space-y-4">
        <div className="flex items-start justify-between gap-4">
          <div>
            <h3 className="text-xl font-bold text-white">{data.title}</h3>
            <p className="text-sm text-white/70 mt-1.5 leading-relaxed">{data.problem_statement}</p>
          </div>
          <Badge className="bg-accent/15 text-accent border-accent/30 shrink-0 font-semibold">{data.difficulty}</Badge>
        </div>

        {/* Combined Skills & Tech Stack */}
        <div className="pt-2 border-t border-white/5 flex flex-wrap items-center gap-2">
          <span className="text-xs text-white/40 font-medium">Demonstrates:</span>
          {data.skills_demonstrated.map((s) => (
            <Badge key={s} className="bg-accent2/15 text-accent2 border-accent2/30 text-xs font-medium">
              {s}
            </Badge>
          ))}
          <span className="text-white/20 mx-1">·</span>
          <span className="text-xs text-white/40 font-medium">Tech Stack:</span>
          {data.required_tools.map((t) => (
            <Badge key={t} className="bg-white/5 text-white/80 border-white/10 text-xs">
              {t}
            </Badge>
          ))}
        </div>
      </div>

      {/* Interactive Milestones */}
      <div className="card p-6 space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <ListChecks size={18} className="text-accent" />
            <h4 className="text-sm font-semibold text-white">Project Build Milestones</h4>
          </div>
          <span className="text-xs text-accent2 font-semibold">
            {completedSteps} / {totalSteps} Completed ({progressPct}%)
          </span>
        </div>

        {/* Progress bar */}
        <div className="h-1.5 bg-white/5 rounded-full overflow-hidden">
          <div className="h-full bg-accent2 transition-all duration-300" style={{ width: `${progressPct}%` }} />
        </div>

        <div className="space-y-2.5 pt-1">
          {data.milestones.map((m) => {
            const isDone = !!checkedMilestones[m.step];
            return (
              <div
                key={m.step}
                onClick={() => toggleMilestone(m.step)}
                className={`p-3.5 rounded-xl border transition-all cursor-pointer flex items-start gap-3 ${
                  isDone
                    ? 'bg-accent2/[0.08] border-accent2/30 text-white'
                    : 'bg-white/[0.02] border-white/5 hover:border-white/10 text-white/80'
                }`}
              >
                <div className="mt-0.5 shrink-0">
                  {isDone ? (
                    <CheckCircle2 size={18} className="text-accent2" />
                  ) : (
                    <div className="w-4 h-4 rounded-full border border-white/30 flex items-center justify-center text-[10px] text-white/40 font-semibold">
                      {m.step}
                    </div>
                  )}
                </div>
                <div>
                  <p className={`text-sm font-semibold ${isDone ? 'line-through text-white/50' : 'text-white'}`}>
                    {m.name}
                  </p>
                  <p className="text-xs text-white/50 mt-0.5 leading-relaxed">{m.deliverable}</p>
                </div>
              </div>
            );
          })}
        </div>

        {/* Action to log into Career Twin */}
        <div className="pt-3 border-t border-white/5 flex items-center justify-between flex-wrap gap-3">
          <div>
            {recordSuccess ? (
              <p className="text-xs text-accent2 font-medium">
                ✓ Recorded this completed project into {candidate.name}&apos;s Career Twin profile!
              </p>
            ) : (
              <p className="text-xs text-white/40">
                Check off milestone steps as you build, then save to your Career Twin.
              </p>
            )}
          </div>
          <button
            onClick={handleRecordToTwin}
            disabled={recording || recordSuccess}
            className="bg-accent hover:bg-accent/90 disabled:opacity-50 text-ink font-semibold text-xs px-4 py-2 rounded-xl transition-colors shadow-glow flex items-center gap-1.5"
          >
            {recording ? 'Recording...' : recordSuccess ? '✓ Recorded to Career Twin' : 'Record in Career Twin'}
          </button>
        </div>
      </div>
    </div>
  );
}
