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

# ── page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Customer Segmentation",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded",
)

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

# ── colour tokens ─────────────────────────────────────────────────────────────
BG         = "#0d1117"
SURFACE    = "#161b22"
SURFACE2   = "#1c2330"
BORDER     = "#30363d"
TEXT       = "#e6edf3"
MUTED      = "#8b949e"
ACCENT     = "#58a6ff"

PERSONAS = {
    0: {
        "label":  "Tech-Savvy Singles",
        "color":  "#58a6ff",
        "bg":     "#0d2149",
        "stat":   "High electronics and gaming spend, fewest children, below-average tenure",
        "desc":   "These customers skew toward electronics and video games with almost no children at home. They are high value per visit but visit fewer stores. Tech launches, gaming bundles and upgrade programs resonate strongly with this group.",
        "campaigns": [
            ("Buy 1 Video Game, get 1 free",
             "Targets the above-average video-game spend and gaming affinity found in basket rules."),
            ("Buy AirPods and Bluetooth Headphones, get 20% off your next electronics purchase",
             "Reinforces the top basket association rule for this cluster."),
            ("Device trade-in: bring an old device, get 15% off a new one",
             "Drives repeat electronics purchases and builds stickiness."),
        ],
    },
    1: {
        "label":  "Budget-Conscious Multi-Store Shoppers",
        "color":  "#f78166",
        "bg":     "#3d1a1a",
        "stat":   "Lowest total spend, highest store variety, above-average promo usage",
        "desc":   "The most price-sensitive group. They actively seek out promotions and distribute their spend across the highest number of distinct stores. Offers that reward loyalty and reduce cross-shopping incentivize consolidation of spend.",
        "campaigns": [
            ("50% off the second basket item in the baby food category",
             "Addresses the household and essentials basket patterns in this cluster."),
            ("Buy 3 household products, earn EUR 5 off the bill",
             "Directly rewards the basket-consolidation behaviour we want to encourage."),
            ("Loyalty card double-points every Wednesday",
             "Creates a recurring anchor day that pulls price-sensitive shoppers back."),
        ],
    },
    2: {
        "label":  "Core Everyday Shoppers",
        "color":  "#3fb950",
        "bg":     "#0d2818",
        "stat":   "Largest segment (41%), strong groceries, broad product diversity",
        "desc":   "The backbone of the customer base. Moderate across every dimension, with grocery and fresh produce as clear anchors. Basket analysis shows strong vegetable and salad associations. Campaigns should deepen fresh-category loyalty and grow basket size.",
        "campaigns": [
            ("Get 20% off Fish when you also buy Meat",
             "Directly derived from the top meat-to-fish basket lift in this cluster."),
            ("Buy any 5 vegetables, receive salad dressing for free",
             "Reinforces the salad-vegetable association rule identified via Apriori."),
            ("Weekly fresh deals: 30% off selected vegetables every Friday",
             "Creates a habitual visit cadence around a predictable promotional event."),
        ],
    },
    3: {
        "label":  "High-Value Family Households",
        "color":  "#bc8cff",
        "bg":     "#22103d",
        "stat":   "Highest spend (EUR 42k avg), largest households, longest tenure",
        "desc":   "The most profitable and loyal segment. Large households, long relationships and spend spread across all categories. Retention-focused campaigns and VIP recognition programs have outsized impact here given the high lifetime value at stake.",
        "campaigns": [
            ("Family bundle: groceries, meat and fish at 15% off total basket",
             "Matches the multi-category basket composition typical of this cluster."),
            ("VIP loyalty tier: double cashback on all purchases above EUR 200",
             "Rewards and retains the customers who already spend the most."),
            ("Birthday month offer: 20% off any single category of your choice",
             "Personalised reward aligned with the broad category range this cluster buys."),
        ],
    },
    4: {
        "label":  "Pet and Home Essentials",
        "color":  "#ffa657",
        "bg":     "#2e1a00",
        "stat":   "Distinctive pet-food and hygiene spend, very low meat and fish",
        "desc":   "Defined by consistent pet-food and hygiene purchases. Basket rules reveal strong pet-food and household cleaning co-purchases. Subscription mechanics and category-specific bundles match their predictable, routine buying patterns.",
        "campaigns": [
            ("Buy 2 bags of pet food, get 1 free",
             "Directly targets the defining spend category of this cluster."),
            ("Spend EUR 50 in hygiene products, earn a free cleaning kit",
             "Addresses the hygiene basket association and increases category depth."),
            ("Subscribe and Save: 10% off recurring pet food orders",
             "Converts routine purchases into subscriptions, raising retention probability."),
        ],
    },
}

COLOR_MAP = {PERSONAS[i]["label"]: PERSONAS[i]["color"] for i in range(5)}

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:ital,wght@0,300;0,400;0,500;0,600;1,400&family=IBM+Plex+Mono:wght@400;500&display=swap');

/* ════════════════════════════════════════════
   BASE
════════════════════════════════════════════ */
html, body, [class*="css"] {{
    font-family: 'IBM Plex Sans', sans-serif !important;
}}

.stApp, [data-testid="stAppViewContainer"] {{
    background-color: {BG} !important;
}}
[data-testid="stHeader"] {{
    background-color: {BG} !important;
    border-bottom: 1px solid {BORDER} !important;
}}
.main .block-container {{
    padding: 2.5rem 2.75rem 5rem 2.75rem !important;
    max-width: 1380px;
}}
#MainMenu, footer {{ visibility: hidden; }}
.stDeployButton {{ display: none !important; }}

