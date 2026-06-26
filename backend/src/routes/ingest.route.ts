import { Router } from 'express';
import { ingestController } from '../controllers/ingest.controller';
import { asyncHandler } from '../utils/asyncHandler';

const router = Router();

// POST /api/ingest/trigger
router.post('/trigger', asyncHandler(ingestController.trigger));

// GET /api/ingest/status/:jobId
router.get('/status/:jobId', asyncHandler(ingestController.getStatus));

export default router;
