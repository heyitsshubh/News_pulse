import { Request, Response } from 'express';
import { clustersService } from '../services/clusters.service';

export const clustersController = {
  /**
   * GET /api/clusters
   * Returns a flat list of all clusters.
   */
  async list(req: Request, res: Response): Promise<void> {
    const clusters = await clustersService.listClusters();
    res.json({ clusters });
  },

  /**
   * GET /api/clusters/:id
   * Returns a single cluster with its associated articles.
   */
  async getById(req: Request, res: Response): Promise<void> {
    const { id } = req.params;
    const { cluster, articles } = await clustersService.getClusterById(id);
    res.json({ cluster, articles });
  },
};
