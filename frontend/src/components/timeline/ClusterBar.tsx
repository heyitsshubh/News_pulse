import React from 'react';
interface ClusterBarProps {
  x?: number;
  y?: number;
  width?: number;
  height?: number;
  intensity?: number;
  isSelected?: boolean;
  onClick?: () => void;
  clusterId?: string;
}
export const ClusterBar: React.FC<ClusterBarProps> = (props) => {
  const {
    x = 0,
    y = 0,
    width = 0,
    height = 0,
    intensity = 0.5,
    isSelected = false,
    onClick,
  } = props;
  if (!width || width <= 0) return null;
  const clampedIntensity = Math.max(0.1, Math.min(1, intensity));
  const startColor = `rgba(99, 102, 241, ${0.5 + clampedIntensity * 0.5})`;
  const endColor = `rgba(139, 92, 246, ${0.6 + clampedIntensity * 0.4})`;
  const barHeight = Math.max(height, 8);
  const barY = y + (height - barHeight) / 2;
  const radius = Math.min(6, barHeight / 2, width / 2);
  const gradId = `grad-${Math.abs(x * 1000).toFixed(0)}-${Math.abs(y * 100).toFixed(0)}`;
  const glowId = `glow-${Math.abs(x * 1000).toFixed(0)}-${Math.abs(y * 100).toFixed(0)}`;
  return (
    <g
      onClick={onClick}
      style={{ cursor: 'pointer' }}
    >
      <defs>
        <linearGradient id={gradId} x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stopColor={startColor} />
          <stop offset="100%" stopColor={endColor} />
        </linearGradient>
        {isSelected && (
          <filter id={glowId} x="-20%" y="-50%" width="140%" height="200%">
            <feGaussianBlur stdDeviation="4" result="blur" />
            <feMerge>
              <feMergeNode in="blur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        )}
      </defs>
      {}
      {isSelected && (
        <rect
          x={x - 2}
          y={barY - 4}
          width={width + 4}
          height={barHeight + 8}
          rx={radius + 2}
          fill="rgba(99, 102, 241, 0.25)"
          style={{ filter: 'blur(6px)' }}
        />
      )}
      {}
      <rect
        x={x}
        y={barY}
        width={width}
        height={barHeight}
        rx={radius}
        fill={`url(#${gradId})`}
        stroke={isSelected ? 'rgba(99, 102, 241, 0.8)' : 'rgba(99, 102, 241, 0.3)'}
        strokeWidth={isSelected ? 1.5 : 0.5}
        style={{
          transition: 'all 200ms ease',
          filter: isSelected ? `url(#${glowId})` : undefined,
        }}
      />
      {}
      <rect
        x={x}
        y={barY}
        width={width}
        height={barHeight / 2}
        rx={radius}
        fill="rgba(255,255,255,0.06)"
        style={{ pointerEvents: 'none' }}
      />
    </g>
  );
};