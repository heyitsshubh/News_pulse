utf-8
import logging
import sys
from typing import Optional
_LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
_DATE_FORMAT = "%Y-%m-%dT%H:%M:%S"
_configured: set[str] = set()
def get_logger(name: str, level: Optional[str] = None) -> logging.Logger:
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
        logger.propagate = False
        _configured.add(name)
    return logger