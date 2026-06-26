import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';
import { API_BASE } from '../../lib/constants';
import type { Cluster } from '../../types/cluster';
import type { Article } from '../../types/article';
import type { TimelineItem } from '../../types/timeline';
import type { IngestJob } from '../../types/job';

export interface ClusterDetail extends Cluster {
  articles: Article[];
}

export interface TriggerIngestResponse {
  jobId: string;
  message: string;
}

export const newsApi = createApi({
  reducerPath: 'newsApi',
  baseQuery: fetchBaseQuery({ baseUrl: `${API_BASE}/api` }),
  tagTypes: ['Clusters', 'Timeline', 'IngestJob'],
  endpoints: (builder) => ({
    getClusters: builder.query<Cluster[], void>({
      query: () => '/clusters',
      providesTags: ['Clusters'],
    }),
    getClusterById: builder.query<ClusterDetail, string>({
      query: (id) => `/clusters/${id}`,
      providesTags: (_result, _err, id) => [{ type: 'Clusters', id }],
    }),
    getTimeline: builder.query<TimelineItem[], void>({
      query: () => '/timeline',
      providesTags: ['Timeline'],
    }),
    triggerIngest: builder.mutation<TriggerIngestResponse, void>({
      query: () => ({
        url: '/ingest/trigger',
        method: 'POST',
      }),
    }),
    getIngestStatus: builder.query<IngestJob, string>({
      query: (jobId) => `/ingest/status/${jobId}`,
      providesTags: (_result, _err, jobId) => [{ type: 'IngestJob', id: jobId }],
    }),
  }),
});

export const {
  useGetClustersQuery,
  useGetClusterByIdQuery,
  useGetTimelineQuery,
  useTriggerIngestMutation,
  useGetIngestStatusQuery,
} = newsApi;
