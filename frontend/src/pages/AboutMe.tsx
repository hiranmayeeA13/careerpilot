import { useState } from 'react';
import { useApi } from '../lib/useApi';
import { api } from '../lib/api';
import { useCandidate } from '../state/CandidateContext';
import { Spinner, ErrorBanner, SectionTitle, Badge } from '../components/Primitives';
import { UserCircle2, Download, Award, Target, FolderCheck, Mic, ShieldCheck, Mail, Calendar, BookOpen, Printer } from 'lucide-react';
import { evidenceColor } from '../lib/utils';

export function AboutMe() {
  const { candidateId, candidate } = useCandidate();
  const { data, loading, error, refetch } = useApi(() => api.getCareerTwin(candidateId), [candidateId]);
  const readiness = useApi(() => api.getReadiness(candidateId), [candidateId]);
  const [downloadSuccess, setDownloadSuccess] = useState(false);

  if (loading || readiness.loading) return <Spinner label="Loading your personal CareerPilot profile…" />;
  if (error || readiness.error) return <ErrorBanner message={error || readiness.error || 'Failed to load profile.'} onRetry={refetch} />;
  if (!data) return null;

  function downloadJsonProfile() {
    if (!data) return;
    const jsonStr = JSON.stringify(
      {
        profile: data,
        readiness: readiness.data || null,
        exported_at: new Date().toISOString(),
      },
      null,
      2
    );
    const blob = new Blob([jsonStr], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${data.name.replace(/\s+/g, '_')}_CareerPilot_Profile.json`;
    link.click();
    URL.revokeObjectURL(url);
    setDownloadSuccess(true);
    setTimeout(() => setDownloadSuccess(false), 3000);
  }

  const skillEntries = Object.entries(data.skills).sort((a, b) => b[1] - a[1]);
  const verifiedCount = Object.values(data.skill_evidence).filter(
    (e) => e.status === 'Strongly-supported' || e.status === 'Project-demonstrated'
  ).length;

  return (
    <div className="fade-up space-y-6">
      <div className="flex items-start justify-between flex-wrap gap-3">
        <SectionTitle
          icon={<UserCircle2 size={20} />}
          title="About Me"
          subtitle="Your comprehensive personal profile, career readiness metrics, and verified engineering records"
        />
        <div className="flex items-center gap-2">
          <button
            onClick={() => window.print()}
            className="flex items-center gap-1.5 text-xs font-semibold px-3.5 py-2 rounded-xl bg-panel2 text-white/90 hover:bg-panel2/80 hover:text-white transition-colors border border-white/10"
            title="Print or Save as PDF"
          >
            <Printer size={14} />
            Print / PDF
          </button>
          <button
            onClick={downloadJsonProfile}
            className="flex items-center gap-1.5 text-xs font-semibold px-3.5 py-2 rounded-xl bg-accent text-ink hover:bg-accent/90 transition-colors shadow-glow"
          >
            <Download size={14} />
            {downloadSuccess ? '✓ Profile Downloaded' : 'Export Profile (.json)'}
          </button>
        </div>
      </div>

      {/* Header Profile Card */}
      <div className="card p-6 bg-gradient-to-br from-accent/10 via-[#121833] to-transparent border-accent/20">
        <div className="flex items-start justify-between flex-wrap gap-4">
          <div className="flex items-center gap-4">
            <div className="w-14 h-14 rounded-2xl bg-accent/20 border border-accent/40 flex items-center justify-center text-accent font-bold text-xl">
              {data.name.slice(0, 2).toUpperCase()}
            </div>
            <div>
              <h2 className="text-2xl font-bold text-white">{data.name}</h2>
              <p className="text-accent text-sm font-medium mt-0.5">{data.target_role}</p>
              <p className="text-white/40 text-xs mt-1">Candidate ID: {data.id} · Profile updated: {data.updated_at}</p>
            </div>
          </div>
          <Badge className="bg-accent2/15 text-accent2 border-accent2/30 text-xs py-1 px-3">
            {readiness.data?.category || 'Active Profile'}
          </Badge>
        </div>

        {data.twin_summary && (
          <p className="text-sm text-white/70 mt-4 pt-3 border-t border-white/5 leading-relaxed">
            {data.twin_summary}
          </p>
        )}
      </div>

      {/* KPI Cards */}
      <div className="grid sm:grid-cols-4 gap-4">
        <div className="card p-4">
          <p className="text-[10px] uppercase text-white/40 font-semibold">Career Readiness</p>
          <p className="text-2xl font-bold text-accent mt-1">
            {readiness.data?.overall_score ?? '—'}<span className="text-xs text-white/40 font-normal">/100</span>
          </p>
          <p className="text-[11px] text-white/45 mt-0.5">{readiness.data?.category}</p>
        </div>

        <div className="card p-4">
          <p className="text-[10px] uppercase text-white/40 font-semibold">Total Skills</p>
          <p className="text-2xl font-bold text-white mt-1">{skillEntries.length}</p>
          <p className="text-[11px] text-accent2 mt-0.5">{verifiedCount} verified evidence</p>
        </div>

        <div className="card p-4">
          <p className="text-[10px] uppercase text-white/40 font-semibold">Completed Projects</p>
          <p className="text-2xl font-bold text-white mt-1">{data.completed_projects.length}</p>
          <p className="text-[11px] text-white/45 mt-0.5">hands-on deliverables</p>
        </div>

        <div className="card p-4">
          <p className="text-[10px] uppercase text-white/40 font-semibold">Mock Interviews</p>
          <p className="text-2xl font-bold text-white mt-1">{data.interview_history.length}</p>
          <p className="text-[11px] text-white/45 mt-0.5">evaluated sessions</p>
        </div>
      </div>

      {/* Goals & Learning Preferences */}
      <div className="grid md:grid-cols-2 gap-5">
        <div className="card p-5 space-y-3">
          <div className="flex items-center gap-2 text-accent">
            <Target size={16} />
            <h3 className="text-sm font-semibold text-white">Target Career Goals</h3>
          </div>
          {data.goals.length > 0 ? (
            <ul className="space-y-2">
              {data.goals.map((g, i) => (
                <li key={i} className="text-xs text-white/80 flex items-start gap-2 bg-white/[0.02] p-2.5 rounded-lg border border-white/5">
                  <span className="text-accent mt-0.5">▸</span>
                  <span>{g}</span>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-xs text-white/45 italic">No specific goals recorded.</p>
          )}
        </div>

        <div className="card p-5 space-y-3">
          <div className="flex items-center gap-2 text-accent2">
            <BookOpen size={16} />
            <h3 className="text-sm font-semibold text-white">Learning Preferences & Commitment</h3>
          </div>
          <div className="space-y-2">
            {Object.entries(data.learning_preferences || {}).map(([k, v]) => (
              <div key={k} className="p-2.5 rounded-lg bg-white/[0.02] border border-white/5 flex justify-between items-center text-xs">
                <span className="text-white/50 capitalize">{k.replace(/_/g, ' ')}</span>
                <span className="text-white font-medium">{String(v)}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Verified Skills & Evidence */}
      <div className="card p-5 space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2 text-accent">
            <ShieldCheck size={18} />
            <h3 className="text-sm font-semibold text-white">Skills Inventory & Verification Status</h3>
          </div>
          <span className="text-xs text-white/40">{skillEntries.length} skills indexed</span>
        </div>

        <div className="grid sm:grid-cols-2 md:grid-cols-3 gap-3">
          {skillEntries.map(([skill, mastery]) => {
            const ev = data.skill_evidence[skill];
            const status = ev?.status || 'Unverified';
            return (
              <div key={skill} className="p-3 rounded-xl bg-white/[0.02] border border-white/5 space-y-2">
                <div className="flex justify-between items-center">
                  <span className="text-xs font-semibold text-white">{skill}</span>
                  <span className="text-xs font-bold text-accent">{mastery}/100</span>
                </div>
                <div className="h-1.5 bg-white/5 rounded-full overflow-hidden">
                  <div className="h-full bg-accent rounded-full" style={{ width: `${mastery}%` }} />
                </div>
                <div className="flex justify-between items-center text-[10px]">
                  <span className="text-white/40">Status:</span>
                  <Badge className={`text-[10px] ${evidenceColor(status)}`}>{status}</Badge>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Projects & Interviews Log */}
      <div className="grid md:grid-cols-2 gap-5">
        <div className="card p-5 space-y-3">
          <div className="flex items-center gap-2 text-white/80">
            <FolderCheck size={16} className="text-accent" />
            <h3 className="text-sm font-semibold">Completed Projects Record ({data.completed_projects.length})</h3>
          </div>
          {data.completed_projects.length > 0 ? (
            <div className="space-y-2.5">
              {data.completed_projects.map((p) => (
                <div key={p.id} className="p-3 rounded-lg bg-white/[0.02] border border-white/5 space-y-1">
                  <div className="flex justify-between items-center">
                    <p className="text-xs font-bold text-white">{p.title}</p>
                    <span className="text-[10px] text-accent2 font-semibold">Score: {p.evaluation_score ?? '80'}/100</span>
                  </div>
                  <p className="text-[11px] text-white/50 leading-relaxed">{p.description}</p>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-xs text-white/40 italic">No completed projects on record.</p>
          )}
        </div>

        <div className="card p-5 space-y-3">
          <div className="flex items-center gap-2 text-white/80">
            <Mic size={16} className="text-accent2" />
            <h3 className="text-sm font-semibold">Interview History Log ({data.interview_history.length})</h3>
          </div>
          {data.interview_history.length > 0 ? (
            <div className="space-y-2.5">
              {data.interview_history.map((i) => (
                <div key={i.id} className="p-3 rounded-lg bg-white/[0.02] border border-white/5 space-y-1">
                  <div className="flex justify-between items-center">
                    <p className="text-xs font-bold text-white">{i.target_role}</p>
                    <span className="text-[10px] text-accent font-semibold">{i.performance_score}/100</span>
                  </div>
                  <p className="text-[11px] text-white/50 leading-relaxed">{i.feedback}</p>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-xs text-white/40 italic">No mock interviews completed.</p>
          )}
        </div>
      </div>
    </div>
  );
}
