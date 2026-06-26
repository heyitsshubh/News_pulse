import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Home, Compass } from 'lucide-react';
import { Button } from '../components/ui/Button';

export const NotFoundPage: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div
      style={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: 'linear-gradient(160deg, #0a0f1e 0%, #0d1424 60%, #080c18 100%)',
        fontFamily: 'var(--font-sans)',
        padding: '32px',
      }}
    >
      <div
        className="animate-fade-in"
        style={{
          textAlign: 'center',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          gap: '20px',
          maxWidth: '440px',
        }}
      >
        {/* 404 graphic */}
        <div
          className="animate-float"
          style={{
            position: 'relative',
            marginBottom: '8px',
          }}
        >
          <div
            style={{
              fontSize: '120px',
              fontWeight: 900,
              letterSpacing: '-0.05em',
              lineHeight: 1,
              background: 'linear-gradient(135deg, rgba(99,102,241,0.3) 0%, rgba(139,92,246,0.3) 100%)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              backgroundClip: 'text',
              userSelect: 'none',
              filter: 'blur(0.5px)',
            }}
          >
            404
          </div>
          {/* Glow behind */}
          <div
            style={{
              position: 'absolute',
              inset: 0,
              background: 'radial-gradient(ellipse, rgba(99,102,241,0.1) 0%, transparent 70%)',
              zIndex: -1,
            }}
          />
        </div>

        {/* Icon */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            width: '64px',
            height: '64px',
            borderRadius: '18px',
            background: 'rgba(99, 102, 241, 0.1)',
            border: '1px solid rgba(99, 102, 241, 0.2)',
          }}
        >
          <Compass size={28} color="#6366f1" />
        </div>

        <div>
          <h1
            style={{
              fontSize: '24px',
              fontWeight: 700,
              color: 'var(--color-text-primary)',
              letterSpacing: '-0.02em',
              marginBottom: '8px',
            }}
          >
            Page not found
          </h1>
          <p
            style={{
              fontSize: '14px',
              color: 'var(--color-text-secondary)',
              lineHeight: 1.6,
            }}
          >
            The page you're looking for doesn't exist or has been moved.
            Head back to the news timeline to stay informed.
          </p>
        </div>

        <Button
          variant="primary"
          size="lg"
          leftIcon={<Home size={16} />}
          onClick={() => navigate('/')}
          style={{ marginTop: '4px' }}
        >
          Back to Timeline
        </Button>
      </div>
    </div>
  );
};
