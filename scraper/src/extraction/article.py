"""Full-text article body extractor.

Attempts two extraction strategies in order:

1. **trafilatura** — high-quality boilerplate-removal library.
2. **newspaper3k** — fallback for sites that trafilatura cannot handle.

If both strategies fail, ``None`` is returned and the caller should proceed
without body text.  This module is designed to be *fault-tolerant*: it
catches all exceptions and logs them rather than propagating them.
"""

import socket
from typing import Optional

from src.utils.logger import get_logger

log = get_logger(__name__)

_TIMEOUT_SECONDS = 10


def _extract_with_trafilatura(url: str) -> Optional[str]:
    """Download and extract article text using trafilatura.

    Parameters
    ----------
    url:
        Article URL to fetch.

    Returns
    -------
    str or None
        Extracted body text, or ``None`` on failure.
    """
    try:
        import trafilatura

        # Set a socket-level timeout so the fetch does not hang forever.
        original_timeout = socket.getdefaulttimeout()
        socket.setdefaulttimeout(_TIMEOUT_SECONDS)
        try:
            downloaded = trafilatura.fetch_url(url)
        finally:
            socket.setdefaulttimeout(original_timeout)

        if not downloaded:
            log.debug("trafilatura: empty response for %s", url[:80])
            return None

        text = trafilatura.extract(
            downloaded,
            include_comments=False,
            include_tables=False,
            no_fallback=False,
        )
        if text and text.strip():
            log.debug("trafilatura: extracted %d chars from %s", len(text), url[:80])
            return text.strip()

        log.debug("trafilatura: extraction returned empty text for %s", url[:80])
        return None

    except Exception as exc:  # noqa: BLE001
        log.warning("trafilatura failed for %s: %s", url[:80], exc)
        return None


def _extract_with_newspaper(url: str) -> Optional[str]:
    """Download and extract article text using newspaper3k.

    Parameters
    ----------
    url:
        Article URL to fetch.

    Returns
    -------
    str or None
        Extracted body text, or ``None`` on failure.
    """
    try:
        from newspaper import Article, ArticleException  # type: ignore[import]

        article = Article(url, request_timeout=_TIMEOUT_SECONDS)
        article.download()
        article.parse()

        text: str = (article.text or "").strip()
        if text:
            log.debug(
                "newspaper3k: extracted %d chars from %s", len(text), url[:80]
            )
            return text

        log.debug("newspaper3k: extraction returned empty text for %s", url[:80])
        return None

    except Exception as exc:  # noqa: BLE001
        log.warning("newspaper3k failed for %s: %s", url[:80], exc)
        return None


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def extract_article_body(url: str) -> Optional[str]:
    """Extract the full body text of an article at *url*.

    Tries trafilatura first; falls back to newspaper3k if that yields nothing.

    Parameters
    ----------
    url:
        The canonical URL of the article page.

    Returns
    -------
    str or None
        Extracted body text (may be several thousand characters), or ``None``
        if both strategies failed or the URL could not be fetched.
    """
    if not url or not url.startswith(("http://", "https://")):
        log.warning("Skipping body extraction for invalid URL: %s", url[:80])
        return None

    log.debug("Extracting body for: %s", url[:80])

    # --- Primary strategy: trafilatura ---
    body = _extract_with_trafilatura(url)
    if body:
        return body

    # --- Fallback strategy: newspaper3k ---
    log.debug("Falling back to newspaper3k for: %s", url[:80])
    body = _extract_with_newspaper(url)
    if body:
        return body

    log.info("Could not extract body for: %s", url[:80])
    return None
