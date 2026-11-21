import { useState, useEffect } from 'react';
import { Users2, Trophy, ArrowRightLeft, UserCheck } from 'lucide-react';
import { RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, ResponsiveContainer, Legend } from 'recharts';
import { api } from '../lib/api';
import { Spinner, ErrorBanner, SectionTitle, Badge } from '../components/Primitives';
import type { CandidateProfile, ReadinessResponse } from '../types/api';

export function Compare() {
  const [roster, setRoster] = useState<CandidateProfile[]>([]);
  const [loadingRoster, setLoadingRoster] = useState(true);
  const [errorRoster, setErrorRoster] = useState<string | null>(null);

  const [candAId, setCandAId] = useState<string>('');
  const [candBId, setCandBId] = useState<string>('');

  const [profileA, setProfileA] = useState<CandidateProfile | null>(null);
  const [profileB, setProfileB] = useState<CandidateProfile | null>(null);
  const [readinessA, setReadinessA] = useState<ReadinessResponse | null>(null);
  const [readinessB, setReadinessB] = useState<ReadinessResponse | null>(null);
  const [comparing, setComparing] = useState(false);

  useEffect(() => {
    async function fetchRoster() {
      setLoadingRoster(true);
      setErrorRoster(null);
      try {
        const list = await api.getRosterCandidates();
        setRoster(list);
        if (list.length >= 2) {
          setCandAId(list[0].id);
          setCandBId(list[1].id);
        } else if (list.length === 1) {
          setCandAId(list[0].id);
          setCandBId(list[0].id);
        }
      } catch (e: any) {
        setErrorRoster(e?.message || 'Could not load candidate roster.');
      } finally {
        setLoadingRoster(false);
      }
    }
    fetchRoster();
  }, []);

  useEffect(() => {
    if (!candAId || !candBId) return;
    async function loadPair() {
      setComparing(true);
      try {
        const [pa, pb, ra, rb] = await Promise.all([
          api.getCareerTwin(candAId),
          api.getCareerTwin(candBId),
          api.getReadiness(candAId),
          api.getReadiness(candBId),
        ]);
        setProfileA(pa);
        setProfileB(pb);
        setReadinessA(ra);
        setReadinessB(rb);
      } catch {
        // Handled silently or shown in UI
      } finally {
        setComparing(false);
      }
    }
    loadPair();
  }, [candAId, candBId]);

  if (loadingRoster) return <Spinner label="Loading candidate roster for comparison…" />;
  if (errorRoster) return <ErrorBanner message={errorRoster} onRetry={() => window.location.reload()} />;
  if (!roster.length) return <div className="card p-6 text-white/60">No candidates available in roster.</div>;

  // Build union skills for radar chart
  const skillsA = profileA ? Object.keys(profileA.skills) : [];
  const skillsB = profileB ? Object.keys(profileB.skills) : [];
  const allSkills = Array.from(new Set([...skillsA, ...skillsB]));

  // Ensure at least 3 axes for a valid radar polygon
  const radarAxes = allSkills.length >= 3 ? allSkills : [...allSkills, 'Architecture', 'Problem Solving', 'Engineering Fundamentals'].slice(0, 4);

  const radarData = radarAxes.map((skill) => ({
    skill,
    [profileA?.name || 'Candidate A']: profileA?.skills[skill] ?? 0,
    [profileB?.name || 'Candidate B']: profileB?.skills[skill] ?? 0,
  }));

  const leader =
    readinessA && readinessB
      ? readinessA.overall_score === readinessB.overall_score
        ? null
        : readinessA.overall_score > readinessB.overall_score
        ? profileA
        : profileB
      : null;

  return (
    <div className="fade-up space-y-6">
      <SectionTitle
        icon={<Users2 size={20} />}
        title="Compare Candidates"
        subtitle="Head-to-head comparison across all registered and newly added candidate profiles"
      />

      {/* Selectors Bar */}
      <div className="card p-5 grid sm:grid-cols-2 gap-4 border-accent/20">
        <div>
          <label className="text-xs text-white/50 mb-1.5 block font-medium">Select Candidate A</label>
          <select
            value={candAId}
            onChange={(e) => setCandAId(e.target.value)}
            className="w-full bg-white/5 border border-white/10 rounded-xl px-3 py-2 text-sm text-white focus:outline-none focus:border-accent"
          >
            {roster.map((c) => (
              <option key={c.id} value={c.id} className="bg-[#121833] text-white">
                {c.name} ({c.target_role})
              </option>
            ))}
          </select>
        </div>
        <div>
          <label className="text-xs text-white/50 mb-1.5 block font-medium">Select Candidate B</label>
          <select
            value={candBId}
            onChange={(e) => setCandBId(e.target.value)}
            className="w-full bg-white/5 border border-white/10 rounded-xl px-3 py-2 text-sm text-white focus:outline-none focus:border-accent"
          >
            {roster.map((c) => (
              <option key={c.id} value={c.id} className="bg-[#121833] text-white">
                {c.name} ({c.target_role})
              </option>
            ))}
          </select>
        </div>
      </div>

      {comparing && <Spinner label="Updating comparison metrics…" />}

      {!comparing && profileA && profileB && readinessA && readinessB && (
        <>
          {leader && (
            <div className="card p-4 flex items-center gap-3 bg-gradient-to-r from-accent2/10 to-transparent border-accent2/20">
              <Trophy size={18} className="text-accent2 shrink-0" />
              <p className="text-sm text-white/80">
                <span className="font-semibold text-accent2">{leader.name}</span> currently leads with an overall readiness score of{' '}
                <span className="font-bold text-white">{Math.max(readinessA.overall_score, readinessB.overall_score)}/100</span>.
              </p>
            </div>
          )}

          {/* Side by side scorecards */}
          <div className="grid md:grid-cols-2 gap-5">
            {[
              { p: profileA, r: readinessA, color: 'text-accent' },
              { p: profileB, r: readinessB, color: 'text-accent2' },
            ].map(({ p, r, color }) => (
              <div key={p.id} className="card p-5 space-y-4">
                <div className="flex items-start justify-between">
                  <div>
                    <h3 className="text-lg font-bold text-white">{p.name}</h3>
                    <p className="text-xs text-white/50">{p.target_role}</p>
                  </div>
                  <Badge className="bg-white/5 text-white/70 border-white/10">{r.category}</Badge>
                </div>
                <div className="flex items-baseline gap-2">
                  <span className={`text-4xl font-extrabold ${color}`}>{r.overall_score}</span>
                  <span className="text-xs text-white/40">/ 100 overall readiness</span>
                </div>
                <div className="grid grid-cols-4 gap-2 pt-2 border-t border-white/5 text-center">
                  <div className="bg-white/[0.02] p-2 rounded-lg">
                    <p className="text-[10px] text-white/40 uppercase">Skills</p>
                    <p className="text-sm font-semibold text-white mt-0.5">{r.breakdown.skills}</p>
                  </div>
                  <div className="bg-white/[0.02] p-2 rounded-lg">
                    <p className="text-[10px] text-white/40 uppercase">Evidence</p>
                    <p className="text-sm font-semibold text-white mt-0.5">{r.breakdown.evidence}</p>
                  </div>
                  <div className="bg-white/[0.02] p-2 rounded-lg">
                    <p className="text-[10px] text-white/40 uppercase">Interview</p>
                    <p className="text-sm font-semibold text-white mt-0.5">{r.breakdown.interview}</p>
                  </div>
                  <div className="bg-white/[0.02] p-2 rounded-lg">
                    <p className="text-[10px] text-white/40 uppercase">Portfolio</p>
                    <p className="text-sm font-semibold text-white mt-0.5">{r.breakdown.portfolio}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Comparative Radar Chart */}
          <div className="card p-5">
            <h4 className="text-sm font-semibold text-white/80 mb-3">Head-to-Head Skill Mastery Radar</h4>
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <RadarChart data={radarData} outerRadius="75%">
                  <PolarGrid stroke="rgba(255,255,255,0.08)" />
                  <PolarAngleAxis dataKey="skill" tick={{ fill: '#b8c0ea', fontSize: 11 }} />
                  <PolarRadiusAxis domain={[0, 100]} tick={{ fill: 'rgba(255,255,255,0.2)', fontSize: 10 }} />
                  <Radar name={profileA.name} dataKey={profileA.name} stroke="#6c8cff" fill="#6c8cff" fillOpacity={0.25} />
                  <Radar name={profileB.name} dataKey={profileB.name} stroke="#36d7b7" fill="#36d7b7" fillOpacity={0.25} />
                  <Legend wrapperStyle={{ paddingTop: 10, fontSize: 12 }} />
                </RadarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Differential Skill Breakdown */}
          <div className="card p-5">
            <h4 className="text-sm font-semibold text-white/80 mb-3">Skill Differential Comparison</h4>
            <div className="space-y-2">
              {allSkills.map((sk) => {
                const valA = profileA.skills[sk] ?? 0;
                const valB = profileB.skills[sk] ?? 0;
                const diff = valA - valB;
                return (
                  <div key={sk} className="flex items-center justify-between text-xs py-2 border-b border-white/5">
                    <span className="text-white/70 font-medium w-36">{sk}</span>
                    <span className="text-accent font-semibold w-12 text-center">{valA}</span>
                    <div className="flex-1 mx-3 h-2 bg-white/5 rounded-full overflow-hidden flex">
                      <div className="bg-accent h-full" style={{ width: `${valA / 2}%` }} />
                      <div className="bg-accent2 h-full" style={{ width: `${valB / 2}%` }} />
                    </div>
                    <span className="text-accent2 font-semibold w-12 text-center">{valB}</span>
                    <span className={`w-20 text-right font-medium ${diff > 0 ? 'text-accent' : diff < 0 ? 'text-accent2' : 'text-white/40'}`}>
                      {diff > 0 ? `+${diff} A` : diff < 0 ? `+${Math.abs(diff)} B` : 'Tie'}
                    </span>
                  </div>
                );
              })}
            </div>
          </div>
        </>
      )}

      {/* Complete Roster Overview */}
      <div className="card p-5">
        <h4 className="text-sm font-semibold text-white/80 mb-3 flex items-center gap-2">
          <UserCheck size={16} className="text-accent" />
          Full Candidate Roster ({roster.length})
        </h4>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-white/70">
            <thead className="bg-white/5 text-white/40 text-[10px] uppercase">
              <tr>
                <th className="p-2.5">Name</th>
                <th className="p-2.5">Target Role</th>
                <th className="p-2.5">Skills Recorded</th>
                <th className="p-2.5">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/5">
              {roster.map((c) => (
                <tr key={c.id} className="hover:bg-white/[0.02]">
                  <td className="p-2.5 font-medium text-white">{c.name}</td>
                  <td className="p-2.5">{c.target_role}</td>
                  <td className="p-2.5">{Object.keys(c.skills).length} skills</td>
                  <td className="p-2.5 flex gap-2">
                    <button
                      onClick={() => setCandAId(c.id)}
                      className="px-2 py-1 rounded bg-accent/20 text-accent hover:bg-accent/30 text-[11px]"
                    >
                      Set as A
                    </button>
                    <button
                      onClick={() => setCandBId(c.id)}
                      className="px-2 py-1 rounded bg-accent2/20 text-accent2 hover:bg-accent2/30 text-[11px]"
                    >
                      Set as B
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
