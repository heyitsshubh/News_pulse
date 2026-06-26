import morgan, { StreamOptions } from 'morgan';
import logger from '../utils/logger';

// Pipe Morgan's output into winston so all logs go through one transport
const stream: StreamOptions = {
  write: (message: string) => {
    // Trim the trailing newline Morgan adds
    logger.http(message.trim());
  },
};

// Skip logging in test environments
const skip = (): boolean => process.env['NODE_ENV'] === 'test';

/**
 * Morgan request logger using 'combined' format, piped into the winston logger.
 * Skipped entirely when NODE_ENV=test to keep test output clean.
 */
export const requestLogger = morgan('combined', { stream, skip });
