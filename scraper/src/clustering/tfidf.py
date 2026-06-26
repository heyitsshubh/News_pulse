utf-8
from typing import Any
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from src.clustering.labeler import generate_label
from src.utils.logger import get_logger
log = get_logger(__name__)
class _UnionFind:
    def __init__(self, n: int) -> None:
        self._parent: list[int] = list(range(n))
        self._rank: list[int] = [0] * n
    def find(self, x: int) -> int:
        if self._parent[x] != x:
            self._parent[x] = self.find(self._parent[x])
        return self._parent[x]
    def union(self, x: int, y: int) -> None:
        rx, ry = self.find(x), self.find(y)
        if rx == ry:
            return
        if self._rank[rx] < self._rank[ry]:
            rx, ry = ry, rx
        self._parent[ry] = rx
        if self._rank[rx] == self._rank[ry]:
            self._rank[rx] += 1
    def groups(self) -> dict[int, list[int]]:
        result: dict[int, list[int]] = {}
        for i in range(len(self._parent)):
            root = self.find(i)
            result.setdefault(root, []).append(i)
        return result
def cluster_articles(
    articles: list[dict[str, Any]],
    threshold: float = 0.25,
    min_cluster_size: int = 2,
) -> list[dict[str, Any]]:
    if not articles:
        log.warning("cluster_articles called with empty article list.")
        return []
    if len(articles) == 1:
        return [
            {
                : articles[0].get("headline", "Article")[:60],
                : articles,
                : 1,
            }
        ]
    documents: list[str] = []
    for art in articles:
        headline: str = art.get("headline", "") or ""
        summary: str = art.get("summary", "") or ""
        documents.append(f"{headline} {summary}".strip())
    vectorizer = TfidfVectorizer(
        stop_words="english",
        max_features=5000,
        sublinear_tf=True,        
        strip_accents="unicode",
        analyzer="word",
        min_df=1,
    )
    try:
        tfidf_matrix = vectorizer.fit_transform(documents)
    except ValueError as exc:
        log.error("TF-IDF vectorisation failed: %s", exc)
        return [
            {"label": art.get("headline", "Article")[:60], "articles": [art], "article_count": 1}
            for art in articles
        ]
    n = len(articles)
    log.info(
        , n, tfidf_matrix.shape[1]
    )
    sim_matrix: np.ndarray = cosine_similarity(tfidf_matrix)
    uf = _UnionFind(n)
    for i in range(n):
        for j in range(i + 1, n):
            if sim_matrix[i, j] >= threshold:
                uf.union(i, j)
    groups = uf.groups()  
    clusters: list[dict[str, Any]] = []
    for root, member_indices in groups.items():
        member_articles = [articles[i] for i in member_indices]
        label = generate_label(articles, vectorizer, tfidf_matrix, member_indices)
        clusters.append(
            {
                : label,
                : member_articles,
                : len(member_articles),
            }
        )
    clusters.sort(key=lambda c: c["article_count"], reverse=True)
    multi = [c for c in clusters if c["article_count"] >= min_cluster_size]
    singletons = [c for c in clusters if c["article_count"] < min_cluster_size]
    for cluster in singletons:
        if cluster["articles"]:
            cluster["label"] = cluster["articles"][0].get("headline", "Article")[:60]
    all_clusters = multi + singletons
    log.info(
        ,
        len(multi),
        len(singletons),
    )
    return all_clusters