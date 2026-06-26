utf-8
import hashlib
import time
from datetime import datetime, timezone
from types import SimpleNamespace
from typing import Any
from unittest.mock import MagicMock, patch
import pytest
from src.feeds.parser import (
    _extract_summary,
    _parse_date,
    _sha256,
    parse_feed,
)
class TestSha256:
    def test_known_hash(self) -> None:
        url = "https://www.bbc.co.uk/news/world-12345"
        expected = hashlib.sha256(url.encode()).hexdigest()
        assert _sha256(url) == expected
    def test_empty_string(self) -> None:
        result = _sha256("")
        assert isinstance(result, str)
        assert len(result) == 64  
    def test_different_urls_different_hashes(self) -> None:
        h1 = _sha256("https://example.com/a")
        h2 = _sha256("https://example.com/b")
        assert h1 != h2
    def test_same_url_same_hash(self) -> None:
        url = "https://example.com/stable"
        assert _sha256(url) == _sha256(url)
    def test_hash_length(self) -> None:
        assert len(_sha256("any string")) == 64
class TestParseDate:
    def test_returns_none_for_none(self) -> None:
        assert _parse_date(None) is None
    def test_struct_time(self) -> None:
        st = time.strptime("2024-01-15 12:00:00", "%Y-%m-%d %H:%M:%S")
        result = _parse_date(st)
        assert isinstance(result, datetime)
        assert result.tzinfo is not None
    def test_iso_string(self) -> None:
        result = _parse_date("2024-03-10T08:30:00+00:00")
        assert isinstance(result, datetime)
        assert result.year == 2024
        assert result.month == 3
        assert result.day == 10
    def test_rfc2822_string(self) -> None:
        result = _parse_date("Mon, 15 Jan 2024 12:00:00 GMT")
        assert isinstance(result, datetime)
        assert result.year == 2024
    def test_naive_datetime_gets_utc(self) -> None:
        result = _parse_date("2024-05-01 09:00:00")
        assert isinstance(result, datetime)
        assert result.tzinfo == timezone.utc
    def test_garbage_string_returns_none(self) -> None:
        result = _parse_date("not-a-date-at-all")
        assert result is None
    def test_unknown_type_returns_none(self) -> None:
        assert _parse_date(42) is None  
def _make_entry(**kwargs: Any) -> Any:
    entry = SimpleNamespace(**kwargs)
    if not hasattr(entry, "content"):
        entry.content = []
    if not hasattr(entry, "summary"):
        entry.summary = ""
    if not hasattr(entry, "description"):
        entry.description = ""
    return entry
class TestExtractSummary:
    def test_prefers_content_encoded(self) -> None:
        entry = _make_entry(content=[{"value": "Full content text"}])
        result = _extract_summary(entry)
        assert result == "Full content text"
    def test_falls_back_to_summary(self) -> None:
        entry = _make_entry(summary="Short summary text")
        result = _extract_summary(entry)
        assert result == "Short summary text"
    def test_strips_html_from_summary(self) -> None:
        entry = _make_entry(summary="<p>Hello <b>world</b></p>")
        result = _extract_summary(entry)
        assert "<" not in (result or "")
        assert "Hello" in (result or "")
        assert "world" in (result or "")
    def test_strips_html_from_content(self) -> None:
        entry = _make_entry(content=[{"value": "<div>Article <em>text</em></div>"}])
        result = _extract_summary(entry)
        assert "<" not in (result or "")
    def test_returns_none_when_all_empty(self) -> None:
        entry = _make_entry()
        result = _extract_summary(entry)
        assert result is None
    def test_whitespace_only_returns_none(self) -> None:
        entry = _make_entry(summary="   ")
        result = _extract_summary(entry)
        assert result is None
