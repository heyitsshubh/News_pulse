"""Database engine, session factory, and helper utilities.

This module is the single point of truth for how SQLAlchemy connects to
Postgres.  Import :func:`get_db` for a context-managed session in application
code and :func:`init_db` during startup to ensure all tables exist.
"""

from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from src.utils.config import settings
from src.utils.logger import get_logger

log = get_logger(__name__)

# ---------------------------------------------------------------------------
# Engine — created once at import time.
# ---------------------------------------------------------------------------

_engine: Engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,          # Re-establish stale connections automatically.
    pool_size=5,
    max_overflow=10,
    echo=False,
)

# ---------------------------------------------------------------------------
# Session factory
# ---------------------------------------------------------------------------

SessionLocal: sessionmaker[Session] = sessionmaker(
    bind=_engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,      # Avoid lazy-load errors after commit.
)


# ---------------------------------------------------------------------------
# Context manager — preferred way to get a session in application code.
# ---------------------------------------------------------------------------

@contextmanager
def get_db() -> Generator[Session, None, None]:
    """Yield a database session that is automatically committed or rolled back.

    Usage
    -----
    ::

        with get_db() as session:
            articles = session.query(Article).all()

    The session is rolled back on any unhandled exception, then closed.
    """
    session: Session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


# ---------------------------------------------------------------------------
# Table bootstrap
# ---------------------------------------------------------------------------

def init_db() -> None:
    """Create all ORM-mapped tables that do not yet exist in the database.

    This is *not* a replacement for the SQL migration file; it is a
    convenience function that ensures the schema exists when running the
    service locally or in CI without a full migration runner.

    Note: ``gen_random_uuid()`` requires the ``pgcrypto`` extension which must
    be created separately (see ``migrations/001_initial.sql``).
    """
    from src.db.models import Base  # local import to avoid circular dependency

    log.info("Initialising database schema …")
    # Attempt to create pgcrypto extension; ignore error if already present or
    # if the user lacks superuser privileges (handled by the migration instead).
    try:
        with _engine.connect() as conn:
            conn.execute(text('CREATE EXTENSION IF NOT EXISTS "pgcrypto"'))
            conn.commit()
    except Exception as exc:
        log.warning("Could not create pgcrypto extension: %s", exc)

    Base.metadata.create_all(bind=_engine)
    log.info("Database schema ready.")
