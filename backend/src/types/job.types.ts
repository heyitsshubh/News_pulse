export type JobStatus = 'pending' | 'running' | 'done' | 'failed';

export interface IngestJob {
  id: string;
  status: JobStatus;
  startedAt: string | null;
  finishedAt: string | null;
  error: string | null;
  createdAt: string;
}
