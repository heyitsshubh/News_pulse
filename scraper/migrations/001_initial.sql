-- migrations/001_initial.sql
-- Initial schema for News Pulse.
-- Requires the pgcrypto extension for gen_random_uuid().

CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE TABLE IF NOT EXISTS articles (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  url          TEXT UNIQUE NOT NULL,
  url_hash     TEXT UNIQUE NOT NULL,
  headline     TEXT NOT NULL,
  summary      TEXT,
  body         TEXT,
  source       TEXT NOT NULL,
  published_at TIMESTAMPTZ,
  fetched_at   TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS clusters (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  label         TEXT NOT NULL,
  article_count INT DEFAULT 0,
  created_at    TIMESTAMPTZ DEFAULT NOW(),
  updated_at    TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS cluster_articles (
  cluster_id  UUID REFERENCES clusters(id) ON DELETE CASCADE,
  article_id  UUID REFERENCES articles(id) ON DELETE CASCADE,
  PRIMARY KEY (cluster_id, article_id)
);

CREATE TABLE IF NOT EXISTS ingest_jobs (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  status       TEXT NOT NULL DEFAULT 'pending',
  started_at   TIMESTAMPTZ,
  finished_at  TIMESTAMPTZ,
  error        TEXT,
  created_at   TIMESTAMPTZ DEFAULT NOW()
);
