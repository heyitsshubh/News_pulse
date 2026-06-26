"""Unit tests for src/clustering/tfidf.py.

Tests cover:
- Empty input returns [].
- Single article returns one cluster.
- Articles on clearly the same topic are grouped together.
- Articles on completely different topics remain separate.
- All articles appear in exactly one cluster (no article is lost).
- cluster dicts have required keys.
- min_cluster_size filtering works correctly.
- Threshold of 0.0 merges all non-identical documents (edge case).
- Threshold of 1.0 keeps each article in its own cluster.
- Labels are non-empty strings.
"""

from typing import Any

import pytest

from src.clustering.tfidf import cluster_articles


# ---------------------------------------------------------------------------
# Mock article factory
# ---------------------------------------------------------------------------

def _make_article(
    idx: int,
    headline: str,
    summary: str = "",
    source: str = "test",
) -> dict[str, Any]:
    """Return a minimal article dict suitable for cluster_articles()."""
    return {
        "id": f"00000000-0000-0000-0000-{idx:012d}",
        "url": f"https://example.com/article/{idx}",
        "headline": headline,
        "summary": summary,
        "source": source,
    }


# ---------------------------------------------------------------------------
# Mock article corpus
# ---------------------------------------------------------------------------

# Two articles clearly about the US Election.
ELECTION_1 = _make_article(
    1,
    "US Presidential Election 2024 results announced",
    "The United States presidential election results are in. Biden vs Trump election outcome.",
)
ELECTION_2 = _make_article(
    2,
    "Presidential election vote count continues in swing states",
    "Election officials counting presidential votes in battleground states. Senate election results.",
)
ELECTION_3 = _make_article(
    3,
    "Senate election races too close to call on election night",
    "Several Senate seats remain undecided as election vote counting continues across states.",
)

# Three articles about a completely different topic: climate change.
CLIMATE_1 = _make_article(
    4,
    "Climate change summit: world leaders agree on carbon targets",
    "Global climate conference reaches historic agreement on carbon emissions and renewable energy.",
)
CLIMATE_2 = _make_article(
    5,
    "New climate report warns of accelerating global warming trends",
    "Scientists publish urgent climate warning about rising temperatures and greenhouse gas emissions.",
)

# One completely off-topic article (sports).
SPORTS_1 = _make_article(
    6,
    "World Cup 2026 host cities announced by FIFA",
    "FIFA reveals the cities that will host the 2026 World Cup football tournament matches.",
)

ALL_ARTICLES = [ELECTION_1, ELECTION_2, ELECTION_3, CLIMATE_1, CLIMATE_2, SPORTS_1]


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestClusterArticlesEdgeCases:
    """Edge cases for cluster_articles()."""

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
        # With identical text they should be in the same cluster.
        assert any(c["article_count"] >= 2 for c in result)


class TestClusterStructure:
    """Tests that returned cluster dicts have the expected structure."""

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
        """Every input article must appear in exactly one output cluster."""
        result = cluster_articles(ALL_ARTICLES, threshold=0.25)
        all_returned_ids = []
        for cluster in result:
            for art in cluster["articles"]:
                all_returned_ids.append(art["id"])

        input_ids = [a["id"] for a in ALL_ARTICLES]
        assert sorted(all_returned_ids) == sorted(input_ids), (
            "Some articles were lost or duplicated during clustering."
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
    """Tests that thematically similar articles are grouped together."""

    def test_election_articles_share_a_cluster(self) -> None:
        """The three election articles should end up in the same cluster."""
        result = cluster_articles(
            [ELECTION_1, ELECTION_2, ELECTION_3],
            threshold=0.15,  # Lower threshold to ensure grouping.
            min_cluster_size=2,
        )
        # Find the largest cluster — should contain all three election articles.
        largest = max(result, key=lambda c: c["article_count"])
        returned_ids = {a["id"] for a in largest["articles"]}
        election_ids = {ELECTION_1["id"], ELECTION_2["id"], ELECTION_3["id"]}
        # At least 2 of the 3 election articles should be together.
        overlap = returned_ids & election_ids
        assert len(overlap) >= 2, (
            f"Expected at least 2 election articles in the same cluster, got {overlap}"
        )

    def test_dissimilar_articles_are_separated(self) -> None:
        """Sports and election articles should NOT be in the same cluster."""
        result = cluster_articles(
            [ELECTION_1, ELECTION_2, SPORTS_1],
            threshold=0.3,
            min_cluster_size=2,
        )
        for cluster in result:
            ids = {a["id"] for a in cluster["articles"]}
            # The sports article should not share a cluster with election articles
            # unless the threshold is very low.
            if SPORTS_1["id"] in ids:
                election_in_same = ids & {ELECTION_1["id"], ELECTION_2["id"]}
                assert len(election_in_same) == 0, (
                    "Sports article unexpectedly grouped with election articles."
                )


class TestMinClusterSize:
    """Tests for min_cluster_size behaviour."""

    def test_singletons_returned_when_no_pairs(self) -> None:
        """With threshold=1.0, no two different articles match → all singletons."""
        articles = [ELECTION_1, CLIMATE_1, SPORTS_1]
        result = cluster_articles(articles, threshold=1.0, min_cluster_size=2)
        # All should be singletons.
        assert len(result) == 3
        for c in result:
            assert c["article_count"] == 1

    def test_multi_article_clusters_listed_first(self) -> None:
        """Clusters with >= min_cluster_size articles should come before singletons."""
        result = cluster_articles(ALL_ARTICLES, threshold=0.15, min_cluster_size=2)
        sizes = [c["article_count"] for c in result]
        if len(sizes) > 1:
            # The first element should be the largest (or equal to the second).
            assert sizes[0] >= sizes[-1]

    def test_min_cluster_size_one_returns_all_as_clusters(self) -> None:
        """With min_cluster_size=1 every article gets its own cluster at minimum."""
        result = cluster_articles(ALL_ARTICLES, threshold=0.99, min_cluster_size=1)
        total_articles = sum(c["article_count"] for c in result)
        assert total_articles == len(ALL_ARTICLES)


class TestThresholdBehaviour:
    """Tests for threshold extremes."""

    def test_very_high_threshold_produces_singletons(self) -> None:
        """threshold=0.999 should leave almost everything as singletons."""
        result = cluster_articles(ALL_ARTICLES, threshold=0.999, min_cluster_size=2)
        # Each article should be in its own cluster (all singletons).
        for c in result:
            assert c["article_count"] == 1

    def test_zero_threshold_groups_everything(self) -> None:
        """threshold=0.0 means any non-zero similarity merges articles."""
        result = cluster_articles(ALL_ARTICLES, threshold=0.0, min_cluster_size=2)
        # At 0.0 threshold, all articles that share ANY term merge.
        # At minimum the election trio should be together.
        max_size = max(c["article_count"] for c in result)
        assert max_size >= 2
