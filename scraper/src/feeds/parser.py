"""RSS / Atom feed parser.

Fetches and normalises feed entries from each registered source into a
consistent dict structure ready for persistence.

Normalisation covers:
- Multiple possible summary/description field names.
- Missing publication dates (fallback to current UTC time).
- Various date string formats via ``dateutil.parser.parse``.
- SHA-256 URL hashing for deduplication.
- Entries with no URL or headline are silently dropped.
"""

import hashlib
from datetime import datetime, timezone
from typing import Any, Optional

import feedparser
from dateutil import parser as dateutil_parser

from src.feeds.sources import FeedSource, SOURCES
from src.utils.logger import get_logger

log = get_logger(__name__)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _sha256(text: str) -> str:
    """Return the hex-encoded SHA-256 digest of *text*."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _parse_date(raw: Any) -> Optional[datetime]:
    """Attempt to parse *raw* into a timezone-aware :class:`datetime`.

    Accepts:
    - A ``time.struct_time`` as returned by feedparser (``entry.published_parsed``).
    - A date string in any format understood by ``dateutil``.
    - ``None`` → returns ``None``.

    Returns ``None`` on any parse failure so callers can fall back to ``NOW()``.
    """
    if raw is None:
        return None

    # feedparser sets published_parsed to a time.struct_time (9-tuple).
    import time as _time
    if isinstance(raw, _time.struct_time):
        try:
            ts = _time.mktime(raw)
            return datetime.fromtimestamp(ts, tz=timezone.utc)
        except (OverflowError, OSError, ValueError):
            return None

    if isinstance(raw, str):
        try:
            dt = dateutil_parser.parse(raw)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
        except (ValueError, OverflowError):
            return None

    return None


def _extract_summary(entry: feedparser.FeedParserDict) -> Optional[str]:
    """Pull the best available short text from a feed entry.

    Priority order:
    1. ``content[0].value`` (``<content:encoded>``)
    2. ``summary`` (``<description>`` / ``<summary>``)
    3. ``description`` (some feeds use this key)

    HTML tags are stripped by feedparser automatically when the entry is
    parsed, but we do one extra strip() to remove leading/trailing whitespace.
    """
    # Try rich content first.
    content_list = getattr(entry, "content", None)
    if content_list:
        value = content_list[0].get("value", "").strip()
        if value:
            # Strip any lingering HTML tags that feedparser may have left.
            import re
            value = re.sub(r"<[^>]+>", " ", value).strip()
            return value or None

    summary: str = (
        getattr(entry, "summary", None)
        or getattr(entry, "description", None)
        or ""
    ).strip()
    if summary:
        import re
        summary = re.sub(r"<[^>]+>", " ", summary).strip()
        return summary or None

    return None


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def parse_feed(source: FeedSource) -> list[dict[str, Any]]:
    """Fetch and parse a single RSS/Atom feed.

    Parameters
    ----------
    source:
        A :class:`FeedSource` dict (name, label, url).

    Returns
    -------
    list[dict]
        Normalised article dicts, each containing:
        ``url``, ``url_hash``, ``headline``, ``summary``, ``source``,
        ``published_at``.
    """
    log.info("Fetching feed: %s (%s)", source["label"], source["url"])

    try:
        feed = feedparser.parse(source["url"])
    except Exception as exc:  # noqa: BLE001
        log.error("Failed to fetch feed %s: %s", source["name"], exc)
        return []

    if feed.bozo and feed.bozo_exception:
        # bozo=True means the feed was malformed; we still try to process it.
        log.warning(
            "Feed %s is malformed (bozo): %s",
            source["name"],
            feed.bozo_exception,
        )

    entries: list[dict[str, Any]] = []

    for entry in feed.entries:
        # --- URL ---
        url: str = (
            getattr(entry, "link", None)
            or getattr(entry, "id", None)
            or ""
        ).strip()
        if not url:
            log.debug("Skipping entry with no URL in feed %s", source["name"])
            continue

        # --- Headline ---
        headline: str = getattr(entry, "title", "").strip()
        if not headline:
            log.debug("Skipping entry with no headline: %s", url[:80])
            continue

        # --- Summary ---
        summary = _extract_summary(entry)

        # --- Published date ---
        # Prefer the pre-parsed struct_time; fall back to the raw string.
        published_at = _parse_date(
            getattr(entry, "published_parsed", None)
            or getattr(entry, "updated_parsed", None)
        )
        if published_at is None:
            raw_date = (
                getattr(entry, "published", None)
                or getattr(entry, "updated", None)
            )
            published_at = _parse_date(raw_date)
        if published_at is None:
            log.debug("No parseable date for %s; using NOW()", url[:80])
            published_at = datetime.now(timezone.utc)

        entries.append(
            {
                "url": url,
                "url_hash": _sha256(url),
                "headline": headline,
                "summary": summary,
                "source": source["name"],
                "published_at": published_at,
            }
        )

    log.info(
        "Parsed %d entries from feed %s", len(entries), source["label"]
    )
    return entries


def parse_all_feeds() -> list[dict[str, Any]]:
    """Fetch and parse every registered feed source.

    Returns
    -------
    list[dict]
        Combined list of normalised article dicts from all sources.
    """
    all_entries: list[dict[str, Any]] = []
    for source in SOURCES:
        all_entries.extend(parse_feed(source))

    log.info("Total entries parsed across all feeds: %d", len(all_entries))
    return all_entries
