FROM python:3.11-slim

WORKDIR /app

# Install Node.js 20 and system dependencies for Python packages
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    libpq-dev \
    libxml2-dev \
    libxslt1-dev \
    libjpeg-dev \
    zlib1g-dev \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies for the scraper
COPY scraper/requirements.txt ./scraper/
RUN pip install --no-cache-dir -r scraper/requirements.txt

# Install Node.js dependencies for the backend
COPY backend/package*.json ./backend/
RUN cd backend && npm ci

# Copy source code
COPY scraper/ ./scraper/
COPY backend/ ./backend/

# Build backend
RUN cd backend && npm run build

# Environment variables required for Python scraper resolution
ENV PYTHON_CMD=python
ENV SCRAPER_PATH=/app/scraper/src/main.py
ENV PYTHONPATH=/app/scraper

EXPOSE 3001

# Start script: Run DB migrations then start the Node.js backend
WORKDIR /app
CMD sh -c "cd /app/scraper && python -m src.db.migrate && cd /app/backend && node dist/index.js"
