import { useEffect, useState } from "react";
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from "recharts";
import { SEGMENT_BY_ID } from "../../data/segments";

/**
 * Interactive per-cluster distribution explorer.
 *
 * Loads /data/histograms.json (pre-computed by app/scripts/build_histograms.py
 * from data/customer_info.csv + outputs/customer_clusters.csv) and lets the
 * user switch between metrics and toggle between stacked / grouped views.
 */
export default function DistributionExplorer() {
  const [data, setData] = useState(null);
  const [metricKey, setMetricKey] = useState(null);
  const [stacked, setStacked] = useState(true);
  const [hidden, setHidden] = useState(new Set());

  useEffect(() => {
    fetch("/data/histograms.json")
      .then((r) => r.json())
      .then((d) => {
        setData(d);
        setMetricKey(Object.keys(d.metrics)[0]);
      })
      .catch(console.error);
  }, []);

  if (!data || !metricKey) {
    return (
      <div className="card p-10 text-center text-sm text-slate-400">
        Loading histograms…
      </div>
    );
  }

  const metricKeys = Object.keys(data.metrics);
  const current = data.metrics[metricKey];
  const clusters = data.clusters;

  const toggle = (cid) => {
    const next = new Set(hidden);
    next.has(cid) ? next.delete(cid) : next.add(cid);
    setHidden(next);
  };

  return (
    <div className="card p-5">
      {/* Controls */}
      <div className="flex flex-wrap items-center justify-between gap-4 mb-4">
        <div className="flex flex-wrap gap-2">
          {metricKeys.map((k) => (
            <button
              key={k}
              onClick={() => setMetricKey(k)}
              className={[
                "px-3 py-1.5 rounded-full text-xs font-medium border transition-all",
                k === metricKey
                  ? "bg-slate-900 text-white border-slate-900"
                  : "bg-white text-slate-700 border-slate-200 hover:border-slate-300",
              ].join(" ")}
            >
              {data.metrics[k].label}
            </button>
          ))}
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => setStacked(true)}
            className={[
              "px-3 py-1.5 rounded-full text-xs font-medium border transition-all",
              stacked
                ? "bg-slate-900 text-white border-slate-900"
                : "bg-white text-slate-700 border-slate-200 hover:border-slate-300",
            ].join(" ")}
          >
            Stacked
          </button>
          <button
            onClick={() => setStacked(false)}
            className={[
              "px-3 py-1.5 rounded-full text-xs font-medium border transition-all",
              !stacked
                ? "bg-slate-900 text-white border-slate-900"
                : "bg-white text-slate-700 border-slate-200 hover:border-slate-300",
            ].join(" ")}
          >
            Grouped
          </button>
        </div>
      </div>

      {/* Title */}
      <h3 className="font-semibold text-slate-900 mb-3">
        {current.label} by cluster
      </h3>

      {/* Chart */}
      <div style={{ width: "100%", height: 360 }}>
        <ResponsiveContainer>
          <BarChart
            data={current.bins}
            margin={{ top: 10, right: 10, left: 0, bottom: 5 }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
            <XAxis
              dataKey="bin"
              stroke="#64748b"
              fontSize={11}
              angle={-25}
              textAnchor="end"
              height={60}
              interval={0}
            />
            <YAxis stroke="#64748b" fontSize={11} />
            <Tooltip
              contentStyle={{ borderRadius: 8, fontSize: 12 }}
              formatter={(v, name) => {
                const seg = SEGMENT_BY_ID[Number(name)];
                return [v.toLocaleString(), seg?.short ?? `Cluster ${name}`];
              }}
              labelFormatter={(l) => `${current.label}: ${l}`}
            />
            <Legend wrapperStyle={{ fontSize: 12 }} />
            {clusters
              .filter((cid) => !hidden.has(cid))
              .map((cid) => {
                const seg = SEGMENT_BY_ID[cid] ?? {};
                return (
                  <Bar
                    key={cid}
                    dataKey={String(cid)}
                    name={seg.short ?? `Cluster ${cid}`}
                    fill={seg.color ?? "#94a3b8"}
                    stackId={stacked ? "all" : undefined}
                    radius={stacked ? [0, 0, 0, 0] : [3, 3, 0, 0]}
                  />
                );
              })}
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Cluster toggles */}
      <div className="mt-3 flex flex-wrap gap-2 justify-center">
        {clusters.map((cid) => {
          const seg = SEGMENT_BY_ID[cid] ?? {};
          const isHidden = hidden.has(cid);
          return (
            <button
              key={cid}
              onClick={() => toggle(cid)}
              className={[
                "inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium border transition-all",
                isHidden
                  ? "border-slate-200 text-slate-400 opacity-50"
                  : "border-slate-300 text-slate-700 hover:bg-slate-50",
              ].join(" ")}
            >
              <span
                className="w-2 h-2 rounded-full"
                style={{ backgroundColor: seg.color ?? "#94a3b8" }}
              />
              {seg.short ?? `C${cid}`}
            </button>
          );
        })}
      </div>
    </div>
  );
}
