import { clustersRepository } from '../repositories/clusters.repository';
import { ClusterListItem, Cluster } from '../types/cluster.types';
import { Article } from '../types/article.types';
import { ApiError } from '../utils/ApiError';
export const clustersService = {
  async listClusters(): Promise<ClusterListItem[]> {
    return clustersRepository.findAll();
  },
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