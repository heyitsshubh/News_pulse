# 📡 News Pulse — Topic-Clustered News Timeline

> A full-stack system that pulls live news from RSS feeds, automatically clusters related articles by topic using TF-IDF, and visualises those clusters as a Gantt-style interactive timeline.

---

## 🏗️ Architecture Overview

```
news-pulse/
├── scraper/      # Python — RSS ingestion, article extraction, TF-IDF clustering
├── backend/      # Node.js + TypeScript — REST API (Express)
└── frontend/     # Vite + React 18 + TypeScript + Redux Toolkit
```

| Component | Technology | Hosting |
|-----------|-----------|---------|
| Frontend | Vite + React 18 + TypeScript + Redux Toolkit + Recharts | Vercel |
| Backend API | Express + TypeScript + pg + Zod | Render |
| Python Pipeline | Python 3.11, feedparser, trafilatura, scikit-learn, SQLAlchemy | Triggered via Node API on Render |
| Database | PostgreSQL (Neon) | Neon (free tier) |

---

## 📰 News Sources

| Source | RSS Feed |
|--------|----------|
| BBC News | `http://feeds.bbci.co.uk/news/rss.xml` |
| NPR | `https://feeds.npr.org/1001/rss.xml` |
| The Guardian | `https://www.theguardian.com/world/rss` |

---

## 🧠 Topic Grouping Approach

**Method: TF-IDF + Cosine Similarity** (Option B from assessment)

1. For each article, concatenate `headline + summary` into a text document
2. Compute TF-IDF vectors using scikit-learn (`TfidfVectorizer`, stop_words='english', max_features=5000)
3. Calculate pairwise cosine similarity across all article vectors
4. Use **Union-Find (disjoint set)** to greedily merge articles whose cosine similarity ≥ threshold into the same cluster
5. Auto-label each cluster using the **top 3 TF-IDF terms** from the cluster's centroid vector

**Threshold**: `COSINE_THRESHOLD=0.25` (configurable via env var). Empirically tuned — too low creates noise clusters, too high fragments real topic stories.

**Limitation**: TF-IDF is bag-of-words — it misses semantic similarity. "Ukraine war" and "Russia conflict" may land in different clusters despite covering the same story. A sentence-transformer embedding model would solve this but adds significant latency and cost.

---

## 🗄️ Database Schema

```sql
-- Articles (deduped by SHA-256 of URL)
articles (id UUID, url TEXT UNIQUE, url_hash TEXT UNIQUE, headline TEXT,
          summary TEXT, body TEXT, source TEXT, published_at TIMESTAMPTZ, fetched_at TIMESTAMPTZ)

-- Topic clusters
clusters (id UUID, label TEXT, article_count INT, created_at TIMESTAMPTZ, updated_at TIMESTAMPTZ)

-- Many-to-many join
cluster_articles (cluster_id UUID, article_id UUID)

-- Async ingest jobs
ingest_jobs (id UUID, status TEXT, started_at TIMESTAMPTZ, finished_at TIMESTAMPTZ, error TEXT, created_at TIMESTAMPTZ)
```

---

## 🚀 Local Setup

### Prerequisites
- Node.js 20+
- Python 3.11+
- A PostgreSQL database (Neon free tier recommended)

### 1. Clone & configure environment

```bash
git clone <your-repo-url>
cd news-pulse

# Backend
cp backend/.env.example backend/.env
# Fill in: DATABASE_URL, FRONTEND_URL, SCRAPER_PATH

# Frontend
cp frontend/.env.example frontend/.env.local
# Fill in: VITE_API_URL=http://localhost:3001

# Scraper
cp scraper/.env.example scraper/.env
# Fill in: DATABASE_URL (same Neon URL)
```

### 2. Run DB migrations

```bash
cd scraper
pip install -r requirements.txt
python -m src.db.migrate
```

### 3. Run the scraper (first data load)

```bash
cd scraper
python -m src.main
```

### 4. Start the backend

```bash
cd backend
npm install
npm run dev      # starts on http://localhost:3001
```