/* ════════════════════════════════════════════
   SIDEBAR
════════════════════════════════════════════ */
[data-testid="stSidebar"] {{
    background-color: {SURFACE} !important;
    border-right: 1px solid {BORDER} !important;
}}
[data-testid="stSidebar"] .block-container {{
    padding: 2rem 1.25rem !important;
}}

/* ════════════════════════════════════════════
   TYPOGRAPHY  —  strict scale
════════════════════════════════════════════ */
p, span, div, label {{ color: {TEXT} !important; }}
h1, h2, h3, h4 {{ color: {TEXT} !important; }}

/* ════════════════════════════════════════════
   METRIC CARDS
════════════════════════════════════════════ */
[data-testid="metric-container"] {{
    background: {SURFACE} !important;
    border: 1px solid {BORDER} !important;
    border-radius: 10px !important;
    padding: 1.1rem 1.3rem 1rem !important;
    transition: border-color 0.2s;
}}
[data-testid="metric-container"]:hover {{
    border-color: {ACCENT}55 !important;
}}
[data-testid="stMetricLabel"] > div {{
    color: {MUTED} !important;
    font-size: 0.68rem !important;
    text-transform: uppercase;
    letter-spacing: 0.09em;
    font-weight: 600;
}}
[data-testid="stMetricValue"] > div {{
    color: {TEXT} !important;
    font-size: 1.45rem !important;
    font-weight: 600 !important;
    letter-spacing: -0.01em;
    line-height: 1.2;
}}
[data-testid="stMetricDelta"] {{
    font-size: 0.72rem !important;
}}

/* ════════════════════════════════════════════
   SELECTBOX
════════════════════════════════════════════ */
[data-testid="stSelectbox"] {{ background: transparent; }}
[data-baseweb="select"] > div {{
    background-color: {SURFACE2} !important;
    border: 1px solid {BORDER} !important;
    border-radius: 7px !important;
    color: {TEXT} !important;
}}
[data-baseweb="select"] span {{ color: {TEXT} !important; }}
[data-baseweb="popover"] ul {{
    background-color: {SURFACE2} !important;
    border: 1px solid {BORDER} !important;
    border-radius: 7px !important;
}}
[data-baseweb="popover"] li:hover {{ background-color: {SURFACE} !important; }}

/* ════════════════════════════════════════════
   RADIO  (sidebar nav)
════════════════════════════════════════════ */
[data-testid="stRadio"] > div {{ gap: 0.15rem !important; }}
[data-testid="stRadio"] label {{
    padding: 0.48rem 0.8rem !important;
    border-radius: 6px !important;
    color: {MUTED} !important;
    font-size: 0.83rem !important;
    cursor: pointer;
    transition: background 0.15s, color 0.15s;
    display: block;
}}
[data-testid="stRadio"] label:hover {{
    background: {SURFACE2} !important;
    color: {TEXT} !important;
}}
[data-testid="stRadio"] [data-checked="true"] + div label,
[data-testid="stRadio"] label[data-selected="true"] {{
    color: {ACCENT} !important;
    background: {SURFACE2} !important;
    font-weight: 500 !important;
}}

/* ════════════════════════════════════════════
   BUTTONS
════════════════════════════════════════════ */
[data-testid="stButton"] > button {{
    background-color: {ACCENT} !important;
    color: #0d1117 !important;
    border: none !important;
    border-radius: 7px !important;
    font-weight: 600 !important;
    font-size: 0.83rem !important;
    padding: 0.5rem 1.3rem !important;
    letter-spacing: 0.01em;
    transition: opacity 0.15s;
}}
[data-testid="stButton"] > button:hover {{ opacity: 0.82 !important; }}
[data-testid="stDownloadButton"] > button {{
    background-color: transparent !important;
    color: {ACCENT} !important;
    border: 1px solid {ACCENT}88 !important;
    border-radius: 7px !important;
    font-size: 0.83rem !important;
    transition: border-color 0.15s;
}}
[data-testid="stDownloadButton"] > button:hover {{
    border-color: {ACCENT} !important;
}}

/* ════════════════════════════════════════════
   NUMBER INPUT
════════════════════════════════════════════ */
[data-baseweb="input"] {{
    background-color: {SURFACE2} !important;
    border: 1px solid {BORDER} !important;
    border-radius: 7px !important;
}}
[data-baseweb="input"] input {{
    color: {TEXT} !important;
    background-color: {SURFACE2} !important;
}}

/* ════════════════════════════════════════════
   DATAFRAME
════════════════════════════════════════════ */
[data-testid="stDataFrame"] {{
    border: 1px solid {BORDER} !important;
    border-radius: 8px !important;
    overflow: hidden;
}}

/* ════════════════════════════════════════════
   DIVIDER
════════════════════════════════════════════ */
hr {{
    border: none !important;
    border-top: 1px solid {BORDER} !important;
    margin: 2rem 0 !important;
}}

/* ════════════════════════════════════════════
   ALERTS
════════════════════════════════════════════ */
[data-testid="stAlert"] {{
    background-color: {SURFACE2} !important;
    border-left-color: {ACCENT} !important;
    border-radius: 0 7px 7px 0 !important;
}}
[data-testid="stAlert"] p {{ color: {TEXT} !important; }}

