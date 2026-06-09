"""
Pre-compute per-cluster histograms for the React app.

Reads:
    ../data/customer_info.csv
    ../outputs/customer_clusters.csv

Writes:
    public/data/histograms.json

Each metric is binned into a fixed number of buckets across the full dataset,
then each bucket gets counts per cluster. The output is tiny (~20–30 KB)
compared to shipping the 6.4 MB raw CSV to the client.

Run from the project root:
    python app/scripts/build_histograms.py
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
APP_DIR = ROOT / "app"
DATA_OUT = APP_DIR / "public" / "data" / "histograms.json"


def derive_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    # Mirror src/preprocessing.py
    dob = pd.to_datetime(df["customer_birthdate"], format="%m/%d/%Y %I:%M %p", errors="coerce")
    df["age"] = 2024 - dob.dt.year
    df["total_children"] = df["kids_home"].fillna(0) + df["teens_home"].fillna(0)

    spend_cols = [c for c in df.columns if c.startswith("lifetime_spend_")]
    df["total_spend"] = df[spend_cols].sum(axis=1)
    df["tenure_years"] = (2024 - df["year_first_transaction"].fillna(2020)).clip(lower=0)
    return df


METRICS = {
    "age": {"label": "Age", "unit": "y", "bins": 12, "clip": (18, 95)},
    "tenure_years": {"label": "Tenure (years)", "unit": "y", "bins": 10, "clip": (0, 25)},
    "total_children": {"label": "Children at home", "unit": "", "bins": 9, "clip": (0, 8)},
    "total_spend": {"label": "Lifetime total spend", "unit": "€", "bins": 12, "clip": (0, 80_000)},
    "distinct_stores_visited": {"label": "Distinct stores visited", "unit": "", "bins": 10, "clip": (0, 12)},
    "percentage_of_products_bought_promotion": {
        "label": "Share of basket on promotion",
        "unit": "%",
        "bins": 10,
        "clip": (0, 1),
        "scale": 100,
    },
}


def histogram_for(values: np.ndarray, clusters: np.ndarray, meta: dict, cluster_ids: list[int]) -> list[dict]:
    lo, hi = meta["clip"]
    n_bins = meta["bins"]
    edges = np.linspace(lo, hi, n_bins + 1)

    out = []
    for i in range(n_bins):
        left, right = edges[i], edges[i + 1]
        # Last bin includes the right edge
        mask = (values >= left) & (values < right) if i < n_bins - 1 else (values >= left) & (values <= right)

        scale = meta.get("scale", 1)
        bin_label = format_bin(left * scale, right * scale, meta["unit"])
        entry = {"bin": bin_label, "binStart": float(left * scale)}
        for cid in cluster_ids:
            entry[str(cid)] = int(((clusters == cid) & mask).sum())
        out.append(entry)
    return out


def format_bin(left: float, right: float, unit: str) -> str:
    def fmt(v: float) -> str:
        if v >= 1000:
            return f"{v / 1000:.0f}k"
        return f"{v:.0f}" if v == int(v) else f"{v:.1f}"
    if unit == "€":
        return f"€{fmt(left)}–{fmt(right)}"
    if unit == "%":
        return f"{fmt(left)}–{fmt(right)}%"
    if unit:
        return f"{fmt(left)}–{fmt(right)}{unit}"
    return f"{fmt(left)}–{fmt(right)}"


def main() -> int:
    info_path = ROOT / "data" / "customer_info.csv"
    clusters_path = ROOT / "outputs" / "customer_clusters.csv"

    if not info_path.exists():
        print(f"ERROR: {info_path} not found", file=sys.stderr)
        return 1
    if not clusters_path.exists():
        print(f"ERROR: {clusters_path} not found — run `python run_pipeline.py` first", file=sys.stderr)
        return 1

    print(f"Reading {info_path.relative_to(ROOT)} …")
    df_info = pd.read_csv(info_path)
    print(f"Reading {clusters_path.relative_to(ROOT)} …")
    df_clusters = pd.read_csv(clusters_path)

    print("Deriving features …")
    df_info = derive_features(df_info)

    merged = df_info.merge(df_clusters[["customer_id", "cluster"]], on="customer_id", how="inner")
    print(f"Merged: {len(merged):,} customers")

    cluster_ids = sorted(merged["cluster"].dropna().unique().astype(int).tolist())
    clusters_arr = merged["cluster"].values

    output: dict = {"clusters": cluster_ids, "metrics": {}}

    for col, meta in METRICS.items():
        if col not in merged.columns:
            print(f"  ⚠️  Skipping {col} — not in merged dataframe")
            continue
        values = merged[col].fillna(merged[col].median()).values.astype(float)
        hist = histogram_for(values, clusters_arr, meta, cluster_ids)
        output["metrics"][col] = {
            "label": meta["label"],
            "unit": meta["unit"],
            "bins": hist,
        }
        print(f"  ✓ {col:<45} {len(hist)} bins")

    DATA_OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(DATA_OUT, "w") as f:
        json.dump(output, f, separators=(",", ":"))

    size_kb = os.path.getsize(DATA_OUT) / 1024
    print(f"\nWrote {DATA_OUT.relative_to(ROOT)} ({size_kb:.1f} KB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
