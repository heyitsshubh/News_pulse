"""Registered RSS feed sources for News Pulse.

Add new sources here as plain dicts with the following keys:

- ``name``  — short identifier (used as the ``source`` column value).
- ``label`` — human-readable display name.
- ``url``   — RSS/Atom feed URL.
"""

from typing import TypedDict


class FeedSource(TypedDict):
    """Type alias for a feed source entry."""

    name: str
    label: str
    url: str


SOURCES: list[FeedSource] = [
    {
        "name": "bbc",
        "label": "BBC News",
        "url": "http://feeds.bbci.co.uk/news/rss.xml",
    },
    {
        "name": "npr",
        "label": "NPR",
        "url": "https://feeds.npr.org/1001/rss.xml",
    },
    {
        "name": "guardian",
        "label": "The Guardian",
        "url": "https://www.theguardian.com/world/rss",
    },
]
