"""
Customer Segmentation - Interactive Streamlit App
Run with: streamlit run app.py
"""
import os
import sys

import matplotlib
matplotlib.use("Agg")
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

sys.path.insert(0, os.path.dirname(__file__))
from src.preprocessing import load_customer_info, preprocess_for_clustering
from src.clustering import (
    find_optimal_k, fit_kmeans, reduce_pca,
    cluster_profiles, describe_clusters,
)
from src.association import load_basket, rules_per_cluster

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Customer Segmentation",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded",
)

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

# ---------------------------------------------------------------------------
# Design system
# ---------------------------------------------------------------------------
BG        = "#0d1117"
SURFACE   = "#161b22"
SURFACE2  = "#1c2330"
BORDER    = "#30363d"
TEXT      = "#e6edf3"
TEXT_MUTED= "#8b949e"
ACCENT    = "#58a6ff"

CLUSTER_PERSONAS = {
    0: {
        "label":  "Tech-Savvy Singles",
        "color":  "#58a6ff",
        "tag_bg": "#0d2149",
        "stats":  "High electronics + gaming spend, fewest children, below-average tenure",
        "description": (
            "These customers skew toward electronics and video games with almost no "
            "children at home. They are high value per visit but visit fewer stores. "
            "Tech launches, gaming bundles and upgrade programs resonate strongly "
            "with this group."
        ),
        "campaigns": [
            ("Buy 1 Video Game, get 1 free",          "Targets the above-average video-game spend and strong gaming affinity found in basket rules."),
            ("Buy AirPods and Bluetooth Headphones, receive 20% off your next electronics purchase", "Reinforces the top basket association rule for this cluster."),
            ("Device trade-in: bring an old device, get 15% off a new one",                          "Drives repeat electronics purchases and builds stickiness."),
        ],
    },
    1: {
        "label":  "Budget-Conscious Multi-Store Shoppers",
        "color":  "#f78166",
        "tag_bg": "#3d1a1a",
        "stats":  "Lowest total spend, highest store variety, above-average promo usage",
        "description": (
            "The most price-sensitive group. They actively seek out promotions and "
            "distribute their spend across the highest number of distinct stores of "
            "any cluster. Offers that reward loyalty and reduce cross-shopping "
            "incentivize consolidation of spend."
        ),
        "campaigns": [
            ("50% off the second basket item in the baby food category",    "Addresses the household and essentials basket patterns in this cluster."),
            ("Buy 3 household products, earn EUR 5 off the bill",           "Directly rewards the basket-consolidation behaviour we want to encourage."),
            ("Loyalty card double-points every Wednesday",                  "Creates a recurring anchor day that pulls price-sensitive shoppers back."),
        ],
    },
    2: {
        "label":  "Core Everyday Shoppers",
        "color":  "#3fb950",
        "tag_bg": "#0d2818",
        "stats":  "Largest segment (41%), strong groceries, broad product diversity",
        "description": (
            "The backbone of the customer base. Moderate across every dimension, "
            "with grocery and fresh produce as clear anchors. Basket analysis shows "
            "strong vegetable and salad associations. Campaigns should deepen "
            "fresh-category loyalty and grow basket size."
        ),
        "campaigns": [
            ("Get 20% off Fish when you also buy Meat",                      "Directly derived from the top meat-to-fish basket lift in this cluster."),
            ("Buy any 5 vegetables, receive salad dressing for free",        "Reinforces the salad-vegetable association rule identified via Apriori."),
            ("Weekly fresh deals: 30% off selected vegetables every Friday", "Creates habitual visit cadence around a predictable promotional event."),
        ],
    },
    3: {
        "label":  "High-Value Family Households",
        "color":  "#bc8cff",
        "tag_bg": "#22103d",
        "stats":  "Highest spend (EUR 42 k avg), largest households, longest tenure",
        "description": (
            "The most profitable and loyal segment. Large households, long "
            "relationships and spend spread across all categories. "
            "Retention-focused campaigns and VIP recognition programs have "
            "outsized impact here given the high lifetime value at stake."
        ),
        "campaigns": [
            ("Family bundle: groceries and meat and fish, 15% off total basket",       "Matches the multi-category basket composition typical of this cluster."),
            ("VIP loyalty tier: double cashback on all purchases above EUR 200",       "Rewards and retains the customers who already spend the most."),
            ("Birthday month offer: 20% off any single category of your choice",       "Personalised reward that aligns with the broad category range this cluster buys."),
        ],
    },
    4: {
        "label":  "Pet and Home Essentials",
        "color":  "#ffa657",
        "tag_bg": "#2e1a00",
        "stats":  "Distinctive pet-food and hygiene spend, very low meat and fish",
        "description": (
            "Defined by consistent pet-food and hygiene purchases. Basket rules "
            "reveal strong pet-food and household cleaning co-purchases. "
            "Subscription mechanics and category-specific bundles match their "
            "predictable, routine buying patterns."
        ),
        "campaigns": [
            ("Buy 2 bags of pet food, get 1 free",                             "Directly targets the defining spend category of this cluster."),
            ("Spend EUR 50 in hygiene products, earn a free cleaning kit",     "Addresses the hygiene basket association and increases category depth."),
            ("Subscribe and Save: 10% off recurring pet food orders",          "Converts routine purchases into subscriptions, raising retention probability."),
        ],
    },
}

