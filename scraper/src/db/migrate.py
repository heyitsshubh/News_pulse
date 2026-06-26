utf-8
import pathlib
import sys
from sqlalchemy import text
from src.db.session import _engine
from src.utils.logger import get_logger
log = get_logger(__name__)
_MIGRATIONS_DIR = pathlib.Path(__file__).resolve().parents[2] / "migrations"
def run_migration(sql_file: pathlib.Path) -> None:
    if not sql_file.exists():
        log.error("Migration file not found: %s", sql_file)
        sys.exit(1)
    raw_sql = sql_file.read_text(encoding="utf-8")
    statements = [s.strip() for s in raw_sql.split(";") if s.strip()]
    log.info("Running migration: %s (%d statements)", sql_file.name, len(statements))
    with _engine.begin() as conn:
        for stmt in statements:
            log.debug("Executing: %s …", stmt[:60])
            conn.execute(text(stmt))
    log.info("Migration complete: %s", sql_file.name)
def main() -> None:
    sql_file = _MIGRATIONS_DIR / "001_initial.sql"
    run_migration(sql_file)
if __name__ == "__main__":
    main()