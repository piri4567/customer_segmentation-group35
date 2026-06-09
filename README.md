# Customer Segmentation

**Machine Learning II - Nova IMS - Data Science Degree**

## Project Overview

This project performs unsupervised customer segmentation on 33,038 retail customers using K-Means clustering. The segmentation is enriched with basket association rules mined with Apriori, then translated into targeted marketing campaign recommendations through an interactive React dashboard.

The final deliverable is the interactive dashboard in `app/`.

## Customer Segments

| Segment | Customers | Share | Avg Lifetime Spend |
|---|---:|---:|---:|
| High-Value Families | 6,950 | 21.0% | EUR 42,723 |
| Core Everyday Shoppers | 13,451 | 40.7% | EUR 19,234 |
| Pet and Home Essentials | 6,976 | 21.1% | EUR 17,323 |
| Tech-Savvy Singles | 3,322 | 10.1% | EUR 23,744 |
| Budget-Conscious Shoppers | 2,339 | 7.1% | EUR 10,613 |

## Repository Structure

```text
customer_segmentation/
├── app/                          # Interactive React dashboard
│   ├── public/
│   │   ├── data/                 # CSV outputs used by the dashboard
│   │   └── images/               # Visualisations and campaign creatives
│   └── src/                      # React components, pages, and segment metadata
├── data/
│   ├── customer_info.csv          # Customer-level dataset
│   └── customer_basket.csv        # Basket transaction dataset
├── outputs/                       # Generated pipeline outputs
│   ├── customer_clusters.csv      # Customer-to-cluster assignments
│   ├── segment_mapping.csv        # Cluster-to-segment mapping
│   ├── cluster_summary.csv        # Mean feature values by cluster
│   ├── cluster_metrics.csv        # Inertia and silhouette scores
│   ├── rules_cluster_*.csv        # Association rules by cluster
│   └── *.png                      # Generated visualisations
├── src/
│   ├── preprocessing.py           # Data loading, cleaning, and feature engineering
│   ├── clustering.py              # K-Means, PCA, profiling, and segment labels
│   ├── association.py             # Apriori association-rule mining
│   └── visualization.py           # Plot generation helpers
├── run_pipeline.py                # End-to-end Python pipeline
├── requirements.txt               # Python dependencies
└── README.md
```

## Setup

### Python Pipeline

Requires Python 3.10 or higher.

Install the Python dependencies from the project root:

```bash
pip install -r requirements.txt
```

Run the full pipeline:

```bash
python run_pipeline.py
```

This loads the raw data, engineers features, fits K-Means with `k=5`, assigns segment labels, generates visualisations, mines association rules, and writes all outputs to `outputs/`.

### Interactive Dashboard

From the project root:

```bash
cd app
npm install
npm run dev
```

Then open the URL printed by Vite, usually:

```text
http://localhost:5173
```

To create a production build:

```bash
npm run build
npm run preview
```

## Methodology

| Step | Choice | Rationale |
|---|---|---|
| Feature engineering | Demographic, spend, tenure, promotion, and category-ratio features | Captures both customer profile and purchasing behaviour |
| Scaling | `StandardScaler` | K-Means is distance-based, so features must be comparable |
| Cluster model | K-Means | Interpretable and suitable for customer segmentation |
| Cluster count | `k=5` | Selected using elbow and silhouette analysis over `k=2..9` |
| Dimensionality reduction | PCA | Used for 2-D visualisation of clusters |
| Segment labelling | Feature-signature matching | Converts numeric clusters into business-readable personas |
| Basket analysis | Apriori association rules | Identifies product affinities within each segment |
| Dashboard | React + Vite + Tailwind + Recharts | Provides an interactive way to explore the segmentation results |

## Dashboard Sections

| Section | Description |
|---|---|
| Overview | Executive KPIs, segment split, revenue contribution, and strategic priorities |
| Segments | Detailed profile for each customer segment |
| Methodology | Clustering metrics, PCA visualisation, and modelling decisions |
| Visualisations | Interactive charts and generated figures from the pipeline |
| Campaigns | Segment-specific campaigns and association rules |

## Deliverables

| Deliverable | Description |
|---|---|
| `app/` | Interactive React dashboard, the main project deliverable |
| `outputs/customer_clusters.csv` | Final customer-to-segment assignment file |
| `outputs/cluster_summary.csv` | Segment-level feature summary |
| `outputs/rules_cluster_*.csv` | Association rules by segment |
| `src/*.py` | Modular Python source code for the ML pipeline |

## Notes

The dashboard is static and does not require a backend or database. It reads pre-generated CSVs and images from `app/public/data/` and `app/public/images/`.

If the Python pipeline is re-run, copy the refreshed files from `outputs/` into the app:

```bash
cp outputs/*.csv app/public/data/
cp outputs/*.png app/public/images/
```

On Windows PowerShell, use:

```powershell
Copy-Item outputs\*.csv app\public\data\ -Force
Copy-Item outputs\*.png app\public\images\ -Force
```

## Authors

- Leonardo Rodrigues Silva e Souza
- Jaime Abreu
- Afonso Fonseca
