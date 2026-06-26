import { Router } from 'express';
import { ingestController } from '../controllers/ingest.controller';
import { asyncHandler } from '../utils/asyncHandler';
const router = Router();
router.post('/trigger', asyncHandler(ingestController.trigger));
router.get('/status/:jobId', asyncHandler(ingestController.getStatus));
export default router;