/* ════════════════════════════════════════════
   SPINNER
════════════════════════════════════════════ */
[data-testid="stSpinner"] p {{ color: {MUTED} !important; }}

/* ════════════════════════════════════════════
   PLOTLY CHART CONTAINERS
════════════════════════════════════════════ */
[data-testid="stPlotlyChart"] > div {{
    background: {SURFACE} !important;
    border: 1px solid {BORDER} !important;
    border-radius: 10px !important;
    padding: 0.25rem !important;
    overflow: hidden;
}}

[data-testid="column"] {{ padding: 0 0.3rem !important; }}
</style>
""", unsafe_allow_html=True)


# ── html helpers ──────────────────────────────────────────────────────────────

def page_header(title, subtitle=""):
    sub = (
        f'<p style="margin:0.4rem 0 0;font-size:0.85rem;color:{MUTED};'
        f'font-weight:400;letter-spacing:0">{subtitle}</p>'
    ) if subtitle else ""
    st.markdown(
        f'<div style="margin-bottom:2rem;padding-bottom:1.4rem;'
        f'border-bottom:1px solid {BORDER}">'
        f'<h1 style="margin:0;font-size:1.75rem;font-weight:600;color:{TEXT};'
        f'letter-spacing:-0.025em;line-height:1.15">{title}</h1>{sub}</div>',
        unsafe_allow_html=True,
    )


def subsection_header(title, subtitle=""):
    sub = (
        f'<p style="margin:0.25rem 0 0;font-size:0.8rem;color:{MUTED}">{subtitle}</p>'
    ) if subtitle else ""
    st.markdown(
        f'<div style="margin:2rem 0 1rem">'
        f'<p style="margin:0;font-size:1.05rem;font-weight:600;color:{TEXT};'
        f'letter-spacing:-0.01em">{title}</p>{sub}</div>',
        unsafe_allow_html=True,
    )


def section_label(text):
    st.markdown(
        f'<p style="margin:0 0 0.55rem;font-size:0.67rem;font-weight:700;'
        f'text-transform:uppercase;letter-spacing:0.1em;color:{MUTED}55;'
        f'border-left:2px solid {MUTED}44;padding-left:0.5rem">{text}</p>',
        unsafe_allow_html=True,
    )


def chart_card_open(label=""):
    label_html = (
        f'<p style="margin:0 0 0.9rem;font-size:0.67rem;font-weight:700;'
        f'text-transform:uppercase;letter-spacing:0.1em;color:{MUTED}88;'
        f'border-left:2px solid {MUTED}44;padding-left:0.5rem">{label}</p>'
    ) if label else ""
    st.markdown(
        f'<div style="background:{SURFACE};border:1px solid {BORDER};'
        f'border-radius:10px;padding:1.25rem 1.25rem 0.5rem;margin-bottom:0.15rem">'
        f'{label_html}',
        unsafe_allow_html=True,
    )


def chart_card_close():
    st.markdown('</div>', unsafe_allow_html=True)


def pill(label, color, bg):
    return (
        f'<span style="display:inline-block;background:{bg};color:{color};'
        f'border:1px solid {color}44;border-radius:4px;font-size:0.67rem;'
        f'font-weight:700;letter-spacing:0.07em;padding:0.2rem 0.6rem;'
        f'text-transform:uppercase;font-family:\'IBM Plex Mono\',monospace">{label}</span>'
    )


def segment_card_overview(cid, row, persona):
    color = persona["color"]
    n     = int(row["size"])
    pct   = float(row["pct"])
    spend = float(row["total_spend"])
    st.markdown(
        f'<div style="background:{SURFACE};border:1px solid {BORDER};'
        f'border-top:3px solid {color};border-radius:0 0 10px 10px;'
        f'padding:1.1rem 1.1rem 1.15rem;height:100%;transition:border-color 0.2s">'
        f'<p style="margin:0 0 0.25rem;font-size:0.82rem;font-weight:600;'
        f'color:{TEXT};line-height:1.3;letter-spacing:-0.005em">{persona["label"]}</p>'
        f'<p style="margin:0 0 1rem;font-size:0.69rem;color:{MUTED};line-height:1.45">'
        f'{persona["stat"]}</p>'
        f'<div style="display:flex;justify-content:space-between;align-items:flex-end">'
        f'<div>'
        f'<p style="margin:0;font-size:0.6rem;color:{MUTED};text-transform:uppercase;'
        f'letter-spacing:0.07em;font-weight:600">Customers</p>'
        f'<p style="margin:0;font-size:1.15rem;font-weight:600;color:{TEXT};'
        f'letter-spacing:-0.01em;line-height:1.2">{n:,}</p>'
        f'<p style="margin:0.1rem 0 0;font-size:0.67rem;color:{MUTED}">{pct:.0f}% of base</p>'
        f'</div>'
        f'<div style="text-align:right">'
        f'<p style="margin:0;font-size:0.6rem;color:{MUTED};text-transform:uppercase;'
        f'letter-spacing:0.07em;font-weight:600">Avg spend</p>'
        f'<p style="margin:0;font-size:1.15rem;font-weight:600;color:{color};'
        f'letter-spacing:-0.01em;line-height:1.2">EUR {spend:,.0f}</p>'
        f'</div></div></div>',
        unsafe_allow_html=True,
    )


def campaign_card(campaign, rationale, color, idx):
    st.markdown(
        f'<div style="background:{SURFACE};border:1px solid {BORDER};'
        f'border-left:3px solid {color};border-radius:0 8px 8px 0;'
        f'padding:0.9rem 1.1rem;margin-bottom:0.5rem">'
        f'<div style="display:flex;gap:0.75rem;align-items:flex-start">'
        f'<span style="font-family:\'IBM Plex Mono\',monospace;color:{color};'
        f'font-size:0.65rem;font-weight:700;min-width:1.3rem;padding-top:3px;'
        f'opacity:0.9">C{idx}</span>'
        f'<div>'
        f'<p style="margin:0 0 0.28rem;font-weight:500;font-size:0.86rem;'
        f'color:{TEXT};line-height:1.4">{campaign}</p>'
        f'<p style="margin:0;font-size:0.75rem;color:{MUTED};line-height:1.55">'
        f'{rationale}</p>'
        f'</div></div></div>',
        unsafe_allow_html=True,
    )


def rule_card(ant, cons, confidence, lift, color):
    bar = min(int(confidence * 100), 100)
    st.markdown(
        f'<div style="background:{SURFACE2};border:1px solid {BORDER};'
        f'border-left:3px solid {color};border-radius:0 6px 6px 0;'
        f'padding:0.8rem 1rem;margin-bottom:0.45rem">'
        f'<div style="display:flex;justify-content:space-between;align-items:center">'
        f'<span style="font-size:0.82rem;color:{TEXT};line-height:1.4">'
        f'<span style="color:{MUTED}">if </span>{ant}'
        f'<span style="color:{MUTED}"> then </span>{cons}</span>'
        f'<span style="font-family:\'IBM Plex Mono\',monospace;font-size:0.74rem;'
        f'color:{color};white-space:nowrap;margin-left:0.9rem;font-weight:500">'
        f'lift {lift:.2f}</span></div>'
        f'<div style="margin-top:0.5rem;background:{BORDER};border-radius:2px;height:2px">'
        f'<div style="width:{bar}%;background:{color};border-radius:2px;height:2px"></div></div>'
        f'<span style="font-size:0.66rem;color:{MUTED}44;font-family:\'IBM Plex Mono\',monospace">'
        f'conf {confidence:.1%}</span>'
        f'</div>',
        unsafe_allow_html=True,
    )


# ── plotly theme helper ───────────────────────────────────────────────────────
def theme(fig, height=None, **kw):
    layout = dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="IBM Plex Sans, sans-serif", color=TEXT, size=12),
        margin=dict(l=16, r=16, t=40, b=16),
    )
    if height:
        layout["height"] = height
    layout.update(kw)
    fig.update_layout(**layout)
    fig.update_xaxes(gridcolor=BORDER, zerolinecolor=BORDER, linecolor=BORDER)
    fig.update_yaxes(gridcolor=BORDER, zerolinecolor=BORDER, linecolor=BORDER)
    return fig


# ── data loading ──────────────────────────────────────────────────────────────
@st.cache_data(show_spinner="Loading data and building clusters...")
def load_all():
    df_info     = load_customer_info(os.path.join(DATA_DIR, "customer_info.csv"))
    X_scaled, feature_cols, _, scaler, df_eng = preprocess_for_clustering(df_info)
    km, labels  = fit_kmeans(X_scaled, n_clusters=5)
    X_pca, _    = reduce_pca(X_scaled)
    summary     = describe_clusters(df_eng, labels)
    profile     = cluster_profiles(df_eng, labels, feature_cols)
    spend_cols  = [c for c in feature_cols if c.startswith("lifetime_spend_")]
    metrics     = find_optimal_k(X_scaled, k_range=range(2, 10))
    return df_eng, labels, X_pca, summary, profile, spend_cols, feature_cols, metrics


@st.cache_data(show_spinner="Mining association rules per segment...")
def load_rules(_df_eng, _labels):
    df_basket = load_basket(os.path.join(DATA_DIR, "customer_basket.csv"))
    cmap      = pd.Series(_labels, index=_df_eng["customer_id"].values)
    return rules_per_cluster(df_basket, cmap, min_support=0.01, min_confidence=0.25, min_lift=1.1)


df_eng, labels, X_pca, summary, profile, spend_cols, feature_cols, metrics = load_all()

df_labeled           = df_eng.copy()
df_labeled["cluster"]= labels
df_labeled["Segment"]= [PERSONAS[l]["label"] for l in labels]


# ── sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        f'<p style="font-size:0.63rem;text-transform:uppercase;letter-spacing:0.1em;color:{MUTED};margin-bottom:0.2rem">Machine Learning II</p>'
        f'<p style="font-size:1rem;font-weight:600;color:{TEXT};margin:0 0 1.8rem">Customer Segmentation</p>',
        unsafe_allow_html=True,
    )
    section = st.radio(
        "nav",
        ["Overview", "Methodology", "Segment Explorer", "Campaigns", "Customer Lookup"],
        label_visibility="collapsed",
    )
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown(
        f'<div style="font-size:0.73rem;color:{MUTED};line-height:2">'
        f'33,038 customers<br>5 segments<br>K-Means + PCA<br>Apriori rules</div>',
        unsafe_allow_html=True,
    )


# ══════════════════════════════════════════════════════════════════════════════
# OVERVIEW
# ══════════════════════════════════════════════════════════════════════════════
if section == "Overview":
    page_header("Segment Overview",
                "Five customer groups identified via K-Means clustering on demographic and lifetime spend features.")

    cols = st.columns(5, gap="small")
    for cid, col in enumerate(cols):
        with col:
            segment_card_overview(cid, summary.loc[cid], PERSONAS[cid])

    st.markdown("<br>", unsafe_allow_html=True)

    subsection_header("Customer Distribution", "Each point is one customer projected onto 2 principal components.")
    left, right = st.columns([3, 2], gap="large")

    with left:
        chart_card_open("PCA 2D projection  —  colour = segment")
        df_plot = pd.DataFrame({
            "PC1": X_pca[:, 0],
            "PC2": X_pca[:, 1],
            "Segment": [PERSONAS[l]["label"] for l in labels],
            "Total Spend": df_eng["total_spend"].values.round(0),
            "Age": df_eng["age"].values,
        })
        fig = px.scatter(
            df_plot, x="PC1", y="PC2", color="Segment",
            color_discrete_map=COLOR_MAP,
            hover_data={"Total Spend": ":,.0f", "Age": True, "PC1": False, "PC2": False},
            opacity=0.5, height=420,
        )
        fig.update_traces(marker=dict(size=4))
        theme(fig, height=420,
              legend=dict(orientation="h", y=-0.14, x=0,
                          font=dict(size=11), bgcolor="rgba(0,0,0,0)"))
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        chart_card_close()

    with right:
        chart_card_open("Customers per segment")
        sizes = pd.DataFrame({
            "Segment": [PERSONAS[i]["label"] for i in range(5)],
            "Count":   [int(summary.loc[i, "size"]) for i in range(5)],
            "Color":   [PERSONAS[i]["color"] for i in range(5)],
        }).sort_values("Count", ascending=True)
        fig2 = go.Figure(go.Bar(
            y=sizes["Segment"], x=sizes["Count"], orientation="h",
            marker_color=sizes["Color"].tolist(), marker_line_width=0,
            text=[f"{v:,}" for v in sizes["Count"]],
            textposition="outside",
            textfont=dict(size=11, color=MUTED),
        ))
        theme(fig2, height=420,
              xaxis=dict(visible=False, gridcolor=BORDER),
              yaxis=dict(tickfont=dict(size=11), gridcolor="rgba(0,0,0,0)",
                         zerolinecolor=BORDER, linecolor=BORDER))
        st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})
        chart_card_close()

    subsection_header("Category Spend Heatmap", "Average lifetime spend per category (EUR). Darker = higher.")
    chart_card_open()
    heat = profile[spend_cols].copy()
    heat.index   = [PERSONAS[i]["label"] for i in heat.index]
    heat.columns = [c.replace("lifetime_spend_", "").replace("_", " ").title() for c in spend_cols]
    fig3 = px.imshow(
        heat, text_auto=".0f",
        color_continuous_scale=[[0, SURFACE2], [0.45, "#1e4d6e"], [1, ACCENT]],
        aspect="auto", height=280,
    )
    fig3.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="IBM Plex Sans, sans-serif", color=TEXT, size=12),
        margin=dict(l=16, r=16, t=16, b=16),
        coloraxis_colorbar=dict(thickness=10, tickfont=dict(size=10, color=MUTED)),
        xaxis=dict(side="top", tickfont=dict(size=11), gridcolor="rgba(0,0,0,0)",
                   linecolor=BORDER, zerolinecolor=BORDER),
        yaxis=dict(tickfont=dict(size=11), gridcolor="rgba(0,0,0,0)",
                   linecolor=BORDER, zerolinecolor=BORDER),
    )
    fig3.update_traces(textfont_size=11)
    st.plotly_chart(fig3, use_container_width=True, config={"displayModeBar": False})
    chart_card_close()


# ══════════════════════════════════════════════════════════════════════════════
# METHODOLOGY
# ══════════════════════════════════════════════════════════════════════════════
elif section == "Methodology":
    page_header("Methodology",
                "Exploratory data analysis, feature engineering and cluster selection.")

    subsection_header("Dataset at a Glance")
    m1, m2, m3, m4 = st.columns(4, gap="small")
    m1.metric("Customers",          f"{len(df_eng):,}")
    m2.metric("Features used",      str(len(feature_cols)))
    m3.metric("Avg missing values", f"{round(df_eng[feature_cols].isnull().mean().mean()*100,1)}%")
    m4.metric("Segments selected",  "5")

    subsection_header("Exploratory Analysis", "Spend patterns and demographic distribution across segments.")
    left, right = st.columns(2, gap="large")

    with left:
        chart_card_open("Spend by category  —  log scale")
        spend_long = (
            profile[spend_cols].reset_index()
            .melt(id_vars="cluster", var_name="category", value_name="spend")
        )
        spend_long["category"] = (spend_long["category"]
            .str.replace("lifetime_spend_", "")
            .str.replace("_", " ").str.title())
        spend_long["Segment"] = spend_long["cluster"].map(lambda i: PERSONAS[i]["label"])
        fig4 = px.box(
            spend_long, x="category", y="spend", color="Segment",
            color_discrete_map=COLOR_MAP, log_y=True, height=360,
            labels={"spend": "Avg Spend (EUR, log)", "category": ""},
        )
        theme(fig4, showlegend=False,
              xaxis=dict(tickangle=-35, tickfont=dict(size=10),
                         gridcolor=BORDER, zerolinecolor=BORDER, linecolor=BORDER),
              yaxis=dict(gridcolor=BORDER, zerolinecolor=BORDER, linecolor=BORDER))
        st.plotly_chart(fig4, use_container_width=True, config={"displayModeBar": False})
        chart_card_close()

    with right:
        chart_card_open("Age vs household size by segment")
        fig5 = px.scatter(
            df_labeled, x="age", y="total_children", color="Segment",
            color_discrete_map=COLOR_MAP, opacity=0.45, height=360,
            labels={"age": "Age", "total_children": "Total Children at Home"},
        )
        fig5.update_traces(marker=dict(size=4))
        theme(fig5,
              legend=dict(orientation="h", y=-0.22, font=dict(size=10),
                          bgcolor="rgba(0,0,0,0)"))
        st.plotly_chart(fig5, use_container_width=True, config={"displayModeBar": False})
        chart_card_close()

    subsection_header("Cluster Selection", "Elbow and silhouette analysis used to select k = 5.")
    chart_card_open()
    fig6 = make_subplots(rows=1, cols=2,
                         subplot_titles=["Inertia (Elbow)", "Silhouette Score"])
    fig6.add_trace(go.Scatter(
        x=metrics["k"], y=metrics["inertia"],
        mode="lines+markers", name="Inertia",
        marker=dict(size=7, color=ACCENT), line=dict(color=ACCENT, width=2)),
        row=1, col=1)
    fig6.add_trace(go.Scatter(
        x=metrics["k"], y=metrics["silhouette"],
        mode="lines+markers", name="Silhouette",
        marker=dict(size=7, color=PERSONAS[3]["color"]),
        line=dict(color=PERSONAS[3]["color"], width=2)),
        row=1, col=2)
    fig6.add_vline(x=5, line_dash="dot", line_color=PERSONAS[0]["color"], line_width=1.5)
    fig6.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="IBM Plex Sans, sans-serif", color=TEXT, size=12),
        margin=dict(l=16, r=16, t=40, b=16),
        height=300, showlegend=False,
    )
    fig6.update_xaxes(title_text="k", gridcolor=BORDER, linecolor=BORDER,
                      zerolinecolor=BORDER)
    fig6.update_yaxes(gridcolor=BORDER, linecolor=BORDER, zerolinecolor=BORDER)
    fig6.update_annotations(font_color=MUTED)
    st.plotly_chart(fig6, use_container_width=True, config={"displayModeBar": False})
    chart_card_close()

    st.markdown(
        f'<div style="background:{SURFACE};border:1px solid {BORDER};'
        f'border-left:3px solid {ACCENT};border-radius:0 8px 8px 0;'
        f'padding:1rem 1.2rem;margin-top:0.75rem">'
        f'<p style="margin:0 0 0.2rem;font-size:0.7rem;font-weight:700;color:{ACCENT};'
        f'text-transform:uppercase;letter-spacing:0.08em">Decision</p>'
        f'<p style="margin:0;font-size:0.83rem;color:{TEXT};line-height:1.75">'
        f'<strong style="color:{TEXT}">k = 5</strong> was selected as the optimal number of clusters. '
        f'The elbow curve shows diminishing inertia gains beyond k = 5, '
        f'and k = 5 achieves the highest silhouette score (0.187) in the tested range, '
        f'indicating the most compact and well-separated clusters. '
        f'Features were standardised with StandardScaler; missing values imputed by column median.</p></div>',
        unsafe_allow_html=True,
    )

    subsection_header("Promotion Sensitivity", "Fraction of basket purchased on promotion, broken down by segment.")
    chart_card_open()
    fig7 = px.box(
        df_labeled, x="Segment", y="percentage_of_products_bought_promotion",
        color="Segment", color_discrete_map=COLOR_MAP, points=False, height=320,
        labels={"percentage_of_products_bought_promotion": "Fraction of Basket on Promotion",
                "Segment": ""},
    )
    theme(fig7, showlegend=False,
          xaxis=dict(tickangle=-15, tickfont=dict(size=11),
                     gridcolor=BORDER, zerolinecolor=BORDER, linecolor=BORDER),
          yaxis=dict(gridcolor=BORDER, zerolinecolor=BORDER, linecolor=BORDER))
    st.plotly_chart(fig7, use_container_width=True, config={"displayModeBar": False})
    chart_card_close()


# ══════════════════════════════════════════════════════════════════════════════
# SEGMENT EXPLORER
# ══════════════════════════════════════════════════════════════════════════════
elif section == "Segment Explorer":
    page_header("Segment Explorer", "Deep-dive into a single segment's profile and behaviour.")

    selected = st.selectbox(
        "Select segment",
        options=list(range(5)),
        format_func=lambda i: PERSONAS[i]["label"],
    )
    p     = PERSONAS[selected]
    color = p["color"]
    row   = summary.loc[selected]

    st.markdown(
        f'<div style="background:{SURFACE};border:1px solid {BORDER};'
        f'border-left:4px solid {color};border-radius:0 10px 10px 0;'
        f'padding:1.2rem 1.5rem;margin:0.75rem 0 1.5rem">'
        f'{pill(p["label"], color, p["bg"])}'
        f'<p style="margin:0.65rem 0 0;font-size:0.88rem;color:{TEXT};line-height:1.7">{p["desc"]}</p>'
        f'<p style="margin:0.5rem 0 0;font-size:0.75rem;color:{MUTED};'
        f'padding-top:0.5rem;border-top:1px solid {BORDER}">{p["stat"]}</p>'
        f'</div>',
        unsafe_allow_html=True,
    )

    subsection_header("Key Metrics")
    k1, k2, k3, k4, k5, k6 = st.columns(6, gap="small")
    k1.metric("Customers",          f"{int(row['size']):,}",  f"{row['pct']:.1f}% of total")
    k2.metric("Avg Lifetime Spend", f"EUR {row['total_spend']:,.0f}")
    k3.metric("Avg Age",            f"{row['age']:.0f} yrs")
    k4.metric("Avg Children",       f"{row['total_children']:.1f}")
    k5.metric("Avg Tenure",         f"{row['tenure_years']:.1f} yrs")
    k6.metric("Avg Complaints",     f"{row['number_complaints']:.2f}")

    subsection_header("Spend Profile", "How this segment's category spend compares to the global average.")
    col_a, col_b = st.columns(2, gap="large")

    with col_a:
        chart_card_open("Spend breakdown vs global average")
        global_spend = profile[spend_cols].mean()
        seg_spend    = profile.loc[selected, spend_cols]
        cats = [c.replace("lifetime_spend_", "").replace("_", " ").title() for c in spend_cols]

        fig8 = go.Figure()
        fig8.add_trace(go.Bar(
            y=cats, x=global_spend.values, orientation="h",
            name="Global avg", marker_color=BORDER, marker_line_width=0,
        ))
        fig8.add_trace(go.Bar(
            y=cats, x=seg_spend.values, orientation="h",
            name=p["label"], marker_color=color, marker_line_width=0, opacity=0.88,
        ))
        theme(fig8, height=400, barmode="overlay",
              legend=dict(orientation="h", y=-0.14, bgcolor="rgba(0,0,0,0)",
                          font=dict(size=11)),
              xaxis=dict(title="Avg Spend (EUR)", gridcolor=BORDER,
                         zerolinecolor=BORDER, linecolor=BORDER),
              yaxis=dict(tickfont=dict(size=10), gridcolor=BORDER,
                         zerolinecolor=BORDER, linecolor=BORDER))
        st.plotly_chart(fig8, use_container_width=True, config={"displayModeBar": False})
        chart_card_close()

    with col_b:
        chart_card_open("Radar  —  this segment vs all others")
        norm = profile[spend_cols].copy()
        for c in spend_cols:
            rng = norm[c].max() - norm[c].min()
            norm[c] = (norm[c] - norm[c].min()) / (rng + 1e-9)
        cats_r = [c.replace("lifetime_spend_", "").replace("_", " ").title() for c in spend_cols]

        fig9 = go.Figure()
        for cid in range(5):
            vals = norm.loc[cid, spend_cols].tolist() + [norm.loc[cid, spend_cols].tolist()[0]]
            is_sel = cid == selected
            fig9.add_trace(go.Scatterpolar(
                r=vals, theta=cats_r + [cats_r[0]],
                name=PERSONAS[cid]["label"],
                opacity=1.0 if is_sel else 0.22,
                line=dict(width=2.5 if is_sel else 1, color=PERSONAS[cid]["color"]),
                fill="toself" if is_sel else "none",
                fillcolor="rgba(88,166,255,0.08)" if is_sel else "rgba(0,0,0,0)"))
        fig9.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="IBM Plex Sans, sans-serif", color=TEXT, size=12),
            margin=dict(l=16, r=16, t=40, b=16),
            height=420,
            polar=dict(
                bgcolor="rgba(0,0,0,0)",
                angularaxis=dict(tickfont=dict(size=10), linecolor=BORDER, gridcolor=BORDER),
                radialaxis=dict(visible=True, gridcolor=BORDER,
                                tickfont=dict(size=9), showticklabels=False),
            ),
            legend=dict(orientation="h", y=-0.12, font=dict(size=10),
                        bgcolor="rgba(0,0,0,0)"),
        )
        st.plotly_chart(fig9, use_container_width=True, config={"displayModeBar": False})
        chart_card_close()

    subsection_header("Feature Distributions", "Violin plots show shape, median and IQR across all segments.")
    feat_map = {
        "Total Lifetime Spend":      "total_spend",
        "Age":                       "age",
        "Tenure (years)":            "tenure_years",
        "Number of Complaints":      "number_complaints",
        "Promotion Sensitivity":     "percentage_of_products_bought_promotion",
        "Distinct Stores Visited":   "distinct_stores_visited",
    }
    feat_choice = st.selectbox("Feature", list(feat_map.keys()), label_visibility="collapsed")
    feat_col    = feat_map[feat_choice]

    chart_card_open()
    fig10 = px.violin(
        df_labeled, x="Segment", y=feat_col, color="Segment",
        color_discrete_map=COLOR_MAP, box=True, points=False, height=350,
        labels={feat_col: feat_choice, "Segment": ""},
    )
    theme(fig10, showlegend=False,
          xaxis=dict(tickangle=-15, tickfont=dict(size=11),
                     gridcolor=BORDER, zerolinecolor=BORDER, linecolor=BORDER),
          yaxis=dict(gridcolor=BORDER, zerolinecolor=BORDER, linecolor=BORDER))
    st.plotly_chart(fig10, use_container_width=True, config={"displayModeBar": False})
    chart_card_close()


# ══════════════════════════════════════════════════════════════════════════════
# CAMPAIGNS
# ══════════════════════════════════════════════════════════════════════════════
elif section == "Campaigns":
    page_header("Targeted Campaigns",
                "Promotions grounded in basket association rules, tailored per segment.")

    with st.spinner("Mining association rules..."):
        cluster_rules = load_rules(df_eng, labels)

    selected = st.selectbox(
        "Select segment",
        options=list(range(5)),
        format_func=lambda i: PERSONAS[i]["label"],
    )
    p     = PERSONAS[selected]
    color = p["color"]

    st.markdown(
        f'<div style="margin:0.4rem 0 1.4rem">{pill(p["label"], color, p["bg"])}</div>',
        unsafe_allow_html=True,
    )

    camp_col, rules_col = st.columns(2, gap="large")

    with camp_col:
        subsection_header("Recommended Campaigns")
        for i, (campaign, rationale) in enumerate(p["campaigns"], 1):
            campaign_card(campaign, rationale, color, i)

    with rules_col:
        subsection_header("Top Association Rules")
        rules = cluster_rules.get(selected, pd.DataFrame())
        if rules.empty:
            st.info("No significant rules found for this segment with current thresholds.")
        else:
            for _, r in rules.head(8).iterrows():
                rule_card(r["antecedents_str"], r["consequents_str"],
                          r["confidence"], r["lift"], color)

    if not rules.empty:
        subsection_header("Rule Map", "Each bubble is one rule. X = confidence, Y = lift, size = support.")
        chart_card_open()
        fig11 = px.scatter(
            rules.head(60), x="confidence", y="lift", size="support",
            color="lift",
            color_continuous_scale=[[0, "#30363d"], [0.5, "#3d7fc0"], [1, "#58a6ff"]],
            hover_data={"antecedents_str": True, "consequents_str": True,
                        "support": ":.4f", "confidence": ":.3f", "lift": ":.2f"},
            labels={"confidence": "Confidence", "lift": "Lift"},
            height=380,
        )
        theme(fig11,
              coloraxis_colorbar=dict(title="Lift", thickness=10,
                                      tickfont=dict(size=10, color=MUTED)))
        st.plotly_chart(fig11, use_container_width=True, config={"displayModeBar": False})
        chart_card_close()


# ══════════════════════════════════════════════════════════════════════════════
# CUSTOMER LOOKUP
# ══════════════════════════════════════════════════════════════════════════════
elif section == "Customer Lookup":
    page_header("Customer Lookup",
                "Retrieve the segment assignment and profile for any individual customer.")

    subsection_header("Search")
    id_col, _ = st.columns([1, 2])
    with id_col:
        section_label("Customer ID")
        customer_id = st.number_input(
            "Customer ID", label_visibility="collapsed",
            min_value=int(df_labeled["customer_id"].min()),
            max_value=int(df_labeled["customer_id"].max()),
            step=1,
        )
        lookup_btn = st.button("Look up customer")

    if lookup_btn:
        row = df_labeled[df_labeled["customer_id"] == customer_id]
        if row.empty:
            st.error("Customer not found in dataset.")
        else:
            r     = row.iloc[0]
            cid   = int(r["cluster"])
            p     = PERSONAS[cid]
            color = p["color"]

            subsection_header("Segment Assignment")
            st.markdown(
                f'<div style="background:{SURFACE};border:1px solid {BORDER};'
                f'border-left:4px solid {color};border-radius:0 10px 10px 0;'
                f'padding:1.2rem 1.5rem;margin:0 0 1.4rem">'
                f'{pill(p["label"], color, p["bg"])}'
                f'<p style="margin:0.65rem 0 0;font-size:0.87rem;color:{TEXT};line-height:1.7">'
                f'{p["desc"]}</p>'
                f'<p style="margin:0.5rem 0 0;font-size:0.74rem;color:{MUTED};'
                f'padding-top:0.5rem;border-top:1px solid {BORDER}">{p["stat"]}</p>'
                f'</div>',
                unsafe_allow_html=True,
            )
            subsection_header("Customer Metrics")
            k1, k2, k3, k4, k5 = st.columns(5, gap="small")
            k1.metric("Lifetime Spend", f"EUR {r['total_spend']:,.0f}")
            k2.metric("Age",            f"{r['age']:.0f} yrs")
            k3.metric("Tenure",         f"{r['tenure_years']:.0f} yrs")
            k4.metric("Children",       f"{r['total_children']:.0f}")
            k5.metric("Complaints",     f"{r['number_complaints']:.0f}")

            subsection_header("Recommended Promotions")
            for i, (campaign, rationale) in enumerate(p["campaigns"], 1):
                campaign_card(campaign, rationale, color, i)

    st.markdown("<hr>", unsafe_allow_html=True)
    subsection_header("Export")
    
    # Requirement: Deliver a csv file with each customer_id and its proposed cluster.
    assignment_df = df_labeled[["customer_id", "cluster"]].copy()
    csv = assignment_df.to_csv(index=False).encode('utf-8')
    
    st.download_button("Download customer_clusters.csv", csv,
                       "customer_clusters.csv", "text/csv")
    st.markdown(
        f'<p style="font-size:0.74rem;color:{MUTED};margin-top:0.4rem">'
        f'{len(assignment_df):,} customers — columns: customer_id, cluster</p>',
        unsafe_allow_html=True,
    )