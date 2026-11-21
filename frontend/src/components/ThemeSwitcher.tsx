import { useState } from 'react';
import { Moon, Flame, Check } from 'lucide-react';
import { useTheme, type Theme } from '../state/ThemeContext';

const THEME_OPTIONS: { id: Theme; label: string; sub: string; icon: any; previewColor: string; swatches: string[] }[] = [
  {
    id: 'warm-terracotta',
    label: 'Batch 1: Warm Terracotta',
    sub: 'Espresso, Mocha & Caramel Gradient',
    icon: Flame,
    previewColor: '#D18B47',
    swatches: ['#3E2723', '#A0522D', '#D18B47', '#E4C7A1', '#FFFCF8'],
  },
  {
    id: 'midnight-slate',
    label: 'Batch 2: Midnight Slate',
    sub: 'Obsidian Steel Dark Mode',
    icon: Moon,
    previewColor: '#0F172A',
    swatches: ['#0F172A', '#334155', '#64748B', '#94A3B8', '#FFFFFF'],
  },
];

export function ThemeSwitcher() {
  const { theme, setTheme } = useTheme();
  const [open, setOpen] = useState(false);

  const activeOption = THEME_OPTIONS.find((t) => t.id === theme) || THEME_OPTIONS[0];
  const IconComponent = activeOption.icon;

  return (
    <div className="relative">
      <button
        onClick={() => setOpen((o) => !o)}
        className="flex items-center gap-2 px-3 py-1.5 rounded-xl border border-white/10 bg-black/30 hover:bg-black/45 transition-all text-xs font-medium text-white shadow-sm"
        title="Switch color palette theme"
      >
        <span
          className="w-3.5 h-3.5 rounded-full border border-white/20 shadow-sm shrink-0"
          style={{ backgroundColor: activeOption.previewColor }}
        />
        <IconComponent size={14} className="text-accent" />
        <span className="hidden sm:inline">{activeOption.label}</span>
      </button>

      {open && (
        <>
          <div className="fixed inset-0 z-40" onClick={() => setOpen(false)} />
          <div className="absolute right-0 mt-2 w-64 bg-panel border border-white/15 rounded-2xl p-2.5 z-50 fade-up space-y-1 shadow-2xl backdrop-blur-2xl">
            <div className="px-2.5 py-1.5 border-b border-white/5">
              <p className="text-[10px] uppercase font-bold tracking-wider text-white/40">Select Visual Palette</p>
            </div>
            {THEME_OPTIONS.map((opt) => {
              const OptIcon = opt.icon;
              const isSelected = opt.id === theme;
              return (
                <button
                  key={opt.id}
                  onClick={() => {
                    setTheme(opt.id);
                    setOpen(false);
                  }}
                  className={`w-full text-left p-2.5 rounded-xl text-xs flex items-center justify-between transition-colors ${
                    isSelected
                      ? 'bg-accent/15 text-accent font-semibold border border-accent/25'
                      : 'hover:bg-white/5 text-white/70 border border-transparent'
                  }`}
                >
                  <div className="flex items-center gap-2.5">
                    <span
                      className="w-4 h-4 rounded-full border border-white/20 shrink-0"
                      style={{ backgroundColor: opt.previewColor }}
                    />
                    <div>
                      <p className="text-white text-xs font-medium leading-none">{opt.label}</p>
                      <p className="text-[10px] text-white/40 mt-1 leading-tight">{opt.sub}</p>
                      <div className="flex items-center gap-1 mt-1.5">
                        {opt.swatches.map((color, idx) => (
                          <span
                            key={idx}
                            className="w-2.5 h-2.5 rounded-full border border-black/20 shrink-0"
                            style={{ backgroundColor: color }}
                            title={color}
                          />
                        ))}
                      </div>
                    </div>
                  </div>
                  {isSelected && <Check size={14} className="text-accent shrink-0" />}
                </button>
              );
            })}
          </div>
        </>
      )}
    </div>
  );
}
