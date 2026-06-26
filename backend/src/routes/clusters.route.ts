import { Router } from 'express';
import { clustersController } from '../controllers/clusters.controller';
import { asyncHandler } from '../utils/asyncHandler';
const router = Router();
router.get('/', asyncHandler(clustersController.list));
router.get('/:id', asyncHandler(clustersController.getById));
export default router;