import React, { useEffect, useState } from 'react';
import { RefreshCw, CheckCircle, AlertCircle } from 'lucide-react';
import { Button } from '../ui/Button';
import { useAppDispatch } from '../../store/hooks';
import { setActiveJob } from '../../store/slices/ingestSlice';
import { useTriggerIngestMutation } from '../../store/api/newsApi';
import { useIngestPolling } from '../../hooks/useIngestPolling';

export const RefreshButton: React.FC = () => {
  const dispatch = useAppDispatch();
  const [triggerIngest, { isLoading: isTriggerLoading }] = useTriggerIngestMutation();
  const { isPolling, status, error } = useIngestPolling();
  const [showSuccess, setShowSuccess] = useState(false);
  const [showError, setShowError] = useState(false);

  const isRunning = isTriggerLoading || isPolling;

  // Watch for done/failed transitions
  useEffect(() => {
    if (status === 'done' && !isPolling) {
      setShowSuccess(true);
      const t = setTimeout(() => setShowSuccess(false), 3000);
      return () => clearTimeout(t);
    }
    if (status === 'failed' && !isPolling) {
      setShowError(true);
      const t = setTimeout(() => setShowError(false), 4000);
      return () => clearTimeout(t);
    }
  }, [status, isPolling]);

  const handleClick = async () => {
    try {
      setShowSuccess(false);
      setShowError(false);
      const result = await triggerIngest().unwrap();
      dispatch(setActiveJob(result.jobId));
    } catch {
      setShowError(true);
      const t = setTimeout(() => setShowError(false), 4000);
      return () => clearTimeout(t);
    }
  };

  if (showSuccess) {
    return (
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '6px',
          fontSize: '13px',
          fontWeight: 600,
          color: 'var(--color-success)',
          padding: '8px 14px',
          borderRadius: '8px',
          background: 'rgba(16, 185, 129, 0.1)',
          border: '1px solid rgba(16, 185, 129, 0.25)',
          animation: 'fadeIn 300ms ease forwards',
        }}
      >
        <CheckCircle size={15} />
        Updated!
      </div>
    );
  }

  if (showError) {
    return (
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '6px',
          fontSize: '13px',
          fontWeight: 600,
          color: 'var(--color-error)',
          padding: '8px 14px',
          borderRadius: '8px',
          background: 'rgba(239, 68, 68, 0.1)',
          border: '1px solid rgba(239, 68, 68, 0.25)',
          animation: 'fadeIn 300ms ease forwards',
        }}
      >
        <AlertCircle size={15} />
        {error ?? 'Ingest failed'}
      </div>
    );
  }

  return (
    <Button
      variant="primary"
      size="sm"
      loading={isRunning}
      onClick={handleClick}
      disabled={isRunning}
      leftIcon={
        !isRunning ? (
          <RefreshCw
            size={14}
            style={{
              transition: 'transform 300ms ease',
            }}
          />
        ) : undefined
      }
      style={{
        minWidth: '110px',
      }}
    >
      {isRunning ? 'Refreshing…' : 'Refresh News'}
    </Button>
  );
};
