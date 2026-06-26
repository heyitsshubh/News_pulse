"""News Pulse scraper — main pipeline orchestrator.

Pipeline steps
--------------
1. Parse all RSS feeds from all registered sources.
2. Persist new articles to the database (dedup by url_hash / SHA-256).
3. Extract full article body text for newly inserted articles.
4. Load ALL articles from the database for clustering.
5. Run TF-IDF cosine-similarity clustering.
6. Save clusters back to the database (old clusters are replaced).
7. Optionally update an :class:`~src.db.models.IngestJob` row.

Usage
-----
Run as a module::

    python -m src.main

With job tracking::

    python -m src.main --job-id <uuid>
"""

import argparse
import sys
import traceback
import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from src.clustering.tfidf import cluster_articles
from src.db.repository import (
    get_all_articles,
    get_or_create_article,
    save_clusters,
    update_article_body,
    update_job_status,
)
from src.db.session import get_db, init_db
from src.extraction.article import extract_article_body
from src.feeds.parser import parse_all_feeds
from src.utils.config import settings
from src.utils.logger import get_logger

log = get_logger(__name__)


# ---------------------------------------------------------------------------
# CLI argument parsing
# ---------------------------------------------------------------------------

def _parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="News Pulse RSS scraper and clustering pipeline."
    )
    parser.add_argument(
        "--job-id",
        type=str,
        default=None,
        help="UUID of an existing ingest_jobs row to update with run status.",
    )
    return parser.parse_args()


# ---------------------------------------------------------------------------
# Pipeline helpers
# ---------------------------------------------------------------------------

def _article_to_dict(article: Any) -> dict[str, Any]:
    """Convert an ORM :class:`~src.db.models.Article` to a plain dict.

    The dict format matches what :func:`~src.clustering.tfidf.cluster_articles`
    and :func:`~src.db.repository.save_clusters` expect.
    """
    return {
        "id": article.id,
        "url": article.url,
        "headline": article.headline or "",
        "summary": article.summary or "",
        "body": article.body or "",
        "source": article.source,
        "published_at": article.published_at,
    }


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------

def run_pipeline(job_id: Optional[uuid.UUID] = None) -> None:
    """Execute the full scrape → cluster pipeline.

    Parameters
    ----------
    job_id:
        Optional UUID of an :class:`~src.db.models.IngestJob` to track.
        When provided the job's status is updated to ``running``, then
        ``done`` (or ``failed`` on error).
    """
    start_time = datetime.now(timezone.utc)

    # --- Mark job as running ---
    if job_id is not None:
        with get_db() as session:
            update_job_status(session, job_id, "running")

    try:
        # ------------------------------------------------------------------
        # Step 1 — Fetch and parse RSS feeds
        # ------------------------------------------------------------------
        log.info("=== Step 1: Fetching RSS feeds ===")
        feed_entries: list[dict[str, Any]] = parse_all_feeds()
        log.info("Total feed entries fetched: %d", len(feed_entries))

        # ------------------------------------------------------------------
        # Step 2 — Persist new articles (dedup by url_hash)
        # ------------------------------------------------------------------
        log.info("=== Step 2: Persisting articles ===")
        new_articles: list[dict[str, Any]] = []

        with get_db() as session:
            for entry in feed_entries:
                article, created = get_or_create_article(session, entry)
                if created:
                    # Flush to get the server-assigned id.
                    session.flush()
                    new_articles.append(
                        {
                            "id": article.id,
                            "url": article.url,
                            "headline": article.headline,
                        }
                    )

        log.info(
            "Articles: %d fetched, %d new.", len(feed_entries), len(new_articles)
        )

        # ------------------------------------------------------------------
        # Step 3 — Extract full body text for new articles
        # ------------------------------------------------------------------
        log.info("=== Step 3: Extracting article bodies (%d new) ===", len(new_articles))
        extraction_success = 0
        extraction_failure = 0

        for art_stub in new_articles:
            body = extract_article_body(art_stub["url"])
            if body:
                with get_db() as session:
                    update_article_body(session, art_stub["id"], body)
                extraction_success += 1
            else:
                extraction_failure += 1

        log.info(
            "Body extraction: %d succeeded, %d failed / skipped.",
            extraction_success,
            extraction_failure,
        )

        # ------------------------------------------------------------------
        # Step 4 — Load ALL articles for clustering
        # ------------------------------------------------------------------
        log.info("=== Step 4: Loading all articles for clustering ===")
        with get_db() as session:
            all_orm_articles = get_all_articles(session)
            all_articles_dicts = [_article_to_dict(a) for a in all_orm_articles]

        log.info("Articles available for clustering: %d", len(all_articles_dicts))

        # ------------------------------------------------------------------
        # Step 5 — TF-IDF clustering
        # ------------------------------------------------------------------
        log.info("=== Step 5: Running TF-IDF clustering ===")
        clusters = cluster_articles(
            all_articles_dicts,
            threshold=settings.COSINE_THRESHOLD,
            min_cluster_size=settings.MIN_CLUSTER_SIZE,
        )
        log.info("Clusters produced: %d", len(clusters))

        # ------------------------------------------------------------------
        # Step 6 — Persist clusters (replace old)
        # ------------------------------------------------------------------
        log.info("=== Step 6: Saving clusters to database ===")
        with get_db() as session:
            saved = save_clusters(session, clusters)

        multi_clusters = [c for c in clusters if c["article_count"] >= settings.MIN_CLUSTER_SIZE]

        # ------------------------------------------------------------------
        # Step 7 — Summary log
        # ------------------------------------------------------------------
        elapsed = (datetime.now(timezone.utc) - start_time).total_seconds()
        log.info(
            "=== Pipeline complete in %.1fs | "
            "%d articles fetched | %d new | "
            "%d clusters created (%d multi-article) ===",
            elapsed,
            len(feed_entries),
            len(new_articles),
            len(saved),
            len(multi_clusters),
        )

        # --- Mark job as done ---
        if job_id is not None:
            with get_db() as session:
                update_job_status(session, job_id, "done")

    except Exception as exc:  # noqa: BLE001
        tb = traceback.format_exc()
        log.error("Pipeline failed: %s\n%s", exc, tb)

        if job_id is not None:
            with get_db() as session:
                update_job_status(session, job_id, "failed", error=tb)

        sys.exit(1)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    """CLI entry point."""
    args = _parse_args()

    job_id: Optional[uuid.UUID] = None
    if args.job_id:
        try:
            job_id = uuid.UUID(args.job_id)
        except ValueError:
            log.error("Invalid --job-id value: %r (must be a valid UUID)", args.job_id)
            sys.exit(1)

    # Ensure schema exists (idempotent).
    init_db()

    run_pipeline(job_id=job_id)


if __name__ == "__main__":
    main()
