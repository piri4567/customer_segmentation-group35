"""
Customer Segmentation - Clustering Module
"""
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score


def find_optimal_k(X_scaled: np.ndarray, k_range=range(2, 11), random_state: int = 42) -> pd.DataFrame:
    """Compute inertia and silhouette score for a range of k values."""
    results = []
    for k in k_range:
        km = KMeans(n_clusters=k, random_state=random_state, n_init=10)
        labels = km.fit_predict(X_scaled)
        inertia = km.inertia_
        sil = silhouette_score(X_scaled, labels, sample_size=min(5000, len(labels)), random_state=random_state)
        results.append({"k": k, "inertia": inertia, "silhouette": sil})
    return pd.DataFrame(results)


def fit_kmeans(X_scaled: np.ndarray, n_clusters: int, random_state: int = 42) -> tuple:
    """Fit KMeans and return (model, labels)."""
    km = KMeans(n_clusters=n_clusters, random_state=random_state, n_init=15)
    labels = km.fit_predict(X_scaled)
    return km, labels


def reduce_pca(X_scaled: np.ndarray, n_components: int = 2) -> tuple:
    """PCA reduction for visualization."""
    pca = PCA(n_components=n_components, random_state=42)
    X_pca = pca.fit_transform(X_scaled)
    return X_pca, pca


def cluster_profiles(df_eng: pd.DataFrame, labels: np.ndarray, feature_cols: list) -> pd.DataFrame:
    """Return mean feature values per cluster."""
    df_eng = df_eng.copy()
    df_eng["cluster"] = labels
    profile = df_eng.groupby("cluster")[feature_cols].mean().round(2)
    return profile


def describe_clusters(df_eng: pd.DataFrame, labels: np.ndarray) -> pd.DataFrame:
    """High-level description per cluster."""
    df_eng = df_eng.copy()
    df_eng["cluster"] = labels

    summary_cols = [
        "age", "total_spend", "total_children",
        "tenure_years", "number_complaints",
        "distinct_stores_visited", "percentage_of_products_bought_promotion",
        "lifetime_spend_groceries", "lifetime_spend_electronics",
        "lifetime_spend_meat", "lifetime_spend_fish",
        "lifetime_spend_videogames", "lifetime_spend_petfood",
        "lifetime_spend_alcohol_drinks",
    ]
    summary_cols = [c for c in summary_cols if c in df_eng.columns]
    summary = df_eng.groupby("cluster")[summary_cols].mean().round(1)
    summary["size"] = df_eng.groupby("cluster").size()
    summary["pct"] = (summary["size"] / len(df_eng) * 100).round(1)
    return summary
