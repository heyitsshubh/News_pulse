import { query } from '../db/pool';
import { Article } from '../types/article.types';

interface ArticleRow {
  id: string;
  url: string;
  headline: string;
  summary: string | null;
  source: string;
  published_at: string | null;
  fetched_at: string;
}

function rowToArticle(row: ArticleRow): Article {
  return {
    id: row.id,
    url: row.url,
    headline: row.headline,
    summary: row.summary,
    source: row.source,
    publishedAt: row.published_at,
    fetchedAt: row.fetched_at,
  };
}

export const articlesRepository = {
  /**
   * Fetch all articles that belong to a given cluster, ordered
   * chronologically (oldest first).
   */
  async findByClusterId(clusterId: string): Promise<Article[]> {
    const sql = `
      SELECT
        a.id,
        a.url,
        a.headline,
        a.summary,
        a.source,
        a.published_at,
        a.fetched_at
      FROM articles a
      INNER JOIN cluster_articles ca ON ca.article_id = a.id
      WHERE ca.cluster_id = $1
      ORDER BY a.published_at ASC NULLS LAST
    `;
    const result = await query<ArticleRow>(sql, [clusterId]);
    return result.rows.map(rowToArticle);
  },
};
