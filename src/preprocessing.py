"""
Customer Segmentation - Preprocessing Module
Nova IMS · Machine Learning II · Data Science Degree
 
Responsibilities:
- Load raw CSVs
- Engineer demographic and spend features
- Scale features for clustering
"""
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
 
 
# ── Loaders ───────────────────────────────────────────────────────────────────
 
def load_customer_info(path: str) -> pd.DataFrame:
    """Load customer_info CSV from *path*."""
    return pd.read_csv(path)
 
 
# ── Feature helpers ───────────────────────────────────────────────────────────
 
def _parse_age(birthdate_series: pd.Series, reference_year: int = 2024) -> pd.Series:
    """Convert birthdate strings to integer ages relative to *reference_year*."""
    dob = pd.to_datetime(birthdate_series, format="%m/%d/%Y %I:%M %p", errors="coerce")
    return reference_year - dob.dt.year
 
 
def _extract_education(name: str) -> str:
    """Extract education level prefix from customer name string."""
    if pd.isna(name):
        return "Unknown"
    name_lower = name.lower()
    if "phd" in name_lower:
        return "PhD"
    if "msc" in name_lower or "mba" in name_lower:
        return "Master"
    if "bsc" in name_lower:
        return "Bachelor"
    return "Other"
 
 
# ── Engineering ───────────────────────────────────────────────────────────────
 
def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add derived columns to *df* and return the result.
 
    Columns added:
        age, total_children, total_spend,
        tenure_years (clamped ≥ 0),
        ratio_<category> for each lifetime_spend_<category> column,
        education (ordinal), gender_encoded (binary int)
    """
    df = df.copy()
 
    # Demographics
    df["age"] = _parse_age(df["customer_birthdate"])
    df["total_children"] = df["kids_home"].fillna(0) + df["teens_home"].fillna(0)
    df["gender_encoded"] = (df["customer_gender"] == "male").astype(int)
    df["education"] = df["customer_name"].apply(_extract_education)
 
    # Spend aggregates
    spend_cols = [c for c in df.columns if c.startswith("lifetime_spend_")]
    df["total_spend"] = df[spend_cols].sum(axis=1)
 
    # Category spend ratios (robust to zero total spend)
    for col in spend_cols:
        ratio_name = col.replace("lifetime_spend_", "ratio_")
        df[ratio_name] = df[col] / (df["total_spend"] + 1e-9)
 
    # Tenure — clamp at 0 to handle future-dated year_first_transaction values
    df["tenure_years"] = (2024 - df["year_first_transaction"].fillna(2020)).clip(lower=0)
 
    return df
 
 
# ── Feature selection ─────────────────────────────────────────────────────────
 
def select_clustering_features(df: pd.DataFrame) -> list[str]:
    """
    Return the list of numeric feature column names used for clustering.
 
    Includes base behavioural/demographic features, all lifetime spend columns,
    and all spend ratio columns.  Engineered columns that exist in *df* are
    included automatically so the list stays consistent with engineer_features().
    """
    spend_cols = [c for c in df.columns if c.startswith("lifetime_spend_")]
    ratio_cols = [c for c in df.columns if c.startswith("ratio_")]
 
    base_features = [
        "age",
        "gender_encoded",
        "total_children",
        "number_complaints",
        "distinct_stores_visited",
        "lifetime_total_distinct_products",
        "percentage_of_products_bought_promotion",
        "tenure_years",
        "total_spend",
        "typical_hour",
    ]
 
    all_features = base_features + spend_cols + ratio_cols
    # Keep only columns that are actually present after engineering
    return [c for c in all_features if c in df.columns]
 
 
# ── Pipeline entry point ──────────────────────────────────────────────────────
 
def preprocess_for_clustering(df: pd.DataFrame) -> tuple:
    """
    Full preprocessing pipeline.
 
    Returns
    -------
    X_scaled      : np.ndarray, shape (n_customers, n_features)
    feature_cols  : list[str]
    scaler        : fitted StandardScaler
    df_engineered : pd.DataFrame with all engineered columns
    """
    df_eng = engineer_features(df)
    feature_cols = select_clustering_features(df_eng)
 
    X = df_eng[feature_cols].fillna(df_eng[feature_cols].median())
 
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
 
    return X_scaled, feature_cols, scaler, df_eng