import { config } from './config/env';
import app from './app';
import logger from './utils/logger';
const PORT = config.PORT;
const server = app.listen(PORT, () => {
  logger.info(`🚀 News Pulse API running on http://localhost:${PORT}`);
  logger.info(`   NODE_ENV  : ${config.NODE_ENV}`);
  logger.info(`   FRONTEND  : ${config.FRONTEND_URL}`);
  logger.info(`   DB        : ${config.DATABASE_URL.replace(/:\/\/.*@/, '://<credentials>@')}`);
});
function shutdown(signal: string): void {
  logger.info(`Received ${signal}. Shutting down gracefully…`);
  server.close(() => {
    logger.info('HTTP server closed.');
    process.exit(0);
  });
  setTimeout(() => {
    logger.error('Forcing shutdown after timeout.');
    process.exit(1);
  }, 10_000).unref();
}
process.on('SIGTERM', () => shutdown('SIGTERM'));
process.on('SIGINT', () => shutdown('SIGINT'));
process.on('uncaughtException', (err: Error) => {
  logger.error('Uncaught exception — shutting down:', err);
  process.exit(1);
});
process.on('unhandledRejection', (reason: unknown) => {
  logger.error('Unhandled promise rejection:', reason);
  process.exit(1);
});
export default server;