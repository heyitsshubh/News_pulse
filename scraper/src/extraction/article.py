utf-8
import socket
from typing import Optional
from src.utils.logger import get_logger
log = get_logger(__name__)
_TIMEOUT_SECONDS = 10
def _extract_with_trafilatura(url: str) -> Optional[str]:
    try:
        import trafilatura
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
    except Exception as exc:  
        log.warning("trafilatura failed for %s: %s", url[:80], exc)
        return None
def _extract_with_newspaper(url: str) -> Optional[str]:
    try:
        from newspaper import Article, ArticleException  
        article = Article(url, request_timeout=_TIMEOUT_SECONDS)
        article.download()
        article.parse()
        text: str = (article.text or "").strip()
        if text:
            log.debug(
                , len(text), url[:80]
            )
            return text
        log.debug("newspaper3k: extraction returned empty text for %s", url[:80])
        return None
    except Exception as exc:  
        log.warning("newspaper3k failed for %s: %s", url[:80], exc)
        return None
def extract_article_body(url: str) -> Optional[str]:
    if not url or not url.startswith(("http://", "https://")):
        log.warning("Skipping body extraction for invalid URL: %s", url[:80])
        return None
    log.debug("Extracting body for: %s", url[:80])
    body = _extract_with_trafilatura(url)
    if body:
        return body
    log.debug("Falling back to newspaper3k for: %s", url[:80])
    body = _extract_with_newspaper(url)
    if body:
        return body
    log.info("Could not extract body for: %s", url[:80])
    return None