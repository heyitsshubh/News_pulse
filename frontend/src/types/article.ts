export type Source = 'bbc' | 'npr' | 'guardian';
export interface Article {
  id: string;
  url: string;
  headline: string;
  summary: string | null;
  source: Source;
  publishedAt: string | null;
}