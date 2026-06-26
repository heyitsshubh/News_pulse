import { Router } from 'express';
import { clustersController } from '../controllers/clusters.controller';
import { asyncHandler } from '../utils/asyncHandler';

const router = Router();

// GET /api/clusters
router.get('/', asyncHandler(clustersController.list));

// GET /api/clusters/:id
router.get('/:id', asyncHandler(clustersController.getById));

export default router;
