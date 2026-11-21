import { NavLink, Outlet } from 'react-router-dom';
import {
  Gauge,
  FlaskConical,
  UserCircle2,
  Compass,
  FolderGit2,
  Users2,
  Rocket,
  ChevronDown,
  Upload as UploadIcon,
  Briefcase,
  CalendarDays,
  Mic2,
  SendHorizonal,
} from 'lucide-react';
import { useState } from 'react';
import { useCandidate } from '../state/CandidateContext';
import { ThemeSwitcher } from './ThemeSwitcher';
import { CommandPalette } from './CommandPalette';
import { cn } from '../lib/utils';

const TABS = [
  { to: '/', label: 'Readiness', icon: Gauge, end: true },
  { to: '/about-me', label: 'About Me', icon: UserCircle2 },
  { to: '/intake', label: 'Resume Intake', icon: UploadIcon },
  { to: '/simulator', label: 'What-If Simulator', icon: FlaskConical },
  { to: '/twin', label: 'Career Twin', icon: UserCircle2 },
  { to: '/job-market', label: 'Job Market & Gap', icon: Briefcase },
  { to: '/plan', label: 'Learning Plan', icon: CalendarDays },
  { to: '/reality-check', label: 'Reality Check', icon: Compass },
  { to: '/portfolio', label: 'Portfolio Generator', icon: FolderGit2 },
  { to: '/mock-interview', label: 'Mock Interview', icon: Mic2 },
  { to: '/applications', label: 'Applications', icon: SendHorizonal },
  { to: '/compare', label: 'Compare Candidates', icon: Users2 },
];

function CandidateSwitcher() {
  const { candidateId, setCandidateId, candidate, allCandidates } = useCandidate();
  const [open, setOpen] = useState(false);

  return (
    <div className="relative">
      <button
        onClick={() => setOpen((o) => !o)}
        className="flex items-center gap-2.5 pl-2 pr-3 py-1.5 rounded-xl border border-white/10 bg-white/5 hover:bg-white/10 transition-colors shadow-sm"
      >
        <div className="w-7 h-7 rounded-full bg-gradient-to-br from-accent to-accent2 flex items-center justify-center text-xs font-bold text-ink">
          {candidate.name.split(' ').map((n) => n[0]).join('')}
        </div>
        <div className="text-left leading-tight hidden sm:block">
          <p className="text-xs font-semibold text-white">{candidate.name}</p>
          <p className="text-[10px] text-white/40">{candidate.role}</p>
        </div>
        <ChevronDown size={14} className="text-white/40" />
      </button>
      {open && (
        <>
          <div className="fixed inset-0 z-40" onClick={() => setOpen(false)} />
          <div className="absolute right-0 mt-2 w-64 card p-1.5 z-50 fade-up max-h-80 overflow-y-auto scrollbar-thin space-y-1">
            <div className="px-2.5 py-1 border-b border-white/5">
              <p className="text-[10px] uppercase font-bold tracking-wider text-white/40">Switch Candidate</p>
            </div>
            {allCandidates.map((c) => (
              <button
                key={c.id}
                onClick={() => {
                  setCandidateId(c.id);
                  setOpen(false);
                }}
                className={cn(
                  'w-full text-left px-3 py-2 rounded-xl text-xs flex items-center justify-between hover:bg-white/5 transition-colors',
                  c.id === candidateId ? 'bg-accent/15 text-accent font-semibold border border-accent/20' : 'text-white/70'
                )}
              >
                <span>
                  <span className="text-white font-medium block">{c.name}</span>
                  <span className="block text-[10px] text-white/40 mt-0.5">{c.role}</span>
                </span>
                {c.id === candidateId && <span className="text-[10px] text-accent font-bold">Active</span>}
              </button>
            ))}
          </div>
        </>
      )}
    </div>
  );
}

export function Layout() {
  return (
    <div className="min-h-screen flex flex-col lg:flex-row">
      {/* Sidebar (desktop) */}
      <aside className="hidden lg:flex flex-col w-64 shrink-0 border-r border-white/5 p-5 gap-6 sticky top-0 h-screen">
        <div className="flex items-center gap-2.5 px-1">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-accent to-accent2 flex items-center justify-center shadow-md">
            <Rocket size={18} className="text-ink" />
          </div>
          <div>
            <p className="font-extrabold text-white leading-none text-base tracking-tight">CareerPilot</p>
            <p className="text-[10px] uppercase font-bold tracking-wider text-accent mt-1 leading-none">AI Readiness Engine</p>
          </div>
        </div>

        <nav className="flex flex-col gap-1 overflow-y-auto scrollbar-thin pr-1">
          {TABS.map((tab) => (
            <NavLink
              key={tab.to}
              to={tab.to}
              end={tab.end}
              className={({ isActive }) =>
                cn(
                  'flex items-center gap-2.5 px-3 py-2 rounded-xl text-[13px] font-medium transition-all',
                  isActive
                    ? 'bg-accent/15 text-accent border border-accent/30 shadow-sm font-semibold'
                    : 'text-white/60 hover:text-white hover:bg-white/5 border border-transparent'
                )
              }
            >
              <tab.icon size={17} />
              {tab.label}
            </NavLink>
          ))}
        </nav>

        <div className="mt-auto p-3 rounded-xl bg-white/[0.02] border border-white/5 text-[11px] text-white/40 text-center leading-relaxed">
          Deterministic scoring · No hiring guarantees
        </div>
      </aside>

      {/* Main column */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Topbar */}
        <header className="flex items-center justify-between gap-3 px-5 lg:px-8 py-3.5 border-b border-white/5 sticky top-0 bg-ink/80 backdrop-blur-md z-30">
          <div className="flex items-center gap-3">
            <div className="lg:hidden flex items-center gap-2">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-accent to-accent2 flex items-center justify-center">
                <Rocket size={16} className="text-ink" />
              </div>
              <p className="font-bold text-white text-sm">CareerPilot</p>
            </div>
            <CommandPalette />
          </div>

          <div className="flex items-center gap-2.5">
            <ThemeSwitcher />
            <CandidateSwitcher />
          </div>
        </header>

        {/* Mobile tab strip */}
        <nav className="lg:hidden flex gap-1 overflow-x-auto scrollbar-thin px-4 py-2 border-b border-white/5">
          {TABS.map((tab) => (
            <NavLink
              key={tab.to}
              to={tab.to}
              end={tab.end}
              className={({ isActive }) =>
                cn(
                  'flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium whitespace-nowrap transition-colors shrink-0',
                  isActive ? 'bg-accent/15 text-accent font-semibold border border-accent/30' : 'text-white/50 hover:text-white'
                )
              }
            >
              <tab.icon size={14} />
              {tab.label}
            </NavLink>
          ))}
        </nav>

        <main className="flex-1 px-5 lg:px-8 py-6 max-w-6xl w-full mx-auto">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
