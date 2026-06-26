import { Request, Response, NextFunction } from 'express';
import { ApiError } from '../utils/ApiError';

/**
 * Catch-all for routes that don't match any registered handler.
 * Passes a 404 ApiError to the next error handler.
 */
export function notFound(
  req: Request,
  _res: Response,
  next: NextFunction,
): void {
  next(new ApiError(404, `Route not found: ${req.method} ${req.originalUrl}`));
}
