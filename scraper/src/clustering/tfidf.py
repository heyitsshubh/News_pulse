"""TF-IDF cosine-similarity clustering for news articles.

Algorithm overview
------------------
1. Concatenate each article's headline + summary into a single document.
2. Fit a TF-IDF matrix (max 5 000 features, English stop words removed).
3. Compute pairwise cosine similarities.
4. Use a greedy Union-Find (disjoint-set) to group articles whose pairwise
   similarity meets or exceeds *threshold*.
5. Return cluster dicts that include a generated human-readable label.

Singleton clusters (fewer than *min_cluster_size* articles) are returned as
individual single-article clusters so that every article is always assigned to
exactly one cluster.
"""

from typing import Any

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from src.clustering.labeler import generate_label
from src.utils.logger import get_logger

log = get_logger(__name__)


# ---------------------------------------------------------------------------
# Union-Find (disjoint-set) data structure
# ---------------------------------------------------------------------------

class _UnionFind:
    """Simple path-compressed Union-Find for grouping indices."""

    def __init__(self, n: int) -> None:
        self._parent: list[int] = list(range(n))
        self._rank: list[int] = [0] * n

    def find(self, x: int) -> int:
        """Return the root of *x*'s component (with path compression)."""
        if self._parent[x] != x:
            self._parent[x] = self.find(self._parent[x])
        return self._parent[x]

    def union(self, x: int, y: int) -> None:
        """Merge the components containing *x* and *y*."""
        rx, ry = self.find(x), self.find(y)
        if rx == ry:
            return
        # Union by rank keeps the tree shallow.
        if self._rank[rx] < self._rank[ry]:
            rx, ry = ry, rx
        self._parent[ry] = rx
        if self._rank[rx] == self._rank[ry]:
            self._rank[rx] += 1

    def groups(self) -> dict[int, list[int]]:
        """Return a mapping of root → list of member indices."""
        result: dict[int, list[int]] = {}
        for i in range(len(self._parent)):
            root = self.find(i)
            result.setdefault(root, []).append(i)
        return result


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def cluster_articles(
    articles: list[dict[str, Any]],
    threshold: float = 0.25,
    min_cluster_size: int = 2,
) -> list[dict[str, Any]]:
    """Cluster a list of article dicts by headline + summary similarity.

    Parameters
    ----------
    articles:
        List of article dicts.  Required keys: ``headline``.
        Optional key: ``summary`` (used when present to enrich the document).
        Any additional keys (e.g. ``id``, ``url``) are preserved and forwarded
        into the returned cluster dicts.
    threshold:
        Minimum cosine-similarity for two articles to be placed in the same
        cluster.  Defaults to ``0.25``.
    min_cluster_size:
        Clusters with fewer members are *not* discarded; instead every such
        article is still returned as its own one-member cluster so that no
        article is lost.

    Returns
    -------
    list[dict]
        List of cluster dicts, each containing:
        - ``label`` (str): auto-generated human-readable label.
        - ``articles`` (list[dict]): member article dicts.
        - ``article_count`` (int): number of members.

    Notes
    -----
    If *articles* is empty or contains fewer than 2 items, the function returns
    immediately without fitting a TF-IDF model.
    """
    if not articles:
        log.warning("cluster_articles called with empty article list.")
        return []

    if len(articles) == 1:
        return [
            {
                "label": articles[0].get("headline", "Article")[:60],
                "articles": articles,
                "article_count": 1,
            }
        ]

    # --- Build document corpus ---
    documents: list[str] = []
    for art in articles:
        headline: str = art.get("headline", "") or ""
        summary: str = art.get("summary", "") or ""
        documents.append(f"{headline} {summary}".strip())

    # --- TF-IDF vectorisation ---
    vectorizer = TfidfVectorizer(
        stop_words="english",
        max_features=5000,
        sublinear_tf=True,        # Apply log(1+tf) — dampens very frequent terms.
        strip_accents="unicode",
        analyzer="word",
        min_df=1,
    )

    try:
        tfidf_matrix = vectorizer.fit_transform(documents)
    except ValueError as exc:
        # This can happen if all documents are empty after stop-word removal.
        log.error("TF-IDF vectorisation failed: %s", exc)
        # Return every article as its own cluster.
        return [
            {"label": art.get("headline", "Article")[:60], "articles": [art], "article_count": 1}
            for art in articles
        ]

    n = len(articles)
    log.info(
        "TF-IDF matrix: %d articles × %d features", n, tfidf_matrix.shape[1]
    )

    # --- Pairwise cosine similarity ---
    # We compute in one shot; for large corpora (>10k articles) a chunked
    # approach would be more memory-efficient.
    sim_matrix: np.ndarray = cosine_similarity(tfidf_matrix)

    # --- Union-Find grouping ---
    uf = _UnionFind(n)
    for i in range(n):
        for j in range(i + 1, n):
            if sim_matrix[i, j] >= threshold:
                uf.union(i, j)

    groups = uf.groups()  # {root: [idx, ...]}

    # --- Build cluster result dicts ---
    clusters: list[dict[str, Any]] = []
    for root, member_indices in groups.items():
        member_articles = [articles[i] for i in member_indices]
        label = generate_label(articles, vectorizer, tfidf_matrix, member_indices)

        clusters.append(
            {
                "label": label,
                "articles": member_articles,
                "article_count": len(member_articles),
            }
        )

    # Sort largest clusters first for display convenience.
    clusters.sort(key=lambda c: c["article_count"], reverse=True)

    # Separate multi-article clusters from singletons.
    multi = [c for c in clusters if c["article_count"] >= min_cluster_size]
    singletons = [c for c in clusters if c["article_count"] < min_cluster_size]

    # For singletons, use the headline as the label.
    for cluster in singletons:
        if cluster["articles"]:
            cluster["label"] = cluster["articles"][0].get("headline", "Article")[:60]

    all_clusters = multi + singletons

    log.info(
        "Clustering complete: %d multi-article clusters, %d singletons.",
        len(multi),
        len(singletons),
    )
    return all_clusters
