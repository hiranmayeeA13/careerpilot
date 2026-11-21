import { AlertTriangle, Loader2, RefreshCw } from 'lucide-react';
import { cn } from '../lib/utils';

export function Spinner({ label }: { label?: string }) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 py-16 text-white/50">
      <Loader2 className="animate-spin" size={28} />
      {label && <p className="text-sm">{label}</p>}
    </div>
  );
}

export function ErrorBanner({ message, onRetry }: { message: string; onRetry?: () => void }) {
  return (
    <div className="card border-danger/30 bg-danger/10 p-5 flex items-start gap-3 fade-up">
      <AlertTriangle className="text-danger shrink-0 mt-0.5" size={20} />
      <div className="flex-1">
        <p className="text-sm text-danger font-medium">{message}</p>
        <p className="text-xs text-white/40 mt-1">
          Tip: run the backend with <code className="text-white/60">uvicorn app.main:app --port 8008</code> and check
          VITE_API_BASE_URL in .env
        </p>
      </div>
      {onRetry && (
        <button
          onClick={onRetry}
          className="flex items-center gap-1.5 text-xs font-medium px-3 py-1.5 rounded-lg bg-danger/20 hover:bg-danger/30 transition-colors text-danger shrink-0"
        >
          <RefreshCw size={13} /> Retry
        </button>
      )}
    </div>
  );
}

export function Badge({ children, className }: { children: React.ReactNode; className?: string }) {
  return (
    <span className={cn('inline-flex items-center gap-1 text-xs font-medium px-2.5 py-1 rounded-full border', className)}>
      {children}
    </span>
  );
}

export function SectionTitle({
  icon,
  title,
  subtitle,
}: {
  icon?: React.ReactNode;
  title: string;
  subtitle?: string;
}) {
  return (
    <div className="flex items-start gap-3 mb-5">
      {icon && <div className="p-2 rounded-xl bg-accent/10 text-accent shrink-0">{icon}</div>}
      <div>
        <h2 className="text-lg font-semibold text-white tracking-tight">{title}</h2>
        {subtitle && <p className="text-sm text-white/45 mt-0.5">{subtitle}</p>}
      </div>
    </div>
  );
}

export function StatPill({ label, value, accent }: { label: string; value: string | number; accent?: string }) {
  return (
    <div className="flex-1 min-w-[110px] card p-4">
      <p className="text-[11px] uppercase tracking-wider text-white/40 font-medium">{label}</p>
      <p className={cn('text-2xl font-bold mt-1', accent)}>{value}</p>
    </div>
  );
}
