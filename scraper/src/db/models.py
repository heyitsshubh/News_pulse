utf-8
import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import DateTime, ForeignKey, Integer, Text, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
class Base(DeclarativeBase):
class Article(Base):
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
    cluster_articles: Mapped[list["ClusterArticle"]] = relationship(
        , back_populates="article", cascade="all, delete-orphan"
    )
    def __repr__(self) -> str:
        return f"<Article id={self.id} source={self.source!r} headline={self.headline[:40]!r}>"
class Cluster(Base):
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
    cluster_articles: Mapped[list["ClusterArticle"]] = relationship(
        , back_populates="cluster", cascade="all, delete-orphan"
    )
    def __repr__(self) -> str:
        return f"<Cluster id={self.id} label={self.label!r} count={self.article_count}>"
class ClusterArticle(Base):
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