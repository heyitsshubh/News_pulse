"""SQLAlchemy 2.0 ORM models for News Pulse.

Each model maps 1-to-1 to a table in the Postgres schema defined in
``migrations/001_initial.sql``.  The ``gen_random_uuid()`` default is
delegated to the database server so that IDs are always generated even when
rows are inserted via raw SQL or other tools.
"""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, Text, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Shared declarative base for all ORM models."""


class Article(Base):
    """Persisted news article.

    Attributes
    ----------
    id:
        Server-generated UUID primary key.
    url:
        Canonical article URL (unique).
    url_hash:
        SHA-256 hex digest of *url* — used for fast dedup lookups.
    headline:
        Article title / headline text.
    summary:
        Short description extracted from the RSS feed or article metadata.
    body:
        Full article body text extracted by trafilatura / newspaper3k.
    source:
        Short source identifier, e.g. ``"bbc"``.
    published_at:
        Publication timestamp as reported by the feed.
    fetched_at:
        Wall-clock time when the row was first inserted.
    """

    __tablename__ = "articles"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    url: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    url_hash: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    headline: Mapped[str] = mapped_column(Text, nullable=False)
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    body: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    source: Mapped[str] = mapped_column(Text, nullable=False)
    published_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    fetched_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        server_default=text("NOW()"),
        nullable=True,
    )

    # Relationship back to cluster memberships.
    cluster_articles: Mapped[list["ClusterArticle"]] = relationship(
        "ClusterArticle", back_populates="article", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Article id={self.id} source={self.source!r} headline={self.headline[:40]!r}>"


class Cluster(Base):
    """A group of thematically similar articles produced by TF-IDF clustering.

    Attributes
    ----------
    id:
        Server-generated UUID primary key.
    label:
        Human-readable label derived from top TF-IDF terms.
    article_count:
        Denormalised count of member articles for quick reads.
    created_at:
        Row creation timestamp.
    updated_at:
        Row last-updated timestamp.
    """

    __tablename__ = "clusters"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    label: Mapped[str] = mapped_column(Text, nullable=False)
    article_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), server_default=text("NOW()"), nullable=True
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), server_default=text("NOW()"), nullable=True
    )

    # Relationship to member articles via junction table.
    cluster_articles: Mapped[list["ClusterArticle"]] = relationship(
        "ClusterArticle", back_populates="cluster", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Cluster id={self.id} label={self.label!r} count={self.article_count}>"


class ClusterArticle(Base):
    """Junction / association table linking clusters to their member articles.

    Attributes
    ----------
    cluster_id:
        FK → clusters.id
    article_id:
        FK → articles.id
    """

    __tablename__ = "cluster_articles"

    cluster_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("clusters.id", ondelete="CASCADE"),
        primary_key=True,
    )
    article_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("articles.id", ondelete="CASCADE"),
        primary_key=True,
    )

    cluster: Mapped["Cluster"] = relationship("Cluster", back_populates="cluster_articles")
    article: Mapped["Article"] = relationship("Article", back_populates="cluster_articles")

    def __repr__(self) -> str:
        return f"<ClusterArticle cluster={self.cluster_id} article={self.article_id}>"


class IngestJob(Base):
    """Audit record for a single pipeline run.

    Attributes
    ----------
    id:
        Server-generated UUID primary key.
    status:
        One of ``pending``, ``running``, ``done``, ``failed``.
    started_at:
        When the job transitioned to *running*.
    finished_at:
        When the job transitioned to *done* or *failed*.
    error:
        Error message / traceback when *status* is ``failed``.
    created_at:
        Row creation timestamp.
    """

    __tablename__ = "ingest_jobs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    status: Mapped[str] = mapped_column(Text, nullable=False, default="pending")
    started_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    finished_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), server_default=text("NOW()"), nullable=True
    )

    def __repr__(self) -> str:
        return f"<IngestJob id={self.id} status={self.status!r}>"
