export interface Article {
  id: string;
  url: string;
  headline: string;
  summary: string | null;
  source: string;
  publishedAt: string | null;
  fetchedAt: string;
}
