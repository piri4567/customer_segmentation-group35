"""
Customer Segmentation - Association Rules Module
Nova IMS · Machine Learning II · Data Science Degree
 
Responsibilities:
- Parse and encode basket transactions
- Mine frequent itemsets via Apriori
- Derive association rules per customer cluster
"""
import ast
import pandas as pd
from mlxtend.frequent_patterns import apriori, association_rules
from mlxtend.preprocessing import TransactionEncoder
 
 
# ── Loaders ───────────────────────────────────────────────────────────────────
 
def load_basket(path: str) -> pd.DataFrame:
    """Load customer_basket CSV and parse the list_of_goods column."""
    df = pd.read_csv(path)
    df["items"] = df["list_of_goods"].apply(_safe_parse)
    return df
 
 
# ── Parsing ───────────────────────────────────────────────────────────────────
 
def _safe_parse(x) -> list[str]:
    """Parse a stringified Python list of item names into a clean list."""
    try:
        parsed = ast.literal_eval(x)
        return [str(i).strip().lower() for i in parsed]
    except Exception:
        return []
 
 
# ── Encoding ──────────────────────────────────────────────────────────────────
 
def encode_transactions(transactions: list[list[str]]) -> pd.DataFrame:
    """One-hot encode a list of transaction item lists for use with mlxtend."""
    te = TransactionEncoder()
    te_array = te.fit_transform(transactions)
    return pd.DataFrame(te_array, columns=te.columns_)
 
 
# ── Rule mining ───────────────────────────────────────────────────────────────
 
def mine_rules(
    df_basket: pd.DataFrame,
    min_support: float = 0.01,
    min_confidence: float = 0.25,
    min_lift: float = 1.1,
    max_len: int = 3,
) -> pd.DataFrame:
    """
    Mine association rules from *df_basket*.
 
    Parameters
    ----------
    df_basket      : DataFrame with an 'items' column (list of strings per row)
    min_support    : Minimum itemset support threshold
    min_confidence : Minimum rule confidence threshold
    min_lift       : Minimum rule lift threshold
    max_len        : Maximum itemset length passed to Apriori
 
    Returns
    -------
    DataFrame of rules sorted by lift descending, with human-readable
    antecedents_str and consequents_str columns added.  Empty DataFrame
    if no rules pass the thresholds.
    """
    transactions = df_basket["items"].tolist()
    df_encoded = encode_transactions(transactions)
 
    frequent = apriori(
        df_encoded,
        min_support=min_support,
        use_colnames=True,
        max_len=max_len,
    )
    if frequent.empty:
        return pd.DataFrame()
 
    # num_itemsets is required by mlxtend >= 0.23
    rules = association_rules(
        frequent,
        metric="confidence",
        min_threshold=min_confidence,
        num_itemsets=len(frequent),
    )
    rules = rules[rules["lift"] >= min_lift].copy()
    rules = rules.sort_values("lift", ascending=False).reset_index(drop=True)
 
    rules["antecedents_str"] = rules["antecedents"].apply(lambda x: ", ".join(sorted(x)))
    rules["consequents_str"] = rules["consequents"].apply(lambda x: ", ".join(sorted(x)))
    return rules
 
 
def rules_per_cluster(
    df_basket: pd.DataFrame,
    customer_cluster_map: pd.Series,
    min_support: float = 0.01,
    min_confidence: float = 0.25,
    min_lift: float = 1.1,
    max_len: int = 3,
) -> dict[int, pd.DataFrame]:
    """
    Mine association rules separately for each customer cluster.
 
    Parameters
    ----------
    df_basket            : Basket DataFrame with 'customer_id' and 'items' columns
    customer_cluster_map : Series mapping customer_id → cluster integer
    Remaining kwargs are forwarded to mine_rules().
 
    Returns
    -------
    Dict mapping cluster_id (int) → rules DataFrame.
    """
    df_basket = df_basket.copy()
    df_basket["cluster"] = df_basket["customer_id"].map(customer_cluster_map)
 
    cluster_rules: dict[int, pd.DataFrame] = {}
    for cluster_id, group in df_basket.groupby("cluster"):
        rules = mine_rules(
            group,
            min_support=min_support,
            min_confidence=min_confidence,
            min_lift=min_lift,
            max_len=max_len,
        )
        cluster_rules[int(cluster_id)] = rules
 
    return cluster_rules