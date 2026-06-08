import ImageViewer from "../components/ImageViewer";

const GROUPS = [
  {
    title: "Segment portrait",
    items: [
      {
        src: "/images/spend_heatmap.png",
        alt: "Spend heatmap",
        caption:
          "Average lifetime spend per category and segment. Reveals the defining category for each cluster.",
      },
      {
        src: "/images/radar_chart.png",
        alt: "Radar chart",
        caption:
          "Normalised category profile per segment (radar). Each axis = one product category; each polygon = one segment.",
      },
      {
        src: "/images/fig_revenue.png",
        alt: "Revenue contribution by segment",
        caption:
          "Estimated total lifetime revenue attributed to each segment (€ millions).",
      },
      {
        src: "/images/fig_seg_metrics.png",
        alt: "Key demographic and spend metrics per segment",
        caption: "Key demographic and spend metrics across segments.",
      },
    ],
  },
  {
    title: "Promotion and price sensitivity",
    items: [
      {
        src: "/images/fig_promo_sensitivity.png",
        alt: "Promotion sensitivity by segment",
        caption:
          "Fraction of basket purchased on promotion by segment. Budget-Conscious and Core Everyday are the most promotion-responsive.",
      },
      {
        src: "/images/dist_percentage_of_products_bought_promotion.png",
        alt: "Distribution of promotion ratio per cluster",
        caption: "Full distribution of promotion-purchase share per cluster.",
      },
    ],
  },
  {
    title: "Demographic and behavioural distributions",
    items: [
      {
        src: "/images/dist_age.png",
        alt: "Age distribution per cluster",
        caption: "Customer age distribution per cluster.",
      },
      {
        src: "/images/dist_tenure_years.png",
        alt: "Tenure distribution per cluster",
        caption: "Customer tenure (years) distribution per cluster.",
      },
      {
        src: "/images/dist_total_children.png",
        alt: "Total children distribution per cluster",
        caption: "Total children at home per cluster.",
      },
      {
        src: "/images/dist_total_spend.png",
        alt: "Total spend distribution per cluster",
        caption: "Lifetime total spend distribution per cluster.",
      },
      {
        src: "/images/dist_distinct_stores_visited.png",
        alt: "Distinct stores visited per cluster",
        caption: "Distinct stores visited per cluster.",
      },
    ],
  },
  {
    title: "Cluster selection",
    items: [
      {
        src: "/images/elbow_plot.png",
        alt: "Elbow + silhouette curves",
        caption: "Inertia and silhouette score for k = 2 to 9 — both metrics support k = 5.",
      },
      {
        src: "/images/pca_clusters.png",
        alt: "PCA 2-D projection",
        caption: "PCA 2-D projection coloured by cluster.",
      },
    ],
  },
];

export default function Visualisations() {
  return (
    <div className="space-y-8">
      <header>
        <h1 className="text-3xl font-bold text-slate-900">Visualisations</h1>
        <p className="mt-1 text-slate-600">
          Complete visual evidence supporting the segmentation, grouped by
          theme. All figures are reproducible from{" "}
          <code className="text-xs bg-slate-100 px-1.5 py-0.5 rounded">
            run_pipeline.py
          </code>
          .
        </p>
      </header>

      {GROUPS.map((g) => (
        <section key={g.title} className="space-y-4">
          <h2 className="text-lg font-bold text-slate-800">{g.title}</h2>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {g.items.map((it) => (
              <ImageViewer key={it.src} {...it} />
            ))}
          </div>
        </section>
      ))}
    </div>
  );
}
