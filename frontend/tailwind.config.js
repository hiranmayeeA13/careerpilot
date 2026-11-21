/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        ink: 'var(--bg-ink)',
        panel: 'var(--bg-panel)',
        panel2: 'var(--bg-panel2)',
        accent: 'var(--color-accent)',
        accent2: 'var(--color-accent2)',
        warn: '#f6a94c',
        danger: '#ff6b7a',
        batch1: {
          espresso: '#3E2723',
          terracotta: '#A0522D',
          caramel: '#D18B47',
          almond: '#E4C7A1',
          cream: '#F6E6D9',
          peach: '#FFF0E8',
          white: '#FFFCF8',
        },
        batch2: {
          slate900: '#0F172A',
          slate700: '#334155',
          slate500: '#64748B',
          slate400: '#94A3B8',
          slate200: '#E2E8F0',
          slate50: '#F8FAFC',
          white: '#FFFFFF',
        },
      },
      fontFamily: {
        sans: ['Plus Jakarta Sans', 'Inter', 'ui-sans-serif', 'system-ui', 'sans-serif'],
      },
      boxShadow: {
        glow: '0 0 0 1px var(--border-glow), 0 8px 30px rgba(0,0,0,0.3)',
      },
    },
  },
  plugins: [],
};
