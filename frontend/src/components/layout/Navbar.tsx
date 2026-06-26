import React from 'react';
import { Radio } from 'lucide-react';
import { RefreshButton } from '../ingest/RefreshButton';
import { useAppSelector } from '../../store/hooks';
import { formatDistanceToNow } from 'date-fns';
export const Navbar: React.FC = () => {
  const lastRefreshed = useAppSelector((state) => state.ingest.lastRefreshed);
  const refreshedText = lastRefreshed
    ? `Updated ${formatDistanceToNow(new Date(lastRefreshed), { addSuffix: true })}`
    : 'Not yet refreshed';
  return (
    <nav
      style={{
        position: 'sticky',
        top: 0,
        zIndex: 'var(--z-navbar)' as unknown as number,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '0 28px',
        height: '64px',
        background: 'rgba(10, 15, 30, 0.85)',
        backdropFilter: 'blur(12px)',
        WebkitBackdropFilter: 'blur(12px)',
        borderBottom: '1px solid rgba(99, 102, 241, 0.1)',
        boxShadow: '0 1px 0 rgba(99, 102, 241, 0.05)',
      }}
    >
      {}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '10px',
          textDecoration: 'none',
        }}
      >
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            width: '36px',
            height: '36px',
            borderRadius: '10px',
            background: 'linear-gradient(135deg, #6366f1, #8b5cf6)',
            boxShadow: '0 0 16px rgba(99, 102, 241, 0.4)',
            flexShrink: 0,
          }}
        >
          <Radio size={18} color="#ffffff" />
        </div>
        <div>
          <span
            style={{
              fontSize: '18px',
              fontWeight: 800,
              letterSpacing: '-0.03em',
              background: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #a78bfa 100%)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              backgroundClip: 'text',
              display: 'block',
              lineHeight: 1.1,
            }}
          >
            News Pulse
          </span>
          <span
            style={{
              fontSize: '10px',
              fontWeight: 500,
              color: 'var(--color-text-muted)',
              letterSpacing: '0.08em',
              textTransform: 'uppercase',
              display: 'block',
              lineHeight: 1,
            }}
          >
            Live Topic Clusters
          </span>
        </div>
      </div>
      {}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '6px',
          fontSize: '12px',
          color: 'var(--color-text-muted)',
          fontWeight: 500,
        }}
      >
        <span
          style={{
            display: 'inline-block',
            width: '6px',
            height: '6px',
            borderRadius: '50%',
            background: lastRefreshed ? 'var(--color-success)' : 'var(--color-text-muted)',
            boxShadow: lastRefreshed ? '0 0 6px var(--color-success)' : 'none',
            animation: lastRefreshed ? 'none' : 'pulse 2s ease-in-out infinite',
          }}
        />
        {refreshedText}
      </div>
      {}
      <RefreshButton />
    </nav>
  );
};