import { Gauge, TrendingUp, TrendingDown, ArrowRight, Award, Sparkles, FolderGit2, Mic2, FlaskConical } from 'lucide-react';
import { RadialBarChart, RadialBar, PolarAngleAxis, BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import { useNavigate } from 'react-router-dom';
import { useCandidate } from '../state/CandidateContext';
import { useApi } from '../lib/useApi';
import { api } from '../lib/api';
import { Spinner, ErrorBanner, SectionTitle, Badge } from '../components/Primitives';
import { categoryColor, scoreColor } from '../lib/utils';

export function Dashboard() {
  const { candidateId, candidate } = useCandidate();
  const { data, loading, error, refetch } = useApi(() => api.getReadiness(candidateId), [candidateId]);
  const navigate = useNavigate();

  if (loading) return <Spinner label="Computing readiness score…" />;
  if (error) return <ErrorBanner message={error} onRetry={refetch} />;
  if (!data) return null;

  const breakdownData = [
    { name: 'Skills', value: data.breakdown.skills, weight: '40%' },
    { name: 'Interview', value: data.breakdown.interview, weight: '25%' },
    { name: 'Portfolio', value: data.breakdown.portfolio, weight: '20%' },
    { name: 'Evidence', value: data.breakdown.evidence, weight: '15%' },
  ];

  const gaugeData = [{ name: 'score', value: data.overall_score, fill: scoreColor(data.overall_score) }];

  // Tier logic
  const isJobReady = data.overall_score >= 75;
  const isDeveloping = data.overall_score >= 50 && data.overall_score < 75;
  const currentTier = isJobReady ? 'Tier 3 — Job-Ready Professional' : isDeveloping ? 'Tier 2 — Developing Specialist' : 'Tier 1 — Apprentice Engineer';
  const nextTarget = isJobReady ? 100 : isDeveloping ? 75 : 50;
  const pointsNeeded = Math.max(0, nextTarget - data.overall_score);
  const tierProgress = isJobReady
    ? 100
    : isDeveloping
    ? Math.round(((data.overall_score - 50) / 25) * 100)
    : Math.round((data.overall_score / 50) * 100);

  return (
    <div className="fade-up space-y-6">
      <SectionTitle
        icon={<Gauge size={20} />}
        title="Career Readiness Score"
        subtitle={`${candidate.name} · targeting ${candidate.role}`}
      />

      {/* Level Progression Banner */}
      <div className="card p-5 bg-gradient-to-r from-accent/15 via-[#1a1210] to-transparent border-accent/25">
        <div className="flex items-center justify-between flex-wrap gap-3">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-accent/20 flex items-center justify-center text-accent">
              <Award size={20} />
            </div>
            <div>
              <p className="text-[10px] uppercase font-bold tracking-wider text-accent">Engineering Level Progression</p>
              <h3 className="text-base font-bold text-white mt-0.5">{currentTier}</h3>
            </div>
          </div>
          <div className="text-right">
            <span className="text-xs text-white/50">
              {isJobReady ? 'Peak Tier Achieved' : `${pointsNeeded} points needed to reach ${isDeveloping ? 'Job-Ready' : 'Developing'}`}
            </span>
          </div>
        </div>
        <div className="h-2 bg-white/10 rounded-full overflow-hidden mt-3">
          <div className="h-full bg-gradient-to-r from-accent to-accent2 transition-all duration-500" style={{ width: `${tierProgress}%` }} />
        </div>
      </div>

      <div className="grid md:grid-cols-5 gap-5">
        {/* Gauge */}
        <div className="card p-6 md:col-span-2 flex flex-col items-center justify-center relative">
          <div className="w-52 h-52 relative">
            <ResponsiveContainer width="100%" height="100%">
              <RadialBarChart
                innerRadius="75%"
                outerRadius="100%"
                data={gaugeData}
                startAngle={90}
                endAngle={-270}
                barSize={14}
              >
                <PolarAngleAxis type="number" domain={[0, 100]} angleAxisId={0} tick={false} />
                <RadialBar background={{ fill: 'rgba(255,255,255,0.06)' }} dataKey="value" cornerRadius={10} />
              </RadialBarChart>
            </ResponsiveContainer>
            <div className="absolute inset-0 flex flex-col items-center justify-center">
              <p className="text-5xl font-extrabold text-white">{data.overall_score}</p>
              <p className="text-xs text-white/40 mt-1">out of 100</p>
            </div>
          </div>
          <Badge className={categoryColor(data.category) + ' mt-5 text-sm px-4 py-1.5'}>{data.category}</Badge>
        </div>

        {/* Breakdown bars */}
        <div className="card p-6 md:col-span-3">
          <p className="text-sm font-semibold text-white/80 mb-4">Four-Pillar Deterministic Breakdown</p>
          <div className="h-56">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={breakdownData} layout="vertical" margin={{ left: 10, right: 20 }}>
                <XAxis type="number" domain={[0, 100]} hide />
                <YAxis
                  type="category"
                  dataKey="name"
                  width={80}
                  tick={{ fill: '#b8c0ea', fontSize: 13 }}
                  axisLine={false}
                  tickLine={false}
                />
                <Tooltip
                  cursor={{ fill: 'rgba(255,255,255,0.04)' }}
                  contentStyle={{ background: '#171f42', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 10 }}
                  formatter={(v: number) => [`${v.toFixed(1)}`, 'Score']}
                />
                <Bar dataKey="value" radius={[0, 8, 8, 0]} barSize={22}>
                  {breakdownData.map((entry, i) => (
                    <Cell key={i} fill={scoreColor(entry.value)} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
          <div className="flex gap-3 mt-2 text-[11px] text-white/40 flex-wrap">
            {breakdownData.map((b) => (
              <span key={b.name} className="bg-white/[0.02] px-2 py-0.5 rounded border border-white/5">
                {b.name}: <strong className="text-white/70">{b.weight}</strong>
              </span>
            ))}
          </div>
        </div>
      </div>

      <div className="grid md:grid-cols-2 gap-5">
        <div className="card p-5 space-y-3">
          <div className="flex items-center gap-2 text-accent2">
            <TrendingUp size={17} />
            <p className="text-sm font-semibold">Verified Strengths & Positive Signals</p>
          </div>
          <ul className="space-y-2">
            {data.top_positive_factors.map((f, i) => (
              <li key={i} className="text-xs text-white/75 flex gap-2 bg-white/[0.02] p-2.5 rounded-lg border border-white/5">
                <span className="text-accent2 mt-0.5">▸</span>
                <span>{f}</span>
              </li>
            ))}
          </ul>
        </div>
        <div className="card p-5 space-y-3">
          <div className="flex items-center gap-2 text-danger">
            <TrendingDown size={17} />
            <p className="text-sm font-semibold">Priority Deficits & Growth Gaps</p>
          </div>
          <ul className="space-y-2">
            {data.top_negative_factors.map((f, i) => (
              <li key={i} className="text-xs text-white/75 flex gap-2 bg-white/[0.02] p-2.5 rounded-lg border border-white/5">
                <span className="text-danger mt-0.5">▸</span>
                <span>{f}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>

      {/* Recommended Next Action with Direct Shortcuts */}
      <div className="card p-5 bg-gradient-to-r from-accent/10 to-transparent border-accent/20 space-y-4">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-xl bg-accent/20 text-accent shrink-0">
            <ArrowRight size={18} />
          </div>
          <div>
            <p className="text-xs uppercase tracking-wider text-white/40 font-semibold">Recommended Immediate Action</p>
            <p className="text-sm text-white/90 font-medium mt-0.5">{data.recommended_next_action}</p>
          </div>
        </div>

        <div className="flex flex-wrap gap-2 pt-2 border-t border-white/5">
          <button
            onClick={() => navigate('/portfolio')}
            className="flex items-center gap-1.5 text-xs font-semibold px-3 py-1.5 rounded-lg bg-accent/20 hover:bg-accent/30 text-accent border border-accent/30 transition-colors"
          >
            <FolderGit2 size={13} /> Build Portfolio Project
          </button>
          <button
            onClick={() => navigate('/mock-interview')}
            className="flex items-center gap-1.5 text-xs font-semibold px-3 py-1.5 rounded-lg bg-accent2/20 hover:bg-accent2/30 text-accent2 border border-accent2/30 transition-colors"
          >
            <Mic2 size={13} /> Complete Technical Interview
          </button>
          <button
            onClick={() => navigate('/simulator')}
            className="flex items-center gap-1.5 text-xs font-semibold px-3 py-1.5 rounded-lg bg-white/10 hover:bg-white/15 text-white transition-colors"
          >
            <FlaskConical size={13} /> Run What-If Simulator
          </button>
        </div>
      </div>
    </div>
  );
}
