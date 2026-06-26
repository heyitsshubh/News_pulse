import React from 'react';
import { format } from 'date-fns';
import { Layers, CalendarRange, FileText } from 'lucide-react';
import { useGetClusterByIdQuery } from '../../store/api/newsApi';
import { ArticleCard } from './ArticleCard';
import { Spinner } from '../ui/Spinner';
interface ClusterDetailProps {
  clusterId: string;
}
const DetailSkeleton: React.FC = () => (
  <div style={{ padding: '20px 24px', display: 'flex', flexDirection: 'column', gap: '12px' }}>
    <div className="skeleton" style={{ width: '70%', height: '18px', marginBottom: '4px' }} />
    <div className="skeleton" style={{ width: '45%', height: '14px' }} />
    <div className="skeleton" style={{ width: '30%', height: '14px', marginBottom: '16px' }} />
    {Array.from({ length: 4 }).map((_, i) => (
      <div
        key={i}
        style={{
          padding: '14px',
          borderLeft: '3px solid rgba(99,102,241,0.2)',
          borderRadius: '0 8px 8px 0',
          display: 'flex',
          flexDirection: 'column',
          gap: '8px',
        }}
      >
        <div className="skeleton" style={{ width: '60px', height: '16px', borderRadius: '9999px' }} />
        <div className="skeleton" style={{ width: '90%', height: '13px' }} />
        <div className="skeleton" style={{ width: '75%', height: '13px' }} />
      </div>
    ))}
  </div>
);
export const ClusterDetail: React.FC<ClusterDetailProps> = ({ clusterId }) => {
  const { data, isLoading, isError } = useGetClusterByIdQuery(clusterId);
  if (isLoading) return <DetailSkeleton />;
  if (isError || !data) {
    return (
      <div
        style={{
          padding: '40px 24px',
          textAlign: 'center',
          color: 'var(--color-error)',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          gap: '12px',
        }}
      >
        <span style={{ fontSize: '28px' }}>⚠️</span>
        <p style={{ fontSize: '14px', fontWeight: 600 }}>Failed to load cluster</p>
        <p style={{ fontSize: '12px', color: 'var(--color-text-muted)' }}>
          Try closing and reopening the panel.
        </p>
      </div>
    );
  }
  const startFormatted = data.startTime
    ? format(new Date(data.startTime), 'MMM d, yyyy HH:mm')
    : null;
  const endFormatted = data.endTime
    ? format(new Date(data.endTime), 'HH:mm')
    : null;
  const articles = data.articles ?? [];
  return (
    <div className="animate-fade-in">
      {}
      <div
        style={{
          padding: '20px 24px 16px',
          borderBottom: '1px solid rgba(30, 41, 59, 0.8)',
          background: 'rgba(99, 102, 241, 0.03)',
        }}
      >
        {}
        <div style={{ display: 'flex', gap: '16px', flexWrap: 'wrap' }}>
          {}
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              fontSize: '12px',
              color: 'var(--color-text-secondary)',
              background: 'rgba(30, 41, 59, 0.5)',
              borderRadius: '8px',
              padding: '6px 12px',
              border: '1px solid rgba(30, 41, 59, 0.8)',
            }}
          >
            <FileText size={12} color="#6366f1" />
            <strong style={{ color: 'var(--color-text-primary)', fontWeight: 700 }}>
              {data.articleCount}
            </strong>
            <span>article{data.articleCount !== 1 ? 's' : ''}</span>
          </div>
          {}
          {startFormatted && (
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                fontSize: '12px',
                color: 'var(--color-text-secondary)',
                background: 'rgba(30, 41, 59, 0.5)',
                borderRadius: '8px',
                padding: '6px 12px',
                border: '1px solid rgba(30, 41, 59, 0.8)',
              }}
            >
              <CalendarRange size={12} color="#8b5cf6" />
              <span>
                {startFormatted}
                {endFormatted && ` → ${endFormatted}`}
              </span>
            </div>
          )}
        </div>
        {}
        {articles.length > 0 && (() => {
          const counts: Record<string, number> = {};
          articles.forEach((a) => {
            counts[a.source] = (counts[a.source] ?? 0) + 1;
          });
          const SOURCE_COLORS: Record<string, string> = {
            bbc: '#ef4444',
            npr: '#3b82f6',
            guardian: '#14b8a6',
          };
          return (
            <div style={{ display: 'flex', gap: '8px', marginTop: '10px', flexWrap: 'wrap' }}>
              {Object.entries(counts).map(([src, cnt]) => (
                <span
                  key={src}
                  style={{
                    fontSize: '10px',
                    fontWeight: 600,
                    letterSpacing: '0.04em',
                    textTransform: 'uppercase',
                    color: SOURCE_COLORS[src] ?? '#6366f1',
                    background: `${SOURCE_COLORS[src] ?? '#6366f1'}15`,
                    border: `1px solid ${SOURCE_COLORS[src] ?? '#6366f1'}30`,
                    borderRadius: '9999px',
                    padding: '2px 8px',
                  }}
                >
                  {src} · {cnt}
                </span>
              ))}
            </div>
          );
        })()}
      </div>
      {}
      <div style={{ padding: '12px 16px 24px' }}>
        {articles.length === 0 ? (
          <div
            style={{
              padding: '32px',
              textAlign: 'center',
              color: 'var(--color-text-muted)',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              gap: '8px',
            }}
          >
            <Layers size={28} color="var(--color-text-muted)" style={{ opacity: 0.5 }} />
            <p style={{ fontSize: '13px' }}>No articles in this cluster</p>
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
            {articles.map((article, i) => (
              <ArticleCard key={article.id} article={article} index={i} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
};