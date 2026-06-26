import React from 'react';
import { Layers } from 'lucide-react';

export const TimelineEmpty: React.FC = () => {
  return (
    <div
      className="animate-fade-in"
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '80px 32px',
        gap: '20px',
        textAlign: 'center',
      }}
    >
      {/* Icon wrapper */}
      <div
        className="animate-float"
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          width: '88px',
          height: '88px',
          borderRadius: '24px',
          background: 'linear-gradient(135deg, rgba(99,102,241,0.12) 0%, rgba(139,92,246,0.12) 100%)',
          border: '1px solid rgba(99,102,241,0.2)',
          boxShadow: '0 0 32px rgba(99,102,241,0.1)',
          marginBottom: '8px',
        }}
      >
        <Layers
          size={40}
          style={{
            color: '#6366f1',
            filter: 'drop-shadow(0 0 8px rgba(99,102,241,0.6))',
          }}
        />
      </div>

      <div>
        <h3
          style={{
            fontSize: '22px',
            fontWeight: 700,
            color: 'var(--color-text-primary)',
            letterSpacing: '-0.02em',
            marginBottom: '8px',
          }}
        >
          No clusters yet
        </h3>
        <p
          style={{
            fontSize: '14px',
            color: 'var(--color-text-secondary)',
            maxWidth: '300px',
            lineHeight: 1.6,
          }}
        >
          Click{' '}
          <span
            style={{
              color: 'var(--color-accent-primary)',
              fontWeight: 600,
            }}
          >
            Refresh News
          </span>{' '}
          in the top bar to ingest the latest stories and build topic clusters.
        </p>
      </div>

      {/* Decorative dots */}
      <div style={{ display: 'flex', gap: '8px', marginTop: '8px' }}>
        {[0, 0.2, 0.4].map((delay, i) => (
          <div
            key={i}
            style={{
              width: '6px',
              height: '6px',
              borderRadius: '50%',
              background: 'var(--color-accent-primary)',
              opacity: 0.4,
              animation: `pulse 2s ${delay}s ease-in-out infinite`,
            }}
          />
        ))}
      </div>
    </div>
  );
};