COLOR_MAP = {CLUSTER_PERSONAS[i]["label"]: CLUSTER_PERSONAS[i]["color"] for i in range(5)}

PLOTLY_BASE = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="'IBM Plex Sans', 'DM Sans', sans-serif", color=TEXT, size=12),
    margin=dict(l=16, r=16, t=36, b=16),
)

# Axis defaults applied via update_xaxes / update_yaxes (avoids key conflicts)
AXIS_STYLE = dict(gridcolor=BORDER, zerolinecolor=BORDER, linecolor=BORDER)


def _apply_base(fig, height: int = None, **extra_layout):
    """Apply shared theme to any figure, then call update_xaxes/yaxes."""
    kw = dict(**PLOTLY_BASE)
    if height:
        kw["height"] = height
    kw.update(extra_layout)
    fig.update_layout(**kw)
    fig.update_xaxes(**AXIS_STYLE)
    fig.update_yaxes(**AXIS_STYLE)
    return fig

# ---------------------------------------------------------------------------
# CSS
# ---------------------------------------------------------------------------
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@300;400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap');

html, body, [class*="css"] {{
    font-family: 'IBM Plex Sans', sans-serif;
    background-color: {BG};
    color: {TEXT};
}}

/* Main container */
.main .block-container {{
    padding: 2rem 2.5rem 3rem 2.5rem;
    max-width: 1400px;
}}

/* Sidebar */
section[data-testid="stSidebar"] {{
    background-color: {SURFACE};
    border-right: 1px solid {BORDER};
}}
section[data-testid="stSidebar"] .block-container {{
    padding: 1.5rem 1rem;
}}

/* Hide default Streamlit chrome */
#MainMenu, footer, header {{ visibility: hidden; }}
.stDeployButton {{ display: none; }}

/* Typography */
h1 {{ font-size: 1.65rem !important; font-weight: 600 !important; letter-spacing: -0.02em; color: {TEXT} !important; }}
h2 {{ font-size: 1.1rem !important; font-weight: 500 !important; color: {TEXT} !important; letter-spacing: -0.01em; }}
h3 {{ font-size: 0.95rem !important; font-weight: 500 !important; color: {TEXT_MUTED} !important; text-transform: uppercase; letter-spacing: 0.06em; }}

/* Metric cards */
[data-testid="metric-container"] {{
    background: {SURFACE};
    border: 1px solid {BORDER};
    border-radius: 8px;
    padding: 1rem 1.2rem !important;
}}
[data-testid="stMetricLabel"] {{ color: {TEXT_MUTED} !important; font-size: 0.72rem !important; text-transform: uppercase; letter-spacing: 0.05em; }}
[data-testid="stMetricValue"] {{ color: {TEXT} !important; font-size: 1.45rem !important; font-weight: 600 !important; }}
[data-testid="stMetricDelta"] {{ font-size: 0.75rem !important; }}

/* Dividers */
hr {{ border-color: {BORDER} !important; margin: 1.5rem 0 !important; }}

/* Selectbox / inputs */
[data-testid="stSelectbox"] > div > div {{
    background: {SURFACE2};
    border: 1px solid {BORDER};
    border-radius: 6px;
    color: {TEXT};
}}
[data-baseweb="select"] span {{ color: {TEXT} !important; }}
[data-baseweb="popover"] {{ background: {SURFACE2} !important; border: 1px solid {BORDER} !important; }}

/* Buttons */
[data-testid="stButton"] > button {{
    background: {ACCENT};
    color: #0d1117;
    border: none;
    border-radius: 6px;
    font-weight: 600;
    font-size: 0.82rem;
    letter-spacing: 0.02em;
    padding: 0.5rem 1.2rem;
    transition: opacity 0.15s;
}}
[data-testid="stButton"] > button:hover {{ opacity: 0.85; }}

/* Download button */
[data-testid="stDownloadButton"] > button {{
    background: transparent;
    color: {ACCENT};
    border: 1px solid {ACCENT};
    border-radius: 6px;
    font-size: 0.82rem;
    font-weight: 500;
}}

/* Radio nav */
[data-testid="stRadio"] label {{
    font-size: 0.82rem !important;
    color: {TEXT_MUTED} !important;
    padding: 0.4rem 0.6rem;
    border-radius: 5px;
    display: block;
    cursor: pointer;
}}
[data-testid="stRadio"] label:hover {{ color: {TEXT} !important; background: {SURFACE2}; }}
[data-testid="stRadio"] [data-checked="true"] label {{ color: {ACCENT} !important; background: {SURFACE2}; }}

