import React, { useMemo, useCallback } from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from 'recharts';
import { format } from 'date-fns';
import type { TimelineItem } from '../../types/timeline';
import { ClusterBar } from './ClusterBar';
import { TimelineEmpty } from './TimelineEmpty';
import { Spinner } from '../ui/Spinner';
interface TimelineChartProps {
  items: TimelineItem[];
  selectedClusterId: string | null;
  onClusterClick: (id: string, label: string) => void;
  isLoading: boolean;
  isError: boolean;
}
const TimelineSkeleton: React.FC = () => (
  <div style={{ padding: '24px 0', display: 'flex', flexDirection: 'column', gap: '14px' }}>
    {Array.from({ length: 6 }).map((_, i) => (
      <div key={i} style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
        <div
          className="skeleton"
          style={{
            width: `${60 + (i % 3) * 20}px`,
            height: '14px',
            flexShrink: 0,
          }}
        />
        <div
          className="skeleton"
          style={{
            height: '32px',
            width: `${120 + Math.sin(i) * 80 + 80}px`,
            marginLeft: `${20 + (i * 37) % 80}px`,
            borderRadius: '6px',
          }}
        />
      </div>
    ))}
  </div>
);
const CustomTooltip: React.FC<{
  active?: boolean;
  payload?: Array<{ payload: TimelineItem & { startMs: number; endMs: number } }>;
}> = ({ active, payload }) => {
  if (!active || !payload?.length) return null;
  const item = payload[0]?.payload;
  if (!item) return null;
  const start = item.start ? format(new Date(item.start), 'MMM d, HH:mm') : '—';
  const end = item.end ? format(new Date(item.end), 'MMM d, HH:mm') : '—';
  const intensityPct = Math.round((item.intensity ?? 0) * 100);
  return (
    <div
      style={{
        background: '#0f172a',
        border: '1px solid rgba(99, 102, 241, 0.25)',
        borderRadius: '10px',
        padding: '12px 16px',
        boxShadow: '0 8px 32px rgba(0,0,0,0.6)',
        maxWidth: '240px',
        fontFamily: 'var(--font-sans)',
        animation: 'fadeInFast 100ms ease',
        pointerEvents: 'none',
      }}
    >
      <p
        style={{
          fontSize: '13px',
          fontWeight: 700,
          color: '#f1f5f9',
          marginBottom: '8px',
          lineHeight: 1.3,
        }}
      >
        {item.label}
      </p>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
        <span style={{ fontSize: '11px', color: '#94a3b8' }}>
          🕐 {start} → {end}
        </span>
        <span style={{ fontSize: '11px', color: '#94a3b8' }}>
          📰 {item.count} article{item.count !== 1 ? 's' : ''}
        </span>
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            marginTop: '2px',
          }}
        >
          <div
            style={{
              flex: 1,
              height: '3px',
              borderRadius: '9999px',
              background: 'rgba(99, 102, 241, 0.15)',
              overflow: 'hidden',
            }}
          >
            <div
              style={{
                width: `${intensityPct}%`,
                height: '100%',
                background: 'linear-gradient(90deg, #6366f1, #8b5cf6)',
                borderRadius: '9999px',
              }}
            />
          </div>
          <span
            style={{
              fontSize: '10px',
              color: '#6366f1',
              fontWeight: 700,
              minWidth: '28px',
              textAlign: 'right',
            }}
          >
            {intensityPct}%
          </span>
        </div>
      </div>
      <p
        style={{
          fontSize: '10px',
          color: '#475569',
          marginTop: '8px',
          fontStyle: 'italic',
        }}
      >
        Click to view articles →
      </p>
    </div>
  );
};
const CustomYTick: React.FC<{
  x?: number;
  y?: number;
  payload?: { value: string };
}> = ({ x = 0, y = 0, payload }) => {
  const label = payload?.value ?? '';
  const truncated = label.length > 22 ? label.slice(0, 22) + '…' : label;
  return (
    <text
      x={x}
      y={y}
      dy={5}
      textAnchor="end"
      style={{
        fill: '#94a3b8',
        fontSize: '12px',
        fontFamily: 'Inter, sans-serif',
        fontWeight: 500,
      }}
    >
      {truncated}
    </text>
  );
};
const CustomXTick: React.FC<{
  x?: number;
  y?: number;
  payload?: { value: number };
}> = ({ x = 0, y = 0, payload }) => {
  const ts = payload?.value;
  if (!ts) return null;
  const label = format(new Date(ts), 'HH:mm');
  return (
    <text
      x={x}
      y={y}
      dy={14}
      textAnchor="middle"
      style={{ fill: '#475569', fontSize: '10px', fontFamily: 'Inter, sans-serif' }}
    >
      {label}
    </text>
  );
};
export const TimelineChart: React.FC<TimelineChartProps> = ({
  items,
  selectedClusterId,
  onClusterClick,
  isLoading,
  isError,
}) => {
  const chartData = useMemo(() => {
    const safeItems = Array.isArray(items) ? items : [];
    return safeItems
      .filter((item) => item.start && item.end)
      .map((item) => {
        const startMs = new Date(item.start).getTime();
        let endMs = new Date(item.end).getTime();
        if (endMs - startMs < 3600000) {
          endMs = startMs + 3600000;
        }
        return {
          ...item,
          startMs,
          endMs,
          range: [startMs, endMs] as [number, number],
          labelShort:
            item.label.length > 24 ? item.label.slice(0, 24) + '…' : item.label,
        };
      })
      .sort((a, b) => a.startMs - b.startMs);
  }, [items]);
  const allTimestamps = useMemo(
    () => chartData.flatMap((d) => [d.startMs, d.endMs]),
    [chartData]
  );
  const domainMin = allTimestamps.length ? Math.min(...allTimestamps) : 0;
  const domainMax = allTimestamps.length ? Math.max(...allTimestamps) : 1;
  const padding = (domainMax - domainMin) * 0.05;
  const domain: [number, number] = [
    domainMin - padding,
    domainMax + padding,
  ];
  const handleBarClick = useCallback(
    (data: { id: string; label: string }) => {
      if (data?.id) onClusterClick(data.id, data.label);
    },
    [onClusterClick]
  );
  const rowHeight = 48;
  const chartHeight = Math.max(300, chartData.length * rowHeight + 60);
  if (isError) {
    return (
      <div
        style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          padding: '60px',
          gap: '12px',
          color: 'var(--color-error)',
        }}
      >
        <span style={{ fontSize: '32px' }}>⚠️</span>
        <p style={{ fontSize: '14px', fontWeight: 600 }}>
          Failed to load timeline data
        </p>
        <p style={{ fontSize: '12px', color: 'var(--color-text-muted)' }}>
          Check your API connection and try refreshing.
        </p>
      </div>
    );
  }
  if (isLoading) {
    return (
      <div>
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '10px',
            padding: '20px 24px 0',
            color: 'var(--color-text-muted)',
            fontSize: '13px',
          }}
        >
          <Spinner size="sm" />
          Loading timeline…
        </div>
        <div style={{ padding: '0 24px' }}>
          <TimelineSkeleton />
        </div>
      </div>
    );
  }
  if (!chartData.length) {
    return <TimelineEmpty />;
  }
  return (
    <div className="animate-fade-in" style={{ width: '100%' }}>
      <ResponsiveContainer width="100%" height={chartHeight}>
        <BarChart
          layout="vertical"
          data={chartData}
          margin={{ top: 8, right: 32, bottom: 8, left: 160 }}
          barSize={Math.min(28, rowHeight - 16)}
          onClick={(data: any) => {
            if (data?.activePayload?.[0]?.payload) {
              handleBarClick(data.activePayload[0].payload);
            }
          }}
        >
          <CartesianGrid
            horizontal={false}
            stroke="rgba(30, 41, 59, 0.8)"
            strokeDasharray="4 4"
          />
          {}
          <XAxis
            type="number"
            dataKey="endMs"
            domain={domain}
            scale="time"
            tickCount={8}
            tick={<CustomXTick />}
            tickLine={false}
            axisLine={{ stroke: 'rgba(30, 41, 59, 0.6)' }}
          />
          {}
          <YAxis
            type="category"
            dataKey="label"
            width={155}
            tick={<CustomYTick />}
            tickLine={false}
            axisLine={false}
          />
          <Tooltip
            content={<CustomTooltip />}
            cursor={{
              fill: 'rgba(99, 102, 241, 0.05)',
              stroke: 'rgba(99, 102, 241, 0.15)',
              strokeWidth: 1,
            }}
          />
          <Bar
            dataKey="range"
            isAnimationActive={true}
            animationDuration={600}
            animationEasing="ease-out"
            shape={(barProps: any) => {
              const { payload, ...rest } = barProps;
              const isSelected = payload?.id === selectedClusterId;
              return (
                <ClusterBar
                  {...rest}
                  intensity={payload?.intensity ?? 0.5}
                  isSelected={isSelected}
                  clusterId={payload?.id}
                  onClick={() => {
                    if (payload?.id) onClusterClick(payload.id, payload.label);
                  }}
                />
              );
            }}
          >
            {chartData.map((entry) => (
              <Cell
                key={entry.id}
                fill={`rgba(99,102,241,${0.4 + entry.intensity * 0.6})`}
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};