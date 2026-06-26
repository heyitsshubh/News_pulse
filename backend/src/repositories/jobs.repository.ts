import { v4 as uuidv4 } from 'uuid';
import { query } from '../db/pool';
import { IngestJob, JobStatus } from '../types/job.types';
interface JobRow {
  id: string;
  status: string;
  started_at: string | null;
  finished_at: string | null;
  error: string | null;
  created_at: string;
}
function rowToJob(row: JobRow): IngestJob {
  return {
    id: row.id,
    status: row.status as JobStatus,
    startedAt: row.started_at,
    finishedAt: row.finished_at,
    error: row.error,
    createdAt: row.created_at,
  };
}
export const jobsRepository = {
  async create(): Promise<IngestJob> {
    const id = uuidv4();
    const sql = `
      INSERT INTO ingest_jobs (id, status, started_at, created_at)
      VALUES ($1, 'running', NOW(), NOW())
      RETURNING id, status, started_at, finished_at, error, created_at
    `;
    const result = await query<JobRow>(sql, [id]);
    return rowToJob(result.rows[0]);
  },
  async findById(id: string): Promise<IngestJob | null> {
    const sql = `
      SELECT id, status, started_at, finished_at, error, created_at
      FROM ingest_jobs
      WHERE id = $1
    `;
    const result = await query<JobRow>(sql, [id]);
    if (result.rows.length === 0) return null;
    return rowToJob(result.rows[0]);
  },
  async updateStatus(
    id: string,
    status: 'done' | 'failed',
    error?: string,
  ): Promise<IngestJob | null> {
    const sql = `
      UPDATE ingest_jobs
      SET
        status      = $2,
        finished_at = NOW(),
        error       = $3
      WHERE id = $1
      RETURNING id, status, started_at, finished_at, error, created_at
    `;
    const result = await query<JobRow>(sql, [id, status, error ?? null]);
    if (result.rows.length === 0) return null;
    return rowToJob(result.rows[0]);
  },
};