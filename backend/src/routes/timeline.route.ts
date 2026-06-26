import { Router } from 'express';
import { timelineController } from '../controllers/timeline.controller';
import { asyncHandler } from '../utils/asyncHandler';

const router = Router();

// GET /api/timeline
router.get('/', asyncHandler(timelineController.getTimeline));

export default router;
