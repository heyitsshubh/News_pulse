import { Request, Response } from 'express';
import { clustersService } from '../services/clusters.service';
export const clustersController = {
  async list(req: Request, res: Response): Promise<void> {
    const clusters = await clustersService.listClusters();
    res.json({ clusters });
  },
  async getById(req: Request, res: Response): Promise<void> {
    const { id } = req.params;
    const { cluster, articles } = await clustersService.getClusterById(id);
    res.json({ cluster, articles });
  },
};