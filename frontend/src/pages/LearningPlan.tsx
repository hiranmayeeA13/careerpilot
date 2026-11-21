import { useState } from 'react';
import { CalendarDays, RefreshCw, CheckCircle2, Circle, Clock, Award, BookOpen } from 'lucide-react';
import { useCandidate } from '../state/CandidateContext';
import { useApi } from '../lib/useApi';
import { api } from '../lib/api';
import { Spinner, ErrorBanner, SectionTitle, Badge } from '../components/Primitives';

export function LearningPlan() {
  const { candidateId, candidate } = useCandidate();
  const { data, loading, error, refetch } = useApi(() => api.getLearningPlan(candidateId), [candidateId]);
  const [regenLoading, setRegenLoading] = useState(false);
  const [completedTasks, setCompletedTasks] = useState<Record<string, boolean>>({});
  const [syncingSkill, setSyncingSkill] = useState<string | null>(null);
  const [syncSuccessMsg, setSyncSuccessMsg] = useState<string | null>(null);

  async function regenerate() {
    setRegenLoading(true);
    try {
      await api.regenerateLearningPlan(candidateId);
      refetch();
    } finally {
      setRegenLoading(false);
    }
  }

  function toggleTask(taskId: string) {
    setCompletedTasks((prev) => ({ ...prev, [taskId]: !prev[taskId] }));
  }

  async function syncProgressToTwin(skillName: string, weekNum: number) {
    setSyncingSkill(skillName);
    setSyncSuccessMsg(null);
    try {
      await api.updateCareerTwin(candidateId, 'learning_task_completed', {
        skill_name: skillName,
        week: weekNum,
        points: 5,
      });
      setSyncSuccessMsg(`✓ Logged +5 mastery points for ${skillName} in ${candidate.name}'s Career Twin!`);
    } catch {
      // ignore
    } finally {
      setSyncingSkill(null);
    }
  }

  if (loading) return <Spinner label="Generating week-by-week plan…" />;
  if (error) return <ErrorBanner message={error} onRetry={refetch} />;
  if (!data) return null;

  // Compute total tasks and progress
  let totalTasks = 0;
  data.weeks.forEach((w) => {
    totalTasks += (w.tasks || []).length;
  });
  const finishedTasksCount = Object.values(completedTasks).filter(Boolean).length;
  const progressPct = totalTasks > 0 ? Math.round((finishedTasksCount / totalTasks) * 100) : 0;
  const estimatedHoursInvested = finishedTasksCount * 4;

  return (
    <div className="fade-up space-y-6">
      <div className="flex items-start justify-between flex-wrap gap-3">
        <SectionTitle
          icon={<CalendarDays size={20} />}
          title="Interactive Week-by-Week Learning Plan"
          subtitle={`${data.total_weeks}-week curriculum for ${candidate.name} toward ${data.target_role}`}
        />
        <button
          onClick={regenerate}
          disabled={regenLoading}
          className="flex items-center gap-1.5 text-xs font-semibold px-3 py-1.5 rounded-lg bg-accent/20 hover:bg-accent/30 text-accent border border-accent/30 transition-colors"
        >
          <RefreshCw size={13} className={regenLoading ? 'animate-spin' : ''} /> Regenerate from current gaps
        </button>
      </div>

      {/* Progress & stats dashboard */}
      <div className="card p-5 grid sm:grid-cols-3 gap-4 border-accent/20">
        <div>
          <p className="text-[10px] uppercase text-white/40 font-semibold">Curriculum Completion</p>
          <div className="flex items-baseline gap-2 mt-1">
            <span className="text-2xl font-bold text-accent2">{progressPct}%</span>
            <span className="text-xs text-white/50">
              ({finishedTasksCount} / {totalTasks} tasks)
            </span>
          </div>
          <div className="h-1.5 bg-white/5 rounded-full overflow-hidden mt-2">
            <div className="h-full bg-accent2 transition-all duration-300" style={{ width: `${progressPct}%` }} />
          </div>
        </div>

        <div>
          <p className="text-[10px] uppercase text-white/40 font-semibold">Study Hours Invested</p>
          <div className="flex items-baseline gap-2 mt-1">
            <span className="text-2xl font-bold text-accent">{estimatedHoursInvested} hrs</span>
            <span className="text-xs text-white/50">logged</span>
          </div>
          <p className="text-[11px] text-white/40 mt-1">~4 hours per practical task</p>
        </div>

        <div>
          <p className="text-[10px] uppercase text-white/40 font-semibold">Plan Generation Source</p>
          <Badge
            className={`mt-1.5 ${
              data.source === 'real_job_postings'
                ? 'bg-accent2/15 text-accent2 border-accent2/25'
                : 'bg-white/5 text-white/60 border-white/10'
            }`}
          >
            {data.source === 'real_job_postings' ? 'Real Job Descriptions' : 'Role Competency Benchmark'}
          </Badge>
          <p className="text-[11px] text-white/40 mt-1">{data.adjustment_note}</p>
        </div>
      </div>

      {syncSuccessMsg && (
        <div className="p-3 rounded-xl bg-accent2/10 border border-accent2/25 text-xs text-accent2 font-medium">
          {syncSuccessMsg}
        </div>
      )}

      {/* Weeks Timeline */}
      <div className="relative pl-6 space-y-5">
        <div className="absolute left-[9px] top-2 bottom-2 w-px bg-white/10" />
        {data.weeks.map((w) => {
          const primarySkill = w.focus_skills[0] || 'Foundational Skill';
          return (
            <div key={w.week} className="relative card p-5 space-y-3">
              <div className="absolute -left-[29px] top-5 w-4 h-4 rounded-full bg-accent/20 border-2 border-accent flex items-center justify-center" />
              <div className="flex items-start justify-between flex-wrap gap-2">
                <div>
                  <span className="text-xs font-bold text-accent uppercase tracking-wider">Week {w.week}</span>
                  <h4 className="text-base font-bold text-white mt-0.5">{w.focus_skills.join(', ')}</h4>
                  <p className="text-xs text-white/50 mt-1">
                    Focus: <span className="text-white/80 font-medium">{primarySkill}</span> · ~{w.hours_allocated} hours recommended
                  </p>
                </div>

                <button
                  onClick={() => syncProgressToTwin(primarySkill, w.week)}
                  disabled={syncingSkill === primarySkill}
                  className="flex items-center gap-1.5 text-xs font-semibold px-3 py-1.5 rounded-lg bg-white/5 hover:bg-white/10 border border-white/10 text-white/80 transition-colors"
                >
                  <Award size={13} className="text-accent2" />
                  {syncingSkill === primarySkill ? 'Logging…' : 'Log Skill Progress (+5)'}
                </button>
              </div>

              {/* Checkable Milestones */}
              <div className="space-y-2 pt-2 border-t border-white/5">
                <p className="text-[11px] uppercase tracking-wider text-white/40 font-semibold">Weekly Action Items:</p>
                {(w.tasks || []).map((m, idx) => {
                  const taskId = `w${w.week}_m${idx}`;
                  const isChecked = !!completedTasks[taskId];
                  return (
                    <div
                      key={idx}
                      onClick={() => toggleTask(taskId)}
                      className={`p-2.5 rounded-lg border transition-all cursor-pointer flex items-center gap-2.5 ${
                        isChecked
                          ? 'bg-accent2/[0.06] border-accent2/25 text-white/90'
                          : 'bg-white/[0.02] border-white/5 hover:border-white/10 text-white/70'
                      }`}
                    >
                      {isChecked ? (
                        <CheckCircle2 size={16} className="text-accent2 shrink-0" />
                      ) : (
                        <Circle size={16} className="text-white/30 shrink-0" />
                      )}
                      <span className={`text-xs ${isChecked ? 'line-through text-white/45' : 'text-white/85'}`}>{m}</span>
                    </div>
                  );
                })}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
