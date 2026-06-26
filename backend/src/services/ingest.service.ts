import { spawn } from 'child_process';
import { config } from '../config/env';
import { jobsRepository } from '../repositories/jobs.repository';
import { IngestJob } from '../types/job.types';
import logger from '../utils/logger';
export const ingestService = {
  async triggerIngest(): Promise<IngestJob> {
    const job = await jobsRepository.create();
    const { id: jobId } = job;
    logger.info(`Starting ingest job ${jobId}`);
    logger.info(
      `Spawning: ${config.PYTHON_CMD} ${config.SCRAPER_PATH} --job-id ${jobId}`,
    );
    const child = spawn(config.PYTHON_CMD, [
      config.SCRAPER_PATH,
      '--job-id',
      jobId,
    ]);
    const stderrChunks: Buffer[] = [];
    child.stdout.on('data', (chunk: Buffer) => {
      logger.debug(`[scraper:${jobId}] ${chunk.toString().trim()}`);
    });
    child.stderr.on('data', (chunk: Buffer) => {
      stderrChunks.push(chunk);
      logger.warn(`[scraper:${jobId}] stderr: ${chunk.toString().trim()}`);
    });
    child.on('error', async (err: Error) => {
      logger.error(`[scraper:${jobId}] Failed to spawn process: ${err.message}`);
      await jobsRepository
        .updateStatus(jobId, 'failed', err.message)
        .catch((dbErr: Error) =>
          logger.error(`[scraper:${jobId}] DB update error: ${dbErr.message}`),
        );
    });
    child.on('close', async (code: number | null) => {
      const stderr = Buffer.concat(stderrChunks).toString().trim();
      if (code === 0) {
        logger.info(`[scraper:${jobId}] completed successfully`);
        await jobsRepository.updateStatus(jobId, 'done').catch((err: Error) =>
          logger.error(`[scraper:${jobId}] DB update error: ${err.message}`),
        );
      } else {
        const errorMsg =
          stderr || `Process exited with non-zero code: ${code ?? 'unknown'}`;
        logger.error(`[scraper:${jobId}] failed — ${errorMsg}`);
        await jobsRepository
          .updateStatus(jobId, 'failed', errorMsg)
          .catch((err: Error) =>
            logger.error(`[scraper:${jobId}] DB update error: ${err.message}`),
          );
      }
    });
    return job;
  },
  async getJobStatus(jobId: string): Promise<IngestJob | null> {
    return jobsRepository.findById(jobId);
  },
};