utf-8
import hashlib
import uuid
from datetime import datetime, timezone
from typing import Any, Optional
from sqlalchemy import delete, select
from sqlalchemy.orm import Session
from src.db.models import Article, Cluster, ClusterArticle, IngestJob
from src.utils.logger import get_logger
log = get_logger(__name__)
def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()
def get_or_create_article(
    session: Session,
    article_data: dict[str, Any],
) -> tuple[Article, bool]:
    url: str = article_data["url"]
    url_hash: str = _sha256(url)
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
    stmt = select(Article).where(Article.id == article_id)
    article = session.execute(stmt).scalar_one_or_none()
    if article is not None:
        article.body = body
        log.debug("Updated body for article %s", article_id)
def get_all_articles(session: Session) -> list[Article]:
    stmt = select(Article).order_by(Article.published_at.desc().nullslast())
    return list(session.execute(stmt).scalars().all())
def save_clusters(
    session: Session,
    clusters_data: list[dict[str, Any]],
) -> list[Cluster]:
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
        session.flush()  
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
def update_job_status(
    session: Session,
    job_id: uuid.UUID,
    status: str,
    error: Optional[str] = None,
) -> None:
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