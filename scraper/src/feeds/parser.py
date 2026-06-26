utf-8
import hashlib
from datetime import datetime, timezone
from typing import Any, Optional
import feedparser
from dateutil import parser as dateutil_parser
from src.feeds.sources import FeedSource, SOURCES
from src.utils.logger import get_logger
log = get_logger(__name__)
def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()
def _parse_date(raw: Any) -> Optional[datetime]:
    if raw is None:
        return None
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
    content_list = getattr(entry, "content", None)
    if content_list:
        value = content_list[0].get("value", "").strip()
        if value:
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
def parse_feed(source: FeedSource) -> list[dict[str, Any]]:
    log.info("Fetching feed: %s (%s)", source["label"], source["url"])
    try:
        feed = feedparser.parse(source["url"])
    except Exception as exc:  
        log.error("Failed to fetch feed %s: %s", source["name"], exc)
        return []
    if feed.bozo and feed.bozo_exception:
        log.warning(
            ,
            source["name"],
            feed.bozo_exception,
        )
    entries: list[dict[str, Any]] = []
    for entry in feed.entries:
        url: str = (
            getattr(entry, "link", None)
            or getattr(entry, "id", None)
            or ""
        ).strip()
        if not url:
            log.debug("Skipping entry with no URL in feed %s", source["name"])
            continue
        headline: str = getattr(entry, "title", "").strip()
        if not headline:
            log.debug("Skipping entry with no headline: %s", url[:80])
            continue
        summary = _extract_summary(entry)
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
                : url,
                : _sha256(url),
                : headline,
                : summary,
                : source["name"],
                : published_at,
            }
        )
    log.info(
        , len(entries), source["label"]
    )
    return entries
def parse_all_feeds() -> list[dict[str, Any]]:
    all_entries: list[dict[str, Any]] = []
    for source in SOURCES:
        all_entries.extend(parse_feed(source))
    log.info("Total entries parsed across all feeds: %d", len(all_entries))
    return all_entries