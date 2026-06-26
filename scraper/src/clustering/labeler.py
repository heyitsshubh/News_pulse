utf-8
from typing import Any
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
def generate_label(
    articles: list[dict[str, Any]],
    vectorizer: TfidfVectorizer,
    tfidf_matrix: Any,  
    indices: list[int],
) -> str:
    if not indices:
        return "Cluster"
    cluster_matrix = tfidf_matrix[indices]          
    centroid = np.asarray(cluster_matrix.mean(axis=0)).flatten()  
    feature_names: list[str] = vectorizer.get_feature_names_out().tolist()
    if centroid.size == 0 or not feature_names:
        return "Cluster"
    top_n = min(3, len(feature_names))
    top_indices = np.argsort(centroid)[::-1][:top_n]
    top_terms = [feature_names[i].title() for i in top_indices if centroid[i] > 0]
    if not top_terms:
        return "Cluster"
    return " ".join(top_terms)