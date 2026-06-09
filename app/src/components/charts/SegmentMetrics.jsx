import { useState } from "react";
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Cell,
} from "recharts";
import { useClusterSummary } from "../../utils/useClusterSummary";

const METRICS = [
  { key: "age", label: "Avg Age", unit: "y", decimals: 1 },
  { key: "total_spend", label: "Avg Lifetime Spend", unit: "€", decimals: 0, scale: 1 },
  { key: "total_children", label: "Avg Children", unit: "", decimals: 1 },
  { key: "tenure_years", label: "Avg Tenure", unit: "y", decimals: 1 },
  { key: "distinct_stores_visited", label: "Stores Visited", unit: "", decimals: 1 },
  { key: "number_complaints", label: "Complaints", unit: "", decimals: 1 },
];

export default function SegmentMetrics() {
  const { rows, loading } = useClusterSummary();
  const [metricKey, setMetricKey] = useState(METRICS[1].key);
  if (loading) {
    return (
      <div className="h-64 flex items-center justify-center text-sm text-slate-400">
        Loading data…
      </div>
    );
  }

  const meta = METRICS.find((m) => m.key === metricKey);
  const data = rows
    .map((r) => ({
      name: r.short,
      value: +r[metricKey].toFixed(meta.decimals),
      color: r.color,
    }))
    .sort((a, b) => b.value - a.value);

  const formatVal = (v) =>
    meta.unit === "€"
      ? `€${v.toLocaleString()}`
      : `${v}${meta.unit}`;

  return (
    <div>
      <div className="mb-3 flex flex-wrap gap-2">
        {METRICS.map((m) => (
          <button
            key={m.key}
            onClick={() => setMetricKey(m.key)}
            className={[
              "px-3 py-1.5 rounded-full text-xs font-medium border transition-all",
              m.key === metricKey
                ? "bg-slate-900 text-white border-slate-900"
                : "bg-white text-slate-700 border-slate-200 hover:border-slate-300",
            ].join(" ")}
          >
            {m.label}
          </button>
        ))}
      </div>

      <div style={{ width: "100%", height: 280 }}>
        <ResponsiveContainer>
          <BarChart data={data} margin={{ top: 10, right: 20, left: 10, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
            <XAxis dataKey="name" stroke="#64748b" fontSize={12} />
            <YAxis
              stroke="#64748b"
              fontSize={11}
              tickFormatter={formatVal}
            />
            <Tooltip
              contentStyle={{ borderRadius: 8, fontSize: 12 }}
              formatter={(v) => formatVal(v)}
            />
            <Bar dataKey="value" radius={[6, 6, 0, 0]}>
              {data.map((d, i) => (
                <Cell key={i} fill={d.color} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
