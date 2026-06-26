import { Request, Response } from 'express';
import { timelineService } from '../services/timeline.service';

export const timelineController = {
  /**
   * GET /api/timeline
   * Returns timeline items enriched with intensity scores.
   */
  async getTimeline(req: Request, res: Response): Promise<void> {
    const items = await timelineService.getTimeline();
    res.json({ items });
  },
};
