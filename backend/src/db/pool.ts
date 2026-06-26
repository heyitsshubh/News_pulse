import { Pool, QueryResult, QueryResultRow } from 'pg';
import { config } from '../config/env';
import logger from '../utils/logger';

let pool: Pool | null = null;

function getPool(): Pool {
  if (!pool) {
    pool = new Pool({
      connectionString: config.DATABASE_URL,
      max: 10,
      idleTimeoutMillis: 30_000,
      connectionTimeoutMillis: 5_000,
      ssl:
        config.NODE_ENV === 'production'
          ? { rejectUnauthorized: false }
          : undefined,
    });

    pool.on('error', (err: Error) => {
      logger.error('Unexpected pg pool error:', err);
    });

    pool.on('connect', () => {
      logger.debug('New pg client connected');
    });
  }
  return pool;
}

/**
 * Execute a parameterised query against the shared pool.
 * Automatically acquires and releases a client.
 */
export async function query<T extends QueryResultRow = QueryResultRow>(
  text: string,
  params?: unknown[],
): Promise<QueryResult<T>> {
  const start = Date.now();
  const result = await getPool().query<T>(text, params);
  const duration = Date.now() - start;
  logger.debug(`query executed in ${duration}ms — rows: ${result.rowCount}`);
  return result;
}

export default getPool;
