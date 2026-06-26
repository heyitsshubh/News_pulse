import express, { Application } from 'express';
import helmet from 'helmet';
import cors from 'cors';
import { config } from './config/env';
import apiRouter from './routes/index';
import { requestLogger } from './middlewares/requestLogger';
import { notFound } from './middlewares/notFound';
import { errorHandler } from './middlewares/errorHandler';

const app: Application = express();

// ── Security & parsing ───────────────────────────────────────────────────────
app.use(helmet());
app.use(
  cors({
    origin: config.FRONTEND_URL,
    methods: ['GET', 'POST', 'OPTIONS'],
    allowedHeaders: ['Content-Type', 'Authorization'],
    credentials: true,
  }),
);
app.use(express.json({ limit: '1mb' }));
app.use(express.urlencoded({ extended: true }));

// ── Request logging ──────────────────────────────────────────────────────────
app.use(requestLogger);

// ── API routes ───────────────────────────────────────────────────────────────
app.use('/api', apiRouter);

// ── Error handling (must be LAST) ────────────────────────────────────────────
app.use(notFound);
app.use(errorHandler);

export default app;
