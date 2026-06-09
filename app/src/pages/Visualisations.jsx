import ImageViewer from "../components/ImageViewer";
import SpendByCategory from "../components/charts/SpendByCategory";
import SpendRadar from "../components/charts/SpendRadar";
import PromoSensitivity from "../components/charts/PromoSensitivity";
import SegmentMetrics from "../components/charts/SegmentMetrics";
import DistributionExplorer from "../components/charts/DistributionExplorer";

export default function Visualisations() {
  return (
    <div className="space-y-8">
      <header>
        <h1 className="text-3xl font-bold text-slate-900">Visualisations</h1>
        <p className="mt-1 text-slate-600">
          Interactive views of the segmentation results. All charts are
          rendered live from the CSVs in <code className="text-xs bg-slate-100 px-1.5 py-0.5 rounded">outputs/</code>.
        </p>
      </header>

      {/* ── Segment portrait ─────────────────────────────────────────── */}
      <section className="space-y-4">
        <h2 className="text-lg font-bold text-slate-800">Segment portrait</h2>

        <div className="card p-5">
          <div className="flex items-start justify-between gap-4 mb-3">
            <h3 className="font-semibold text-slate-900">
              Average lifetime spend by category and segment
            </h3>
            <span className="text-xs text-slate-500">Hover bars for exact €</span>
          </div>
          <SpendByCategory />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <div className="card p-5">
            <h3 className="font-semibold text-slate-900 mb-3">
              Category profile (radar, normalised)
            </h3>
            <SpendRadar />
          </div>

          <div className="card p-5">
            <h3 className="font-semibold text-slate-900 mb-3">
              Segment metrics — pick a metric
            </h3>
            <SegmentMetrics />
          </div>
        </div>
      </section>

      {/* ── Promotion sensitivity ────────────────────────────────────── */}
      <section className="space-y-4">
        <h2 className="text-lg font-bold text-slate-800">
          Promotion sensitivity
        </h2>
        <div className="card p-5">
          <h3 className="font-semibold text-slate-900 mb-1">
            Fraction of basket purchased on promotion
          </h3>
          <p className="text-sm text-slate-600 mb-4">
            Higher = more promotion-responsive. Drives campaign design: value
            offers for the top bars, aspirational offers for the bottom.
          </p>
          <PromoSensitivity />
        </div>
      </section>

      {/* ── Behavioural distributions (now interactive) ──────────────── */}
      <section className="space-y-4">
        <h2 className="text-lg font-bold text-slate-800">
          Behavioural distributions
        </h2>
        <p className="text-sm text-slate-600 -mt-2">
          Pick a metric, switch between stacked or grouped, and toggle clusters.
          Histograms are pre-computed by{" "}
          <code className="text-xs bg-slate-100 px-1.5 py-0.5 rounded">
            app/scripts/build_histograms.py
          </code>{" "}
          for fast client-side rendering.
        </p>
        <DistributionExplorer />
      </section>

      {/* ── Cluster selection (PCA scatter kept as PNG — needs per-customer PCA components) ── */}
      <section className="space-y-4">
        <h2 className="text-lg font-bold text-slate-800">Cluster selection</h2>
        <p className="text-sm text-slate-600 -mt-2">
          Interactive elbow and silhouette curves are available in the{" "}
          <strong>Methodology</strong> tab.
        </p>
        <ImageViewer
          src="/images/pca_clusters.png"
          alt="PCA 2-D projection of all 33 038 customers"
          caption="PCA 2-D projection of all 33,038 customers coloured by assigned cluster. (Rendered server-side as the per-customer PCA components are not exported by the pipeline.)"
        />
      </section>
    </div>
  );
}
