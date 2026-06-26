import React from 'react';
import { useAppDispatch, useAppSelector } from '../../store/hooks';
import { toggleSource, setAllSources, clearSources } from '../../store/slices/filtersSlice';
import { SOURCES } from '../../lib/constants';

export const SourceFilter: React.FC = () => {
  const dispatch = useAppDispatch();
  const activeSources = useAppSelector((state) => state.filters.activeSources);

  const allActive = activeSources.length === SOURCES.length;
  const noneActive = activeSources.length === 0;

  return (
    <div
      style={{
        display: 'flex',
        alignItems: 'center',
        gap: '8px',
        flexWrap: 'wrap',
      }}
    >
      <span
        style={{
          fontSize: '11px',
          fontWeight: 600,
          color: 'var(--color-text-muted)',
          textTransform: 'uppercase',
          letterSpacing: '0.08em',
          marginRight: '4px',
        }}
      >
        Sources
      </span>

      {SOURCES.map((source) => {
        const isActive = activeSources.includes(source.key);
        return (
          <button
            key={source.key}
            onClick={() => dispatch(toggleSource(source.key))}
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '6px',
              padding: '6px 14px',
              borderRadius: '9999px',
              fontSize: '12px',
              fontWeight: 600,
              letterSpacing: '0.02em',
              cursor: 'pointer',
              transition: 'all 200ms ease',
              border: `1.5px solid ${isActive ? source.color : 'rgba(148, 163, 184, 0.2)'}`,
              background: isActive ? `${source.color}18` : 'transparent',
              color: isActive ? source.color : 'var(--color-text-muted)',
              boxShadow: isActive ? `0 0 12px ${source.color}20` : 'none',
              fontFamily: 'var(--font-sans)',
            }}
            onMouseEnter={(e) => {
              if (!isActive) {
                e.currentTarget.style.borderColor = `${source.color}60`;
                e.currentTarget.style.color = source.color;
                e.currentTarget.style.background = `${source.color}0a`;
              } else {
                e.currentTarget.style.filter = 'brightness(1.2)';
              }
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.filter = '';
              if (!isActive) {
                e.currentTarget.style.borderColor = 'rgba(148, 163, 184, 0.2)';
                e.currentTarget.style.color = 'var(--color-text-muted)';
                e.currentTarget.style.background = 'transparent';
              }
            }}
          >
            {/* Colored dot */}
            <span
              style={{
                width: '6px',
                height: '6px',
                borderRadius: '50%',
                background: isActive ? source.color : 'var(--color-text-muted)',
                flexShrink: 0,
                transition: 'background 200ms ease',
                boxShadow: isActive ? `0 0 6px ${source.color}` : 'none',
              }}
            />
            {source.label}
          </button>
        );
      })}

      {/* Divider */}
      <div
        style={{
          width: '1px',
          height: '20px',
          background: 'rgba(148, 163, 184, 0.15)',
          margin: '0 4px',
        }}
      />

      {/* All / None quick toggles */}
      <button
        onClick={() => (allActive ? dispatch(clearSources()) : dispatch(setAllSources()))}
        style={{
          fontSize: '11px',
          fontWeight: 600,
          color: allActive ? 'var(--color-accent-primary)' : 'var(--color-text-muted)',
          background: 'transparent',
          border: 'none',
          cursor: 'pointer',
          padding: '4px 8px',
          borderRadius: '6px',
          transition: 'all 150ms ease',
          fontFamily: 'var(--font-sans)',
          letterSpacing: '0.04em',
          textTransform: 'uppercase',
        }}
        onMouseEnter={(e) => { e.currentTarget.style.background = 'rgba(99, 102, 241, 0.1)'; }}
        onMouseLeave={(e) => { e.currentTarget.style.background = 'transparent'; }}
      >
        {allActive ? 'All ✓' : 'All'}
      </button>
    </div>
  );
};
