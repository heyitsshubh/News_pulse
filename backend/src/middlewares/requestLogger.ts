import morgan, { StreamOptions } from 'morgan';
import logger from '../utils/logger';
const stream: StreamOptions = {
  write: (message: string) => {
    logger.http(message.trim());
  },
};
const skip = (): boolean => process.env['NODE_ENV'] === 'test';
export const requestLogger = morgan('combined', { stream, skip });