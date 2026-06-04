"""
Customer Segmentation - Association Rules Module
"""
import ast
import pandas as pd
from mlxtend.frequent_patterns import apriori, association_rules
from mlxtend.preprocessing import TransactionEncoder


def load_basket(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    df["items"] = df["list_of_goods"].apply(_safe_parse)
    return df


def _safe_parse(x):
    """Parse a stringified list of items."""
    try:
        parsed = ast.literal_eval(x)
        return [str(i).strip().lower() for i in parsed]
    except Exception:
        return []


def encode_transactions(transactions: list) -> pd.DataFrame:
    """One-hot encode transactions for mlxtend."""
    te = TransactionEncoder()
    te_array = te.fit_transform(transactions)
    return pd.DataFrame(te_array, columns=te.columns_)


def mine_rules(
    df_basket: pd.DataFrame,
    min_support: float = 0.01,
    min_confidence: float = 0.3,
    min_lift: float = 1.2,
    max_len: int = 3,
) -> pd.DataFrame:
    """Mine association rules from basket data."""
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

    rules = association_rules(frequent, metric="confidence", min_threshold=min_confidence)
    rules = rules[rules["lift"] >= min_lift].copy()
    rules = rules.sort_values("lift", ascending=False).reset_index(drop=True)

    # Stringify frozensets for display
    rules["antecedents_str"] = rules["antecedents"].apply(lambda x: ", ".join(sorted(x)))
    rules["consequents_str"] = rules["consequents"].apply(lambda x: ", ".join(sorted(x)))
    return rules


def rules_per_cluster(
    df_basket: pd.DataFrame,
    customer_cluster_map: pd.Series,
    min_support: float = 0.01,
    min_confidence: float = 0.3,
    min_lift: float = 1.2,
) -> dict:
    """Mine association rules for each cluster separately."""
    df_basket = df_basket.copy()
    df_basket["cluster"] = df_basket["customer_id"].map(customer_cluster_map)
    cluster_rules = {}
    for cluster_id, group in df_basket.groupby("cluster"):
        rules = mine_rules(group, min_support, min_confidence, min_lift)
        cluster_rules[int(cluster_id)] = rules
    return cluster_rules
