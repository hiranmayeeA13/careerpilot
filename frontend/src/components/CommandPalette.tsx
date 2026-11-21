import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Search,
  Gauge,
  UserCircle2,
  Upload,
  FlaskConical,
  Briefcase,
  CalendarDays,
  Compass,
  FolderGit2,
  Mic2,
  SendHorizonal,
  Users2,
  Moon,
  Flame,
  Sun,
  User,
  X,
  Sparkles,
} from 'lucide-react';
import { useCandidate } from '../state/CandidateContext';
import { useTheme } from '../state/ThemeContext';

interface CommandItem {
  id: string;
  category: 'Navigation' | 'Candidates' | 'Theme' | 'Actions';
  label: string;
  sub?: string;
  icon: any;
  action: () => void;
}

export function CommandPalette() {
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState('');
  const navigate = useNavigate();
  const { allCandidates, setCandidateId, candidateId } = useCandidate();
  const { setTheme } = useTheme();

  // Listen for Ctrl+K or Cmd+K
  useEffect(() => {
    function handleKeyDown(e: KeyboardEvent) {
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        setOpen((o) => !o);
      } else if (e.key === 'Escape' && open) {
        setOpen(false);
      }
    }
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [open]);

  const items: CommandItem[] = [
    // Navigation items
    { id: 'nav-readiness', category: 'Navigation', label: 'Career Readiness Dashboard', sub: 'Composite score & breakdown', icon: Gauge, action: () => navigate('/') },
    { id: 'nav-about-me', category: 'Navigation', label: 'About Me Profile', sub: 'Your complete profile & verified history', icon: UserCircle2, action: () => navigate('/about-me') },
    { id: 'nav-intake', category: 'Navigation', label: 'Resume & Role Intake', sub: 'Parse new resume & candidate identity', icon: Upload, action: () => navigate('/intake') },
    { id: 'nav-simulator', category: 'Navigation', label: 'What-If Career Simulator', sub: 'Simulate hypothetical skill upgrades', icon: FlaskConical, action: () => navigate('/simulator') },
    { id: 'nav-twin', category: 'Navigation', label: 'Persistent Career Twin', sub: 'Radar chart, goals & preferences', icon: UserCircle2, action: () => navigate('/twin') },
    { id: 'nav-job-market', category: 'Navigation', label: 'Job Market & Gap Analysis', sub: 'Real postings & market demand', icon: Briefcase, action: () => navigate('/job-market') },
    { id: 'nav-plan', category: 'Navigation', label: 'Interactive Learning Plan', sub: 'Week-by-week checklist', icon: CalendarDays, action: () => navigate('/plan') },
    { id: 'nav-reality-check', category: 'Navigation', label: 'Career Reality Check', sub: 'Prerequisites & preparation sequence', icon: Compass, action: () => navigate('/reality-check') },
    { id: 'nav-portfolio', category: 'Navigation', label: 'Smart Portfolio Generator', sub: 'Tailored hands-on project briefs', icon: FolderGit2, action: () => navigate('/portfolio') },
    { id: 'nav-interview', category: 'Navigation', label: 'Technical Mock Interview', sub: 'Question variations & deep rubric scoring', icon: Mic2, action: () => navigate('/mock-interview') },
    { id: 'nav-applications', category: 'Navigation', label: 'Applications & Pitch Notes', sub: 'Pipeline tracking & conversion', icon: SendHorizonal, action: () => navigate('/applications') },
    { id: 'nav-compare', category: 'Navigation', label: 'Compare Candidates', sub: 'Head-to-head radar comparison', icon: Users2, action: () => navigate('/compare') },

    // Candidates
    ...allCandidates.map((c) => ({
      id: `cand-${c.id}`,
      category: 'Candidates' as const,
      label: `Switch Candidate: ${c.name}`,
      sub: `${c.role} ${c.id === candidateId ? '(Active)' : ''}`,
      icon: User,
      action: () => setCandidateId(c.id),
    })),

    // Themes
    { id: 'th-warm', category: 'Theme', label: 'Theme: Batch 1 (Warm Terracotta)', sub: 'Espresso, Mocha & Caramel Gradient (#3E2723, #D18B47)', icon: Flame, action: () => setTheme('warm-terracotta') },
    { id: 'th-dark', category: 'Theme', label: 'Theme: Batch 2 (Midnight Slate)', sub: 'Obsidian Steel Dark Mode (#0F172A, #334155)', icon: Moon, action: () => setTheme('midnight-slate') },
  ];

  const filtered = items.filter((item) => {
    const q = query.toLowerCase();
    return item.label.toLowerCase().includes(q) || (item.sub && item.sub.toLowerCase().includes(q)) || item.category.toLowerCase().includes(q);
  });

  return (
    <>
      {/* Header Search Trigger Button */}
      <button
        onClick={() => setOpen(true)}
        className="flex items-center gap-2.5 px-3 py-1.5 rounded-xl border border-white/10 bg-black/30 hover:bg-black/45 transition-colors text-xs text-white/60 w-44 md:w-60 justify-between shadow-sm"
      >
        <span className="flex items-center gap-2">
          <Search size={14} className="text-white/40" />
          <span className="text-white/60">Quick search...</span>
        </span>
        <kbd className="hidden sm:inline-block text-[10px] bg-white/10 px-1.5 py-0.5 rounded text-white/50 font-mono">
          Ctrl K
        </kbd>
      </button>

      {/* Modal Dialog */}
      {open && (
        <div className="fixed inset-0 z-50 flex items-start justify-center pt-20 px-4">
          <div className="fixed inset-0 bg-black/80 backdrop-blur-md" onClick={() => setOpen(false)} />
          <div className="relative w-full max-w-xl bg-panel border border-white/15 rounded-2xl p-5 shadow-2xl backdrop-blur-2xl fade-up space-y-3.5 z-10">
            <div className="flex items-center gap-2.5 px-1 pb-3 border-b border-white/10">
              <Search size={18} className="text-accent shrink-0" />
              <input
                autoFocus
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Search tabs, candidates, themes, or quick actions..."
                className="w-full bg-transparent text-sm text-white placeholder:text-white/35 focus:outline-none"
              />
              <button onClick={() => setOpen(false)} className="text-white/40 hover:text-white text-xs px-1">
                <X size={16} />
              </button>
            </div>

            <div className="max-h-96 overflow-y-auto scrollbar-thin space-y-1">
              {filtered.length === 0 ? (
                <div className="p-6 text-center text-xs text-white/40">No matching commands or pages found.</div>
              ) : (
                filtered.map((item) => {
                  const ItemIcon = item.icon;
                  return (
                    <button
                      key={item.id}
                      onClick={() => {
                        item.action();
                        setOpen(false);
                      }}
                      className="w-full text-left p-2.5 rounded-xl text-xs flex items-center justify-between hover:bg-white/[0.06] transition-colors border border-transparent hover:border-white/5"
                    >
                      <div className="flex items-center gap-3">
                        <div className="w-7 h-7 rounded-lg bg-white/5 flex items-center justify-center text-accent shrink-0">
                          <ItemIcon size={15} />
                        </div>
                        <div>
                          <p className="text-white font-medium">{item.label}</p>
                          {item.sub && <p className="text-[11px] text-white/40 mt-0.5">{item.sub}</p>}
                        </div>
                      </div>
                      <span className="text-[10px] uppercase font-bold text-white/30 bg-white/5 px-2 py-0.5 rounded">
                        {item.category}
                      </span>
                    </button>
                  );
                })
              )}
            </div>

            <div className="pt-2 border-t border-white/5 flex items-center justify-between text-[11px] text-white/35 px-1">
              <span>Navigate with click · Press ESC to close</span>
              <span className="text-accent2">CareerPilot AI Quick Navigator</span>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
