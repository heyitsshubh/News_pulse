import { Request, Response } from 'express';
import { timelineService } from '../services/timeline.service';
export const timelineController = {
  async getTimeline(req: Request, res: Response): Promise<void> {
    const items = await timelineService.getTimeline();
    res.json({ items });
  },
};