"""
Customer Segmentation - Clustering Module
Nova IMS · Machine Learning II · Data Science Degree
 
Responsibilities:
- KMeans model selection (elbow + silhouette)
- Final KMeans fit
- PCA dimensionality reduction for visualisation
- Cluster profiling and summary statistics
- Robust cluster → segment name assignment
"""
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
 
# Use the same n_init throughout so that the elbow/silhouette curves that
# guide k selection are produced under identical conditions to the final model.
_N_INIT = 15
_RANDOM_STATE = 42
 
 
# ── Segment metadata ──────────────────────────────────────────────────────────
 
SEGMENT_DEFINITIONS = {
    "Tech-Savvy Singles": {
        "color_hex": "#4f8ef7",
        "description": (
            "These customers spend heavily on electronics and video games, have almost no children "
            "at home, and visit fewer stores than average. Despite lower visit frequency they are "
            "high-value per visit. Tech launch cycles, gaming bundles, and device upgrade programmes "
            "are the most effective levers for this group."
        ),
        "characteristics": [
            "Highest electronics and video-game lifetime spend of any segment",
            "Fewest children at home (average 0.6)",
            "Below-average store visit count — concentrated spend pattern",
            "Shorter customer tenure than average at 6.7 years",
        ],
        "campaigns": [
            (
                "Buy 1 Video Game, get 1 free",
                "Basket rules for this cluster show strong video game co-purchase patterns. "
                "A BOGOF offer directly targets the defining category and drives volume.",
            ),
            (
                "Buy AirPods and Bluetooth Headphones, get 20% off your next electronics purchase",
                "The top association rule links audio accessories. The follow-on discount reinforces "
                "this natural co-purchase and drives repeat electronics spend.",
            ),
            (
                "Device trade-in: bring an old device, get 15% off a new one",
                "Upgrade mechanics match this segment's propensity for tech purchases and build "
                "long-term stickiness.",
            ),
            (
                "Tech Tier Loyalty Programme — Bronze, Silver and Gold tiers based on annual electronics + gaming spend",
                "Each tier unlocks escalating benefits: early access to product launches, "
                "progressive discounts (5% / 10% / 15%) on tech purchases, and quarterly VIP "
                "preview events. The defining trait of this segment is concentrated high-value "
                "tech spending; a tiered programme converts that pattern into recurring, "
                "predictable loyalty without offering blanket discounts.",
            ),
        ],
    },
    "Budget-Conscious Shoppers": {
        "color_hex": "#f87171",
        "description": (
            "The most price-sensitive segment. They spread their spend across the highest number of "
            "distinct stores, indicating active cross-shopping behaviour. Above-average promotion usage "
            "signals strong price responsiveness. Loyalty mechanics that reward consolidation are the "
            "highest-impact strategy here."
        ),
        "characteristics": [
            "Lowest average lifetime spend at EUR 10,602",
            "Highest number of distinct stores visited — strongest cross-shopping signal",
            "Above-average promotional purchase rate",
            "Moderate household size (average 1.8 children)",
        ],
        "campaigns": [
            (
                "50% off the second basket item in the baby food and household category",
                "Basket analysis shows household and essentials dominance. A half-price second item "
                "drives quantity consolidation and rewards in-store spending.",
            ),
            (
                "Buy 3 household products, earn EUR 5 off your total bill",
                "Directly rewards basket consolidation, reducing the cross-shopping behaviour "
                "identified in this cluster.",
            ),
            (
                "Loyalty card double-points every Wednesday",
                "Creates a recurring anchor visit day. The price-sensitive profile of this group "
                "makes points rewards highly effective at building habitual visits.",
            ),
            (
                "Price Match Promise — match any competitor price within 7 days and earn an extra 10% in loyalty points",
                "These customers visit the highest number of distinct stores, signalling active "
                "competitor price-checking. A formal price-match policy with a points bonus reframes "
                "their cross-shopping behaviour into a reason to consolidate purchases with us. "
                "Standard practice in modern grocery retail (Aldi, Walmart, Tesco) and directly "
                "addresses the defining behaviour of the cluster.",
            ),
        ],
    },
    "Core Everyday Shoppers": {
        "color_hex": "#34c97a",
        "description": (
            "The backbone of the customer base at 41% of all customers. Grocery and fresh produce are "
            "the dominant categories, with broad product diversity. Spending and demographics are moderate "
            "across all dimensions. Incremental basket size growth through cross-category promotions "
            "represents the largest single revenue opportunity."
        ),
        "characteristics": [
            "Largest segment: 40.7% of the customer base",
            "Grocery and vegetables are dominant spend categories",
            "Broadest product diversity across all segments",
            "Youngest age profile at 49.3 years average",
        ],
        "campaigns": [
            (
                "Get 20% off Fish when you also buy Meat",
                "The top association rule for this cluster is a meat-to-fish co-purchase with strong "
                "lift. The discount formalises this natural buying behaviour.",
            ),
            (
                "Buy any 5 vegetables, receive salad dressing for free",
                "Vegetable basket rules show strong salad associations. A free accompaniment grows "
                "fresh-category engagement and basket size.",
            ),
            (
                "Weekly fresh deals: 30% off selected vegetables every Friday",
                "Creates habitual visit cadence and deepens loyalty to fresh produce — the category "
                "where this segment already over-indexes.",
            ),
            (
                "Recipe of the Week — every Monday a featured recipe with all ingredients automatically discounted at checkout when the full set is in the basket",
                "Combines the broad product diversity already characteristic of this segment with a "
                "concrete reason to grow basket size. The auto-discount at checkout (triggered by the "
                "complete ingredient set) is a proven mechanic used by Tesco UK and Carrefour. Builds "
                "a recurring weekly anchor without requiring active promotional browsing from the "
                "customer.",
            ),
        ],
    },
    "High-Value Families": {
        "color_hex": "#a78bfa",
        "description": (
            "The most profitable and loyal segment. Large households, the longest customer tenure, and "
            "spend spread across every category. Even modest churn reduction in this group has outsized "
            "revenue impact. VIP recognition and family-oriented bundle offers are the highest-return "
            "investment."
        ),
        "characteristics": [
            "Highest average lifetime spend: EUR 42,729 — 2.5x the portfolio average",
            "Largest household size (average 3.8 children)",
            "Longest customer tenure at 11.1 years — most loyal segment",
            "Spend distributed broadly across all categories",
        ],
        "campaigns": [
            (
                "Family bundle: groceries, meat and fish at 15% off total basket",
                "Multi-category basket composition is the defining trait of this cluster. A bundle "
                "reward matches their natural purchasing pattern and grows total basket value.",
            ),
            (
                "VIP loyalty tier: double cashback on all purchases above EUR 200",
                "The high average spend makes this segment the natural fit for a premium loyalty tier. "
                "Meaningful cashback reinforces loyalty at scale.",
            ),
            (
                "Birthday month offer: 20% off any single category of your choice",
                "A personalised milestone reward reinforces the emotional connection to the brand for "
                "the most profitable and longest-tenured customers.",
            ),
            (
                "Family Box monthly subscription — curated pre-assembled basket combining groceries, meat, fish and hygiene at 10% off the aggregate, delivered on a scheduled day",
                "These customers already buy broadly across categories every month. The Family Box "
                "consolidates that natural multi-category purchasing into a single recurring "
                "transaction, lowers acquisition cost (they would visit anyway), and adds a "
                "convenience dimension that matches the time-pressured profile of large households "
                "(average 3.8 children).",
            ),
        ],
    },
    "Pet and Home Essentials": {
        "color_hex": "#f59e0b",
        "description": (
            "Characterised by consistent, predictable pet-food and hygiene purchases with very low "
            "penetration in meat and fish. The regularity of their purchasing behaviour makes this "
            "segment ideal for subscription-based offers, which lock in repeat revenue and raise "
            "switching costs."
        ),
        "characteristics": [
            "Highest pet-food and hygiene spend ratio of any segment",
            "Very low meat and fish category penetration",
            "Highly predictable and routine purchasing patterns",
            "Lowest promotional purchase rate — not price-driven",
        ],
        "campaigns": [
            (
                "Buy 2 bags of pet food, get 1 free",
                "Pet food is the defining category of this cluster. A multi-buy offer directly "
                "incentivises the behaviour already observed in basket data.",
            ),
            (
                "Spend EUR 50 in hygiene products, earn a free cleaning kit",
                "Hygiene is the second defining category. A threshold reward increases average "
                "transaction value and deepens category loyalty.",
            ),
            (
                "Subscribe and Save: 10% off recurring pet food orders",
                "The predictable, routine purchase pattern of this segment makes subscription "
                "conversion straightforward and high-value for both parties.",
            ),
            (
                "Pantry Auto-Refill — customer-defined subscription across pet food and hygiene with selectable cadence (monthly or bimonthly), 10% off, priority delivery, and cancel anytime",
                "Extends the standard Subscribe and Save into a flexible bundle across the two "
                "defining categories of this cluster. Customer-chosen cadence respects their "
                "consumption rhythm rather than imposing a fixed schedule. Mirrors the Chewy and "
                "Amazon Subscribe and Save mechanics, both proven at scale for routine-purchase "
                "segments like this one.",
            ),
        ],
    },
}
 
 
# ── k selection ───────────────────────────────────────────────────────────────
 
