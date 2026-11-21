import { useState } from 'react';
import { UserCircle2, Target, Clock, BookOpen, FolderCheck, Mic, Plus, CheckCircle2, ShieldCheck } from 'lucide-react';
import { Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer } from 'recharts';
import { useCandidate } from '../state/CandidateContext';
import { useApi } from '../lib/useApi';
import { api } from '../lib/api';
import { Spinner, ErrorBanner, SectionTitle, Badge } from '../components/Primitives';
import { evidenceColor } from '../lib/utils';

export function CareerTwin() {
  const { candidateId } = useCandidate();
  const { data, loading, error, refetch } = useApi(() => api.getCareerTwin(candidateId), [candidateId]);
  const [newGoal, setNewGoal] = useState('');
  const [addingGoal, setAddingGoal] = useState(false);

  if (loading) return <Spinner label="Syncing career twin…" />;
  if (error) return <ErrorBanner message={error} onRetry={refetch} />;
  if (!data) return null;

  // Build radar data: ensure at least 3 axes so polygon renders properly even for new candidates
  const skillEntries = Object.entries(data.skills);
  let radarData = skillEntries.map(([skill, mastery]) => ({ skill, mastery }));

  if (radarData.length < 3) {
    const fallbacks = ['System Architecture', 'Core Problem Solving', 'Code Quality & Testing'];
    fallbacks.forEach((f) => {
      if (!radarData.some((d) => d.skill === f)) {
        radarData.push({ skill: f, mastery: 30 });
      }
    });
    radarData = radarData.slice(0, 4);
  }

  async function handleAddGoal() {
    if (!newGoal.trim() || !data) return;
    setAddingGoal(true);
    try {
      const updatedGoals = [...data.goals, newGoal.trim()];
      await api.saveCandidateProfile({
        ...data,
        goals: updatedGoals,
      } as any);
      setNewGoal('');
      refetch();
    } catch {
      // ignore
    } finally {
      setAddingGoal(false);
    }
  }

  return (
    <div className="fade-up space-y-6">
      <SectionTitle
        icon={<UserCircle2 size={20} />}
        title="Persistent Career Twin"
        subtitle={`${data.name} — ${data.target_role}`}
      />

      {data.twin_summary && (
        <div className="card p-5 bg-gradient-to-br from-accent/10 to-accent2/5 border-accent/20">
          <p className="text-xs uppercase tracking-wider text-white/40 font-semibold mb-2">Twin Synthesis Summary</p>
          <p className="text-sm text-white/85 leading-relaxed">{data.twin_summary}</p>
        </div>
      )}

      <div className="grid lg:grid-cols-2 gap-5">
        {/* Radar Chart */}
        <div className="card p-5">
          <div className="flex items-center justify-between mb-2">
            <p className="text-sm font-semibold text-white/80">Skill Mastery Radar</p>
            <span className="text-xs text-white/40">{Object.keys(data.skills).length} Active Skills</span>
          </div>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <RadarChart data={radarData} outerRadius="75%">
                <PolarGrid stroke="rgba(255,255,255,0.08)" />
                <PolarAngleAxis dataKey="skill" tick={{ fill: '#b8c0ea', fontSize: 11 }} />
                <PolarRadiusAxis domain={[0, 100]} tick={{ fill: 'rgba(255,255,255,0.2)', fontSize: 10 }} />
                <Radar dataKey="mastery" stroke="#6c8cff" fill="#6c8cff" fillOpacity={0.35} />
              </RadarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Goals & Preferences */}
        <div className="card p-5 space-y-5">
          <div>
            <div className="flex items-center justify-between mb-2.5">
              <div className="flex items-center gap-2 text-accent">
                <Target size={16} />
                <p className="text-sm font-semibold">Career Goals</p>
              </div>
              <span className="text-xs text-white/40">{data.goals.length} Recorded</span>
            </div>
            <ul className="space-y-2">
              {data.goals.map((g, i) => (
                <li key={i} className="text-xs text-white/80 flex items-start gap-2 bg-white/[0.02] p-2.5 rounded-lg border border-white/5">
                  <span className="text-accent mt-0.5">▸</span>
                  <span>{g}</span>
                </li>
              ))}
            </ul>

            {/* Inline add goal */}
            <div className="mt-3 flex gap-2">
              <input
                value={newGoal}
                onChange={(e) => setNewGoal(e.target.value)}
                placeholder="Add a new career goal..."
                className="flex-1 bg-white/5 border border-white/10 rounded-lg px-3 py-1.5 text-xs text-white placeholder:text-white/25 focus:outline-none focus:border-accent"
              />
              <button
                onClick={handleAddGoal}
                disabled={addingGoal}
                className="px-3 py-1.5 rounded-lg bg-accent/20 hover:bg-accent/30 text-accent text-xs font-semibold flex items-center gap-1 transition-colors"
              >
                <Plus size={13} /> {addingGoal ? 'Saving…' : 'Add'}
              </button>
            </div>
          </div>

          <div className="pt-3 border-t border-white/5">
            <div className="flex items-center gap-2 text-accent2 mb-2">
              <Clock size={16} />
              <p className="text-sm font-semibold">Learning Preferences</p>
            </div>
            <div className="grid grid-cols-2 gap-2 text-xs">
              <div className="bg-white/[0.02] p-2.5 rounded-lg border border-white/5">
                <span className="text-white/40 block text-[10px] uppercase">Format</span>
                <span className="text-white font-medium capitalize mt-0.5 block">{String(data.learning_preferences.preferred_format || 'Hands-on projects')}</span>
              </div>
              <div className="bg-white/[0.02] p-2.5 rounded-lg border border-white/5">
                <span className="text-white/40 block text-[10px] uppercase">Weekly Commitment</span>
                <span className="text-white font-medium mt-0.5 block">{String(data.learning_preferences.weekly_hours || 10)} hrs / week</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Skills & Evidence Breakdown */}
      <div className="card p-5">
        <h3 className="text-sm font-semibold text-white/80 mb-3 flex items-center gap-2">
          <ShieldCheck size={16} className="text-accent2" />
          Verified Skills & Evidence Inventory
        </h3>
        <div className="grid sm:grid-cols-2 md:grid-cols-3 gap-3">
          {Object.entries(data.skills)
            .sort((a, b) => b[1] - a[1])
            .map(([skill, mastery]) => {
              const ev = data.skill_evidence[skill];
              const status = ev?.status || 'Unverified';
              return (
                <div key={skill} className="rounded-xl bg-white/[0.02] border border-white/5 p-3.5 space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-white">{skill}</span>
                    <span className="text-xs font-bold text-accent">{mastery}/100</span>
                  </div>
                  <div className="h-1.5 bg-white/5 rounded-full overflow-hidden">
                    <div className="h-full bg-accent rounded-full" style={{ width: `${mastery}%` }} />
                  </div>
                  <div className="flex items-center justify-between pt-1">
                    <span className="text-[10px] text-white/40">Evidence Status:</span>
                    <Badge className={`text-[10px] ${evidenceColor(status)}`}>{status}</Badge>
                  </div>
                </div>
              );
            })}
        </div>
      </div>

      {/* Completed Projects & Interviews */}
      <div className="grid md:grid-cols-2 gap-5">
        <div className="card p-5 space-y-3">
          <div className="flex items-center gap-2 text-white/80">
            <FolderCheck size={16} className="text-accent" />
            <h4 className="text-sm font-semibold">Completed Projects ({data.completed_projects.length})</h4>
          </div>
          {data.completed_projects.length > 0 ? (
            <div className="space-y-2.5">
              {data.completed_projects.map((p) => (
                <div key={p.id} className="p-3 rounded-lg bg-white/[0.02] border border-white/5">
                  <p className="text-xs font-bold text-white">{p.title}</p>
                  <p className="text-[11px] text-white/50 mt-0.5">{p.description}</p>
                  <p className="text-[10px] text-accent2 mt-1">Evaluation Score: {p.evaluation_score ?? '80'}/100</p>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-xs text-white/45 italic">No completed projects on record yet. Build a recommended project to unlock verified evidence.</p>
          )}
        </div>

        <div className="card p-5 space-y-3">
          <div className="flex items-center gap-2 text-white/80">
            <Mic size={16} className="text-accent2" />
            <h4 className="text-sm font-semibold">Interview History ({data.interview_history.length})</h4>
          </div>
          {data.interview_history.length > 0 ? (
            <div className="space-y-2.5">
              {data.interview_history.map((i) => (
                <div key={i.id} className="p-3 rounded-lg bg-white/[0.02] border border-white/5">
                  <div className="flex justify-between items-center">
                    <span className="text-xs font-bold text-white">{i.target_role}</span>
                    <span className="text-xs font-bold text-accent2">{i.performance_score}/100</span>
                  </div>
                  <p className="text-[11px] text-white/50 mt-1">{i.feedback}</p>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-xs text-white/45 italic">No technical interviews completed yet. Complete a mock interview to establish verified depth.</p>
          )}
        </div>
      </div>
    </div>
  );
}
