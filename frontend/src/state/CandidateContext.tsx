import { createContext, useContext, useState, useMemo, type ReactNode } from 'react';

export interface KnownCandidate {
  id: string;
  name: string;
  role: string;
}

const SEED_CANDIDATES: KnownCandidate[] = [
  { id: 'cand_devops_001', name: 'Alex Rivera', role: 'DevOps Engineer' },
  { id: 'cand_backend_001', name: 'Priya Sharma', role: 'Backend Engineer' },
];

const EXTRA_STORAGE_KEY = 'careerpilot.extraCandidates';
const SELECTED_STORAGE_KEY = 'careerpilot.candidateId';

function loadExtraCandidates(): KnownCandidate[] {
  try {
    const raw = localStorage.getItem(EXTRA_STORAGE_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
}

interface CandidateContextValue {
  candidateId: string;
  setCandidateId: (id: string) => void;
  candidate: KnownCandidate;
  allCandidates: KnownCandidate[];
  addCandidate: (c: KnownCandidate, save?: boolean) => void;
}

const CandidateContext = createContext<CandidateContextValue | null>(null);

export function CandidateProvider({ children }: { children: ReactNode }) {
  const [extraCandidates, setExtraCandidates] = useState<KnownCandidate[]>(loadExtraCandidates);
  const [sessionCandidates, setSessionCandidates] = useState<KnownCandidate[]>([]);
  const [candidateId, setCandidateIdState] = useState<string>(() => {
    return localStorage.getItem(SELECTED_STORAGE_KEY) || SEED_CANDIDATES[0].id;
  });

  const allCandidates = useMemo(() => {
    const combined = [
      ...SEED_CANDIDATES,
      ...extraCandidates,
      ...sessionCandidates.filter((c) => !extraCandidates.some((p) => p.id === c.id)),
    ];
    const seenIds = new Set<string>();
    const seenNames = new Set<string>();
    const unique: KnownCandidate[] = [];
    for (const c of combined) {
      const normName = c.name.trim().toLowerCase();
      if (!seenIds.has(c.id) && !seenNames.has(normName)) {
        seenIds.add(c.id);
        seenNames.add(normName);
        unique.push(c);
      }
    }
    return unique;
  }, [extraCandidates, sessionCandidates]);

  const setCandidateId = (id: string) => {
    const isPersistent = SEED_CANDIDATES.some(c => c.id === id) || extraCandidates.some(c => c.id === id);
    if (isPersistent) localStorage.setItem(SELECTED_STORAGE_KEY, id);
    else localStorage.removeItem(SELECTED_STORAGE_KEY);
    setCandidateIdState(id);
  };

  const addCandidate = (c: KnownCandidate, save = true) => {
    if (!save) { setSessionCandidates(prev => [...prev.filter(p => p.id !== c.id), c]); localStorage.removeItem(SELECTED_STORAGE_KEY); setCandidateIdState(c.id); return; }
    setExtraCandidates((prev) => {
      const next = [...prev.filter((p) => p.id !== c.id), c];
      localStorage.setItem(EXTRA_STORAGE_KEY, JSON.stringify(next));
      return next;
    });
    localStorage.setItem(SELECTED_STORAGE_KEY, c.id);
    setCandidateIdState(c.id);
  };

  const candidate = useMemo(
    () => allCandidates.find((c) => c.id === candidateId) || allCandidates[0],
    [candidateId, allCandidates]
  );

  return (
    <CandidateContext.Provider value={{ candidateId, setCandidateId, candidate, allCandidates, addCandidate }}>
      {children}
    </CandidateContext.Provider>
  );
}

export function useCandidate() {
  const ctx = useContext(CandidateContext);
  if (!ctx) throw new Error('useCandidate must be used within CandidateProvider');
  return ctx;
}

// Kept for the Compare tab, which intentionally compares only the two seeded candidates.
export const KNOWN_CANDIDATES = SEED_CANDIDATES;
