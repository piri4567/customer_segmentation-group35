"""
Customer Segmentation - Visualization Helpers
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np
import pandas as pd
import seaborn as sns


PALETTE = sns.color_palette("tab10")


def plot_elbow(metrics_df: pd.DataFrame, save_path: str = None):
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    axes[0].plot(metrics_df["k"], metrics_df["inertia"], marker="o", color="steelblue")
    axes[0].set_title("Elbow Method (Inertia)")
    axes[0].set_xlabel("Number of Clusters (k)")
    axes[0].set_ylabel("Inertia")

    axes[1].plot(metrics_df["k"], metrics_df["silhouette"], marker="o", color="darkorange")
    axes[1].set_title("Silhouette Score")
    axes[1].set_xlabel("Number of Clusters (k)")
    axes[1].set_ylabel("Silhouette Score")

    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=120, bbox_inches="tight")
    return fig


def plot_pca_clusters(X_pca: np.ndarray, labels: np.ndarray, save_path: str = None):
    fig, ax = plt.subplots(figsize=(9, 6))
    unique_labels = sorted(set(labels))
    for lbl in unique_labels:
        mask = labels == lbl
        ax.scatter(X_pca[mask, 0], X_pca[mask, 1], s=15, alpha=0.5,
                   label=f"Cluster {lbl}", color=PALETTE[lbl % len(PALETTE)])
    ax.set_title("Customer Clusters (PCA 2D Projection)")
    ax.set_xlabel("PC1")
    ax.set_ylabel("PC2")
    ax.legend()
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=120, bbox_inches="tight")
    return fig


def plot_cluster_radar(profile: pd.DataFrame, cols: list, save_path: str = None):
    """Radar / spider chart of cluster profiles on selected columns."""
    from math import pi
    cats = cols
    N = len(cats)
    angles = [n / float(N) * 2 * pi for n in range(N)]
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
    ax.set_theta_offset(pi / 2)
    ax.set_theta_direction(-1)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels([c.replace("lifetime_spend_", "").replace("_", " ") for c in cats], size=8)

    # Normalize each feature 0-1 for display
    norm = profile[cols].copy()
    for c in cols:
        rng = norm[c].max() - norm[c].min()
        norm[c] = (norm[c] - norm[c].min()) / (rng + 1e-9)

    for idx, row in norm.iterrows():
        values = row.tolist() + [row.tolist()[0]]
        ax.plot(angles, values, linewidth=2, label=f"Cluster {idx}", color=PALETTE[idx % len(PALETTE)])
        ax.fill(angles, values, alpha=0.08, color=PALETTE[idx % len(PALETTE)])

    ax.legend(loc="upper right", bbox_to_anchor=(1.3, 1.1))
    ax.set_title("Cluster Spend Profile (normalized)", size=13, pad=20)
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=120, bbox_inches="tight")
    return fig


def plot_feature_distributions(df: pd.DataFrame, feature: str, labels: np.ndarray, save_path: str = None):
    df = df.copy()
    df["cluster"] = labels
    fig, ax = plt.subplots(figsize=(9, 4))
    for lbl in sorted(df["cluster"].unique()):
        data = df.loc[df["cluster"] == lbl, feature].dropna()
        data.plot.kde(ax=ax, label=f"Cluster {lbl}", color=PALETTE[lbl % len(PALETTE)])
    ax.set_title(f"Distribution of {feature} by Cluster")
    ax.legend()
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=120, bbox_inches="tight")
    return fig


def plot_spend_heatmap(profile: pd.DataFrame, spend_cols: list, save_path: str = None):
    data = profile[spend_cols].copy()
    data.columns = [c.replace("lifetime_spend_", "").replace("_", " ") for c in spend_cols]
    # Normalize by row max for readability
    data_norm = data.div(data.max(axis=1), axis=0)
    fig, ax = plt.subplots(figsize=(12, max(4, len(profile) * 0.8)))
    sns.heatmap(data_norm, annot=data.round(0), fmt="g", cmap="YlOrRd", ax=ax, linewidths=0.5)
    ax.set_title("Spend Heatmap by Cluster (normalized, values = €)")
    ax.set_ylabel("Cluster")
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=120, bbox_inches="tight")
    return fig
