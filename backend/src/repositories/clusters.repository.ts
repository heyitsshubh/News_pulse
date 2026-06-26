import { query } from '../db/pool';
import { ClusterListItem, Cluster } from '../types/cluster.types';
import { Article } from '../types/article.types';

// ── DB row shapes ────────────────────────────────────────────────────────────

interface ClusterRow {
  id: string;
  label: string;
  article_count: number;
  start_time: string | null;
  end_time: string | null;
  created_at: string;
  updated_at: string;
}

interface ArticleRow {
  id: string;
  url: string;
  headline: string;
  summary: string | null;
  source: string;
  published_at: string | null;
  fetched_at: string;
}

// ── Helpers ──────────────────────────────────────────────────────────────────

function rowToClusterListItem(row: ClusterRow): ClusterListItem {
  return {
    id: row.id,
    label: row.label,
    articleCount: row.article_count,
    startTime: row.start_time,
    endTime: row.end_time,
  };
}

function rowToCluster(row: ClusterRow): Cluster {
  return {
    id: row.id,
    label: row.label,
    articleCount: row.article_count,
    startTime: row.start_time,
    endTime: row.end_time,
    createdAt: row.created_at,
    updatedAt: row.updated_at,
  };
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

// ── Repository ───────────────────────────────────────────────────────────────

export const clustersRepository = {
  /**
   * Return all clusters with the min/max published_at derived from their
   * linked articles (used for the cluster list).
   */
  async findAll(): Promise<ClusterListItem[]> {
    const sql = `
      SELECT
        c.id,
        c.label,
        c.article_count,
        c.created_at,
        c.updated_at,
        MIN(a.published_at) AS start_time,
        MAX(a.published_at) AS end_time
      FROM clusters c
      LEFT JOIN cluster_articles ca ON ca.cluster_id = c.id
      LEFT JOIN articles a ON a.id = ca.article_id
      GROUP BY c.id, c.label, c.article_count, c.created_at, c.updated_at
      ORDER BY c.created_at DESC
    `;
    const result = await query<ClusterRow>(sql);
    return result.rows.map(rowToClusterListItem);
  },

  /**
   * Return a single cluster with full details plus all of its articles,
   * sorted by published_at ASC.
   */
  async findById(
    id: string,
  ): Promise<{ cluster: Cluster; articles: Article[] } | null> {
    const clusterSql = `
      SELECT
        c.id,
        c.label,
        c.article_count,
        c.created_at,
        c.updated_at,
        MIN(a.published_at) AS start_time,
        MAX(a.published_at) AS end_time
      FROM clusters c
      LEFT JOIN cluster_articles ca ON ca.cluster_id = c.id
      LEFT JOIN articles a ON a.id = ca.article_id
      WHERE c.id = $1
      GROUP BY c.id, c.label, c.article_count, c.created_at, c.updated_at
    `;
    const clusterResult = await query<ClusterRow>(clusterSql, [id]);

    if (clusterResult.rows.length === 0) {
      return null;
    }

    const articlesSql = `
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
    const articlesResult = await query<ArticleRow>(articlesSql, [id]);

    return {
      cluster: rowToCluster(clusterResult.rows[0]),
      articles: articlesResult.rows.map(rowToArticle),
    };
  },

  /**
   * Return all clusters with their time ranges — used by the timeline service.
   * Clusters with no linked articles (and therefore no timestamps) are still
   * returned; the service will filter them out.
   */
  async findAllWithTimeRange(): Promise<ClusterListItem[]> {
    // Re-uses the same query as findAll — the shape is identical.
    return this.findAll();
  },
};
