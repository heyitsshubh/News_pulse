import { useEffect } from 'react';
import { useAppDispatch, useAppSelector } from '../store/hooks';
import { clearJob, setLastRefreshed } from '../store/slices/ingestSlice';
import { newsApi, useGetIngestStatusQuery } from '../store/api/newsApi';
import { POLL_INTERVAL_MS } from '../lib/constants';

export function useIngestPolling() {
  const dispatch = useAppDispatch();
  const activeJobId = useAppSelector((state) => state.ingest.activeJobId);
  const isPolling = useAppSelector((state) => state.ingest.isPolling);

  const { data: statusData, error } = useGetIngestStatusQuery(activeJobId ?? '', {
    skip: !activeJobId,
    pollingInterval: activeJobId ? POLL_INTERVAL_MS : 0,
  });

  useEffect(() => {
    if (!statusData) return;
    if (statusData.status === 'done' || statusData.status === 'failed') {
      dispatch(clearJob());
      dispatch(setLastRefreshed(new Date().toISOString()));
      // Invalidate timeline + clusters so they refetch
      dispatch(newsApi.util.invalidateTags(['Timeline', 'Clusters']));
    }
  }, [statusData, dispatch]);

  return {
    isPolling,
    status: statusData?.status ?? null,
    error: statusData?.error ?? (error ? 'Failed to fetch status' : null),
  };
}
