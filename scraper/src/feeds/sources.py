utf-8
from typing import TypedDict
class FeedSource(TypedDict):
    name: str
    label: str
    url: str
SOURCES: list[FeedSource] = [
    {
        : "bbc",
        : "BBC News",
        : "http://feeds.bbci.co.uk/news/rss.xml",
    },
    {
        : "npr",
        : "NPR",
        : "https://feeds.npr.org/1001/rss.xml",
    },
    {
        : "guardian",
        : "The Guardian",
        : "https://www.theguardian.com/world/rss",
    },
]