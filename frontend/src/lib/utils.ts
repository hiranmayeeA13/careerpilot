import { twMerge } from 'tailwind-merge';
import clsx, { type ClassValue } from 'clsx';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function scoreColor(score: number) {
  if (score >= 75) return '#36d7b7';
  if (score >= 50) return '#6c8cff';
  return '#ff6b7a';
}

export function categoryColor(category: string) {
  switch (category) {
    case 'Job-Ready':
      return 'text-accent2 border-accent2/40 bg-accent2/10';
    case 'Developing':
      return 'text-accent border-accent/40 bg-accent/10';
    default:
      return 'text-warn border-warn/40 bg-warn/10';
  }
}

export function evidenceColor(status: string) {
  switch (status) {
    case 'Strongly-supported':
      return 'bg-accent2/20 text-accent2 border-accent2/30';
    case 'Project-demonstrated':
      return 'bg-accent/20 text-accent border-accent/30';
    case 'Interview-demonstrated':
      return 'bg-warn/20 text-warn border-warn/30';
    case 'Resume-supported':
      return 'bg-white/10 text-white/70 border-white/15';
    default:
      return 'bg-danger/15 text-danger border-danger/30';
  }
}
