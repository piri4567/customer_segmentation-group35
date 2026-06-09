import {
  ResponsiveContainer,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  Tooltip,
  Legend,
} from "recharts";
import { useState } from "react";
import { useClusterSummary } from "../../utils/useClusterSummary";

const SPEND_COLS = [
  { key: "lifetime_spend_groceries", label: "Groceries" },
  { key: "lifetime_spend_electronics", label: "Electronics" },
  { key: "lifetime_spend_meat", label: "Meat" },
  { key: "lifetime_spend_fish", label: "Fish" },
  { key: "lifetime_spend_videogames", label: "Video Games" },
  { key: "lifetime_spend_petfood", label: "Pet Food" },
  { key: "lifetime_spend_alcohol_drinks", label: "Alcohol" },
];

export default function SpendRadar() {
  const { rows, loading } = useClusterSummary();
  const [hidden, setHidden] = useState(new Set());

  if (loading) {
    return (
      <div className="h-72 flex items-center justify-center text-sm text-slate-400">
        Loading data…
      </div>
    );
  }

  // Column-normalised: each category scaled 0..1 across clusters
  const maxes = {};
  SPEND_COLS.forEach((c) => {
    maxes[c.key] = Math.max(...rows.map((r) => r[c.key]));
  });

  const data = SPEND_COLS.map((c) => {
    const point = { category: c.label };
    rows.forEach((r) => {
      point[r.short] = +(r[c.key] / maxes[c.key]).toFixed(3);
    });
    return point;
  });

  const toggle = (short) => {
    const next = new Set(hidden);
    next.has(short) ? next.delete(short) : next.add(short);
    setHidden(next);
  };

  return (
    <div>
      <div style={{ width: "100%", height: 360 }}>
        <ResponsiveContainer>
          <RadarChart data={data} outerRadius="75%">
            <PolarGrid stroke="#e2e8f0" />
            <PolarAngleAxis dataKey="category" tick={{ fill: "#475569", fontSize: 11 }} />
            <PolarRadiusAxis tick={false} axisLine={false} domain={[0, 1]} />
            <Tooltip
              contentStyle={{ borderRadius: 8, fontSize: 12 }}
              formatter={(v) => `${(v * 100).toFixed(0)}% of max`}
            />
            {rows
              .filter((r) => !hidden.has(r.short))
              .map((r) => (
                <Radar
                  key={r.short}
                  name={r.short}
                  dataKey={r.short}
                  stroke={r.color}
                  fill={r.color}
                  fillOpacity={0.18}
                  strokeWidth={2}
                />
              ))}
          </RadarChart>
        </ResponsiveContainer>
      </div>
      <div className="mt-3 flex flex-wrap gap-2 justify-center">
        {rows.map((r) => {
          const isHidden = hidden.has(r.short);
          return (
            <button
              key={r.short}
              onClick={() => toggle(r.short)}
              className={[
                "inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium border transition-all",
                isHidden
                  ? "border-slate-200 text-slate-400 opacity-50"
                  : "border-slate-300 text-slate-700 hover:bg-slate-50",
              ].join(" ")}
            >
              <span
                className="w-2 h-2 rounded-full"
                style={{ backgroundColor: r.color }}
              />
              {r.short}
            </button>
          );
        })}
      </div>
      <p className="mt-3 text-xs text-slate-500 text-center">
        Each axis is column-normalised across segments (1.0 = highest-spending segment in that category).
        Click any legend chip to toggle.
      </p>
    </div>
  );
}
