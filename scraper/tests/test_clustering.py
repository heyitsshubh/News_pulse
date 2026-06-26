utf-8
from typing import Any
import pytest
from src.clustering.tfidf import cluster_articles
def _make_article(
    idx: int,
    headline: str,
    summary: str = "",
    source: str = "test",
) -> dict[str, Any]:
    return {
        : f"00000000-0000-0000-0000-{idx:012d}",
        : f"https://example.com/article/{idx}",
        : headline,
        : summary,
        : source,
    }
ELECTION_1 = _make_article(
    1,
    ,
    ,
)
ELECTION_2 = _make_article(
    2,
    ,
    ,
)
ELECTION_3 = _make_article(
    3,
    ,
    ,
)
CLIMATE_1 = _make_article(
    4,
    ,
    ,
)
CLIMATE_2 = _make_article(
    5,
    ,
    ,
)
SPORTS_1 = _make_article(
    6,
    ,
    ,
)
ALL_ARTICLES = [ELECTION_1, ELECTION_2, ELECTION_3, CLIMATE_1, CLIMATE_2, SPORTS_1]
class TestClusterArticlesEdgeCases:
    def test_empty_list_returns_empty(self) -> None:
        result = cluster_articles([])
        assert result == []
    def test_single_article_returns_one_cluster(self) -> None:
        result = cluster_articles([ELECTION_1])
        assert len(result) == 1
        assert result[0]["article_count"] == 1
        assert ELECTION_1 in result[0]["articles"]
    def test_two_identical_articles_are_clustered(self) -> None:
        a1 = _make_article(10, "Breaking news flood warning issued", "Flash flood warning alert issued")
        a2 = _make_article(11, "Breaking news flood warning issued", "Flash flood warning alert issued")
        result = cluster_articles([a1, a2], threshold=0.9)
        assert any(c["article_count"] >= 2 for c in result)
class TestClusterStructure:
    def test_clusters_have_required_keys(self) -> None:
        result = cluster_articles(ALL_ARTICLES, threshold=0.25)
        for cluster in result:
            assert "label" in cluster, "Missing 'label' key"
            assert "articles" in cluster, "Missing 'articles' key"
            assert "article_count" in cluster, "Missing 'article_count' key"
    def test_article_count_matches_articles_list(self) -> None:
        result = cluster_articles(ALL_ARTICLES, threshold=0.25)
        for cluster in result:
            assert cluster["article_count"] == len(cluster["articles"])
    def test_labels_are_non_empty_strings(self) -> None:
        result = cluster_articles(ALL_ARTICLES, threshold=0.25)
        for cluster in result:
            assert isinstance(cluster["label"], str)
            assert len(cluster["label"].strip()) > 0
    def test_no_article_is_lost(self) -> None:
        result = cluster_articles(ALL_ARTICLES, threshold=0.25)
        all_returned_ids = []
        for cluster in result:
            for art in cluster["articles"]:
                all_returned_ids.append(art["id"])
        input_ids = [a["id"] for a in ALL_ARTICLES]
        assert sorted(all_returned_ids) == sorted(input_ids), (
        )
    def test_no_article_is_duplicated(self) -> None:
        result = cluster_articles(ALL_ARTICLES, threshold=0.25)
        all_ids = [
            art["id"]
            for cluster in result
            for art in cluster["articles"]
        ]
        assert len(all_ids) == len(set(all_ids)), "Duplicate articles found in clusters."
class TestClusterTopicGrouping:
    def test_election_articles_share_a_cluster(self) -> None:
        result = cluster_articles(
            [ELECTION_1, ELECTION_2, ELECTION_3],
            threshold=0.15,  
            min_cluster_size=2,
        )
        largest = max(result, key=lambda c: c["article_count"])
        returned_ids = {a["id"] for a in largest["articles"]}
        election_ids = {ELECTION_1["id"], ELECTION_2["id"], ELECTION_3["id"]}
        overlap = returned_ids & election_ids
        assert len(overlap) >= 2, (
            f"Expected at least 2 election articles in the same cluster, got {overlap}"
        )
    def test_dissimilar_articles_are_separated(self) -> None:
        result = cluster_articles(
            [ELECTION_1, ELECTION_2, SPORTS_1],
            threshold=0.3,
            min_cluster_size=2,
        )
        for cluster in result:
            ids = {a["id"] for a in cluster["articles"]}
            if SPORTS_1["id"] in ids:
                election_in_same = ids & {ELECTION_1["id"], ELECTION_2["id"]}
                assert len(election_in_same) == 0, (
                )
class TestMinClusterSize:
    def test_singletons_returned_when_no_pairs(self) -> None:
        articles = [ELECTION_1, CLIMATE_1, SPORTS_1]
        result = cluster_articles(articles, threshold=1.0, min_cluster_size=2)
        assert len(result) == 3
        for c in result:
            assert c["article_count"] == 1
    def test_multi_article_clusters_listed_first(self) -> None:
        result = cluster_articles(ALL_ARTICLES, threshold=0.15, min_cluster_size=2)
        sizes = [c["article_count"] for c in result]
        if len(sizes) > 1:
            assert sizes[0] >= sizes[-1]
    def test_min_cluster_size_one_returns_all_as_clusters(self) -> None:
        result = cluster_articles(ALL_ARTICLES, threshold=0.99, min_cluster_size=1)
        total_articles = sum(c["article_count"] for c in result)
        assert total_articles == len(ALL_ARTICLES)
class TestThresholdBehaviour:
    def test_very_high_threshold_produces_singletons(self) -> None:
        result = cluster_articles(ALL_ARTICLES, threshold=0.999, min_cluster_size=2)
        for c in result:
            assert c["article_count"] == 1
    def test_zero_threshold_groups_everything(self) -> None:
        result = cluster_articles(ALL_ARTICLES, threshold=0.0, min_cluster_size=2)
        max_size = max(c["article_count"] for c in result)
        assert max_size >= 2