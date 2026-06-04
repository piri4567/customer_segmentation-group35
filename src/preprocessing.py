"""
Customer Segmentation - Preprocessing Module
"""
import re
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler


def load_customer_info(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    return df


def extract_education(name: str) -> str:
    """Extract education level from customer name."""
    if pd.isna(name):
        return "Unknown"
    name_lower = name.lower()
    if "phd" in name_lower or "dr." in name_lower:
        return "PhD"
    if "msc" in name_lower or "mba" in name_lower or "master" in name_lower:
        return "Master"
    if "bsc" in name_lower or "ba." in name_lower or "bs." in name_lower:
        return "Bachelor"
    return "Other"


def parse_age(birthdate_series: pd.Series, reference_year: int = 2024) -> pd.Series:
    """Parse birthdate and compute age."""
    dob = pd.to_datetime(birthdate_series, format="%m/%d/%Y %I:%M %p", errors="coerce")
    age = reference_year - dob.dt.year
    return age


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """Feature engineering on customer_info."""
    df = df.copy()

    # Demographics
    df["age"] = parse_age(df["customer_birthdate"])
    df["education"] = df["customer_name"].apply(extract_education)
    df["total_children"] = df["kids_home"].fillna(0) + df["teens_home"].fillna(0)
    df["gender_encoded"] = (df["customer_gender"] == "male").astype(int)

    # Spend aggregates
    spend_cols = [c for c in df.columns if c.startswith("lifetime_spend_")]
    df["total_spend"] = df[spend_cols].sum(axis=1)

    # Spend ratios (avoid div-by-zero)
    for col in spend_cols:
        ratio_name = col.replace("lifetime_spend_", "ratio_")
        df[ratio_name] = df[col] / (df["total_spend"] + 1e-9)

    # Customer tenure
    df["tenure_years"] = 2024 - df["year_first_transaction"].fillna(2020)

    return df


def select_clustering_features(df: pd.DataFrame) -> list:
    """Return the list of numeric features used for clustering."""
    spend_cols = [c for c in df.columns if c.startswith("lifetime_spend_")]
    ratio_cols = [c for c in df.columns if c.startswith("ratio_")]
    base_features = [
        "age",
        "total_children",
        "number_complaints",
        "distinct_stores_visited",
        "lifetime_total_distinct_products",
        "percentage_of_products_bought_promotion",
        "tenure_years",
        "total_spend",
        "typical_hour",
    ]
    return base_features + spend_cols + ratio_cols


def preprocess_for_clustering(df: pd.DataFrame) -> tuple:
    """
    Returns (X_scaled, feature_names, valid_index).
    Drops rows where all spend is NaN.
    """
    df = engineer_features(df)
    feature_cols = select_clustering_features(df)

    # Keep only columns that exist
    feature_cols = [c for c in feature_cols if c in df.columns]

    X = df[feature_cols].copy()

    # Fill missing with median
    X = X.fillna(X.median())

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    return X_scaled, feature_cols, df.index, scaler, df
