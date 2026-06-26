import 'dotenv/config';
import { z } from 'zod';

const envSchema = z.object({
  PORT: z
    .string()
    .optional()
    .default('3001')
    .transform((v) => parseInt(v, 10))
    .pipe(z.number().int().positive()),
  DATABASE_URL: z.string().url({ message: 'DATABASE_URL must be a valid URL' }),
  FRONTEND_URL: z.string().url().optional().default('https://news-pulse-taupe.vercel.app').transform((v) => v.replace(/\/$/, '')),
  PYTHON_CMD: z.string().optional().default('python3'),
  SCRAPER_PATH: z.string().min(1, { message: 'SCRAPER_PATH is required' }),
  NODE_ENV: z
    .enum(['development', 'production', 'test'])
    .optional()
    .default('development'),
});

const parsed = envSchema.safeParse(process.env);

if (!parsed.success) {
  console.error('❌ Invalid environment variables:');
  console.error(parsed.error.flatten().fieldErrors);
  process.exit(1);
}

export const config = parsed.data;
export type Config = typeof config;