/* Dataframe */
[data-testid="stDataFrame"] {{ background: {SURFACE}; border: 1px solid {BORDER}; border-radius: 8px; }}
[data-testid="stDataFrame"] th {{ background: {SURFACE2} !important; color: {TEXT_MUTED} !important; font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.05em; }}
[data-testid="stDataFrame"] td {{ color: {TEXT} !important; font-size: 0.82rem; }}

/* Info / success banners - replace with custom below */
[data-testid="stAlert"] {{ border-radius: 6px; border-left-width: 3px; background: {SURFACE2} !important; }}

/* Number input */
[data-baseweb="input"] input {{
    background: {SURFACE2} !important;
    color: {TEXT} !important;
    border: 1px solid {BORDER} !important;
    border-radius: 6px;
}}

/* Spinner */
[data-testid="stSpinner"] {{ color: {ACCENT}; }}

/* Slider */
[data-baseweb="slider"] div {{ color: {TEXT} !important; }}
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# HTML helpers
# ---------------------------------------------------------------------------
def _card(content: str, border_color: str = BORDER, pad: str = "1.2rem 1.4rem") -> None:
    st.markdown(
        f'<div style="background:{SURFACE};border:1px solid {border_color};'
        f'border-radius:8px;padding:{pad};margin-bottom:0.75rem">{content}</div>',
        unsafe_allow_html=True,
    )


def _segment_pill(label: str, color: str, tag_bg: str) -> str:
    return (
        f'<span style="background:{tag_bg};color:{color};border:1px solid {color}33;'
        f'border-radius:4px;font-size:0.72rem;font-weight:600;'
        f'letter-spacing:0.05em;padding:0.2rem 0.55rem;text-transform:uppercase">'
        f'{label}</span>'
    )


def _section_header(title: str, subtitle: str = "") -> None:
    sub = f'<p style="color:{TEXT_MUTED};font-size:0.82rem;margin:0.25rem 0 0 0">{subtitle}</p>' if subtitle else ""
    st.markdown(
        f'<div style="margin-bottom:1.5rem">'
        f'<h1 style="margin:0">{title}</h1>{sub}'
        f'</div>',
        unsafe_allow_html=True,
    )


def _label(text: str) -> None:
    st.markdown(
        f'<p style="color:{TEXT_MUTED};font-size:0.72rem;text-transform:uppercase;'
        f'letter-spacing:0.06em;margin:0 0 0.4rem 0;font-weight:500">{text}</p>',
        unsafe_allow_html=True,
    )


def _rule_card(antecedent: str, consequent: str, confidence: float, lift: float, color: str) -> None:
    bar_w = min(int(confidence * 100), 100)
    st.markdown(
        f'<div style="background:{SURFACE2};border:1px solid {BORDER};border-left:3px solid {color};'
        f'border-radius:0 6px 6px 0;padding:0.85rem 1rem;margin-bottom:0.5rem">'
        f'<div style="display:flex;justify-content:space-between;align-items:center">'
        f'<span style="font-size:0.85rem;color:{TEXT}">'
        f'<span style="color:{TEXT_MUTED}">If: </span>{antecedent}'
        f' <span style="color:{TEXT_MUTED};margin:0 0.4rem">then</span>{consequent}</span>'
        f'<span style="font-family:\'IBM Plex Mono\',monospace;font-size:0.78rem;'
        f'color:{color};white-space:nowrap;margin-left:1rem">lift {lift:.2f}</span>'
        f'</div>'
        f'<div style="margin-top:0.5rem;background:{BORDER};border-radius:2px;height:3px">'
        f'<div style="width:{bar_w}%;background:{color};border-radius:2px;height:3px"></div>'
        f'</div>'
        f'<span style="font-size:0.7rem;color:{TEXT_MUTED}">confidence {confidence:.2%}</span>'
        f'</div>',
        unsafe_allow_html=True,
    )


def _campaign_card(campaign: str, rationale: str, color: str, idx: int) -> None:
    st.markdown(
        f'<div style="background:{SURFACE};border:1px solid {BORDER};'
        f'border-top:2px solid {color};border-radius:0 0 8px 8px;'
        f'padding:1rem 1.2rem;margin-bottom:0.6rem">'
        f'<div style="display:flex;gap:0.75rem;align-items:flex-start">'
        f'<span style="font-family:\'IBM Plex Mono\',monospace;color:{color};'
        f'font-size:0.7rem;font-weight:600;min-width:1.4rem;padding-top:1px">C{idx}</span>'
        f'<div>'
        f'<p style="margin:0 0 0.3rem 0;font-weight:500;font-size:0.88rem;color:{TEXT}">{campaign}</p>'
        f'<p style="margin:0;font-size:0.78rem;color:{TEXT_MUTED}">{rationale}</p>'
        f'</div></div></div>',
        unsafe_allow_html=True,
    )