def find_optimal_k(
    X_scaled: np.ndarray,
    k_range: range = range(2, 10),
    random_state: int = _RANDOM_STATE,
) -> pd.DataFrame:
    """
    Compute inertia and silhouette score for each k in *k_range*.
 
    Uses the same n_init as fit_kmeans() so curves reflect the actual model
    conditions rather than a weaker initialisation.
    """
    results = []
    for k in k_range:
        km = KMeans(n_clusters=k, random_state=random_state, n_init=_N_INIT)
        labels = km.fit_predict(X_scaled)
        sil = silhouette_score(
            X_scaled,
            labels,
            sample_size=min(5_000, len(labels)),
            random_state=random_state,
        )
        results.append({"k": k, "inertia": km.inertia_, "silhouette": sil})
    return pd.DataFrame(results)
 
 
# ── Fitting ───────────────────────────────────────────────────────────────────
 
def fit_kmeans(
    X_scaled: np.ndarray,
    n_clusters: int,
    random_state: int = _RANDOM_STATE,
) -> tuple[KMeans, np.ndarray]:
    """Fit KMeans and return *(model, labels)*."""
    km = KMeans(n_clusters=n_clusters, random_state=random_state, n_init=_N_INIT)
    labels = km.fit_predict(X_scaled)
    return km, labels
 
 
