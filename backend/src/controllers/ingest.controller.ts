import { Request, Response } from 'express';
import { ingestService } from '../services/ingest.service';
import { ApiError } from '../utils/ApiError';

export const ingestController = {
  /**
   * POST /api/ingest/trigger
   * Spawns the Python scraper subprocess and returns the new job record.
   */
  async trigger(req: Request, res: Response): Promise<void> {
    const job = await ingestService.triggerIngest();
    res.status(202).json({ jobId: job.id, status: 'pending' });
  },

  /**
   * GET /api/ingest/status/:jobId
   * Returns the current status of a previously triggered job.
   */
  async getStatus(req: Request, res: Response): Promise<void> {
    const { jobId } = req.params;
    const job = await ingestService.getJobStatus(jobId);

    if (!job) {
      throw new ApiError(404, `Ingest job '${jobId}' not found`);
    }

    res.json({
      jobId: job.id,
      status: job.status,
      startedAt: job.startedAt,
      finishedAt: job.finishedAt,
      error: job.error,
    });
  },
};
