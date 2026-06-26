import React from 'react';
interface BadgeProps {
  children?: React.ReactNode;
  color?: string;
  source?: 'bbc' | 'npr' | 'guardian';
  variant?: 'filled' | 'outlined';
  size?: 'sm' | 'md';
  style?: React.CSSProperties;
}
const SOURCE_COLORS: Record<string, string> = {
  bbc: '#ef4444',
  npr: '#3b82f6',
  guardian: '#14b8a6',
};
const SOURCE_LABELS: Record<string, string> = {
  bbc: 'BBC',
  npr: 'NPR',
  guardian: 'Guardian',
};
export const Badge: React.FC<BadgeProps> = ({
  children,
  color,
  source,
  variant = 'filled',
  size = 'sm',
  style,
}) => {
  const resolvedColor = source ? SOURCE_COLORS[source] : (color ?? '#6366f1');
  const label = source ? SOURCE_LABELS[source] : children;
  const baseStyle: React.CSSProperties = {
    display: 'inline-flex',
    alignItems: 'center',
    borderRadius: '9999px',
    fontWeight: 600,
    letterSpacing: '0.04em',
    textTransform: 'uppercase',
    fontFamily: 'var(--font-sans)',
    fontSize: size === 'sm' ? '10px' : '12px',
    padding: size === 'sm' ? '2px 8px' : '4px 12px',
    whiteSpace: 'nowrap',
    transition: 'all 150ms ease',
    ...(variant === 'filled'
      ? {
          background: `${resolvedColor}20`,
          color: resolvedColor,
          border: `1px solid ${resolvedColor}40`,
        }
      : {
          background: 'transparent',
          color: resolvedColor,
          border: `1px solid ${resolvedColor}`,
        }),
    ...style,
  };
  return <span style={baseStyle}>{label}</span>;
};