# ── PCA ───────────────────────────────────────────────────────────────────────
 
def reduce_pca(
    X_scaled: np.ndarray,
    n_components: int = 2,
    random_state: int = _RANDOM_STATE,
) -> tuple[np.ndarray, PCA]:
    """PCA reduction — returns *(X_pca, pca_model)*."""
    pca = PCA(n_components=n_components, random_state=random_state)
    return pca.fit_transform(X_scaled), pca
 
 
# ── Profiling ─────────────────────────────────────────────────────────────────
 
def cluster_profiles(
    df_eng: pd.DataFrame,
    labels: np.ndarray,
    feature_cols: list[str],
) -> pd.DataFrame:
    """Return mean feature values per cluster."""
    df_eng = df_eng.copy()
    df_eng["cluster"] = labels
    return df_eng.groupby("cluster")[feature_cols].mean().round(2)
 
 
def describe_clusters(df_eng: pd.DataFrame, labels: np.ndarray) -> pd.DataFrame:
    """Return a high-level summary table per cluster."""
    df_eng = df_eng.copy()
    df_eng["cluster"] = labels
 
    summary_cols = [
        "age", "total_spend", "total_children",
        "tenure_years", "number_complaints",
        "distinct_stores_visited",
        "percentage_of_products_bought_promotion",
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
 
 
# ── Cluster → segment mapping ─────────────────────────────────────────────────
 
def assign_segment_labels(
    df_eng: pd.DataFrame,
    labels: np.ndarray,
) -> dict[int, str]:
    """
    Map each integer cluster id to a named segment using feature-based heuristics.
 
    The approach is sequential and greedy — each persona is assigned to the
    cluster that best fits its defining signature, then that cluster is removed
    from consideration so no two personas share a label.
 
    Heuristics (in priority order):
        1. High-Value Families    → highest average total_spend
        2. Tech-Savvy Singles     → highest combined electronics + videogames spend
        3. Budget-Conscious       → highest distinct_stores_visited
        4. Pet and Home Essentials→ highest petfood + hygiene spend ratio (of remaining)
        5. Core Everyday Shoppers → the remaining cluster
    """
    df_eng = df_eng.copy()
    df_eng["_cluster"] = labels
 
    grp = df_eng.groupby("_cluster").agg(
        avg_spend=("total_spend", "mean"),
        avg_electronics=("lifetime_spend_electronics", "mean"),
        avg_videogames=("lifetime_spend_videogames", "mean"),
        avg_stores=("distinct_stores_visited", "mean"),
        avg_petfood=("lifetime_spend_petfood", "mean"),
        avg_hygiene=("lifetime_spend_hygiene", "mean"),
        avg_total=("total_spend", "mean"),
    )
 
    remaining = set(grp.index.tolist())
    label_map: dict[int, str] = {}
 
    def _pick(series: pd.Series, maximize: bool = True) -> int:
        sub = series[series.index.isin(remaining)]
        return int(sub.idxmax() if maximize else sub.idxmin())
 
    # 1. High-Value Families — highest total spend
    c = _pick(grp["avg_spend"])
    label_map[c] = "High-Value Families"
    remaining.discard(c)
 
    # 2. Tech-Savvy Singles — highest electronics + videogames
    tech_score = grp["avg_electronics"] + grp["avg_videogames"]
    c = _pick(tech_score)
    label_map[c] = "Tech-Savvy Singles"
    remaining.discard(c)
 
    # 3. Budget-Conscious — most distinct stores visited
    c = _pick(grp["avg_stores"])
    label_map[c] = "Budget-Conscious Shoppers"
    remaining.discard(c)
 
    # 4. Pet and Home Essentials — highest petfood + hygiene normalised by total spend
    pet_score = (grp["avg_petfood"] + grp["avg_hygiene"]) / (grp["avg_total"] + 1e-9)
    c = _pick(pet_score)
    label_map[c] = "Pet and Home Essentials"
    remaining.discard(c)
 
    # 5. Core Everyday Shoppers — the one that is left
    label_map[remaining.pop()] = "Core Everyday Shoppers"
 
    return label_map