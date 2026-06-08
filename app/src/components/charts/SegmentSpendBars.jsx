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

const SPEND_COLS = [
  { key: "lifetime_spend_groceries", label: "Groceries" },
  { key: "lifetime_spend_electronics", label: "Electronics" },
  { key: "lifetime_spend_meat", label: "Meat" },
  { key: "lifetime_spend_fish", label: "Fish" },
  { key: "lifetime_spend_videogames", label: "Video Games" },
  { key: "lifetime_spend_petfood", label: "Pet Food" },
  { key: "lifetime_spend_alcohol_drinks", label: "Alcohol" },
];

/**
 * Horizontal bar chart of the active segment's spend per category,
 * sorted descending. Highlights the dominant 1–2 categories visually.
 */
export default function SegmentSpendBars({ segmentId }) {
  const { rows, loading } = useClusterSummary();
  if (loading) {
    return (
      <div className="h-48 flex items-center justify-center text-sm text-slate-400">
        Loading…
      </div>
    );
  }

  const row = rows.find((r) => r.cluster === segmentId);
  if (!row) return null;

  const data = SPEND_COLS.map((c) => ({
    category: c.label,
    value: Math.round(row[c.key]),
  })).sort((a, b) => b.value - a.value);

  const maxVal = data[0].value;

  return (
    <div style={{ width: "100%", height: 280 }}>
      <ResponsiveContainer>
        <BarChart
          data={data}
          layout="vertical"
          margin={{ top: 5, right: 30, left: 10, bottom: 5 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
          <XAxis
            type="number"
            stroke="#64748b"
            fontSize={11}
            tickFormatter={(v) => `€${(v / 1000).toFixed(0)}k`}
          />
          <YAxis
            type="category"
            dataKey="category"
            stroke="#64748b"
            fontSize={12}
            width={90}
          />
          <Tooltip
            contentStyle={{ borderRadius: 8, fontSize: 12 }}
            formatter={(v) => `€${v.toLocaleString()}`}
          />
          <Bar dataKey="value" radius={[0, 6, 6, 0]}>
            {data.map((d, i) => (
              <Cell
                key={i}
                fill={row.color}
                fillOpacity={0.3 + (d.value / maxVal) * 0.7}
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
