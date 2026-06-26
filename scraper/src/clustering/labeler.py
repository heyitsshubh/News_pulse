"""Cluster label generator.

Generates a human-readable label for a cluster of articles by examining the
cluster's centroid TF-IDF vector and extracting the top-3 most discriminating
terms.
"""

from typing import Any

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer


def generate_label(
    articles: list[dict[str, Any]],
    vectorizer: TfidfVectorizer,
    tfidf_matrix: Any,  # scipy sparse matrix
    indices: list[int],
) -> str:
    """Generate a human-readable label for a cluster.

    The label is derived by computing the centroid of the cluster's TF-IDF
    vectors and then picking the top-3 terms with the highest centroid weight.
    Terms are title-cased and joined with spaces.

    Example output: ``"Election Senate Vote"``

    Parameters
    ----------
    articles:
        Full list of article dicts (same order as rows in *tfidf_matrix*).
        Not used directly but kept for potential future use (e.g. date ranges).
    vectorizer:
        The fitted :class:`~sklearn.feature_extraction.text.TfidfVectorizer`
        instance whose vocabulary is used to map column indices to terms.
    tfidf_matrix:
        The full sparse TF-IDF matrix (``n_articles × n_features``).
    indices:
        Row indices (into *tfidf_matrix*) of the articles that belong to this
        cluster.

    Returns
    -------
    str
        A title-cased label string, e.g. ``"Climate Energy Policy"``.
        Falls back to ``"Cluster"`` if no terms can be extracted.
    """
    if not indices:
        return "Cluster"

    # Extract the submatrix for this cluster and compute the centroid.
    cluster_matrix = tfidf_matrix[indices]          # shape: (k, n_features)
    centroid = np.asarray(cluster_matrix.mean(axis=0)).flatten()  # (n_features,)

    # Get feature names from the vectorizer.
    feature_names: list[str] = vectorizer.get_feature_names_out().tolist()

    if centroid.size == 0 or not feature_names:
        return "Cluster"

    # Pick the top-3 terms by centroid weight.
    top_n = min(3, len(feature_names))
    top_indices = np.argsort(centroid)[::-1][:top_n]
    top_terms = [feature_names[i].title() for i in top_indices if centroid[i] > 0]

    if not top_terms:
        return "Cluster"

    return " ".join(top_terms)
