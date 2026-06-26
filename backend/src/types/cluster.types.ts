export interface Cluster {
  id: string;
  label: string;
  articleCount: number;
  startTime: string | null;
  endTime: string | null;
  createdAt: string;
  updatedAt: string;
}

export interface ClusterListItem {
  id: string;
  label: string;
  articleCount: number;
  startTime: string | null;
  endTime: string | null;
}
