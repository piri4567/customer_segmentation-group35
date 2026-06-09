"""
Customer Segmentation - Main Pipeline
Nova IMS · Machine Learning II · Data Science Degree
 
Reproduces all outputs from raw data:
    python run_pipeline.py
 
Outputs are written to the outputs/ directory (created if absent).
The final customer_clusters.csv is also written to outputs/.
"""
import logging
import os
import sys
 
import numpy as np
import pandas as pd
 
sys.path.insert(0, os.path.dirname(__file__))
 
from src.preprocessing import load_customer_info, preprocess_for_clustering
from src.clustering import (
    find_optimal_k,
    fit_kmeans,
    reduce_pca,
    describe_clusters,
    cluster_profiles,
    assign_segment_labels,
)
from src.association import load_basket, rules_per_cluster
from src.visualization import (
    plot_elbow,
    plot_pca_clusters,
    plot_cluster_radar,
    plot_spend_heatmap,
    plot_feature_distributions,
    plot_revenue_by_segment,
    plot_promo_sensitivity,
    plot_segment_metrics,
)
 
# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)
 
# ── Paths ─────────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")  
OUT_DIR  = os.path.join(BASE_DIR, "outputs")
os.makedirs(OUT_DIR, exist_ok=True)
 
# ── Configuration ─────────────────────────────────────────────────────────────
N_CLUSTERS = 5   # optimal k determined from elbow + silhouette (k=2..9)
 
 
def _out(filename: str) -> str:
    return os.path.join(OUT_DIR, filename)
 
 
def main():
    # ── 1. Load ───────────────────────────────────────────────────────────────
    log.info("Loading data …")
    df_info   = load_customer_info(os.path.join(DATA_DIR, "customer_info.csv"))
    df_basket = load_basket(os.path.join(DATA_DIR, "customer_basket.csv"))
    log.info("  customer_info:   %d rows", len(df_info))
    log.info("  customer_basket: %d rows", len(df_basket))
 
    # ── 2. Preprocess ─────────────────────────────────────────────────────────
    log.info("Preprocessing …")
    X_scaled, feature_cols, scaler, df_eng = preprocess_for_clustering(df_info)
    log.info("  Feature matrix: %s", X_scaled.shape)
 
    # ── 3. Optimal k ─────────────────────────────────────────────────────────
    log.info("Searching for optimal k (k=2..9) …")
    metrics = find_optimal_k(X_scaled, k_range=range(2, 10))
    metrics.to_csv(_out("cluster_metrics.csv"), index=False)
    plot_elbow(metrics, save_path=_out("elbow_plot.png"))
    log.info("\n%s", metrics.to_string(index=False))
 
    # ── 4. Fit KMeans ─────────────────────────────────────────────────────────
    log.info("Fitting KMeans (k=%d) …", N_CLUSTERS)
    km_model, labels = fit_kmeans(X_scaled, n_clusters=N_CLUSTERS)
 
    # ── 5. Segment label assignment ───────────────────────────────────────────
    log.info("Assigning segment labels …")
    segment_names = assign_segment_labels(df_eng, labels)
    log.info("  Cluster → Segment mapping:")
    for cid, name in sorted(segment_names.items()):
        count = (labels == cid).sum()
        log.info("    cluster %d → %-30s (%d customers)", cid, name, count)
 
    # ── 6. Cluster descriptions ───────────────────────────────────────────────
    summary = describe_clusters(df_eng, labels)
    log.info("\n=== Cluster summary ===\n%s", summary.to_string())
    summary.to_csv(_out("cluster_summary.csv"))
 
    spend_cols = [c for c in feature_cols if c.startswith("lifetime_spend_")]
    profile    = cluster_profiles(df_eng, labels, feature_cols)
 
    # ── 7. Core visualisations ────────────────────────────────────────────────
    log.info("Generating visualisations …")
 
    X_pca, _ = reduce_pca(X_scaled)
    plot_pca_clusters(X_pca, labels, segment_names, save_path=_out("pca_clusters.png"))
 
    plot_spend_heatmap(profile, spend_cols, segment_names, save_path=_out("spend_heatmap.png"))
 
    if len(spend_cols) >= 3:
        plot_cluster_radar(profile, spend_cols, segment_names, save_path=_out("radar_chart.png"))
 
    for feat in ["total_spend", "age", "tenure_years",
                 "distinct_stores_visited", "total_children",
                 "percentage_of_products_bought_promotion"]:
        if feat in df_eng.columns:
            plot_feature_distributions(
                df_eng, feat, labels, segment_names,
                save_path=_out(f"dist_{feat}.png"),
            )
 
    # ── 8. NEW: Previously missing figures ───────────────────────────────────
    log.info("Generating supplementary figures …")
    plot_revenue_by_segment(df_eng, labels, segment_names, save_path=_out("fig_revenue.png"))
    plot_promo_sensitivity(df_eng, labels, segment_names,  save_path=_out("fig_promo_sensitivity.png"))
    plot_segment_metrics(df_eng, labels, segment_names,    save_path=_out("fig_seg_metrics.png"))
 
    # ── 9. Association rules per cluster ──────────────────────────────────────
    log.info("Mining association rules per cluster …")
    customer_cluster = pd.Series(
        labels,
        index=df_eng["customer_id"].values,
        name="cluster",
    )
 
    try:
        cluster_rules_dict = rules_per_cluster(
            df_basket,
            customer_cluster,
            min_support=0.01,
            min_confidence=0.25,
            min_lift=1.1,
        )
        for cid, rules in cluster_rules_dict.items():
            if not rules.empty:
                top = rules.head(20)[
                    ["antecedents_str", "consequents_str", "support", "confidence", "lift"]
                ]
                top.to_csv(_out(f"rules_cluster_{cid}.csv"), index=False)
                log.info(
                    "Cluster %d (%s) — top rule: %s → %s  lift=%.2f",
                    cid,
                    segment_names.get(cid, "?"),
                    top.iloc[0]["antecedents_str"],
                    top.iloc[0]["consequents_str"],
                    top.iloc[0]["lift"],
                )
    except Exception as exc:
        log.warning("Association rules step failed: %s — continuing without rules.", exc)
        cluster_rules_dict = {}
 
    # ── 10. Customer → cluster CSV (required deliverable) ────────────────────
    log.info("Saving customer cluster assignments …")
    assignment = pd.DataFrame(
        {
            "customer_id": df_info["customer_id"].values,
            "cluster":     labels,
            "segment":     [segment_names.get(int(l), f"Cluster {l}") for l in labels],
        }
    )
    # Sanity check: every customer must appear exactly once
    assert len(assignment) == len(df_info), "Row count mismatch in assignment CSV"
    assert assignment["customer_id"].nunique() == len(df_info), "Duplicate customer_ids detected"
    assignment.to_csv(_out("customer_clusters.csv"), index=False)
    log.info("  %d customers written to outputs/customer_clusters.csv", len(assignment))
 
    # ── 11. Persist segment mapping ───────────────────────────────────────────
    pd.DataFrame(
        [{"cluster_id": k, "segment": v} for k, v in segment_names.items()]
    ).to_csv(_out("segment_mapping.csv"), index=False)
 
    log.info("Pipeline complete — all outputs in %s/", OUT_DIR)
    return df_eng, labels, cluster_rules_dict, summary, segment_names
 
 
if __name__ == "__main__":
    main()
 