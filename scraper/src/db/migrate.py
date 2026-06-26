"""Standalone migration runner.

Usage
-----
Run from the ``scraper/`` directory::

    python -m src.db.migrate

This script reads ``migrations/001_initial.sql`` relative to the repository
root and executes each statement against the configured database.
"""

import pathlib
import sys

from sqlalchemy import text

from src.db.session import _engine
from src.utils.logger import get_logger

log = get_logger(__name__)

_MIGRATIONS_DIR = pathlib.Path(__file__).resolve().parents[2] / "migrations"


def run_migration(sql_file: pathlib.Path) -> None:
    """Execute all SQL statements in *sql_file* against the current database.

    Parameters
    ----------
    sql_file:
        Absolute path to the .sql file to execute.
    """
    if not sql_file.exists():
        log.error("Migration file not found: %s", sql_file)
        sys.exit(1)

    raw_sql = sql_file.read_text(encoding="utf-8")

    # Split on semicolons, strip whitespace, and drop empty fragments.
    statements = [s.strip() for s in raw_sql.split(";") if s.strip()]

    log.info("Running migration: %s (%d statements)", sql_file.name, len(statements))

    with _engine.begin() as conn:
        for stmt in statements:
            log.debug("Executing: %s …", stmt[:60])
            conn.execute(text(stmt))

    log.info("Migration complete: %s", sql_file.name)


def main() -> None:
    """Entry point — run the initial migration."""
    sql_file = _MIGRATIONS_DIR / "001_initial.sql"
    run_migration(sql_file)


if __name__ == "__main__":
    main()
