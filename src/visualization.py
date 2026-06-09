"""
Customer Segmentation - Visualisation Module
Nova IMS · Machine Learning II · Data Science Degree
 
All public functions accept an optional *save_path* argument.  When provided
the figure is saved to that path (PNG, 180 dpi) in addition to being returned.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd
import seaborn as sns
 
PALETTE = sns.color_palette("tab10")
DPI = 180
 
 
def _save(fig: plt.Figure, save_path: str | None) -> plt.Figure:
    if save_path:
        fig.savefig(save_path, dpi=DPI, bbox_inches="tight")
    return fig
 
 
# ── Cluster selection ─────────────────────────────────────────────────────────
 
def plot_elbow(metrics_df: pd.DataFrame, save_path: str | None = None) -> plt.Figure:
    """Elbow (inertia) and silhouette score side-by-side."""
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
 
    axes[0].plot(metrics_df["k"], metrics_df["inertia"], marker="o", color="steelblue")
    axes[0].set_title("Elbow Method (Inertia)")
    axes[0].set_xlabel("Number of Clusters (k)")
    axes[0].set_ylabel("Inertia")
    axes[0].grid(True, alpha=0.3)
 
    axes[1].plot(metrics_df["k"], metrics_df["silhouette"], marker="o", color="darkorange")
    axes[1].set_title("Silhouette Score")
    axes[1].set_xlabel("Number of Clusters (k)")
    axes[1].set_ylabel("Silhouette Score")
    axes[1].grid(True, alpha=0.3)
 
    plt.tight_layout()
    return _save(fig, save_path)
 
 
# ── Cluster visualisation ─────────────────────────────────────────────────────
 
def plot_pca_clusters(
    X_pca: np.ndarray,
    labels: np.ndarray,
    segment_names: dict[int, str] | None = None,
    save_path: str | None = None,
) -> plt.Figure:
    """2-D PCA scatter coloured by cluster, optionally labelled by segment name."""
    fig, ax = plt.subplots(figsize=(9, 6))
    for lbl in sorted(set(labels)):
        mask = labels == lbl
        name = (segment_names or {}).get(lbl, f"Cluster {lbl}")
        ax.scatter(
            X_pca[mask, 0], X_pca[mask, 1],
            s=12, alpha=0.45, label=name,
            color=PALETTE[lbl % len(PALETTE)],
        )
    ax.set_title("Customer Segments (PCA 2-D Projection)")
    ax.set_xlabel("PC 1")
    ax.set_ylabel("PC 2")
    ax.legend(fontsize=8, markerscale=2)
    plt.tight_layout()
    return _save(fig, save_path)
 
 
def plot_cluster_radar(
    profile: pd.DataFrame,
    cols: list[str],
    segment_names: dict[int, str] | None = None,
    save_path: str | None = None,
) -> plt.Figure:
    """Spider / radar chart of cluster spend profiles (column-normalised)."""
    from math import pi
    N = len(cols)
    angles = [n / float(N) * 2 * pi for n in range(N)]
    angles += angles[:1]
 
    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
    ax.set_theta_offset(pi / 2)
    ax.set_theta_direction(-1)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(
        [c.replace("lifetime_spend_", "").replace("_", " ") for c in cols],
        size=8,
    )
 
    # Column-wise normalisation: each feature scaled 0-1 across all clusters
    norm = profile[cols].copy()
    for c in cols:
        rng = norm[c].max() - norm[c].min()
        norm[c] = (norm[c] - norm[c].min()) / (rng + 1e-9)
 
    for idx, row in norm.iterrows():
        values = row.tolist() + row.tolist()[:1]
        name = (segment_names or {}).get(idx, f"Cluster {idx}")
        ax.plot(angles, values, linewidth=2, label=name, color=PALETTE[idx % len(PALETTE)])
        ax.fill(angles, values, alpha=0.07, color=PALETTE[idx % len(PALETTE)])
 
    ax.legend(loc="upper right", bbox_to_anchor=(1.35, 1.1), fontsize=8)
    ax.set_title("Segment Spend Profile (column-normalised)", size=13, pad=20)
    plt.tight_layout()
    return _save(fig, save_path)
 
 
def plot_spend_heatmap(
    profile: pd.DataFrame,
    spend_cols: list[str],
    segment_names: dict[int, str] | None = None,
    save_path: str | None = None,
) -> plt.Figure:
    """
    Spend heatmap with column-wise normalisation.
 
    Column-wise normalisation (each category divided by its maximum across
    all clusters) allows fair comparisons: the colour shows which segment
    over-indexes on each category relative to others.  Raw EUR values are
    annotated in each cell.
    """
    data = profile[spend_cols].copy()
    data.columns = [c.replace("lifetime_spend_", "").replace("_", " ") for c in spend_cols]
 
    if segment_names:
        data.index = [segment_names.get(i, f"Cluster {i}") for i in data.index]
 
    # Column-wise normalisation: highlight which segment leads each category
    data_norm = data.div(data.max(axis=0), axis=1)
 
    fig, ax = plt.subplots(figsize=(14, max(4, len(profile) * 1.2)))
    sns.heatmap(
        data_norm,
        annot=data.round(0),
        fmt="g",
        cmap="YlOrRd",
        ax=ax,
        linewidths=0.5,
        cbar_kws={"label": "Relative spend (column-normalised)"},
    )
    ax.set_title("Average Lifetime Spend by Segment and Category (EUR)", pad=12)
    ax.set_ylabel("")
    plt.xticks(rotation=30, ha="right", fontsize=9)
    plt.yticks(rotation=0, fontsize=9)
    plt.tight_layout()
    return _save(fig, save_path)
 
 
def plot_feature_distributions(
    df: pd.DataFrame,
    feature: str,
    labels: np.ndarray,
    segment_names: dict[int, str] | None = None,
    save_path: str | None = None,
) -> plt.Figure:
    """KDE of *feature* split by cluster."""
    df = df.copy()
    df["cluster"] = labels
    fig, ax = plt.subplots(figsize=(9, 4))
    for lbl in sorted(df["cluster"].unique()):
        data = df.loc[df["cluster"] == lbl, feature].dropna()
        name = (segment_names or {}).get(lbl, f"Cluster {lbl}")
        data.plot.kde(ax=ax, label=name, color=PALETTE[lbl % len(PALETTE)])
    ax.set_title(f"Distribution of {feature.replace('_', ' ').title()} by Segment")
    ax.set_xlabel(feature.replace("_", " ").title())
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    return _save(fig, save_path)
 
 
# ── NEW: Revenue contribution ─────────────────────────────────────────────────
 
def plot_revenue_by_segment(
    df_eng: pd.DataFrame,
    labels: np.ndarray,
    segment_names: dict[int, str],
    save_path: str | None = None,
) -> plt.Figure:
    """
    Horizontal bar chart of estimated total lifetime revenue per segment.
 
    Revenue = sum of total_spend for all customers in that cluster.
    """
    df_eng = df_eng.copy()
    df_eng["cluster"] = labels
 
    revenue = (
        df_eng.groupby("cluster")["total_spend"]
        .sum()
        .div(1_000_000)
        .rename(index=segment_names)
        .sort_values(ascending=True)
    )
 
    colors = [PALETTE[i % len(PALETTE)] for i in range(len(revenue))]
    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.barh(revenue.index, revenue.values, color=colors, edgecolor="white", height=0.6)
 
    for bar, val in zip(bars, revenue.values):
        ax.text(
            bar.get_width() + revenue.max() * 0.01,
            bar.get_y() + bar.get_height() / 2,
            f"€{val:.1f}M",
            va="center",
            fontsize=9,
        )
 
    ax.set_xlabel("Estimated Total Lifetime Revenue (EUR millions)")
    ax.set_title("Revenue Contribution by Segment")
    ax.grid(True, axis="x", alpha=0.3)
    ax.spines[["top", "right"]].set_visible(False)
    plt.tight_layout()
    return _save(fig, save_path)
 
 
# ── NEW: Promotion sensitivity ────────────────────────────────────────────────
 
def plot_promo_sensitivity(
    df_eng: pd.DataFrame,
    labels: np.ndarray,
    segment_names: dict[int, str],
    save_path: str | None = None,
) -> plt.Figure:
    """
    Bar chart showing the mean fraction of basket purchased on promotion
    per segment, sorted descending.
    """
    df_eng = df_eng.copy()
    df_eng["cluster"] = labels
 
    promo = (
        df_eng.groupby("cluster")["percentage_of_products_bought_promotion"]
        .mean()
        .rename(index=segment_names)
        .sort_values(ascending=False)
    )
 
    colors = [PALETTE[i % len(PALETTE)] for i in range(len(promo))]
    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.bar(promo.index, promo.values * 100, color=colors, edgecolor="white", width=0.6)
 
    for bar, val in zip(bars, promo.values):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.5,
            f"{val * 100:.1f}%",
            ha="center",
            va="bottom",
            fontsize=9,
        )
 
    ax.set_ylabel("Mean % of Basket Bought on Promotion")
    ax.set_title("Promotion Sensitivity by Segment")
    ax.set_ylim(0, promo.max() * 130)
    ax.grid(True, axis="y", alpha=0.3)
    ax.spines[["top", "right"]].set_visible(False)
    plt.xticks(rotation=20, ha="right")
    plt.tight_layout()
    return _save(fig, save_path)
 
 
# ── NEW: Segment metrics grid ─────────────────────────────────────────────────
 
def plot_segment_metrics(
    df_eng: pd.DataFrame,
    labels: np.ndarray,
    segment_names: dict[int, str],
    save_path: str | None = None,
) -> plt.Figure:
    """
    2×2 grid comparing four key metrics across segments:
    average total spend, average children, average tenure, average store visits.
    """
    df_eng = df_eng.copy()
    df_eng["cluster"] = labels
 
    agg = (
        df_eng.groupby("cluster")
        .agg(
            avg_spend=("total_spend", "mean"),
            avg_children=("total_children", "mean"),
            avg_tenure=("tenure_years", "mean"),
            avg_stores=("distinct_stores_visited", "mean"),
        )
        .rename(index=segment_names)
    )
 
    metrics = [
        ("avg_spend", "Avg Lifetime Spend (EUR)", "steelblue"),
        ("avg_children", "Avg Children at Home", "darkorange"),
        ("avg_tenure", "Avg Customer Tenure (yrs)", "seagreen"),
        ("avg_stores", "Avg Distinct Stores Visited", "mediumpurple"),
    ]
 
    fig, axes = plt.subplots(2, 2, figsize=(13, 8))
    for ax, (col, title, color) in zip(axes.flat, metrics):
        series = agg[col].sort_values(ascending=False)
        bars = ax.barh(series.index, series.values, color=color, alpha=0.8, edgecolor="white")
        for bar, val in zip(bars, series.values):
            ax.text(
                bar.get_width() * 1.01,
                bar.get_y() + bar.get_height() / 2,
                f"{val:,.1f}",
                va="center",
                fontsize=8,
            )
        ax.set_title(title, fontsize=10, fontweight="bold")
        ax.grid(True, axis="x", alpha=0.3)
        ax.spines[["top", "right"]].set_visible(False)
        ax.tick_params(axis="y", labelsize=8)
 
    plt.suptitle("Key Metrics Across Segments", fontsize=13, fontweight="bold", y=1.01)
    plt.tight_layout()
    return _save(fig, save_path)