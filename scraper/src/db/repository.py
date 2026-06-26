"""Database repository — all persistence operations in one place.

This module contains functions that translate between plain Python dicts
(used by the feed parser and clustering layers) and SQLAlchemy ORM objects.
All functions accept an open :class:`sqlalchemy.orm.Session` so that callers
control transaction boundaries.
"""

import hashlib
import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from src.db.models import Article, Cluster, ClusterArticle, IngestJob
from src.utils.logger import get_logger

log = get_logger(__name__)


# ---------------------------------------------------------------------------
# Articles
# ---------------------------------------------------------------------------

def _sha256(text: str) -> str:
    """Return the hex-encoded SHA-256 digest of *text*."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def get_or_create_article(
    session: Session,
    article_data: dict[str, Any],
) -> tuple[Article, bool]:
    """Fetch an existing article or insert a new one, keyed on *url_hash*.

    The *url_hash* field is always computed here (even if one was already
    present in *article_data*) so that callers do not need to worry about
    it.

    Parameters
    ----------
    session:
        An open SQLAlchemy session.  The caller is responsible for committing.
    article_data:
        Dict with at minimum: ``url``, ``headline``, ``source``.
        Optional keys: ``summary``, ``body``, ``published_at``.

    Returns
    -------
    tuple[Article, bool]
        ``(article, created)`` where *created* is ``True`` when a new row was
        inserted.
    """
    url: str = article_data["url"]
    url_hash: str = _sha256(url)

    # Fast lookup by hash.
    stmt = select(Article).where(Article.url_hash == url_hash)
    existing = session.execute(stmt).scalar_one_or_none()
    if existing is not None:
        return existing, False

    article = Article(
        url=url,
        url_hash=url_hash,
        headline=article_data["headline"],
        summary=article_data.get("summary"),
        body=article_data.get("body"),
        source=article_data["source"],
        published_at=article_data.get("published_at"),
    )
    session.add(article)
    log.debug("Inserting new article: %s", url[:80])
    return article, True


def update_article_body(session: Session, article_id: uuid.UUID, body: str) -> None:
    """Persist the extracted full-text body for an existing article.

    Parameters
    ----------
    session:
        An open SQLAlchemy session.
    article_id:
        UUID of the article to update.
    body:
        Full extracted article text.
    """
    stmt = select(Article).where(Article.id == article_id)
    article = session.execute(stmt).scalar_one_or_none()
    if article is not None:
        article.body = body
        log.debug("Updated body for article %s", article_id)


def get_all_articles(session: Session) -> list[Article]:
    """Return every article in the database, ordered by *published_at* desc.

    Parameters
    ----------
    session:
        An open SQLAlchemy session.

    Returns
    -------
    list[Article]
        All persisted articles.
    """
    stmt = select(Article).order_by(Article.published_at.desc().nullslast())
    return list(session.execute(stmt).scalars().all())


# ---------------------------------------------------------------------------
# Clusters
# ---------------------------------------------------------------------------

def save_clusters(
    session: Session,
    clusters_data: list[dict[str, Any]],
) -> list[Cluster]:
    """Replace all existing clusters with a fresh set.

    This performs a full replacement (delete-all → insert-all) so that stale
    clusters from previous runs are never surfaced.  ``ON DELETE CASCADE`` on
    ``cluster_articles`` handles junction-table cleanup automatically.

    Parameters
    ----------
    session:
        An open SQLAlchemy session.
    clusters_data:
        List of dicts, each with:
        - ``label`` (str): human-readable cluster label.
        - ``articles`` (list[dict]): list of article dicts, each containing at
          minimum an ``id`` key (UUID).

    Returns
    -------
    list[Cluster]
        The newly persisted :class:`Cluster` objects.
    """
    # Delete all existing clusters (cascade removes cluster_articles rows).
    session.execute(delete(ClusterArticle))
    session.execute(delete(Cluster))
    log.debug("Cleared existing clusters.")

    created_clusters: list[Cluster] = []
    for cluster_dict in clusters_data:
        article_ids: list[uuid.UUID] = [
            a["id"] for a in cluster_dict.get("articles", [])
        ]
        cluster = Cluster(
            label=cluster_dict["label"],
            article_count=len(article_ids),
            updated_at=datetime.now(timezone.utc),
        )
        session.add(cluster)
        session.flush()  # Populate server-generated id before inserting children.

        for art_id in article_ids:
            link = ClusterArticle(
                cluster_id=cluster.id,
                article_id=art_id,
            )
            session.add(link)

        created_clusters.append(cluster)
        log.debug("Saved cluster %r with %d articles.", cluster.label, cluster.article_count)

    log.info("Saved %d clusters to the database.", len(created_clusters))
    return created_clusters


# ---------------------------------------------------------------------------
# Ingest jobs
# ---------------------------------------------------------------------------

def update_job_status(
    session: Session,
    job_id: uuid.UUID,
    status: str,
    error: Optional[str] = None,
) -> None:
    """Update the *status* (and optionally *error*) on an :class:`IngestJob`.

    Also sets *started_at* when status becomes ``running`` and *finished_at*
    when status becomes ``done`` or ``failed``.

    Parameters
    ----------
    session:
        An open SQLAlchemy session.
    job_id:
        UUID of the job to update.
    status:
        New status string: ``"running"``, ``"done"``, or ``"failed"``.
    error:
        Optional error message / traceback to persist when status is
        ``"failed"``.
    """
    stmt = select(IngestJob).where(IngestJob.id == job_id)
    job = session.execute(stmt).scalar_one_or_none()
    if job is None:
        log.warning("IngestJob %s not found — cannot update status.", job_id)
        return

    now = datetime.now(timezone.utc)
    job.status = status

    if status == "running":
        job.started_at = now
    elif status in ("done", "failed"):
        job.finished_at = now

    if error is not None:
        job.error = error

    log.info("IngestJob %s → %s", job_id, status)