def _cluster_overview_card(cid: int, row, persona: dict) -> None:
    color  = persona["color"]
    label  = persona["label"]
    stats  = persona["stats"]
    n      = int(row["size"])
    pct    = float(row["pct"])
    spend  = float(row["total_spend"])
    age    = float(row["age"])
    st.markdown(
        f'<div style="background:{SURFACE};border:1px solid {BORDER};'
        f'border-top:3px solid {color};border-radius:0 0 8px 8px;padding:1.1rem 1.2rem">'
        f'<p style="margin:0 0 0.6rem 0;font-weight:600;font-size:0.88rem;color:{TEXT}">{label}</p>'
        f'<p style="margin:0 0 0.8rem 0;font-size:0.74rem;color:{TEXT_MUTED};line-height:1.45">{stats}</p>'
        f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:0.4rem">'
        f'<div><p style="margin:0;font-size:0.68rem;color:{TEXT_MUTED};text-transform:uppercase;letter-spacing:0.04em">Customers</p>'
        f'<p style="margin:0;font-size:1.1rem;font-weight:600;color:{TEXT}">{n:,} <span style="font-size:0.72rem;color:{TEXT_MUTED}">({pct:.0f}%)</span></p></div>'
        f'<div><p style="margin:0;font-size:0.68rem;color:{TEXT_MUTED};text-transform:uppercase;letter-spacing:0.04em">Avg Lifetime Spend</p>'
        f'<p style="margin:0;font-size:1.1rem;font-weight:600;color:{color}">EUR {spend:,.0f}</p></div>'
        f'</div></div>',
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------
@st.cache_data(show_spinner="Loading data and building clusters...")
def load_all():
    df_info = load_customer_info(os.path.join(DATA_DIR, "customer_info.csv"))
    X_scaled, feature_cols, idx, scaler, df_eng = preprocess_for_clustering(df_info)
    km, labels = fit_kmeans(X_scaled, n_clusters=5)
    X_pca, pca  = reduce_pca(X_scaled)
    summary     = describe_clusters(df_eng, labels)
    profile     = cluster_profiles(df_eng, labels, feature_cols)
    spend_cols  = [c for c in feature_cols if c.startswith("lifetime_spend_")]
    metrics     = find_optimal_k(X_scaled, k_range=range(2, 10))
    return df_eng, labels, X_pca, summary, profile, spend_cols, feature_cols, metrics


@st.cache_data(show_spinner="Mining association rules per segment...")
def load_rules(_df_eng, _labels):
    df_basket = load_basket(os.path.join(DATA_DIR, "customer_basket.csv"))
    customer_cluster = pd.Series(_labels, index=_df_eng["customer_id"].values)
    return rules_per_cluster(
        df_basket, customer_cluster,
        min_support=0.01, min_confidence=0.25, min_lift=1.1,
    )


df_eng, labels, X_pca, summary, profile, spend_cols, feature_cols, metrics = load_all()

# Attach cluster labels to df_eng for distribution plots
df_eng_labeled = df_eng.copy()
df_eng_labeled["cluster"]       = labels
df_eng_labeled["Segment"]       = [CLUSTER_PERSONAS[l]["label"] for l in labels]
df_eng_labeled["segment_color"] = [CLUSTER_PERSONAS[l]["color"] for l in labels]


# ---------------------------------------------------------------------------
# Sidebar navigation
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown(
        f'<p style="font-size:0.65rem;text-transform:uppercase;letter-spacing:0.1em;'
        f'color:{TEXT_MUTED};margin-bottom:0.2rem">Machine Learning II</p>'
        f'<p style="font-size:1rem;font-weight:600;color:{TEXT};margin:0 0 1.5rem 0">'
        f'Customer Segmentation</p>',
        unsafe_allow_html=True,
    )
    section = st.radio(
        "Navigation",
        ["Overview", "Methodology", "Segment Explorer", "Campaigns", "Customer Lookup"],
        label_visibility="collapsed",
    )
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown(
        f'<p style="font-size:0.72rem;color:{TEXT_MUTED};line-height:1.6">'
        f'33,038 customers<br>5 segments identified<br>K-Means + PCA<br>'
        f'Apriori association rules</p>',
        unsafe_allow_html=True,
    )


# ===========================================================================
# OVERVIEW
# ===========================================================================
if section == "Overview":
    _section_header(
        "Segment Overview",
        "Five distinct customer groups identified via K-Means clustering on demographic and spend features.",
    )

    # Segment cards row
    cols = st.columns(5, gap="small")
    for cid, col in enumerate(cols):
        with col:
            _cluster_overview_card(cid, summary.loc[cid], CLUSTER_PERSONAS[cid])

    st.markdown("<br>", unsafe_allow_html=True)

    left, right = st.columns([3, 2], gap="large")

    with left:
        _label("Customer distribution  —  PCA 2D projection")
        df_plot = pd.DataFrame({
            "PC1": X_pca[:, 0],
            "PC2": X_pca[:, 1],
            "Segment": [CLUSTER_PERSONAS[l]["label"] for l in labels],
            "Total Spend": df_eng["total_spend"].values.round(0),
            "Age": df_eng["age"].values,
        })
        fig_pca = px.scatter(
            df_plot, x="PC1", y="PC2", color="Segment",
            color_discrete_map=COLOR_MAP,
            hover_data={"Total Spend": ":,.0f", "Age": True, "PC1": False, "PC2": False},
            opacity=0.55,
            height=440,
        )
        fig_pca.update_traces(marker=dict(size=4))
        _apply_base(fig_pca, height=440,
            legend=dict(orientation="h", y=-0.12, x=0,
                        font=dict(size=11), bgcolor="rgba(0,0,0,0)"),
        )
        st.plotly_chart(fig_pca, use_container_width=True, config={"displayModeBar": False})

    with right:
        _label("Segment size distribution")
        seg_sizes = pd.DataFrame({
            "Segment": [CLUSTER_PERSONAS[i]["label"] for i in range(5)],
            "Count":   [int(summary.loc[i, "size"]) for i in range(5)],
            "Color":   [CLUSTER_PERSONAS[i]["color"] for i in range(5)],
        }).sort_values("Count", ascending=True)
        fig_bar = go.Figure(go.Bar(
            y=seg_sizes["Segment"],
            x=seg_sizes["Count"],
            orientation="h",
            marker_color=seg_sizes["Color"],
            marker_line_width=0,
            text=[f"{v:,}" for v in seg_sizes["Count"]],
            textposition="outside",
            textfont=dict(size=11, color=TEXT_MUTED),
        ))
        _apply_base(fig_bar, height=440,
            xaxis=dict(visible=False),
            yaxis=dict(gridcolor="rgba(0,0,0,0)", tickfont=dict(size=11)),
        )
        st.plotly_chart(fig_bar, use_container_width=True, config={"displayModeBar": False})

    st.markdown("<hr>", unsafe_allow_html=True)

    # Spend heatmap
    _label("Average lifetime spend by category and segment  (EUR)")
    heat_data = profile[spend_cols].copy()
    heat_data.index = [CLUSTER_PERSONAS[i]["label"] for i in heat_data.index]
    heat_data.columns = [
        c.replace("lifetime_spend_", "").replace("_", " ").title() for c in spend_cols
    ]
    fig_heat = px.imshow(
        heat_data,
        text_auto=".0f",
        color_continuous_scale=[[0, SURFACE2], [0.4, "#1e4d6e"], [1, ACCENT]],
        aspect="auto",
        height=280,
    )
    fig_heat.update_layout(
        **PLOTLY_BASE,
        coloraxis_colorbar=dict(
            thickness=10, len=0.8,
            tickfont=dict(size=10, color=TEXT_MUTED),
        ),
    )
    fig_heat.update_xaxes(side="top", tickfont=dict(size=11), gridcolor="rgba(0,0,0,0)")
    fig_heat.update_yaxes(tickfont=dict(size=11), gridcolor="rgba(0,0,0,0)")
    fig_heat.update_traces(textfont_size=11)
    st.plotly_chart(fig_heat, use_container_width=True, config={"displayModeBar": False})


# ===========================================================================
# METHODOLOGY
# ===========================================================================
elif section == "Methodology":
    _section_header(
        "Methodology",
        "Exploratory data analysis, feature engineering and cluster selection.",
    )

    # Dataset stats
    _label("Dataset at a glance")
    total      = len(df_eng)
    n_features = len(feature_cols)
    miss_pct   = round(df_eng[feature_cols].isnull().mean().mean() * 100, 1)
    m1, m2, m3, m4 = st.columns(4, gap="small")
    m1.metric("Customers",            f"{total:,}")
    m2.metric("Features used",        str(n_features))
    m3.metric("Missing values (avg)", f"{miss_pct}%")
    m4.metric("Segments selected",    "5")

    st.markdown("<br>", unsafe_allow_html=True)

    left, right = st.columns(2, gap="large")

    with left:
        _label("Spend distribution by category  (log scale)")
        spend_long = (
            profile[spend_cols]
            .reset_index()
            .melt(id_vars="cluster", var_name="category", value_name="spend")
        )
        spend_long["category"] = spend_long["category"].str.replace("lifetime_spend_", "").str.replace("_", " ").str.title()
        spend_long["Segment"]  = spend_long["cluster"].map(lambda i: CLUSTER_PERSONAS[i]["label"])
        fig_violin = px.box(
            spend_long, x="category", y="spend", color="Segment",
            color_discrete_map=COLOR_MAP,
            log_y=True, height=370,
            labels={"spend": "Avg Spend (EUR, log)", "category": ""},
        )
        fig_violin.update_layout(**PLOTLY_BASE, showlegend=False)
        fig_violin.update_xaxes(tickangle=-35, tickfont=dict(size=10), **AXIS_STYLE)
        st.plotly_chart(fig_violin, use_container_width=True, config={"displayModeBar": False})

    with right:
        _label("Age and household size by segment")
        fig_scatter = px.scatter(
            df_eng_labeled, x="age", y="total_children",
            color="Segment", color_discrete_map=COLOR_MAP,
            opacity=0.45, height=370,
            labels={"age": "Age", "total_children": "Total Children at Home"},
        )
        fig_scatter.update_traces(marker=dict(size=4))
        _apply_base(fig_scatter,
            legend=dict(orientation="h", y=-0.2, font=dict(size=10), bgcolor="rgba(0,0,0,0)"),
        )
        st.plotly_chart(fig_scatter, use_container_width=True, config={"displayModeBar": False})

    st.markdown("<hr>", unsafe_allow_html=True)

    # Elbow + silhouette
    _label("Cluster selection  —  elbow and silhouette analysis")
    fig_sel = make_subplots(rows=1, cols=2, subplot_titles=["Inertia (Elbow)", "Silhouette Score"])
    fig_sel.add_trace(
        go.Scatter(x=metrics["k"], y=metrics["inertia"],
                   mode="lines+markers",
                   marker=dict(size=7, color=ACCENT),
                   line=dict(color=ACCENT, width=2)),
        row=1, col=1,
    )
    fig_sel.add_trace(
        go.Scatter(x=metrics["k"], y=metrics["silhouette"],
                   mode="lines+markers",
                   marker=dict(size=7, color=CLUSTER_PERSONAS[0]["color"]),
                   line=dict(color=CLUSTER_PERSONAS[0]["color"], width=2)),
        row=1, col=2,
    )
    # Vertical lines at k=5
    for col_idx in [1, 2]:
        fig_sel.add_vline(x=5, line_dash="dot", line_color=CLUSTER_PERSONAS[3]["color"],
                          line_width=1.5, row=1, col=col_idx)
    fig_sel.update_layout(
        **PLOTLY_BASE,
        height=300,
        showlegend=False,
        annotations=[
            dict(x=5, y=metrics.loc[metrics.k==5, "inertia"].values[0],
                 text="k=5 selected", showarrow=True, arrowhead=2,
                 arrowcolor=CLUSTER_PERSONAS[3]["color"],
                 font=dict(size=10, color=CLUSTER_PERSONAS[3]["color"]),
                 xref="x1", yref="y1", ax=40, ay=-30),
        ],
    )
    fig_sel.update_xaxes(title_text="k", gridcolor=BORDER, linecolor=BORDER, zerolinecolor=BORDER)
    fig_sel.update_yaxes(gridcolor=BORDER, linecolor=BORDER, zerolinecolor=BORDER)
    fig_sel.update_annotations(font_color=TEXT_MUTED)
    st.plotly_chart(fig_sel, use_container_width=True, config={"displayModeBar": False})

    _card(
        f'<p style="margin:0;font-size:0.82rem;color:{TEXT};line-height:1.7">'
        f'<strong style="color:{ACCENT}">k = 5 was selected</strong> as the optimal number of clusters. '
        f'The elbow curve shows a clear reduction in the rate of inertia improvement beyond k = 5, '
        f'and k = 5 achieves the highest silhouette score (0.187) across the tested range, '
        f'indicating the most compact and well-separated clusters. Features were standardised '
        f'with StandardScaler and missing values imputed using per-column medians before clustering.</p>',
        border_color=ACCENT,
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # Promotion sensitivity
    _label("Promotion sensitivity by segment")
    fig_promo = px.box(
        df_eng_labeled, x="Segment", y="percentage_of_products_bought_promotion",
        color="Segment", color_discrete_map=COLOR_MAP,
        points=False, height=320,
        labels={"percentage_of_products_bought_promotion": "% of Basket on Promotion", "Segment": ""},
    )
    fig_promo.update_layout(**PLOTLY_BASE, showlegend=False)
    fig_promo.update_xaxes(tickangle=-20, tickfont=dict(size=11), **AXIS_STYLE)
    fig_promo.update_yaxes(**AXIS_STYLE)
    st.plotly_chart(fig_promo, use_container_width=True, config={"displayModeBar": False})


# ===========================================================================
# SEGMENT EXPLORER
# ===========================================================================
elif section == "Segment Explorer":
    _section_header("Segment Explorer", "Deep-dive into a single segment's profile and behaviour.")

    selected = st.selectbox(
        "Select segment",
        options=list(range(5)),
        format_func=lambda i: CLUSTER_PERSONAS[i]["label"],
    )
    persona  = CLUSTER_PERSONAS[selected]
    color    = persona["color"]
    row      = summary.loc[selected]

    # Header card
    st.markdown(
        f'<div style="background:{SURFACE};border:1px solid {BORDER};'
        f'border-left:4px solid {color};border-radius:0 8px 8px 0;'
        f'padding:1.2rem 1.5rem;margin-bottom:1.5rem">'
        f'{_segment_pill(persona["label"], color, persona["tag_bg"])}'
        f'<p style="margin:0.6rem 0 0 0;font-size:0.88rem;color:{TEXT};line-height:1.65">'
        f'{persona["description"]}</p>'
        f'<p style="margin:0.5rem 0 0 0;font-size:0.78rem;color:{TEXT_MUTED}">{persona["stats"]}</p>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # KPI strip
    k1, k2, k3, k4, k5, k6 = st.columns(6, gap="small")
    k1.metric("Customers",         f"{int(row['size']):,}",   f"{row['pct']:.1f}% of total")
    k2.metric("Avg Lifetime Spend",f"EUR {row['total_spend']:,.0f}")
    k3.metric("Avg Age",           f"{row['age']:.0f} yrs")
    k4.metric("Avg Children",      f"{row['total_children']:.1f}")
    k5.metric("Avg Tenure",        f"{row['tenure_years']:.1f} yrs")
    k6.metric("Avg Complaints",    f"{row['number_complaints']:.2f}")

    st.markdown("<br>", unsafe_allow_html=True)

    col_a, col_b = st.columns(2, gap="large")

    with col_a:
        _label("Spend breakdown vs segment average")
        # This segment vs global mean
        global_spend = profile[spend_cols].mean()
        seg_spend    = profile.loc[selected, spend_cols]
        cats         = [c.replace("lifetime_spend_", "").replace("_", " ").title() for c in spend_cols]

        fig_bar = go.Figure()
        fig_bar.add_trace(go.Bar(
            y=cats, x=global_spend.values, orientation="h",
            name="Global avg", marker_color=BORDER, marker_line_width=0,
        ))
        fig_bar.add_trace(go.Bar(
            y=cats, x=seg_spend.values, orientation="h",
            name=persona["label"], marker_color=color,
            marker_line_width=0, opacity=0.85,
        ))
        _apply_base(fig_bar, height=400,
            barmode="overlay",
            legend=dict(orientation="h", y=-0.12, bgcolor="rgba(0,0,0,0)", font=dict(size=11)),
            xaxis=dict(title="Avg Spend (EUR)", gridcolor=BORDER, zerolinecolor=BORDER, linecolor=BORDER),
            yaxis=dict(tickfont=dict(size=10), gridcolor=BORDER, zerolinecolor=BORDER, linecolor=BORDER),
        )
        st.plotly_chart(fig_bar, use_container_width=True, config={"displayModeBar": False})

    with col_b:
        _label("Radar  —  this segment vs all others")
        norm = profile[spend_cols].copy()
        for c in spend_cols:
            rng = norm[c].max() - norm[c].min()
            norm[c] = (norm[c] - norm[c].min()) / (rng + 1e-9)

        categories = [c.replace("lifetime_spend_", "").replace("_", " ").title() for c in spend_cols]
        fig_radar = go.Figure()
        for cid in range(5):
            vals = norm.loc[cid, spend_cols].tolist()
            vals += [vals[0]]
            is_sel = cid == selected
            fig_radar.add_trace(go.Scatterpolar(
                r=vals, theta=categories + [categories[0]],
                name=CLUSTER_PERSONAS[cid]["label"],
                opacity=1.0 if is_sel else 0.25,
                line=dict(
                    width=2.5 if is_sel else 1,
                    color=CLUSTER_PERSONAS[cid]["color"],
                ),
                fill="toself" if is_sel else "none",
                fillcolor="rgba(88,166,255,0.08)" if is_sel else "rgba(0,0,0,0)"))
        fig_radar.update_layout(
            **PLOTLY_BASE,
            polar=dict(
                bgcolor="rgba(0,0,0,0)",
                angularaxis=dict(tickfont=dict(size=10), linecolor=BORDER, gridcolor=BORDER),
                radialaxis=dict(visible=True, gridcolor=BORDER, tickfont=dict(size=9), showticklabels=False),
            ),
            legend=dict(orientation="h", y=-0.12, font=dict(size=10), bgcolor="rgba(0,0,0,0)"),
            height=420,
        )
        st.plotly_chart(fig_radar, use_container_width=True, config={"displayModeBar": False})

    st.markdown("<hr>", unsafe_allow_html=True)

    # Distribution comparison
    _label("Distribution comparison across segments")
    feat_map = {
        "Total Lifetime Spend":        "total_spend",
        "Age":                         "age",
        "Tenure (years)":              "tenure_years",
        "Number of Complaints":        "number_complaints",
        "Promotion Sensitivity (%)":   "percentage_of_products_bought_promotion",
        "Distinct Stores Visited":     "distinct_stores_visited",
    }
    feat_choice = st.selectbox("Feature", list(feat_map.keys()), label_visibility="collapsed")
    feat_col    = feat_map[feat_choice]

    fig_violin = px.violin(
        df_eng_labeled, x="Segment", y=feat_col, color="Segment",
        color_discrete_map=COLOR_MAP, box=True, points=False,
        height=350,
        labels={feat_col: feat_choice, "Segment": ""},
    )
    fig_violin.update_layout(**PLOTLY_BASE, showlegend=False)
    fig_violin.update_xaxes(tickangle=-20, tickfont=dict(size=11), **AXIS_STYLE)
    fig_violin.update_yaxes(**AXIS_STYLE)
    st.plotly_chart(fig_violin, use_container_width=True, config={"displayModeBar": False})


# ===========================================================================
# CAMPAIGNS
# ===========================================================================
elif section == "Campaigns":
    _section_header(
        "Targeted Campaigns",
        "Promotions grounded in basket association rules, tailored per segment.",
    )

    with st.spinner("Mining association rules..."):
        cluster_rules = load_rules(df_eng, labels)

    selected = st.selectbox(
        "Select segment",
        options=list(range(5)),
        format_func=lambda i: CLUSTER_PERSONAS[i]["label"],
    )
    persona = CLUSTER_PERSONAS[selected]
    color   = persona["color"]

    st.markdown(
        f'<div style="margin:0.5rem 0 1.25rem 0">'
        f'{_segment_pill(persona["label"], color, persona["tag_bg"])}'
        f'</div>',
        unsafe_allow_html=True,
    )

    camp_col, rules_col = st.columns([1, 1], gap="large")

    with camp_col:
        _label("Recommended campaigns")
        for i, (campaign, rationale) in enumerate(persona["campaigns"], 1):
            _campaign_card(campaign, rationale, color, i)

    with rules_col:
        _label("Top basket association rules")
        rules = cluster_rules.get(selected, pd.DataFrame())
        if rules.empty:
            st.info("No significant rules found for this segment with current thresholds.")
        else:
            for _, r in rules.head(8).iterrows():
                _rule_card(r["antecedents_str"], r["consequents_str"],
                           r["confidence"], r["lift"], color)

    st.markdown("<hr>", unsafe_allow_html=True)

    # Rules scatter
    if not rules.empty:
        _label("Association rule map  —  confidence vs lift  (bubble size = support)")
        fig_rules = px.scatter(
            rules.head(60),
            x="confidence", y="lift",
            size="support",
            color="lift",
            color_continuous_scale=[
    [0, BORDER],
    [0.5, "rgba(88,166,255,0.53)"],
    [1, color]
],
            hover_data={
                "antecedents_str": True, "consequents_str": True,
                "support": ":.4f", "confidence": ":.3f", "lift": ":.2f",
            },
            labels={"confidence": "Confidence", "lift": "Lift"},
            height=380,
        )
        _apply_base(fig_rules,
            coloraxis_colorbar=dict(
                title="Lift", thickness=10,
                tickfont=dict(size=10, color=TEXT_MUTED),
            ),
        )
        st.plotly_chart(fig_rules, use_container_width=True, config={"displayModeBar": False})


# ===========================================================================
# CUSTOMER LOOKUP
# ===========================================================================
elif section == "Customer Lookup":
    _section_header("Customer Lookup", "Retrieve the segment assignment and profile for any individual customer.")

    id_col, _ = st.columns([1, 2])
    with id_col:
        _label("Customer ID")
        customer_id = st.number_input(
            "Customer ID", label_visibility="collapsed",
            min_value=int(df_eng_labeled["customer_id"].min()),
            max_value=int(df_eng_labeled["customer_id"].max()),
            step=1,
        )
        lookup_btn = st.button("Look up customer")

    if lookup_btn:
        row = df_eng_labeled[df_eng_labeled["customer_id"] == customer_id]
        if row.empty:
            st.error("Customer not found in dataset.")
        else:
            r        = row.iloc[0]
            cid      = int(r["cluster"])
            persona  = CLUSTER_PERSONAS[cid]
            color    = persona["color"]

            st.markdown(
                f'<div style="background:{SURFACE};border:1px solid {BORDER};'
                f'border-left:4px solid {color};border-radius:0 8px 8px 0;'
                f'padding:1.2rem 1.5rem;margin:1rem 0">'
                f'{_segment_pill(persona["label"], color, persona["tag_bg"])}'
                f'<p style="margin:0.6rem 0 0 0;font-size:0.85rem;color:{TEXT};line-height:1.65">'
                f'{persona["description"]}</p>'
                f'</div>',
                unsafe_allow_html=True,
            )

            k1, k2, k3, k4, k5 = st.columns(5, gap="small")
            k1.metric("Lifetime Spend",  f"EUR {r['total_spend']:,.0f}")
            k2.metric("Age",             f"{r['age']:.0f} yrs")
            k3.metric("Tenure",          f"{r['tenure_years']:.0f} yrs")
            k4.metric("Children",        f"{r['total_children']:.0f}")
            k5.metric("Complaints",      f"{r['number_complaints']:.0f}")

            st.markdown("<br>", unsafe_allow_html=True)
            _label("Recommended promotions")
            for i, (campaign, rationale) in enumerate(persona["campaigns"], 1):
                _campaign_card(campaign, rationale, color, i)

    st.markdown("<hr>", unsafe_allow_html=True)

    _label("Export full assignment file")
    assignment_df = df_eng_labeled[["customer_id", "cluster", "Segment"]].rename(
        columns={"Segment": "segment_label"}
    )
    csv = assignment_df.to_csv(index=False).encode()
    st.download_button(
        "Download customer_clusters.csv",
        csv, "customer_clusters.csv", "text/csv",
    )
    st.markdown(
        f'<p style="font-size:0.75rem;color:{TEXT_MUTED};margin-top:0.4rem">'
        f'{len(assignment_df):,} customers, 3 columns: customer_id, cluster (0-4), segment_label</p>',
        unsafe_allow_html=True,
    )
