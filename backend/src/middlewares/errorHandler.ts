import { Request, Response, NextFunction } from 'express';
import { ApiError } from '../utils/ApiError';
import logger from '../utils/logger';

// eslint-disable-next-line @typescript-eslint/no-unused-vars
export function errorHandler(
  err: Error,
  req: Request,
  res: Response,
  // `next` must be declared even if unused — Express identifies error handlers by arity = 4
  _next: NextFunction,
): void {
  if (err instanceof ApiError) {
    if (!err.isOperational) {
      logger.error(`[Operational=false] ${err.message}`, err);
    } else {
      logger.warn(`ApiError ${err.statusCode}: ${err.message}`);
    }

    res.status(err.statusCode).json({
      error: {
        message: err.message,
        statusCode: err.statusCode,
      },
    });
    return;
  }

  // Unexpected programmer errors — always log the full stack
  logger.error('Unhandled error:', err);

  const statusCode = 500;
  const errorPayload: Record<string, unknown> = {
    message: 'Internal Server Error',
    statusCode,
  };

  // Expose stack trace only in non-production environments
  if (process.env['NODE_ENV'] !== 'production') {
    errorPayload['stack'] = err.stack;
  }

  res.status(statusCode).json({ error: errorPayload });
}

