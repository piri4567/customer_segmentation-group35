"""
Customer Segmentation - Main Pipeline
Run this script to reproduce all results:
    python run_pipeline.py
"""
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(__file__))
from src.preprocessing import load_customer_info, preprocess_for_clustering
from src.clustering import find_optimal_k, fit_kmeans, reduce_pca, describe_clusters, cluster_profiles
from src.association import load_basket, rules_per_cluster
from src.visualization import (
    plot_elbow, plot_pca_clusters, plot_cluster_radar,
    plot_spend_heatmap, plot_feature_distributions
)

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
OUT_DIR = os.path.join(os.path.dirname(__file__), "outputs")
os.makedirs(OUT_DIR, exist_ok=True)

N_CLUSTERS = 5   # optimal k determined from elbow + silhouette analysis


def main():
    # ── 1. Load & preprocess ──────────────────────────────────────────────────
    print("Loading data...")
    df_info = load_customer_info(os.path.join(DATA_DIR, "customer_info.csv"))
    df_basket = load_basket(os.path.join(DATA_DIR, "customer_basket.csv"))

    print("Preprocessing...")
    X_scaled, feature_cols, idx, scaler, df_eng = preprocess_for_clustering(df_info)

    # ── 2. Find optimal k ─────────────────────────────────────────────────────
    print("Finding optimal k (this may take a minute)...")
    metrics = find_optimal_k(X_scaled, k_range=range(2, 10))
    metrics.to_csv(os.path.join(OUT_DIR, "cluster_metrics.csv"), index=False)
    plot_elbow(metrics, save_path=os.path.join(OUT_DIR, "elbow_plot.png"))
    print(metrics.to_string(index=False))

    # ── 3. Fit KMeans ─────────────────────────────────────────────────────────
    print(f"\nFitting KMeans with k={N_CLUSTERS}...")
    km_model, labels = fit_kmeans(X_scaled, n_clusters=N_CLUSTERS)

    # ── 4. Visualize clusters ─────────────────────────────────────────────────
    print("Generating visualizations...")
    X_pca, pca = reduce_pca(X_scaled)
    plot_pca_clusters(X_pca, labels, save_path=os.path.join(OUT_DIR, "pca_clusters.png"))

    spend_cols = [c for c in feature_cols if c.startswith("lifetime_spend_")]
    profile = cluster_profiles(df_eng, labels, feature_cols)
    plot_spend_heatmap(profile, spend_cols, save_path=os.path.join(OUT_DIR, "spend_heatmap.png"))

    radar_cols = spend_cols
    if len(radar_cols) >= 3:
        plot_cluster_radar(profile, radar_cols, save_path=os.path.join(OUT_DIR, "radar_chart.png"))

    for feat in ["total_spend", "age", "tenure_years"]:
        if feat in df_eng.columns:
            plot_feature_distributions(
                df_eng, feat, labels,
                save_path=os.path.join(OUT_DIR, f"dist_{feat}.png")
            )

    # ── 5. Cluster summaries ──────────────────────────────────────────────────
    summary = describe_clusters(df_eng, labels)
    print("\n=== Cluster Summary ===")
    print(summary.to_string())
    summary.to_csv(os.path.join(OUT_DIR, "cluster_summary.csv"))

    # ── 6. Association rules per cluster ─────────────────────────────────────
    print("\nMining association rules per cluster (this may take several minutes)...")
    customer_cluster = pd.Series(labels, index=df_eng["customer_id"].values)
    cluster_rules_dict = rules_per_cluster(
        df_basket, customer_cluster,
        min_support=0.01, min_confidence=0.25, min_lift=1.1
    )
    for cid, rules in cluster_rules_dict.items():
        if not rules.empty:
            top = rules.head(20)[["antecedents_str", "consequents_str", "support", "confidence", "lift"]]
            top.to_csv(os.path.join(OUT_DIR, f"rules_cluster_{cid}.csv"), index=False)
            print(f"\nCluster {cid} - top rules:")
            print(top.head(5).to_string(index=False))

    # ── 7. Customer → Cluster assignment CSV ──────────────────────────────────
    assignment = pd.DataFrame({
        "customer_id": df_info["customer_id"],
        "cluster": labels
    })
    assignment.to_csv(os.path.join(OUT_DIR, "customer_clusters.csv"), index=False)
    print(f"\nCustomer cluster assignments saved -> outputs/customer_clusters.csv")
    print(f"Total customers: {len(assignment)}")

    print("\nPipeline complete. All outputs saved to /outputs/")
    return df_eng, labels, cluster_rules_dict, summary


if __name__ == "__main__":
    main()
