import { useState } from 'react';
import { Upload, Loader2, Sparkles, CheckCircle2, Download, Database, ShieldAlert, Check } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useCandidate } from '../state/CandidateContext';
import { api, ApiError } from '../lib/api';
import { SectionTitle, Badge } from '../components/Primitives';
import type { ResumeIntakeResponse } from '../types/api';

export function Intake() {
  const { addCandidate } = useCandidate();
  const navigate = useNavigate();

  const [name, setName] = useState('');
  const [targetRole, setTargetRole] = useState('Full Stack Developer');
  const [weeklyHours, setWeeklyHours] = useState(10);
  const [resumeText, setResumeText] = useState('');
  const [saveToRoster, setSaveToRoster] = useState(true);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<ResumeIntakeResponse | null>(null);
  const [downloaded, setDownloaded] = useState(false);

  async function submit() {
    if (!name.trim() || !resumeText.trim()) {
      setError('Please enter a candidate name and paste your resume text.');
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const res = await api.intakeResume({
        name,
        target_role: targetRole,
        resume_text: resumeText,
        weekly_hours: weeklyHours,
        save_to_database: saveToRoster,
      });
      setResult(res);
      addCandidate({ id: res.candidate_id, name: res.name, role: res.target_role }, saveToRoster);
    } catch (e) {
      setError(e instanceof ApiError ? e.message : 'Resume intake failed.');
    } finally {
      setLoading(false);
    }
  }

  function downloadJson() {
    if (!result) return;
    const blob = new Blob([JSON.stringify(result, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${result.name.replace(/\s+/g, '_')}_profile.json`;
    link.click();
    URL.revokeObjectURL(url);
    setDownloaded(true);
    setTimeout(() => setDownloaded(false), 3000);
  }

  return (
    <div className="fade-up space-y-6">
      <SectionTitle
        icon={<Upload size={20} />}
        title="Resume & Target-Role Intake"
        subtitle="Parse any candidate resume and configure whether to save it into the persistent roster or keep it as a temporary session"
      />

      {!result && (
        <div className="card p-6 space-y-4">
          <div className="grid md:grid-cols-2 gap-4">
            <div>
              <label className="text-xs text-white/50 mb-1.5 block font-medium">Candidate Name</label>
              <input
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="e.g. Jordan Lee"
                className="w-full bg-white/5 border border-white/10 rounded-xl px-3 py-2 text-sm text-white placeholder:text-white/25 focus:outline-none focus:border-accent"
              />
            </div>
            <div>
              <label className="text-xs text-white/50 mb-1.5 block font-medium">Target Engineering Role</label>
              <input
                value={targetRole}
                onChange={(e) => setTargetRole(e.target.value)}
                placeholder="e.g. Full Stack Developer, DevOps Engineer"
                className="w-full bg-white/5 border border-white/10 rounded-xl px-3 py-2 text-sm text-white placeholder:text-white/25 focus:outline-none focus:border-accent"
              />
            </div>
          </div>

          <div>
            <label className="text-xs text-white/50 mb-1.5 block font-medium">Weekly Study Hours Available</label>
            <input
              type="number"
              min={1}
              max={60}
              value={weeklyHours}
              onChange={(e) => setWeeklyHours(Number(e.target.value))}
              className="w-36 bg-white/5 border border-white/10 rounded-xl px-3 py-2 text-sm text-white focus:outline-none focus:border-accent"
            />
          </div>

          <div>
            <label className="text-xs text-white/50 mb-1.5 block font-medium">Resume Text (Plain Text)</label>
            <textarea
              value={resumeText}
              onChange={(e) => setResumeText(e.target.value)}
              rows={9}
              placeholder="Paste plain-text resume content here (experience, skills, tools used, cloud architectures)..."
              className="w-full bg-white/5 border border-white/10 rounded-xl px-3 py-2.5 text-sm text-white placeholder:text-white/25 focus:outline-none focus:border-accent font-sans"
            />
          </div>

          {/* Save to Database Toggle */}
          <div className="p-3.5 rounded-xl bg-white/[0.02] border border-white/10 flex items-center justify-between">
            <div className="flex items-center gap-2.5">
              <Database size={18} className={saveToRoster ? 'text-accent' : 'text-white/30'} />
              <div>
                <p className="text-xs font-semibold text-white">Save Profile into Persistent SQLite Database</p>
                <p className="text-[11px] text-white/45">
                  {saveToRoster
                    ? 'Candidate will be stored in SQLite database and available in Compare Candidates and all tabs across sessions.'
                    : 'Unchecked: Candidate profile is held in temporary memory for this session only without saving to SQLite.'}
                </p>
              </div>
            </div>
            <input
              type="checkbox"
              checked={saveToRoster}
              onChange={(e) => setSaveToRoster(e.target.checked)}
              className="w-4 h-4 accent-accent rounded cursor-pointer"
            />
          </div>

          {error && <p className="text-xs text-danger">{error}</p>}

          <button
            onClick={submit}
            disabled={loading}
            className="flex items-center justify-center gap-2 bg-accent hover:bg-accent/90 disabled:opacity-60 text-ink font-semibold text-sm px-6 py-2.5 rounded-xl transition-colors shadow-glow"
          >
            {loading ? <Loader2 size={16} className="animate-spin" /> : <Sparkles size={16} />}
            Analyze Resume & Initialize Career Twin
          </button>
        </div>
      )}

      {result && (
        <div className="card p-6 bg-gradient-to-br from-accent2/10 to-transparent border-accent2/20 fade-up space-y-4">
          <div className="flex items-center justify-between flex-wrap gap-2">
            <div className="flex items-center gap-2 text-accent2">
              <CheckCircle2 size={18} />
              <h3 className="text-base font-bold text-white">Resume Ingested & Analyzed Successfully</h3>
            </div>
            <Badge className="bg-accent2/15 text-accent2 border-accent2/30">
              {saveToRoster ? 'Saved to Database' : 'Temporary Session'}
            </Badge>
          </div>

          <p className="text-sm text-white/70 leading-relaxed">{result.message}</p>

          <div>
            <p className="text-xs uppercase tracking-wider text-white/40 font-semibold mb-2">
              Extracted Skills ({result.skills_detected}):
            </p>
            <div className="flex flex-wrap gap-2">
              {Object.entries(result.extracted_skills).map(([skill, mastery]) => (
                <Badge key={skill} className="bg-white/5 text-white/80 border-white/10 text-xs py-1">
                  {skill}: <span className="text-accent font-bold ml-1">{mastery}</span>
                </Badge>
              ))}
            </div>
          </div>

          <div className="pt-3 border-t border-white/5 flex items-center justify-between flex-wrap gap-3">
            <div className="flex gap-2">
              <button
                onClick={downloadJson}
                className="flex items-center gap-1.5 text-xs font-semibold px-3 py-2 rounded-xl bg-white/10 hover:bg-white/15 text-white transition-colors"
              >
                {downloaded ? <Check size={14} className="text-accent2" /> : <Download size={14} />}
                {downloaded ? '✓ JSON Downloaded' : 'Save as .json file'}
              </button>
            </div>

            <div className="flex gap-2">
              <button
                onClick={() => navigate('/about-me')}
                className="bg-accent2/20 hover:bg-accent2/30 text-accent2 border border-accent2/40 font-semibold text-xs px-4 py-2 rounded-xl transition-colors"
              >
                View About Me Profile
              </button>
              <button
                onClick={() => navigate('/')}
                className="bg-accent hover:bg-accent/90 text-ink font-semibold text-xs px-4 py-2 rounded-xl transition-colors shadow-glow"
              >
                View Career Readiness Score
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
