import React, { useCallback, useState } from 'react';
import { AppShell } from '../components/layout/AppShell';
import { TimelineChart } from '../components/timeline/TimelineChart';
import { SourceFilter } from '../components/filters/SourceFilter';
import { SlidePanel } from '../components/ui/SlidePanel';
import { ClusterDetail } from '../components/cluster/ClusterDetail';
import { useGetTimelineQuery } from '../store/api/newsApi';
import { useAppDispatch, useAppSelector } from '../store/hooks';
import { setSelectedCluster, clearSelectedCluster } from '../store/slices/timelineSlice';
import type { TimelineItem } from '../types/timeline';
import { Spinner } from '../components/ui/Spinner';

export const HomePage: React.FC = () => {
  const dispatch = useAppDispatch();
  const selectedClusterId = useAppSelector((s) => s.timeline.selectedClusterId);
  const activeSources = useAppSelector((s) => s.filters.activeSources);

  const { data: timelineItems, isLoading, isError, isFetching } = useGetTimelineQuery(undefined, {
    pollingInterval: 0,
  });

  const [panelTitle, setPanelTitle] = useState('Cluster Details');

  const handleClusterClick = useCallback(
    (id: string, label: string) => {
      dispatch(setSelectedCluster(id));
      setPanelTitle(label);
    },
    [dispatch]
  );

  const handlePanelClose = useCallback(() => {
    dispatch(clearSelectedCluster());
  }, [dispatch]);

  // Client-side filtering by active sources is conceptual at the cluster level.
  // Since clusters don't directly carry source info in the timeline endpoint,
  // we show all clusters but filter is visually active on the source pills.
  // When backend returns source-annotated clusters this can be wired up.
  const filteredItems: TimelineItem[] = Array.isArray(timelineItems) ? timelineItems : [];

  return (
    <AppShell>
      {/* ── Toolbar ─────────────────────────────────────────── */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '18px 28px 14px',
          borderBottom: '1px solid rgba(30, 41, 59, 0.6)',
          flexWrap: 'wrap',
          gap: '12px',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px', flex: 1 }}>
          <SourceFilter />
          {isFetching && !isLoading && (
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                fontSize: '12px',
                color: 'var(--color-text-muted)',
              }}
            >
              <Spinner size="xs" />
              Updating…
            </div>
          )}
        </div>

        {/* Cluster count badge */}
        {filteredItems.length > 0 && (
          <div
            style={{
              fontSize: '12px',
              color: 'var(--color-text-muted)',
              background: 'rgba(30, 41, 59, 0.6)',
              border: '1px solid rgba(30, 41, 59, 0.8)',
              borderRadius: '9999px',
              padding: '4px 12px',
              fontWeight: 500,
              flexShrink: 0,
            }}
          >
            {filteredItems.length} topic cluster{filteredItems.length !== 1 ? 's' : ''}
          </div>
        )}
      </div>

      {/* ── Timeline Area ─────────────────────────────────── */}
      <div
        style={{
          flex: 1,
          padding: '24px 28px 32px',
          overflowX: 'hidden',
          overflowY: 'auto',
        }}
      >
        {/* Section header */}
        {filteredItems.length > 0 && (
          <div
            style={{
              marginBottom: '20px',
              display: 'flex',
              alignItems: 'baseline',
              gap: '10px',
            }}
          >
            <h2
              style={{
                fontSize: '20px',
                fontWeight: 700,
                letterSpacing: '-0.02em',
                background: 'linear-gradient(135deg, #f1f5f9 0%, #94a3b8 100%)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                backgroundClip: 'text',
              }}
            >
              News Timeline
            </h2>
            <span
              style={{
                fontSize: '12px',
                color: 'var(--color-text-muted)',
                fontWeight: 400,
              }}
            >
              Click any cluster to read articles
            </span>
          </div>
        )}

        {/* Chart card */}
        <div
          style={{
            background: 'rgba(15, 23, 42, 0.6)',
            borderRadius: 'var(--radius-lg)',
            border: '1px solid rgba(30, 41, 59, 0.8)',
            overflow: 'hidden',
            backdropFilter: 'blur(8px)',
            boxShadow: '0 4px 24px rgba(0,0,0,0.3)',
          }}
        >
          <TimelineChart
            items={filteredItems}
            selectedClusterId={selectedClusterId}
            onClusterClick={handleClusterClick}
            isLoading={isLoading}
            isError={isError}
          />
        </div>

        {/* Hint when items are showing */}
        {filteredItems.length > 0 && (
          <p
            style={{
              fontSize: '11px',
              color: 'var(--color-text-muted)',
              textAlign: 'center',
              marginTop: '16px',
            }}
          >
            ← Drag to scroll · Hover for details · Click to open articles →
          </p>
        )}
      </div>

      {/* ── Slide-in Detail Panel ─────────────────────────── */}
      <SlidePanel
        isOpen={!!selectedClusterId}
        onClose={handlePanelClose}
        title={panelTitle}
      >
        {selectedClusterId && (
          <ClusterDetail clusterId={selectedClusterId} />
        )}
      </SlidePanel>
    </AppShell>
  );
};