### 5. Start the frontend

```bash
cd frontend
npm install
npm run dev      # starts on http://localhost:5173
```

---

## 🌐 API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/clusters` | List all topic clusters |
| `GET` | `/api/clusters/:id` | Cluster detail with all articles |
| `GET` | `/api/timeline` | Timeline-formatted data for Gantt chart |
| `POST` | `/api/ingest/trigger` | Trigger scraper pipeline (returns jobId) |
| `GET` | `/api/ingest/status/:jobId` | Poll job status |
| `GET` | `/api/health` | Health check |

---

## ☁️ Deployment

### Backend → Render

1. Push repo to GitHub
2. Create a new **Web Service** on [render.com](https://render.com)
3. Set **Root Directory**: `backend`
4. **Build Command**: `npm install && npm run build`
5. **Start Command**: `npm start`
6. Add env vars: `DATABASE_URL`, `FRONTEND_URL`, `NODE_ENV=production`, `PYTHON_CMD=python3`, `SCRAPER_PATH=../scraper/src/main.py`

### Frontend → Vercel

1. Import repo on [vercel.com](https://vercel.com)
2. Set **Root Directory**: `frontend`
3. **Framework Preset**: Vite
4. Add env var: `VITE_API_URL=https://your-render-backend-url.onrender.com`
5. The `vercel.json` handles SPA routing rewrites automatically

### Database → Neon

1. Create a free project at [neon.tech](https://neon.tech)
2. Copy the connection string as `DATABASE_URL`
3. Run migrations: `python -m src.db.migrate`

---

## 📁 Project Structure

```
news-pulse/
├── scraper/
│   ├── src/
│   │   ├── feeds/          # RSS parsing + source config
│   │   ├── extraction/     # Full article body extraction (trafilatura)
│   │   ├── clustering/     # TF-IDF vectorization + labeling
│   │   ├── db/             # SQLAlchemy models, session, repository, migrations
│   │   └── utils/          # Config (pydantic-settings), logger
│   ├── migrations/         # SQL migration files
│   ├── tests/
│   └── requirements.txt
│
├── backend/
│   └── src/
│       ├── config/         # Zod env validation
│       ├── controllers/    # HTTP request/response handlers
│       ├── services/       # Business logic layer
│       ├── repositories/   # Raw SQL queries (pg)
│       ├── routes/         # Express router definitions
│       ├── middlewares/    # Error handler, 404, request logger
│       ├── types/          # TypeScript interfaces
│       ├── db/             # pg Pool singleton
│       └── utils/          # ApiError, asyncHandler, winston logger
│
└── frontend/
    └── src/
        ├── components/
        │   ├── ui/         # Button, Badge, Spinner, Tooltip, SlidePanel
        │   ├── layout/     # Navbar, AppShell
        │   ├── timeline/   # TimelineChart (Gantt), ClusterBar, TimelineEmpty
        │   ├── cluster/    # ClusterDetail, ArticleCard
        │   ├── filters/    # SourceFilter
        │   └── ingest/     # RefreshButton
        ├── store/
        │   ├── slices/     # timelineSlice, ingestSlice, filtersSlice
        │   └── api/        # RTK Query (newsApi)
        ├── pages/          # HomePage, NotFoundPage
        ├── hooks/          # useIngestPolling
        ├── types/          # TypeScript interfaces
        └── lib/            # constants
```

---

## 📝 Assumptions Made

- **Cluster freshness**: Old clusters are deleted and rebuilt on every scraper run. This ensures the timeline always reflects the most recent groupings without stale data.
- **Source filtering**: Implemented client-side in Redux — the API returns all clusters, and the frontend filters by active sources.
- **Job persistence**: Ingest job status is stored in Postgres (not in-memory), so it survives backend restarts on Render.
- **Cold starts**: Render free tier has ~30s cold starts — this is acceptable per the assessment.

---

## 🎥 Video Walkthrough

> Link: _[Add your Loom/OBS recording link here]_
