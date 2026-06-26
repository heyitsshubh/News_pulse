import { Router, Request, Response } from 'express';
import clustersRouter from './clusters.route';
import timelineRouter from './timeline.route';
import ingestRouter from './ingest.route';
const router = Router();
router.use('/clusters', clustersRouter);
router.use('/timeline', timelineRouter);
router.use('/ingest', ingestRouter);
router.get('/health', (_req: Request, res: Response) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});
export default router;