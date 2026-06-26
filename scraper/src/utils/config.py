"""Application configuration via pydantic-settings.

Reads settings from environment variables and/or a .env file located in the
working directory.  All fields have sensible defaults so the service can start
without a full .env file (DATABASE_URL is the only mandatory setting).
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Centralised application settings.

    Attributes
    ----------
    DATABASE_URL:
        PostgreSQL connection string understood by SQLAlchemy, e.g.
        ``postgresql://user:password@localhost:5432/news_pulse``.
    COSINE_THRESHOLD:
        Minimum cosine-similarity score for two articles to be placed in the
        same cluster.  Range ``[0, 1]``.  Lower values create bigger, looser
        clusters.
    MIN_CLUSTER_SIZE:
        Clusters with fewer than this many articles are discarded as noise.
    LOG_LEVEL:
        Standard Python logging level name: ``DEBUG``, ``INFO``, ``WARNING``,
        ``ERROR``, or ``CRITICAL``.
    """

    DATABASE_URL: str
    COSINE_THRESHOLD: float = 0.25
    MIN_CLUSTER_SIZE: int = 2
    LOG_LEVEL: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


# Singleton — import this everywhere instead of constructing a new object.
settings = Settings()  # type: ignore[call-arg]
