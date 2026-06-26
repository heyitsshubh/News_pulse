import express, { Application } from 'express';
import helmet from 'helmet';
import cors from 'cors';
import { config } from './config/env';
import apiRouter from './routes/index';
import { requestLogger } from './middlewares/requestLogger';
import { notFound } from './middlewares/notFound';
import { errorHandler } from './middlewares/errorHandler';
const app: Application = express();
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
app.use(requestLogger);
app.use('/api', apiRouter);
app.use(notFound);
app.use(errorHandler);
export default app;