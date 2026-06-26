utf-8
from contextlib import contextmanager
from typing import Generator
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker
from src.utils.config import settings
from src.utils.logger import get_logger
log = get_logger(__name__)
_engine: Engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,          
    pool_size=5,
    max_overflow=10,
    echo=False,
)
SessionLocal: sessionmaker[Session] = sessionmaker(
    bind=_engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,      
)
@contextmanager
def get_db() -> Generator[Session, None, None]:
    session: Session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
def init_db() -> None:
    from src.db.models import Base  
    log.info("Initialising database schema …")
    try:
        with _engine.connect() as conn:
            conn.execute(text('CREATE EXTENSION IF NOT EXISTS "pgcrypto"'))
            conn.commit()
    except Exception as exc:
        log.warning("Could not create pgcrypto extension: %s", exc)
    Base.metadata.create_all(bind=_engine)
    log.info("Database schema ready.")