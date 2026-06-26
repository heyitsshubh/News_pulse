import React from 'react';

type SpinnerSize = 'xs' | 'sm' | 'md' | 'lg';

interface SpinnerProps {
  size?: SpinnerSize;
  color?: string;
  style?: React.CSSProperties;
}

const SIZE_MAP: Record<SpinnerSize, number> = {
  xs: 12,
  sm: 16,
  md: 24,
  lg: 36,
};

const BORDER_MAP: Record<SpinnerSize, number> = {
  xs: 1.5,
  sm: 2,
  md: 2.5,
  lg: 3,
};

export const Spinner: React.FC<SpinnerProps> = ({
  size = 'md',
  color = 'var(--color-accent-primary)',
  style,
}) => {
  const dim = SIZE_MAP[size];
  const border = BORDER_MAP[size];

  return (
    <span
      style={{
        display: 'inline-block',
        width: `${dim}px`,
        height: `${dim}px`,
        borderRadius: '50%',
        border: `${border}px solid transparent`,
        borderTopColor: color,
        borderRightColor: color,
        animation: 'spin 0.7s linear infinite',
        flexShrink: 0,
        ...style,
      }}
      role="status"
      aria-label="Loading"
    />
  );
};
