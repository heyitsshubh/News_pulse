/// <reference types="vite/client" />
export const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:3001';

export const SOURCES = [
  { key: 'bbc', label: 'BBC News', color: '#ef4444' },
  { key: 'npr', label: 'NPR', color: '#3b82f6' },
  { key: 'guardian', label: 'The Guardian', color: '#14b8a6' },
] as const;

export const POLL_INTERVAL_MS = 2000;