def _build_mock_feed(entries: list[dict[str, Any]]) -> MagicMock:
    mock_feed = MagicMock()
    mock_feed.bozo = False
    mock_feed.bozo_exception = None
    feed_entries = []
    for e in entries:
        entry = SimpleNamespace(
            link=e.get("link", ""),
            id=e.get("id", ""),
            title=e.get("title", ""),
            summary=e.get("summary", ""),
            description=e.get("description", ""),
            content=e.get("content", []),
            published_parsed=e.get("published_parsed", None),
            updated_parsed=e.get("updated_parsed", None),
            published=e.get("published", None),
            updated=e.get("updated", None),
        )
        feed_entries.append(entry)
    mock_feed.entries = feed_entries
    return mock_feed
class TestParseFeed:
    _SOURCE = {"name": "bbc", "label": "BBC News", "url": "http://feeds.bbci.co.uk/news/rss.xml"}
    def test_returns_list_of_dicts(self) -> None:
        mock_feed = _build_mock_feed([
            {"link": "https://bbc.co.uk/1", "title": "Test Article", "summary": "A summary"},
        ])
        with patch("src.feeds.parser.feedparser.parse", return_value=mock_feed):
            result = parse_feed(self._SOURCE)
        assert isinstance(result, list)
        assert len(result) == 1
    def test_dict_contains_required_keys(self) -> None:
        mock_feed = _build_mock_feed([
            {"link": "https://bbc.co.uk/2", "title": "Another Article"},
        ])
        with patch("src.feeds.parser.feedparser.parse", return_value=mock_feed):
            result = parse_feed(self._SOURCE)
        article = result[0]
        for key in ("url", "url_hash", "headline", "source", "published_at"):
            assert key in article, f"Missing key: {key}"
    def test_url_hash_is_sha256_of_url(self) -> None:
        url = "https://bbc.co.uk/specific-article"
        mock_feed = _build_mock_feed([{"link": url, "title": "Hash Test"}])
        with patch("src.feeds.parser.feedparser.parse", return_value=mock_feed):
            result = parse_feed(self._SOURCE)
        assert result[0]["url_hash"] == hashlib.sha256(url.encode()).hexdigest()
    def test_skips_entry_with_no_url(self) -> None:
        mock_feed = _build_mock_feed([
            {"link": "", "id": "", "title": "No URL Article"},
        ])
        with patch("src.feeds.parser.feedparser.parse", return_value=mock_feed):
            result = parse_feed(self._SOURCE)
        assert result == []
    def test_skips_entry_with_no_headline(self) -> None:
        mock_feed = _build_mock_feed([
            {"link": "https://bbc.co.uk/no-title", "title": ""},
        ])
        with patch("src.feeds.parser.feedparser.parse", return_value=mock_feed):
            result = parse_feed(self._SOURCE)
        assert result == []
    def test_published_at_falls_back_to_now(self) -> None:
        mock_feed = _build_mock_feed([
            {"link": "https://bbc.co.uk/no-date", "title": "No Date Article"},
        ])
        before = datetime.now(timezone.utc)
        with patch("src.feeds.parser.feedparser.parse", return_value=mock_feed):
            result = parse_feed(self._SOURCE)
        after = datetime.now(timezone.utc)
        pub = result[0]["published_at"]
        assert before <= pub <= after
    def test_source_matches_feed_name(self) -> None:
        mock_feed = _build_mock_feed([
            {"link": "https://bbc.co.uk/src-test", "title": "Source Test"},
        ])
        with patch("src.feeds.parser.feedparser.parse", return_value=mock_feed):
            result = parse_feed(self._SOURCE)
        assert result[0]["source"] == "bbc"
    def test_handles_feedparser_exception_gracefully(self) -> None:
        with patch("src.feeds.parser.feedparser.parse", side_effect=Exception("network error")):
            result = parse_feed(self._SOURCE)
        assert result == []
    def test_multiple_entries(self) -> None:
        entries = [
            {"link": f"https://bbc.co.uk/{i}", "title": f"Article {i}"}
            for i in range(5)
        ]
        mock_feed = _build_mock_feed(entries)
        with patch("src.feeds.parser.feedparser.parse", return_value=mock_feed):
            result = parse_feed(self._SOURCE)
        assert len(result) == 5