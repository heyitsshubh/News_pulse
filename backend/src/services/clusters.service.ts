import { clustersRepository } from '../repositories/clusters.repository';
import { ClusterListItem, Cluster } from '../types/cluster.types';
import { Article } from '../types/article.types';
import { ApiError } from '../utils/ApiError';

export const clustersService = {
  /**
   * Return a lightweight list of all clusters (no article details).
   */
  async listClusters(): Promise<ClusterListItem[]> {
    return clustersRepository.findAll();
  },

  /**
   * Return a single cluster with its full article list.
   * Throws 404 when the cluster does not exist.
   */
  async getClusterById(
    id: string,
  ): Promise<{ cluster: Cluster; articles: Article[] }> {
    const result = await clustersRepository.findById(id);
    if (!result) {
      throw new ApiError(404, `Cluster with id '${id}' not found`);
    }
    return result;
  },
};
