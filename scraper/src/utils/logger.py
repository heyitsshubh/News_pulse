"""Structured application logger.

Usage
-----
    from src.utils.logger import get_logger

    log = get_logger(__name__)
    log.info("Feed fetched", extra={"source": "bbc", "count": 42})
"""

import logging
import sys
from typing import Optional

_LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
_DATE_FORMAT = "%Y-%m-%dT%H:%M:%S"

# Keep track of loggers we've already configured so we don't add duplicate
# handlers if get_logger() is called multiple times for the same name.
_configured: set[str] = set()


def get_logger(name: str, level: Optional[str] = None) -> logging.Logger:
    """Return a named logger configured with the application log level.

    Parameters
    ----------
    name:
        Logger name — pass ``__name__`` from the calling module.
    level:
        Override log level for this specific logger.  When *None* the level
        is read from :attr:`src.utils.config.settings.LOG_LEVEL`.

    Returns
    -------
    logging.Logger
        A ready-to-use logger instance.
    """
    # Lazy import to avoid circular imports at module load time.
    try:
        from src.utils.config import settings
        resolved_level = level or settings.LOG_LEVEL
    except Exception:
        resolved_level = level or "INFO"

    numeric_level = getattr(logging, resolved_level.upper(), logging.INFO)

    logger = logging.getLogger(name)

    if name not in _configured:
        logger.setLevel(numeric_level)

        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(numeric_level)
        formatter = logging.Formatter(fmt=_LOG_FORMAT, datefmt=_DATE_FORMAT)
        handler.setFormatter(formatter)

        logger.addHandler(handler)
        # Prevent log records from propagating to the root logger so we don't
        # get duplicate lines when a root handler is also configured.
        logger.propagate = False

        _configured.add(name)

    return logger
