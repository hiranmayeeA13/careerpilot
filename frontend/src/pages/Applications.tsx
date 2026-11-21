import { useState } from 'react';
import { SendHorizonal, Plus, Loader2, TrendingUp, Search, Sparkles, Copy, Check } from 'lucide-react';
import { useCandidate } from '../state/CandidateContext';
import { useApi } from '../lib/useApi';
import { api, ApiError } from '../lib/api';
import { Spinner, ErrorBanner, SectionTitle, Badge, StatPill } from '../components/Primitives';
import type { ApplicationStatus } from '../types/api';

const STATUS_OPTIONS: ApplicationStatus[] = ['Applied', 'Interviewing', 'Rejected', 'Offer', 'No Response'];

function statusColor(status: ApplicationStatus) {
  switch (status) {
    case 'Offer':
      return 'bg-accent2/15 text-accent2 border-accent2/25';
    case 'Interviewing':
      return 'bg-accent/15 text-accent border-accent2/25';
    case 'Rejected':
      return 'bg-danger/15 text-danger border-danger/25';
    case 'No Response':
      return 'bg-white/5 text-white/40 border-white/10';
    default:
      return 'bg-warn/15 text-warn border-warn/25';
  }
}

export function Applications() {
  const { candidateId, candidate } = useCandidate();
  const apps = useApi(() => api.listApplications(candidateId), [candidateId]);
  const insights = useApi(() => api.getApplicationInsights(candidateId), [candidateId]);

  const [company, setCompany] = useState('');
  const [roleTitle, setRoleTitle] = useState('');
  const [status, setStatus] = useState<ApplicationStatus>('Applied');
  const [logging, setLogging] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Search & Filter state
  const [searchQuery, setSearchQuery] = useState('');
  const [activeFilter, setActiveFilter] = useState<string>('All');

  // Tailored pitch note state
  const [activePitch, setActivePitch] = useState<{ company: string; role: string; pitch: string } | null>(null);
  const [copiedPitch, setCopiedPitch] = useState(false);

  async function submit() {
    if (!company.trim() || !roleTitle.trim()) {
      setError('Company and role title are required.');
      return;
    }
    setLogging(true);
    setError(null);
    try {
      await api.logApplication({ candidate_id: candidateId, company, role_title: roleTitle, status });
      setCompany('');
      setRoleTitle('');
      setStatus('Applied');
      apps.refetch();
      insights.refetch();
    } catch (e) {
      setError(e instanceof ApiError ? e.message : 'Could not log application.');
    } finally {
      setLogging(false);
    }
  }

  async function changeStatus(id: string, newStatus: ApplicationStatus) {
    await api.updateApplicationStatus(id, newStatus);
    apps.refetch();
    insights.refetch();
  }

  function generatePitchNote(compName: string, roleName: string) {
    const pitch = `Hi Team,\n\nI am thrilled to apply for the ${roleName} position at ${compName}. With focused technical proficiency in ${candidate.role} and hands-on experience designing scalable architectures and containerized microservices, I bring proven readiness to contribute immediately to ${compName}'s engineering goals.\n\nKey Strengths:\n• System reliability & clean architectural design\n• Production-tested problem-solving and rigorous verification\n• Fast learner with structured technical execution\n\nI would welcome the opportunity to connect and discuss how my skill set aligns with your team's objectives.`;
    setActivePitch({ company: compName, role: roleName, pitch });
    setCopiedPitch(false);
  }

  function copyPitch() {
    if (!activePitch) return;
    navigator.clipboard.writeText(activePitch.pitch);
    setCopiedPitch(true);
    setTimeout(() => setCopiedPitch(false), 2000);
  }

  const allApps = apps.data || [];
  const filteredApps = allApps.filter((a) => {
    const matchesSearch =
      a.company.toLowerCase().includes(searchQuery.toLowerCase()) ||
      a.role_title.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesFilter = activeFilter === 'All' || a.status === activeFilter;
    return matchesSearch && matchesFilter;
  });

  return (
    <div className="fade-up space-y-6">
      <SectionTitle
        icon={<SendHorizonal size={20} />}
        title="Application Tracker & Response Insights"
        subtitle={`Track job applications for ${candidate.name} and dynamically calibrate learning priorities from employer response rates`}
      />

      {/* Insights dashboard */}
      {insights.data && (
        <div className="card p-5 bg-gradient-to-br from-accent/10 to-accent2/5 border-accent/20">
          <div className="flex items-center gap-2 text-accent mb-2">
            <TrendingUp size={16} />
            <h4 className="text-xs uppercase tracking-wider font-semibold">Live Market Conversion Rate</h4>
          </div>
          <div className="grid sm:grid-cols-3 gap-4 pt-1">
            <div>
              <p className="text-[10px] uppercase text-white/40">Total Tracked</p>
              <p className="text-2xl font-bold text-white mt-0.5">{insights.data.total_applications}</p>
            </div>
            <div>
              <p className="text-[10px] uppercase text-white/40">Response Rate</p>
              <p className="text-2xl font-bold text-accent2 mt-0.5">{Math.round((insights.data.overall_response_rate || 0) * 100)}%</p>
            </div>
            <div>
              <p className="text-[10px] uppercase text-white/40">Active Pipeline</p>
              <p className="text-2xl font-bold text-accent mt-0.5">
                {allApps.filter((a) => a.status === 'Applied' || a.status === 'Interviewing').length}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Log Application Card */}
      <div className="card p-5 space-y-3">
        <h4 className="text-xs uppercase tracking-wider text-white/50 font-semibold">Log New Application</h4>
        <div className="grid md:grid-cols-3 gap-3">
          <input
            value={company}
            onChange={(e) => setCompany(e.target.value)}
            placeholder="Company name (e.g. Stripe, Datadog)..."
            className="bg-white/5 border border-white/10 rounded-xl px-3 py-2 text-sm text-white placeholder:text-white/25 focus:outline-none focus:border-accent"
          />
          <input
            value={roleTitle}
            onChange={(e) => setRoleTitle(e.target.value)}
            placeholder="Role title (e.g. DevOps Engineer)..."
            className="bg-white/5 border border-white/10 rounded-xl px-3 py-2 text-sm text-white placeholder:text-white/25 focus:outline-none focus:border-accent"
          />
          <select
            value={status}
            onChange={(e) => setStatus(e.target.value as ApplicationStatus)}
            className="bg-white/5 border border-white/10 rounded-xl px-3 py-2 text-sm text-white focus:outline-none focus:border-accent"
          >
            {STATUS_OPTIONS.map((opt) => (
              <option key={opt} value={opt} className="bg-[#121833] text-white">
                {opt}
              </option>
            ))}
          </select>
        </div>

        {error && <p className="text-xs text-danger">{error}</p>}

        <div className="flex justify-end pt-1">
          <button
            onClick={submit}
            disabled={logging}
            className="flex items-center gap-1.5 bg-accent hover:bg-accent/90 disabled:opacity-60 text-ink font-semibold text-xs px-4 py-2 rounded-xl transition-colors shadow-glow"
          >
            {logging ? <Loader2 size={14} className="animate-spin" /> : <Plus size={14} />}
            Log Application
          </button>
        </div>
      </div>

      {/* Search & Filter Toolbar */}
      <div className="card p-4 space-y-3 border-white/5">
        <div className="flex items-center justify-between flex-wrap gap-3">
          <div className="relative flex-1 max-w-sm">
            <Search size={14} className="absolute left-3 top-3 text-white/40" />
            <input
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search applications by company or role..."
              className="w-full bg-white/5 border border-white/10 rounded-xl pl-8 pr-3 py-1.5 text-xs text-white placeholder:text-white/30 focus:outline-none focus:border-accent"
            />
          </div>

          {/* Status filter pills */}
          <div className="flex flex-wrap gap-1.5">
            {['All', ...STATUS_OPTIONS].map((opt) => (
              <button
                key={opt}
                onClick={() => setActiveFilter(opt)}
                className={`px-2.5 py-1 rounded-lg text-xs font-medium transition-colors ${
                  activeFilter === opt
                    ? 'bg-accent text-ink font-semibold'
                    : 'bg-white/5 text-white/60 hover:bg-white/10'
                }`}
              >
                {opt}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Tailored Pitch Note Modal */}
      {activePitch && (
        <div className="card p-5 bg-gradient-to-br from-accent/15 via-[#121833] to-transparent border-accent/30 fade-up space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-accent">
              <Sparkles size={16} />
              <h4 className="text-sm font-bold text-white">
                Tailored Pitch Note for {activePitch.company} ({activePitch.role})
              </h4>
            </div>
            <button
              onClick={() => setActivePitch(null)}
              className="text-xs text-white/40 hover:text-white transition-colors"
            >
              ✕ Close
            </button>
          </div>
          <textarea
            value={activePitch.pitch}
            readOnly
            rows={7}
            className="w-full bg-white/5 border border-white/10 rounded-xl p-3 text-xs text-white/90 font-mono leading-relaxed focus:outline-none"
          />
          <div className="flex justify-end gap-2">
            <button
              onClick={copyPitch}
              className="flex items-center gap-1.5 bg-accent text-ink font-semibold text-xs px-3.5 py-1.5 rounded-lg transition-colors"
            >
              {copiedPitch ? <Check size={13} /> : <Copy size={13} />}
              {copiedPitch ? 'Copied to Clipboard' : 'Copy Pitch Note'}
            </button>
          </div>
        </div>
      )}

      {/* Applications List */}
      {apps.loading ? (
        <Spinner label="Loading application pipeline…" />
      ) : filteredApps.length === 0 ? (
        <div className="card p-6 text-center text-xs text-white/40">
          No applications match your search criteria.
        </div>
      ) : (
        <div className="card overflow-hidden">
          <table className="w-full text-left text-xs text-white/80">
            <thead className="bg-white/5 text-[10px] uppercase text-white/40 font-semibold border-b border-white/5">
              <tr>
                <th className="p-3">Company</th>
                <th className="p-3">Role</th>
                <th className="p-3">Date Applied</th>
                <th className="p-3">Status</th>
                <th className="p-3 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/5">
              {filteredApps.map((a) => (
                <tr key={a.id} className="hover:bg-white/[0.02] transition-colors">
                  <td className="p-3 font-semibold text-white">{a.company}</td>
                  <td className="p-3 text-white/70">{a.role_title}</td>
                  <td className="p-3 text-white/45">{a.date_applied}</td>
                  <td className="p-3">
                    <select
                      value={a.status}
                      onChange={(e) => changeStatus(a.id, e.target.value as ApplicationStatus)}
                      className={`text-xs px-2 py-1 rounded-md border bg-[#121833] focus:outline-none cursor-pointer ${statusColor(
                        a.status
                      )}`}
                    >
                      {STATUS_OPTIONS.map((opt) => (
                        <option key={opt} value={opt} className="bg-[#121833] text-white">
                          {opt}
                        </option>
                      ))}
                    </select>
                  </td>
                  <td className="p-3 text-right">
                    <button
                      onClick={() => generatePitchNote(a.company, a.role_title)}
                      className="text-accent hover:text-accent/80 font-medium text-[11px] px-2.5 py-1 rounded-lg bg-accent/10 border border-accent/20 transition-colors inline-flex items-center gap-1"
                    >
                      <Sparkles size={11} /> Pitch Note
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
