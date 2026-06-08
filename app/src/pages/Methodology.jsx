import { useEffect, useState } from "react";
import { loadCSV } from "../utils/csv";
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from "recharts";
import ImageViewer from "../components/ImageViewer";

export default function Methodology() {
  const [metrics, setMetrics] = useState([]);

  useEffect(() => {
    loadCSV("/data/cluster_metrics.csv").then(setMetrics).catch(console.error);
  }, []);

  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-3xl font-bold text-slate-900">Methodology</h1>
        <p className="mt-1 text-slate-600">
          K-Means clustering on standardised features. Cluster count selected
          via elbow inertia and silhouette score across k = 2 to 9.
        </p>
      </header>

      {/* Decisions table */}
      <div className="card p-6">
        <h3 className="section-title">Modelling decisions</h3>
        <table className="w-full text-sm">
          <thead className="text-slate-500 text-xs uppercase tracking-wider border-b border-slate-200">
            <tr>
              <th className="py-2 text-left font-semibold">Step</th>
              <th className="py-2 text-left font-semibold">Choice</th>
              <th className="py-2 text-left font-semibold">Rationale</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            <Row
              step="Scaling"
              choice="StandardScaler"
              rationale="K-Means is distance-based; features must share a scale."
            />
            <Row
              step="k selection"
              choice="Elbow + silhouette, k = 2..9"
              rationale="k=5 maximises silhouette (0.179) and shows clear elbow inflection."
            />
            <Row
              step="Initialisations"
              choice="n_init = 15"
              rationale="Identical setting across the k-search and the final fit."
            />
            <Row
              step="Random state"
              choice="42 (fixed)"
              rationale="Reproducibility across re-runs."
            />
            <Row
              step="Visualisation"
              choice="PCA (2 components)"
              rationale="Used only for 2-D scatter; clustering runs on full feature space."
            />
            <Row
              step="Segment labelling"
              choice="Feature-signature matching (greedy)"
              rationale="Sequential persona assignment by defining characteristic; stable across re-runs."
            />
            <Row
              step="Basket rules"
              choice="Apriori (support≥1%, confidence≥25%, lift≥1.1)"
              rationale="Mined separately per cluster for segment-specific relevance."
            />
          </tbody>
        </table>
      </div>

      {/* k metrics chart */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <div className="card p-5">
          <h3 className="section-title">Inertia by k (elbow)</h3>
          <div style={{ width: "100%", height: 260 }}>
            <ResponsiveContainer>
              <LineChart data={metrics}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis dataKey="k" stroke="#64748b" fontSize={12} />
                <YAxis stroke="#64748b" fontSize={11} />
                <Tooltip contentStyle={{ borderRadius: 8, fontSize: 12 }} />
                <Line
                  type="monotone"
                  dataKey="inertia"
                  stroke="#2563eb"
                  strokeWidth={2.5}
                  dot={{ r: 4 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="card p-5">
          <h3 className="section-title">Silhouette score by k</h3>
          <div style={{ width: "100%", height: 260 }}>
            <ResponsiveContainer>
              <LineChart data={metrics}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis dataKey="k" stroke="#64748b" fontSize={12} />
                <YAxis stroke="#64748b" fontSize={11} />
                <Tooltip contentStyle={{ borderRadius: 8, fontSize: 12 }} />
                <Line
                  type="monotone"
                  dataKey="silhouette"
                  stroke="#f59e0b"
                  strokeWidth={2.5}
                  dot={{ r: 4 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* PCA scatter */}
      <ImageViewer
        src="/images/pca_clusters.png"
        alt="PCA 2-D projection coloured by cluster"
        caption="2-D PCA projection of all 33 038 customers coloured by assigned cluster. PCA is used for visualisation only — the K-Means model fits the full 50+ feature space."
      />
    </div>
  );
}

function Row({ step, choice, rationale }) {
  return (
    <tr>
      <td className="py-3 font-semibold text-slate-900">{step}</td>
      <td className="py-3 text-slate-700">{choice}</td>
      <td className="py-3 text-slate-600">{rationale}</td>
    </tr>
  );
}
