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
      transformResponse: (response: any) => {
        if (Array.isArray(response)) return response;
        if (response && Array.isArray(response.clusters)) return response.clusters;
        return [];
      },
      providesTags: ['Clusters'],
    }),
    getClusterById: builder.query<ClusterDetail, string>({
      query: (id) => `/clusters/${id}`,
      transformResponse: (response: any) => {
        if (response && response.cluster && response.articles) {
          return { ...response.cluster, articles: response.articles };
        }
        return response;
      },
      providesTags: (_result, _err, id) => [{ type: 'Clusters', id }],
    }),
    getTimeline: builder.query<TimelineItem[], void>({
      query: () => '/timeline',
      transformResponse: (response: any) => {
        if (Array.isArray(response)) return response;
        if (response && Array.isArray(response.items)) return response.items;
        return [];
      },
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