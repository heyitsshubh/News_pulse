utf-8
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
def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="News Pulse RSS scraper and clustering pipeline."
    )
    parser.add_argument(
        ,
        type=str,
        default=None,
        help="UUID of an existing ingest_jobs row to update with run status.",
    )
    return parser.parse_args()
def _article_to_dict(article: Any) -> dict[str, Any]:
    return {
        : article.id,
        : article.url,
        : article.headline or "",
        : article.summary or "",
        : article.body or "",
        : article.source,
        : article.published_at,
    }
def run_pipeline(job_id: Optional[uuid.UUID] = None) -> None:
    start_time = datetime.now(timezone.utc)
    if job_id is not None:
        with get_db() as session:
            update_job_status(session, job_id, "running")
    try:
        log.info("=== Step 1: Fetching RSS feeds ===")
        feed_entries: list[dict[str, Any]] = parse_all_feeds()
        log.info("Total feed entries fetched: %d", len(feed_entries))
        log.info("=== Step 2: Persisting articles ===")
        new_articles: list[dict[str, Any]] = []
        with get_db() as session:
            for entry in feed_entries:
                article, created = get_or_create_article(session, entry)
                if created:
                    session.flush()
                    new_articles.append(
                        {
                            : article.id,
                            : article.url,
                            : article.headline,
                        }
                    )
        log.info(
            , len(feed_entries), len(new_articles)
        )
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
            ,
            extraction_success,
            extraction_failure,
        )
        log.info("=== Step 4: Loading all articles for clustering ===")
        with get_db() as session:
            all_orm_articles = get_all_articles(session)
            all_articles_dicts = [_article_to_dict(a) for a in all_orm_articles]
        log.info("Articles available for clustering: %d", len(all_articles_dicts))
        log.info("=== Step 5: Running TF-IDF clustering ===")
        clusters = cluster_articles(
            all_articles_dicts,
            threshold=settings.COSINE_THRESHOLD,
            min_cluster_size=settings.MIN_CLUSTER_SIZE,
        )
        log.info("Clusters produced: %d", len(clusters))
        log.info("=== Step 6: Saving clusters to database ===")
        with get_db() as session:
            saved = save_clusters(session, clusters)
        multi_clusters = [c for c in clusters if c["article_count"] >= settings.MIN_CLUSTER_SIZE]
        elapsed = (datetime.now(timezone.utc) - start_time).total_seconds()
        log.info(
            ,
            elapsed,
            len(feed_entries),
            len(new_articles),
            len(saved),
            len(multi_clusters),
        )
        if job_id is not None:
            with get_db() as session:
                update_job_status(session, job_id, "done")
    except Exception as exc:  
        tb = traceback.format_exc()
        log.error("Pipeline failed: %s\n%s", exc, tb)
        if job_id is not None:
            with get_db() as session:
                update_job_status(session, job_id, "failed", error=tb)
        sys.exit(1)
def main() -> None:
    args = _parse_args()
    job_id: Optional[uuid.UUID] = None
    if args.job_id:
        try:
            job_id = uuid.UUID(args.job_id)
        except ValueError:
            log.error("Invalid --job-id value: %r (must be a valid UUID)", args.job_id)
            sys.exit(1)
    init_db()
    run_pipeline(job_id=job_id)
if __name__ == "__main__":
    main()