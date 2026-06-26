import React from 'react';
import { ExternalLink, Clock } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';
import type { Article } from '../../types/article';
import { Badge } from '../ui/Badge';
interface ArticleCardProps {
  article: Article;
  index?: number;
}
const SOURCE_COLORS: Record<string, string> = {
  bbc: '#ef4444',
  npr: '#3b82f6',
  guardian: '#14b8a6',
};
export const ArticleCard: React.FC<ArticleCardProps> = ({ article, index = 0 }) => {
  const accentColor = SOURCE_COLORS[article.source] ?? '#6366f1';
  const timeAgo =
    article.publishedAt
      ? formatDistanceToNow(new Date(article.publishedAt), { addSuffix: true })
      : 'Unknown time';
  return (
    <a
      href={article.url}
      target="_blank"
      rel="noopener noreferrer"
      className="animate-fade-in"
      style={{
        display: 'block',
        textDecoration: 'none',
        padding: '16px 20px',
        borderLeft: `3px solid ${accentColor}`,
        background: 'rgba(30, 41, 59, 0.35)',
        borderRadius: '0 8px 8px 0',
        marginBottom: '2px',
        transition: 'all 200ms ease',
        animationDelay: `${index * 50}ms`,
        animationFillMode: 'both',
        cursor: 'pointer',
        position: 'relative',
        overflow: 'hidden',
      }}
      onMouseEnter={(e) => {
        const el = e.currentTarget;
        el.style.background = 'rgba(30, 41, 59, 0.65)';
        el.style.borderLeftColor = accentColor;
        el.style.transform = 'translateX(3px)';
        el.style.boxShadow = `inset 0 0 0 1px ${accentColor}18`;
      }}
      onMouseLeave={(e) => {
        const el = e.currentTarget;
        el.style.background = 'rgba(30, 41, 59, 0.35)';
        el.style.transform = 'translateX(0)';
        el.style.boxShadow = 'none';
      }}
    >
      {}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          marginBottom: '8px',
          gap: '8px',
        }}
      >
        <Badge source={article.source as 'bbc' | 'npr' | 'guardian'} />
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '4px',
            fontSize: '10px',
            color: 'var(--color-text-muted)',
            fontWeight: 500,
            flexShrink: 0,
          }}
        >
          <Clock size={10} />
          {timeAgo}
        </div>
      </div>
      {}
      <div
        style={{
          display: 'flex',
          alignItems: 'flex-start',
          justifyContent: 'space-between',
          gap: '8px',
          marginBottom: article.summary ? '8px' : '0',
        }}
      >
        <p
          style={{
            fontSize: '13px',
            fontWeight: 600,
            color: 'var(--color-text-primary)',
            lineHeight: 1.45,
            flex: 1,
          }}
        >
          {article.headline}
        </p>
        <ExternalLink
          size={12}
          style={{
            color: accentColor,
            opacity: 0.7,
            flexShrink: 0,
            marginTop: '2px',
          }}
        />
      </div>
      {}
      {article.summary && (
        <p
          className="line-clamp-2"
          style={{
            fontSize: '12px',
            color: 'var(--color-text-secondary)',
            lineHeight: 1.55,
          }}
        >
          {article.summary}
        </p>
      )}
    </a>
  );
};